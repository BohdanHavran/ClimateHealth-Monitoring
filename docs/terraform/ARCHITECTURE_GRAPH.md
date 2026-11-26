# AWS architecture — поточний варіант B

26.11.2026. Схема вихідного коду, не розгорнутої AWS. Повний статичний граф має 199 вузлів/543 ребра; 55 AWS blocks. Розміщення нижче не визначає Terraform DAG. [Точні залежності](DEPENDENCY_GRAPH.md).

```mermaid
flowchart TB
  root["Root infrastructure/terraform: 15 inputs"]
  root --- net["networking: VPC, routes, 3 SG"]
  net --- public["2 public subnets + IGW"]
  net --- private["2 private subnets, без default internet route"]
  net --- gateway["S3 Gateway endpoint"]
  root --- registry["ecr: 1 backend repository"]
  root --- frontend["frontend: 2 private S3, OAC, CloudFront"]
  root --- db["mysql: RDS MySQL Single-AZ, TLS, backup"]
  root --- logs["Retained CloudWatch log group"]
  root --- alb["alb: HTTPS ALB, TG, listener, header rule"]
  root --- ecs["ecs-backend: ECS, LT, ASG, CP, task/service"]
  public --- alb
  public --- host["Public t3.small, bridge8080 to container8000"]
  ecs --- host
  private --- db
```

networking/ecr/frontend/mysql/logs завжди присутні в конфігурації. alb/backend та origin DNS лише deploy_application=true; CloudFront тоді додає API origin. AI/EC2 MySQL/security module відсутні; 3 SG та6rules належать networking. CloudFront + bucket policies, IAM policies та task definition залежать від конкретних outputs; точний source граф показує ці ребра, а не штучну послідовність VPC→SG→ALB→ECS для всіх блоків.

ASG керує host EBS/ENI/EC2, ECS CP — managed alarms/scaling; RDS керує master secret. Ці service-managed objects не видаються за додаткові Terraform blocks. Модель/AI runtime відкладені. [Reuse matrix](VARIANT_B_REUSE.md), [runbook](VARIANT_B_REPORT.md).
