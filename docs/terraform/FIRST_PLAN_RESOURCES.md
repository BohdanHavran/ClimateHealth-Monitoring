# Очікувані ресурси першого HCP Plan

26.11.2026. Це статичне розгортання відомих default count/for_each, **не результат Plan**. Для актуального порожнього State, deploy_application=false, backend_desired_count=0 очікується **45 to add,0 to change,0 to destroy**. Якщо State змінився, ця кількість не є автоматичним критерієм прийняття — зупинити review й дослідити розбіжність.

| Scope | Instances |
|---|---:|
| module.networking |23|
| module.ecr |2|
| module.frontend |16|
| module.database |3|
| root log group |1|
| Разом |45|

У таблиці `<local.name>` — шаблон climatehealth-${environment}-${name_suffix}, а не значення для HCP. Scope module.database викликає каталог modules/mysql. Дві public subnet не означають наявність public EC2 чи ALB. Наявні ALB/backend SG — без прикріпленого compute.

| Terraform resource address | Витрати | Public/private | Джерело |
|---|---|---|---|
| `aws_cloudwatch_log_group.backend` | За ingestion/storage; порожня group без usage | Конфігурація/не endpoint | [source L40](../../infrastructure/terraform/main.tf#L40) |
| `module.ecr.aws_ecr_repository.ecr["<local.name>-backend"]` | За image storage/transfer; порожній repo без storage charge | Конфігурація/не endpoint | [source L2](../../infrastructure/terraform/modules/ecr/main.tf#L2) |
| `module.ecr.aws_ecr_lifecycle_policy.images["<local.name>-backend"]` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L19](../../infrastructure/terraform/modules/ecr/main.tf#L19) |
| `module.frontend.aws_s3_bucket.frontend` | За фактичним storage/requests/versions | Private; BPA, TLS deny, frontend read тільки OAC | [source L13](../../infrastructure/terraform/modules/frontend/main.tf#L13) |
| `module.frontend.aws_s3_bucket.artifacts` | За фактичним storage/requests/versions | Private; BPA, TLS deny, frontend read тільки OAC | [source L17](../../infrastructure/terraform/modules/frontend/main.tf#L17) |
| `module.frontend.aws_s3_bucket_public_access_block.this["frontend"]` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L22](../../infrastructure/terraform/modules/frontend/main.tf#L22) |
| `module.frontend.aws_s3_bucket_public_access_block.this["artifacts"]` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L22](../../infrastructure/terraform/modules/frontend/main.tf#L22) |
| `module.frontend.aws_s3_bucket_versioning.this["frontend"]` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L30](../../infrastructure/terraform/modules/frontend/main.tf#L30) |
| `module.frontend.aws_s3_bucket_versioning.this["artifacts"]` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L30](../../infrastructure/terraform/modules/frontend/main.tf#L30) |
| `module.frontend.aws_s3_bucket_server_side_encryption_configuration.this["frontend"]` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L35](../../infrastructure/terraform/modules/frontend/main.tf#L35) |
| `module.frontend.aws_s3_bucket_server_side_encryption_configuration.this["artifacts"]` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L35](../../infrastructure/terraform/modules/frontend/main.tf#L35) |
| `module.frontend.aws_s3_bucket_ownership_controls.this["frontend"]` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L42](../../infrastructure/terraform/modules/frontend/main.tf#L42) |
| `module.frontend.aws_s3_bucket_ownership_controls.this["artifacts"]` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L42](../../infrastructure/terraform/modules/frontend/main.tf#L42) |
| `module.frontend.aws_cloudfront_origin_access_control.this` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L47](../../infrastructure/terraform/modules/frontend/main.tf#L47) |
| `module.frontend.aws_cloudfront_cache_policy.assets` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L62](../../infrastructure/terraform/modules/frontend/main.tf#L62) |
| `module.frontend.aws_cloudfront_function.routes` | За invocation; до початку трафіку немає usage | Конфігурація/не endpoint | [source L76](../../infrastructure/terraform/modules/frontend/main.tf#L76) |
| `module.frontend.aws_cloudfront_distribution.this` | За traffic/requests; PAYG, allowances не гарантовано | Public HTTPS CDN, лише S3 origin на першому етапі | [source L89](../../infrastructure/terraform/modules/frontend/main.tf#L89) |
| `module.frontend.aws_s3_bucket_policy.frontend` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L155](../../infrastructure/terraform/modules/frontend/main.tf#L155) |
| `module.frontend.aws_s3_bucket_policy.artifacts` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L164](../../infrastructure/terraform/modules/frontend/main.tf#L164) |
| `module.database.aws_db_subnet_group.this` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L13](../../infrastructure/terraform/modules/mysql/main.tf#L13) |
| `module.database.aws_db_parameter_group.this` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L16](../../infrastructure/terraform/modules/mysql/main.tf#L16) |
| `module.database.aws_db_instance.this` | Так: compute +20GBgp3 +managed master secret, backup/CPUcredits за умовами | Private,3306 лише backendSG,TLS | [source L23](../../infrastructure/terraform/modules/mysql/main.tf#L23) |
| `module.networking.aws_vpc.this` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L10](../../infrastructure/terraform/modules/networking/main.tf#L10) |
| `module.networking.aws_internet_gateway.this` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L19](../../infrastructure/terraform/modules/networking/main.tf#L19) |
| `module.networking.aws_subnet.public[0]` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L25](../../infrastructure/terraform/modules/networking/main.tf#L25) |
| `module.networking.aws_subnet.public[1]` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L25](../../infrastructure/terraform/modules/networking/main.tf#L25) |
| `module.networking.aws_subnet.private[0]` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L36](../../infrastructure/terraform/modules/networking/main.tf#L36) |
| `module.networking.aws_subnet.private[1]` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L36](../../infrastructure/terraform/modules/networking/main.tf#L36) |
| `module.networking.aws_route_table.public` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L47](../../infrastructure/terraform/modules/networking/main.tf#L47) |
| `module.networking.aws_route.internet` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L48](../../infrastructure/terraform/modules/networking/main.tf#L48) |
| `module.networking.aws_route_table.private` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L53](../../infrastructure/terraform/modules/networking/main.tf#L53) |
| `module.networking.aws_route_table_association.public[0]` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L54](../../infrastructure/terraform/modules/networking/main.tf#L54) |
| `module.networking.aws_route_table_association.public[1]` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L54](../../infrastructure/terraform/modules/networking/main.tf#L54) |
| `module.networking.aws_route_table_association.private[0]` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L59](../../infrastructure/terraform/modules/networking/main.tf#L59) |
| `module.networking.aws_route_table_association.private[1]` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L59](../../infrastructure/terraform/modules/networking/main.tf#L59) |
| `module.networking.aws_vpc_endpoint.s3` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L65](../../infrastructure/terraform/modules/networking/main.tf#L65) |
| `module.networking.aws_security_group.alb` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L85](../../infrastructure/terraform/modules/networking/main.tf#L85) |
| `module.networking.aws_security_group.backend` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L90](../../infrastructure/terraform/modules/networking/main.tf#L90) |
| `module.networking.aws_security_group.mysql` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L95](../../infrastructure/terraform/modules/networking/main.tf#L95) |
| `module.networking.aws_vpc_security_group_ingress_rule.cloudfront` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L100](../../infrastructure/terraform/modules/networking/main.tf#L100) |
| `module.networking.aws_vpc_security_group_ingress_rule.targets` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L108](../../infrastructure/terraform/modules/networking/main.tf#L108) |
| `module.networking.aws_vpc_security_group_egress_rule.targets` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L116](../../infrastructure/terraform/modules/networking/main.tf#L116) |
| `module.networking.aws_vpc_security_group_ingress_rule.database` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L124](../../infrastructure/terraform/modules/networking/main.tf#L124) |
| `module.networking.aws_vpc_security_group_egress_rule.database` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L132](../../infrastructure/terraform/modules/networking/main.tf#L132) |
| `module.networking.aws_vpc_security_group_egress_rule.https` | Ні, окремої hourly немає | Конфігурація/не endpoint | [source L140](../../infrastructure/terraform/modules/networking/main.tf#L140) |

## Що не повинно створюватися

Жодних module.backend[0]/module.alb[0], ECScluster/service/taskdefinition/CP, ASG/LT/EC2/EBS hosts, IAMroles/profile/policies ECS, Route53 origin record, APICloudFront origin, AI, EC2MySQL, NATGateway/NATInstance, interface endpoints, Bastion, Kubernetes, S3TerraformState, ACM/domain/hostedzone. S3 Gateway endpoint є погодженою частиною мережі, не NAT.

П’ять активних AWS data sources читають calleridentity, availabilityzones, region, CloudFront prefixlist і Managed-CachingDisabled. Data aws_cloudfront_origin_request_policy.api має count0. Читання data source — не create ресурс.

RDS створює AWS-managed master secret як побічний керований об’єкт; окремого Terraform aws_secretsmanager_secret block немає, але storage/API secret платні. Подібно default VPC objects AWS не слід рахувати як додаткові керовані HCL addresses.

RDSengine8.4.13, клас/dbfamily/AZ availability треба підтвердити; Plan не гарантує успішний AWS CreateDBInstance. [Поточні inputs, checklist і кошторис](FIRST_HCP_PLAN.md).
