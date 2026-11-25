# ClimateHealth — один HCP Terraform root

**Review code, не запущена й не перевірена Terraform інфраструктура.** Не запускати локально Terraform/Docker. HCP VCS connection/runs/apply також потребують окремого дозволу. Не створювали state або AWS-ресурсів.

```
infrastructure/terraform/
  main.tf                 # 8 local module calls, review gate, origin DNS alias
  provider.tf             # hashicorp/aws=6.74.0, region input, no static credentials
  variable.tf             # typed workspace inputs and safe gates
  output.tf               # non-sensitive endpoints/identifiers/reviewed task handoff
  modules/
    networking/
    security/
    ecr/                  # directly adapted owner module, provenance documented
    alb/
    frontend/             # private frontend/artifact S3, OAC, CloudFront/cache/SPA rules
    ecs-backend/           # AL2023 LT, ASG/CP, IAM, task/service/logs
    mysql/                 # RDS8.4 or private approved EC2 MySQL AMI
    ai/                    # optional private CPU EC2 / signed S3 release AMI contract
```

Дві запропоновані workspaces climatehealth-dev і climatehealth-production використовують цей самий root, різні state/variables/account roles. Немає environments/*, backend S3 або cloud block для обраного VCS-driven workflow. Старий AWS scaffold збережено точно в ../../docs/history/terraform-aws-20261124/aws-ec2-s3-state-20261124/**/*.historical; не є другим root. Не мігрували/видаляли будь-який state. Архівні інструкції не є командами до виконання.

Рекомендований режим: ECS t3.small bridge/public host outbound, ALB ingress (CloudFront prefix+header), MySQL RDS private, AI off, no NAT. Root не реалізує всі 4800 вартісних альтернатив: Fargate/Compose/NAT/AI capacity provider — порівняння, а не готові switch flags. Контрольоване app window може видаляти ALB/service/DNS alias через окремо reviewed manual HCP apply; RDS/network/storage лишаються. Звичайне service_enabled=false не прибирає ALB/RDS fees.

Дефолти: infrastructure_reviewed=false, application_window_open=false, service_enabled=false, ai_enabled=false, allow_deployment_capacity=false. Це не нульова ціна майбутнього apply: root містить RDS/storage, які можуть оплачуватися навіть без app window. Дозвіл на код ≠ дозвіл на запуск. Відкриті readiness gates: approved account/region/credits, globally unique suffix, existing DNS zone/validated origin ACM certificate, pinned AL2023 AMI/image digest, DB reader/TLS/restore/import, runtime SSM ARN references, AI signed-release agent/AMI/token/CA. Немає image builds, PyTorch model або клінічних результатів.

[HCP/OIDC](../../docs/HCP_TERRAFORM.md), [архітектура](../../docs/AWS_ARCHITECTURE.md), [cost matrix](../../docs/AWS_COST_ESTIMATE.md), [module provenance](../../docs/TERRAFORM_MODULE_REUSE.md), [CI/CD](../../docs/CI_CD_PIPELINE.md). Синтаксис/SDK schema, Terraform fmt/validate/plan та реальні deployment health/rollback ще не перевірено; .terraform.lock.hcl не вигадується.

## Provider та workspace inputs

`provider.tf` використовує aws_region без default, Terraform >=1.11,<2, AWS =6.74.0 і default_tags (Project/Environment/ManagedBy/Owner). Provider-level account guard прибрано за рішенням користувача; aws_account_id залишається обовʼязковим для перевірок ACM/SSM/IAM ARN, але не перевіряє фактичний account credentials. Доступ обмежують HCP OIDC exact trust, окремі dev/production phase roles, least-privilege permissions та review run identity. HCP dynamic OIDC надає credentials через environment, без access keys/profile у коді. Регіон не затверджено: validator тимчасово дозволяє лише кошторисний кандидат us-east-1; інший регіон потребує окремого review. CloudFront використовує стандартний distribution certificate; ALB потребує наявного ACM certificate у регіоні backend, тому зайвий alias не потрібний.

Root inputs `region` → `aws_region`, `account_id` → `aws_account_id`: у HCP UI використовувати нові назви, видалити старі дублікати перед першим run. Child backend input `region` збережено; outputs і resource/module labels незмінні. VPC/subnet CIDRs тепер явні inputs з попередніми defaults; їх зміну після provisioning не вважати безпечним перейменуванням. RDS class/engine/storage/retention, CloudFront PAYG/PriceClass100 і ALB HTTPS/health/drain налаштування залишено фіксованими в модулях для збереження архітектури та кошторису. [Повний HCP UI inventory](../../docs/HCP_TERRAFORM.md#workspace-variable-inventory).

Старих aws/, dev/, production/, history/, backend.tf і сторонніх provider scaffolds у цьому root немає. Архіви поза ним: [legacy](../../docs/history/terraform-legacy-20261125/) і [попередній AWS](../../docs/history/terraform-aws-20261124/). Історичні звіти з попередніми шляхами не є поточними інструкціями. [Звіт перенесення](../../docs/TERRAFORM_ROOT_SIMPLIFICATION.md).
