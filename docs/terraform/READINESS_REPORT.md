# Результати підготовки контрольованого розгортання

26.11.2026. База Git: main5f01e24. До цієї зміни включено незакомічені результати попереднього аудиту, включно з видаленням owner/manual account input, графами й довідниками. Користувацькі порожні рядки main.tf збережено. Налаштування HCP та спосіб авторизації не змінювалися.

## Що виправлено

1. Ранні етапи більше не потребують образу/AMI/ACM/runtime secrets. Root33 inputs,3 без default замість11; решта8 колишніх required стали умовними. Значення перевіряються при активації відповідного етапу, перевірки ARN account/region збережені через caller identity.
2. Додано provisioning gates і окремі activity gates. Stateful buckets/ECR/RDS/AI/DB volumes та log group захищені prevent_destroy;22 moved blocks описують зміну індексованих адрес без ручного перенесення state. Новий ресурс лише aws_ec2_instance_state.power; усі69 попередніх resource declarations збережено.
3. AWS MySQL використовує перевірений CA, hostname verification і TLS>=1.2. CA включено в image як публічний сертифікат. Помилки TLS, включно з wrapped PyMySQL2003, обробляються без витоку credentials. Локальний non-TLS режим доступний лише для local/non-RDS.
4. Backend task одержує умовний HTTPS ML endpoint, allowlisted hostname та optional CA path. Shared token передається через SSM secret reference. Client обмежує timeouts, перевіряє TLS, забороняє redirects/небезпечні URL. Реального прогнозу не додає.
5. Замість широкого ALB module barrier ECS чекає фактичний listener rule через precondition; додано IAM policy readiness, route readiness та EC2/EBS propagated tags. CloudFront API origin залежить від реального DNS alias й існує тільки у відкритому window.
6. t3.micro заблокований для backend provisioning; default t3.small/task1024/OS+Agent reserve512 лишено. Capacity surge до2 лише за явним прапорцем, без автоматичного постійного збільшення. Автоматичний Instance Refresh не додано.
7. HCP керує task_definition, щоб зміни TLS/env/secrets застосовувалися. Direct ECS deployment draft лишено disabled із HOLD до погодження ownership. Жодні infrastructure deployment jobs не активовано.

## Документація і графи

- [Порядок етапів, conditional inputs, TLS/ML/ECS та невирішені питання](CONTROLLED_DEPLOYMENT.md).
- [Завершення демонстрації та залишкові витрати](DEMO_SHUTDOWN.md).
- [HCP inventory33 inputs](../HCP_TERRAFORM.md).
- [Усі93 variables](VARIABLES_REFERENCE.md), [70 resource blocks](RESOURCES_AUDIT.md), [data/locals/outputs](MODULES_REFERENCE.md).
- [Dependency graph](DEPENDENCY_GRAPH.md), [DOT](terraform-dependencies.dot), [мережа](NETWORK_GRAPH.md), [архітектура](ARCHITECTURE_GRAPH.md).

Графи регенеровано власним lexical/static аналізатором:303 nodes,918 edges,0 нерозвʼязаних підтримуваних references,0 циклів у символічному графі. Graphify на попередньому етапі не зміг обробити HCL через відсутню grammar; його повторно не встановлювали й не називаємо результат власного аналізатора Graphify/Plan. Не розгортаються count instances, не перевіряється provider schema чи AWS feasibility.

## Перевірки

| Перевірка | Результат |
|---|---|
| Python unittest |81 total:78 PASS,3 SKIP (ізольовані MySQL integration, не запускалися на наявній БД) |
| Нові regression tests |12: MySQL TLS/downgrade/pre-auth/помилки, ML TLS/URL/тайм-аути, захист state/address moves |
| Ruff lint / формат extracted modules | PASS |
| pip check | PASS |
| React component tests |18 PASS |
| ESLint / TypeScript / production build | PASS; frontend source не змінено |
| OpenAPI backend/ML | PASS |
| Реальний loopback Flask→FastAPI HTTP | PASS:503 model_unavailable, value=null; без моделі й медичних даних |
| Source checker |22 TF files,8 module contracts,33 inputs,4800 cost rows PASS |
| Resource declaration comparison |69 попередніх збережено, один power-state block додано |
| HRI | climate_health/fuzzy.py byte-identical до snapshot,27 правил не змінені |
| Public CA |3 CA certificates, валідні на26.11.2026; SSLContext завантажує їх; приватних ключів немає |
| Secrets | Candidate files+Git history+точне зіставлення локального credential:0 знахідок; перед commit повторено для index |

Поточні машинні результати: [verification.json](verification.json). Старі VERIFICATION/AUDIT sections — baseline до змін, не доказ поточного remote CI. Локальний secret scanner евристичний, його проходження не гарантує абсолютну відсутність секретів.

## Залишається неперевіреним

Terraform Init/Validate/Plan, provider schema, реальні state migrations/count branches й resource replacement — не виконувалися за забороною. Немає runtime вимірювань memory/CPU, ASG scale-from-zero/rolling/draining, реального RDS TLS/reader/schema/restore, private AI DNS/TLS/token/AMI agent. AI provisioning заблокований ai_runtime_reviewed=false до фактичного review. Engine version availability, IAM boundary і KMS дозволи потребують перевірки в погодженому середовищі.

AWS/Docker/Terraform локально не запускалися; HCP runs, workspace configuration та AWS resources не змінено. MySQL дані/структура, HRI, React та Word незмінні. Жодного push і нового remote CI. Наступний крок — review змін та окремий дозвіл на push; VCS push може автоматично викликати HCP Plan, що слід врахувати перед публікацією. Apply лишається окремою контрольною точкою.

## Перелік файлів локального коміту

До index включено53 файли, зокрема матеріали попереднього аудиту. Немає env secrets, venv, plans/state, backups або Word.

- .dockerignore
- .env.example
- Dockerfile
- climat.py
- climate_health/ml_client.py
- climate_health/tls.py
- docs/CI_CD_PIPELINE.md
- docs/HCP_TERRAFORM.md
- docs/INFRASTRUCTURE.md
- docs/ROADMAP.md
- docs/TERRAFORM_GUIDE.md
- docs/api/backend.openapi.yaml
- docs/terraform/ARCHITECTURE_GRAPH.md
- docs/terraform/AUDIT_REPORT.md
- docs/terraform/CONTROLLED_DEPLOYMENT.md
- docs/terraform/COST_AUDIT.md
- docs/terraform/DEMO_SHUTDOWN.md
- docs/terraform/DEPENDENCY_GRAPH.md
- docs/terraform/HOW_TERRAFORM_WORKS.md
- docs/terraform/MODULES_REFERENCE.md
- docs/terraform/NETWORK_GRAPH.md
- docs/terraform/READINESS_REPORT.md
- docs/terraform/README.md
- docs/terraform/REQUIRED_VARIABLES_AUDIT.md
- docs/terraform/RESOURCES_AUDIT.md
- docs/terraform/VARIABLES_REFERENCE.md
- docs/terraform/VERIFICATION.md
- docs/terraform/graphify-attempt.json
- docs/terraform/graphify-method.json
- docs/terraform/terraform-dependencies.dot
- docs/terraform/terraform-inventory.json
- docs/terraform/verification.json
- infrastructure/certificates/README.md
- infrastructure/certificates/rds-us-east-1-bundle.crt
- infrastructure/ci/application-release.yml.example
- infrastructure/terraform/README.md
- infrastructure/terraform/data.tf
- infrastructure/terraform/main.tf
- infrastructure/terraform/modules/ai/main.tf
- infrastructure/terraform/modules/ecr/main.tf
- infrastructure/terraform/modules/ecr/variable.tf
- infrastructure/terraform/modules/ecs-backend/main.tf
- infrastructure/terraform/modules/frontend/main.tf
- infrastructure/terraform/modules/mysql/main.tf
- infrastructure/terraform/modules/networking/main.tf
- infrastructure/terraform/provider.tf
- infrastructure/terraform/variable.tf
- scripts/audit_terraform.py
- scripts/check_infrastructure_sources.py
- scripts/document_terraform.py
- scripts/terraform_audit_notes.py
- tests/test_deployment_readiness.py
- tests/test_terraform_audit.py
