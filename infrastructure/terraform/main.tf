locals {
  name = "climatehealth-${var.environment}-${var.name_suffix}"
  tags = { Project = "ClimateHealth", Environment = var.environment, ManagedBy = "Terraform" }
}

module "networking" {
  source = "./modules/networking"
  name = local.name
  vpc_cidr = var.vpc_cidr
}
module "ecr" {
  source = "./modules/ecr"
  ecr_names = ["${local.name}-backend"]
}
module "database" {
  source = "./modules/mysql"
  name = local.name
  subnet_ids = module.networking.private_subnet_ids
  security_group = module.networking.mysql_sg
  availability_zone = module.networking.availability_zone
}
module "frontend" {
  source = "./modules/frontend"
  name = local.name
  api_enabled = var.deploy_application
  origin_hostname = var.deploy_application ? trimsuffix(aws_route53_record.origin[0].fqdn, ".") : null
  origin_header = var.origin_verification_header
}
module "alb" {
  count = var.deploy_application ? 1 : 0
  source = "./modules/alb"
  vpc_id = module.networking.vpc_id
  subnet_ids = module.networking.public_subnet_ids
  security_group = module.networking.alb_sg
  certificate_arn = var.origin_certificate_arn
  origin_header = var.origin_verification_header
}

# Retained independently of application teardown; never put logs behind the app count.
resource "aws_cloudwatch_log_group" "backend" {
  name = "/climatehealth/${local.name}/backend"
  retention_in_days = 7
  lifecycle { prevent_destroy = true }
}
module "backend" {
  count = var.deploy_application ? 1 : 0
  source = "./modules/ecs-backend"
  name = local.name
  region = var.aws_region
  tags = local.tags
  permissions_boundary_arn = var.permissions_boundary_arn
  ami_id = var.ecs_ami_id
  subnet_id = module.networking.public_subnet_ids[0]
  security_group = module.networking.backend_sg
  target_group_arn = module.alb[0].target_group_arn
  listener_rule_arn = module.alb[0].listener_rule_arn
  image = var.backend_image
  desired_count = var.backend_desired_count
  max_instances = var.backend_max_instances
  repository_arn = module.ecr.arns["${local.name}-backend"]
  secret_arns = var.runtime_secret_arns
  db_host = module.database.host
  log_group_name = aws_cloudwatch_log_group.backend.name
  log_group_arn = aws_cloudwatch_log_group.backend.arn
}
resource "aws_route53_record" "origin" {
  count = var.deploy_application ? 1 : 0
  zone_id = var.origin_zone_id
  name = var.origin_hostname
  type = "A"
  lifecycle {
    precondition {
      condition = module.alb[0].listener_rule_arn != null
      error_message = "Publish origin DNS only after the HTTPS forwarding rule is ready."
    }
  }
  alias {
    name = module.alb[0].dns
    zone_id = module.alb[0].zone_id
    evaluate_target_health = true
  }
}
