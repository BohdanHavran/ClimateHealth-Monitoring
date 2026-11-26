# Data sources, locals та outputs

Усі допоміжні блоки активного коду. Expressions не виконувалися. Data sources читають AWS тільки під час майбутнього погодженого HCP run; зараз виконано лише читання локальних файлів.


## module.alb

| Вид / адреса | Вираз або призначення | Джерело |
|---|---|---|
| output: `output.target_group_arn` | `aws_lb_target_group.backend.arn` | [код L76](../../infrastructure/terraform/modules/alb/main.tf#L76) |
| output: `output.listener_rule_arn` | `aws_lb_listener_rule.origin.arn` | [код L77](../../infrastructure/terraform/modules/alb/main.tf#L77) |
| output: `output.dns` | `aws_lb.this.dns_name` | [код L78](../../infrastructure/terraform/modules/alb/main.tf#L78) |
| output: `output.zone_id` | `aws_lb.this.zone_id` | [код L79](../../infrastructure/terraform/modules/alb/main.tf#L79) |

## module.backend

| Вид / адреса | Вираз або призначення | Джерело |
|---|---|---|
| local: `local.ec2_trust` | `jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Service = "ec2.amazonaws.com" }, Action = "sts:AssumeRole" }] })` | [код L60](../../infrastructure/terraform/modules/ecs-backend/main.tf#L60) |
| local: `local.task_trust` | `jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" }, Action = "sts:AssumeRole" }] })` | [код L60](../../infrastructure/terraform/modules/ecs-backend/main.tf#L60) |
| output: `output.cluster` | `aws_ecs_cluster.this.name` | [код L254](../../infrastructure/terraform/modules/ecs-backend/main.tf#L254) |
| output: `output.service` | `aws_ecs_service.this.name` | [код L255](../../infrastructure/terraform/modules/ecs-backend/main.tf#L255) |
| output: `output.asg_name` | `aws_autoscaling_group.host.name` | [код L256](../../infrastructure/terraform/modules/ecs-backend/main.tf#L256) |
| output: `output.task_definition_arn` | `aws_ecs_task_definition.initial.arn` | [код L257](../../infrastructure/terraform/modules/ecs-backend/main.tf#L257) |
| output: `output.capacity_provider` | `aws_ecs_capacity_provider.host.name` | [код L258](../../infrastructure/terraform/modules/ecs-backend/main.tf#L258) |

## module.database

| Вид / адреса | Вираз або призначення | Джерело |
|---|---|---|
| output: `output.host` | `aws_db_instance.this.address` | [код L50](../../infrastructure/terraform/modules/mysql/main.tf#L50) |

## module.ecr

| Вид / адреса | Вираз або призначення | Джерело |
|---|---|---|
| output: `output.arns` | `{ for k,v in aws_ecr_repository.ecr : k => v.arn }` | [код L24](../../infrastructure/terraform/modules/ecr/main.tf#L24) |
| output: `output.urls` | `{ for k,v in aws_ecr_repository.ecr : k => v.repository_url }` | [код L25](../../infrastructure/terraform/modules/ecr/main.tf#L25) |

## module.frontend

| Вид / адреса | Вираз або призначення | Джерело |
|---|---|---|
| local: `local.buckets` | `{ frontend = aws_s3_bucket.frontend.id, artifacts = aws_s3_bucket.artifacts.id }` | [код L21](../../infrastructure/terraform/modules/frontend/main.tf#L21) |
| data: `data.aws_cloudfront_cache_policy.disabled` | Знаходить Managed-CachingDisabled policy для frontend dynamic/index та API. | [код L54](../../infrastructure/terraform/modules/frontend/main.tf#L54) |
| data: `data.aws_cloudfront_origin_request_policy.api` | Знаходить Managed-AllViewerExceptHostHeader policy для API forwarding. | [код L58](../../infrastructure/terraform/modules/frontend/main.tf#L58) |
| output: `output.domain` | `try(aws_cloudfront_distribution.this.domain_name, null)` | [код L169](../../infrastructure/terraform/modules/frontend/main.tf#L169) |
| output: `output.distribution_id` | `try(aws_cloudfront_distribution.this.id, null)` | [код L170](../../infrastructure/terraform/modules/frontend/main.tf#L170) |
| output: `output.bucket` | `try(aws_s3_bucket.frontend.id, null)` | [код L171](../../infrastructure/terraform/modules/frontend/main.tf#L171) |
| output: `output.artifact_bucket` | `try(aws_s3_bucket.artifacts.id, null)` | [код L172](../../infrastructure/terraform/modules/frontend/main.tf#L172) |
| output: `output.artifact_bucket_arn` | `try(aws_s3_bucket.artifacts.arn, null)` | [код L173](../../infrastructure/terraform/modules/frontend/main.tf#L173) |

## module.networking

| Вид / адреса | Вираз або призначення | Джерело |
|---|---|---|
| data: `data.aws_availability_zones.available` | Читає доступні AZ; local.zones бере перші2. Фактичний набір залежить від регіону/акаунта. | [код L8](../../infrastructure/terraform/modules/networking/main.tf#L8) |
| local: `local.zones` | `slice(data.aws_availability_zones.available.names, 0, 2)` | [код L9](../../infrastructure/terraform/modules/networking/main.tf#L9) |
| data: `data.aws_region.current` | Читає регіон успадкованого provider для regional service/prefix-list name. | [код L64](../../infrastructure/terraform/modules/networking/main.tf#L64) |
| output: `output.vpc_id` | `aws_vpc.this.id` | [код L71](../../infrastructure/terraform/modules/networking/main.tf#L71) |
| output: `output.public_subnet_ids` | `aws_subnet.public[*].id` | [код L72](../../infrastructure/terraform/modules/networking/main.tf#L72) |
| output: `output.private_subnet_ids` | `aws_subnet.private[*].id` | [код L76](../../infrastructure/terraform/modules/networking/main.tf#L76) |
| output: `output.availability_zone` | `local.zones[0]` | [код L80](../../infrastructure/terraform/modules/networking/main.tf#L80) |
| data: `data.aws_ec2_managed_prefix_list.cloudfront` | AWS-managed CloudFront origin-facing prefix list для ALB ingress; rule weight55. | [код L83](../../infrastructure/terraform/modules/networking/main.tf#L83) |
| output: `output.alb_sg` | `aws_security_group.alb.id` | [код L148](../../infrastructure/terraform/modules/networking/main.tf#L148) |
| output: `output.backend_sg` | `aws_security_group.backend.id` | [код L150](../../infrastructure/terraform/modules/networking/main.tf#L150) |
| output: `output.mysql_sg` | `aws_security_group.mysql.id` | [код L152](../../infrastructure/terraform/modules/networking/main.tf#L152) |

## root

| Вид / адреса | Вираз або призначення | Джерело |
|---|---|---|
| data: `data.aws_caller_identity.current` | Читає фактичний account з уже налаштованої AWS identity; AWS STS виклик у майбутньому HCP Plan, не offline обчислення. | [код L3](../../infrastructure/terraform/data.tf#L3) |
| local: `local.name` | `"climatehealth-${var.environment}-${var.name_suffix}"` | [код L1](../../infrastructure/terraform/main.tf#L1) |
| local: `local.tags` | `{ Project = "ClimateHealth", Environment = var.environment, ManagedBy = "Terraform" }` | [код L1](../../infrastructure/terraform/main.tf#L1) |
| output: `output.vpc_id` | `module.networking.vpc_id` | [код L1](../../infrastructure/terraform/output.tf#L1) |
| output: `output.cloudfront_domain` | `module.frontend.domain` | [код L2](../../infrastructure/terraform/output.tf#L2) |
| output: `output.cloudfront_distribution_id` | `module.frontend.distribution_id` | [код L3](../../infrastructure/terraform/output.tf#L3) |
| output: `output.frontend_bucket` | `module.frontend.bucket` | [код L4](../../infrastructure/terraform/output.tf#L4) |
| output: `output.artifact_bucket` | `module.frontend.artifact_bucket` | [код L5](../../infrastructure/terraform/output.tf#L5) |
| output: `output.ecr_urls` | `module.ecr.urls` | [код L6](../../infrastructure/terraform/output.tf#L6) |
| output: `output.database_endpoint` | `module.database.host` | [код L7](../../infrastructure/terraform/output.tf#L7) |
| output: `output.alb_dns` | `try(module.alb[0].dns, null)` | [код L8](../../infrastructure/terraform/output.tf#L8) |
| output: `output.ecs_cluster` | `try(module.backend[0].cluster, null)` | [код L9](../../infrastructure/terraform/output.tf#L9) |
| output: `output.ecs_service` | `try(module.backend[0].service, null)` | [код L10](../../infrastructure/terraform/output.tf#L10) |
| output: `output.backend_asg` | `try(module.backend[0].asg_name, null)` | [код L11](../../infrastructure/terraform/output.tf#L11) |
| output: `output.task_definition_arn` | `try(module.backend[0].task_definition_arn, null)` | [код L12](../../infrastructure/terraform/output.tf#L12) |
| output: `output.capacity_provider` | `try(module.backend[0].capacity_provider, null)` | [код L13](../../infrastructure/terraform/output.tf#L13) |
