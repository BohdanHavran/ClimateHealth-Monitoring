# Повний аудит resource blocks

У цьому переліку кожен із 55 AWS resource blocks має окрему таблицю. count/for_each instances не обчислено. «Завжди» означає наявність блоку без його count, а не факт існування ресурсу в AWS. Умовність батьківського module також враховано.

Dependencies/consumers витягнуті з traversals/input-output bindings і явних depends_on. provider/variables/locals можуть зʼявлятися як залежності, не лише AWS ресурси. Region/account permissions/API availability і реальний AWS state не перевірялися. Replacement оцінка консервативна: точне replace/update/destroy визначить лише дозволений provider Plan з існуючим state; нижче не вигадано ForceNew schema.

Cost notes — орієнтири us-east-1 зі збереженого кошторису24.11 та переглянутих офіційних цін, не bill prediction. Не підсумовувати повʼязані policy/rule charges удруге. Детальна різниця reserve/реальних ресурсів — [COST_AUDIT](COST_AUDIT.md).


## module.alb


### module.alb.aws_lb.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_lb` / `this` / `module.alb`; [код L18](../../infrastructure/terraform/modules/alb/main.tf#L18) |
| Purpose | Internet-facing HTTPS Application Load Balancer |
| Depends on | `module.alb::var.security_group`<br>`module.alb::var.subnet_ids`<br>`root::module.alb`<br>`root::provider.aws` |
| Used by | `module.alb::aws_lb_listener.https`<br>`module.alb::output.dns`<br>`module.alb::output.zone_id` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.deploy_application`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: var.deploy_application ? 1 : 0` |
| Cost | Так: $0.0225/h + LCU + щонайменше2 IPv4 по$0.005/h |
| Public / network | Public443, SG обмежує CloudFront prefix |
| Security / replacement / deletion | ALB не зупиняється разом з EC2; заміна/VPC/subnet зміни вимагають review; немає access logs/deletion protection. |

### module.alb.aws_lb_target_group.backend

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_lb_target_group` / `backend` / `module.alb`; [код L28](../../infrastructure/terraform/modules/alb/main.tf#L28) |
| Purpose | Instance targets host8080, health /health/ready |
| Depends on | `module.alb::var.vpc_id`<br>`root::module.alb`<br>`root::provider.aws` |
| Used by | `module.alb::aws_lb_listener_rule.origin`<br>`module.alb::output.target_group_arn` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.deploy_application`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: var.deploy_application ? 1 : 0` |
| Cost | Не окрема hourly; LCU рахують на ALB |
| Public / network | HTTP8080 лише внутрішній SG шлях |
| Security / replacement / deletion | Protocol/target_type/VPC зміни потенційно replacement; readiness залежить від DB TLS/reader. |

### module.alb.aws_lb_listener.https

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_lb_listener` / `https` / `module.alb`; [код L46](../../infrastructure/terraform/modules/alb/main.tf#L46) |
| Purpose | HTTPS443 listener з переданим ACM та default403 |
| Depends on | `module.alb::aws_lb.this`<br>`module.alb::var.certificate_arn`<br>`root::module.alb`<br>`root::provider.aws` |
| Used by | `module.alb::aws_lb_listener_rule.origin` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.deploy_application`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.origin_certificate_arn`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: var.deploy_application ? 1 : 0` |
| Cost | Не окрема hourly, ALB/LCU окремо |
| Public / network | Public TLS listener під SG CloudFront gate |
| Security / replacement / deletion | Certificate має існувати/бути виданий/покривати origin hostname; зміна listener може перервати TLS. |

### module.alb.aws_lb_listener_rule.origin

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_lb_listener_rule` / `origin` / `module.alb`; [код L62](../../infrastructure/terraform/modules/alb/main.tf#L62) |
| Purpose | Forward лише за секретним origin header |
| Depends on | `module.alb::aws_lb_listener.https`<br>`module.alb::aws_lb_target_group.backend`<br>`module.alb::var.origin_header`<br>`root::module.alb`<br>`root::provider.aws` |
| Used by | `module.alb::output.listener_rule_arn` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.deploy_application`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.origin_certificate_arn`<br>`root::var.origin_verification_header`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: var.deploy_application ? 1 : 0` |
| Cost | Не окрема hourly, rule evaluations можуть впливати на LCU |
| Public / network | Header restriction, не user authentication |
| Security / replacement / deletion | Header зберігається у state/CloudFront; rotation потребує узгодження обох сторін. |

## module.backend


### module.backend.aws_ecs_cluster.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_ecs_cluster` / `this` / `module.backend`; [код L53](../../infrastructure/terraform/modules/ecs-backend/main.tf#L53) |
| Purpose | Логічний ECS cluster, Container Insights disabled |
| Depends on | `module.backend::var.name`<br>`root::module.backend`<br>`root::provider.aws` |
| Used by | `module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::aws_launch_template.host`<br>`module.backend::output.cluster` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.deploy_application`<br>`root::var.environment`<br>`root::var.name_suffix` |
| Creation / condition | `Без власного count/for_each; parent module: var.deploy_application ? 1 : 0` |
| Cost | ECS EC2 control plane без окремої compute hourly; hosts оплачуються |
| Public / network | Не public application endpoint |
| Security / replacement / deletion | Cluster name зміна може вимагати replacement; один host/AZ не HA. |

### module.backend.aws_iam_role.host

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_role` / `host` / `module.backend`; [код L64](../../infrastructure/terraform/modules/ecs-backend/main.tf#L64) |
| Purpose | Окремі EC2 host та ECS execution identities. |
| Depends on | `module.backend::local.ec2_trust`<br>`module.backend::var.name`<br>`module.backend::var.permissions_boundary_arn`<br>`root::module.backend`<br>`root::provider.aws` |
| Used by | `module.backend::aws_iam_instance_profile.host`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.deploy_application`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn` |
| Creation / condition | `Без власного count/for_each; parent module: var.deploy_application ? 1 : 0` |
| Cost | Без окремої hourly |
| Public / network | Service trust; не мережевий endpoint. |
| Security / replacement / deletion | Існуюча permissions boundary потрібна API; task role без permissions видалена. Boundary content не перевірено. |

### module.backend.aws_iam_role_policy_attachment.agent

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_role_policy_attachment` / `agent` / `module.backend`; [код L69](../../infrastructure/terraform/modules/ecs-backend/main.tf#L69) |
| Purpose | AWS managed host ECS agent або SSM policy |
| Depends on | `module.backend::aws_iam_role.host`<br>`root::module.backend`<br>`root::provider.aws` |
| Used by | `module.backend::aws_iam_instance_profile.host` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.deploy_application`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn` |
| Creation / condition | `Без власного count/for_each; parent module: var.deploy_application ? 1 : 0` |
| Cost | Окремої hourly немає |
| Public / network | IAM permissions, не network egress |
| Security / replacement / deletion | Managed policies ширші за custom scope; launch template не залежить прямо від attachments. |

### module.backend.aws_iam_role_policy_attachment.ssm

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_role_policy_attachment` / `ssm` / `module.backend`; [код L73](../../infrastructure/terraform/modules/ecs-backend/main.tf#L73) |
| Purpose | AWS managed host ECS agent або SSM policy |
| Depends on | `module.backend::aws_iam_role.host`<br>`root::module.backend`<br>`root::provider.aws` |
| Used by | `module.backend::aws_iam_instance_profile.host` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.deploy_application`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn` |
| Creation / condition | `Без власного count/for_each; parent module: var.deploy_application ? 1 : 0` |
| Cost | Окремої hourly немає |
| Public / network | IAM permissions, не network egress |
| Security / replacement / deletion | Managed policies ширші за custom scope; launch template не залежить прямо від attachments. |

### module.backend.aws_iam_instance_profile.host

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_instance_profile` / `host` / `module.backend`; [код L77](../../infrastructure/terraform/modules/ecs-backend/main.tf#L77) |
| Purpose | Передача IAM role EC2 instance |
| Depends on | `module.backend::aws_iam_role.host`<br>`module.backend::aws_iam_role_policy_attachment.agent`<br>`module.backend::aws_iam_role_policy_attachment.ssm`<br>`root::module.backend`<br>`root::provider.aws` |
| Used by | `module.backend::aws_launch_template.host` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.deploy_application`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn` |
| Creation / condition | `Без власного count/for_each; parent module: var.deploy_application ? 1 : 0` |
| Cost | Окремої hourly немає |
| Public / network | Credentials через IMDSv2, не public endpoint |
| Security / replacement / deletion | Не чекає attachment/inline policy readiness само по собі; name/role зміни перевірити перед заміною. |

### module.backend.aws_iam_role.execution

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_role` / `execution` / `module.backend`; [код L81](../../infrastructure/terraform/modules/ecs-backend/main.tf#L81) |
| Purpose | Окремі EC2 host та ECS execution identities. |
| Depends on | `module.backend::local.task_trust`<br>`module.backend::var.name`<br>`module.backend::var.permissions_boundary_arn`<br>`root::module.backend`<br>`root::provider.aws` |
| Used by | `module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_role_policy.execution` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.deploy_application`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn` |
| Creation / condition | `Без власного count/for_each; parent module: var.deploy_application ? 1 : 0` |
| Cost | Без окремої hourly |
| Public / network | Service trust; не мережевий endpoint. |
| Security / replacement / deletion | Існуюча permissions boundary потрібна API; task role без permissions видалена. Boundary content не перевірено. |

### module.backend.aws_iam_role_policy.execution

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_iam_role_policy` / `execution` / `module.backend`; [код L86](../../infrastructure/terraform/modules/ecs-backend/main.tf#L86) |
| Purpose | Custom inline permissions execution/AI/backup |
| Depends on | `module.backend::aws_iam_role.execution`<br>`module.backend::var.log_group_arn`<br>`module.backend::var.repository_arn`<br>`module.backend::var.secret_arns`<br>`root::module.backend`<br>`root::provider.aws` |
| Used by | `module.backend::aws_ecs_service.this` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.deploy_application`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns` |
| Creation / condition | `Без власного count/for_each; parent module: var.deploy_application ? 1 : 0` |
| Cost | Окремої hourly немає |
| Public / network | ECR/SSM/logs/S3 IAM scope |
| Security / replacement / deletion | Execution role auth token Resource* потрібний API; secrets можуть потребувати kms:Decrypt для CMK. Не всі startup paths залежать від policy attachment. |

### module.backend.aws_launch_template.host

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_launch_template` / `host` / `module.backend`; [код L95](../../infrastructure/terraform/modules/ecs-backend/main.tf#L95) |
| Purpose | Approved AL2023 ECS AMI, t3.small, encrypted20GBgp3, IMDSv2. |
| Depends on | `module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_iam_instance_profile.host`<br>`module.backend::var.ami_id`<br>`module.backend::var.name`<br>`module.backend::var.security_group`<br>`module.backend::var.tags`<br>`root::module.backend`<br>`root::provider.aws` |
| Used by | `module.backend::aws_autoscaling_group.host` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.deploy_application`<br>`root::var.ecs_ami_id`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: var.deploy_application ? 1 : 0` |
| Cost | Створені host/EBS/IPv4 оплачуються. |
| Public / network | Public IP, inbound лише ALB SG8080; SSH немає. |
| Security / replacement / deletion | EC2/EBS tags є; нова LT version не перезапускає наявні hosts, Instance Refresh окремо погоджується. |

### module.backend.aws_autoscaling_group.host

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_autoscaling_group` / `host` / `module.backend`; [код L141](../../infrastructure/terraform/modules/ecs-backend/main.tf#L141) |
| Purpose | Host capacity0/1, optionalmax2 для deployment |
| Depends on | `module.backend::aws_launch_template.host`<br>`module.backend::var.desired_count`<br>`module.backend::var.max_instances`<br>`module.backend::var.name`<br>`module.backend::var.subnet_id`<br>`module.backend::var.tags`<br>`root::module.backend`<br>`root::provider.aws` |
| Used by | `module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::output.asg_name` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.backend_desired_count`<br>`root::var.backend_max_instances`<br>`root::var.deploy_application`<br>`root::var.ecs_ami_id`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: var.deploy_application ? 1 : 0` |
| Cost | Так для EC2/IP/EBS: t3.small$0.0208/h +IPv4$0.005/h |
| Public / network | Одна public subnet/AZ, SG контролює host8080 |
| Security / replacement / deletion | desired_capacity ignore_changes; health_check_type EC2 не ALB. Max1/from-zero/rolling потребують тестів; видалення host видаляє root EBS. |

### module.backend.aws_ecs_capacity_provider.host

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_ecs_capacity_provider` / `host` / `module.backend`; [код L173](../../infrastructure/terraform/modules/ecs-backend/main.tf#L173) |
| Purpose | Managed scaling/draining backend ASG. |
| Depends on | `module.backend::aws_autoscaling_group.host`<br>`module.backend::var.name`<br>`root::module.backend`<br>`root::provider.aws` |
| Used by | `module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_service.this`<br>`module.backend::output.capacity_provider` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.backend_desired_count`<br>`root::var.backend_max_instances`<br>`root::var.deploy_application`<br>`root::var.ecs_ami_id`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: var.deploy_application ? 1 : 0` |
| Cost | EC2/EBS/IP та managed monitoring charges окремо. |
| Public / network | Control plane, не endpoint. |
| Security / replacement / deletion | Початковий empty-ASG bootstrap при count0; count1 лише після association. Scale-from-zero/rolling runtime не перевірено. |

### module.backend.aws_ecs_cluster_capacity_providers.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_ecs_cluster_capacity_providers` / `this` / `module.backend`; [код L190](../../infrastructure/terraform/modules/ecs-backend/main.tf#L190) |
| Purpose | Асоціація Capacity Provider з cluster |
| Depends on | `module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`root::module.backend`<br>`root::provider.aws` |
| Used by | `module.backend::aws_ecs_service.this` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.backend_desired_count`<br>`root::var.backend_max_instances`<br>`root::var.deploy_application`<br>`root::var.ecs_ami_id`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: var.deploy_application ? 1 : 0` |
| Cost | Окремої hourly немає |
| Public / network | Не endpoint |
| Security / replacement / deletion | Не окремий Capacity Provider; зміна асоціації впливає на scheduling. |

### module.backend.aws_ecs_task_definition.initial

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_ecs_task_definition` / `initial` / `module.backend`; [код L196](../../infrastructure/terraform/modules/ecs-backend/main.tf#L196) |
| Purpose | HCP-owned backend revision: bridge8000/8080,1024MiB, read-only root. |
| Depends on | `module.backend::aws_iam_role.execution`<br>`module.backend::var.db_host`<br>`module.backend::var.image`<br>`module.backend::var.log_group_name`<br>`module.backend::var.name`<br>`module.backend::var.region`<br>`module.backend::var.secret_arns`<br>`root::module.backend`<br>`root::provider.aws` |
| Used by | `module.backend::aws_ecs_service.this`<br>`module.backend::output.task_definition_arn` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.backend_image`<br>`root::var.deploy_application`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: var.deploy_application ? 1 : 0` |
| Cost | Без compute hourly за declaration. |
| Public / network | Task definition сама не запускає container. |
| Security / replacement / deletion | DB verify_identity/CA env передані; runtime reader та TLS chain ще перевірити. tmpfs споживає RAM; ML runtime не provisioned. |

### module.backend.aws_ecs_service.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_ecs_service` / `this` / `module.backend`; [код L218](../../infrastructure/terraform/modules/ecs-backend/main.tf#L218) |
| Purpose | HCP-owned service через CP, ALB readiness, circuit breaker і steady-state waiter. |
| Depends on | `module.backend::aws_autoscaling_group.host`<br>`module.backend::aws_ecs_capacity_provider.host`<br>`module.backend::aws_ecs_cluster.this`<br>`module.backend::aws_ecs_cluster_capacity_providers.this`<br>`module.backend::aws_ecs_task_definition.initial`<br>`module.backend::aws_iam_role_policy.execution`<br>`module.backend::var.desired_count`<br>`module.backend::var.listener_rule_arn`<br>`module.backend::var.max_instances`<br>`module.backend::var.target_group_arn`<br>`root::module.backend`<br>`root::provider.aws` |
| Used by | `module.backend::output.service` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.backend_desired_count`<br>`root::var.backend_image`<br>`root::var.backend_max_instances`<br>`root::var.deploy_application`<br>`root::var.ecs_ami_id`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.origin_certificate_arn`<br>`root::var.origin_verification_header`<br>`root::var.permissions_boundary_arn`<br>`root::var.runtime_secret_arns`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: var.deploy_application ? 1 : 0` |
| Cost | Capacity/ALB/log charges. |
| Public / network | ALB до instance8080. |
| Security / replacement / deletion | HCP володіє task_definition. Default min0 допускає downtime; host8080 потребує другого EC2 для rolling, ще не перевірено. |

## module.database


### module.database.aws_db_subnet_group.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_db_subnet_group` / `this` / `module.database`; [код L13](../../infrastructure/terraform/modules/mysql/main.tf#L13) |
| Purpose | Private subnet placement group для RDS |
| Depends on | `module.database::var.subnet_ids`<br>`root::provider.aws` |
| Used by | `module.database::aws_db_instance.this` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Не endpoint; дві subnet AZ, RDS усе одно Single-AZ |
| Security / replacement / deletion | Subnet/VPC зміни можуть впливати на replacement/доступність DB. |

### module.database.aws_db_parameter_group.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_db_parameter_group` / `this` / `module.database`; [код L16](../../infrastructure/terraform/modules/mysql/main.tf#L16) |
| Purpose | mysql8.4 require_secure_transport=ON |
| Depends on | `root::provider.aws` |
| Used by | `module.database::aws_db_instance.this` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Вимагає TLS до DB endpoint |
| Security / replacement / deletion | Family change/reboot може бути необхідний; поточний PyMySQL client TLS ще не налаштований. |

### module.database.aws_db_instance.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_db_instance` / `this` / `module.database`; [код L23](../../infrastructure/terraform/modules/mysql/main.tf#L23) |
| Purpose | Encrypted private MySQL8.4.13 Single-AZ,managed master secret,backup7днів |
| Depends on | `module.database::aws_db_parameter_group.this`<br>`module.database::aws_db_subnet_group.this`<br>`module.database::var.availability_zone`<br>`module.database::var.name`<br>`module.database::var.security_group`<br>`root::provider.aws` |
| Used by | `module.database::output.host` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Так навіть при appwindowfalse:0.016/h +20GBgp3$2.30/міс +managed secret |
| Public / network | publicly_accessible=false,3306 тільки backendSG |
| Security / replacement / deletion | deletion_protection/finalsnapshot захищають, але не обнуляють витрати; snapshotname повторно може конфліктувати; engine/class availability перевірити в region. |

## module.ecr


### module.ecr.aws_ecr_repository.ecr

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_ecr_repository` / `ecr` / `module.ecr`; [код L2](../../infrastructure/terraform/modules/ecr/main.tf#L2) |
| Purpose | Єдиний backend immutable image repository. |
| Depends on | `module.ecr::var.ecr_names`<br>`root::provider.aws` |
| Used by | `module.ecr::aws_ecr_lifecycle_policy.images`<br>`module.ecr::output.arns`<br>`module.ecr::output.urls` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix` |
| Creation / condition | `toset(var.ecr_names); parent module: без count` |
| Cost | Storage/transfer за використанням; порожній repository без storage charge. |
| Public / network | IAM-only AWS API. |
| Security / replacement / deletion | prevent_destroy; tagged images накопичуються, retention потребує review. |

### module.ecr.aws_ecr_lifecycle_policy.images

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_ecr_lifecycle_policy` / `images` / `module.ecr`; [код L19](../../infrastructure/terraform/modules/ecr/main.tf#L19) |
| Purpose | Видалення untagged images через14днів |
| Depends on | `module.ecr::aws_ecr_repository.ecr`<br>`root::provider.aws` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix` |
| Creation / condition | `aws_ecr_repository.ecr; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Management policy, не endpoint |
| Security / replacement / deletion | Не видаляє tagged releases; занадто короткий retention може знищити rollback images. |

## module.frontend


### module.frontend.aws_s3_bucket.frontend

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_s3_bucket` / `frontend` / `module.frontend`; [код L13](../../infrastructure/terraform/modules/frontend/main.tf#L13) |
| Purpose | Private frontend assets або artifacts/backups |
| Depends on | `module.frontend::var.name`<br>`root::provider.aws` |
| Used by | `module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::local.buckets`<br>`module.frontend::output.bucket` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Так: storage/requests/versioning; baseline5GB+requests=$0.124/міс сумарно |
| Public / network | Bucket public access blocked, frontend читає тільки CF OAC |
| Security / replacement / deletion | Bucket name зміна може замінити ресурс; nonempty bucket не видалиться просто; versions накопичуються. |

### module.frontend.aws_s3_bucket.artifacts

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_s3_bucket` / `artifacts` / `module.frontend`; [код L17](../../infrastructure/terraform/modules/frontend/main.tf#L17) |
| Purpose | Private frontend assets або artifacts/backups |
| Depends on | `module.frontend::var.name`<br>`root::provider.aws` |
| Used by | `module.frontend::aws_s3_bucket_policy.artifacts`<br>`module.frontend::local.buckets`<br>`module.frontend::output.artifact_bucket`<br>`module.frontend::output.artifact_bucket_arn` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Так: storage/requests/versioning; baseline5GB+requests=$0.124/міс сумарно |
| Public / network | Bucket public access blocked, frontend читає тільки CF OAC |
| Security / replacement / deletion | Bucket name зміна може замінити ресурс; nonempty bucket не видалиться просто; versions накопичуються. |

### module.frontend.aws_s3_bucket_public_access_block.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_s3_bucket_public_access_block` / `this` / `module.frontend`; [код L22](../../infrastructure/terraform/modules/frontend/main.tf#L22) |
| Purpose | Усі4 механізми S3 Block Public Access |
| Depends on | `module.frontend::local.buckets`<br>`root::provider.aws` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix` |
| Creation / condition | `local.buckets; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Забороняє public bucket/ACL policy paths |
| Security / replacement / deletion | Вимкнення послаблює доступ; не замінює IAM та bucket policy. |

### module.frontend.aws_s3_bucket_versioning.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_s3_bucket_versioning` / `this` / `module.frontend`; [код L30](../../infrastructure/terraform/modules/frontend/main.tf#L30) |
| Purpose | Збереження попередніх object versions |
| Depends on | `module.frontend::local.buckets`<br>`root::provider.aws` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix` |
| Creation / condition | `local.buckets; parent module: без count` |
| Cost | Немає плати за config; старі versions оплачуються як storage |
| Public / network | Не відкриває bucket |
| Security / replacement / deletion | Немає lifecycle expiry, тому index/assets/artifacts versions можуть необмежено зростати. |

### module.frontend.aws_s3_bucket_server_side_encryption_configuration.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_s3_bucket_server_side_encryption_configuration` / `this` / `module.frontend`; [код L35](../../infrastructure/terraform/modules/frontend/main.tf#L35) |
| Purpose | SSE-S3 AES256 для objects |
| Depends on | `module.frontend::local.buckets`<br>`root::provider.aws` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix` |
| Creation / condition | `local.buckets; parent module: без count` |
| Cost | Окремої config/KMS key hourly немає |
| Public / network | Encryption at rest, не authorization |
| Security / replacement / deletion | Не забезпечує transit TLS; існуючі objects/нові keys перевіряти окремо. |

### module.frontend.aws_s3_bucket_ownership_controls.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_s3_bucket_ownership_controls` / `this` / `module.frontend`; [код L42](../../infrastructure/terraform/modules/frontend/main.tf#L42) |
| Purpose | BucketOwnerEnforced, без ACL ownership ambiguity |
| Depends on | `module.frontend::local.buckets`<br>`root::provider.aws` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix` |
| Creation / condition | `local.buckets; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | ACL відключені |
| Security / replacement / deletion | Зміна може зробити несумісними clients, які виставляють ACL. |

### module.frontend.aws_cloudfront_origin_access_control.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_cloudfront_origin_access_control` / `this` / `module.frontend`; [код L47](../../infrastructure/terraform/modules/frontend/main.tf#L47) |
| Purpose | SigV4 доступ CloudFront до S3 origin |
| Depends on | `module.frontend::var.name`<br>`root::provider.aws` |
| Used by | `module.frontend::aws_cloudfront_distribution.this` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Захищає приватний origin, viewer access лишається public |
| Security / replacement / deletion | Потрібні відповідна bucket policy та distribution; не захищає ALB origin. |

### module.frontend.aws_cloudfront_cache_policy.assets

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_cloudfront_cache_policy` / `assets` / `module.frontend`; [код L62](../../infrastructure/terraform/modules/frontend/main.tf#L62) |
| Purpose | Cache policy для immutable assets |
| Depends on | `module.frontend::var.name`<br>`root::provider.aws` |
| Used by | `module.frontend::aws_cloudfront_distribution.this` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Окремої hourly немає, traffic/requests окремо |
| Public / network | Public cached assets без cookies/query/header cache key |
| Security / replacement / deletion | Не застосовувати цю policy до персональних/API відповідей; TTL зміна впливає на stale content. |

### module.frontend.aws_cloudfront_function.routes

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_cloudfront_function` / `routes` / `module.frontend`; [код L76](../../infrastructure/terraform/modules/frontend/main.tf#L76) |
| Purpose | Viewer-request rewrite лише відомих SPA paths |
| Depends on | `module.frontend::var.name`<br>`root::provider.aws` |
| Used by | `module.frontend::aws_cloudfront_distribution.this` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Так за виклики;10k calls≈$0.001 до allowances |
| Public / network | Працює на public viewer requests |
| Security / replacement / deletion | Trailing slash/невідомі routes не переписуються; code update потребує функціональних тестів. |

### module.frontend.aws_cloudfront_distribution.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_cloudfront_distribution` / `this` / `module.frontend`; [код L89](../../infrastructure/terraform/modules/frontend/main.tf#L89) |
| Purpose | HTTPS frontend та /api/* reverse proxy до origin hostname |
| Depends on | `module.frontend::aws_cloudfront_cache_policy.assets`<br>`module.frontend::aws_cloudfront_function.routes`<br>`module.frontend::aws_cloudfront_origin_access_control.this`<br>`module.frontend::aws_s3_bucket.frontend`<br>`module.frontend::data.aws_cloudfront_cache_policy.disabled`<br>`module.frontend::data.aws_cloudfront_origin_request_policy.api`<br>`module.frontend::var.api_enabled`<br>`module.frontend::var.origin_header`<br>`module.frontend::var.origin_hostname`<br>`root::provider.aws` |
| Used by | `module.frontend::aws_s3_bucket_policy.frontend`<br>`module.frontend::output.distribution_id`<br>`module.frontend::output.domain` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.deploy_application`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.origin_certificate_arn`<br>`root::var.origin_hostname`<br>`root::var.origin_verification_header`<br>`root::var.origin_zone_id`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Так за traffic/requests; попередній10GB/100k PAYG baseline=$0.95 |
| Public / network | Public viewer endpoint; API не має CloudFront user auth |
| Security / replacement / deletion | Default certificate без custom domain; API origin може не існувати при windowfalse; propagation/disable не миттєві. |

### module.frontend.aws_s3_bucket_policy.frontend

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_s3_bucket_policy` / `frontend` / `module.frontend`; [код L155](../../infrastructure/terraform/modules/frontend/main.tf#L155) |
| Purpose | Frontend OAC SourceArn allow/TLS deny або artifact TLS deny |
| Depends on | `module.frontend::aws_cloudfront_distribution.this`<br>`module.frontend::aws_s3_bucket.frontend`<br>`root::provider.aws` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.deploy_application`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.origin_certificate_arn`<br>`root::var.origin_hostname`<br>`root::var.origin_verification_header`<br>`root::var.origin_zone_id`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Frontend не public; artifact access через IAM |
| Security / replacement / deletion | Policy change може надати/заблокувати доступ; wildcard у Deny не є wildcard Allow. |

### module.frontend.aws_s3_bucket_policy.artifacts

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_s3_bucket_policy` / `artifacts` / `module.frontend`; [код L164](../../infrastructure/terraform/modules/frontend/main.tf#L164) |
| Purpose | Frontend OAC SourceArn allow/TLS deny або artifact TLS deny |
| Depends on | `module.frontend::aws_s3_bucket.artifacts`<br>`root::provider.aws` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Окремої hourly немає |
| Public / network | Frontend не public; artifact access через IAM |
| Security / replacement / deletion | Policy change може надати/заблокувати доступ; wildcard у Deny не є wildcard Allow. |

## module.networking


### module.networking.aws_vpc.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc` / `this` / `module.networking`; [код L10](../../infrastructure/terraform/modules/networking/main.tf#L10) |
| Purpose | Ізольований IPv4 address space та DNS |
| Depends on | `module.networking::var.name`<br>`module.networking::var.vpc_cidr`<br>`root::provider.aws` |
| Used by | `module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_security_group.alb`<br>`module.networking::aws_security_group.backend`<br>`module.networking::aws_security_group.mysql`<br>`module.networking::aws_subnet.private`<br>`module.networking::aws_subnet.public`<br>`module.networking::aws_vpc_endpoint.s3`<br>`module.networking::output.vpc_id` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | VPC без додаткових сервісів: без hourly |
| Public / network | Сам не має public endpoint |
| Security / replacement / deletion | Зміна основного CIDR може вимагати заміни VPC та залежної мережі. |

### module.networking.aws_internet_gateway.this

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_internet_gateway` / `this` / `module.networking`; [код L19](../../infrastructure/terraform/modules/networking/main.tf#L19) |
| Purpose | Вихід public subnet до інтернету |
| Depends on | `module.networking::aws_vpc.this`<br>`module.networking::var.name`<br>`root::provider.aws` |
| Used by | `module.networking::aws_route.internet` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly; transfer/IPv4 окремо |
| Public / network | Шлюз до internet; не відкриває SG самостійно |
| Security / replacement / deletion | Detach/replacement може зупинити public traffic. |

### module.networking.aws_subnet.public

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_subnet` / `public` / `module.networking`; [код L25](../../infrastructure/terraform/modules/networking/main.tf#L25) |
| Purpose | Дві public та дві private /24 subnets у двох AZ. |
| Depends on | `module.networking::aws_vpc.this`<br>`module.networking::local.zones`<br>`module.networking::var.name`<br>`module.networking::var.vpc_cidr`<br>`root::provider.aws` |
| Used by | `module.networking::aws_route_table_association.public`<br>`module.networking::output.public_subnet_ids` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `2; parent module: без count` |
| Cost | Без окремої hourly |
| Public / network | Private DB без internet default route; public host має явну IP у LT. |
| Security / replacement / deletion | CIDR/AZ/VPC зміни можуть спричинити replacement. |

### module.networking.aws_subnet.private

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_subnet` / `private` / `module.networking`; [код L36](../../infrastructure/terraform/modules/networking/main.tf#L36) |
| Purpose | Дві public та дві private /24 subnets у двох AZ. |
| Depends on | `module.networking::aws_vpc.this`<br>`module.networking::local.zones`<br>`module.networking::var.name`<br>`module.networking::var.vpc_cidr`<br>`root::provider.aws` |
| Used by | `module.networking::aws_route_table_association.private`<br>`module.networking::output.private_subnet_ids` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `2; parent module: без count` |
| Cost | Без окремої hourly |
| Public / network | Private DB без internet default route; public host має явну IP у LT. |
| Security / replacement / deletion | CIDR/AZ/VPC зміни можуть спричинити replacement. |

### module.networking.aws_route_table.public

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_route_table` / `public` / `module.networking`; [код L47](../../infrastructure/terraform/modules/networking/main.tf#L47) |
| Purpose | Набір маршрутів public або private subnet |
| Depends on | `module.networking::aws_vpc.this`<br>`root::provider.aws` |
| Used by | `module.networking::aws_route.internet`<br>`module.networking::aws_route_table_association.public`<br>`module.networking::aws_vpc_endpoint.s3` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Маршрути визначають reachability, не application authorization |
| Security / replacement / deletion | VPC change може замінити table; route change може розірвати connectivity. |

### module.networking.aws_route.internet

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_route` / `internet` / `module.networking`; [код L48](../../infrastructure/terraform/modules/networking/main.tf#L48) |
| Purpose | Default IPv4 route через IGW |
| Depends on | `module.networking::aws_internet_gateway.this`<br>`module.networking::aws_route_table.public`<br>`root::provider.aws` |
| Used by | `module.networking::output.public_subnet_ids` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Internet egress/ingress можливий тільки з IP та SG |
| Security / replacement / deletion | Зміна target/table може перервати трафік; порядок host readiness не гарантований. |

### module.networking.aws_route_table.private

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_route_table` / `private` / `module.networking`; [код L53](../../infrastructure/terraform/modules/networking/main.tf#L53) |
| Purpose | Набір маршрутів public або private subnet |
| Depends on | `module.networking::aws_vpc.this`<br>`root::provider.aws` |
| Used by | `module.networking::aws_route_table_association.private`<br>`module.networking::aws_vpc_endpoint.s3` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Маршрути визначають reachability, не application authorization |
| Security / replacement / deletion | VPC change може замінити table; route change може розірвати connectivity. |

### module.networking.aws_route_table_association.public

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_route_table_association` / `public` / `module.networking`; [код L54](../../infrastructure/terraform/modules/networking/main.tf#L54) |
| Purpose | Привʼязка subnet до route table |
| Depends on | `module.networking::aws_route_table.public`<br>`module.networking::aws_subnet.public`<br>`root::provider.aws` |
| Used by | `module.networking::output.public_subnet_ids` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `2; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Public/private routing policy |
| Security / replacement / deletion | Reassociation може миттєво змінити доступність subnet. |

### module.networking.aws_route_table_association.private

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_route_table_association` / `private` / `module.networking`; [код L59](../../infrastructure/terraform/modules/networking/main.tf#L59) |
| Purpose | Привʼязка subnet до route table |
| Depends on | `module.networking::aws_route_table.private`<br>`module.networking::aws_subnet.private`<br>`root::provider.aws` |
| Used by | `module.networking::output.private_subnet_ids` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `2; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Public/private routing policy |
| Security / replacement / deletion | Reassociation може миттєво змінити доступність subnet. |

### module.networking.aws_vpc_endpoint.s3

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc_endpoint` / `s3` / `module.networking`; [код L65](../../infrastructure/terraform/modules/networking/main.tf#L65) |
| Purpose | S3 Gateway endpoint для двох route tables |
| Depends on | `module.networking::aws_route_table.private`<br>`module.networking::aws_route_table.public`<br>`module.networking::aws_vpc.this`<br>`module.networking::data.aws_region.current`<br>`root::provider.aws` |
| Used by | `module.networking::output.private_subnet_ids` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Gateway S3 без hourly, S3/transfer оплачуються окремо |
| Public / network | Приватний S3 route, не internet/NAT |
| Security / replacement / deletion | Policy default широка; не забезпечує ECR/SSM/CloudWatch/Open-Meteo. Тип/VPC зміни можуть вимагати replacement. |

### module.networking.aws_security_group.alb

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_security_group` / `alb` / `module.networking`; [код L85](../../infrastructure/terraform/modules/networking/main.tf#L85) |
| Purpose | Три SG для ALB/backend/RDS. |
| Depends on | `module.networking::aws_vpc.this`<br>`module.networking::var.name`<br>`root::provider.aws` |
| Used by | `module.networking::aws_vpc_security_group_egress_rule.targets`<br>`module.networking::aws_vpc_security_group_ingress_rule.cloudfront`<br>`module.networking::aws_vpc_security_group_ingress_rule.targets`<br>`module.networking::output.alb_sg` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Без окремої hourly |
| Public / network | Порти задають окремі SG-to-SG rules. |
| Security / replacement / deletion | Зміна VPC/name може замінити SG; жодного AI SG. |

### module.networking.aws_security_group.backend

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_security_group` / `backend` / `module.networking`; [код L90](../../infrastructure/terraform/modules/networking/main.tf#L90) |
| Purpose | Три SG для ALB/backend/RDS. |
| Depends on | `module.networking::aws_vpc.this`<br>`module.networking::var.name`<br>`root::provider.aws` |
| Used by | `module.networking::aws_vpc_security_group_egress_rule.database`<br>`module.networking::aws_vpc_security_group_egress_rule.https`<br>`module.networking::aws_vpc_security_group_egress_rule.targets`<br>`module.networking::aws_vpc_security_group_ingress_rule.database`<br>`module.networking::aws_vpc_security_group_ingress_rule.targets`<br>`module.networking::output.backend_sg` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Без окремої hourly |
| Public / network | Порти задають окремі SG-to-SG rules. |
| Security / replacement / deletion | Зміна VPC/name може замінити SG; жодного AI SG. |

### module.networking.aws_security_group.mysql

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_security_group` / `mysql` / `module.networking`; [код L95](../../infrastructure/terraform/modules/networking/main.tf#L95) |
| Purpose | Три SG для ALB/backend/RDS. |
| Depends on | `module.networking::aws_vpc.this`<br>`module.networking::var.name`<br>`root::provider.aws` |
| Used by | `module.networking::aws_vpc_security_group_egress_rule.database`<br>`module.networking::aws_vpc_security_group_ingress_rule.database`<br>`module.networking::output.mysql_sg` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Без окремої hourly |
| Public / network | Порти задають окремі SG-to-SG rules. |
| Security / replacement / deletion | Зміна VPC/name може замінити SG; жодного AI SG. |

### module.networking.aws_vpc_security_group_ingress_rule.cloudfront

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc_security_group_ingress_rule` / `cloudfront` / `module.networking`; [код L100](../../infrastructure/terraform/modules/networking/main.tf#L100) |
| Purpose | Окремий дозвіл вхідного TCP traffic |
| Depends on | `module.networking::aws_security_group.alb`<br>`module.networking::data.aws_ec2_managed_prefix_list.cloudfront`<br>`root::provider.aws` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Див. порти/джерела у NETWORK_GRAPH |
| Security / replacement / deletion | Не є auth/TLS; зміна source/port може відкрити або перервати доступ. |

### module.networking.aws_vpc_security_group_ingress_rule.targets

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc_security_group_ingress_rule` / `targets` / `module.networking`; [код L108](../../infrastructure/terraform/modules/networking/main.tf#L108) |
| Purpose | Окремий дозвіл вхідного TCP traffic |
| Depends on | `module.networking::aws_security_group.alb`<br>`module.networking::aws_security_group.backend`<br>`root::provider.aws` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Див. порти/джерела у NETWORK_GRAPH |
| Security / replacement / deletion | Не є auth/TLS; зміна source/port може відкрити або перервати доступ. |

### module.networking.aws_vpc_security_group_egress_rule.targets

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc_security_group_egress_rule` / `targets` / `module.networking`; [код L116](../../infrastructure/terraform/modules/networking/main.tf#L116) |
| Purpose | Окремий дозвіл вихідного TCP traffic |
| Depends on | `module.networking::aws_security_group.alb`<br>`module.networking::aws_security_group.backend`<br>`root::provider.aws` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | HTTPS backend 0.0.0.0/0 або SG/S3-only |
| Security / replacement / deletion | Звузити без тестів означає ризик зупинки API/agent; не domain allowlist. |

### module.networking.aws_vpc_security_group_ingress_rule.database

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc_security_group_ingress_rule` / `database` / `module.networking`; [код L124](../../infrastructure/terraform/modules/networking/main.tf#L124) |
| Purpose | Окремий дозвіл вхідного TCP traffic |
| Depends on | `module.networking::aws_security_group.backend`<br>`module.networking::aws_security_group.mysql`<br>`root::provider.aws` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | Див. порти/джерела у NETWORK_GRAPH |
| Security / replacement / deletion | Не є auth/TLS; зміна source/port може відкрити або перервати доступ. |

### module.networking.aws_vpc_security_group_egress_rule.database

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc_security_group_egress_rule` / `database` / `module.networking`; [код L132](../../infrastructure/terraform/modules/networking/main.tf#L132) |
| Purpose | Окремий дозвіл вихідного TCP traffic |
| Depends on | `module.networking::aws_security_group.backend`<br>`module.networking::aws_security_group.mysql`<br>`root::provider.aws` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | HTTPS backend 0.0.0.0/0 або SG/S3-only |
| Security / replacement / deletion | Звузити без тестів означає ризик зупинки API/agent; не domain allowlist. |

### module.networking.aws_vpc_security_group_egress_rule.https

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_vpc_security_group_egress_rule` / `https` / `module.networking`; [код L140](../../infrastructure/terraform/modules/networking/main.tf#L140) |
| Purpose | Окремий дозвіл вихідного TCP traffic |
| Depends on | `module.networking::aws_security_group.backend`<br>`root::provider.aws` |
| Used by | Немає явних споживачів/посилань. |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.vpc_cidr` |
| Creation / condition | `Без власного count/for_each; parent module: без count` |
| Cost | Немає окремої hourly |
| Public / network | HTTPS backend 0.0.0.0/0 або SG/S3-only |
| Security / replacement / deletion | Звузити без тестів означає ризик зупинки API/agent; не domain allowlist. |

## root


### root.aws_cloudwatch_log_group.backend

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_cloudwatch_log_group` / `backend` / `root`; [код L40](../../infrastructure/terraform/main.tf#L40) |
| Purpose | Backend logs із retention7днів |
| Depends on | `root::local.name`<br>`root::provider.aws` |
| Used by | `root::module.backend.input.log_group_arn`<br>`root::module.backend.input.log_group_name` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.environment`<br>`root::var.name_suffix` |
| Creation / condition | `Без власного count/for_each` |
| Cost | Так за ingestion/storage; порожній group не дорівнює$0.83 monitoring reserve |
| Public / network | AWS Logs API; не public logs |
| Security / replacement / deletion | Немає metric alarms/Budgets ресурсів; secret-safe logging лишається application відповідальністю. |

### root.aws_route53_record.origin

| Поле | Пояснення |
|---|---|
| Type / name / module | `aws_route53_record` / `origin` / `root`; [код L66](../../infrastructure/terraform/main.tf#L66) |
| Purpose | A alias origin hostname→ALB у вже існуючій hosted zone |
| Depends on | `module.alb::output.dns`<br>`module.alb::output.listener_rule_arn`<br>`module.alb::output.zone_id`<br>`root::provider.aws`<br>`root::var.deploy_application`<br>`root::var.origin_hostname`<br>`root::var.origin_zone_id` |
| Used by | `root::module.frontend.input.origin_hostname` |
| Root inputs, transitively | `root::var.aws_region`<br>`root::var.deploy_application`<br>`root::var.environment`<br>`root::var.name_suffix`<br>`root::var.origin_certificate_arn`<br>`root::var.origin_hostname`<br>`root::var.origin_verification_header`<br>`root::var.origin_zone_id`<br>`root::var.vpc_cidr` |
| Creation / condition | `var.deploy_application ? 1 : 0` |
| Cost | Окремої плати за record немає; zone/queries/account usage окремо |
| Public / network | Public DNS record, не сам web endpoint |
| Security / replacement / deletion | Countoff прибирає alias; зміна hostname/zone може замінити record, не реєструє домен/сертифікат. |
