> Актуальне уточнення 26.11.2026: реалізовано [варіант B](terraform/VARIANT_B_REPORT.md): 6 modules/15 root inputs, RDS-only, AI відкладено, HCP володіє ECS revisions. Старі gates та EC2 MySQL нижче — контекст попереднього етапу. Поточні inputs/runbook/графи наведено у звіті B. Наступний крок: review diff і окреме погодження публікації; потім дозволений remote validate/Plan, не автоматичний Apply.

# ClimateHealth — повторне використання власних Terraform-модулів

24.11.2026. Перевірено доступ до `D:/Робота/Codica/golfer2golfer/terraform/modules/`. Знайдено **28 каталогів**, не припускається наявність інших. Оригінали лише читалися, Git-команд у сторонньому проєкті не було. Інвентар охоплює активні resource/variable/output декларації, без закоментованих блоків; точні імена inputs/outputs і Terraform constraints — [JSON](reports/terraform-module-inventory.json).

| Модуль | AWS/інша роль | Рішення | Причина |
|---|---|---|---|
| alb | aws_alb_listener, aws_alb_target_group, aws_lb, aws_lb_listener, aws_lb_listener_rule, aws_s3_bucket, aws_s3_bucket_policy | Перепроєктовано | instance targets для bridge; HTTPS, matcher200, header403 gate, без випадкового IP redirect/force_destroy log bucket. |
| api_gateway | aws_apigatewayv2_api, aws_apigatewayv2_api_mapping, aws_apigatewayv2_domain_name, aws_apigatewayv2_integration, aws_apigatewayv2_route, aws_apigatewayv2_stage, aws_lambda_permission, aws_route53_record | Не потрібний | Не входить до обраного ECS/MySQL/CloudFront контуру; додаткові сервіси/інтеграції не копіювалися. |
| cdn | aws_cloudfront_distribution | Враховано як приклад | API behavior без кешу, default frontend; глобальний origin/cache ignore_changes не переносили. |
| cdn-imgproxy | aws_cloudfront_distribution | Не потрібний | Не входить до обраного ECS/MySQL/CloudFront контуру; додаткові сервіси/інтеграції не копіювалися. |
| cdn_s3 | aws_cloudfront_distribution | Перепроєктовано | OAC замість custom-origin S3; не приховує origin/cache drift, outputs додані. |
| cloudfront | aws_cloudfront_distribution | Враховано як приклад | Frontend/API origins з OAC та origin verification; старі WAF/domain assumptions не перенесені. |
| cognito | aws_cognito_user_pool, aws_cognito_user_pool_client, aws_cognito_user_pool_domain | Не потрібний | Не входить до обраного ECS/MySQL/CloudFront контуру; додаткові сервіси/інтеграції не копіювалися. |
| cw_alarms | aws_cloudwatch_metric_alarm, aws_sns_topic | Відкладено | Метрики/пороги після benchmark; log retention реалізовано, alarm обсяги закладено в бюджет. |
| ec2 | aws_instance, aws_key_pair, aws_security_group | Перепроєктовано | Немає SSH0/0/t2 default/AMI-ignore; IMDSv2/encryptedgp3/privateAI. |
| ecr | aws_ecr_lifecycle_policy, aws_ecr_repository, aws_kms_key | Адаптовано безпосередньо | Скопійовано repository block із main.tf і ecr_names variable block; IMMUTABLE, scan_on_push, AES256, локальна lifecycle policy; прибрано платний CMK та чужі policy files. |
| ecs | aws_autoscaling_group, aws_cloudwatch_log_group, aws_ecs_capacity_provider, aws_ecs_cluster, aws_ecs_cluster_capacity_providers, aws_ecs_service, aws_iam_instance_profile, aws_iam_role, aws_iam_role_policy_attachment, aws_launch_template, aws_security_group | Перепроєктовано | Окремий EC2 Capacity Provider/ASG і bridge networking; AL2023 pinned AMI замість EOL AL2, task definition/IAM створені в локальному модулі. |
| elasticache | aws_cloudwatch_log_group, aws_elasticache_cluster | Не потрібний | Не входить до обраного ECS/MySQL/CloudFront контуру; додаткові сервіси/інтеграції не копіювалися. |
| event_bridge | aws_cloudwatch_event_rule, aws_cloudwatch_event_target | Не потрібний | Не входить до обраного ECS/MySQL/CloudFront контуру; додаткові сервіси/інтеграції не копіювалися. |
| ga | aws_globalaccelerator_accelerator, aws_globalaccelerator_endpoint_group, aws_globalaccelerator_listener | Не потрібний | Не входить до обраного ECS/MySQL/CloudFront контуру; додаткові сервіси/інтеграції не копіювалися. |
| iam | aws_iam_instance_profile, aws_iam_policy, aws_iam_role, aws_iam_role_policy_attachment | Не копіювали | GitLab/сторонні ARN/policies не потрібні; окремі task/execution/host та HCP/GitHub identities. |
| iam_roles | aws_iam_instance_profile, aws_iam_policy, aws_iam_role, aws_iam_role_policy_attachment | Не копіювали | Динамічні ARN у for_each keys, використання лише першого custom policy; прості ролі описані явно. |
| imgproxy | aws_cloudfront_distribution, aws_cloudfront_origin_access_control, aws_cloudwatch_log_group, aws_iam_role, aws_iam_role_policy, aws_lambda_function, aws_lambda_function_url, aws_lambda_permission | Не потрібний | Не входить до обраного ECS/MySQL/CloudFront контуру; додаткові сервіси/інтеграції не копіювалися. |
| lambda | aws_iam_role, aws_iam_role_policy_attachment, aws_lambda_function | Не потрібний | Не входить до обраного ECS/MySQL/CloudFront контуру; додаткові сервіси/інтеграції не копіювалися. |
| pagerduty | pagerduty_service, pagerduty_service_event_rule, pagerduty_service_integration | Не потрібний | Не входить до обраного ECS/MySQL/CloudFront контуру; додаткові сервіси/інтеграції не копіювалися. |
| rds | aws_db_instance, aws_kms_key, random_password, random_string | Не копіювали | Модуль фактично PostgreSQL:5432, random password у state, до500GB autoscale; MySQL8.4 реалізовано заново. |
| s3 | aws_s3_bucket, aws_s3_bucket_cors_configuration, aws_s3_bucket_ownership_controls, aws_s3_bucket_policy, aws_s3_bucket_public_access_block, aws_s3_bucket_versioning | Перепроєктовано | Private REST origin, OAC, BPA/encryption/versioning; без website endpoint та ignore_changes захисту. |
| security_groups | aws_security_group, aws_security_group_rule | Перепроєктовано | SG-reference matrix замість широких CIDR, немає Redis/bastion. |
| service_discovery | aws_service_discovery_private_dns_namespace, aws_service_discovery_service | Відкладено | Private AI AMI contract; Cloud Map/AI capacity provider лише альтернатива з окремим IAM/network plan. |
| slack | slack_conversation | Не потрібний | Не входить до обраного ECS/MySQL/CloudFront контуру; додаткові сервіси/інтеграції не копіювалися. |
| sns | aws_kms_key, aws_sns_topic | Не потрібний | Не входить до обраного ECS/MySQL/CloudFront контуру; додаткові сервіси/інтеграції не копіювалися. |
| vpc | aws_db_subnet_group, aws_eip, aws_elasticache_subnet_group, aws_instance, aws_internet_gateway, aws_nat_gateway, aws_route_table, aws_route_table_association, aws_security_group, aws_subnet, aws_vpc | Перепроєктовано | Збережено ідею public/private; прибрано дубльовані маршрути, unconditional EIP, ElastiCache і hardcoded key/AZ; no-NAT root. |
| waf | aws_cloudwatch_log_group, aws_wafv2_ip_set, aws_wafv2_web_acl, aws_wafv2_web_acl_logging_configuration | Не потрібний | Не входить до обраного ECS/MySQL/CloudFront контуру; додаткові сервіси/інтеграції не копіювалися. |
| ws | aws_cloudwatch_log_group, aws_ecs_cluster, aws_ecs_cluster_capacity_providers, aws_ecs_service, aws_kms_key | Не потрібний | Не входить до обраного ECS/MySQL/CloudFront контуру; додаткові сервіси/інтеграції не копіювалися. |

## Сумісність і залежності
Частина модулів декларує Terraform >=1.3.2 та AWS >=4.36.0; інші не мають власних provider constraints. Це не доводить сумісність із AWS6.74.0: є застарілі AMI/attributes/lifecycle і локальні file() dependencies. Новий root pin =6.74.0, child modules >=6.74,<7, Terraform >=1.11,<2. Provider/schema validation не виконувалася через заборону Terraform. Рідний AL2 ECS AMI після 30.06.2026 EOL: [AWS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/al2-to-al2023-ami-transition.html).

Виявлено ризики: ALB health matcher200-499, дубльовані VPC default routes, unconditional EIP, broad NAT ingress/egress, SSH0/0 default у EC2, ignore_changes AMI/origin/cache/security controls, mutable ECR і вимкнений scan, приватний RDS з неправильною для нас СУБД, пароль RDS у state. Це статичні знахідки, не твердження про фактичні ресурси чи їх експлуатацію.

Новий root самодостатній: лише `./modules/...`, усі потрібні файли всередині ClimateHealth-Monitoring. Прямо адаптований тільки ECR; інші модулі — нові спрощені реалізації з урахуванням прочитаних патернів. «Використано без змін» — жодного повного модуля. Не копіювали policies стороннього проєкту, секрети, tfstate, ключі, tfvars, Git-конфігурації або встановлені provider binaries. `file()` на абсолютні Windows-шляхи немає.

Точні вихідні SHA256 ECR main.tf/vars.tf включено до локального audit manifest; це внутрішня технічна provenance, не runtime dependency. Підсумкова перевірка оригіналів виконується за SHA256 усіх прочитаних .tf файлів. Сумісність із Terraform/AWS schema та Linux boot є неперевіреною, а не успішною за припущенням.
