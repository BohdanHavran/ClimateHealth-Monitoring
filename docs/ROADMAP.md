# Диплом — дорожня карта ClimateHealth

> Оновлення 26.11.2026: [поетапне розгортання](terraform/CONTROLLED_DEPLOYMENT.md) замінює попередні вимоги всіх runtime inputs на першому Plan. Лише environment/aws_region/name_suffix required; gates лишаються false до review. HCP володіє ECS task revisions; direct ECS deployment example лишається disabled. Авторизацію HCP не змінювати.

24.11.2026. Зберігаються виконані фази1–3, React redesign4b3033b, Flask/MySQL/API/27HRI rules та ML unavailable boundary. GitHub main; push не дозволений поточним завданням.

## Підготовлено
- Доступні28 власних модулів перевірені; ECR безпосередньо адаптовано, решта потрібних компонентів спрощені. Оригінали незмінні.
- Один AWS root і8 локальних модулів: ECS EC2/ASG/CP, ALB, private S3/OAC/CF, private MySQL, optional CPU AI, SG/VPC.
- HCP dev/production design, exact phase OIDC trust examples, VCS trigger root+modules, Auto Apply=false; не підключено/не запускалося.
- 4800 offline cost combinations80/730год, ECSmicro/small/Fargate/Compose, ALB/DB/AI/NAT/endpoints/CF alternatives й limitations.
- Application release draft (не активний), source-only GitHub infrastructure checks, offline ECS revision helper/tests, ML unavailable packaging без моделі.

## Наступні gates
1. Затвердити ECSsmall/ALB demo window/RDS/AIoff, us-east-1 та data residency, gross monthly budget$35 й credit eligibility/expiration. Альтернативу Compose безALB для24/7 можна обрати після зміни пріоритету.
2. HCP VCS/root та авторизація вже налаштовані користувачем; не замінювати спосіб доступу. Перевірити потрібні workspace inputs і scope існуючих permissions у своєму середовищі. Аудит не змінює configuration й не запускає HCP. Повний [розбір](terraform/AUDIT_REPORT.md) та [required inputs](terraform/REQUIRED_VARIABLES_AUDIT.md).
3. Після дозволу HCP init/fmt/schema/plan, справжній lockfile, module/policy tests; Linux Docker builds/image scans; жодних локальних Terraform/Docker зараз.
4. Approved AL2023 AMI/image digest, domain/Route53/ACM, runtime SSM reader, MySQL TLS client support, дозволені дані/backup/restore, AI AMI agent/CA/token. Вони блокують реальний запуск, не маскуються успішною source перевіркою.
5. Окреме схвалення конкретного remote plan перед apply; application CI/CD activation після image/health/rollback tests. Application release не робить Terraform apply.
6. Benchmark micro/small/Fargate та реального CPU AI за погодженим протоколом; max2 deployment capacity тільки з бюджетом. Немає zero-downtime гарантії на одному host.
7. Узгоджений app window: manual HCP ALB/service lifecycle, RDS/storage persistent. Budgets не hard cap, стопtasks не припиняє ALB/RDS fees. Ніякого auto-destroy.

## Науковий напрям
Валідація HRI й provenance історії; погодження легального медичного target/territory/available_at; baselines→MLP із chronological split/fit-only-train. Немає погодженої медичної цілі чи дозволу training. PyTorch модель не створено, model_unavailable чесний. Word/локальнаMySQL не змінюються.

Поточна структура після перенесення 25.11.2026: один root `infrastructure/terraform`, `aws_region`/`aws_account_id` обовʼязкові без defaults; HCP trigger `/infrastructure/terraform/**`, Auto Apply=false. Наступне — погодження account/region/HCP organization, IAM/AMI/DNS/DB prerequisites, потім окремо дозволений remote plan. [Звіт перенесення](TERRAFORM_ROOT_SIMPLIFICATION.md).

Повний стан: [попередній ECS/HCP report](AWS_ECS_HCP_REPORT.md), [architecture](AWS_ARCHITECTURE.md), [cost](AWS_COST_ESTIMATE.md), [HCP](HCP_TERRAFORM.md).
