# ClimateHealth — спрощення Terraform root та AWS Provider

25.11.2026. Виконано фактичне перенесення; без Terraform/Docker, HCP runs, AWS provisioning, зміни state або Git push. Гілка main, збережено HEAD 4b3033b та всі попередні незакомічені AWS-матеріали.

## Результат і дерево

Єдиний активний root — `infrastructure/terraform`. Два HCP workspaces climatehealth-dev / climatehealth-production використовують однаковий код, але незалежні state, inputs та phase IAM roles. AWS — єдина платформа, тому окремий рівень aws не потрібний; дублювання dev/production каталогів також не потрібне.

```text
infrastructure/terraform/
  main.tf
  provider.tf
  variable.tf
  output.tf
  README.md
  modules/
    networking/   main.tf, terraform.tf
    security/     main.tf, terraform.tf
    ecr/          main.tf, terraform.tf, variable.tf
    alb/          main.tf, terraform.tf
    frontend/     main.tf, terraform.tf
    ecs-backend/  main.tf, terraform.tf
    mysql/        main.tf, terraform.tf
    ai/           main.tf, terraform.tf
```

Разом 21 Terraform-файл і README, 8 локальних модулів. Старої вкладеності, backend, історії або іншого провайдера всередині root більше немає. .terraform.lock.hcl не вигадувався: для його отримання потрібен окремо дозволений init у відповідному середовищі.

## Перенесені файли

Нижче повний перелік 22 переміщених файлів. Джерела в таблиці є історією цієї операції, не поточними інструкціями HCP.

| Було | Стало |
|---|---|
| `infrastructure/terraform/aws/main.tf` | `infrastructure/terraform/main.tf` |
| `infrastructure/terraform/aws/output.tf` | `infrastructure/terraform/output.tf` |
| `infrastructure/terraform/aws/provider.tf` | `infrastructure/terraform/provider.tf` |
| `infrastructure/terraform/aws/README.md` | `infrastructure/terraform/README.md` |
| `infrastructure/terraform/aws/variable.tf` | `infrastructure/terraform/variable.tf` |
| `infrastructure/terraform/aws/modules/ai/main.tf` | `infrastructure/terraform/modules/ai/main.tf` |
| `infrastructure/terraform/aws/modules/ai/terraform.tf` | `infrastructure/terraform/modules/ai/terraform.tf` |
| `infrastructure/terraform/aws/modules/alb/main.tf` | `infrastructure/terraform/modules/alb/main.tf` |
| `infrastructure/terraform/aws/modules/alb/terraform.tf` | `infrastructure/terraform/modules/alb/terraform.tf` |
| `infrastructure/terraform/aws/modules/ecr/main.tf` | `infrastructure/terraform/modules/ecr/main.tf` |
| `infrastructure/terraform/aws/modules/ecr/terraform.tf` | `infrastructure/terraform/modules/ecr/terraform.tf` |
| `infrastructure/terraform/aws/modules/ecr/variable.tf` | `infrastructure/terraform/modules/ecr/variable.tf` |
| `infrastructure/terraform/aws/modules/ecs-backend/main.tf` | `infrastructure/terraform/modules/ecs-backend/main.tf` |
| `infrastructure/terraform/aws/modules/ecs-backend/terraform.tf` | `infrastructure/terraform/modules/ecs-backend/terraform.tf` |
| `infrastructure/terraform/aws/modules/frontend/main.tf` | `infrastructure/terraform/modules/frontend/main.tf` |
| `infrastructure/terraform/aws/modules/frontend/terraform.tf` | `infrastructure/terraform/modules/frontend/terraform.tf` |
| `infrastructure/terraform/aws/modules/mysql/main.tf` | `infrastructure/terraform/modules/mysql/main.tf` |
| `infrastructure/terraform/aws/modules/mysql/terraform.tf` | `infrastructure/terraform/modules/mysql/terraform.tf` |
| `infrastructure/terraform/aws/modules/networking/main.tf` | `infrastructure/terraform/modules/networking/main.tf` |
| `infrastructure/terraform/aws/modules/networking/terraform.tf` | `infrastructure/terraform/modules/networking/terraform.tf` |
| `infrastructure/terraform/aws/modules/security/main.tf` | `infrastructure/terraform/modules/security/main.tf` |
| `infrastructure/terraform/aws/modules/security/terraform.tf` | `infrastructure/terraform/modules/security/terraform.tf` |

Усі module sources залишилися `./modules/<name>`, тому після спільного перенесення root і modules вони вказують правильно. file()/templatefile()/path.module references у вихідному активному коді відсутні: зовнішніх policy/templates/scripts file paths для перепривʼязки немає. Вбудовані jsonencode/user_data/CloudFront function bodies збережено.

## Прибрані зайві файли та захист матеріалів

Перед змінами збережено локальний snapshot 47 файлів та SHA256 у `.local-verification/terraform-root-before-20261125/`, виключений із Git. Вісім старих файлів іншої платформи та попередній entry-point README (9 файлів) архівовано з byte-exact перевіркою в `docs/history/terraform-legacy-20261125/`; розширення `.historical` виключає виконання як Terraform. Прибрано з активного root:

- `backend.spaces.hcl.example`
- `backend.tf`
- `main.tf`
- `outputs.tf`
- `providers.tf`
- `README.md`
- `terraform.tfvars.example`
- `variables.tf`
- `versions.tf`

Старий AWS history (16 файлів) перенесено без змін у `docs/history/terraform-aws-20261124/`. У ньому лишився єдиний історичний підкаталог aws-ec2-s3-state-20261124 з manifest та неактивними файлами. Усі 25 архівних файлів порівняно з початковими хешами. Це збереження унікальних незакомічених матеріалів поза активною робочою структурою, а не їх безповоротне видалення. Поточні Terraform файли старої платформи прибрано; дубліката root або runtime звʼязку з архівом немає. Git history не змінено. Сторонній golfer2golfer не змінювався.

## AWS Provider

Фактичний provider.tf:

```hcl
terraform {
  required_version = ">= 1.11.0, < 2.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 6.74.0"
    }
  }
}
# VCS-driven HCP workspaces own state; intentionally no backend/cloud block.
provider "aws" {
  region              = var.aws_region
  allowed_account_ids = [var.aws_account_id]
  default_tags {
    tags = {
      Project     = "ClimateHealth"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = var.owner
    }
  }
}

```

Versions залишено >=1.11,<2 та AWS =6.74.0. Account allowlist збережено; credentials/profile/assume_role/access keys у provider відсутні. default_tags застосовуються до ресурсів із підтримкою tagging; ManagedBy приведено до Terraform (раніше HCP-Terraform), що під час майбутнього plan може створити tag-only diff. Реальне OIDC trust/assume-role не виконувалося.

CloudFront використовує default distribution certificate, а ALB — наявний регіональний ACM certificate, переданий input. Current region validator обмежує кандидат us-east-1; додаткового provider alias не потрібно. Регіон тепер **не має default**: користувач має явно погодити значення. Для іншого регіону або custom CloudFront domain знадобиться окремий перегляд ACM/alias/cost конфігурації.

Provider конфігурацію звірено з [офіційним описом AWS provider v6.74.0](https://raw.githubusercontent.com/hashicorp/terraform-provider-aws/v6.74.0/website/docs/index.html.markdown), [HCP AWS dynamic credentials](https://developer.hashicorp.com/terraform/cloud-docs/dynamic-provider-credentials/aws-configuration) та [HCP VCS settings](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/settings/vcs). Це перевірка документації, не запуск provider.

## Inputs та сумісність

Навмисні зміни конфігурації під час перенесення:

- Root `region` → `aws_region`, `account_id` → `aws_account_id`; у HCP UI потрібні нові назви. Обидва без default. Child backend input region збережено і отримує var.aws_region. Outputs і всі module/resource labels незмінні, moved blocks не потрібні; state migration не виконувалася.
- Додано перевірки owner, AMI IDs, origin DNS/ACM/account, SSM ARN/account/region, hosted zone, permissions boundary та optional AI/MySQL prerequisites. Validation не перевіряє існування чи права AWS обʼєктів.
- CIDRs винесено в 3 явні inputs з **тим самим** VPC/subnet адресним планом. Схема та кількість subnet не змінюються при defaults; containment/non-overlap початкових значень перевірено Python ipaddress. Інші CIDRs перед використанням потребують review, після deployment можуть вимагати replacement.
- ManagedBy tag приведено до наданого користувачем значення Terraform. ECS, ALB, CloudFront, RDS, security та AI поведінку не перепроєктовано.

Збережено 69 декларацій ресурсів з однаковими labels і module paths, всі root outputs; 17 з 21 переміщених .tf файлів залишилися byte-exact. Змінено тільки root main/provider/variables і networking main; README адаптовано до нового місця. Нові optional child networking inputs мають старі defaults; решта child contracts незмінні. Gates infrastructure_reviewed/application_window_open/service_enabled/ai_enabled/allow_deployment_capacity залишилися false.

[HCP variable inventory](HCP_TERRAFORM.md#workspace-variable-inventory) містить усі **27** Terraform inputs, типи, defaults і sensitive flags. Обовʼязкові без default:

`aws_region`, `aws_account_id`, `environment`, `owner`, `name_suffix`, `backend_image`, `ecs_ami_id`, `origin_hostname`, `origin_certificate_arn`, `origin_verification_header`, `runtime_secret_arns`, `origin_zone_id`, `permissions_boundary_arn`.

Environment variables окремо для dev/production: TFC_AWS_PROVIDER_AUTH=true, TFC_AWS_PLAN_ROLE_ARN, TFC_AWS_APPLY_ROLE_ARN. Реальні role ARNs, токени, credentials, AMIs та домени не вигадувалися. Environment має бути dev або production.

## HCP, CI та актуальні інструкції

Working Directory обох workspaces: **infrastructure/terraform**; trigger pattern **/infrastructure/terraform/** включає root і modules. Auto Apply=false, state/plan/manual apply виключно HCP. S3 backend/cloud block не додано. VCS connection та workspaces фактично не налаштовувалися.

`.github/workflows/terraform-ci.yml` виконує тільки `python scripts/check_infrastructure_sources.py` з кореня repository; BASE у скрипті тепер infrastructure/terraform. Перевірки розширено: один root, provider versions/account guard, оголошені root/child variables, required child inputs, false gates, повнота HCP variable inventory. GitHub Terraform apply не створено. Неактивний application-release.yml.example не має старих Terraform paths; container jobs лишаються вимкненими. Віддалений CI не запускався, push не було.

Оновлено AWS_ARCHITECTURE, INFRASTRUCTURE, TERRAFORM_GUIDE, HCP_TERRAFORM, CI_CD_PIPELINE, ROADMAP, root README, ADR0005, ARCHITECTURE, TECH_STACK_DECISIONS і TERRAFORM_MODULE_REUSE. Попередні AWS_ECS_HCP_REPORT/AWS_MIGRATION_REPORT, reports та docs/history збережено як історичні snapshots, без механічного переписування старих шляхів.

## Перевірки

Підсумкові результати записуються у [машинний звіт](reports/terraform-root-migration.json). Виконуються лише статичні перевірки: source lexical/module contracts, збереження декларацій/outputs/архівів, YAML, Markdown links, Ruff, git diff --check та secret scan candidates/history. Вони не замінюють Terraform parsing/provider schema/plan. Повторні application/browser/ML тести не потрібні для цього перенесення: код застосунку не змінювався.

Фактичні результати: source checker PASS (21 .tf,8 module contracts,27 inputs,4800 рядків незмінного кошторису); усі 69 resource declarations та root outputs/module labels збережено. Defaults CIDR containment/non-overlap PASS; 25 архівних файлів та 17 незмінених перенесених файлів звірено за хешами. Чотири контрольні негативні сценарії checker відхилив: зайвий aws каталог, відсутній account guard, відсутній required child input, відкритий AI gate. YAML 4 workflows/drafts PASS, container/release jobs вимкнені; посилання 13 актуальних документів PASS, Ruff і git diff --check PASS. Сканер перевірив 223 Git candidates та історію, включно з локальним exact credential check: 0 знахідок; локальні values не виводилися. Евристичний scan не є абсолютною гарантією відсутності секретів. Нові глобальні allowlists не додавалися.

## Перед першим дозволеним Remote Plan

Погодити account/region/HCP organization/project/конкретну Terraform version; підготувати окремі plan/apply IAM roles, точні OIDC trust subjects, permissions boundary та bootstrap permissions. Задати 13 required Terraform inputs і 3 environment variables окремо у workspaces, підтвердити AMI/platform, ECR digest, DNS/ACM, DB reader/TLS/restore та runtime SSM ARNs. Невідомі значення не заповнювати демонстраційними credentials.

З infrastructure_reviewed=false precondition навмисно зупиняє plan: зміна цього gate потребує виконаного review та окремо дозволеного run, не означає дозвіл apply. Інші gates лишити закритими до runtime readiness. Потрібні справжні init/provider checksum/lockfile, HCL/schema validation і review конкретного remote plan. Поточна робота цього не виконувала. Не змінювати state чи запускати локальні Terraform/Docker команди.

Git: main, HEAD 4b3033b5e4badcdf2e8a7f4bb87e4c2967c515cb, випереджає origin/main на один попередній коміт. Поточні AWS та migration зміни незакомічені, старі tracked scaffolds показані як видалення/заміна з byte-exact архівом. Немає commit/push цього етапу або переписування історії. Backend/frontend/ML/HRI/MySQL/Word та хмарні ресурси не змінювалися.
