# ClimateHealth — AWS provider та перевірки перед публікацією

25.11.2026. Поточна конфігурація — `infrastructure/terraform`; старі звіти відображають стан на дату написання та не замінюють цю інструкцію.

## Зміна provider

За прямою вказівкою користувача прибрано provider-level `allowed_account_ids`. Terraform >=1.11,<2, hashicorp/aws =6.74.0, region input та default_tags збережено. Credentials, profiles, access keys або фактичний AWS Account ID не додавалися.

`aws_account_id` лишається required input без default: його використовують validations для ACM certificate ARN, runtime SSM parameter ARNs та IAM permissions boundary ARN. Він більше не обмежує фактичний account provider credentials. IAM/OIDC templates мають placeholders account/organization/project/workspace, а не runtime залежність від Terraform input; фактичні значення потребують окремого погодження.

Основні механізми контролю: HCP OIDC із точними workspace/run-phase trust conditions, окремі dev/production plan/apply roles, least-privilege permissions, окремі state, Manual Apply та Auto Apply=false. Це підготовлена конфігурація, не підтвердження створеного IAM або HCP connection. Незалежний GitHub release action account check збережено. Source checker більше не вимагає видаленого provider guard; інші перевірки credentials, inputs, gates, trust audience/subject та module contracts збережено.

## Склад підготовленого AWS-коміту

- Один активний Terraform root, 21 .tf файл та 8 локальних modules: networking/security/ecr/alb/frontend/ecs-backend/mysql/ai. Outputs та 69 декларацій ресурсів збережено при перенесенні.
- Старі активні scaffolds прибрано з root; byte-exact історичні матеріали збережені під docs/history з неактивними розширеннями. Backend/cloud blocks у поточному root відсутні, S3 state bucket не використовується.
- ECS/EC2/ECR/ALB/VPC/S3/CloudFront/MySQL/AI code, HCP/OIDC instructions/templates, неактивний application release draft, ADR/кошториси та машинні інвентарі.
- Source checker, offline cost calculator, ECS revision helper і два тести; ML Dockerfile пакує лише поточний model_unavailable API boundary, без навченої моделі.
- Адресний .gitattributes pattern для docs/history/**/*.historical вимикає newline normalization лише для оригінальних snapshots; staged blobs мають збігатися з локальними SHA256, а не лише робочі копії. Це не binary/exclude правило сканера секретів.
- Terraform workflow — тільки ручні Python source checks; container job залишається false, release файл має .example та false job. Deployment не активовано.

Раніше створений UI/UX коміт `4b3033b5e4badcdf2e8a7f4bb87e4c2967c515cb` залишається незмінним із первинним автором. Нових application/HRI/UI/ML/Word змін у цьому етапі немає. Автор нового коміту береться з чинної Git configuration, без її зміни.

## Локальні результати перед комітом

| Перевірка | Результат |
|---|---|
| Python unit/API/ML/helper tests | 63 загалом: 60 PASS, 3 MySQL write integration SKIP |
| React components | 18 PASS |
| ESLint / TypeScript / Vite production build | PASS |
| JS HTML-escaping assertions | 5 PASS |
| Ruff / format extracted modules | PASS |
| pip check / OpenAPI backend та ML | PASS |
| Реальний loopback Flask → FastAPI | Чесний HTTP503 model_unavailable; без БД/прогнозу |
| Terraform source checker | PASS:21 .tf,8 contracts,27 inputs,4800 cost rows |
| JSON / YAML / disabled deployment gates | PASS |
| Git diff / index та secret checks | Перевіряються повторно після staging і перед push |

Starlette/httpx deprecation warning залишається; це не падіння тестів. Локальні MySQL write tests не запускалися. Frontend build outputs лишаються ігнорованими.

## Git, секрети та межі виконання

Origin перевірено: git@github.com:BohdanHavran/ClimateHealth-Monitoring.git. До підготовки коміту main випереджала origin/main одним незмінним UI комітом. Read-only SSH перевірка підтвердила віддалений SHA43b3ba1; перед push виконується повторна перевірка.

Git candidates перевірено за scope, file type та ignore rules. .env/.venv/.secrets, Terraform state/plans, приватні ключі, архіви, backups, node_modules, dist і .local-verification виключені. Єдині нові архівні матеріали в docs/history — прочитані текстові конфігурації, без перенесення секретів/state. Staged bytes та повна commit history проходять offline сканування; локальне exact DB credential comparison не виводить значення. Евристичний scan не гарантує абсолютної відсутності секретів.

Користувач дозволив один звичайний push main після успішних перевірок без переписування історії. Цей документ є pre-publication snapshot: результат push та фактичні GitHub Actions будуть зафіксовані в окремому фінальному звіті. Наступні push виправлень CI потребують нового дозволу.

Terraform CLI/Docker/HCP runs/AWS provisioning, доступ до домашньої MySQL, платні ресурси та Word не запускалися/не змінювалися. Source checks не є HCL/provider validation або Terraform Plan. Перед першим дозволеним HCP run потрібні approved account/region/org/project, IAM/OIDC bootstrap/phase roles, protected variables, pinned AMI/image digest, DNS/ACM та DB reader/TLS/restore prerequisites. Усі activation gates false; їх зміна та run/apply потребують окремого review й дозволу.

Повні поточні інструкції: [HCP](HCP_TERRAFORM.md), [root](../infrastructure/terraform/README.md), [архітектура](AWS_ARCHITECTURE.md), [кошторис](AWS_COST_ESTIMATE.md), [CI/CD](CI_CD_PIPELINE.md). Історичні згадки account guard та попередньої вкладеності в датованих звітах не є вимогами до поточного provider.
