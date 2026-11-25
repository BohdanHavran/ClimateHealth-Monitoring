locals { name = "climatehealth-${var.environment}-${var.name_suffix}" }
resource "terraform_data" "review_gate" {
  lifecycle {
    precondition {
      condition     = var.infrastructure_reviewed
      error_message = "Review cost, HCP identity and saved remote plan before enabling infrastructure."
    }
    precondition {
      condition     = var.backend_instance_type != "t3.micro" || var.task_memory_mib <= 256
      error_message = "Micro is a benchmark-only configuration with <=256 MiB task memory; not the recommended stack."
    }
  }
}
module "networking" {
  source = "./modules/networking"
  name   = local.name
  vpc_cidr = var.vpc_cidr
  public_subnet_cidrs = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}
module "ecr" {
  source    = "./modules/ecr"
  ecr_names = ["${local.name}-backend", "${local.name}-ai"]
}
module "security" {
  source = "./modules/security"
  name   = local.name
  vpc_id = module.networking.vpc_id
}
module "database" {
  permissions_boundary_arn = var.permissions_boundary_arn
  source          = "./modules/mysql"
  name            = local.name
  mode            = var.database_mode
  subnet_ids      = module.networking.private_subnet_ids
  security_group  = module.security.mysql_sg
  availability_zone = module.networking.availability_zone
  mysql_ami_id    = var.mysql_ami_id
  artifact_bucket_arn = module.frontend.artifact_bucket_arn
}
module "frontend" {
  source          = "./modules/frontend"
  name            = local.name
  origin_hostname = var.origin_hostname
  origin_header   = var.origin_verification_header
}
module "alb" {
  count = var.application_window_open ? 1 : 0
  source          = "./modules/alb"
  name            = local.name
  vpc_id          = module.networking.vpc_id
  subnet_ids      = module.networking.public_subnet_ids
  security_group  = module.security.alb_sg
  certificate_arn = var.origin_certificate_arn
  origin_header   = var.origin_verification_header
}
module "backend" {
  permissions_boundary_arn = var.permissions_boundary_arn
  depends_on = [module.alb]
  source          = "./modules/ecs-backend"
  name            = local.name
  region          = var.aws_region
  ami_id          = var.ecs_ami_id
  instance_type   = var.backend_instance_type
  subnet_id       = module.networking.public_subnet_ids[0]
  security_group  = module.security.backend_sg
  target_group_arn = try(module.alb[0].target_group_arn, null)
  listener_arn    = try(module.alb[0].listener_arn, null)
  image           = var.backend_image
  enabled         = var.service_enabled && var.application_window_open
  active_window   = var.application_window_open
  task_memory     = var.task_memory_mib
  extra_capacity  = var.allow_deployment_capacity
  repository_arns = values(module.ecr.arns)
  secret_arns     = var.runtime_secret_arns
  db_host         = module.database.host
}
module "ai" {
  permissions_boundary_arn = var.permissions_boundary_arn
  source             = "./modules/ai"
  name               = local.name
  enabled            = var.ai_enabled
  ami_id             = var.ai_ami_id
  instance_type      = var.ai_instance_type
  subnet_id          = module.networking.private_subnet_ids[0]
  security_group     = module.security.ai_sg
  artifact_bucket_arn = module.frontend.artifact_bucket_arn
}

resource "aws_route53_record" "origin" {
  count = var.application_window_open ? 1 : 0
  zone_id = var.origin_zone_id
  name = var.origin_hostname
  type = "A"
  alias {
    name = module.alb[0].dns
    zone_id = module.alb[0].zone_id
    evaluate_target_health = true
  }
}
