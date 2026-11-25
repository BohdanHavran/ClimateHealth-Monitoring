> Історичний звіт першого AWS дизайну. Актуальний пакет: [ECS/HCP report](AWS_ECS_HCP_REPORT.md), [ADR0005](adr/0005-ecs-cloudfront-hcp-terraform.md). Не є поточним runbook.

# Диплом — AWS: звіт про архітектуру та бюджет

24.11.2026. Система ClimateHealth; репозиторій ClimateHealth-Monitoring. AWS — єдина цільова хмара. Виконано документування та підготовку конфігурацій; платні ресурси не створювалися.

## Результат
1. Виявлено неактуальні cloud-схеми в INFRASTRUCTURE, ARCHITECTURE, TERRAFORM_GUIDE, ROADMAP та хмарній частині ADR 0002; їх замінено посиланнями/рішеннями AWS. Історичні звіти фаз збережені як записи відповідних етапів.
2. Спроєктовано App EC2, приватний CPU AI EC2, app-only MySQL (EC2 або RDS), VPC/SG, HTTPS/service auth, ECR/S3 releases. Запропоновано один EC2 як дешевший демонстраційний початок. Немає Kubernetes/EKS/Helm.
3. Для private AI без NAT передбачено S3 gateway endpoint і підписані OCI/model bundles, baked AMI/agent. Уточнено, що це не дає прямого ECR/SSM/PyPI/CloudWatch доступу. Агент, workload IAM і TLS ще потребують реалізації/перевірки; секретний bootstrap — окремий gate.
4. Додано AWS review scaffold: state bootstrap з approval guard, versioning/SSE/public-block/TLS/prevent_destroy; networking/security modules; resource-free dev/production roots. Офіційний hashicorp/aws 6.74.0 перевірено у Registry через публічний read-only HTTP, не встановлено. Модулі EC2/RDS/ECR та повні identity permissions ще не реалізовано й не підключено до roots.
5. Оновлено тільки неактивний Terraform workflow target на AWS. Active application/secret workflows не змінено; контейнерний і Terraform jobs вимкнені. OIDC trust/state policy examples не створюють ролей і не є повною deploy policy.
6. Тарифи EC2/RDS реально прочитано з відкритих прайс-листів без AWS login/API credentials; збережено selected rateCode/SKU. Інші статті мають офіційні pricing references й явні обсяги. Ніяких AWS CLI/SDK provisioning-команд не виконували.

## Кошторис us-east-1
730 год/місяць, USD до податків/кредитів:
| Сценарій | Baseline | З резервом 20% |
|---|---:|---:|
| A: один EC2 t3.medium, MySQL/ML приватні процеси | $39.77 | $47.73 |
| B: app t3.medium + AI t3.small, MySQL на app | $56.56 | $67.87 |
| C: два t3.small + RDS db.t4g.micro, gp3 20 GB | $53.75 | $64.50 |
| A-demo: 80 активних годин, storage весь місяць | $9.48 | $11.38 |

Докладні EBS/IPv4/S3/ECR/traffic/logs/snapshots/NAT/endpoint припущення: [AWS_COST_ESTIMATE](AWS_COST_ESTIMATE.md). Розміри не benchmark; B/C мають різний розмір app, бо C не розміщує там MySQL. Рекомендовано A-demo, gross monthly budget $25, cumulative credit ledger, $20 резерву. Budgets не є hard cap, додаткові кредити/Free Tier/GPU не враховано. Реальний залишок і expiration $100 у Billing не перевірялися.

Важлива знахідка: RDS MySQL 8.0 завершила standard support 31.07.2026. Для майбутньої копії пропонується MySQL 8.4 LTS після compatibility/restore tests, без автоматичної зміни локальної 8.0.40. Extended Support charges не включені до baseline.

## Файли
**Оновлено:** README.md; docs/ARCHITECTURE.md, INFRASTRUCTURE.md, TERRAFORM_GUIDE.md, CI_CD_PIPELINE.md, ROADMAP.md, TECH_STACK_DECISIONS.md; docs/adr/0002-static-dashboard-and-private-ml.md (лише позначення superseded cloud-рішення); .github/workflows/terraform-ci.yml (job лишився вимкненим).

**Створено:**
- docs/AWS_ARCHITECTURE.md — схеми, мережа, private AI без NAT, порівняння MySQL.
- docs/AWS_COST_ESTIMATE.md — ставки, формули, три сценарії, бюджет/кредитний контроль.
- docs/adr/0004-aws-infrastructure-and-credit-budget.md та ADR index.
- infrastructure/terraform/README.md — історичний parent root не застосовувати.
- infrastructure/terraform/aws/README.md, bootstrap/main.tf, modules/networking/main.tf, modules/security/main.tf.
- infrastructure/terraform/aws/environments/{dev,production}/{versions.tf,backend.tf,main.tf,backend.s3.hcl.example} — review roots і S3 backend examples.
- infrastructure/ci/aws-production-trust.json.example, aws-state-policy.json.example — IAM приклади з placeholders, не credentials.
- docs/reports/aws-price-evidence.json, aws-cost-model.json, aws-design-checks.json; цей звіт.

## Перевірки та обмеження
- YAML прочитано наявним PyYAML; manual-only Terraform if:false, application container if:false підтверджені. JSON templates/price evidence валідні. Бюджетні суми перевірено з неокруглених складових, локальні Markdown links існують, git diff --check успішний.
- SHA-256 усіх 8 історичних Terraform/config files збігаються з початковими. git diff для frontend/backend/API/ML/tests порожній. Локальний 4b3033b збережено, origin не змінено.
- Офлайн перевірка кандидатів Git та історії, включно з перевіркою точного локального секрету: 0 знахідок. Значення секретів не виводилися. Це евристична перевірка, не гарантія абсолютної відсутності секретів.
- Terraform fmt/init/validate/plan/apply/destroy, Docker, AWS provisioning не запускалися. HCL parser/provider schema validation відкладені; нових залежностей не встановлювали. Текстовий review не видається за перевірку Terraform.
- Програмні тести не перезапускали: програмні файли й залежності незмінні, це документаційний/конфігураційний етап. Немає нового remote CI, push або модифікацій наявної MySQL/Word.
- Застосовано наявні інструкції Terraform patterns і ADR для структури, state/lock, pinning та наслідків рішень. Graphify/REA не потрібні: програмну архітектуру не змінювали.

## Що узгодити
- Сценарій A/B/C, us-east-1/data residency, RAM/ліміти й щомісячний бюджет/строк демонстрації.
- Фактичні credits, eligible services/expiration, owner/email для Budgets та доступ людини через federation/MFA.
- Cloud MySQL варіант/версію, дозволений export dataset, backup/restore/RPO/RTO, reader identity й TLS клієнт.
- Домен/HTTPS, public access control, IAM/environment protections, AMI/deployment agent та секретний bootstrap.
- Окремо: push; виконання Docker/Terraform checks; S3 bootstrap; billable plan/apply; deployment. Жоден із цих дозволів не виводиться з погодження AWS як платформи.

## Git і наступний крок
HEAD 4b3033b5e4badcdf2e8a7f4bb87e4c2967c515cb, main попереду origin/main на один локальний UI-коміт. AWS-зміни залишено окремим незакоміченим набором для перегляду; історію не переписували, push не виконано. Наступний крок — погодити A-demo/region/budget і переглянути AWS diff; до окремого дозволу інфраструктуру не запускати.
