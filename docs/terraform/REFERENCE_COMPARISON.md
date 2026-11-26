# Порівняння референсних модулів і ClimateHealth

26.11.2026. Поточний код: commit09f2d790 f5668 a40 d17 d2 ae5960 ca9 e20 ffc1 d3 c, root `infrastructure/terraform`. Референс: `D:/Робота/Codica/golfer2golfer/terraform/modules`, виключно читання. Усі 96 `.tf` файлів 28 модулів прочитано локальним лексичним аналізатором; відповідні main/vars/outputs/data та README перечитано для порівняння. Код референсу не запускався. Криптографічні snapshot hashes збережено локально для перевірки незмінності; жодних reference Git operations.

Також прочитано common_infra/main.tf, production/main.tf, production/provider.tf, відповідні module inputs/outputs, IAM task policy template та nat_userdata.sh. Батьківські виклики підтверджують common VPC/NAT instance і production ECS use_fargate=true; отже сам факт наявності EC2-гілки не доводить, що саме її перевірено експлуатацією. Чинність конфігурації reference на Provider6.74.0 не перевірена.

## Висновок щодо походження

Попередній документ TERRAFORM_MODULE_REUSE.md прямо вказує: безпосередньо адаптовано лише ECR; жоден повний модуль не використано без змін. Source-to-target зіставлення нижче це підтверджує. Для VPC/ECS/ALB можна було зберегти більше структури й contracts референсу, але це вимагало б цільової адаптації. Називати створені модулі «повторним використанням готових модулів» без цього уточнення некоректно.

REUSE означає майже незмінний придатний модуль; ADAPT — копія з конкретними змінами; KEEP CURRENT — поточне рішення краще; REWRITE — жодна реалізація не придатна в потрібному вигляді; REMOVE — сервіс поза цільовим контуром. Це рекомендації, не внесені зміни.

## Інвентар обох каталогів

Current:8 модулів,22 TF файли разом із root,70 resource declarations (69 AWS + terraform_data),93 variables (33 root +60 child),48 outputs,8 data sources. Declaration — текстовий блок, не число створених AWS instances. Для увімкненого RDS demo/AIoff ручне розгортання count/for_each дає 71 AWS instances +1 builtin; реальний Plan може відрізнятися.

| Референсний каталог | TF файлів | Resource blocks | Variables | Outputs | Рішення |
|---|---:|---:|---:|---:|---|
| `alb` | 4 | 8 | 6 | 3 | ADAPT |
| `api_gateway` | 3 | 8 | 6 | 0 | REMOVE з цільової архітектури |
| `cdn` | 4 | 1 | 5 | 0 | REMOVE як окремий CDN |
| `cdn-imgproxy` | 4 | 1 | 2 | 0 | REMOVE з цільової архітектури |
| `cdn_s3` | 3 | 1 | 4 | 0 | KEEP CURRENT |
| `cloudfront` | 3 | 1 | 5 | 0 | KEEP CURRENT |
| `cognito` | 4 | 3 | 3 | 3 | REMOVE з цільової архітектури |
| `cw_alarms` | 3 | 3 | 1 | 3 | ADAPT після runtime benchmark |
| `ec2` | 3 | 3 | 14 | 0 | ADAPT для майбутнього AI |
| `ecr` | 3 | 3 | 3 | 1 | ADAPT / KEEP CURRENT |
| `ecs` | 4 | 13 | 13 | 1 | ADAPT |
| `elasticache` | 4 | 2 | 7 | 1 | REMOVE з цільової архітектури |
| `event_bridge` | 3 | 2 | 1 | 0 | REMOVE з цільової архітектури |
| `ga` | 3 | 4 | 3 | 0 | REMOVE з цільової архітектури |
| `iam` | 4 | 18 | 6 | 5 | REMOVE generic runner stack |
| `iam_roles` | 3 | 4 | 1 | 3 | REWRITE лише за окремої потреби |
| `imgproxy` | 4 | 8 | 9 | 0 | REMOVE з цільової архітектури |
| `lambda` | 4 | 3 | 7 | 2 | REMOVE з цільової архітектури |
| `pagerduty` | 3 | 3 | 4 | 5 | REMOVE з цільової архітектури |
| `rds` | 4 | 4 | 3 | 5 | KEEP CURRENT, RDS-only |
| `s3` | 4 | 6 | 5 | 1 | ADAPT |
| `security_groups` | 3 | 8 | 12 | 5 | KEEP CURRENT |
| `service_discovery` | 3 | 2 | 3 | 1 | REMOVE зараз; повернути при потребі |
| `slack` | 3 | 1 | 1 | 1 | REMOVE з цільової архітектури |
| `sns` | 3 | 4 | 4 | 3 | REMOVE з цільової архітектури |
| `vpc` | 4 | 22 | 11 | 11 | ADAPT |
| `waf` | 3 | 4 | 9 | 1 | REMOVE з цільової архітектури |
| `ws` | 3 | 5 | 14 | 0 | REMOVE з цільової архітектури |

## VPC, subnets та routing: ADAPT

Джерело: [modules/vpc/main.tf:5](<D:/Робота/Codica/golfer2golfer/terraform/modules/vpc/main.tf:5>). Поточний код: [infrastructure/terraform/modules/networking/main.tf:18](../../infrastructure/terraform/modules/networking/main.tf#L18).

Reference: VPC,6 subnets/3 AZ, IGW, NAT alternatives, EIP, DB та ElastiCache subnet groups. Current:2 public+2 private/2 AZ, IGW, дві route tables і S3 Gateway endpoint, без NAT.

**Inputs/outputs та залежності.** Reference11 inputs/11 outputs: project/vpc_name/DNS/NAT settings; окремі subnet outputs. Current4 inputs/4 outputs: name та CIDRs, subnet lists і AZ; region/AZ data sources. Залишити list outputs, CIDR input і явне маршрутизування.

**Security/lifecycle/адаптація.** Адаптувати VPC/subnet/IGW/association основу: прибрати Redis subnet group, дубльовані default routes (reference185–212), зробити EIP умовним (15–17), прибрати NAT як default. nat output29 зараз індексує instance навіть для неіснуючого no-NAT режиму. Не копіювати hardcoded ключ 28, ignore_changes35 або автоматичні 3 AZ. Current route readiness outputs64–70 виправдані; CIDR overlap/containment validation ще відсутня.

## Security Groups: KEEP CURRENT

Джерело: [modules/security_groups/main.tf:12](<D:/Робота/Codica/golfer2golfer/terraform/modules/security_groups/main.tf:12>). Поточний код: [infrastructure/terraform/modules/security/main.tf:24](../../infrastructure/terraform/modules/security/main.tf#L24).

Reference8 resource blocks: PostgreSQL5432, Redis6379, ECS/ALB CIDR rules та optional bastion. Current4 SG й окремі ingress/egress rules, MySQL3306 та AI8001.

**Inputs/outputs та залежності.** Reference12 inputs/5 outputs, count/list rules; current2 inputs/4 outputs. Не потрібно API для Redis/bastion або широкі CIDRs. Списки з count менш стабільні при перестановці, ніж named SG rules.

**Security/lifecycle/адаптація.** Зберегти SG→SG правила current. Перенести їх до networking або залишити security окремо, якщо це полегшує читання; саме зменшення числа каталогів не є метою. AI-specific правила можна створювати разом із AI. HTTPS egress0/0 потрібний для Open-Meteo; це не привід дозволяти inbound0/0. Reference hardcoded DB5432/VPC CIDR не переносити.

## ECS EC2 / Capacity Provider: ADAPT

Джерело: [modules/ecs/main.tf:173](<D:/Робота/Codica/golfer2golfer/terraform/modules/ecs/main.tf:173>). Поточний код: [infrastructure/terraform/modules/ecs-backend/main.tf:117](../../infrastructure/terraform/modules/ecs-backend/main.tf#L117).

В обох є cluster, log group, LT, ASG, CP та service. Reference також підтримує Fargate, service discovery і кілька сервісів; current додає task definition та scoped execution policy.

**Inputs/outputs та залежності.** Reference13 inputs/1 output, ECS service list(object), багато map(any); current21 inputs/7 outputs. Варто зберегти reference структуру cluster/LT/ASG/CP, а не всі можливості універсального модуля.

**Security/lifecycle/адаптація.** Видалити reference terraform_remote_state S3 (data.tf2–9), AL2 SSM path(main.tf221), Fargate/Spot/discovery branches та network_configuration для bridge. Привести ALB target_type до instance. Не включати execute-command без потреби. У current зменшити gates, зберегти IMDSv2/encryptedgp3/logging/readiness. AWS AL2 EOL30.06.2026 підтверджено офіційною документацією; автоматичний latest AMI потребує controlled refresh.

## EC2 / AI host: ADAPT

Джерело: [modules/ec2/main.tf:2](<D:/Робота/Codica/golfer2golfer/terraform/modules/ec2/main.tf:2>). Поточний код: [infrastructure/terraform/modules/ai/main.tf:43](../../infrastructure/terraform/modules/ai/main.tf#L43).

Reference generic EC2 + optional SSH key + optional SG. Current private EC2/IAM/S3-read profile + power state, encrypted20 GB, prevent_destroy.

**Inputs/outputs та залежності.** Reference14 inputs/0 outputs та власний provider requirement; current10 inputs/1 output. Придатна саме EC2 основа після видалення зайвих SSH/SG defaults; окремий AI module поки є заготовкою.

**Security/lifecycle/адаптація.** Reference AMI/tag/userdata drift ігнорується (main.tf21–23), encrypted/IMDSv2 не задано, default SSH22 з 0/0 (variables.tf79–85), Owner обовʼязковий у map. Це не переносити. Current AI DNS/TLS/token/agent не доставляються; додаткові runtime gates не замінюють реалізацію. AIoff залишити без host; power state має сенс лише після підтвердженої потреби створеного EC2.

## ECR: ADAPT / KEEP CURRENT

Джерело: [modules/ecr/main.tf:23](<D:/Робота/Codica/golfer2golfer/terraform/modules/ecr/main.tf:23>). Поточний код: [infrastructure/terraform/modules/ecr/main.tf:2](../../infrastructure/terraform/modules/ecr/main.tf#L2).

Reference KMS key, repositories і lifecycle policy files; current repositories+lifecycle, AES256, immutable tags, scan-on-push.

**Inputs/outputs та залежності.** Reference3 inputs/1 output; current2 inputs/2 outputs з maps за repository name. for_each repo names збережено; це найочевидніший безпосередній reuse.

**Security/lifecycle/адаптація.** Зберегти current encryption/immutability/scanning та named outputs. Не копіювати MUTABLE/scanfalse і зайвий CMK з reference9–41. Current policy очищає лише untagged images, тому tagged SHA revisions ростимуть; потрібний окремий погоджений retention без видалення rollback digests. AI repository відкласти разом із AI, якщо зручніше.

## ALB / targets / HTTPS: ADAPT

Джерело: [modules/alb/main.tf:9](<D:/Робота/Codica/golfer2golfer/terraform/modules/alb/main.tf:9>). Поточний код: [infrastructure/terraform/modules/alb/main.tf:20](../../infrastructure/terraform/modules/alb/main.tf#L20).

Reference8 blocks включає HTTPredirect/IP exception/log S3,3 subnets та ip targets. Current4 blocks:ALB, instance target group, HTTPSlistener, origin-header rule.

**Inputs/outputs та залежності.** Reference6 inputs/3 outputs (target groups list + load_balancer map); current6 inputs/5 outputs. Current name input не використовується. listener_arn фактично містить listener RULE ARN, а не listener ARN.

**Security/lifecycle/адаптація.** Можна адаптувати reference базові ALB/TG/listener blocks; лишити 2 subnets, instance targets, health ready/matcher200, deregistration30, default403. Не переносити matcher200-499(vars.tf25), IP-specific redirect(main.tf158–177), force_destroy logs181. Поточний header validation виправити до API exposure; деталі finding1. Access logs — опційне operational рішення, не обовʼязково окремий модуль.

## Приватні S3 buckets: ADAPT

Джерело: [modules/s3/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/s3/main.tf:1>). Поточний код: [infrastructure/terraform/modules/frontend/main.tf:14](../../infrastructure/terraform/modules/frontend/main.tf#L14).

Reference універсальний S3 з optional policy/CORS, versioning/ownership. Current2 buckets (frontend/artifacts) і по 2 security/versioning/encryption/ownership ресурси, policies.

**Inputs/outputs та залежності.** Reference5 inputs/1 output; current frontend6 inputs/5 outputs охоплює і CDN. Придатний reference bucket/BPA/versioning contract після звуження; generic CORS не потрібний same-origin frontend.

**Security/lifecycle/адаптація.** Зберегти BucketOwnerEnforced, усі 4 BPA=true, explicit encryption, TLS deny, versioning. Прибрати reference ignore_changes для BPA/ownership(main.tf14–16,83–85). OAC policy привʼязати до конкретної distribution. Не копіювати production bucket-public-access settings із референсу. Artifact storage не повинен змушувати RDS залежати від API origin.

## CloudFront: KEEP CURRENT

Джерело: [modules/cdn_s3/main.tf:5](<D:/Робота/Codica/golfer2golfer/terraform/modules/cdn_s3/main.tf:5>). Поточний код: [infrastructure/terraform/modules/frontend/main.tf:92](../../infrastructure/terraform/modules/frontend/main.tf#L92).

Reference cdn/cdn_s3/cloudfront — три різні single-distribution variants, без S3 OAC. Current одна distribution з private S3 OAC, SPA function, assets cache і optional API origin.

**Inputs/outputs та залежності.** Reference CDN variants мають 4–5 inputs і 0 outputs; current frontend6 inputs/5 outputs. Не потрібні дві незалежні distributions для S3 та API.

**Security/lifecycle/адаптація.** Current OAC та exact source ARN краще відповідають вимозі private S3. Reference cdn_s3 custom origin не підписує S3 requests, а ignore_changes(origin/cache) приховує drift. Reference cloudfront дозволяє тільки GET/HEAD/OPTIONS, тому HRI POST не працював би; direct reuse непридатний. Custom viewer ACM/aliases не додавати до першої демонстрації без потреби.

## RDS MySQL: KEEP CURRENT, прибрати EC2 альтернативу після state check

Джерело: [modules/rds/main.tf:22](<D:/Робота/Codica/golfer2golfer/terraform/modules/rds/main.tf:22>). Поточний код: [infrastructure/terraform/modules/mysql/main.tf:26](../../infrastructure/terraform/modules/mysql/main.tf#L26).

Reference — явно PostgreSQL5432 + random username/password +CMK. Current RDS MySQL8.4, require_secure_transport, managed master secret, SingleAZ/private20 GB; також speculative EC2 alternative.

**Inputs/outputs та залежності.** Reference3 inputs/5 outputs (у тому числі password); current9 inputs/1 output,4 inputs потрібні лише EC2/backup branch. Engine change не є безпечною copy/paste адаптацією production DB.

**Security/lifecycle/адаптація.** Зберегти current RDS path, приватність/TLS/backup/deletion protection. Не переносити PostgreSQL log exports/ports/engine/500 GB ceiling чи plaintext password у state. Reference map default misspells backap_retention_period(vars.tf13) при читанні backup_retention_period(main.tf48). Current engine8.4.13 availability та service-linked roles потребують реального Plan/API перевірки, не припущення.

## IAM: KEEP CURRENT для вузьких ролей; REMOVE generic runner stack

Джерело: [modules/iam/main.tf:9](<D:/Робота/Codica/golfer2golfer/terraform/modules/iam/main.tf:9>). Поточний код: [infrastructure/terraform/modules/ecs-backend/main.tf:68](../../infrastructure/terraform/modules/ecs-backend/main.tf#L68).

Reference iam створює 18 blocks для app/GitLab runners/flow logs/execution; iam_roles — generic4 blocks. Current host/execution/task roles, optionalAI S3 role та EC2 DB backup role.

**Inputs/outputs та залежності.** iam6 inputs/5 outputs, iam_roles1 roles object/3 outputs; current roles локальні до workload, permissions boundary із root. Host/execution не обʼєднувати; порожній app task role можна відкласти, доки Flask не викликає AWS API.

**Security/lifecycle/адаптація.** Reference fixed role names конфліктують між workspaces, рольові політики надто широкі для ClimateHealth. iam_roles flatten генерує однаковий custom policy ARN для кожного p, а policy resource використовує лише[0]; два custom policies можуть дати duplicate for_each keys і решта policy ігнорується. Ключі for_each містять computedARN, що може бути невідомим у першому Plan. Generic factory тут зайва; не переносити runner/flow-log roles або чужі policy files.

## Private service discovery / AI DNS: REMOVE зараз, ADAPT після погодження DNS

Джерело: [modules/service_discovery/main.tf:9](<D:/Робота/Codica/golfer2golfer/terraform/modules/service_discovery/main.tf:9>). Поточний код: [infrastructure/terraform/modules/ai/main.tf:69](../../infrastructure/terraform/modules/ai/main.tf#L69).

Reference приватний DNS namespace та service(A+SRV). Current лише private_ip output; автоматичного DNS record чи CloudMap registration немає.

**Inputs/outputs та залежності.** Reference3 inputs/1 output; current ML endpoint задається вручну якпогоджений HTTPS DNS, це не використання private_ip output.

**Security/lifecycle/адаптація.** Не додавати CloudMap лише для одного майбутнього AI host. Перед AI узгодити простий private Route53 record або справді потрібний discovery; перевірити cert SAN і token delivery. SG8001 не є доказом runtime.

## Monitoring / autoscaling: ADAPT лише за виміряною потребою

Джерело: [modules/cw_alarms/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cw_alarms/main.tf:1>). Поточний код: [infrastructure/terraform/modules/ecs-backend/main.tf:101](../../infrastructure/terraform/modules/ecs-backend/main.tf#L101).

Reference cw_alarms/SNS configurable alarms; current7 day log group, CP managed scaling, без custom alarm/Budget resources.

**Inputs/outputs та залежності.** Reference cw_alarms1 input/3 outputs. ECS-managed policies/alarms — можливі service side effects, не окремі HCL blocks. ASG/CP не потребують копіювання всього monitoring stack.

**Security/lifecycle/адаптація.** Потрібні фінансові alerts і базові failure signals, але не копіювати SNS/PagerDuty/Slack dependencies автоматично. Спершу виміряти memory/latency/credits. Budgets — окрема погоджена операція, не реалізована цим аудитом.

## Providers, tags та naming

Reference ec2/provider.tf: Core>=1.3.2, AWS>=4.36; production/provider.tf: Core>=1.0, AWS>=4.61 та S3 backend; більшість child modules не мають власних constraints. Це не доказ сумісності з AWS6.74. Current root точно pin6.74.0/Core>=1.11<2, child8 requirements>=6.74<7. Root provider успадковується без credentials/alias. State лишається HCP, без нового cloud/S3 backend. Додавати reference backend або remote_state не можна.

Reference має повторені common_tags/Service/Owner/фіксовані role names; current provider tags Project/Environment/ManagedBy та namespaced local.name. Ручні owner/account variables не повертати. current LT/ASG tags потрібні, оскільки created EC2/EBS не успадковують Terraform provider tags так само, як прямі Terraform resources. Naming/tagging — не підстава переписувати всю мережу.

## Точні джерела inventory та contracts

Нижче для кожного модуля перелічено реально прочитані TF-файли, усі активні resource/data addresses та всі input/output names. Закоментовані блоки не враховано. Values секретів/чужі AWS IDs не переносяться. Для невідповідних сервісів REMOVE означає не додавати їх у ClimateHealth, а не видаляти щось у референсі.

### Reference `alb`

Файли: [modules/alb/data.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/alb/data.tf:1>), [modules/alb/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/alb/main.tf:1>), [modules/alb/out.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/alb/out.tf:1>), [modules/alb/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/alb/vars.tf:1>).

resources: `aws_alb_target_group.ecs`, `aws_lb.application`, `aws_alb_listener.https`, `aws_lb_listener_rule.ecs`, `aws_lb_listener.http`, `aws_lb_listener_rule.one_ip_to_http`, `aws_s3_bucket.alb_logs`, `aws_s3_bucket_policy.this`.

data: `aws_iam_policy_document.s3_bucket_lb_write`, `aws_elb_service_account.main`.

variables: `vpc_id`, `target_groups_config`, `load_balancer`, `alb_certificate_arn`, `project`, `s3_bucket_name`.

outputs: `tg_arns`, `alb_domain`, `alb_id`.

README: README.md.

### Reference `api_gateway`

Файли: [modules/api_gateway/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/api_gateway/main.tf:1>), [modules/api_gateway/provider.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/api_gateway/provider.tf:1>), [modules/api_gateway/variables.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/api_gateway/variables.tf:1>).

resources: `aws_apigatewayv2_api.this`, `aws_apigatewayv2_stage.this`, `aws_apigatewayv2_integration.this`, `aws_apigatewayv2_route.this`, `aws_lambda_permission.this`, `aws_apigatewayv2_domain_name.this`, `aws_apigatewayv2_api_mapping.this`, `aws_route53_record.this`.

data: `aws_route53_zone.this`.

variables: `apigateway_name`, `stage_name`, `description`, `protocol_type`, `Custom_domain`, `integrations`.

outputs: немає.

README: немає.

### Reference `cdn`

Файли: [modules/cdn/data.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cdn/data.tf:1>), [modules/cdn/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cdn/main.tf:1>), [modules/cdn/out.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cdn/out.tf>), [modules/cdn/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cdn/vars.tf:1>).

resources: `aws_cloudfront_distribution.this`.

data: `aws_cloudfront_cache_policy.optimized`, `aws_cloudfront_cache_policy.disabled`.

variables: `alb_domain`, `aliases`, `path_pattern`, `default_cache_behavior`, `ordered_cache_behavior`.

outputs: немає.

README: README.md.

### Reference `cdn-imgproxy`

Файли: [modules/cdn-imgproxy/data.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cdn-imgproxy/data.tf:1>), [modules/cdn-imgproxy/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cdn-imgproxy/main.tf:1>), [modules/cdn-imgproxy/outputs.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cdn-imgproxy/outputs.tf>), [modules/cdn-imgproxy/variables.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cdn-imgproxy/variables.tf:1>).

resources: `aws_cloudfront_distribution.cdn`.

data: `aws_acm_certificate.for_cdn`, `aws_lb.lb_dns`, `aws_cloudfront_cache_policy.alb_policy`.

variables: `img_proxy_fqdn`, `img_proxy_dns`.

outputs: немає.

README: README.md.

### Reference `cdn_s3`

Файли: [modules/cdn_s3/data.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cdn_s3/data.tf:1>), [modules/cdn_s3/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cdn_s3/main.tf:1>), [modules/cdn_s3/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cdn_s3/vars.tf:1>).

resources: `aws_cloudfront_distribution.this`.

data: `aws_cloudfront_cache_policy.optimized`.

variables: `s3_origin`, `aliases`, `default_cache_behavior`, `acm_certificate_arn`.

outputs: немає.

README: README.md.

### Reference `cloudfront`

Файли: [modules/cloudfront/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cloudfront/main.tf:1>), [modules/cloudfront/out.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cloudfront/out.tf>), [modules/cloudfront/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cloudfront/vars.tf:1>).

resources: `aws_cloudfront_distribution.this`.

data: немає.

variables: `project`, `alb_dns`, `certificate_arn`, `domain_name`, `waf_arn`.

outputs: немає.

README: немає.

### Reference `cognito`

Файли: [modules/cognito/data.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cognito/data.tf:1>), [modules/cognito/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cognito/main.tf:1>), [modules/cognito/out.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cognito/out.tf:1>), [modules/cognito/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cognito/vars.tf:1>).

resources: `aws_cognito_user_pool.this`, `aws_cognito_user_pool_domain.this`, `aws_cognito_user_pool_client.this`.

data: `aws_region.current`.

variables: `project`, `cognito`, `callback_urls`.

outputs: `client_id`, `cognito_domain`, `pool_arn`.

README: README.md.

### Reference `cw_alarms`

Файли: [modules/cw_alarms/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cw_alarms/main.tf:1>), [modules/cw_alarms/out.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cw_alarms/out.tf:1>), [modules/cw_alarms/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/cw_alarms/vars.tf:1>).

resources: `aws_cloudwatch_metric_alarm.this`, `aws_sns_topic.cloudwatch_common_alarm`, `aws_sns_topic.cloudwatch_usage_alarm`.

data: немає.

variables: `alarms`.

outputs: `cloudwatch_alarm_arn`, `common_sns_topic_arn`, `usage_sns_topic_arns`.

README: README.md.

### Reference `ec2`

Файли: [modules/ec2/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/ec2/main.tf:1>), [modules/ec2/provider.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/ec2/provider.tf:1>), [modules/ec2/variables.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/ec2/variables.tf:1>).

resources: `aws_instance.this`, `aws_key_pair.this`, `aws_security_group.this`.

data: `aws_ami.this`.

variables: `instance_type`, `name`, `key_name`, `public_key`, `user_data`, `ami_id`, `iam_instance_profile`, `image`, `volume_size`, `vpc_security_group_ids`, `security_group_rules`, `subnet_id`, `vpc_id`, `tags`.

outputs: немає.

README: немає.

### Reference `ecr`

Файли: [modules/ecr/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/ecr/main.tf:1>), [modules/ecr/out.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/ecr/out.tf:1>), [modules/ecr/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/ecr/vars.tf:1>).

resources: `aws_kms_key.for_ecr`, `aws_ecr_repository.ecr`, `aws_ecr_lifecycle_policy.images`.

data: немає.

variables: `ecr_names`, `kms_key_arn`, `project`.

outputs: `ecr_arns`.

README: README.md.

### Reference `ecs`

Файли: [modules/ecs/data.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/ecs/data.tf:1>), [modules/ecs/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/ecs/main.tf:1>), [modules/ecs/out.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/ecs/out.tf:1>), [modules/ecs/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/ecs/vars.tf:1>).

resources: `aws_ecs_cluster.this`, `aws_cloudwatch_log_group.this`, `aws_ecs_cluster_capacity_providers.fargate`, `aws_ecs_service.app_fargate`, `aws_ecs_service.app_ec2`, `aws_launch_template.ecs_ec2`, `aws_security_group.ecs_sg_ec2`, `aws_autoscaling_group.ecs_asg`, `aws_ecs_capacity_provider.ecs-ec2`, `aws_ecs_cluster_capacity_providers.ecs-ec2`, `aws_iam_role.ecs_cluster_role_ec2`, `aws_iam_role_policy_attachment.ecs_cluster_role_policy`, `aws_iam_instance_profile.ecs_cluster`.

data: `terraform_remote_state.main`, `aws_ssm_parameter.ecs`, `aws_iam_policy_document.ecs_cluster_doc_ec2`.

variables: `project`, `env`, `security_groups`, `cluster_subnet`, `use_fargate`, `cluster_name`, `cloudwatch`, `launch_configuration`, `autoscaling_group`, `fargate_strategy`, `fargate_spot_strategy`, `target_group_arn`, `ecs_service`.

outputs: `ecs_service_id`.

README: README.md.

### Reference `elasticache`

Файли: [modules/elasticache/data.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/elasticache/data.tf:1>), [modules/elasticache/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/elasticache/main.tf:1>), [modules/elasticache/out.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/elasticache/out.tf:1>), [modules/elasticache/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/elasticache/vars.tf:1>).

resources: `aws_elasticache_cluster.redis`, `aws_cloudwatch_log_group.redis_slow_log`.

data: `aws_region.current`, `aws_caller_identity.current`, `aws_partition.current`, `aws_iam_policy_document.cloudwatch_logs_ws`.

variables: `project`, `cloudwatch_log_group_name`, `log_retention`, `enable_redis`, `elc_mutable`, `engine_version`, `elc_immutable`.

outputs: `elc_link`.

README: README.md.

### Reference `event_bridge`

Файли: [modules/event_bridge/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/event_bridge/main.tf:1>), [modules/event_bridge/output.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/event_bridge/output.tf>), [modules/event_bridge/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/event_bridge/vars.tf:1>).

resources: `aws_cloudwatch_event_rule.ecs-rule`, `aws_cloudwatch_event_target.ecs-target`.

data: немає.

variables: `topic_ecs_arn`.

outputs: немає.

README: README.md.

### Reference `ga`

Файли: [modules/ga/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/ga/main.tf:1>), [modules/ga/out.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/ga/out.tf>), [modules/ga/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/ga/vars.tf:1>).

resources: `aws_globalaccelerator_accelerator.main`, `aws_globalaccelerator_endpoint_group.ga_group`, `aws_globalaccelerator_endpoint_group.ga_group_eu`, `aws_globalaccelerator_listener.ga_listener`.

data: немає.

variables: `s3_bucket_name`, `project`, `alb_arn`.

outputs: немає.

README: README.md.

### Reference `iam`

Файли: [modules/iam/data.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/iam/data.tf:1>), [modules/iam/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/iam/main.tf:1>), [modules/iam/out.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/iam/out.tf:1>), [modules/iam/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/iam/vars.tf:1>).

resources: `aws_iam_role.task`, `aws_iam_policy.task`, `aws_iam_role_policy_attachment.task`, `aws_iam_role_policy_attachment.instance_profile`, `aws_iam_role_policy_attachment.gitlabrole`, `aws_iam_policy.instanceprofile`, `aws_iam_policy.gitlabrunner`, `aws_iam_role.instance_profile`, `aws_iam_role.gitlabrunner`, `aws_iam_role.ecs`, `aws_iam_instance_profile.ecs`, `aws_iam_instance_profile.gitlab_runner`, `aws_iam_role_policy_attachment.ecs`, `aws_iam_role.ecs_task_execution_role`, `aws_iam_role_policy_attachment.ecs_task`, `aws_iam_role.vpc_flow_logs`, `aws_iam_policy.vpc_flow_logs`, `aws_iam_role_policy_attachment.vpc_flow_logs`.

data: `aws_iam_policy_document.task`, `aws_iam_policy_document.ecs`.

variables: `policy_ecs`, `project`, `ecr_arns`, `bucket_arns`, `gitlab_arns`, `cache_backet_arn`.

outputs: `role_for_app`, `role_for_ecs`, `role_for_cluster`, `role_ws_task`, `flow_log_role`.

README: README.md.

### Reference `iam_roles`

Файли: [modules/iam_roles/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/iam_roles/main.tf:1>), [modules/iam_roles/output.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/iam_roles/output.tf:1>), [modules/iam_roles/variable.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/iam_roles/variable.tf:1>).

resources: `aws_iam_role.this`, `aws_iam_policy.this`, `aws_iam_role_policy_attachment.this`, `aws_iam_instance_profile.this`.

data: немає.

variables: `roles`.

outputs: `roles`, `custom_policies`, `instance_profiles`.

README: немає.

### Reference `imgproxy`

Файли: [modules/imgproxy/data.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/imgproxy/data.tf:1>), [modules/imgproxy/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/imgproxy/main.tf:1>), [modules/imgproxy/output.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/imgproxy/output.tf>), [modules/imgproxy/variable.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/imgproxy/variable.tf:1>).

resources: `aws_lambda_function.this`, `aws_lambda_function_url.this`, `aws_lambda_permission.this`, `aws_cloudfront_origin_access_control.this`, `aws_cloudfront_distribution.this`, `aws_cloudwatch_log_group.this`, `aws_iam_role.this`, `aws_iam_role_policy.this`.

data: `aws_caller_identity.current`, `aws_region.current`.

variables: `function_name`, `image_uri`, `architecture`, `memory_size`, `timeout`, `environment_ssm_path`, `variables`, `acm_certificate_arn`, `cloudfront_aliases`.

outputs: немає.

README: немає.

### Reference `lambda`

Файли: [modules/lambda/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/lambda/main.tf:1>), [modules/lambda/outputs.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/lambda/outputs.tf:1>), [modules/lambda/provider.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/lambda/provider.tf:1>), [modules/lambda/variables.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/lambda/variables.tf:1>).

resources: `aws_iam_role.this`, `aws_iam_role_policy_attachment.this`, `aws_lambda_function.this`.

data: немає.

variables: `runtime`, `filename`, `function_name`, `handler`, `architectures`, `memory_size`, `timeout`.

outputs: `lambda_arn`, `lambda_name`.

README: немає.

### Reference `pagerduty`

Файли: [modules/pagerduty/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/pagerduty/main.tf:1>), [modules/pagerduty/outputs.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/pagerduty/outputs.tf:1>), [modules/pagerduty/variables.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/pagerduty/variables.tf:1>).

resources: `pagerduty_service.this`, `pagerduty_service_integration.prometheus`, `pagerduty_service_event_rule.start_session`.

data: `pagerduty_escalation_policy.main`, `pagerduty_vendor.integrations`, `pagerduty_priority.p5`.

variables: `project`, `slack_channel_id`, `slack_workspace_id`, `list_of_integration`.

outputs: `pagerduty_vendor`, `pagerduty_integrations_ids`, `pagerduty_integrations_integration_keys`, `pagerduty_integrations_html_urls`, `pagerduty_integration_email`.

README: README.md.

### Reference `rds`

Файли: [modules/rds/data.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/rds/data.tf:1>), [modules/rds/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/rds/main.tf:1>), [modules/rds/out.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/rds/out.tf:1>), [modules/rds/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/rds/vars.tf:1>).

resources: `random_string.user`, `random_password.password`, `aws_db_instance.postgres`, `aws_kms_key.rds_key`.

data: `aws_region.current`.

variables: `project`, `rds_mutable`, `rds_immutable`.

outputs: `rds_port`, `rds_user`, `rds_link`, `db_id`, `rds_password`.

README: README.md.

### Reference `s3`

Файли: [modules/s3/data.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/s3/data.tf>), [modules/s3/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/s3/main.tf:1>), [modules/s3/out.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/s3/out.tf:1>), [modules/s3/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/s3/vars.tf:1>).

resources: `aws_s3_bucket.this`, `aws_s3_bucket_public_access_block.this`, `aws_s3_bucket_policy.this`, `aws_s3_bucket_cors_configuration.rule`, `aws_s3_bucket_versioning.this`, `aws_s3_bucket_ownership_controls.s3_bucket_acl_ownership`.

data: немає.

variables: `s3_bucket_name`, `versioning`, `bucket_policy`, `cors_rule`, `bucket_public_access`.

outputs: `bucket_arn`.

README: README.md.

### Reference `security_groups`

Файли: [modules/security_groups/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/security_groups/main.tf:1>), [modules/security_groups/out.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/security_groups/out.tf:1>), [modules/security_groups/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/security_groups/vars.tf:1>).

resources: `aws_security_group.rds`, `aws_security_group.elasticache`, `aws_security_group.ecs`, `aws_security_group.alb`, `aws_security_group.bastion`, `aws_security_group_rule.ecs_cidr`, `aws_security_group_rule.alb_cidr`, `aws_security_group_rule.bastion_cidr`.

data: немає.

variables: `vpc_id`, `project`, `rds_sg_name`, `elasticache_sg_name`, `ecs_sg_name`, `alb_sg_name`, `cidr_to_anywhere`, `cidr_only_vpc`, `ecs_cidr_rules`, `alb_cidr_rules`, `bastion_cidr_rules`, `bastion_create`.

outputs: `elc_sg`, `rds_sg`, `cluster_sg`, `alb_sg`, `bastion_rule`.

README: README.md.

### Reference `service_discovery`

Файли: [modules/service_discovery/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/service_discovery/main.tf:1>), [modules/service_discovery/out.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/service_discovery/out.tf:1>), [modules/service_discovery/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/service_discovery/vars.tf:1>).

resources: `aws_service_discovery_private_dns_namespace.this`, `aws_service_discovery_service.this`.

data: немає.

variables: `project`, `discovery_namespace`, `discovery_service`.

outputs: `discovery_service_arn`.

README: немає.

### Reference `slack`

Файли: [modules/slack/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/slack/main.tf:1>), [modules/slack/outputs.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/slack/outputs.tf:1>), [modules/slack/variables.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/slack/variables.tf:1>).

resources: `slack_conversation.this`.

data: немає.

variables: `project`.

outputs: `slack_channel_id`.

README: README.md.

### Reference `sns`

Файли: [modules/sns/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/sns/main.tf:1>), [modules/sns/output.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/sns/output.tf:1>), [modules/sns/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/sns/vars.tf:1>).

resources: `aws_sns_topic.topic`, `aws_sns_topic.ecs-topic`, `aws_sns_topic.topic-rds`, `aws_kms_key.sns-key`.

data: `aws_caller_identity.current`, `aws_partition.current`, `aws_region.current`.

variables: `topic_rds_events`, `topic_main`, `project`, `topic_ecs`.

outputs: `topic_main_arn`, `topic_rds_arn`, `topic_ecs_arn`.

README: README.md.

### Reference `vpc`

Файли: [modules/vpc/data.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/vpc/data.tf:1>), [modules/vpc/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/vpc/main.tf:1>), [modules/vpc/out.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/vpc/out.tf:1>), [modules/vpc/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/vpc/vars.tf:1>).

resources: `aws_vpc.main`, `aws_eip.this`, `aws_instance.nat`, `aws_security_group.nat`, `aws_internet_gateway.this`, `aws_nat_gateway.this`, `aws_subnet.public_1`, `aws_subnet.public_2`, `aws_subnet.public_3`, `aws_subnet.private_1`, `aws_subnet.private_2`, `aws_subnet.private_3`, `aws_db_subnet_group.rds`, `aws_elasticache_subnet_group.this`, `aws_route_table.public`, `aws_route_table.private`, `aws_route_table_association.public_1`, `aws_route_table_association.public_2`, `aws_route_table_association.public_3`, `aws_route_table_association.private_1`, `aws_route_table_association.private_2`, `aws_route_table_association.private_3`.

data: `aws_region.current`, `aws_ami.nat`.

variables: `project`, `rds_subnet_group_name`, `elc_subnet_group_name`, `enable_dns_support`, `enable_dns_hostnames`, `cidr_to_anywhere`, `vpc_name`, `nat_type`, `instance_type`, `key_name`, `enable_nat_schedule`.

outputs: `vpc_id`, `elc_group`, `rds_group`, `private_sub_1`, `private_sub_2`, `private_sub_3`, `pub_sub`, `pub_sub2`, `pub_sub3`, `nat`, `igw`.

README: README.md.

### Reference `waf`

Файли: [modules/waf/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/waf/main.tf:1>), [modules/waf/out.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/waf/out.tf:1>), [modules/waf/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/waf/vars.tf:1>).

resources: `aws_wafv2_web_acl.this`, `aws_cloudwatch_log_group.this`, `aws_wafv2_web_acl_logging_configuration.this`, `aws_wafv2_ip_set.this`.

data: немає.

variables: `project`, `alb_arn`, `associate_alb`, `web_acl_name`, `rules`, `ipset_allocation`, `enable_ipset`, `ipset_name`, `log_prefix`.

outputs: `waf_arn`.

README: немає.

### Reference `ws`

Файли: [modules/ws/data.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/ws/data.tf:1>), [modules/ws/main.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/ws/main.tf:1>), [modules/ws/vars.tf:1](<D:/Робота/Codica/golfer2golfer/terraform/modules/ws/vars.tf:1>).

resources: `aws_ecs_cluster.ecs_cluster-ws`, `aws_ecs_cluster_capacity_providers.ws_capacity`, `aws_ecs_service.ws`, `aws_cloudwatch_log_group.logs_ws`, `aws_kms_key.ws_key`.

data: `aws_cloudwatch_log_group.logs_ws`, `aws_region.current`, `aws_caller_identity.current`, `aws_partition.current`, `aws_iam_policy_document.cloudwatch_logs_ws`.

variables: `cluster_name`, `task_family_name`, `tg_arn`, `cluster_subnet`, `cluster_role`, `container_for_balancing`, `service_name`, `ecs_sg`, `ecr_api`, `task_role`, `ecr_env`, `project`, `task`, `env_prefix`.

outputs: немає.

README: README.md.

Первинні зовнішні підтвердження: [ECS AL2/AL2023](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html), [ECS target types/ports](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/alb.html). Поточні runtime/security findings — [INDEPENDENT_REVIEW](INDEPENDENT_REVIEW.md); план — [SIMPLIFICATION_PROPOSAL](SIMPLIFICATION_PROPOSAL.md).
