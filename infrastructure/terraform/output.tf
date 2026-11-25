output "vpc_id" { value = module.networking.vpc_id }
output "cloudfront_domain" { value = module.frontend.domain }
output "cloudfront_distribution_id" { value = module.frontend.distribution_id }
output "frontend_bucket" { value = module.frontend.bucket }
output "artifact_bucket" { value = module.frontend.artifact_bucket }
output "alb_dns" { value = try(module.alb[0].dns, null) }
output "ecs_cluster" { value = module.backend.cluster }
output "ecs_service" { value = module.backend.service }
output "ecr_urls" { value = module.ecr.urls }
output "database_endpoint" { value = module.database.host }
output "ai_private_ip" { value = module.ai.private_ip }

output "reviewed_task_definition_arn" { value = module.backend.task_definition_arn }
output "backend_task_role_arn" { value = module.backend.task_role_arn }
output "backend_execution_role_arn" { value = module.backend.execution_role_arn }

output "alb_arn" { value = try(module.alb[0].arn, null) }
output "target_group_arn" { value = try(module.alb[0].target_group_arn, null) }
output "backend_asg" { value = module.backend.asg_name }
output "capacity_provider" { value = module.backend.capacity_provider }
output "private_subnet_ids" { value = module.networking.private_subnet_ids }
