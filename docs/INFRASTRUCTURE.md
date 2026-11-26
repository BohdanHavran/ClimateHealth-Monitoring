# ClimateHealth infrastructure

Актуальна реалізація — [варіант B](terraform/VARIANT_B_REPORT.md), єдиний root `infrastructure/terraform`. Шість модулів: networking (включно SG), ecr, frontend, mysql, alb, ecs-backend. RDS-only, private S3/OAC/CloudFront, API ALB→ECS EC2t3.small без NAT. AI не provisioned. Наявна програма/27HRIrules не змінені.

State/Plan/Apply — HCP, application tests/image handoff — GitHub Actions. [HCP variables](HCP_TERRAFORM.md), [архітектура](terraform/ARCHITECTURE_GRAPH.md), [мережа](terraform/NETWORK_GRAPH.md), [безпека/ризики/витрати](terraform/VARIANT_B_REPORT.md), [джерела адаптації](terraform/VARIANT_B_REUSE.md).

Немає збереженого State у перевіреному workspace, але це не доказ відсутності unmanaged AWS resources. Розгортання не виконано. Manual Apply залишається обов’язковим, Auto Apply Off; HCP auth/workspaces не змінювалися. Для інших State потрібна окрема перевірка перед адресним рефакторингом. Старі scaffolds у docs/history — не активні roots.
