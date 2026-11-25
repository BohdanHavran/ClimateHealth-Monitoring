# ADR 0005: ECS EC2, CloudFront та HCP Terraform

Дата24.11.2026. **HCP/один root прийняті користувачем; ECS small/ALB/RDS та бюджет — рекомендовані, очікують затвердження.** AWS як платформа й чинний стек зберігаються. Замінює state/compute-частини ADR0004; жодної state migration не виконано.

## Контекст
$100 підтверджених кредитів, потрібна відтворювана демонстрація без локального apply. Власні модулі містять корисні патерни, але також PostgreSQL, EOL AL2 AMI, broad SG, mutable tags та drift-ignore. Реальна ML модель і memory benchmark відсутні.

## Рішення
Уточнення структури 25.11.2026 за прямою вказівкою користувача: єдиний root — `infrastructure/terraform`, без зайвої AWS вкладеності. Два HCP workspaces з окремими state/variables/roles зберігають ізоляцію; окремі локальні dev/production roots не потрібні. Деталі перенесення та сумісності inputs — [звіт](../TERRAFORM_ROOT_SIMPLIFICATION.md). Архітектура ресурсів від цього уточнення не змінюється.

Один локальний root і8 modules, HCP VCS-driven workspaces climatehealth-dev/production з незалежними state/phase roles, remote plan та manual apply, auto apply off. GitHub окремо будує/сканує/публікує app/frontend/AI, не виконує Terraform Apply. ECR адаптовано з власного джерела; без зовнішніх runtime paths/секретів.

Рекомендовано ECS EC2 t3.small AL2023, bridge task1024MiB/host reserved512, ASG max1 із чесним downtime або окремо дозволеним max2 для deployment. Private RDS MySQL8.4 Single-AZ, AI off → private t3.small після benchmark. React private S3/OAC/CloudFront PAYG; ALB HTTPS, prefix+header gate, тільки під час погодженого80год демонстраційного вікна. No NAT: backend outbound через host IPv4/IGW, AI private S3 release contract. Це не HA або гарантований zero downtime.

## Альтернативи
Micro: defaulttask не вміщується; не рекомендується. Fargate .25/1: нижчий compute/без host patching, потребує benchmark та іншого network/task implementation, не виключено в майбутньому. Compose безALB дешевший для24/7, але власні TLS/health/rollback. ALB24/7 коштує~$24.31/місяць: якщо постійна доступність стає метою, рішення треба переглянути. NAT Instance дешевша заGW, але SPOF/patching; endpoints не забезпечують Open-Meteo. S3 state відхилено на користь HCP за прямою вказівкою користувача.

## Наслідки та gates
Повний baseline AIoff/RDSpersistent: $24.26/80год або$62.68/730год; із20% $29.12/$75.21. $100 арифметично~3.43 демонстраційних або1.33 безперервних місяця до expiration/непокритих charges. ALB80год вимагає явного manual видалення/створення, не stop; DB/storage лишаються. HCP Free умови та availability перевірити на фактичній organization, AWS credits не оплачують платний HCP автоматично.

Цей код не перевірено Terraform/provider schema, ресурси не створено. Потрібні approved AMI/image, reader credentials/TLS client, domain/ACM/DNS, HCP/IAM bootstrap, data approval/restore, AI agent/CA/token, health/rollback та особисте підтвердження run. Немає нових прогнозів/навчання/змін HRI, MySQL або Word. [Архітектура](../AWS_ARCHITECTURE.md), [кошторис](../AWS_COST_ESTIMATE.md), [HCP](../HCP_TERRAFORM.md), [reuse](../TERRAFORM_MODULE_REUSE.md).
