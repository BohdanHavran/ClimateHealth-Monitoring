# ClimateHealth — HCP Terraform

## Рекомендована організація
Оновлення provider 25.11.2026: provider-level account allowlist вилучено за прямою вказівкою користувача. `aws_account_id` збережено для account-bound перевірок ACM, SSM та permissions boundary ARN; input сам по собі не перевіряє фактичну AWS identity. Окремі exact OIDC trust/phase roles, least privilege, ізоляція state та Manual Apply залишаються обовʼязковими. GitHub deployment action має незалежний account check, який не змінювався. Перед першим дозволеним remote run перевірити account обох HCP role ARNs та їхніх IAM permissions.

Один root `infrastructure/terraform`; VCS repository BohdanHavran/ClimateHealth-Monitoring. Проєкт HCP/organization ще не погоджено, підключення не виконано. Workspaces запропоновано `climatehealth-dev` і `climatehealth-production`, remote execution, окремі state/variables/roles; **Auto Apply=false для обох**. Для поточного VCS-driven сценарію `cloud` block у коді не потрібний: workspace задає джерело й working directory, HCP керує state. CLI-driven integration могла б потребувати cloud block, але вона тут не обрана. Немає S3 backend/state bucket і не виконували state migration.

[Налаштування VCS](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/settings/vcs): після окремого дозволу вибрати repository/main, working directory infrastructure/terraform, Terraform 1.11.4 або окремо перевірену новішу версію, remote execution. Trigger pattern `/infrastructure/terraform/**` охоплює root і вкладені modules; документацію/історичні файли не додавати до trigger. Перевірити PR speculative plan для зміни тільки module та для root. Жодних cross-workspace run triggers/auto production applies.

## Змінні
| Категорія | Значення |
|---|---|
| Terraform | aws_account_id, environment=dev/production, aws_region (обовʼязковий; us-east-1 лише кандидат), owner, name_suffix, permissions_boundary_arn з різними значеннями для workspaces |
| Terraform runtime configuration | ecs_ami_id (AL2023 pinned), backend_image@sha256, origin_hostname, origin_zone_id, origin_certificate_arn, task_memory_mib, database_mode, runtime_secret_arns (тільки SSM ARNs), approved AI/MySQL AMI IDs за потреби |
| Sensitive Terraform | origin_verification_header: новий окремий випадковий value на workspace; Terraform може зберігати його у state, доступ до state мінімальний |
| Безпечні початкові gates | infrastructure_reviewed=false, application_window_open=false, service_enabled=false, ai_enabled=false, allow_deployment_capacity=false |
| HCP environment | TFC_AWS_PROVIDER_AUTH=true, TFC_AWS_PLAN_ROLE_ARN, TFC_AWS_APPLY_ROLE_ARN; окремі значення dev/prod |

Не задавати AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY, root credentials або домашні DB values. HCP managed dynamic credentials не потрібно замінювати файлами credentials у repo. SecureString parameters для runtime створює окрема погоджена адміністративна процедура; Terraform зберігає ARN, а не читає plaintext через data source. RDS master managed secret не передається Flask; потрібний окремий reader account.

## HCP OIDC → AWS
[Офіційна динамічна автентифікація](https://developer.hashicorp.com/terraform/cloud-docs/dynamic-provider-credentials/aws-configuration): issuer app.terraform.io, audience aws.workload.identity. Trust StringEquals для **точних** organization/project/workspace/run_phase. Підготовлено чотири `infrastructure/ci/hcp-{dev,production}-{plan,apply}-trust.json.example`; placeholders замінюються тільки після погодження names/account.

- Dev plan/apply roles не мають доступу до production ARNs або IAM profiles. Production roles окремі; plan phase read-only inventory, apply phase scoped lifecycle permissions.
- Plan role: опис тільки потрібних EC2/ECS/ELB/S3/CF/RDS/IAM resources, без writes. Apply role: лише ресурси ClimateHealth свого environment, region/account constraints, tags, bounded iam:PassRole на execution/task/instance profiles. Створення IAM ролей — тільки із reviewed permissions boundary; не AdministratorAccess/iam:*.
- OIDC provider/bootstrap policies створюються окремою федеративною людиною з MFA після дозволу. Це не робиться поточним root через власні ще неіснуючі credentials.
- GitHub OIDC інший: token.actions.githubusercontent.com, audience sts.amazonaws.com, repo/environment subject. Його release roles мають ECR/S3/CloudFront/ECS permissions, **не** Terraform infrastructure privileges. HCP не використовує GitHub deployment role.

## Plan, apply, drift і state
VCS change → remote speculative/review plan → підтвердження конкретного saved run → manual apply. Не робити другий apply у GitHub Actions. Призначити людей для review/apply з доступними на фактичному plan permissions; не припускати enterprise RBAC. State access не надається всім repo collaborators. Не запускати destroy чи state manipulation автоматично. Усі поточні HCP operations потребують окремого дозволу; не створено workspace/VCS connection/run.

Drift: reviewed refresh/plan у HCP після погодження; автоматичні health assessments та advanced governance залежать від тарифу, тут не налаштовані. Application CD володіє ECS task revisions; lifecycle ignore_changes тільки service.task_definition документує цю межу. Не ігноруються SG/origin/cache/security/AMI changes. Нові task revision зміни HCP service infrastructure повинні перевіряти фактичну current revision, а не мовчки повертати bootstrap image.

## Free Plan і витрати
[Офіційні ліміти HCP](https://developer.hashicorp.com/terraform/cloud-docs/overview), перевірено 24.11.2026: Free до 500 managed resources на organization, 1 concurrent remote run; VCS та remote execution доступні. Обидва workspaces та інші проєкти організації витрачають спільний ліміт. 500 — не кількість блоків у файлах і не гарантія, що акаунт має вільний залишок. Dynamic credentials/Manual Apply не потребують локального apply. Audit logging/custom RBAC/advanced governance, concurrency й автоматичні assessments перевірити в обраному plan; їх не вважаємо безкоштовно налаштованими.

HCP Europe має окремі contract plans; цей Free-сценарій не переноситься туди автоматично. Не активувати trial/upgrade/pay-as-you-go без дозволу. Вартість платного HCP не включена до $100 AWS Credits: це окремий постачальник/рахунок, точну ставку та доступні функції перевірити в organization перед підключенням. Lockfile/checksums мають бути отримані під час майбутнього дозволеного HCP init й зафіксовані окремим review; зараз їх не вигадуємо.

## Workspace variable inventory

Оновлено 25.11.2026. Налаштування UI лише підготовлені, не застосовані. Для **обох** workspaces: Working Directory `infrastructure/terraform`, VCS repository/main, remote execution, Auto Apply **false**, trigger pattern `/infrastructure/terraform/**` (root + вкладені modules). Terraform version має відповідати >=1.11,<2; узгодити конкретну версію перед першим run.

`region` та `account_id` замінено на `aws_region` та `aws_account_id`. Якщо колись було створено старі workspace variables або TF_VAR_region/TF_VAR_account_id, прибрати дублікати та перенести значення вручну після погодження, без state migration. Обидва нові inputs **не мають default**. Валідатор зараз дозволяє тільки кошторисний us-east-1 як кандидат; це не дозвіл на його використання. Інший регіон потребує review validation, ACM та кошторису.

### Terraform Variables — повний перелік root inputs

У HCP UI string inputs вводити як текст; bool/number/list/map позначати HCL. Для optional inputs дозволено залишити defaults із коду. Для sensitive origin header потрібне нове окреме значення кожного середовища, не приклад із документації. Не передавати паролі замість SSM ARN.

| Назва | Тип | Default / обовʼязковість | Sensitive UI |
|---|---|---|---|
| `aws_account_id` | `string` | обовʼязкова; без default | ні |
| `environment` | `string` | обовʼязкова; без default | ні |
| `aws_region` | `string` | обовʼязкова; без default | ні |
| `owner` | `string` | обовʼязкова; без default | ні |
| `name_suffix` | `string` | обовʼязкова; без default | ні |
| `infrastructure_reviewed` | `bool` | `false` | ні |
| `service_enabled` | `bool` | `false` | ні |
| `backend_image` | `string` | обовʼязкова; без default | ні |
| `ecs_ami_id` | `string` | обовʼязкова; без default | ні |
| `backend_instance_type` | `string` | `"t3.small"` | ні |
| `task_memory_mib` | `number` | `1024` | ні |
| `allow_deployment_capacity` | `bool` | `false` | ні |
| `origin_hostname` | `string` | обовʼязкова; без default | ні |
| `origin_certificate_arn` | `string` | обовʼязкова; без default | ні |
| `origin_verification_header` | `string` | обовʼязкова; без default | так |
| `runtime_secret_arns` | `map(string)` | обовʼязкова; без default | ні |
| `database_mode` | `string` | `"rds"` | ні |
| `mysql_ami_id` | `string` | `null` | ні |
| `ai_enabled` | `bool` | `false` | ні |
| `ai_ami_id` | `string` | `null` | ні |
| `ai_instance_type` | `string` | `"t3.small"` | ні |
| `application_window_open` | `bool` | `false` | ні |
| `origin_zone_id` | `string` | обовʼязкова; без default | ні |
| `permissions_boundary_arn` | `string` | обовʼязкова; без default | ні |
| `vpc_cidr` | `string` | `"10.42.0.0/16"` | ні |
| `public_subnet_cidrs` | `list(string)` | `["10.42.0.0/24", "10.42.1.0/24"]` | ні |
| `private_subnet_cidrs` | `list(string)` | `["10.42.10.0/24", "10.42.11.0/24"]` | ні |

### Environment Variables — окремо dev і production

| Назва | climatehealth-dev | climatehealth-production |
|---|---|---|
| `TFC_AWS_PROVIDER_AUTH` | `true` | `true` |
| `TFC_AWS_PLAN_ROLE_ARN` | ARN погодженої dev plan role | ARN погодженої production plan role |
| `TFC_AWS_APPLY_ROLE_ARN` | ARN погодженої dev apply role | ARN погодженої production apply role |

Це category **Environment**, не Terraform. ARN не є секретним ключем; захищати можливість змінювати role/workspace configuration. Реальних ARN тут немає. `TFC_AWS_RUN_ROLE_ARN` не потрібний, якщо задані обидві phase roles. Не додавати AWS access keys, root credentials, profile або власні shared credential files: вони можуть заважати HCP OIDC. Автентифікація перевірена за [офіційним описом HCP](https://developer.hashicorp.com/terraform/cloud-docs/dynamic-provider-credentials/aws-configuration), але реальний trust/assume-role не виконувався.

### Значення, що залишилися фіксованими

Root не отримує неоглядний набір tuning flags. Вхідні CIDRs мають ті самі початкові значення: VPC10.42.0.0/16, public .0/.1 і private .10/.11 по /24; дві AZ, без NAT. Перед зміною CIDRs перевірити containment/non-overlap, а після provisioning — replacement plan. Offline checker перевіряє початкові значення; Terraform validation перевіряє форму та кількість CIDRs, не повний мережевий дизайн.

У mysql module лишаються MySQL8.4.13, db.t4g.micro,20GiB encrypted gp3, Single-AZ,7 днів backup; у frontend — PAYG,PriceClass100,OAC,distribution default certificate; у alb — HTTPS443,health/readiness,30s draining. Їх не змінено при перенесенні та не додано нових значень заради API змінних. Для CloudFront custom domain потрібен окремий review certificate/alias; зараз CloudFront ACM certificate ресурс відсутній, тому додатковий provider alias не потрібний. ALB ACM ARN у us-east-1 відповідає поточному обмеженому регіону.
