# Повний довідник Terraform Variables

Джерело — активний root та всі шість child modules, lexical/static аналіз. Root variables задаються через HCP workspace variables/defaults; child variables заповнюють module arguments у main.tf. Child required=true НЕ означає нове required поле HCP UI. Внутрішні name/region/enabled є API модулів, не дублікати UI значень, які треба вводити двічі.

Required нижче означає «немає default»; це не те саме, що non-null або потрібний лише при count>0. Sensitive=true приховує звичайне відображення, але не шифрує самостійно state; тип string не гарантує, що secret не потрапив у Terraform. ARN metadata не є plaintext password. В усіх прикладах AWS identifiers треба брати лише з власних погоджених ресурсів; вигаданих AMI/account/ARN значень немає.

Used in містить прямі source-level consumers. Affects — транзитивний вплив на AWS resource blocks, включно з validations/provider tags; він не означає обовʼязкову зміну кожного ресурсу при кожному значенні. Структурні contains ребра виключені. Повні addresses дозволяють зіставити запис з DOT/RESOURCE аудитом.


## module.alb


### module.alb.vpc_id

| Поле | Пояснення |
|---|---|
| Variable | `vpc_id`; [код L2](../../infrastructure/terraform/modules/alb/main.tf#L2) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Ідентифікатор VPC з networking output для SG або ALB target group. |
| Used in | `module.alb::aws_lb_target_group.backend` |
| Affects | `module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_ecs_service.this`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`root::aws_route53_record.origin` |
| Example | `Root передає: module.networking.vpc_id` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.alb.subnet_ids

| Поле | Пояснення |
|---|---|
| Variable | `subnet_ids`; [код L5](../../infrastructure/terraform/modules/alb/main.tf#L5) |
| Type | `list(string)` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Список subnet IDs: ALBpublic pair або RDSprivate pair; EC2 MySQL бере першу private subnet. |
| Used in | `module.alb::aws_lb.this` |
| Affects | `module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.backend::aws_ecs_service.this`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`root::aws_route53_record.origin` |
| Example | `Root передає: module.networking.public_subnet_ids` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.alb.security_group

| Поле | Пояснення |
|---|---|
| Variable | `security_group`; [код L8](../../infrastructure/terraform/modules/alb/main.tf#L8) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | SG ID відповідного компонента з security output; не нове HCP поле. |
| Used in | `module.alb::aws_lb.this` |
| Affects | `module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.backend::aws_ecs_service.this`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`root::aws_route53_record.origin` |
| Example | `Root передає: module.networking.alb_sg` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.alb.certificate_arn

| Поле | Пояснення |
|---|---|
| Variable | `certificate_arn`; [код L11](../../infrastructure/terraform/modules/alb/main.tf#L11) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Внутрішній ALB input з root origin_certificate_arn. |
| Used in | `module.alb::aws_lb_listener.https` |
| Affects | `module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.backend::aws_ecs_service.this`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`root::aws_route53_record.origin` |
| Example | `Root передає: var.origin_certificate_arn` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.alb.origin_header

| Поле | Пояснення |
|---|---|
| Variable | `origin_header`; [код L14](../../infrastructure/terraform/modules/alb/main.tf#L14) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | true; metadata ARN не є secret value |
| Purpose | Внутрішня sensitive копія root origin_verification_header для ALB або CloudFront; не окремий секрет. |
| Used in | `module.alb::aws_lb_listener_rule.origin` |
| Affects | `module.alb::aws_lb_listener_rule.origin`<br>`module.backend::aws_ecs_service.this`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`root::aws_route53_record.origin` |
| Example | `Згенероване приватне значення; не публікувати і не копіювати з прикладу` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

## module.backend


### module.backend.name

| Поле | Пояснення |
|---|---|
| Variable | `name`; [код L2](../../infrastructure/terraform/modules/ecs-backend/main.tf#L2) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Внутрішнє складене імʼя з root local.name; застосовується до назв і tags відповідного child module. |
| Used in | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_launch_template.host` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host` |
| Example | `Root передає: local.name` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.region

| Поле | Пояснення |
|---|---|
| Variable | `region`; [код L5](../../infrastructure/terraform/modules/ecs-backend/main.tf#L5) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Child ECS awslogs region, переданий з root aws_region; не новий provider і не alias. |
| Used in | `module.backend::aws_ecs_task_definition.initial` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial` |
| Example | `Root передає: var.aws_region` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.tags

| Поле | Пояснення |
|---|---|
| Variable | `tags`; [код L8](../../infrastructure/terraform/modules/ecs-backend/main.tf#L8) |
| Type | `map(string)` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Project/Environment/ManagedBy для EC2 та EBS і ASG propagated tags. |
| Used in | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_launch_template.host` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_launch_template.host` |
| Example | `Root передає: local.tags` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.permissions_boundary_arn

| Поле | Пояснення |
|---|---|
| Variable | `permissions_boundary_arn`; [код L11](../../infrastructure/terraform/modules/ecs-backend/main.tf#L11) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Наявна погоджена IAM boundary для ECS host/execution roles; потрібна лише з API deployment. |
| Used in | `module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host` |
| Example | `Root передає: var.permissions_boundary_arn` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.ami_id

| Поле | Пояснення |
|---|---|
| Variable | `ami_id`; [код L14](../../infrastructure/terraform/modules/ecs-backend/main.tf#L14) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Child approved EC2 AMI ID, підставлений root для backend чи AI; null не можна запускати. |
| Used in | `module.backend::aws_launch_template.host` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_launch_template.host` |
| Example | `Root передає: var.ecs_ami_id` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.subnet_id

| Поле | Пояснення |
|---|---|
| Variable | `subnet_id`; [код L17](../../infrastructure/terraform/modules/ecs-backend/main.tf#L17) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Один subnet ID з networking output; backend public[0], AI private[0], це одна AZ. |
| Used in | `module.backend::aws_autoscaling_group.host` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this` |
| Example | `Root передає: module.networking.public_subnet_ids[0]` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.security_group

| Поле | Пояснення |
|---|---|
| Variable | `security_group`; [код L20](../../infrastructure/terraform/modules/ecs-backend/main.tf#L20) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | SG ID відповідного компонента з security output; не нове HCP поле. |
| Used in | `module.backend::aws_launch_template.host` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_launch_template.host` |
| Example | `Root передає: module.networking.backend_sg` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.target_group_arn

| Поле | Пояснення |
|---|---|
| Variable | `target_group_arn`; [код L23](../../infrastructure/terraform/modules/ecs-backend/main.tf#L23) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | ALB target group output або null при windowoff; потрібний активному ECS service. |
| Used in | `module.backend::aws_ecs_service.this` |
| Affects | `module.backend::aws_ecs_service.this` |
| Example | `Root передає: module.alb[0].target_group_arn` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.listener_rule_arn

| Поле | Пояснення |
|---|---|
| Variable | `listener_rule_arn`; [код L26](../../infrastructure/terraform/modules/ecs-backend/main.tf#L26) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Точна залежність готовності HTTPS forwarding rule перед ECS service. |
| Used in | `module.backend::aws_ecs_service.this` |
| Affects | `module.backend::aws_ecs_service.this` |
| Example | `Root передає: module.alb[0].listener_rule_arn` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.image

| Поле | Пояснення |
|---|---|
| Variable | `image`; [код L29](../../infrastructure/terraform/modules/ecs-backend/main.tf#L29) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Внутрішня копія immutable backend_image для container definition. |
| Used in | `module.backend::aws_ecs_task_definition.initial` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial` |
| Example | `Root передає: var.backend_image` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.desired_count

| Поле | Пояснення |
|---|---|
| Variable | `desired_count`; [код L32](../../infrastructure/terraform/modules/ecs-backend/main.tf#L32) |
| Type | `number` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Бажана кількість ECS tasks 0/1; також min_size ASG, desired_capacity далі керує Capacity Provider. |
| Used in | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_service.this` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this` |
| Example | `Root передає: var.backend_desired_count` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.max_instances

| Поле | Пояснення |
|---|---|
| Variable | `max_instances`; [код L35](../../infrastructure/terraform/modules/ecs-backend/main.tf#L35) |
| Type | `number` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Максимальна кількість EC2 у backend ASG, не постійна кількість серверів. |
| Used in | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_service.this` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this` |
| Example | `Root передає: var.backend_max_instances` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.repository_arn

| Поле | Пояснення |
|---|---|
| Variable | `repository_arn`; [код L38](../../infrastructure/terraform/modules/ecs-backend/main.tf#L38) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | ARN єдиного backend ECR repository для scoped pull permissions. |
| Used in | `module.backend::aws_iam_role_policy.execution` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_iam_role_policy.execution` |
| Example | `Root передає: module.ecr.arns["${local.name}-backend"]` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.secret_arns

| Поле | Пояснення |
|---|---|
| Variable | `secret_arns`; [код L41](../../infrastructure/terraform/modules/ecs-backend/main.tf#L41) |
| Type | `map(string)` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Map runtime SSM ARN references для execution IAM та task secrets injection; самі значення паролів не передаються Terraform. |
| Used in | `module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_role_policy.execution` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_role_policy.execution` |
| Example | `Root передає: var.runtime_secret_arns` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.db_host

| Поле | Пояснення |
|---|---|
| Variable | `db_host`; [код L44](../../infrastructure/terraform/modules/ecs-backend/main.tf#L44) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Endpoint address/private IP з database output для DB_HOST у task definition. |
| Used in | `module.backend::aws_ecs_task_definition.initial` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial` |
| Example | `Root передає: module.database.host` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.log_group_name

| Поле | Пояснення |
|---|---|
| Variable | `log_group_name`; [код L47](../../infrastructure/terraform/modules/ecs-backend/main.tf#L47) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Ім’я незалежно збереженої root CloudWatch log group. |
| Used in | `module.backend::aws_ecs_task_definition.initial` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial` |
| Example | `Root передає: aws_cloudwatch_log_group.backend.name` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.log_group_arn

| Поле | Пояснення |
|---|---|
| Variable | `log_group_arn`; [код L50](../../infrastructure/terraform/modules/ecs-backend/main.tf#L50) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | ARN збереженої log group для scoped execution IAM permissions. |
| Used in | `module.backend::aws_iam_role_policy.execution` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_iam_role_policy.execution` |
| Example | `Root передає: aws_cloudwatch_log_group.backend.arn` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

## module.database


### module.database.name

| Поле | Пояснення |
|---|---|
| Variable | `name`; [код L1](../../infrastructure/terraform/modules/mysql/main.tf#L1) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Внутрішнє складене імʼя з root local.name; застосовується до назв і tags відповідного child module. |
| Used in | `module.database::aws_db_instance.this` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.database::aws_db_instance.this` |
| Example | `Root передає: local.name` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.database.subnet_ids

| Поле | Пояснення |
|---|---|
| Variable | `subnet_ids`; [код L4](../../infrastructure/terraform/modules/mysql/main.tf#L4) |
| Type | `list(string)` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Список subnet IDs: ALBpublic pair або RDSprivate pair; EC2 MySQL бере першу private subnet. |
| Used in | `module.database::aws_db_subnet_group.this` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_subnet_group.this` |
| Example | `Root передає: module.networking.private_subnet_ids` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.database.security_group

| Поле | Пояснення |
|---|---|
| Variable | `security_group`; [код L7](../../infrastructure/terraform/modules/mysql/main.tf#L7) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | SG ID відповідного компонента з security output; не нове HCP поле. |
| Used in | `module.database::aws_db_instance.this` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.database::aws_db_instance.this` |
| Example | `Root передає: module.networking.mysql_sg` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.database.availability_zone

| Поле | Пояснення |
|---|---|
| Variable | `availability_zone`; [код L10](../../infrastructure/terraform/modules/mysql/main.tf#L10) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Перша обрана networking AZ для Single-AZ RDS; дві subnet group не роблять DB Multi-AZ. |
| Used in | `module.database::aws_db_instance.this` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.database::aws_db_instance.this` |
| Example | `Root передає: module.networking.availability_zone` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

## module.ecr


### module.ecr.ecr_names

| Поле | Пояснення |
|---|---|
| Variable | `ecr_names`; [код L1](../../infrastructure/terraform/modules/ecr/variable.tf#L1) |
| Type | `list(string)` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Два імені ECR repositories, сформовані root; for_each keys відомі з inputs. |
| Used in | `module.ecr::aws_ecr_repository.ecr` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr` |
| Example | `Root передає: ["${local.name}-backend"]` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

## module.frontend


### module.frontend.api_enabled

| Поле | Пояснення |
|---|---|
| Variable | `api_enabled`; [код L2](../../infrastructure/terraform/modules/frontend/main.tf#L2) |
| Type | `bool` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Додає API origin/behavior до постійного CloudFront; S3 frontend залишається. |
| Used in | `module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::data.aws_cloudfront_origin_request_policy.api` |
| Affects | `module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend` |
| Example | `Root передає: var.deploy_application` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.frontend.name

| Поле | Пояснення |
|---|---|
| Variable | `name`; [код L3](../../infrastructure/terraform/modules/frontend/main.tf#L3) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Внутрішнє складене імʼя з root local.name; застосовується до назв і tags відповідного child module. |
| Used in | `module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend` |
| Affects | `module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this` |
| Example | `Root передає: local.name` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.frontend.origin_hostname

| Поле | Пояснення |
|---|---|
| Variable | `origin_hostname`; [код L6](../../infrastructure/terraform/modules/frontend/main.tf#L6) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Справжнє origin DNS імʼя для CloudFront, ACM та Route53 alias; certificate/DNS zone існують поза root. |
| Used in | `module.frontend::aws_cloudfront_distribution.this` |
| Affects | `module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend` |
| Example | `Root передає: var.deploy_application ? trimsuffix(aws_route53_record.origin[0].fqdn, ".") : null` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.frontend.origin_header

| Поле | Пояснення |
|---|---|
| Variable | `origin_header`; [код L9](../../infrastructure/terraform/modules/frontend/main.tf#L9) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | true; metadata ARN не є secret value |
| Purpose | Внутрішня sensitive копія root origin_verification_header для ALB або CloudFront; не окремий секрет. |
| Used in | `module.frontend::aws_cloudfront_distribution.this` |
| Affects | `module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend` |
| Example | `Згенероване приватне значення; не публікувати і не копіювати з прикладу` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

## module.networking


### module.networking.name

| Поле | Пояснення |
|---|---|
| Variable | `name`; [код L2](../../infrastructure/terraform/modules/networking/main.tf#L2) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Внутрішнє складене імʼя з root local.name; застосовується до назв і tags відповідного child module. |
| Used in | `module.networking::aws_internet_gateway.this`<br>`module.networking::aws_security_group.alb`<br>`module.networking::aws_security_group.backend`<br>`module.networking::aws_security_group.mysql`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this` |
| Affects | `module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_security_group.alb`<br>`module.networking::aws_security_group.backend`<br>`module.networking::aws_security_group.mysql`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.networking::aws_vpc_security_group_egress_rule.database`<br>`module.networking::aws_vpc_security_group_egress_rule.https`<br>`module.networking::aws_vpc_security_group_egress_rule.targets`<br>`module.networking::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.networking::aws_vpc_security_group_ingress_rule.database`<br>`module.networking::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `Root передає: local.name` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.networking.vpc_cidr

| Поле | Пояснення |
|---|---|
| Variable | `vpc_cidr`; [код L5](../../infrastructure/terraform/modules/networking/main.tf#L5) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | IPv4 /16, з якого обчислюються дві public і дві private /24 subnets. |
| Used in | `module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this` |
| Affects | `module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_security_group.alb`<br>`module.networking::aws_security_group.backend`<br>`module.networking::aws_security_group.mysql`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.networking::aws_vpc_security_group_egress_rule.database`<br>`module.networking::aws_vpc_security_group_egress_rule.https`<br>`module.networking::aws_vpc_security_group_egress_rule.targets`<br>`module.networking::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.networking::aws_vpc_security_group_ingress_rule.database`<br>`module.networking::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `Root передає: var.vpc_cidr` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

## root


### root.environment

| Поле | Пояснення |
|---|---|
| Variable | `environment`; [код L1](../../infrastructure/terraform/variable.tf#L1) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Ізоляція імен і Environment tags; dev або production, це не вибір Terraform CLI workspace. |
| Used in | `root::local.name`<br>`root::local.tags`<br>`root::provider.aws`<br>`root::var.backend_image` |
| Affects | `module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_security_group.alb`<br>`module.networking::aws_security_group.backend`<br>`module.networking::aws_security_group.mysql`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.networking::aws_vpc_security_group_egress_rule.database`<br>`module.networking::aws_vpc_security_group_egress_rule.https`<br>`module.networking::aws_vpc_security_group_egress_rule.targets`<br>`module.networking::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.networking::aws_vpc_security_group_ingress_rule.database`<br>`module.networking::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_cloudwatch_log_group.backend`<br>`root::aws_route53_record.origin` |
| Example | `dev або production` |
| Recommendation | Залишити. |

### root.aws_region

| Поле | Пояснення |
|---|---|
| Variable | `aws_region`; [код L9](../../infrastructure/terraform/variable.tf#L9) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Регіон provider/logging/SSM validation; без default, validator наразі допускає кошторисний us-east-1. |
| Used in | `root::module.backend.input.region`<br>`root::provider.aws`<br>`root::var.backend_image`<br>`root::var.runtime_secret_arns` |
| Affects | `module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_security_group.alb`<br>`module.networking::aws_security_group.backend`<br>`module.networking::aws_security_group.mysql`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.networking::aws_vpc_security_group_egress_rule.database`<br>`module.networking::aws_vpc_security_group_egress_rule.https`<br>`module.networking::aws_vpc_security_group_egress_rule.targets`<br>`module.networking::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.networking::aws_vpc_security_group_ingress_rule.database`<br>`module.networking::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_cloudwatch_log_group.backend`<br>`root::aws_route53_record.origin` |
| Example | `us-east-1 — тільки після погодження` |
| Recommendation | Залишити. |

### root.name_suffix

| Поле | Пояснення |
|---|---|
| Variable | `name_suffix`; [код L18](../../infrastructure/terraform/variable.tf#L18) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Унікальна частина всіх імен; потрібна насамперед для глобально унікальних S3 buckets. |
| Used in | `root::local.name`<br>`root::var.backend_image` |
| Affects | `module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_security_group.alb`<br>`module.networking::aws_security_group.backend`<br>`module.networking::aws_security_group.mysql`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.networking::aws_vpc_security_group_egress_rule.database`<br>`module.networking::aws_vpc_security_group_egress_rule.https`<br>`module.networking::aws_vpc_security_group_egress_rule.targets`<br>`module.networking::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.networking::aws_vpc_security_group_ingress_rule.database`<br>`module.networking::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_cloudwatch_log_group.backend`<br>`root::aws_route53_record.origin` |
| Example | `demo26 — лише приклад suffix, глобальну унікальність перевірити` |
| Recommendation | Залишити. |

### root.vpc_cidr

| Поле | Пояснення |
|---|---|
| Variable | `vpc_cidr`; [код L26](../../infrastructure/terraform/variable.tf#L26) |
| Type | `string` |
| Default | `"10.42.0.0/16"` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | IPv4 /16, з якого обчислюються дві public і дві private /24 subnets. |
| Used in | `root::module.networking.input.vpc_cidr` |
| Affects | `module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_security_group.alb`<br>`module.networking::aws_security_group.backend`<br>`module.networking::aws_security_group.mysql`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.networking::aws_vpc_security_group_egress_rule.database`<br>`module.networking::aws_vpc_security_group_egress_rule.https`<br>`module.networking::aws_vpc_security_group_egress_rule.targets`<br>`module.networking::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.networking::aws_vpc_security_group_ingress_rule.database`<br>`module.networking::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `"10.42.0.0/16"` |
| Recommendation | Залишити. |

### root.deploy_application

| Поле | Пояснення |
|---|---|
| Variable | `deploy_application`; [код L35](../../infrastructure/terraform/variable.tf#L35) |
| Type | `bool` |
| Default | `false` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Створення API compute, ALB, DNS та API origin; не керує життєвим циклом RDS чи сховищ. |
| Used in | `root::aws_route53_record.origin`<br>`root::module.alb`<br>`root::module.backend`<br>`root::module.frontend.input.api_enabled`<br>`root::module.frontend.input.origin_hostname`<br>`root::var.backend_desired_count`<br>`root::var.backend_image`<br>`root::var.ecs_ami_id`<br>`root::var.origin_certificate_arn`<br>`root::var.origin_hostname`<br>`root::var.origin_verification_header`<br>`root::var.origin_zone_id`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns` |
| Affects | `module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`root::aws_route53_record.origin` |
| Example | `false` |
| Recommendation | Залишити. |

### root.backend_desired_count

| Поле | Пояснення |
|---|---|
| Variable | `backend_desired_count`; [код L41](../../infrastructure/terraform/variable.tf#L41) |
| Type | `number` |
| Default | `0` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Нуль під час bootstrap Capacity Provider, один після перевірки його готовності. |
| Used in | `root::module.backend.input.desired_count` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this` |
| Example | `0` |
| Recommendation | Залишити. |

### root.backend_max_instances

| Поле | Пояснення |
|---|---|
| Variable | `backend_max_instances`; [код L50](../../infrastructure/terraform/variable.tf#L50) |
| Type | `number` |
| Default | `1` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Стеля ASG: один host або погоджений тимчасовий другий для deployment. |
| Used in | `root::module.backend.input.max_instances` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this` |
| Example | `1` |
| Recommendation | Залишити. |

### root.backend_image

| Поле | Пояснення |
|---|---|
| Variable | `backend_image`; [код L59](../../infrastructure/terraform/variable.tf#L59) |
| Type | `string` |
| Default | `null` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Initial ECR image URI з immutable digest для task definition; не будує і не завантажує image. |
| Used in | `root::module.backend.input.image` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial` |
| Example | `null` |
| Recommendation | Залишити. |

### root.ecs_ami_id

| Поле | Пояснення |
|---|---|
| Variable | `ecs_ami_id`; [код L68](../../infrastructure/terraform/variable.tf#L68) |
| Type | `string` |
| Default | `null` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Pinned ECS-optimized AL2023 x86 AMI; image та agent readiness перевіряються окремо. |
| Used in | `root::module.backend.input.ami_id` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_launch_template.host` |
| Example | `null` |
| Recommendation | Залишити. |

### root.origin_hostname

| Поле | Пояснення |
|---|---|
| Variable | `origin_hostname`; [код L77](../../infrastructure/terraform/variable.tf#L77) |
| Type | `string` |
| Default | `null` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Справжнє origin DNS імʼя для CloudFront, ACM та Route53 alias; certificate/DNS zone існують поза root. |
| Used in | `root::aws_route53_record.origin` |
| Affects | `module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`root::aws_route53_record.origin` |
| Example | `null` |
| Recommendation | Залишити. |

### root.origin_zone_id

| Поле | Пояснення |
|---|---|
| Variable | `origin_zone_id`; [код L86](../../infrastructure/terraform/variable.tf#L86) |
| Type | `string` |
| Default | `null` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | ID наявної public Route53 zone, куди записується origin alias; не створює zone. |
| Used in | `root::aws_route53_record.origin` |
| Affects | `module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`root::aws_route53_record.origin` |
| Example | `null` |
| Recommendation | Залишити. |

### root.origin_certificate_arn

| Поле | Пояснення |
|---|---|
| Variable | `origin_certificate_arn`; [код L95](../../infrastructure/terraform/variable.tf#L95) |
| Type | `string` |
| Default | `null` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | ARN уже виданого ACM certificate для HTTPS ALB; перевіряються shape/region/account, не факт issuance. |
| Used in | `root::module.alb.input.certificate_arn` |
| Affects | `module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.backend::aws_ecs_service.this`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`root::aws_route53_record.origin` |
| Example | `null` |
| Recommendation | Залишити. |

### root.origin_verification_header

| Поле | Пояснення |
|---|---|
| Variable | `origin_verification_header`; [код L104](../../infrastructure/terraform/variable.tf#L104) |
| Type | `string` |
| Default | `null` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | true; metadata ARN не є secret value |
| Purpose | Випадковий sensitive URL-safe header 32–128 символів без wildcard/пробілів; потрібний лише API. |
| Used in | `root::module.alb.input.origin_header`<br>`root::module.frontend.input.origin_header` |
| Affects | `module.alb::aws_lb_listener_rule.origin`<br>`module.backend::aws_ecs_service.this`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`root::aws_route53_record.origin` |
| Example | `null` |
| Recommendation | Залишити. |

### root.runtime_secret_arns

| Поле | Пояснення |
|---|---|
| Variable | `runtime_secret_arns`; [код L114](../../infrastructure/terraform/variable.tf#L114) |
| Type | `map(string)` |
| Default | `{}` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | SSM references DB_USER/DB_PASS до окремого RDS reader; не plaintext credentials. |
| Used in | `root::module.backend.input.secret_arns` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_role_policy.execution` |
| Example | `{}` |
| Recommendation | Залишити. |

### root.permissions_boundary_arn

| Поле | Пояснення |
|---|---|
| Variable | `permissions_boundary_arn`; [код L123](../../infrastructure/terraform/variable.tf#L123) |
| Type | `string` |
| Default | `null` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Наявна погоджена IAM boundary для ECS host/execution roles; потрібна лише з API deployment. |
| Used in | `root::module.backend.input.permissions_boundary_arn` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host` |
| Example | `null` |
| Recommendation | Залишити. |

## Невикористані та схожі за назвою

Немає явних споживачів/посилань.

Root inputs задаються один раз у HCP, child inputs передає root. deploy_application керує лише API compute/ALB/DNS/CDN API origin; backend_desired_count задає 0 або 1 task, backend_max_instances — стелю ASG 1 або 2. RDS, S3, ECR, CloudFront і журнали зберігаються незалежно. AI inputs відкладені до реальної потреби. [Поточні HCP inputs](../HCP_TERRAFORM.md); [порядок deployment](VARIANT_B_REPORT.md).
