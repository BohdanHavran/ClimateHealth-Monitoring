# Adapted from owner ecr/main.tf; see TERRAFORM_MODULE_REUSE.md.
resource "aws_ecr_repository" "ecr" {

  for_each             = toset(var.ecr_names)
  name                 = each.value
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}


resource "aws_ecr_lifecycle_policy" "images" {
  for_each = aws_ecr_repository.ecr
  repository = each.value.name
  policy = jsonencode({ rules = [{ rulePriority = 1, description = "Remove untagged layers after rollback window", selection = { tagStatus = "untagged", countType = "sinceImagePushed", countUnit = "days", countNumber = 14 }, action = { type = "expire" } }] })
}
output "arns" { value = { for k,v in aws_ecr_repository.ecr : k => v.arn } }
output "urls" { value = { for k,v in aws_ecr_repository.ecr : k => v.repository_url } }
