locals {
  name = "climatehealth-${var.environment}-${var.name_suffix}"
  tags = { Project = "ClimateHealth", Environment = var.environment, ManagedBy = "Terraform" }
}

resource "terraform_data" "review_gate" {
  lifecycle {
    precondition {
      condition = (!var.database_provisioned || var.artifacts_provisioned) && (!var.edge_provisioned || var.artifacts_provisioned) && (!var.backend_provisioned || (var.artifacts_provisioned && var.database_provisioned))
      error_message = "Provision artifacts before database/edge and artifacts+database before backend."
    }
    precondition {
      condition = (!var.application_window_open || var.edge_provisioned) && (!var.service_enabled || (var.backend_provisioned && var.application_window_open))
      error_message = "API window needs edge; a running backend needs backend provisioning and an open window."
    }
    precondition {
      condition = !var.ai_provisioned || (var.artifacts_provisioned && var.ai_runtime_reviewed)
      error_message = "AI provisioning requires artifacts and reviewed private TLS/token/AMI agent delivery."
    }
    precondition {
      condition = !var.ai_enabled || var.ai_provisioned
      error_message = "Provision AI before enabling its running state."
    }
    precondition {
      condition = !var.backend_provisioned || var.ml_service_url == null || contains(keys(var.runtime_secret_arns), "ML_SERVICE_TOKEN")
      error_message = "A configured ML endpoint requires the shared protected ML_SERVICE_TOKEN parameter ARN."
    }
    precondition {
      condition     = var.infrastructure_reviewed
      error_message = "Review cost, HCP identity and saved remote plan before enabling infrastructure."
    }
    precondition {
      condition     = !var.backend_provisioned || (var.backend_instance_type != "t3.micro" && var.task_memory_mib >= 1024 && (var.backend_instance_type != "t3.small" || var.task_memory_mib <= 1024))
      error_message = "AWS backend needs a reviewed small/medium host and at least 1024 MiB; small leaves 512 MiB spare beyond the 512 MiB agent/OS reserve."
    }
  }
}

module "networking" {
  depends_on = [terraform_data.review_gate]
  source = "./modules/networking"
  name   = local.name
  vpc_cidr = var.vpc_cidr
  public_subnet_cidrs = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}
module "ecr" {
  enabled = var.artifacts_provisioned
  depends_on = [terraform_data.review_gate]
  source    = "./modules/ecr"
  ecr_names = ["${local.name}-backend", "${local.name}-ai"]
}

module "security" {
  depends_on = [terraform_data.review_gate]
  source = "./modules/security"
  name   = local.name
  vpc_id = module.networking.vpc_id
}

module "database" {
  provisioned = var.database_provisioned
  depends_on = [terraform_data.review_gate]
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
  storage_enabled = var.artifacts_provisioned
  cdn_enabled = var.edge_provisioned
  api_enabled = var.application_window_open
  depends_on = [terraform_data.review_gate]
  source          = "./modules/frontend"
  name            = local.name
  origin_hostname = var.application_window_open ? trimsuffix(aws_route53_record.origin[0].fqdn, ".") : null
  origin_header   = var.origin_verification_header
}

module "alb" {
  depends_on = [terraform_data.review_gate]
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
  provisioned = var.backend_provisioned
  tags = local.tags
  ml_service_url = var.ml_service_url
  ml_tls_ca_file = var.ml_tls_ca_file
  depends_on = [terraform_data.review_gate]
  permissions_boundary_arn = var.permissions_boundary_arn
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
  provisioned = var.ai_provisioned
  tags = local.tags
  depends_on = [terraform_data.review_gate]
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
  lifecycle {
    precondition {
      condition = try(module.alb[0].listener_arn != null, false)
      error_message = "Create the HTTPS listener/origin rule before publishing the API DNS alias."
    }
  }
  alias {
    name = module.alb[0].dns
    zone_id = module.alb[0].zone_id
    evaluate_target_health = true
  }
}
