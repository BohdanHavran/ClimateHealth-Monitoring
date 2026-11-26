# ClimateHealth — Terraform через HCP

> Оновлення 26.11.2026: [поетапне розгортання](terraform/CONTROLLED_DEPLOYMENT.md) замінює попередні вимоги всіх runtime inputs на першому Plan. Лише environment/aws_region/name_suffix required; gates лишаються false до review. HCP володіє ECS task revisions; direct ECS deployment example лишається disabled. Авторизацію HCP не змінювати.

## Поточне уточнення 25.11.2026

За повідомленням користувача HCP уже підключений до repository/root і AWS-авторизація налаштована окремим способом. Повторне підключення або нові authentication variables не потрібні через сам факт аудиту. Owner variable/tag прибрано, ручний aws_account_id замінено caller identity data source у трьох ARN-перевірках. [Актуальний повний аудит](terraform/AUDIT_REPORT.md), [поточні inputs](HCP_TERRAFORM.md), [як працює run](terraform/HOW_TERRAFORM_WORKS.md). HCP configuration/Plan/Apply не змінювали й не запускали.

Наведений нижче початковий план підключення збережено як контекст попереднього етапу; він не є вимогою замінювати вже налаштовану користувачем авторизацію. Поточний root має 22 .tf файли, 25 root variables та 11 required inputs. Нові локальні зміни ще не відправлені в GitHub.

## Попередня підготовка та незмінні правила review

Єдиний активний root: infrastructure/terraform, з main.tf/provider.tf/variable.tf/output.tf та8 локальними модулями. State/plan/manual apply — HCP Terraform. Немає S3 state bucket, backend.tf або зайвого cloud block. Workspaces dev/production розділені за state, variables та exact workspace/run-phase IAM trust; Auto Apply=false для обох. [Повний runbook](HCP_TERRAFORM.md).

Попередній незакомічений AWS EC2/S3-state scaffold збережено байт у байт у docs/history/terraform-aws-20261124/aws-ec2-s3-state-20261124 з manifest SHA256 і .historical suffix. Backend examples/старий S3 state policy не є активними. Старий каркас іншої платформи прибрано з root після byte-exact архівації у docs/history/terraform-legacy-20261125 (*.historical); у поточному root залишено лише AWS. Жоден state не змінювали/копіювали/мігрували; не припускаємо його існування без окремої перевірки.

Власні модулі джерела проаналізовано; тільки ECR адаптовано безпосередньо, решта потрібних AWS-компонентів спрощені/реалізовані заново, runtime зовнішніх Windows paths немає. [Матриця повторного використання](TERRAFORM_MODULE_REUSE.md). Provider6.74.0 pinned, modules>=6.74,<7, Terraform>=1.11,<2. Lockfile/checksums не створювали, provider не встановлювали.

Порядок після дозволу:
1. Переглянути source diff/ADR0005/cost, затвердити account/region/credits/domain/AMI/database/RPO та HCP organization/project/workspace names.
2. Підготувати OIDC provider/4 scoped phase roles і окремі GitHub release roles без AdministratorAccess, через federated bootstrap з MFA. Поточний root цього доступу ще не створює.
3. Лише після дозволу підключити VCS root, workspace variables, remote execution/version, trigger root+modules, manual apply, permissions/state isolation. Ніяких auto applies або автоматичного destroy.
4. Лише після дозволу виконати HCP init/fmt/schema/module validation/speculative plan, отримати справжній lockfile, переглянути resource diff/кошторис. Поточні lexical/module-contract checks не замінюють Terraform validate.
5. Перед реальним apply — ще окреме підтвердження конкретного run/plan, backup/restore/data licence і runtime prerequisites. Docker image build та Linux smoke також відкладені до дозволу.
6. Перевірити private DB/AI, origin protection, deployment/rollback, quotas/timestamps/модель unavailable; потім погоджена демонстрація. Локальна MySQL не експортується/не мігрується автоматично.

GitHub Actions виконує application release та незалежні source checks; Terraform state/plan/apply не дублює. Код не розгортає Compose/Fargate/NAT alternatives; їхні costs/limitations позначені в матриці. `application_window_open=false` після активного deployment означає reviewed видалення ALB/service/DNS alias; до такого plan потрібне окреме погодження. База не видаляється, deletion protection/final snapshot зберігаються.

У цьому завданні Terraform/Docker/HCP/AWS provisioning не виконано. Підготовлено self-contained code та документи для review, не гарантію успішного apply.
