# ClimateHealth — ECS, HCP Terraform та повторне використання модулів

Дата: 24.11.2026. Результат цього етапу — код та документація для ревʼю, без розгортання. Поточний root: `infrastructure/terraform/aws`. Попередній AWS-каркас збережено як історичний матеріал, без перенесення state.

## Рекомендоване рішення

Для контрольованих демонстрацій: ECS EC2 на одному **t3.small**, AL2023 ECS-optimized AMI, ASG/Capacity Provider, bridge networking та фіксований host port; **ALB** як HTTPS-origin CloudFront; React у приватному **S3 з OAC + CloudFront**; приватна **RDS MySQL Single-AZ**; **без NAT**. Host має public IPv4 для виходу до погодних API, але ingress до backend дозволений тільки від ALB. ALB приймає HTTPS від CloudFront origin-facing prefix list та перевіряє секретний заголовок. Це зменшує можливість обходу, проте не замінює автентифікацію користувачів. S3 gateway endpoint не забезпечує доступу до Open-Meteo.

AI за замовчуванням вимкнений. Надалі — окремий приватний CPU EC2, початковий кандидат t3.small, з переходом до medium/large лише після benchmark. Публікація підписаного пакета в S3 підготовлена як контракт; приватний AMI/агент його отримання ще не реалізований. Моделі та прогнозних результатів немає.

Це не найдешевше рішення для постійного 24/7: Compose без ALB дешевший, а Fargate може бути дешевшим за ECS EC2 при достатності малої памʼяті. ECS обрано для демонстрації керованих task revisions, health checks, rollback та capacity providers. Остаточне sizing потребує вимірювань. Один EC2 не гарантує безперервного оновлення. Дефолт — контрольована перерва; optional друга instance оплачується окремо, а готовність її task ще належить перевірити.

## Аналіз власних модулів

Джерело прочитано без змін і без Git-операцій: `D:\Робота\Codica\golfer2golfer\terraform\modules\`. Перевірено **28 каталогів, 96 Terraform-файлів**, доступні 20 Markdown-документів та 3 JSON policies. SHA256 всіх 96 оригінальних Terraform-файлів залишилися незмінними.

Безпосередньо адаптовано тільки блок ECR repository та змінну ecr_names: immutable tags, scan on push, AES256, lifecycle для untagged images. Інші компоненти написано під вимоги ClimateHealth після аналізу вихідних рішень. Жоден модуль не скопійовано цілком без перевірки. Секрети, tfstate, ключі, tfvars та сторонні локальні конфігурації не переносилися.

Виявлено, зокрема: PostgreSQL замість MySQL у donor RDS, AL2 ECS AMI, широкі SSH/NAT правила, mutable ECR, CDN без OAC, надмірні ignore_changes та дублювання маршрутів. Повна матриця всіх 28 модулів, inputs/outputs/providers та причини відмови наведені в [звіті повторного використання](TERRAFORM_MODULE_REUSE.md); машинний інвентар — [JSON](reports/terraform-module-inventory.json). Походження двох адаптованих фрагментів зафіксовано в [provenance](reports/module-reuse-provenance.json).

## Terraform та HCP

Один самодостатній root, **21 .tf файл, 8 локальних модулів**: networking, security, ecr, alb, frontend, ecs-backend, mysql, ai. Root має main.tf, provider.tf, variable.tf, output.tf, README. Sources відносні; runtime-залежності від donor немає. AWS provider зафіксовано на 6.74.0; сумісність зі схемою provider ще не підтверджена. Lockfile без реального init не вигадувався.

Передбачено dev/production HCP workspaces з незалежними state, змінними та ролями. Запропоновані назви: climatehealth-dev / climatehealth-production; organization/project ще погоджуються. Working directory — `infrastructure/terraform/aws`, trigger pattern охоплює вкладені modules. VCS-driven remote plan та manual apply; Auto Apply вимкнений за проєктним рішенням. Немає S3 state bucket, backend S3 або формального cloud block. Workspaces ще не створені й не підключені.

Підготовлено 4 HCP OIDC trust-шаблони для dev/production × plan/apply з точним subject, audience та run phase. GitHub OIDC має окремий issuer і deployment roles. Повні IAM permissions та permissions boundary підлягають окремому review/bootstrap; адміністративні права не підставлено. Деталі та тарифні обмеження — [HCP Terraform](HCP_TERRAFORM.md).

Попередні **12 файлів AWS-каркаса** збережені з точними SHA256 у `infrastructure/terraform/history/aws-ec2-s3-state-20261124`, Terraform-файли мають суфікс `.historical`. Архів не є активним root. Попередні документи також збережені в docs/history. Існуючий state не читали, не переносили й не змінювали.

## Кошторис і бюджет

Регіон порівняння us-east-1, USD, без податків; використано офіційні цінові сторінки та публічні каталоги. Free Tier/кредити автоматично не віднімаються. Повні припущення, джерела, NAT 10/50/100 GB, endpoints, DB scheduling, AI small/medium та deployment surge — [кошторис](AWS_COST_ESTIMATE.md). [CSV-матриця](reports/aws-architecture-cost-matrix.csv) містить **4800 комбінацій** і позначає технічно непридатні варіанти. Кількість комбінацій не означає реалізації всіх альтернатив у Terraform.

| Профіль | 80 годин backend/ALB | 730 годин backend/ALB |
|---|---:|---:|
| ECS small, RDS постійно, AI off, без NAT | $24.26 | $62.68 |
| Те саме + резерв 20% | $29.12 | $75.21 |
| Те саме з AI small протягом 80 годин | $27.53 | $65.94 |
| Те саме з AI та резервом 20% | $33.03 | $79.13 |
| Compose small без ALB, RDS постійно, AI off | $21.60 | $38.37 |

80-годинний профіль залишає RDS та storage оплачуваними весь місяць. ALB не зупиняється: економія вимагає його погодженого видалення/повторного створення через manual HCP run, а не лише scale-to-zero ECS. Якщо залишити ALB на 730 годин, до 80-годинного профілю додається близько $21.65. Автоматичного destroy/scheduler немає.

$100 кредитів арифметично вистачає приблизно на **3.43 демонстраційного місяця** або **1.33 місяця 24/7** з резервом, лише за відповідності eligibility, строку дії та реального споживання припущенням. Майбутні кредити не підтверджені. HCP Free умовний: до 500 managed resources на organization, спільних для workspaces/проєктів; можливі платні функції не оплачуються автоматично AWS credits. Budget alerts не є жорсткою межею витрат. Запропонований gross budget $35 для демонстраційного профілю ще не створено.

## CI/CD і код

Infrastructure: GitHub → HCP VCS workspace → remote plan → review/manual apply. Дублюючого Terraform apply у GitHub Actions немає. Поточний terraform-ci.yml виконує лише вручну запущені source checks стандартним Python, без Terraform та AWS credentials.

Application release підготовлено як **неактивний `.yml.example`**, job додатково вимкнений. Frontend — build, immutable assets, index.html last/no-store, CloudFront invalidation. Backend — тести, ECR scan, digest, reviewed base task → нова revision → service health/rollback. AI — build і підписаний immutable S3 пакет; фактичне отримання/активація приватним host ще відсутні. Всі Docker/AWS команди тут лише текст майбутнього workflow, вони не запускалися. [CI/CD](CI_CD_PIPELINE.md) містить обмеження та IAM handoff.

Додано offline helper підготовки ECS revision і 2 тести, stdlib калькулятор кошторису, source checker; ML Dockerfile пакує лише існуючий FastAPI model_unavailable boundary, без PyTorch моделі. Application/Secret workflows не змінено; container job залишається вимкненим. Віддалені workflows цього етапу не запускалися, push не було.

## Перевірки та межі достовірності

- Python unit discovery: **63 тести, 60 успішних, 3 пропущені** MySQL write integration tests для ізольованого CI. Наявна MySQL не використовувалася для запису.
- Ruff та git diff --check успішні.
- Source checker: лексична цілісність 21 Terraform-файла, inputs/outputs 8 module contracts, відсутність активних backend/cloud/абсолютних module sources; перевірено арифметику 4800 CSV рядків. Це **не Terraform parser, provider validation або plan**.
- YAML active workflows і release draft, JSON OIDC trust templates перевірені. Source hashes 96 оригіналів та 12 архівних файлів перевірені.
- Secret scan перевірив Git candidates, історію та збіг локального DB credential: **0 нерозвʼязаних знахідок**. Для публічного action SHA та перевірених checksum metadata додано адресні пояснені allowlist pragmas; глобальні правила сканера не послаблено. Евристична перевірка не гарантує абсолютної відсутності секретів.
- React, Flask, API, 27 правил HRI та Word-документи не змінено. Повторні browser/frontend перевірки не проводилися, оскільки UI цього етапу не змінювався. Наявне попередження Starlette/httpx у тестах залишилося без несумісного оновлення залежностей.

Машинний підсумок: [checks](reports/aws-ecs-hcp-checks.json). Terraform fmt/init/validate/plan/apply, Docker, HCP runs, AWS provisioning, cloud health/rollback та live IAM не виконувалися. Встановлення нових інструментів не проводилося. Використано доступні локальні ECC terraform-patterns/ADR інструкції, звичайний статичний аналіз, Python, Git та офіційні вебджерела; Graphify/REA не викликалися для цього інфраструктурного завдання.

## Наступні обовʼязкові узгодження

1. Прийняти або змінити ADR 0005, регіон, демонстраційні вікна, budget, eligibility/expiry кредитів, account, HCP organization/project та ролі.
2. Погодити окреме налаштування HCP VCS/OIDC, IAM bootstrap та remote validation/plan; apply потребує окремого підтвердження. Поточний код ще не deployment-ready.
3. Перевірити provider schema і region/class/engine availability; вибрати pinned AMI, digest, DNS та валідований origin ACM certificate; не використовувати placeholder як готову конфігурацію.
4. Підготувати новий MySQL reader, backup/restore/import та client TLS. Поточний клієнт ще не налаштований на перевірений TLS до RDS з require_secure_transport; запуск сервісу до виправлення заблокований. Локальну БД не переносити без дозволу.
5. Для AI потрібні реальний медичний dataset/benchmark, приватний AMI/підписаний release agent, TLS/CA/token і перевірений model contract. Навчання не розпочинати без погодження даних.
6. Перевірити auth/rate limits, deployment health/rollback та runtime CPU/RAM у дозволеному середовищі; окремо погодити Git commit/push і cloud activation.

## Git та перелік файлів

Гілка main, HEAD `4b3033b5e4badcdf2e8a7f4bb87e4c2967c515cb` збережений. Локальний UI-коміт випереджає origin/main на один коміт; AWS-матеріали попереднього та поточного етапів лишаються незакоміченими. Git history не переписувалася, push не виконувався. Origin не змінювався. Поточний diff не слід трактувати як виключно зміни цього запиту: попередній AWS етап уже мав незакомічені файли.

Основні групи змін: 21 Terraform-файл і root README; history з manifests/snapshots; OIDC/release drafts; 3 helper scripts, 2 helper tests; source-only workflow; архітектура/SG/network/ALB/AI/MySQL порівняння, HCP guide, module reuse, ADR 0005, кошторис/CSV, roadmap та індекси документації. Точний список всіх modified/untracked кандидатів робочого дерева наведено в [маніфесті файлів](reports/aws-ecs-hcp-working-files.txt). Він включає й збережену попередню AWS роботу; .env/.venv/.local-verification виключено через чинний .gitignore.
