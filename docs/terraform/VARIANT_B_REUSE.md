# Варіант B: фактичне повторне використання

Джерело лише для читання: `D:/Робота/Codica/golfer2golfer/terraform/modules`. Це адаптація конкретних прочитаних source blocks, не runtime dependency. Усі target sources локальні; сторонній проєкт не змінено, Git-команди в ньому не виконувалися. Версії/provider constraints ClimateHealth збережено. Раніше проведене повне порівняння: [REFERENCE_COMPARISON](REFERENCE_COMPARISON.md).

| Компонент / реальний donor | Target / рішення | Що адаптовано та чому |
|---|---|---|
| `vpc/main.tf`: aws_vpc.main, aws_internet_gateway.this, public_1/private_1 subnets | `modules/networking/main.tf`: aws_vpc.this, gateway, public/private count=2 — ADAPT | Взято source blocks VPC/IGW/subnets; імена/inputs, дві AZ та /24 із /16; явні окремі маршрути/асоціації з ClimateHealth. NAT/bastion/Redis відсутні. SG об’єднано лише після підтвердження відсутності State. |
| `ecs/main.tf`: ECS cluster, Launch Template, ASG, Capacity Provider та association | `modules/ecs-backend/main.tf` — ADAPT | Реально використано структуру цих блоків; прибрано Fargate/Spot/remote-state/SSH; явний approved AMI, t3.small, IMDSv2, encrypted gp3, EBS/EC2 tags. Залишено поточні scoped IAM, listener readiness і HCP-owned task/service. |
| `alb/main.tf`: aws_lb.application, aws_alb_listener.https, aws_alb_target_group.ecs | `modules/alb/main.tf` — ADAPT | LB/listener blocks адаптовано; TG pattern — один bridge/instance target 8080, readiness 200. HTTPS-only, default403, origin header condition і SG prefix-list з ClimateHealth. Без donor redirect/access-log dependencies. |
| `s3/main.tf`: базовий aws_s3_bucket | `modules/frontend/main.tf` — ADAPT | Базові bucket declarations з адаптацією naming/protection; збережено current BPA, encryption, ownership, versioning, TLS deny, CloudFront OAC і SPA/cache logic. Публічний website bucket не переносився. |
| `ecr/main.tf`: repository for_each + immutable images/scanning | `modules/ecr/main.tf` — ADAPT раніше адаптованого donor | Збережено поточну адаптацію, прибрано enabled input та AI repository; один backend repo, immutable/scanning/encryption/prevent_destroy. |
| RDS/CloudFront OAC/SG-to-SG | Поточні `mysql`, `frontend`, `networking` — KEEP CURRENT | RDS MySQL TLS/backup/protection та приватний S3/OAC доречніші за donor PostgreSQL/публічні налаштування. |
| AI EC2, EC2 MySQL, task empty role | REMOVE у цій конфігурації | Збережених State немає; runtime AI ще не готовий, цільова БД RDS. Немає штучних AMI inputs, EBS/backup roles чи task role без permissions. |

Підтвердження походження — коментарі у target і source-to-target diff, а не обіцянка копіювання byte-for-byte. Відповідні donor blocks були прочитані та використані під час генерації адаптованих target. Хеші вихідного reference та application files порівнюються з локальним checkpoint; секрети/state/локальна конфігурація не переносилися.
