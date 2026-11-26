variable "provisioned" { type = bool }
variable "tags" { type = map(string) }
variable "ml_service_url" { type = string }
variable "ml_tls_ca_file" { type = string }
variable "permissions_boundary_arn" {
  type = string
}
variable "name" {
  type = string
}
variable "region" {
  type = string
}
variable "ami_id" {
  type = string
}
variable "instance_type" {
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
variable "listener_arn" {
  type = string
}
variable "image" {
  type = string
}
variable "active_window" {
  type = bool
}
variable "enabled" {
  type = bool
}
variable "task_memory" {
  type = number
}
variable "extra_capacity" {
  type = bool
}
variable "repository_arns" {
  type = list(string)
}
variable "secret_arns" {
  type = map(string)
}
variable "db_host" {
  type = string
}
resource "aws_ecs_cluster" "this" {
  count = var.provisioned ? 1 : 0
  name = var.name
  setting {
    name = "containerInsights"
    value = "disabled"
  }
}
locals {
  ec2_trust = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Service = "ec2.amazonaws.com" }, Action = "sts:AssumeRole" }] })
  task_trust = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" }, Action = "sts:AssumeRole" }] })
}
resource "aws_iam_role" "host" {
  count = var.provisioned ? 1 : 0
  permissions_boundary = var.permissions_boundary_arn
  name = "${var.name}-host"
  assume_role_policy = local.ec2_trust
}
resource "aws_iam_role_policy_attachment" "agent" {
  count = var.provisioned ? 1 : 0
  role = aws_iam_role.host[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}
resource "aws_iam_role_policy_attachment" "ssm" {
  count = var.provisioned ? 1 : 0
  role = aws_iam_role.host[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
resource "aws_iam_instance_profile" "host" {
  depends_on = [aws_iam_role_policy_attachment.agent, aws_iam_role_policy_attachment.ssm]
  count = var.provisioned ? 1 : 0
  role = aws_iam_role.host[0].name
}
resource "aws_iam_role" "execution" {
  count = var.provisioned ? 1 : 0
  permissions_boundary = var.permissions_boundary_arn
  name = "${var.name}-execution"
  assume_role_policy = local.task_trust
}
resource "aws_iam_role" "task" {
  count = var.provisioned ? 1 : 0
  permissions_boundary = var.permissions_boundary_arn
  name = "${var.name}-task"
  assume_role_policy = local.task_trust
}
resource "aws_cloudwatch_log_group" "backend" {
  count = var.provisioned ? 1 : 0
  name = "/climatehealth/${var.name}/backend"
  retention_in_days = 7
  lifecycle { prevent_destroy = true }
}
resource "aws_iam_role_policy" "execution" {
  count = var.provisioned ? 1 : 0
  role = aws_iam_role.execution[0].id
  policy = jsonencode({ Version = "2012-10-17", Statement = [
        { Effect = "Allow", Action = "ecr:GetAuthorizationToken", Resource = "*" },
        { Effect = "Allow", Action = ["ecr:BatchGetImage","ecr:GetDownloadUrlForLayer","ecr:BatchCheckLayerAvailability"], Resource = var.repository_arns },
        { Effect = "Allow", Action = ["logs:CreateLogStream","logs:PutLogEvents"], Resource = "${aws_cloudwatch_log_group.backend[0].arn}:*" },
        { Effect = "Allow", Action = ["ssm:GetParameters"], Resource = values(var.secret_arns) }
      ] })
}
resource "aws_launch_template" "host" {
  count = var.provisioned ? 1 : 0
  name_prefix = "${var.name}-"
  tag_specifications {
    resource_type = "instance"
    tags = var.tags
  }
  tag_specifications {
    resource_type = "volume"
    tags = var.tags
  }
  image_id = var.ami_id
  instance_type = var.instance_type
  iam_instance_profile { arn = aws_iam_instance_profile.host[0].arn }
  network_interfaces {
    device_index = 0
    delete_on_termination = true
    associate_public_ip_address = true
    security_groups = [var.security_group]
  }
  metadata_options {
    http_tokens = "required"
    http_put_response_hop_limit = 1
  }
  credit_specification { cpu_credits = "standard" }
  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size = 20
      volume_type = "gp3"
      encrypted = true
      delete_on_termination = true
    }
  }
  user_data = base64encode(<<-SH
    #!/bin/bash
    mkdir -p /etc/ecs
    printf 'ECS_CLUSTER=${aws_ecs_cluster.this[0].name}\nECS_RESERVED_MEMORY=512\nECS_ENABLE_AWSLOGS_EXECUTIONROLE_OVERRIDE=true\n' >> /etc/ecs/ecs.config
  SH
  )
}
resource "aws_autoscaling_group" "host" {
  count = var.provisioned ? 1 : 0
  name = "${var.name}-backend"
  vpc_zone_identifier = [var.subnet_id]
  min_size = var.enabled ? 1 : 0
  desired_capacity = var.enabled ? 1 : 0
  max_size = var.enabled ? (var.extra_capacity ? 2 : 1) : 0
  health_check_type = "EC2"
  dynamic "tag" {
    for_each = var.tags
    content {
      key = tag.key
      value = tag.value
      propagate_at_launch = true
    }
  }
  launch_template {
    id = aws_launch_template.host[0].id
    version = aws_launch_template.host[0].latest_version
  }
  tag {
    key = "AmazonECSManaged"
    value = "true"
    propagate_at_launch = true
  }
  lifecycle { ignore_changes = [desired_capacity] }
}
resource "aws_ecs_capacity_provider" "host" {
  count = var.provisioned ? 1 : 0
  name = "${var.name}-backend"
  auto_scaling_group_provider {
    auto_scaling_group_arn = aws_autoscaling_group.host[0].arn
    managed_termination_protection = "DISABLED"
    managed_draining = "ENABLED"
    managed_scaling {
      status = "ENABLED"
      target_capacity = 100
      minimum_scaling_step_size = 1
      maximum_scaling_step_size = 1
    }
  }
}
resource "aws_ecs_cluster_capacity_providers" "this" {
  count = var.provisioned ? 1 : 0
  cluster_name = aws_ecs_cluster.this[0].name
  capacity_providers = [aws_ecs_capacity_provider.host[0].name]
}
resource "aws_ecs_task_definition" "initial" {
  count = var.provisioned ? 1 : 0
  family = "${var.name}-backend"
  requires_compatibilities = ["EC2"]
  network_mode = "bridge"
  execution_role_arn = aws_iam_role.execution[0].arn
  task_role_arn = aws_iam_role.task[0].arn
  container_definitions = jsonencode([{
        name = "backend", image = var.image, essential = true,
        memory = var.task_memory, cpu = 256, stopTimeout = 60, readonlyRootFilesystem = true,
        portMappings = [{ containerPort = 8000, hostPort = 8080, protocol = "tcp" }],
        linuxParameters = { tmpfs = [{ containerPath = "/tmp", size = 128, mountOptions = ["rw","nosuid"] }] },
        command = ["gunicorn","--bind","0.0.0.0:8000","--workers","1","--threads","1","--timeout","30","--graceful-timeout","25","climat:app"],
        environment = concat(
          [{name="DB_HOST",value=var.db_host},{name="DB_NAME",value="climate_db"},{name="DATABASE_WRITES_ENABLED",value="false"},
           {name="CLIMATE_ENV",value="aws"},{name="DB_TLS_MODE",value="verify_identity"},
           {name="DB_TLS_CA_FILE",value="/app/infrastructure/certificates/rds-us-east-1-bundle.crt"}],
          var.ml_service_url == null ? [] : [{name="ML_SERVICE_URL",value=var.ml_service_url},{name="ML_SERVICE_ALLOWED_HOST",value=regex("^https://([^:/]+)",var.ml_service_url)[0]}],
          var.ml_tls_ca_file == null ? [] : [{name="ML_TLS_CA_FILE",value=var.ml_tls_ca_file}]
        ),
        secrets = [for k,v in var.secret_arns : { name=k, valueFrom=v }],
        logConfiguration = { logDriver="awslogs", options={"awslogs-group"=aws_cloudwatch_log_group.backend[0].name,"awslogs-region"=var.region,"awslogs-stream-prefix"="backend"} },
        healthCheck = { command=["CMD","python","-c","import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live',timeout=3)"],interval=30,timeout=5,retries=3,startPeriod=60 }
  }])
}
resource "aws_ecs_service" "this" {
  count = var.provisioned && var.active_window ? 1 : 0
  name = "backend"
  cluster = aws_ecs_cluster.this[0].id
  task_definition = aws_ecs_task_definition.initial[0].arn
  desired_count = var.enabled ? 1 : 0
  deployment_minimum_healthy_percent = var.extra_capacity ? 100 : 0
  deployment_maximum_percent = var.extra_capacity ? 200 : 100
  health_check_grace_period_seconds = 90
  enable_execute_command = false
  deployment_circuit_breaker {
    enable = true
    rollback = true
  }
  capacity_provider_strategy {
    capacity_provider = aws_ecs_capacity_provider.host[0].name
    weight = 1
  }
  load_balancer {
    target_group_arn = var.target_group_arn
    container_name = "backend"
    container_port = 8000
  }
  depends_on = [aws_ecs_cluster_capacity_providers.this, aws_iam_role_policy.execution]
  # HCP owns task configuration for the first controlled deployment. CD remains disabled.
  lifecycle {
    precondition {
      condition = var.listener_arn != null
      error_message = "Wait for the HTTPS listener rule before associating this target group."
    }
  }
}
output "cluster" { value = try(aws_ecs_cluster.this[0].name, null) }
output "service" { value = try(aws_ecs_service.this[0].name, null) }

output "task_definition_arn" { value = try(aws_ecs_task_definition.initial[0].arn, null) }
output "task_role_arn" { value = try(aws_iam_role.task[0].arn, null) }
output "execution_role_arn" { value = try(aws_iam_role.execution[0].arn, null) }

output "asg_name" { value = try(aws_autoscaling_group.host[0].name, null) }
output "capacity_provider" { value = try(aws_ecs_capacity_provider.host[0].name, null) }

# Preserve any earlier unindexed state addresses; never silently recreate hosts/IAM.
moved {
  from = aws_ecs_cluster.this
  to = aws_ecs_cluster.this[0]
}
moved {
  from = aws_iam_role.host
  to = aws_iam_role.host[0]
}
moved {
  from = aws_iam_role_policy_attachment.agent
  to = aws_iam_role_policy_attachment.agent[0]
}
moved {
  from = aws_iam_role_policy_attachment.ssm
  to = aws_iam_role_policy_attachment.ssm[0]
}
moved {
  from = aws_iam_instance_profile.host
  to = aws_iam_instance_profile.host[0]
}
moved {
  from = aws_iam_role.execution
  to = aws_iam_role.execution[0]
}
moved {
  from = aws_iam_role.task
  to = aws_iam_role.task[0]
}
moved {
  from = aws_cloudwatch_log_group.backend
  to = aws_cloudwatch_log_group.backend[0]
}
moved {
  from = aws_iam_role_policy.execution
  to = aws_iam_role_policy.execution[0]
}
moved {
  from = aws_launch_template.host
  to = aws_launch_template.host[0]
}
moved {
  from = aws_autoscaling_group.host
  to = aws_autoscaling_group.host[0]
}
moved {
  from = aws_ecs_capacity_provider.host
  to = aws_ecs_capacity_provider.host[0]
}
moved {
  from = aws_ecs_cluster_capacity_providers.this
  to = aws_ecs_cluster_capacity_providers.this[0]
}
moved {
  from = aws_ecs_task_definition.initial
  to = aws_ecs_task_definition.initial[0]
}
