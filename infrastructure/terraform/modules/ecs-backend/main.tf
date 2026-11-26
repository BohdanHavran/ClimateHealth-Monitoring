# Cluster/LT/ASG/CP adapted from owner modules/ecs. No Fargate, SSH or remote-state dependency.
variable "name" {
  type = string
}
variable "region" {
  type = string
}
variable "tags" {
  type = map(string)
}
variable "permissions_boundary_arn" {
  type = string
}
variable "ami_id" {
  type = string
}
variable "subnet_id" {
  type = string
}
variable "security_group" {
  type = string
}
variable "target_group_arn" {
  type = string
}
variable "listener_rule_arn" {
  type = string
}
variable "image" {
  type = string
}
variable "desired_count" {
  type = number
}
variable "max_instances" {
  type = number
}
variable "repository_arn" {
  type = string
}
variable "secret_arns" {
  type = map(string)
}
variable "db_host" {
  type = string
}
variable "log_group_name" {
  type = string
}
variable "log_group_arn" {
  type = string
}
resource "aws_ecs_cluster" "this" {
  name = var.name
  setting {
    name  = "containerInsights"
    value = "disabled"
  }
}
locals {
  ec2_trust = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Service = "ec2.amazonaws.com" }, Action = "sts:AssumeRole" }] })
  task_trust = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" }, Action = "sts:AssumeRole" }] })
}
resource "aws_iam_role" "host" {
  permissions_boundary = var.permissions_boundary_arn
  name = "${var.name}-host"
  assume_role_policy = local.ec2_trust
}
resource "aws_iam_role_policy_attachment" "agent" {
  role = aws_iam_role.host.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}
resource "aws_iam_role_policy_attachment" "ssm" {
  role = aws_iam_role.host.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
resource "aws_iam_instance_profile" "host" {
  depends_on = [aws_iam_role_policy_attachment.agent, aws_iam_role_policy_attachment.ssm]
  role = aws_iam_role.host.name
}
resource "aws_iam_role" "execution" {
  permissions_boundary = var.permissions_boundary_arn
  name = "${var.name}-execution"
  assume_role_policy = local.task_trust
}
resource "aws_iam_role_policy" "execution" {
  role = aws_iam_role.execution.id
  policy = jsonencode({ Version = "2012-10-17", Statement = [
        { Effect = "Allow", Action = "ecr:GetAuthorizationToken", Resource = "*" },
        { Effect = "Allow", Action = ["ecr:BatchGetImage","ecr:GetDownloadUrlForLayer","ecr:BatchCheckLayerAvailability"], Resource = [var.repository_arn] },
        { Effect = "Allow", Action = ["logs:CreateLogStream","logs:PutLogEvents"], Resource = "${var.log_group_arn}:*" },
        { Effect = "Allow", Action = ["ssm:GetParameters"], Resource = values(var.secret_arns) }
      ] })
}
resource "aws_launch_template" "host" {
  name_prefix          = "${var.name}-"
  image_id             = var.ami_id
  instance_type        = "t3.small"

  iam_instance_profile { arn = aws_iam_instance_profile.host.arn }
  monitoring { enabled = false }

  user_data = base64encode(<<-EOF
      #!/bin/bash
      mkdir -p /etc/ecs
      printf 'ECS_CLUSTER=${aws_ecs_cluster.this.name}\nECS_RESERVED_MEMORY=512\nECS_ENABLE_AWSLOGS_EXECUTIONROLE_OVERRIDE=true\n' >> /etc/ecs/ecs.config
    EOF
  )

  metadata_options {
    http_tokens   = "required"
    http_endpoint = "enabled"
    http_put_response_hop_limit = 1
  }

  credit_specification { cpu_credits = "standard" }
  network_interfaces {
    device_index = 0
    delete_on_termination = true
    associate_public_ip_address = true
    security_groups = [var.security_group]
  }
  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size = 20
      volume_type = "gp3"
      encrypted = true
      delete_on_termination = true
    }
  }
  tag_specifications {
    resource_type = "instance"
    tags = var.tags
  }
  tag_specifications {
    resource_type = "volume"
    tags = var.tags
  }
}
resource "aws_autoscaling_group" "host" {
  name                = "${var.name}-backend"
  vpc_zone_identifier = [var.subnet_id]

  desired_capacity          = var.desired_count
  min_size                  = var.desired_count
  max_size                  = var.max_instances
  health_check_grace_period = 60
  health_check_type         = "EC2"

  launch_template {
    id      = aws_launch_template.host.id
    version = aws_launch_template.host.latest_version
  }

  termination_policies = ["OldestInstance"]

  dynamic "tag" {
    for_each = var.tags
    content {
      key = tag.key
      value = tag.value
      propagate_at_launch = true
    }
  }
  tag {
    key = "AmazonECSManaged"
    value = "true"
    propagate_at_launch = true
  }
  lifecycle { ignore_changes = [desired_capacity] }
}
resource "aws_ecs_capacity_provider" "host" {

  name  = "${var.name}-backend"

  auto_scaling_group_provider {
    auto_scaling_group_arn         = aws_autoscaling_group.host.arn
    managed_termination_protection = "DISABLED"
    managed_draining = "ENABLED"

    managed_scaling {
      status                    = "ENABLED"
      target_capacity           = 100
      minimum_scaling_step_size = 1
      maximum_scaling_step_size = 1
    }
  }
}
resource "aws_ecs_cluster_capacity_providers" "this" {

  cluster_name       = aws_ecs_cluster.this.name
  capacity_providers = [aws_ecs_capacity_provider.host.name]

}
resource "aws_ecs_task_definition" "initial" {
  family = "${var.name}-backend"
  requires_compatibilities = ["EC2"]
  network_mode = "bridge"
  execution_role_arn = aws_iam_role.execution.arn
  container_definitions = jsonencode([{
        name = "backend", image = var.image, essential = true,
        memory = 1024, cpu = 256, stopTimeout = 60, readonlyRootFilesystem = true,
        portMappings = [{ containerPort = 8000, hostPort = 8080, protocol = "tcp" }],
        linuxParameters = { tmpfs = [{ containerPath = "/tmp", size = 128, mountOptions = ["rw","nosuid"] }] },
        command = ["gunicorn","--bind","0.0.0.0:8000","--workers","1","--threads","1","--timeout","30","--graceful-timeout","25","climat:app"],
        environment = [
          {name="DB_HOST",value=var.db_host}, {name="DB_NAME",value="climate_db"},
          {name="DATABASE_WRITES_ENABLED",value="false"}, {name="CLIMATE_ENV",value="aws"},
          {name="DB_TLS_MODE",value="verify_identity"},
          {name="DB_TLS_CA_FILE",value="/app/infrastructure/certificates/rds-us-east-1-bundle.crt"}
        ],
        secrets = [for k,v in var.secret_arns : { name=k, valueFrom=v }],
        logConfiguration = { logDriver="awslogs", options={"awslogs-group"=var.log_group_name,"awslogs-region"=var.region,"awslogs-stream-prefix"="backend"} },
        healthCheck = { command=["CMD","python","-c","import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live',timeout=3)"],interval=30,timeout=5,retries=3,startPeriod=60 }
  }])
}
resource "aws_ecs_service" "this" {
  name = "backend"
  cluster = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.initial.arn
  desired_count = var.desired_count
  deployment_minimum_healthy_percent = var.max_instances > 1 ? 100 : 0
  deployment_maximum_percent = var.max_instances > 1 ? 200 : 100
  health_check_grace_period_seconds = 90
  enable_execute_command = false
  wait_for_steady_state = true
  timeouts {
    create = "20m"
    update = "20m"
  }
  deployment_circuit_breaker {
    enable = true
    rollback = true
  }
  capacity_provider_strategy {
    capacity_provider = aws_ecs_capacity_provider.host.name
    weight = 1
  }
  load_balancer {
    target_group_arn = var.target_group_arn
    container_name = "backend"
    container_port = 8000
  }
  depends_on = [aws_ecs_cluster_capacity_providers.this, aws_iam_role_policy.execution, aws_autoscaling_group.host]
  # HCP owns task configuration for the first controlled deployment. CD remains disabled.
  lifecycle {
    precondition {
      condition = var.listener_rule_arn != null
      error_message = "Wait for the HTTPS listener rule before associating this target group."
    }
  }
}
output "cluster" { value = aws_ecs_cluster.this.name }
output "service" { value = aws_ecs_service.this.name }
output "asg_name" { value = aws_autoscaling_group.host.name }
output "task_definition_arn" { value = aws_ecs_task_definition.initial.arn }
output "capacity_provider" { value = aws_ecs_capacity_provider.host.name }
