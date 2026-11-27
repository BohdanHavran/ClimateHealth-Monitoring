# HCP Terraform — актуальна конфігурація варіанта B

Перед першим запуском: [точні UI variables, очікуваний Plan, кошторис та дії без Apply](terraform/FIRST_HCP_PLAN.md).

Working Directory: `infrastructure/terraform`. Один root, локальні sources `./modules/...`; VCS trigger pattern `/infrastructure/terraform/**` охоплює вкладені модулі. Terraform `>= 1.11.0, < 2.0.0`, AWS Provider `= 6.74.0`. S3 backend і cloud block не потрібні для цього VCS-driven workflow. State залишається у HCP.

Read-only перевірка 26.11.2026: workspace `ClimateHealth-Monitoring` організації `diploma-2025` не має збережених State; Resources 0. Auto Apply вимкнений. Налаштовану користувачем авторизацію не змінено; нових authentication variables не додано. Див. [докази](terraform/STATE_VERIFICATION.md).

`climatehealth-dev` та `climatehealth-production` — майбутні окремі workspaces/state/variables/permissions, а не підтверджені наявні workspaces. Не застосовувати адресний рефакторинг до іншого State без повторної перевірки. Робочі налаштування HCP зараз не змінювалися.

## Terraform variables (повний поточний root contract)

| Input | Default | Призначення |
|---|---|---|
| `environment` | `без default` | Separate HCP workspace environment. |
| `aws_region` | `без default` | Explicitly approve the costed region and regional RDS CA. |
| `vpc_cidr` | `"10.42.0.0/16"` | A /16 IPv4 VPC; four non-overlapping /24 subnets are derived. |
| `deploy_application` | `false` | Create ephemeral API compute/ALB/DNS and its CDN origin; never gates RDS or storage. |
| `backend_desired_count` | `0` | Bootstrap at zero; request one task only after CP association is ready. |
| `backend_max_instances` | `1` | Upper ASG capacity; two is an explicitly approved temporary rolling budget. |
| `backend_image` | `null` | Reviewed digest in this environment's backend ECR repository; CI supplies the digest. |
| `ecs_ami_id` | `null` | Approved AL2023 ECS-optimized x86_64 AMI; replacement/refresh needs review. |
| `origin_hostname` | `null` | Existing DNS hostname covered by the ALB origin certificate. |
| `frontend_domain` | `null` | Optional viewer hostname and existing IAM certificate ID. |
| `origin_certificate_arn` | `null` | Issued ALB ACM certificate ARN with correct DNS SAN/account/region. |
| `origin_verification_header` | `null` | Generate a fresh random URL-safe origin value; never print or commit it. |
| `runtime_secret_arns` | `{}` | SSM ARN references for the RDS reader DB_USER and DB_PASS, never secret values. |
| `permissions_boundary_arn` | `null` | Existing reviewed IAM boundary for application roles; does not change HCP authentication. |

Лише `environment` та `aws_region` не мають default. Для погодженого початкового Plan передаються вони; `deploy_application=false`, task count 0, інші nullable inputs лишаються null. Plan все одно потребує дієвої вже налаштованої AWS-авторизації (caller identity, AZ, CloudFront policies/prefix list). Не вводити випадкових ARN/AMI.

**Початковий Apply створить платні RDS, S3/CloudFront/ECR та інші базові ресурси. False не є no-op чи бюджетним блокуванням.** Manual Apply і review Plan — обов’язкові. Жодних Apply зараз не виконано.

Для `deploy_application=true` потрібні digest власного backend ECR, погоджений ECS-optimized AL2023 AMI, наявні external origin hostname/issued ACM certificate, приватний origin header, SSM DB_USER/DB_PASS reader references та існуюча permissions boundary. Default boundary null не відключає вимогу — validation вимагає її для API. HCP credentials керують provisioning, ці runtime parameters не є новим способом AWS-авторизації.

Sensitive origin header задавати як sensitive HCP variable: нове випадкове URL-safe значення 32–128 символів; не друкувати його. Terraform sensitive приховує звичайний output, але значення все одно захищається контролем доступу до State/plan.

## Володіння deployment

HCP Terraform володіє task definition, service task reference, desired task count, ASG min/max. ECS Capacity Provider володіє ASG desired_capacity (ignore_changes). GitHub Actions тестує/готує digest; публікацію дозволяти окремо. ECS UpdateService/RegisterTaskDefinition з Actions не використовується. Auto Apply лишається Off.

[Bootstrap, завершення демонстрації і ризики](terraform/VARIANT_B_REPORT.md). [Усі root/child variables](terraform/VARIABLES_REFERENCE.md).
