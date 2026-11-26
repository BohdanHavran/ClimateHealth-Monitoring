variable "environment" {
  type = string
  description = "Separate HCP workspace environment."
  validation {
    condition = contains(["dev", "production"], var.environment)
    error_message = "Use dev or production."
  }
}
variable "aws_region" {
  type = string
  nullable = false
  description = "Explicitly approve the costed region and regional RDS CA."
  validation {
    condition = var.aws_region == "us-east-1"
    error_message = "Only the reviewed us-east-1 configuration is supported."
  }
}
variable "name_suffix" {
  type = string
  description = "Stable globally unique non-secret naming suffix."
  validation {
    condition = can(regex("^[a-z0-9][a-z0-9-]{2,14}[a-z0-9]$", var.name_suffix)) && !can(regex("--", var.name_suffix))
    error_message = "Use 4-16 lowercase letters/digits/hyphens, alphanumeric at both ends and no consecutive hyphens."
  }
}
variable "vpc_cidr" {
  type = string
  default = "10.42.0.0/16"
  description = "A /16 IPv4 VPC; four non-overlapping /24 subnets are derived."
  validation {
    condition = can(cidrnetmask(var.vpc_cidr)) && try(tonumber(split("/", var.vpc_cidr)[1]) == 16, false)
    error_message = "Provide a reviewed IPv4 /16 CIDR."
  }
}
variable "deploy_application" {
  type = bool
  default = false
  nullable = false
  description = "Create ephemeral API compute/ALB/DNS and its CDN origin; never gates RDS or storage."
}
variable "backend_desired_count" {
  type = number
  default = 0
  description = "Bootstrap at zero; request one task only after CP association is ready."
  validation {
    condition = contains([0, 1], var.backend_desired_count) && (var.deploy_application || var.backend_desired_count == 0)
    error_message = "Use 0 or 1; keep zero while deploy_application is false."
  }
}
variable "backend_max_instances" {
  type = number
  default = 1
  description = "Upper ASG capacity; two is an explicitly approved temporary rolling budget."
  validation {
    condition = contains([1, 2], var.backend_max_instances)
    error_message = "Allow one host normally or two for a reviewed rolling deployment."
  }
}
variable "backend_image" {
  type = string
  default = null
  description = "Reviewed digest in this environment's backend ECR repository; CI supplies the digest."
  validation {
    condition = var.backend_image == null ? !var.deploy_application : (can(regex("@sha256:[a-f0-9]{64}$", var.backend_image)) && startswith(var.backend_image, "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/climatehealth-${var.environment}-${var.name_suffix}-backend@sha256:"))
    error_message = "Use an immutable digest from the selected account/region/environment backend ECR repository."
  }
}
variable "ecs_ami_id" {
  type = string
  default = null
  description = "Approved AL2023 ECS-optimized x86_64 AMI; replacement/refresh needs review."
  validation {
    condition = var.ecs_ami_id == null ? !var.deploy_application : can(regex("^ami-([0-9a-f]{8}|[0-9a-f]{17})$", var.ecs_ami_id))
    error_message = "An approved ECS AMI is required for the application. Syntax does not verify its contents."
  }
}
variable "origin_hostname" {
  type = string
  default = null
  description = "Existing DNS hostname covered by the ALB origin certificate."
  validation {
    condition = var.origin_hostname == null ? !var.deploy_application : (length(var.origin_hostname) <= 253 && can(regex("^([a-z0-9]([a-z0-9-]*[a-z0-9])?\\.)+[a-z]{2,63}$", var.origin_hostname)))
    error_message = "Provide a valid approved lowercase DNS hostname without scheme/path/trailing dot."
  }
}
variable "origin_zone_id" {
  type = string
  default = null
  description = "Existing approved Route53 hosted zone; this root does not buy a domain."
  validation {
    condition = var.origin_zone_id == null ? !var.deploy_application : can(regex("^Z[A-Z0-9]+$", var.origin_zone_id))
    error_message = "An existing Route53 zone ID is required for the application."
  }
}
variable "origin_certificate_arn" {
  type = string
  default = null
  description = "Issued ALB ACM certificate ARN with correct DNS SAN/account/region."
  validation {
    condition = var.origin_certificate_arn == null ? !var.deploy_application : (can(regex("^arn:aws:acm:us-east-1:[0-9]{12}:certificate/[0-9a-f-]+$", var.origin_certificate_arn)) && try(split(":", var.origin_certificate_arn)[4] == data.aws_caller_identity.current.account_id, false))
    error_message = "Provide an ACM certificate ARN in the selected account and region; issuance/SAN need review."
  }
}
variable "origin_verification_header" {
  type = string
  default = null
  sensitive = true
  description = "Generate a fresh random URL-safe origin value; never print or commit it."
  validation {
    condition = var.origin_verification_header == null ? !var.deploy_application : can(regex("^[A-Za-z0-9_-]{32,128}$", var.origin_verification_header))
    error_message = "Use 32-128 random URL-safe letters/digits/underscore/hyphen, without wildcards or whitespace."
  }
}
variable "runtime_secret_arns" {
  type = map(string)
  default = {}
  description = "SSM ARN references for the RDS reader DB_USER and DB_PASS, never secret values."
  validation {
    condition = (!var.deploy_application || alltrue([for key in ["DB_USER", "DB_PASS"] : contains(keys(var.runtime_secret_arns), key)])) && alltrue([for key, arn in var.runtime_secret_arns : contains(["DB_USER", "DB_PASS"], key) && startswith(arn, "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/") && can(regex("^arn:aws:ssm:[a-z0-9-]+:[0-9]{12}:parameter/[A-Za-z0-9_./-]+$", arn))])
    error_message = "Only reader DB_USER/DB_PASS SSM parameter ARNs in the selected account/region are accepted."
  }
}
variable "permissions_boundary_arn" {
  type = string
  default = null
  description = "Existing reviewed IAM boundary for application roles; does not change HCP authentication."
  validation {
    condition = var.permissions_boundary_arn == null ? !var.deploy_application : (startswith(var.permissions_boundary_arn, "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/") && try(length(split("policy/", var.permissions_boundary_arn)[1]) > 0, false))
    error_message = "Application IAM roles require an existing reviewed boundary in the selected account."
  }
}
