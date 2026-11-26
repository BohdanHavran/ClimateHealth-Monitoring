# Повний аудит resource blocks

У цьому переліку кожен із69resource blocks має окрему таблицю; один terraform_data не є AWS ресурсом. count/for_each instances не обчислено. «Завжди» означає наявність блоку без його count, а не дозвіл apply з false review gate. Умовність батьківського module також враховано.

Dependencies/consumers витягнуті з traversals/input-output bindings і явних depends_on. provider/variables/locals можуть зʼявлятися як залежності, не лише AWS ресурси. Region/account permissions/API availability і реальний AWS state не перевірялися. Replacement оцінка консервативна: точне replace/update/destroy визначить лише дозволений provider Plan з існуючим state; нижче не вигадано ForceNew schema.

Cost notes — орієнтири us-east-1 зі збереженого кошторису24.11 та переглянутих офіційних цін, не bill prediction. Не підсумовувати повʼязані policy/rule charges удруге. Детальна різниця reserve/реальних ресурсів — [COST_AUDIT](COST_AUDIT.md).


## module.ai


### module.ai.aws_iam_role.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_role` / `this` / `module.ai`; [код L27](../../infrastructure/terraform/modules/ai/main.tf#L27) |
| Purpose | Service identity host/execution/task/AI/backup з permissions boundary |
| Depends on | `module.ai::var.name`<br>`module.ai::var.permissions_boundary_arn`<br>`module.ai::var.provisioned`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role_policy.read` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Не network endpoint; IAM trust/service principal |
| Security / replacement / deletion | Policy boundary існує зовні; role name/path зміна або trust update може зупинити доступ. Service trust без додаткового SourceAccount hardening. |

### module.ai.aws_iam_role_policy.read

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_role_policy` / `read` / `module.ai`; [код L33](../../infrastructure/terraform/modules/ai/main.tf#L33) |
| Purpose | Custom inline permissions execution/AI/backup |
| Depends on | `module.ai::aws_iam_role.this`<br>`module.ai::var.artifact_bucket_arn`<br>`module.ai::var.provisioned`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.ai::aws_iam_instance_profile.this` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | ECR/SSM/logs/S3 IAM scope |
| Security / replacement / deletion | Execution role auth token Resource* потрібний API; secrets можуть потребувати kms:Decrypt для CMK. Не всі startup paths залежать від policy attachment. |

### module.ai.aws_iam_instance_profile.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_instance_profile` / `this` / `module.ai`; [код L38](../../infrastructure/terraform/modules/ai/main.tf#L38) |
| Purpose | Передача IAM role EC2 instance |
| Depends on | `module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::var.provisioned`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.ai::aws_instance.this` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Credentials через IMDSv2, не public endpoint |
| Security / replacement / deletion | Не чекає attachment/inline policy readiness само по собі; name/role зміни перевірити перед заміною. |

### module.ai.aws_instance.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_instance` / `this` / `module.ai`; [код L43](../../infrastructure/terraform/modules/ai/main.tf#L43) |
| Purpose | Private CPU EC2 AI або alternative MySQL |
| Depends on | `module.ai::aws_iam_instance_profile.this`<br>`module.ai::var.ami_id`<br>`module.ai::var.instance_type`<br>`module.ai::var.provisioned`<br>`module.ai::var.security_group`<br>`module.ai::var.subnet_id`<br>`module.ai::var.tags`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::output.private_ip` |
| Root inputs, transitively | `root::var.ai_ami_id`<br>`root::var.ai_enabled`<br>`root::var.ai_instance_type`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.private_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | Так: small$0.0208/h + EBS;20/30GB=$1.60/$2.40 при місячному зберіганні |
| Public / network | associate_public_ip_address=false, тільки VPC SG paths |
| Security / replacement / deletion | AMI/subnet зміни можуть замінити EC2; delete_on_termination=false залишає unmanaged billable root volumes після countoff/replacement. DB prevent_destroy блокує destruction. |

### module.ai.aws_ec2_instance_state.power

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_ec2_instance_state` / `power` / `module.ai`; [код L72](../../infrastructure/terraform/modules/ai/main.tf#L72) |
| Purpose | Керує running/stopped збереженого AI EC2 |
| Depends on | `module.ai::aws_instance.this`<br>`module.ai::var.enabled`<br>`module.ai::var.provisioned`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.ai_ami_id`<br>`root::var.ai_enabled`<br>`root::var.ai_instance_type`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.private_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | EC2 compute тільки running; EBS залишається платним |
| Public / network | Не створює endpoint |
| Security / replacement / deletion | Provisioned instance захищено prevent_destroy; power off не видаляє диск. Створення instance спочатку запускає EC2 навіть якщо кінцева state stopped. |

## module.alb


### module.alb.aws_lb.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_lb` / `this` / `module.alb`; [код L20](../../infrastructure/terraform/modules/alb/main.tf#L20) |
| Purpose | Internet-facing HTTPS Application Load Balancer |
| Depends on | `module.alb::var.security_group`<br>`module.alb::var.subnet_ids`<br>`root::module.alb`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.alb::aws_lb_listener.https`<br>`module.alb::output.arn`<br>`module.alb::output.dns`<br>`module.alb::output.zone_id` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.public_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: var.application_window_open ? 1 : 0` |
| Cost | Так: $0.0225/h + LCU + щонайменше2 IPv4 по$0.005/h |
| Public / network | Public443, SG обмежує CloudFront prefix |
| Security / replacement / deletion | ALB не зупиняється разом з EC2; заміна/VPC/subnet зміни вимагають review; немає access logs/deletion protection. |

### module.alb.aws_lb_target_group.backend

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_lb_target_group` / `backend` / `module.alb`; [код L29](../../infrastructure/terraform/modules/alb/main.tf#L29) |
| Purpose | Instance targets host8080, health /health/ready |
| Depends on | `module.alb::var.vpc_id`<br>`root::module.alb`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.alb::aws_lb_listener_rule.origin`<br>`module.alb::output.target_group_arn` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: var.application_window_open ? 1 : 0` |
| Cost | Не окрема hourly; LCU рахують на ALB |
| Public / network | HTTP8080 лише внутрішній SG шлях |
| Security / replacement / deletion | Protocol/target_type/VPC зміни потенційно replacement; readiness залежить від DB TLS/reader. |

### module.alb.aws_lb_listener.https

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_lb_listener` / `https` / `module.alb`; [код L45](../../infrastructure/terraform/modules/alb/main.tf#L45) |
| Purpose | HTTPS443 listener з переданим ACM та default403 |
| Depends on | `module.alb::aws_lb.this`<br>`module.alb::var.certificate_arn`<br>`root::module.alb`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.alb::aws_lb_listener_rule.origin` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.origin_certificate_arn`<br>`root::var.public_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: var.application_window_open ? 1 : 0` |
| Cost | Не окрема hourly, ALB/LCU окремо |
| Public / network | Public TLS listener під SG CloudFront gate |
| Security / replacement / deletion | Certificate має існувати/бути виданий/покривати origin hostname; зміна listener може перервати TLS. |

### module.alb.aws_lb_listener_rule.origin

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_lb_listener_rule` / `origin` / `module.alb`; [код L59](../../infrastructure/terraform/modules/alb/main.tf#L59) |
| Purpose | Forward лише за секретним origin header |
| Depends on | `module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_target_group.backend`<br>`module.alb::var.origin_header`<br>`root::module.alb`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.alb::output.listener_arn` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.origin_certificate_arn`<br>`root::var.origin_verification_header`<br>`root::var.public_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: var.application_window_open ? 1 : 0` |
| Cost | Не окрема hourly, rule evaluations можуть впливати на LCU |
| Public / network | Header restriction, не user authentication |
| Security / replacement / deletion | Header зберігається у state/CloudFront; rotation потребує узгодження обох сторін. |

## module.backend


### module.backend.aws_ecs_cluster.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_ecs_cluster` / `this` / `module.backend`; [код L56](../../infrastructure/terraform/modules/ecs-backend/main.tf#L56) |
| Purpose | Логічний ECS cluster, Container Insights disabled |
| Depends on | `module.backend::var.name`<br>`module.backend::var.provisioned`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_launch_template.host`<br>`module.backend::output.cluster` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | ECS EC2 control plane без окремої compute hourly; hosts оплачуються |
| Public / network | Не public application endpoint |
| Security / replacement / deletion | Cluster name зміна може вимагати replacement; один host/AZ не HA. |

### module.backend.aws_iam_role.host

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_role` / `host` / `module.backend`; [код L68](../../infrastructure/terraform/modules/ecs-backend/main.tf#L68) |
| Purpose | Service identity host/execution/task/AI/backup з permissions boundary |
| Depends on | `module.backend::local.ec2_trust`<br>`module.backend::var.name`<br>`module.backend::var.permissions_boundary_arn`<br>`module.backend::var.provisioned`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Не network endpoint; IAM trust/service principal |
| Security / replacement / deletion | Policy boundary існує зовні; role name/path зміна або trust update може зупинити доступ. Service trust без додаткового SourceAccount hardening. |

### module.backend.aws_iam_role_policy_attachment.agent

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_role_policy_attachment` / `agent` / `module.backend`; [код L74](../../infrastructure/terraform/modules/ecs-backend/main.tf#L74) |
| Purpose | AWS managed host ECS agent або SSM policy |
| Depends on | `module.backend::aws_iam_role.host`<br>`module.backend::var.provisioned`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.backend::aws_iam_instance_profile.host` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | IAM permissions, не network egress |
| Security / replacement / deletion | Managed policies ширші за custom scope; launch template не залежить прямо від attachments. |

### module.backend.aws_iam_role_policy_attachment.ssm

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_role_policy_attachment` / `ssm` / `module.backend`; [код L79](../../infrastructure/terraform/modules/ecs-backend/main.tf#L79) |
| Purpose | AWS managed host ECS agent або SSM policy |
| Depends on | `module.backend::aws_iam_role.host`<br>`module.backend::var.provisioned`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.backend::aws_iam_instance_profile.host` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | IAM permissions, не network egress |
| Security / replacement / deletion | Managed policies ширші за custom scope; launch template не залежить прямо від attachments. |

### module.backend.aws_iam_instance_profile.host

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_instance_profile` / `host` / `module.backend`; [код L84](../../infrastructure/terraform/modules/ecs-backend/main.tf#L84) |
| Purpose | Передача IAM role EC2 instance |
| Depends on | `module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::var.provisioned`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.backend::aws_launch_template.host` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Credentials через IMDSv2, не public endpoint |
| Security / replacement / deletion | Не чекає attachment/inline policy readiness само по собі; name/role зміни перевірити перед заміною. |

### module.backend.aws_iam_role.execution

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_role` / `execution` / `module.backend`; [код L89](../../infrastructure/terraform/modules/ecs-backend/main.tf#L89) |
| Purpose | Service identity host/execution/task/AI/backup з permissions boundary |
| Depends on | `module.backend::local.task_trust`<br>`module.backend::var.name`<br>`module.backend::var.permissions_boundary_arn`<br>`module.backend::var.provisioned`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::output.execution_role_arn` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Не network endpoint; IAM trust/service principal |
| Security / replacement / deletion | Policy boundary існує зовні; role name/path зміна або trust update може зупинити доступ. Service trust без додаткового SourceAccount hardening. |

### module.backend.aws_iam_role.task

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_role` / `task` / `module.backend`; [код L95](../../infrastructure/terraform/modules/ecs-backend/main.tf#L95) |
| Purpose | Service identity host/execution/task/AI/backup з permissions boundary |
| Depends on | `module.backend::local.task_trust`<br>`module.backend::var.name`<br>`module.backend::var.permissions_boundary_arn`<br>`module.backend::var.provisioned`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.backend::aws_ecs_task_definition.initial`<br>`module.backend::output.task_role_arn` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Не network endpoint; IAM trust/service principal |
| Security / replacement / deletion | Policy boundary існує зовні; role name/path зміна або trust update може зупинити доступ. Service trust без додаткового SourceAccount hardening. |

### module.backend.aws_cloudwatch_log_group.backend

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_cloudwatch_log_group` / `backend` / `module.backend`; [код L101](../../infrastructure/terraform/modules/ecs-backend/main.tf#L101) |
| Purpose | Backend logs із retention7днів |
| Depends on | `module.backend::var.name`<br>`module.backend::var.provisioned`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_role_policy.execution` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | Так за ingestion/storage; порожній group не дорівнює$0.83 monitoring reserve |
| Public / network | AWS Logs API; не public logs |
| Security / replacement / deletion | Немає metric alarms/Budgets ресурсів; secret-safe logging лишається application відповідальністю. |

### module.backend.aws_iam_role_policy.execution

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_role_policy` / `execution` / `module.backend`; [код L107](../../infrastructure/terraform/modules/ecs-backend/main.tf#L107) |
| Purpose | Custom inline permissions execution/AI/backup |
| Depends on | `module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::var.provisioned`<br>`module.backend::var.repository_arns`<br>`module.backend::var.secret_arns`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.backend::aws_ecs_service.this` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | ECR/SSM/logs/S3 IAM scope |
| Security / replacement / deletion | Execution role auth token Resource* потрібний API; secrets можуть потребувати kms:Decrypt для CMK. Не всі startup paths залежать від policy attachment. |

### module.backend.aws_launch_template.host

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_launch_template` / `host` / `module.backend`; [код L117](../../infrastructure/terraform/modules/ecs-backend/main.tf#L117) |
| Purpose | Pinned AL2023 AMI/instance profile/SG/publicIPv4/20GBgp3/ECS config |
| Depends on | `module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::var.ami_id`<br>`module.backend::var.instance_type`<br>`module.backend::var.name`<br>`module.backend::var.provisioned`<br>`module.backend::var.security_group`<br>`module.backend::var.tags`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.backend::aws_autoscaling_group.host` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.ecs_ami_id`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | Config без hourly; створені hosts/volumes/IP оплачуються |
| Public / network | Host має public IP, IMDSv2 hop1; ingress лише SG |
| Security / replacement / deletion | Нова LT version не означає автоматичний instance refresh; відсутні tag_specifications для EC2/volumes. |

### module.backend.aws_autoscaling_group.host

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_autoscaling_group` / `host` / `module.backend`; [код L158](../../infrastructure/terraform/modules/ecs-backend/main.tf#L158) |
| Purpose | Host capacity0/1, optionalmax2 для deployment |
| Depends on | `module.backend::aws_launch_template.host`<br>`module.backend::var.enabled`<br>`module.backend::var.extra_capacity`<br>`module.backend::var.name`<br>`module.backend::var.provisioned`<br>`module.backend::var.subnet_id`<br>`module.backend::var.tags`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::output.asg_name` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.allow_deployment_capacity`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.ecs_ami_id`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.public_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | Так для EC2/IP/EBS: t3.small$0.0208/h +IPv4$0.005/h |
| Public / network | Одна public subnet/AZ, SG контролює host8080 |
| Security / replacement / deletion | desired_capacity ignore_changes; health_check_type EC2 не ALB. Max1/from-zero/rolling потребують тестів; видалення host видаляє root EBS. |

### module.backend.aws_ecs_capacity_provider.host

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_ecs_capacity_provider` / `host` / `module.backend`; [код L185](../../infrastructure/terraform/modules/ecs-backend/main.tf#L185) |
| Purpose | ASG managed scaling/draining для ECS |
| Depends on | `module.backend::aws_autoscaling_group.host`<br>`module.backend::var.name`<br>`module.backend::var.provisioned`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::output.capacity_provider` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.allow_deployment_capacity`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.ecs_ami_id`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.public_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | ASG/EC2 оплату не замінює |
| Public / network | Логічна scheduling/control plane конфігурація |
| Security / replacement / deletion | При scale-from-zero AWS описує initial2instances; max1 не можна оголосити гарантовано працездатним без контрольного тесту. |

### module.backend.aws_ecs_cluster_capacity_providers.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_ecs_cluster_capacity_providers` / `this` / `module.backend`; [код L200](../../infrastructure/terraform/modules/ecs-backend/main.tf#L200) |
| Purpose | Асоціація Capacity Provider з cluster |
| Depends on | `module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::var.provisioned`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.backend::aws_ecs_service.this` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.allow_deployment_capacity`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.ecs_ami_id`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.public_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Не endpoint |
| Security / replacement / deletion | Не окремий Capacity Provider; зміна асоціації впливає на scheduling. |

### module.backend.aws_ecs_task_definition.initial

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_ecs_task_definition` / `initial` / `module.backend`; [код L205](../../infrastructure/terraform/modules/ecs-backend/main.tf#L205) |
| Purpose | Initial backend revision: bridge,1024MiB default,8000/8080,read-only filesystem |
| Depends on | `module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.task`<br>`module.backend::var.db_host`<br>`module.backend::var.image`<br>`module.backend::var.ml_service_url`<br>`module.backend::var.ml_tls_ca_file`<br>`module.backend::var.name`<br>`module.backend::var.provisioned`<br>`module.backend::var.region`<br>`module.backend::var.secret_arns`<br>`module.backend::var.task_memory`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.backend::aws_ecs_service.this`<br>`module.backend::output.task_definition_arn` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_image`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.ml_tls_ca_file`<br>`root::var.mysql_ami_id`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.private_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `var.provisioned ? 1 : 0; parent module: без count` |
| Cost | Task definition без compute hourly; hosts/logs/requests оплачуються |
| Public / network | Сам не запускає container |
| Security / replacement / deletion | Зміна параметрів створює нову revision. ML_SERVICE_URL/DB client TLS не налаштовано цією definition; tmpfs споживає RAM. |

### module.backend.aws_ecs_service.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_ecs_service` / `this` / `module.backend`; [код L230](../../infrastructure/terraform/modules/ecs-backend/main.tf#L230) |
| Purpose | Запуск backend task через CP, health/circuit rollback і ALB |
| Depends on | `module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::var.active_window`<br>`module.backend::var.enabled`<br>`module.backend::var.extra_capacity`<br>`module.backend::var.listener_arn`<br>`module.backend::var.provisioned`<br>`module.backend::var.target_group_arn`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.backend::output.service` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.allow_deployment_capacity`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_image`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.ecs_ami_id`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.ml_tls_ca_file`<br>`root::var.mysql_ami_id`<br>`root::var.name_suffix`<br>`root::var.origin_certificate_arn`<br>`root::var.origin_verification_header`<br>`root::var.permissions_boundary_arn`<br>`root::var.private_subnet_cidrs`<br>`root::var.public_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `var.provisioned && var.active_window ? 1 : 0; parent module: без count` |
| Cost | Service config без окремої hourly, capacity/ALB/logs оплачуються |
| Public / network | Доступ тільки через ALB→instance bridge mapping |
| Security / replacement / deletion | HCP володіє task_definition. Default min0 допускає downtime; host8080 потребує другого EC2 для rolling, ще не перевірено. |

## module.database


### module.database.aws_db_subnet_group.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_db_subnet_group` / `this` / `module.database`; [код L26](../../infrastructure/terraform/modules/mysql/main.tf#L26) |
| Purpose | Private subnet placement group для RDS |
| Depends on | `module.database::var.mode`<br>`module.database::var.provisioned`<br>`module.database::var.subnet_ids`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.database::aws_db_instance.this` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.private_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `var.provisioned && var.mode == "rds" ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Не endpoint; дві subnet AZ, RDS усе одно Single-AZ |
| Security / replacement / deletion | Subnet/VPC зміни можуть впливати на replacement/доступність DB. |

### module.database.aws_db_parameter_group.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_db_parameter_group` / `this` / `module.database`; [код L30](../../infrastructure/terraform/modules/mysql/main.tf#L30) |
| Purpose | mysql8.4 require_secure_transport=ON |
| Depends on | `module.database::var.mode`<br>`module.database::var.provisioned`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.database::aws_db_instance.this` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.provisioned && var.mode == "rds" ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Вимагає TLS до DB endpoint |
| Security / replacement / deletion | Family change/reboot може бути необхідний; поточний PyMySQL client TLS ще не налаштований. |

### module.database.aws_db_instance.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_db_instance` / `this` / `module.database`; [код L38](../../infrastructure/terraform/modules/mysql/main.tf#L38) |
| Purpose | Encrypted private MySQL8.4.13 Single-AZ,managed master secret,backup7днів |
| Depends on | `module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::var.availability_zone`<br>`module.database::var.mode`<br>`module.database::var.name`<br>`module.database::var.provisioned`<br>`module.database::var.security_group`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.database::output.host` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.private_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `var.provisioned && var.mode == "rds" ? 1 : 0; parent module: без count` |
| Cost | Так навіть при appwindowfalse:0.016/h +20GBgp3$2.30/міс +managed secret |
| Public / network | publicly_accessible=false,3306 тільки backendSG |
| Security / replacement / deletion | deletion_protection/finalsnapshot захищають, але не обнуляють витрати; snapshotname повторно може конфліктувати; engine/class availability перевірити в region. |

### module.database.aws_instance.mysql

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_instance` / `mysql` / `module.database`; [код L66](../../infrastructure/terraform/modules/mysql/main.tf#L66) |
| Purpose | Private CPU EC2 AI або alternative MySQL |
| Depends on | `module.database::aws_iam_instance_profile.backup`<br>`module.database::var.mode`<br>`module.database::var.mysql_ami_id`<br>`module.database::var.provisioned`<br>`module.database::var.security_group`<br>`module.database::var.subnet_ids`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.database::output.host` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.mysql_ami_id`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.private_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `var.provisioned && var.mode == "ec2" ? 1 : 0; parent module: без count` |
| Cost | Так: small$0.0208/h + EBS;20/30GB=$1.60/$2.40 при місячному зберіганні |
| Public / network | associate_public_ip_address=false, тільки VPC SG paths |
| Security / replacement / deletion | AMI/subnet зміни можуть замінити EC2; delete_on_termination=false залишає unmanaged billable root volumes після countoff/replacement. DB prevent_destroy блокує destruction. |

### module.database.aws_iam_role.backup

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_role` / `backup` / `module.database`; [код L92](../../infrastructure/terraform/modules/mysql/main.tf#L92) |
| Purpose | Service identity host/execution/task/AI/backup з permissions boundary |
| Depends on | `module.database::var.mode`<br>`module.database::var.name`<br>`module.database::var.permissions_boundary_arn`<br>`module.database::var.provisioned`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role_policy.backup` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.provisioned && var.mode == "ec2" ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Не network endpoint; IAM trust/service principal |
| Security / replacement / deletion | Policy boundary існує зовні; role name/path зміна або trust update може зупинити доступ. Service trust без додаткового SourceAccount hardening. |

### module.database.aws_iam_role_policy.backup

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_role_policy` / `backup` / `module.database`; [код L98](../../infrastructure/terraform/modules/mysql/main.tf#L98) |
| Purpose | Custom inline permissions execution/AI/backup |
| Depends on | `module.database::aws_iam_role.backup`<br>`module.database::var.artifact_bucket_arn`<br>`module.database::var.mode`<br>`module.database::var.provisioned`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.database::aws_iam_instance_profile.backup` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.provisioned && var.mode == "ec2" ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | ECR/SSM/logs/S3 IAM scope |
| Security / replacement / deletion | Execution role auth token Resource* потрібний API; secrets можуть потребувати kms:Decrypt для CMK. Не всі startup paths залежать від policy attachment. |

### module.database.aws_iam_instance_profile.backup

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_instance_profile` / `backup` / `module.database`; [код L106](../../infrastructure/terraform/modules/mysql/main.tf#L106) |
| Purpose | Передача IAM role EC2 instance |
| Depends on | `module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::var.mode`<br>`module.database::var.provisioned`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.database::aws_instance.mysql` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_mode`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.provisioned && var.mode == "ec2" ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Credentials через IMDSv2, не public endpoint |
| Security / replacement / deletion | Не чекає attachment/inline policy readiness само по собі; name/role зміни перевірити перед заміною. |

## module.ecr


### module.ecr.aws_ecr_repository.ecr

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_ecr_repository` / `ecr` / `module.ecr`; [код L2](../../infrastructure/terraform/modules/ecr/main.tf#L2) |
| Purpose | Registry backend та AI container images |
| Depends on | `module.ecr::var.ecr_names`<br>`module.ecr::var.enabled`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::output.arns`<br>`module.ecr::output.urls` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.enabled ? toset(var.ecr_names) : toset([]); parent module: без count` |
| Cost | Так: storage, базовий орієнтир5GB=$0.50/міс; не за порожній repo |
| Public / network | AWS API endpoint; доступ IAM, не public anonymous repository |
| Security / replacement / deletion | Name/encryption changes перевірити на replacement; immutable tags, scan_on_push; tagged images можуть накопичуватися. |

### module.ecr.aws_ecr_lifecycle_policy.images

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_ecr_lifecycle_policy` / `images` / `module.ecr`; [код L19](../../infrastructure/terraform/modules/ecr/main.tf#L19) |
| Purpose | Видалення untagged images через14днів |
| Depends on | `module.ecr::aws_ecr_repository.ecr`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `aws_ecr_repository.ecr; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Management policy, не endpoint |
| Security / replacement / deletion | Не видаляє tagged releases; занадто короткий retention може знищити rollback images. |

## module.frontend


### module.frontend.aws_s3_bucket.frontend

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_s3_bucket` / `frontend` / `module.frontend`; [код L14](../../infrastructure/terraform/modules/frontend/main.tf#L14) |
| Purpose | Private frontend assets або artifacts/backups |
| Depends on | `module.frontend::var.name`<br>`module.frontend::var.storage_enabled`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::local.buckets`<br>`module.frontend::output.bucket` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.storage_enabled ? 1 : 0; parent module: без count` |
| Cost | Так: storage/requests/versioning; baseline5GB+requests=$0.124/міс сумарно |
| Public / network | Bucket public access blocked, frontend читає тільки CF OAC |
| Security / replacement / deletion | Bucket name зміна може замінити ресурс; nonempty bucket не видалиться просто; versions накопичуються. |

### module.frontend.aws_s3_bucket.artifacts

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_s3_bucket` / `artifacts` / `module.frontend`; [код L19](../../infrastructure/terraform/modules/frontend/main.tf#L19) |
| Purpose | Private frontend assets або artifacts/backups |
| Depends on | `module.frontend::var.name`<br>`module.frontend::var.storage_enabled`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::local.buckets`<br>`module.frontend::output.artifact_bucket`<br>`module.frontend::output.artifact_bucket_arn` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.storage_enabled ? 1 : 0; parent module: без count` |
| Cost | Так: storage/requests/versioning; baseline5GB+requests=$0.124/міс сумарно |
| Public / network | Bucket public access blocked, frontend читає тільки CF OAC |
| Security / replacement / deletion | Bucket name зміна може замінити ресурс; nonempty bucket не видалиться просто; versions накопичуються. |

### module.frontend.aws_s3_bucket_public_access_block.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_s3_bucket_public_access_block` / `this` / `module.frontend`; [код L25](../../infrastructure/terraform/modules/frontend/main.tf#L25) |
| Purpose | Усі4 механізми S3 Block Public Access |
| Depends on | `module.frontend::local.buckets`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `local.buckets; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Забороняє public bucket/ACL policy paths |
| Security / replacement / deletion | Вимкнення послаблює доступ; не замінює IAM та bucket policy. |

### module.frontend.aws_s3_bucket_versioning.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_s3_bucket_versioning` / `this` / `module.frontend`; [код L33](../../infrastructure/terraform/modules/frontend/main.tf#L33) |
| Purpose | Збереження попередніх object versions |
| Depends on | `module.frontend::local.buckets`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `local.buckets; parent module: без count` |
| Cost | Немає плати за config; старі versions оплачуються як storage |
| Public / network | Не відкриває bucket |
| Security / replacement / deletion | Немає lifecycle expiry, тому index/assets/artifacts versions можуть необмежено зростати. |

### module.frontend.aws_s3_bucket_server_side_encryption_configuration.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_s3_bucket_server_side_encryption_configuration` / `this` / `module.frontend`; [код L38](../../infrastructure/terraform/modules/frontend/main.tf#L38) |
| Purpose | SSE-S3 AES256 для objects |
| Depends on | `module.frontend::local.buckets`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `local.buckets; parent module: без count` |
| Cost | Окремої config/KMS key hourly немає |
| Public / network | Encryption at rest, не authorization |
| Security / replacement / deletion | Не забезпечує transit TLS; існуючі objects/нові keys перевіряти окремо. |

### module.frontend.aws_s3_bucket_ownership_controls.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_s3_bucket_ownership_controls` / `this` / `module.frontend`; [код L45](../../infrastructure/terraform/modules/frontend/main.tf#L45) |
| Purpose | BucketOwnerEnforced, без ACL ownership ambiguity |
| Depends on | `module.frontend::local.buckets`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `local.buckets; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | ACL відключені |
| Security / replacement / deletion | Зміна може зробити несумісними clients, які виставляють ACL. |

### module.frontend.aws_cloudfront_origin_access_control.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_cloudfront_origin_access_control` / `this` / `module.frontend`; [код L50](../../infrastructure/terraform/modules/frontend/main.tf#L50) |
| Purpose | SigV4 доступ CloudFront до S3 origin |
| Depends on | `module.frontend::var.cdn_enabled`<br>`module.frontend::var.name`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.frontend::aws_cloudfront_distribution.this` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.cdn_enabled ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Захищає приватний origin, viewer access лишається public |
| Security / replacement / deletion | Потрібні відповідна bucket policy та distribution; не захищає ALB origin. |

### module.frontend.aws_cloudfront_cache_policy.assets

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_cloudfront_cache_policy` / `assets` / `module.frontend`; [код L65](../../infrastructure/terraform/modules/frontend/main.tf#L65) |
| Purpose | Cache policy для immutable assets |
| Depends on | `module.frontend::var.cdn_enabled`<br>`module.frontend::var.name`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.frontend::aws_cloudfront_distribution.this` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.cdn_enabled ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає, traffic/requests окремо |
| Public / network | Public cached assets без cookies/query/header cache key |
| Security / replacement / deletion | Не застосовувати цю policy до персональних/API відповідей; TTL зміна впливає на stale content. |

### module.frontend.aws_cloudfront_function.routes

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_cloudfront_function` / `routes` / `module.frontend`; [код L79](../../infrastructure/terraform/modules/frontend/main.tf#L79) |
| Purpose | Viewer-request rewrite лише відомих SPA paths |
| Depends on | `module.frontend::var.cdn_enabled`<br>`module.frontend::var.name`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.frontend::aws_cloudfront_distribution.this` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.cdn_enabled ? 1 : 0; parent module: без count` |
| Cost | Так за виклики;10k calls≈$0.001 до allowances |
| Public / network | Працює на public viewer requests |
| Security / replacement / deletion | Trailing slash/невідомі routes не переписуються; code update потребує функціональних тестів. |

### module.frontend.aws_cloudfront_distribution.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_cloudfront_distribution` / `this` / `module.frontend`; [код L92](../../infrastructure/terraform/modules/frontend/main.tf#L92) |
| Purpose | HTTPS frontend та /api/* reverse proxy до origin hostname |
| Depends on | `module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::data.aws_cloudfront_cache_policy.disabled`<br>`module.frontend::data.aws_cloudfront_origin_request_policy.api`<br>`module.frontend::var.api_enabled`<br>`module.frontend::var.cdn_enabled`<br>`module.frontend::var.origin_header`<br>`module.frontend::var.origin_hostname`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::output.distribution_id`<br>`module.frontend::output.domain` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.origin_certificate_arn`<br>`root::var.origin_hostname`<br>`root::var.origin_verification_header`<br>`root::var.origin_zone_id`<br>`root::var.public_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `var.cdn_enabled ? 1 : 0; parent module: без count` |
| Cost | Так за traffic/requests; попередній10GB/100k PAYG baseline=$0.95 |
| Public / network | Public viewer endpoint; API не має CloudFront user auth |
| Security / replacement / deletion | Default certificate без custom domain; API origin може не існувати при windowfalse; propagation/disable не миттєві. |

### module.frontend.aws_s3_bucket_policy.frontend

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_s3_bucket_policy` / `frontend` / `module.frontend`; [код L158](../../infrastructure/terraform/modules/frontend/main.tf#L158) |
| Purpose | Frontend OAC SourceArn allow/TLS deny або artifact TLS deny |
| Depends on | `module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::var.cdn_enabled`<br>`module.frontend::var.storage_enabled`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.origin_certificate_arn`<br>`root::var.origin_hostname`<br>`root::var.origin_verification_header`<br>`root::var.origin_zone_id`<br>`root::var.public_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `var.storage_enabled ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Frontend не public; artifact access через IAM |
| Security / replacement / deletion | Policy change може надати/заблокувати доступ; wildcard у Deny не є wildcard Allow. |

### module.frontend.aws_s3_bucket_policy.artifacts

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_s3_bucket_policy` / `artifacts` / `module.frontend`; [код L167](../../infrastructure/terraform/modules/frontend/main.tf#L167) |
| Purpose | Frontend OAC SourceArn allow/TLS deny або artifact TLS deny |
| Depends on | `module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::var.storage_enabled`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `var.storage_enabled ? 1 : 0; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Frontend не public; artifact access через IAM |
| Security / replacement / deletion | Policy change може надати/заблокувати доступ; wildcard у Deny не є wildcard Allow. |

## module.networking


### module.networking.aws_vpc.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc` / `this` / `module.networking`; [код L18](../../infrastructure/terraform/modules/networking/main.tf#L18) |
| Purpose | Ізольований IPv4 address space та DNS |
| Depends on | `module.networking::var.name`<br>`module.networking::var.vpc_cidr`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.networking::output.vpc_id` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | VPC без додаткових сервісів: без hourly |
| Public / network | Сам не має public endpoint |
| Security / replacement / deletion | Зміна основного CIDR може вимагати заміни VPC та залежної мережі. |

### module.networking.aws_internet_gateway.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_internet_gateway` / `this` / `module.networking`; [код L24](../../infrastructure/terraform/modules/networking/main.tf#L24) |
| Purpose | Вихід public subnet до інтернету |
| Depends on | `module.networking::aws_vpc.this`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.networking::aws_route.internet` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly; transfer/IPv4 окремо |
| Public / network | Шлюз до internet; не відкриває SG самостійно |
| Security / replacement / deletion | Detach/replacement може зупинити public traffic. |

### module.networking.aws_subnet.public

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_subnet` / `public` / `module.networking`; [код L25](../../infrastructure/terraform/modules/networking/main.tf#L25) |
| Purpose | AZ-specific частина VPC для host/ALB або private DB/AI |
| Depends on | `module.networking::aws_vpc.this`<br>`module.networking::local.zones`<br>`module.networking::var.public_subnet_cidrs`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.networking::aws_route_table_association.public`<br>`module.networking::output.public_subnet_ids` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.public_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `2; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Public/private визначається route table та IP; auto public IP вимкнений |
| Security / replacement / deletion | CIDR/AZ/VPC зміни потенційно replacement; перевірити containment/non-overlap. |

### module.networking.aws_subnet.private

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_subnet` / `private` / `module.networking`; [код L32](../../infrastructure/terraform/modules/networking/main.tf#L32) |
| Purpose | AZ-specific частина VPC для host/ALB або private DB/AI |
| Depends on | `module.networking::aws_vpc.this`<br>`module.networking::local.zones`<br>`module.networking::var.private_subnet_cidrs`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.networking::aws_route_table_association.private`<br>`module.networking::output.private_subnet_ids` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.private_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `2; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Public/private визначається route table та IP; auto public IP вимкнений |
| Security / replacement / deletion | CIDR/AZ/VPC зміни потенційно replacement; перевірити containment/non-overlap. |

### module.networking.aws_route_table.public

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_route_table` / `public` / `module.networking`; [код L39](../../infrastructure/terraform/modules/networking/main.tf#L39) |
| Purpose | Набір маршрутів public або private subnet |
| Depends on | `module.networking::aws_vpc.this`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.networking::aws_route.internet`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_vpc_endpoint.s3` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Маршрути визначають reachability, не application authorization |
| Security / replacement / deletion | VPC change може замінити table; route change може розірвати connectivity. |

### module.networking.aws_route.internet

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_route` / `internet` / `module.networking`; [код L40](../../infrastructure/terraform/modules/networking/main.tf#L40) |
| Purpose | Default IPv4 route через IGW |
| Depends on | `module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route_table.public`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.networking::output.public_subnet_ids` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Internet egress/ingress можливий тільки з IP та SG |
| Security / replacement / deletion | Зміна target/table може перервати трафік; порядок host readiness не гарантований. |

### module.networking.aws_route_table_association.public

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_route_table_association` / `public` / `module.networking`; [код L45](../../infrastructure/terraform/modules/networking/main.tf#L45) |
| Purpose | Привʼязка subnet до route table |
| Depends on | `module.networking::aws_route_table.public`<br>`module.networking::aws_subnet.public`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.networking::output.public_subnet_ids` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.public_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `2; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Public/private routing policy |
| Security / replacement / deletion | Reassociation може миттєво змінити доступність subnet. |

### module.networking.aws_route_table.private

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_route_table` / `private` / `module.networking`; [код L50](../../infrastructure/terraform/modules/networking/main.tf#L50) |
| Purpose | Набір маршрутів public або private subnet |
| Depends on | `module.networking::aws_vpc.this`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.networking::aws_route_table_association.private`<br>`module.networking::aws_vpc_endpoint.s3` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Маршрути визначають reachability, не application authorization |
| Security / replacement / deletion | VPC change може замінити table; route change може розірвати connectivity. |

### module.networking.aws_route_table_association.private

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_route_table_association` / `private` / `module.networking`; [код L51](../../infrastructure/terraform/modules/networking/main.tf#L51) |
| Purpose | Привʼязка subnet до route table |
| Depends on | `module.networking::aws_route_table.private`<br>`module.networking::aws_subnet.private`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.networking::output.private_subnet_ids` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.private_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `2; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Public/private routing policy |
| Security / replacement / deletion | Reassociation може миттєво змінити доступність subnet. |

### module.networking.aws_vpc_endpoint.s3

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc_endpoint` / `s3` / `module.networking`; [код L57](../../infrastructure/terraform/modules/networking/main.tf#L57) |
| Purpose | S3 Gateway endpoint для двох route tables |
| Depends on | `module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::data.aws_region.current`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.networking::output.private_subnet_ids` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Gateway S3 без hourly, S3/transfer оплачуються окремо |
| Public / network | Приватний S3 route, не internet/NAT |
| Security / replacement / deletion | Policy default широка; не забезпечує ECR/SSM/CloudWatch/Open-Meteo. Тип/VPC зміни можуть вимагати replacement. |

## module.security


### module.security.aws_security_group.alb

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_security_group` / `alb` / `module.security`; [код L8](../../infrastructure/terraform/modules/security/main.tf#L8) |
| Purpose | Stateful firewall для ALB/backend/MySQL/AI |
| Depends on | `module.security::var.name`<br>`module.security::var.vpc_id`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`module.security::output.alb_sg` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Публічність визначають окремі rules |
| Security / replacement / deletion | Name/VPC зміни можуть замінити SG; видалення заважають attached interfaces. |

### module.security.aws_security_group.backend

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_security_group` / `backend` / `module.security`; [код L12](../../infrastructure/terraform/modules/security/main.tf#L12) |
| Purpose | Stateful firewall для ALB/backend/MySQL/AI |
| Depends on | `module.security::var.name`<br>`module.security::var.vpc_id`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`module.security::output.backend_sg` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Публічність визначають окремі rules |
| Security / replacement / deletion | Name/VPC зміни можуть замінити SG; видалення заважають attached interfaces. |

### module.security.aws_security_group.mysql

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_security_group` / `mysql` / `module.security`; [код L16](../../infrastructure/terraform/modules/security/main.tf#L16) |
| Purpose | Stateful firewall для ALB/backend/MySQL/AI |
| Depends on | `module.security::var.name`<br>`module.security::var.vpc_id`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::output.mysql_sg` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Публічність визначають окремі rules |
| Security / replacement / deletion | Name/VPC зміни можуть замінити SG; видалення заважають attached interfaces. |

### module.security.aws_security_group.ai

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_security_group` / `ai` / `module.security`; [код L20](../../infrastructure/terraform/modules/security/main.tf#L20) |
| Purpose | Stateful firewall для ALB/backend/MySQL/AI |
| Depends on | `module.security::var.name`<br>`module.security::var.vpc_id`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | `module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::output.ai_sg` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Публічність визначають окремі rules |
| Security / replacement / deletion | Name/VPC зміни можуть замінити SG; видалення заважають attached interfaces. |

### module.security.aws_vpc_security_group_ingress_rule.cloudfront

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc_security_group_ingress_rule` / `cloudfront` / `module.security`; [код L24](../../infrastructure/terraform/modules/security/main.tf#L24) |
| Purpose | Окремий дозвіл вхідного TCP traffic |
| Depends on | `module.security::aws_security_group.alb`<br>`module.security::data.aws_ec2_managed_prefix_list.cloudfront`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Див. порти/джерела у NETWORK_GRAPH |
| Security / replacement / deletion | Не є auth/TLS; зміна source/port може відкрити або перервати доступ. |

### module.security.aws_vpc_security_group_ingress_rule.targets

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc_security_group_ingress_rule` / `targets` / `module.security`; [код L31](../../infrastructure/terraform/modules/security/main.tf#L31) |
| Purpose | Окремий дозвіл вхідного TCP traffic |
| Depends on | `module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Див. порти/джерела у NETWORK_GRAPH |
| Security / replacement / deletion | Не є auth/TLS; зміна source/port може відкрити або перервати доступ. |

### module.security.aws_vpc_security_group_egress_rule.targets

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc_security_group_egress_rule` / `targets` / `module.security`; [код L38](../../infrastructure/terraform/modules/security/main.tf#L38) |
| Purpose | Окремий дозвіл вихідного TCP traffic |
| Depends on | `module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | HTTPS backend 0.0.0.0/0 або SG/S3-only |
| Security / replacement / deletion | Звузити без тестів означає ризик зупинки API/agent; не domain allowlist. |

### module.security.aws_vpc_security_group_ingress_rule.database

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc_security_group_ingress_rule` / `database` / `module.security`; [код L45](../../infrastructure/terraform/modules/security/main.tf#L45) |
| Purpose | Окремий дозвіл вхідного TCP traffic |
| Depends on | `module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Див. порти/джерела у NETWORK_GRAPH |
| Security / replacement / deletion | Не є auth/TLS; зміна source/port може відкрити або перервати доступ. |

### module.security.aws_vpc_security_group_egress_rule.database

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc_security_group_egress_rule` / `database` / `module.security`; [код L52](../../infrastructure/terraform/modules/security/main.tf#L52) |
| Purpose | Окремий дозвіл вихідного TCP traffic |
| Depends on | `module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | HTTPS backend 0.0.0.0/0 або SG/S3-only |
| Security / replacement / deletion | Звузити без тестів означає ризик зупинки API/agent; не domain allowlist. |

### module.security.aws_vpc_security_group_ingress_rule.inference

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc_security_group_ingress_rule` / `inference` / `module.security`; [код L59](../../infrastructure/terraform/modules/security/main.tf#L59) |
| Purpose | Окремий дозвіл вхідного TCP traffic |
| Depends on | `module.security::aws_security_group.ai`<br>`module.security::aws_security_group.backend`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Див. порти/джерела у NETWORK_GRAPH |
| Security / replacement / deletion | Не є auth/TLS; зміна source/port може відкрити або перервати доступ. |

### module.security.aws_vpc_security_group_egress_rule.inference

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc_security_group_egress_rule` / `inference` / `module.security`; [код L66](../../infrastructure/terraform/modules/security/main.tf#L66) |
| Purpose | Окремий дозвіл вихідного TCP traffic |
| Depends on | `module.security::aws_security_group.ai`<br>`module.security::aws_security_group.backend`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | HTTPS backend 0.0.0.0/0 або SG/S3-only |
| Security / replacement / deletion | Звузити без тестів означає ризик зупинки API/agent; не domain allowlist. |

### module.security.aws_vpc_security_group_egress_rule.https

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc_security_group_egress_rule` / `https` / `module.security`; [код L73](../../infrastructure/terraform/modules/security/main.tf#L73) |
| Purpose | Окремий дозвіл вихідного TCP traffic |
| Depends on | `module.security::aws_security_group.backend`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | HTTPS backend 0.0.0.0/0 або SG/S3-only |
| Security / replacement / deletion | Звузити без тестів означає ризик зупинки API/agent; не domain allowlist. |

### module.security.aws_vpc_security_group_egress_rule.s3

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc_security_group_egress_rule` / `s3` / `module.security`; [код L82](../../infrastructure/terraform/modules/security/main.tf#L82) |
| Purpose | Окремий дозвіл вихідного TCP traffic |
| Depends on | `module.security::aws_security_group.ai`<br>`module.security::aws_security_group.mysql`<br>`module.security::data.aws_prefix_list.s3`<br>`root::provider.aws`<br>`root::terraform_data.review_gate` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `{ ai = aws_security_group.ai.id, mysql = aws_security_group.mysql.id }; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | HTTPS backend 0.0.0.0/0 або SG/S3-only |
| Security / replacement / deletion | Звузити без тестів означає ризик зупинки API/agent; не domain allowlist. |

## root


### root.terraform_data.review_gate

| Поле | Пояснення |
|---|---|
| Type / name / module | `terraform_data` / `review_gate` / `root`; [код L6](../../infrastructure/terraform/main.tf#L6) |
| Purpose | Review/precondition gate |
| Depends on | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Used by | `module.ai::aws_ec2_instance_state.power`<br>`module.ai::aws_iam_instance_profile.this`<br>`module.ai::aws_iam_role.this`<br>`module.ai::aws_iam_role_policy.read`<br>`module.ai::aws_instance.this`<br>`module.alb::aws_lb.this`<br>`module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_listener_rule.origin`<br>`module.alb::aws_lb_target_group.backend`<br>`module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_cloudwatch_log_group.backend`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role.execution`<br>`module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role.task`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`module.backend::aws_launch_template.host`<br>`module.database::aws_db_instance.this`<br>`module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::aws_iam_instance_profile.backup`<br>`module.database::aws_iam_role.backup`<br>`module.database::aws_iam_role_policy.backup`<br>`module.database::aws_instance.mysql`<br>`module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::aws_ecr_repository.ecr`<br>`module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.artifacts`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::aws_s3_bucket_ownership_controls.this`<br>`module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::aws_s3_bucket_public_access_block.this`<br>`module.frontend::aws_s3_bucket_server_side_encryption_configuration.this`<br>`module.frontend::aws_s3_bucket_versioning.this`<br>`module.frontend::data.aws_cloudfront_cache_policy.disabled`<br>`module.frontend::data.aws_cloudfront_origin_request_policy.api`<br>`module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route.internet`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_route_table_association.private`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.networking::data.aws_availability_zones.available`<br>`module.networking::data.aws_region.current`<br>`module.security::aws_security_group.ai`<br>`module.security::aws_security_group.alb`<br>`module.security::aws_security_group.backend`<br>`module.security::aws_security_group.mysql`<br>`module.security::aws_vpc_security_group_egress_rule.database`<br>`module.security::aws_vpc_security_group_egress_rule.https`<br>`module.security::aws_vpc_security_group_egress_rule.inference`<br>`module.security::aws_vpc_security_group_egress_rule.s3`<br>`module.security::aws_vpc_security_group_egress_rule.targets`<br>`module.security::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.security::aws_vpc_security_group_ingress_rule.database`<br>`module.security::aws_vpc_security_group_ingress_rule.inference`<br>`module.security::aws_vpc_security_group_ingress_rule.targets`<br>`module.security::data.aws_ec2_managed_prefix_list.cloudfront`<br>`module.security::data.aws_prefix_list.s3`<br>`module.security::data.aws_region.current`<br>`root::module.ai`<br>`root::module.alb`<br>`root::module.backend`<br>`root::module.database`<br>`root::module.ecr`<br>`root::module.frontend`<br>`root::module.networking`<br>`root::module.security` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib` |
| Creation / condition | `Без власного count/for_each` |
| Cost | Немає AWS hourly |
| Public / network | Без endpoint |
| Security / replacement / deletion | Module depends_on повʼязує gate з усіма етапами; false навмисно блокує Plan. Це не IAM policy і не гарантія проти вилучення guard з конфігурації. |

### root.aws_route53_record.origin

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_route53_record` / `origin` / `root`; [код L139](../../infrastructure/terraform/main.tf#L139) |
| Purpose | A alias origin hostname→ALB у вже існуючій hosted zone |
| Depends on | `module.alb::output.dns`<br>`module.alb::output.listener_arn`<br>`module.alb::output.zone_id`<br>`root::provider.aws`<br>`root::var.application_window_open`<br>`root::var.origin_hostname`<br>`root::var.origin_zone_id` |
| Used by | `root::module.frontend.input.origin_hostname` |
| Root inputs, transitively | `root::var.ai_enabled`<br>`root::var.ai_provisioned`<br>`root::var.ai_runtime_reviewed`<br>`root::var.application_window_open`<br>`root::var.artifacts_provisioned`<br>`root::var.aws_region`<br>`root::var.backend_instance_type`<br>`root::var.backend_provisioned`<br>`root::var.database_provisioned`<br>`root::var.edge_provisioned`<br>`root::var.environment`<br>`root::var.infrastructure_reviewed`<br>`root::var.ml_service_url`<br>`root::var.name_suffix`<br>`root::var.origin_certificate_arn`<br>`root::var.origin_hostname`<br>`root::var.origin_verification_header`<br>`root::var.origin_zone_id`<br>`root::var.public_subnet_cidrs`<br>`root::var.runtime_secret_arns`<br>`root::var.service_enabled`<br>`root::var.task_memory_mib`<br>`root::var.vpc_cidr` |
| Creation / condition | `var.application_window_open ? 1 : 0` |
| Cost | Окремої плати за record немає; zone/queries/account usage окремо |
| Public / network | Public DNS record, не сам web endpoint |
| Security / replacement / deletion | Countoff прибирає alias; зміна hostname/zone може замінити record, не реєструє домен/сертифікат. |
