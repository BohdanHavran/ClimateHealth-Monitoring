# ClimateHealth — AWS infrastructure index

> Оновлення 26.11.2026: [поетапне розгортання](terraform/CONTROLLED_DEPLOYMENT.md) замінює попередні вимоги всіх runtime inputs на першому Plan. Лише environment/aws_region/name_suffix required; gates лишаються false до review. HCP володіє ECS task revisions; direct ECS deployment example лишається disabled. Авторизацію HCP не змінювати.

Останній [детальний аудит](terraform/AUDIT_REPORT.md): усі ресурси/змінні, Mermaid/DOT dependency та traffic graphs, required inputs і витрати. Owner/manual account inputs видалено локально, ARN checks використовують caller identity. HCP VCS та авторизацію вже налаштовано користувачем; вони не змінювалися. Історичні звіти нижче не є описом поточного credential setup.

Структуру спрощено 25.11.2026: [поточний звіт](TERRAFORM_ROOT_SIMPLIFICATION.md), [root README](../infrastructure/terraform/README.md). Старі звіти фіксують стан на дату написання; їхні колишні шляхи не є інструкціями для HCP.

Актуальний [ADR0005](adr/0005-ecs-cloudfront-hcp-terraform.md): ECS EC2 Small/ASG/CP, private MySQL RDS, AI off/optional private CPU EC2, private S3+CloudFront OAC, ALB лише погоджене demo window, no NAT. [Architecture + SG/NAT/AI/DB](AWS_ARCHITECTURE.md), [cost matrix](AWS_COST_ESTIMATE.md), [module reuse](TERRAFORM_MODULE_REUSE.md), [HCP workspaces/OIDC](HCP_TERRAFORM.md), [application CI/CD](CI_CD_PIPELINE.md), [Terraform guide](TERRAFORM_GUIDE.md).

Один самодостатній root infrastructure/terraform. State/remote plan/manual apply — HCP, Auto Apply=false, без S3 state bucket/cloud block для VCS workflow. Попередній AWS root збережений у docs/history/terraform-aws-20261124/**/*.historical; існуючий state не чіпали. Програмний код/дизайн/HRI/локальнаMySQL/Word незмінні; AWS/HCP/Docker/Terraform execution та push не виконувалися. Каркас не пройшов Terraform/schema/runtime checks.
