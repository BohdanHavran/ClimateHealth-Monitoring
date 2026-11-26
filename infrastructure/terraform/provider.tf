terraform {
  required_version = ">= 1.11.0, < 2.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 6.74.0"
    }
  }
}
# VCS-driven HCP workspaces own state; intentionally no backend/cloud block.
provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "ClimateHealth"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
