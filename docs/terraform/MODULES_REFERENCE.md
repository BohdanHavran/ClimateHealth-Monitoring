# Data sources, locals та outputs

Усі допоміжні блоки активного коду. Expressions не виконувалися. Data sources читають AWS тільки під час майбутнього погодженого HCP run; зараз виконано лише читання локальних файлів.


## module.ai

| Вид / адреса | Вираз або призначення | Джерело |
|---|---|---|
| output: `output.private_ip` | `try(aws_instance.this[0].private_ip,null)` | [код L69](../../infrastructure/terraform/modules/ai/main.tf#L69) |

## module.alb

| Вид / адреса | Вираз або призначення | Джерело |
|---|---|---|
| output: `output.target_group_arn` | `aws_lb_target_group.backend.arn` | [код L73](../../infrastructure/terraform/modules/alb/main.tf#L73) |
| output: `output.listener_arn` | `aws_lb_listener_rule.origin.arn` | [код L74](../../infrastructure/terraform/modules/alb/main.tf#L74) |
| output: `output.dns` | `aws_lb.this.dns_name` | [код L75](../../infrastructure/terraform/modules/alb/main.tf#L75) |
| output: `output.zone_id` | `aws_lb.this.zone_id` | [код L77](../../infrastructure/terraform/modules/alb/main.tf#L77) |
| output: `output.arn` | `aws_lb.this.arn` | [код L79](../../infrastructure/terraform/modules/alb/main.tf#L79) |

## module.backend

| Вид / адреса | Вираз або призначення | Джерело |
|---|---|---|
| local: `local.ec2_trust` | `jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Service = "ec2.amazonaws.com" }, Action = "sts:AssumeRole" }] })` | [код L64](../../infrastructure/terraform/modules/ecs-backend/main.tf#L64) |
| local: `local.task_trust` | `jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" }, Action = "sts:AssumeRole" }] })` | [код L64](../../infrastructure/terraform/modules/ecs-backend/main.tf#L64) |
| output: `output.cluster` | `try(aws_ecs_cluster.this[0].name, null)` | [код L262](../../infrastructure/terraform/modules/ecs-backend/main.tf#L262) |
| output: `output.service` | `try(aws_ecs_service.this[0].name, null)` | [код L263](../../infrastructure/terraform/modules/ecs-backend/main.tf#L263) |
| output: `output.task_definition_arn` | `try(aws_ecs_task_definition.initial[0].arn, null)` | [код L265](../../infrastructure/terraform/modules/ecs-backend/main.tf#L265) |
| output: `output.task_role_arn` | `try(aws_iam_role.task[0].arn, null)` | [код L266](../../infrastructure/terraform/modules/ecs-backend/main.tf#L266) |
| output: `output.execution_role_arn` | `try(aws_iam_role.execution[0].arn, null)` | [код L267](../../infrastructure/terraform/modules/ecs-backend/main.tf#L267) |
| output: `output.asg_name` | `try(aws_autoscaling_group.host[0].name, null)` | [код L269](../../infrastructure/terraform/modules/ecs-backend/main.tf#L269) |
| output: `output.capacity_provider` | `try(aws_ecs_capacity_provider.host[0].name, null)` | [код L270](../../infrastructure/terraform/modules/ecs-backend/main.tf#L270) |

## module.database

| Вид / адреса | Вираз або призначення | Джерело |
|---|---|---|
| output: `output.host` | `try(var.mode == "rds" ? aws_db_instance.this[0].address : aws_instance.mysql[0].private_ip, null)` | [код L90](../../infrastructure/terraform/modules/mysql/main.tf#L90) |

## module.ecr

| Вид / адреса | Вираз або призначення | Джерело |
|---|---|---|
| output: `output.arns` | `{ for k,v in aws_ecr_repository.ecr : k => v.arn }` | [код L24](../../infrastructure/terraform/modules/ecr/main.tf#L24) |
| output: `output.urls` | `{ for k,v in aws_ecr_repository.ecr : k => v.repository_url }` | [код L25](../../infrastructure/terraform/modules/ecr/main.tf#L25) |

## module.frontend

| Вид / адреса | Вираз або призначення | Джерело |
|---|---|---|
| local: `local.buckets` | `var.storage_enabled ? { frontend = aws_s3_bucket.frontend[0].id, artifacts = aws_s3_bucket.artifacts[0].id } : {}` | [код L24](../../infrastructure/terraform/modules/frontend/main.tf#L24) |
| data: `data.aws_cloudfront_cache_policy.disabled` | Знаходить Managed-CachingDisabled policy для frontend dynamic/index та API. | [код L57](../../infrastructure/terraform/modules/frontend/main.tf#L57) |
| data: `data.aws_cloudfront_origin_request_policy.api` | Знаходить Managed-AllViewerExceptHostHeader policy для API forwarding. | [код L61](../../infrastructure/terraform/modules/frontend/main.tf#L61) |
| output: `output.domain` | `try(aws_cloudfront_distribution.this[0].domain_name, null)` | [код L172](../../infrastructure/terraform/modules/frontend/main.tf#L172) |
| output: `output.distribution_id` | `try(aws_cloudfront_distribution.this[0].id, null)` | [код L173](../../infrastructure/terraform/modules/frontend/main.tf#L173) |
| output: `output.bucket` | `try(aws_s3_bucket.frontend[0].id, null)` | [код L174](../../infrastructure/terraform/modules/frontend/main.tf#L174) |
| output: `output.artifact_bucket` | `try(aws_s3_bucket.artifacts[0].id, null)` | [код L175](../../infrastructure/terraform/modules/frontend/main.tf#L175) |
| output: `output.artifact_bucket_arn` | `try(aws_s3_bucket.artifacts[0].arn, null)` | [код L176](../../infrastructure/terraform/modules/frontend/main.tf#L176) |

## module.networking

| Вид / адреса | Вираз або призначення | Джерело |
|---|---|---|
| data: `data.aws_availability_zones.available` | Читає доступні AZ; local.zones бере перші2. Фактичний набір залежить від регіону/акаунта. | [код L16](../../infrastructure/terraform/modules/networking/main.tf#L16) |
| local: `local.zones` | `slice(data.aws_availability_zones.available.names, 0, 2)` | [код L17](../../infrastructure/terraform/modules/networking/main.tf#L17) |
| data: `data.aws_region.current` | Читає регіон успадкованого provider для regional service/prefix-list name. | [код L56](../../infrastructure/terraform/modules/networking/main.tf#L56) |
| output: `output.vpc_id` | `aws_vpc.this.id` | [код L63](../../infrastructure/terraform/modules/networking/main.tf#L63) |
| output: `output.public_subnet_ids` | `aws_subnet.public[*].id` | [код L64](../../infrastructure/terraform/modules/networking/main.tf#L64) |
| output: `output.private_subnet_ids` | `aws_subnet.private[*].id` | [код L68](../../infrastructure/terraform/modules/networking/main.tf#L68) |
| output: `output.availability_zone` | `local.zones[0]` | [код L72](../../infrastructure/terraform/modules/networking/main.tf#L72) |

## module.security

| Вид / адреса | Вираз або призначення | Джерело |
|---|---|---|
| data: `data.aws_ec2_managed_prefix_list.cloudfront` | AWS-managed CloudFront origin-facing prefix list для ALB ingress; rule weight55. | [код L7](../../infrastructure/terraform/modules/security/main.tf#L7) |
| data: `data.aws_region.current` | Читає регіон успадкованого provider для regional service/prefix-list name. | [код L80](../../infrastructure/terraform/modules/security/main.tf#L80) |
| data: `data.aws_prefix_list.s3` | Регіональний S3 prefix list для AI/MySQL egress rule. | [код L81](../../infrastructure/terraform/modules/security/main.tf#L81) |
| output: `output.alb_sg` | `aws_security_group.alb.id` | [код L90](../../infrastructure/terraform/modules/security/main.tf#L90) |
| output: `output.backend_sg` | `aws_security_group.backend.id` | [код L91](../../infrastructure/terraform/modules/security/main.tf#L91) |
| output: `output.mysql_sg` | `aws_security_group.mysql.id` | [код L92](../../infrastructure/terraform/modules/security/main.tf#L92) |
| output: `output.ai_sg` | `aws_security_group.ai.id` | [код L93](../../infrastructure/terraform/modules/security/main.tf#L93) |

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
| output: `output.alb_dns` | `try(module.alb[0].dns, null)` | [код L6](../../infrastructure/terraform/output.tf#L6) |
| output: `output.ecs_cluster` | `module.backend.cluster` | [код L7](../../infrastructure/terraform/output.tf#L7) |
| output: `output.ecs_service` | `module.backend.service` | [код L8](../../infrastructure/terraform/output.tf#L8) |
| output: `output.ecr_urls` | `module.ecr.urls` | [код L9](../../infrastructure/terraform/output.tf#L9) |
| output: `output.database_endpoint` | `module.database.host` | [код L10](../../infrastructure/terraform/output.tf#L10) |
| output: `output.ai_private_ip` | `module.ai.private_ip` | [код L11](../../infrastructure/terraform/output.tf#L11) |
| output: `output.reviewed_task_definition_arn` | `module.backend.task_definition_arn` | [код L13](../../infrastructure/terraform/output.tf#L13) |
| output: `output.backend_task_role_arn` | `module.backend.task_role_arn` | [код L14](../../infrastructure/terraform/output.tf#L14) |
| output: `output.backend_execution_role_arn` | `module.backend.execution_role_arn` | [код L15](../../infrastructure/terraform/output.tf#L15) |
| output: `output.alb_arn` | `try(module.alb[0].arn, null)` | [код L17](../../infrastructure/terraform/output.tf#L17) |
| output: `output.target_group_arn` | `try(module.alb[0].target_group_arn, null)` | [код L18](../../infrastructure/terraform/output.tf#L18) |
| output: `output.backend_asg` | `module.backend.asg_name` | [код L19](../../infrastructure/terraform/output.tf#L19) |
| output: `output.capacity_provider` | `module.backend.capacity_provider` | [код L20](../../infrastructure/terraform/output.tf#L20) |
| output: `output.private_subnet_ids` | `module.networking.private_subnet_ids` | [код L21](../../infrastructure/terraform/output.tf#L21) |
