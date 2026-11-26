variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "production"], var.environment)
    error_message = "Use dev or production in its own HCP workspace."
  }
}

variable "aws_region" {
  type    = string
  nullable = false
  description = "Explicitly approved workspace region. us-east-1 is the costed candidate, not an implicit deployment decision."
  validation {
    condition     = var.aws_region == "us-east-1"
    error_message = "Only the costed us-east-1 candidate is currently supported; approve region and review costs/certificates before extending this constraint."
  }
}

variable "name_suffix" {
  type = string
  description = "Globally unique, non-secret bucket/name suffix."
  validation {
    condition     = can(regex("^[a-z0-9-]{4,16}$", var.name_suffix))
    error_message = "Use 4-16 lowercase letters, digits or hyphens."
  }
}

variable "infrastructure_reviewed" {
  type = bool
  default = false
}

variable "service_enabled" {
  type = bool
  default = false
}

variable "backend_image" {
  type        = string
  default = null
  description = "Approved ECR image URI pinned by sha256, initial bootstrap only."
  validation {
    condition     = var.backend_image == null ? !var.backend_provisioned : (can(regex("@sha256:[a-f0-9]{64}$", var.backend_image)))
    error_message = "A reviewed immutable image digest is required."
  }
}

variable "ecs_ami_id" {
  type        = string
  default = null
  description = "Approved AL2023 ECS-optimized x86 AMI ID; not an unreviewed latest lookup."
  validation {
    condition     = var.ecs_ami_id == null ? !var.backend_provisioned : (can(regex("^ami-([0-9a-f]{8}|[0-9a-f]{17})$", var.ecs_ami_id)))
    error_message = "Provide an approved ECS AMI ID for the selected region; syntax alone does not verify the image."
  }
}

variable "backend_instance_type" {
  type = string
  default = "t3.small"
  validation {
    condition     = contains(["t3.micro", "t3.small", "t3.medium"], var.backend_instance_type)
    error_message = "CPU-only reviewed instance types."
  }
}

variable "task_memory_mib" {
  type = number
  default = 1024
  validation {
    condition = contains([256,512,768,1024,1536], var.task_memory_mib)
    error_message = "Use a reviewed bounded ECS memory value."
  }
}

variable "allow_deployment_capacity" {
  type = bool
  default = false
}

variable "origin_hostname" {
  type        = string
  default = null
  description = "DNS name pointing to ALB; certificate must cover it. External DNS is an approval gate."
  validation {
    condition     = var.origin_hostname == null ? !var.application_window_open : (length(var.origin_hostname) <= 253 && can(regex("^([a-z0-9]([a-z0-9-]*[a-z0-9])?\\.)+[a-z]{2,63}$", var.origin_hostname)))
    error_message = "Provide an approved lowercase DNS hostname, without a scheme, path or trailing dot."
  }
}

variable "origin_certificate_arn" {
  type        = string
  default = null
  description = "Validated us-east-1 ACM certificate ARN for the ALB origin hostname."
  validation {
    condition     = var.origin_certificate_arn == null ? !var.application_window_open : (can(regex("^arn:aws:acm:us-east-1:[0-9]{12}:certificate/[0-9a-f-]+$", var.origin_certificate_arn)) && try(split(":", var.origin_certificate_arn)[4] == data.aws_caller_identity.current.account_id, false))
    error_message = "Provide an ACM certificate ARN in the selected account and supported ALB region; issuance and domain coverage require separate verification."
  }
}

variable "origin_verification_header" {
  type      = string
  default = null
  sensitive = true
  description = "New environment-specific random origin verification value; kept in protected HCP state, never output."
  validation {
    condition     = var.origin_verification_header == null ? !var.application_window_open : (length(var.origin_verification_header) >= 32)
    error_message = "At least 32 random characters required."
  }
}

variable "runtime_secret_arns" {
  type        = map(string)
  default = {}
  description = "SSM parameter ARNs keyed DB_USER, DB_PASS and optionally ML_SERVICE_TOKEN. Reader credentials, never RDS master."
  validation {
    condition     = (!var.backend_provisioned || alltrue([for k in ["DB_USER", "DB_PASS"] : contains(keys(var.runtime_secret_arns), k)])) && alltrue([for arn in values(var.runtime_secret_arns) : startswith(arn, "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/")])
    error_message = "Reader DB_USER and DB_PASS SSM parameter ARNs in the selected account/region are required, never plaintext values."
  }
}

variable "database_mode" {
  type = string
  default = "rds"
  validation {
    condition     = contains(["rds", "ec2"], var.database_mode)
    error_message = "MySQL only: rds or baked ec2."
  }
}

variable "mysql_ami_id" {
  type = string
  default = null
  validation {
    condition     = var.mysql_ami_id == null ? (!var.database_provisioned || var.database_mode != "ec2") : can(regex("^ami-([0-9a-f]{8}|[0-9a-f]{17})$", var.mysql_ami_id))
    error_message = "EC2 MySQL mode requires an approved MySQL AMI ID."
  }
}

variable "ai_enabled" {
  type = bool
  default = false
}

variable "ai_ami_id" {
  type = string
  default = null
  validation {
    condition     = var.ai_ami_id == null ? !var.ai_provisioned : can(regex("^ami-([0-9a-f]{8}|[0-9a-f]{17})$", var.ai_ami_id))
    error_message = "Enabled AI requires an approved private AI AMI ID."
  }
}

variable "ai_instance_type" {
  type = string
  default = "t3.small"
  validation {
    condition     = contains(["t3.small", "t3.medium", "t3.large"], var.ai_instance_type)
    error_message = "CPU-only AI types; benchmark before increasing memory."
  }
}

variable "application_window_open" {
  type = bool
  default = false
  description = "Manual HCP plan/apply gate for ALB lifecycle; closing deletes ALB/service after explicit plan review, never a scheduler."
}

variable "origin_zone_id" {
  type = string
  default = null
  description = "Approved existing public Route53 hosted zone for the API origin alias; no domain/zone is purchased by this root."
  validation {
    condition     = var.origin_zone_id == null ? !var.application_window_open : (can(regex("^Z[A-Z0-9]+$", var.origin_zone_id)))
    error_message = "Provide the ID of an existing approved Route53 hosted zone."
  }
}

variable "permissions_boundary_arn" {
  type = string
  default = null
  description = "Approved pre-existing environment IAM permissions boundary; bootstrap is separate from this root."
  validation {
    condition     = var.permissions_boundary_arn == null ? !(var.backend_provisioned || var.ai_provisioned || (var.database_provisioned && var.database_mode == "ec2")) : (startswith(var.permissions_boundary_arn, "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/") && try(length(split("policy/", var.permissions_boundary_arn)[1]) > 0, false))
    error_message = "Provide an existing permissions boundary policy ARN in the selected AWS account."
  }
}

variable "vpc_cidr" {
  type = string
  default = "10.42.0.0/16"
  description = "Approved IPv4 VPC range; changing this after provisioning requires replacement review."
  validation {
    condition = can(cidrnetmask(var.vpc_cidr))
    error_message = "An IPv4 CIDR is required; approve containment and non-overlap before the first remote plan."
  }
}
variable "public_subnet_cidrs" {
  type = list(string)
  default = ["10.42.0.0/24", "10.42.1.0/24"]
  description = "Exactly two distinct approved public subnet CIDRs, contained in the VPC."
  validation {
    condition = length(var.public_subnet_cidrs) == 2 && length(distinct(var.public_subnet_cidrs)) == 2 && alltrue([for cidr in var.public_subnet_cidrs : can(cidrnetmask(cidr))])
    error_message = "Provide two distinct IPv4 CIDRs; containment and overlap also require review."
  }
}
variable "private_subnet_cidrs" {
  type = list(string)
  default = ["10.42.10.0/24", "10.42.11.0/24"]
  description = "Exactly two distinct approved private subnet CIDRs, contained in the VPC."
  validation {
    condition = length(var.private_subnet_cidrs) == 2 && length(distinct(var.private_subnet_cidrs)) == 2 && alltrue([for cidr in var.private_subnet_cidrs : can(cidrnetmask(cidr))])
    error_message = "Provide two distinct IPv4 CIDRs; containment and overlap also require review."
  }
}

# Provisioning flags are monotonic after creation; activity flags close demos.
variable "artifacts_provisioned" {
  type = bool
  default = false
  description = "Create protected ECR repositories and private S3 storage; do not turn off after provisioning."
}
variable "database_provisioned" {
  type = bool
  default = false
  description = "Create protected MySQL; false is not a database stop command."
}
variable "edge_provisioned" {
  type = bool
  default = false
  description = "Create CloudFront frontend; API origin exists only during an application window."
}
variable "backend_provisioned" {
  type = bool
  default = false
  description = "Create backend IAM/cluster/task/LT/ASG; workload capacity uses service_enabled and window."
}
variable "ai_provisioned" {
  type = bool
  default = false
  description = "Create protected private AI instance; ai_enabled controls running/stopped state, not destruction."
}
variable "ai_runtime_reviewed" {
  type = bool
  default = false
  description = "Approve actual private TLS/token delivery/AMI agent readiness before creating an AI host."
}
variable "ml_service_url" {
  type = string
  default = null
  description = "Reviewed private HTTPS endpoint, managed separately; never an unverified automatic IP URL."
  validation {
    condition = var.ml_service_url == null ? true : can(regex("^https://[a-z0-9][a-z0-9.-]+(:[0-9]{1,5})?/?$", var.ml_service_url))
    error_message = "Use a reviewed HTTPS DNS endpoint without userinfo, query, fragment or path."
  }
}
variable "ml_tls_ca_file" {
  type = string
  default = null
  description = "Optional absolute CA path already included in the reviewed backend image, for a private ML CA."
  validation {
    condition = var.ml_tls_ca_file == null ? true : startswith(var.ml_tls_ca_file, "/app/")
    error_message = "A private CA must be packaged at an approved /app/ image path."
  }
}
