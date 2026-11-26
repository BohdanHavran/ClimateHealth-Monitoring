# Повний довідник Terraform Variables

Джерело — активний root та всі8child modules, lexical/static аналіз. Root variables задаються через HCP workspace variables/defaults; child variables заповнюють module arguments у main.tf. Child required=true НЕ означає нове required поле HCP UI. Внутрішні name/region/enabled є API модулів, не дублікати UI значень, які треба вводити двічі.

Required нижче означає «немає default»; це не те саме, що non-null або потрібний лише при count>0. Sensitive=true приховує звичайне відображення, але не шифрує самостійно state; тип string не гарантує, що secret не потрапив у Terraform. ARN metadata не є plaintext password. В усіх прикладах AWS identifiers треба брати лише з власних погоджених ресурсів; вигаданих AMI/account/ARN значень немає.

Used in містить прямі source-level consumers. Affects — транзитивний вплив на AWS resource blocks, включно з validations/provider tags; він не означає обовʼязкову зміну кожного ресурсу при кожному значенні. Структурні contains ребра виключені. Повні addresses дозволяють зіставити запис з DOT/RESOURCE аудитом.


## module.ai


### module.ai.provisioned

| Поле | Пояснення |
|---|---|
| Variable | `provisioned`; [код L1](../../infrastructure/terraform/modules/ai/main.tf#L1) |
| Type | `bool` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Child перемикач створення ресурсів, який root передає з відповідного provisioning gate. |
| Used in | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this` |
| Example | `Root передає: var.ai_provisioned` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.ai.tags

| Поле | Пояснення |
|---|---|
| Variable | `tags`; [код L2](../../infrastructure/terraform/modules/ai/main.tf#L2) |
| Type | `map(string)` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Project/Environment/ManagedBy для EC2 та EBS і ASG propagated tags. |
| Used in | `module.ai::aws_instance.this` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_instance.this` |
| Example | `Root передає: local.tags` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.ai.permissions_boundary_arn

| Поле | Пояснення |
|---|---|
| Variable | `permissions_boundary_arn`; [код L3](../../infrastructure/terraform/modules/ai/main.tf#L3) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | ARN наявної IAM permissions boundary для5 ролей; її зміст root не створює і не доводить least privilege. |
| Used in | `module.ai::aws_iam_role.this` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this` |
| Example | `Root передає: var.permissions_boundary_arn` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.ai.name

| Поле | Пояснення |
|---|---|
| Variable | `name`; [код L6](../../infrastructure/terraform/modules/ai/main.tf#L6) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Внутрішнє складене імʼя з root local.name; застосовується до назв і tags відповідного child module. |
| Used in | `module.ai::aws_iam_role.this` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this` |
| Example | `Root передає: local.name` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.ai.enabled

| Поле | Пояснення |
|---|---|
| Variable | `enabled`; [код L9](../../infrastructure/terraform/modules/ai/main.tf#L9) |
| Type | `bool` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Child activity gate: ECR створення, backend capacity, AI power state — залежить від модуля. |
| Used in | `module.ai::aws_ec2_instance_state.power` |
| Affects | `module.ai::aws_ec2_instance_state.power` |
| Example | `Root передає: var.ai_enabled` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.ai.ami_id

| Поле | Пояснення |
|---|---|
| Variable | `ami_id`; [код L12](../../infrastructure/terraform/modules/ai/main.tf#L12) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Child approved EC2 AMI ID, підставлений root для backend чи AI; null не можна запускати. |
| Used in | `module.ai::aws_instance.this` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_instance.this` |
| Example | `Root передає: var.ai_ami_id` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.ai.instance_type

| Поле | Пояснення |
|---|---|
| Variable | `instance_type`; [код L15](../../infrastructure/terraform/modules/ai/main.tf#L15) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Child EC2 CPU/RAM size, підставлений з відповідного root input. |
| Used in | `module.ai::aws_instance.this` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_instance.this` |
| Example | `Root передає: var.ai_instance_type` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.ai.subnet_id

| Поле | Пояснення |
|---|---|
| Variable | `subnet_id`; [код L18](../../infrastructure/terraform/modules/ai/main.tf#L18) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Один subnet ID з networking output; backend public[0], AI private[0], це одна AZ. |
| Used in | `module.ai::aws_instance.this` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_instance.this` |
| Example | `Root передає: module.networking.private_subnet_ids[0]` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.ai.security_group

| Поле | Пояснення |
|---|---|
| Variable | `security_group`; [код L21](../../infrastructure/terraform/modules/ai/main.tf#L21) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | SG ID відповідного компонента з security output; не нове HCP поле. |
| Used in | `module.ai::aws_instance.this` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_instance.this` |
| Example | `Root передає: module.security.ai_sg` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.ai.artifact_bucket_arn

| Поле | Пояснення |
|---|---|
| Variable | `artifact_bucket_arn`; [код L24](../../infrastructure/terraform/modules/ai/main.tf#L24) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | ARN artifact bucket з frontend output для scoped AI/DB backup S3 permissions. |
| Used in | `module.ai::aws_iam_role_policy.read` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this` |
| Example | `Root передає: module.frontend.artifact_bucket_arn` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

## module.alb


### module.alb.name

| Поле | Пояснення |
|---|---|
| Variable | `name`; [код L1](../../infrastructure/terraform/modules/alb/main.tf#L1) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Внутрішнє складене імʼя з root local.name; застосовується до назв і tags відповідного child module. |
| Used in | Немає явних споживачів/посилань. |
| Affects | Не має транзитивних AWS consumers; може лише блокувати Plan або бути невикористаною. |
| Example | `Root передає: local.name` |
| Recommendation | Невикористана. Запропоновано видалити окремо; в межах цього аудиту не прибирати інші API inputs. |

### module.alb.vpc_id

| Поле | Пояснення |
|---|---|
| Variable | `vpc_id`; [код L4](../../infrastructure/terraform/modules/alb/main.tf#L4) |
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
| Variable | `subnet_ids`; [код L7](../../infrastructure/terraform/modules/alb/main.tf#L7) |
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
| Variable | `security_group`; [код L10](../../infrastructure/terraform/modules/alb/main.tf#L10) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | SG ID відповідного компонента з security output; не нове HCP поле. |
| Used in | `module.alb::aws_lb.this` |
| Affects | `module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.backend::aws_ecs_service.this`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`root::aws_route53_record.origin` |
| Example | `Root передає: module.security.alb_sg` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.alb.certificate_arn

| Поле | Пояснення |
|---|---|
| Variable | `certificate_arn`; [код L13](../../infrastructure/terraform/modules/alb/main.tf#L13) |
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
| Variable | `origin_header`; [код L16](../../infrastructure/terraform/modules/alb/main.tf#L16) |
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


### module.backend.provisioned

| Поле | Пояснення |
|---|---|
| Variable | `provisioned`; [код L1](../../infrastructure/terraform/modules/ecs-backend/main.tf#L1) |
| Type | `bool` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Child перемикач створення ресурсів, який root передає з відповідного provisioning gate. |
| Used in | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host` |
| Example | `Root передає: var.backend_provisioned` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.tags

| Поле | Пояснення |
|---|---|
| Variable | `tags`; [код L2](../../infrastructure/terraform/modules/ecs-backend/main.tf#L2) |
| Type | `map(string)` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Project/Environment/ManagedBy для EC2 та EBS і ASG propagated tags. |
| Used in | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_launch_template.host` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_launch_template.host` |
| Example | `Root передає: local.tags` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.ml_service_url

| Поле | Пояснення |
|---|---|
| Variable | `ml_service_url`; [код L3](../../infrastructure/terraform/modules/ecs-backend/main.tf#L3) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Погоджений приватний HTTPS endpoint AI; null залишає сервіс чесно не налаштованим. |
| Used in | `module.backend::aws_ecs_task_definition.initial` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial` |
| Example | `Root передає: var.ml_service_url` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.ml_tls_ca_file

| Поле | Пояснення |
|---|---|
| Variable | `ml_tls_ca_file`; [код L4](../../infrastructure/terraform/modules/ecs-backend/main.tf#L4) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Необовʼязковий шлях до CA, уже включеного у backend image для приватного ML TLS. |
| Used in | `module.backend::aws_ecs_task_definition.initial` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial` |
| Example | `Root передає: var.ml_tls_ca_file` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.permissions_boundary_arn

| Поле | Пояснення |
|---|---|
| Variable | `permissions_boundary_arn`; [код L5](../../infrastructure/terraform/modules/ecs-backend/main.tf#L5) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | ARN наявної IAM permissions boundary для5 ролей; її зміст root не створює і не доводить least privilege. |
| Used in | `module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host` |
| Example | `Root передає: var.permissions_boundary_arn` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.name

| Поле | Пояснення |
|---|---|
| Variable | `name`; [код L8](../../infrastructure/terraform/modules/ecs-backend/main.tf#L8) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Внутрішнє складене імʼя з root local.name; застосовується до назв і tags відповідного child module. |
| Used in | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_launch_template.host` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host` |
| Example | `Root передає: local.name` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.region

| Поле | Пояснення |
|---|---|
| Variable | `region`; [код L11](../../infrastructure/terraform/modules/ecs-backend/main.tf#L11) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Child ECS awslogs region, переданий з root aws_region; не новий provider і не alias. |
| Used in | `module.backend::aws_ecs_task_definition.initial` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial` |
| Example | `Root передає: var.aws_region` |
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

### module.backend.instance_type

| Поле | Пояснення |
|---|---|
| Variable | `instance_type`; [код L17](../../infrastructure/terraform/modules/ecs-backend/main.tf#L17) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Child EC2 CPU/RAM size, підставлений з відповідного root input. |
| Used in | `module.backend::aws_launch_template.host` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_launch_template.host` |
| Example | `Root передає: var.backend_instance_type` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.subnet_id

| Поле | Пояснення |
|---|---|
| Variable | `subnet_id`; [код L20](../../infrastructure/terraform/modules/ecs-backend/main.tf#L20) |
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
| Variable | `security_group`; [код L23](../../infrastructure/terraform/modules/ecs-backend/main.tf#L23) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | SG ID відповідного компонента з security output; не нове HCP поле. |
| Used in | `module.backend::aws_launch_template.host` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_launch_template.host` |
| Example | `Root передає: module.security.backend_sg` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.target_group_arn

| Поле | Пояснення |
|---|---|
| Variable | `target_group_arn`; [код L26](../../infrastructure/terraform/modules/ecs-backend/main.tf#L26) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | ALB target group output або null при windowoff; потрібний активному ECS service. |
| Used in | `module.backend::aws_ecs_service.this` |
| Affects | `module.backend::aws_ecs_service.this` |
| Example | `Root передає: try(module.alb[0].target_group_arn, null)` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.listener_arn

| Поле | Пояснення |
|---|---|
| Variable | `listener_arn`; [код L29](../../infrastructure/terraform/modules/ecs-backend/main.tf#L29) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | ALB listener-rule ARN у lifecycle precondition ECS service; вузька залежність готовності ALB. |
| Used in | `module.backend::aws_ecs_service.this` |
| Affects | `module.backend::aws_ecs_service.this` |
| Example | `Root передає: try(module.alb[0].listener_arn, null)` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.image

| Поле | Пояснення |
|---|---|
| Variable | `image`; [код L32](../../infrastructure/terraform/modules/ecs-backend/main.tf#L32) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Внутрішня копія immutable backend_image для container definition. |
| Used in | `module.backend::aws_ecs_task_definition.initial` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial` |
| Example | `Root передає: var.backend_image` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.active_window

| Поле | Пояснення |
|---|---|
| Variable | `active_window`; [код L35](../../infrastructure/terraform/modules/ecs-backend/main.tf#L35) |
| Type | `bool` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Child умова count ECS service object; відрізняється від enabled/desired_count. |
| Used in | `module.backend::aws_ecs_service.this` |
| Affects | `module.backend::aws_ecs_service.this` |
| Example | `Root передає: var.application_window_open` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.enabled

| Поле | Пояснення |
|---|---|
| Variable | `enabled`; [код L38](../../infrastructure/terraform/modules/ecs-backend/main.tf#L38) |
| Type | `bool` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Child activity gate: ECR створення, backend capacity, AI power state — залежить від модуля. |
| Used in | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_service.this` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this` |
| Example | `Root передає: var.service_enabled && var.application_window_open` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.task_memory

| Поле | Пояснення |
|---|---|
| Variable | `task_memory`; [код L41](../../infrastructure/terraform/modules/ecs-backend/main.tf#L41) |
| Type | `number` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Child container hard memory у MiB з root task_memory_mib. |
| Used in | `module.backend::aws_ecs_task_definition.initial` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial` |
| Example | `Root передає: var.task_memory_mib` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.extra_capacity

| Поле | Пояснення |
|---|---|
| Variable | `extra_capacity`; [код L44](../../infrastructure/terraform/modules/ecs-backend/main.tf#L44) |
| Type | `bool` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Child копія allow_deployment_capacity для ASGmax і ECS deployment percent. |
| Used in | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_service.this` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this` |
| Example | `Root передає: var.allow_deployment_capacity` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.repository_arns

| Поле | Пояснення |
|---|---|
| Variable | `repository_arns`; [код L47](../../infrastructure/terraform/modules/ecs-backend/main.tf#L47) |
| Type | `list(string)` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Scoped ECR repository ARNs для execution pull permissions; включає і AI repository. |
| Used in | `module.backend::aws_iam_role_policy.execution` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_iam_role_policy.execution` |
| Example | `Root передає: values(module.ecr.arns)` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.backend.secret_arns

| Поле | Пояснення |
|---|---|
| Variable | `secret_arns`; [код L50](../../infrastructure/terraform/modules/ecs-backend/main.tf#L50) |
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
| Variable | `db_host`; [код L53](../../infrastructure/terraform/modules/ecs-backend/main.tf#L53) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Endpoint address/private IP з database output для DB_HOST у task definition. |
| Used in | `module.backend::aws_ecs_task_definition.initial` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial` |
| Example | `Root передає: module.database.host` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

## module.database


### module.database.provisioned

| Поле | Пояснення |
|---|---|
| Variable | `provisioned`; [код L1](../../infrastructure/terraform/modules/mysql/main.tf#L1) |
| Type | `bool` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Child перемикач створення ресурсів, який root передає з відповідного provisioning gate. |
| Used in | `module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql` |
| Example | `Root передає: var.database_provisioned` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.database.permissions_boundary_arn

| Поле | Пояснення |
|---|---|
| Variable | `permissions_boundary_arn`; [код L2](../../infrastructure/terraform/modules/mysql/main.tf#L2) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | ARN наявної IAM permissions boundary для5 ролей; її зміст root не створює і не доводить least privilege. |
| Used in | `module.database::aws_iam_role.backup` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql` |
| Example | `Root передає: var.permissions_boundary_arn` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.database.name

| Поле | Пояснення |
|---|---|
| Variable | `name`; [код L5](../../infrastructure/terraform/modules/mysql/main.tf#L5) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Внутрішнє складене імʼя з root local.name; застосовується до назв і tags відповідного child module. |
| Used in | `module.database::aws_db_instance.this`<br>`module.database::aws_iam_role.backup` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql` |
| Example | `Root передає: local.name` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.database.mode

| Поле | Пояснення |
|---|---|
| Variable | `mode`; [код L8](../../infrastructure/terraform/modules/mysql/main.tf#L8) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Child копія database_mode, керує count RDS та EC2 alternatives. |
| Used in | `module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.database::output.host` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql` |
| Example | `Root передає: var.database_mode` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.database.subnet_ids

| Поле | Пояснення |
|---|---|
| Variable | `subnet_ids`; [код L11](../../infrastructure/terraform/modules/mysql/main.tf#L11) |
| Type | `list(string)` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Список subnet IDs: ALBpublic pair або RDSprivate pair; EC2 MySQL бере першу private subnet. |
| Used in | `module.database::aws_db_subnet_group.this`<br>`module.database::aws_instance.mysql` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_instance.mysql` |
| Example | `Root передає: module.networking.private_subnet_ids` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.database.security_group

| Поле | Пояснення |
|---|---|
| Variable | `security_group`; [код L14](../../infrastructure/terraform/modules/mysql/main.tf#L14) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | SG ID відповідного компонента з security output; не нове HCP поле. |
| Used in | `module.database::aws_db_instance.this`<br>`module.database::aws_instance.mysql` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_instance.mysql` |
| Example | `Root передає: module.security.mysql_sg` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.database.availability_zone

| Поле | Пояснення |
|---|---|
| Variable | `availability_zone`; [код L17](../../infrastructure/terraform/modules/mysql/main.tf#L17) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Перша обрана networking AZ для Single-AZ RDS; дві subnet group не роблять DB Multi-AZ. |
| Used in | `module.database::aws_db_instance.this` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.database::aws_db_instance.this` |
| Example | `Root передає: module.networking.availability_zone` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.database.mysql_ami_id

| Поле | Пояснення |
|---|---|
| Variable | `mysql_ami_id`; [код L20](../../infrastructure/terraform/modules/mysql/main.tf#L20) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Тільки для database_mode=ec2: approved image з MySQL/secure init/backup; null дозволений у RDS mode. |
| Used in | `module.database::aws_instance.mysql` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.database::aws_instance.mysql` |
| Example | `Root передає: var.mysql_ami_id` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.database.artifact_bucket_arn

| Поле | Пояснення |
|---|---|
| Variable | `artifact_bucket_arn`; [код L23](../../infrastructure/terraform/modules/mysql/main.tf#L23) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | ARN artifact bucket з frontend output для scoped AI/DB backup S3 permissions. |
| Used in | `module.database::aws_iam_role_policy.backup` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql` |
| Example | `Root передає: module.frontend.artifact_bucket_arn` |
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
| Example | `Root передає: ["${local.name}-backend", "${local.name}-ai"]` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.ecr.enabled

| Поле | Пояснення |
|---|---|
| Variable | `enabled`; [код L5](../../infrastructure/terraform/modules/ecr/variable.tf#L5) |
| Type | `bool` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Child activity gate: ECR створення, backend capacity, AI power state — залежить від модуля. |
| Used in | `module.ecr::aws_ecr_repository.ecr` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr` |
| Example | `Root передає: var.artifacts_provisioned` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

## module.frontend


### module.frontend.storage_enabled

| Поле | Пояснення |
|---|---|
| Variable | `storage_enabled`; [код L1](../../infrastructure/terraform/modules/frontend/main.tf#L1) |
| Type | `bool` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Внутрішній прапорець захищеного S3, переданий з artifacts_provisioned. |
| Used in | `module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::local.buckets` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this` |
| Example | `Root передає: var.artifacts_provisioned` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.frontend.cdn_enabled

| Поле | Пояснення |
|---|---|
| Variable | `cdn_enabled`; [код L2](../../infrastructure/terraform/modules/frontend/main.tf#L2) |
| Type | `bool` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Внутрішній прапорець CloudFront, переданий з edge_provisioned. |
| Used in | `module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::data.aws_cloudfront_cache_policy.disabled`<br>`module.frontend::data.aws_cloudfront_origin_request_policy.api` |
| Affects | `module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket_policy.frontend` |
| Example | `Root передає: var.edge_provisioned` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.frontend.api_enabled

| Поле | Пояснення |
|---|---|
| Variable | `api_enabled`; [код L3](../../infrastructure/terraform/modules/frontend/main.tf#L3) |
| Type | `bool` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Додає CloudFront API origin/cache behavior тільки під час application window. |
| Used in | `module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::data.aws_cloudfront_origin_request_policy.api` |
| Affects | `module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend` |
| Example | `Root передає: var.application_window_open` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.frontend.name

| Поле | Пояснення |
|---|---|
| Variable | `name`; [код L4](../../infrastructure/terraform/modules/frontend/main.tf#L4) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Внутрішнє складене імʼя з root local.name; застосовується до назв і tags відповідного child module. |
| Used in | `module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this` |
| Example | `Root передає: local.name` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.frontend.origin_hostname

| Поле | Пояснення |
|---|---|
| Variable | `origin_hostname`; [код L7](../../infrastructure/terraform/modules/frontend/main.tf#L7) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Справжнє origin DNS імʼя для CloudFront, ACM та Route53 alias; certificate/DNS zone існують поза root. |
| Used in | `module.frontend::aws_cloudfront_distribution.this` |
| Affects | `module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend` |
| Example | `Root передає: var.application_window_open ? trimsuffix(aws_route53_record.origin[0].fqdn, ".") : null` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.frontend.origin_header

| Поле | Пояснення |
|---|---|
| Variable | `origin_header`; [код L10](../../infrastructure/terraform/modules/frontend/main.tf#L10) |
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
| Variable | `name`; [код L1](../../infrastructure/terraform/modules/networking/main.tf#L1) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Внутрішнє складене імʼя з root local.name; застосовується до назв і tags відповідного child module. |
| Used in | `module.networking::aws_vpc.this` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_instance.mysql`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `Root передає: local.name` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.networking.vpc_cidr

| Поле | Пояснення |
|---|---|
| Variable | `vpc_cidr`; [код L4](../../infrastructure/terraform/modules/networking/main.tf#L4) |
| Type | `string` |
| Default | `"10.42.0.0/16"` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Основний IPv4 CIDR; default збережено. Зміна існуючої мережі потенційно руйнівна. |
| Used in | `module.networking::aws_vpc.this` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_instance.mysql`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `"10.42.0.0/16"` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.networking.public_subnet_cidrs

| Поле | Пояснення |
|---|---|
| Variable | `public_subnet_cidrs`; [код L8](../../infrastructure/terraform/modules/networking/main.tf#L8) |
| Type | `list(string)` |
| Default | `["10.42.0.0/24", "10.42.1.0/24"]` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Два IPv4 CIDRs для ALB/backend subnet в перших двох доступних AZ; перевірити containment/overlap. |
| Used in | `module.networking::aws_subnet.public` |
| Affects | `module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.public`<br>`root::aws_route53_record.origin` |
| Example | `["10.42.0.0/24", "10.42.1.0/24"]` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.networking.private_subnet_cidrs

| Поле | Пояснення |
|---|---|
| Variable | `private_subnet_cidrs`; [код L12](../../infrastructure/terraform/modules/networking/main.tf#L12) |
| Type | `list(string)` |
| Default | `["10.42.10.0/24", "10.42.11.0/24"]` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Два IPv4 CIDRs для DB/AI subnet, без internet default route. |
| Used in | `module.networking::aws_subnet.private` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_instance.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_instance.mysql`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_subnet.private` |
| Example | `["10.42.10.0/24", "10.42.11.0/24"]` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

## module.security


### module.security.name

| Поле | Пояснення |
|---|---|
| Variable | `name`; [код L1](../../infrastructure/terraform/modules/security/main.tf#L1) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Внутрішнє складене імʼя з root local.name; застосовується до назв і tags відповідного child module. |
| Used in | `module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_instance.mysql`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `Root передає: local.name` |
| Recommendation | Залишити як внутрішній module contract; не додавати до HCP UI. |

### module.security.vpc_id

| Поле | Пояснення |
|---|---|
| Variable | `vpc_id`; [код L4](../../infrastructure/terraform/modules/security/main.tf#L4) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Ідентифікатор VPC з networking output для SG або ALB target group. |
| Used in | `module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_instance.mysql`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `Root передає: module.networking.vpc_id` |
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
| Used in | `root::local.name`<br>`root::local.tags`<br>`root::provider.aws` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
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
| Used in | `root::module.backend.input.region`<br>`root::provider.aws`<br>`root::var.runtime_secret_arns` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `us-east-1 — тільки після погодження` |
| Recommendation | Залишити. |

### root.name_suffix

| Поле | Пояснення |
|---|---|
| Variable | `name_suffix`; [код L19](../../infrastructure/terraform/variable.tf#L19) |
| Type | `string` |
| Default | Немає |
| Required | Так, без default |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Унікальна частина всіх імен; потрібна насамперед для глобально унікальних S3 buckets. |
| Used in | `root::local.name` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `demo26 — лише приклад suffix, глобальну унікальність перевірити` |
| Recommendation | Залишити. |

### root.infrastructure_reviewed

| Поле | Пояснення |
|---|---|
| Variable | `infrastructure_reviewed`; [код L28](../../infrastructure/terraform/variable.tf#L28) |
| Type | `bool` |
| Default | `false` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Навмисне блокування Plan через terraform_data precondition до review конфігурації/витрат; не вимикач окремих сервісів. |
| Used in | `root::terraform_data.review_gate` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `false` |
| Recommendation | Залишити. |

### root.service_enabled

| Поле | Пояснення |
|---|---|
| Variable | `service_enabled`; [код L33](../../infrastructure/terraform/variable.tf#L33) |
| Type | `bool` |
| Default | `false` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Разом з app window визначає desired backend task і ASG capacity; не керує RDS/S3/ECR/CloudFront створенням. |
| Used in | `root::module.backend.input.enabled`<br>`root::terraform_data.review_gate` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `false` |
| Recommendation | Залишити. |

### root.backend_image

| Поле | Пояснення |
|---|---|
| Variable | `backend_image`; [код L38](../../infrastructure/terraform/variable.tf#L38) |
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
| Variable | `ecs_ami_id`; [код L48](../../infrastructure/terraform/variable.tf#L48) |
| Type | `string` |
| Default | `null` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Pinned ECS-optimized AL2023 x86 AMI; image та agent readiness перевіряються окремо. |
| Used in | `root::module.backend.input.ami_id` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_launch_template.host` |
| Example | `null` |
| Recommendation | Залишити. |

### root.backend_instance_type

| Поле | Пояснення |
|---|---|
| Variable | `backend_instance_type`; [код L58](../../infrastructure/terraform/variable.tf#L58) |
| Type | `string` |
| Default | `"t3.small"` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Розмір backend host; micro benchmark-only, small основний кандидат, medium опція. |
| Used in | `root::module.backend.input.instance_type`<br>`root::terraform_data.review_gate` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `"t3.small"` |
| Recommendation | Залишити. |

### root.task_memory_mib

| Поле | Пояснення |
|---|---|
| Variable | `task_memory_mib`; [код L67](../../infrastructure/terraform/variable.tf#L67) |
| Type | `number` |
| Default | `1024` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Hard memory limit container; не дорівнює усій RAM host,512MiB зарезервовано для ECS/OS. |
| Used in | `root::module.backend.input.task_memory`<br>`root::terraform_data.review_gate` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `1024` |
| Recommendation | Залишити. |

### root.allow_deployment_capacity

| Поле | Пояснення |
|---|---|
| Variable | `allow_deployment_capacity`; [код L76](../../infrastructure/terraform/variable.tf#L76) |
| Type | `bool` |
| Default | `false` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Дозволяє ASGmax2 та deployment100/200%; не гарантує швидкий launch/zero downtime. |
| Used in | `root::module.backend.input.extra_capacity` |
| Affects | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this` |
| Example | `false` |
| Recommendation | Залишити. |

### root.origin_hostname

| Поле | Пояснення |
|---|---|
| Variable | `origin_hostname`; [код L81](../../infrastructure/terraform/variable.tf#L81) |
| Type | `string` |
| Default | `null` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Справжнє origin DNS імʼя для CloudFront, ACM та Route53 alias; certificate/DNS zone існують поза root. |
| Used in | `root::aws_route53_record.origin` |
| Affects | `module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`root::aws_route53_record.origin` |
| Example | `null` |
| Recommendation | Залишити. |

### root.origin_certificate_arn

| Поле | Пояснення |
|---|---|
| Variable | `origin_certificate_arn`; [код L91](../../infrastructure/terraform/variable.tf#L91) |
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
| Variable | `origin_verification_header`; [код L101](../../infrastructure/terraform/variable.tf#L101) |
| Type | `string` |
| Default | `null` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | true; metadata ARN не є secret value |
| Purpose | Випадковий секрет між CloudFront і ALB listener rule; не user auth; зберігається в protected state. |
| Used in | `root::module.alb.input.origin_header`<br>`root::module.frontend.input.origin_header` |
| Affects | `module.alb::aws_lb_listener_rule.origin`<br>`module.backend::aws_ecs_service.this`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`root::aws_route53_record.origin` |
| Example | `null` |
| Recommendation | Залишити. |

### root.runtime_secret_arns

| Поле | Пояснення |
|---|---|
| Variable | `runtime_secret_arns`; [код L112](../../infrastructure/terraform/variable.tf#L112) |
| Type | `map(string)` |
| Default | `{}` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Map SSM parameter ARNs для reader DB_USER/DB_PASS і optional ML_SERVICE_TOKEN, без plaintext credentials. |
| Used in | `root::module.backend.input.secret_arns`<br>`root::terraform_data.review_gate` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `{}` |
| Recommendation | Залишити. |

### root.database_mode

| Поле | Пояснення |
|---|---|
| Variable | `database_mode`; [код L122](../../infrastructure/terraform/variable.tf#L122) |
| Type | `string` |
| Default | `"rds"` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Вибір rds або baked private ec2 MySQL; не міграція даних, перемикання не є безпечним rollback. |
| Used in | `root::module.database.input.mode`<br>`root::var.mysql_ami_id`<br>`root::var.permissions_boundary_arn` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql` |
| Example | `"rds"` |
| Recommendation | Залишити. |

### root.mysql_ami_id

| Поле | Пояснення |
|---|---|
| Variable | `mysql_ami_id`; [код L131](../../infrastructure/terraform/variable.tf#L131) |
| Type | `string` |
| Default | `null` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Тільки для database_mode=ec2: approved image з MySQL/secure init/backup; null дозволений у RDS mode. |
| Used in | `root::module.database.input.mysql_ami_id` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.database::aws_instance.mysql` |
| Example | `null` |
| Recommendation | Залишити. |

### root.ai_enabled

| Поле | Пояснення |
|---|---|
| Variable | `ai_enabled`; [код L140](../../infrastructure/terraform/variable.tf#L140) |
| Type | `bool` |
| Default | `false` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Керує running/stopped через aws_ec2_instance_state, не count AI instance. |
| Used in | `root::module.ai.input.enabled`<br>`root::terraform_data.review_gate` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `false` |
| Recommendation | Залишити. |

### root.ai_ami_id

| Поле | Пояснення |
|---|---|
| Variable | `ai_ami_id`; [код L145](../../infrastructure/terraform/variable.tf#L145) |
| Type | `string` |
| Default | `null` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Погоджена приватна AI AMI; потрібна при ai_provisioned=true. |
| Used in | `root::module.ai.input.ami_id` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_instance.this` |
| Example | `null` |
| Recommendation | Залишити. |

### root.ai_instance_type

| Поле | Пояснення |
|---|---|
| Variable | `ai_instance_type`; [код L154](../../infrastructure/terraform/variable.tf#L154) |
| Type | `string` |
| Default | `"t3.small"` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | CPU AI host size; фактичні PyTorch RAM requirements ще не виміряні. |
| Used in | `root::module.ai.input.instance_type` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_instance.this` |
| Example | `"t3.small"` |
| Recommendation | Залишити. |

### root.application_window_open

| Поле | Пояснення |
|---|---|
| Variable | `application_window_open`; [код L163](../../infrastructure/terraform/variable.tf#L163) |
| Type | `bool` |
| Default | `false` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Визначає root ALB count, origin DNS, ECS service existence; закриття означає infrastructure delete, не stop ALB. |
| Used in | `root::aws_route53_record.origin`<br>`root::module.alb`<br>`root::module.backend.input.active_window`<br>`root::module.backend.input.enabled`<br>`root::module.frontend.input.api_enabled`<br>`root::module.frontend.input.origin_hostname`<br>`root::terraform_data.review_gate`<br>`root::var.origin_certificate_arn`<br>`root::var.origin_hostname`<br>`root::var.origin_verification_header`<br>`root::var.origin_zone_id` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `false` |
| Recommendation | Залишити. |

### root.origin_zone_id

| Поле | Пояснення |
|---|---|
| Variable | `origin_zone_id`; [код L169](../../infrastructure/terraform/variable.tf#L169) |
| Type | `string` |
| Default | `null` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | ID наявної public Route53 zone, куди записується origin alias; не створює zone. |
| Used in | `root::aws_route53_record.origin` |
| Affects | `module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`root::aws_route53_record.origin` |
| Example | `null` |
| Recommendation | Залишити. |

### root.permissions_boundary_arn

| Поле | Пояснення |
|---|---|
| Variable | `permissions_boundary_arn`; [код L179](../../infrastructure/terraform/variable.tf#L179) |
| Type | `string` |
| Default | `null` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | ARN наявної IAM permissions boundary для5 ролей; її зміст root не створює і не доводить least privilege. |
| Used in | `root::module.ai.input.permissions_boundary_arn`<br>`root::module.backend.input.permissions_boundary_arn`<br>`root::module.database.input.permissions_boundary_arn` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql` |
| Example | `null` |
| Recommendation | Залишити. |

### root.vpc_cidr

| Поле | Пояснення |
|---|---|
| Variable | `vpc_cidr`; [код L189](../../infrastructure/terraform/variable.tf#L189) |
| Type | `string` |
| Default | `"10.42.0.0/16"` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Основний IPv4 CIDR; default збережено. Зміна існуючої мережі потенційно руйнівна. |
| Used in | `root::module.networking.input.vpc_cidr` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_instance.mysql`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `"10.42.0.0/16"` |
| Recommendation | Залишити. |

### root.public_subnet_cidrs

| Поле | Пояснення |
|---|---|
| Variable | `public_subnet_cidrs`; [код L198](../../infrastructure/terraform/variable.tf#L198) |
| Type | `list(string)` |
| Default | `["10.42.0.0/24", "10.42.1.0/24"]` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Два IPv4 CIDRs для ALB/backend subnet в перших двох доступних AZ; перевірити containment/overlap. |
| Used in | `root::module.networking.input.public_subnet_cidrs` |
| Affects | `module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.public`<br>`root::aws_route53_record.origin` |
| Example | `["10.42.0.0/24", "10.42.1.0/24"]` |
| Recommendation | Залишити. |

### root.private_subnet_cidrs

| Поле | Пояснення |
|---|---|
| Variable | `private_subnet_cidrs`; [код L207](../../infrastructure/terraform/variable.tf#L207) |
| Type | `list(string)` |
| Default | `["10.42.10.0/24", "10.42.11.0/24"]` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Два IPv4 CIDRs для DB/AI subnet, без internet default route. |
| Used in | `root::module.networking.input.private_subnet_cidrs` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_instance.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_instance.mysql`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_subnet.private` |
| Example | `["10.42.10.0/24", "10.42.11.0/24"]` |
| Recommendation | Залишити. |

### root.artifacts_provisioned

| Поле | Пояснення |
|---|---|
| Variable | `artifacts_provisioned`; [код L218](../../infrastructure/terraform/variable.tf#L218) |
| Type | `bool` |
| Default | `false` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Етап ECR і приватного S3; після створення лишати true. Вимкнення блокується prevent_destroy. |
| Used in | `root::module.ecr.input.enabled`<br>`root::module.frontend.input.storage_enabled`<br>`root::terraform_data.review_gate` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `false` |
| Recommendation | Залишити. |

### root.database_provisioned

| Поле | Пояснення |
|---|---|
| Variable | `database_provisioned`; [код L223](../../infrastructure/terraform/variable.tf#L223) |
| Type | `bool` |
| Default | `false` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Етап MySQL; після створення не вимикати заради зупинки демонстрації. |
| Used in | `root::module.database.input.provisioned`<br>`root::terraform_data.review_gate`<br>`root::var.mysql_ami_id`<br>`root::var.permissions_boundary_arn` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `false` |
| Recommendation | Залишити. |

### root.edge_provisioned

| Поле | Пояснення |
|---|---|
| Variable | `edge_provisioned`; [код L228](../../infrastructure/terraform/variable.tf#L228) |
| Type | `bool` |
| Default | `false` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Етап CloudFront для frontend; API origin додається лише у відкритому application window. |
| Used in | `root::module.frontend.input.cdn_enabled`<br>`root::terraform_data.review_gate` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `false` |
| Recommendation | Залишити. |

### root.backend_provisioned

| Поле | Пояснення |
|---|---|
| Variable | `backend_provisioned`; [код L233](../../infrastructure/terraform/variable.tf#L233) |
| Type | `bool` |
| Default | `false` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Етап IAM/cluster/task definition/LT/ASG. Не дорівнює запуску EC2/task. |
| Used in | `root::module.backend.input.provisioned`<br>`root::terraform_data.review_gate`<br>`root::var.backend_image`<br>`root::var.ecs_ami_id`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `false` |
| Recommendation | Залишити. |

### root.ai_provisioned

| Поле | Пояснення |
|---|---|
| Variable | `ai_provisioned`; [код L238](../../infrastructure/terraform/variable.tf#L238) |
| Type | `bool` |
| Default | `false` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Створення захищеного AI host; відокремлене від running/stopped. |
| Used in | `root::module.ai.input.provisioned`<br>`root::terraform_data.review_gate`<br>`root::var.ai_ami_id`<br>`root::var.permissions_boundary_arn` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `false` |
| Recommendation | Залишити. |

### root.ai_runtime_reviewed

| Поле | Пояснення |
|---|---|
| Variable | `ai_runtime_reviewed`; [код L243](../../infrastructure/terraform/variable.tf#L243) |
| Type | `bool` |
| Default | `false` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Ручне підтвердження AMI, приватного TLS/DNS, доставки токена і S3 agent; це не автоматична перевірка. |
| Used in | `root::terraform_data.review_gate` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `false` |
| Recommendation | Залишити. |

### root.ml_service_url

| Поле | Пояснення |
|---|---|
| Variable | `ml_service_url`; [код L248](../../infrastructure/terraform/variable.tf#L248) |
| Type | `string` |
| Default | `null` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Погоджений приватний HTTPS endpoint AI; null залишає сервіс чесно не налаштованим. |
| Used in | `root::module.backend.input.ml_service_url`<br>`root::terraform_data.review_gate` |
| Affects | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`root::aws_route53_record.origin` |
| Example | `null` |
| Recommendation | Залишити. |

### root.ml_tls_ca_file

| Поле | Пояснення |
|---|---|
| Variable | `ml_tls_ca_file`; [код L257](../../infrastructure/terraform/variable.tf#L257) |
| Type | `string` |
| Default | `null` |
| Required | Ні; conditional preconditions можуть вимагати значення |
| Sensitive | false; metadata ARN не є secret value |
| Purpose | Необовʼязковий шлях до CA, уже включеного у backend image для приватного ML TLS. |
| Used in | `root::module.backend.input.ml_tls_ca_file` |
| Affects | `module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial` |
| Example | `null` |
| Recommendation | Залишити. |

## Невикористані та схожі за назвою

`module.alb.name`

name/env/region копії між scopes — нормальні module bindings. active_window та enabled не еквівалентні: window створює service object/ALB, enabled задає task/ASG capacity. ai_enabled — окремий lifecycle. task_memory_mib→task_memory та allow_deployment_capacity→extra_capacity — перейменування на module boundary, не два незалежні inputs. origin header child inputs — одна передана sensitive root величина.

[Аудит13requiredinputs та групування](REQUIRED_VARIABLES_AUDIT.md). Root CIDR defaults і child defaults дублюються навмисно для backward-compatible standalone module usage; root явно передає значення.
