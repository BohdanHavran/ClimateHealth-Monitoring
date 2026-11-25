# ClimateHealth — ECS / CloudFront / NAT: AWS Cost Analysis

24.11.2026, us-east-1, USD, Linux/x86 On-Demand. Це розрахунки, не рахунок AWS і не виміряний workload. $100 — єдині підтверджені кредити; eligibility/expiration/залишок акаунта не перевіряли. Free Tier allowances не віднімаються автоматично. Податки, домен, платний HCP та GitHub minutes — окремо.

## Повні базові сценарії
Усі рядки: S3+CloudFront PAYG, ALB, приватна RDS MySQL, AI off, no NAT. Для 80год backend/ALB працюють80год, **БД залишається730год**, storage весь місяць. ALB не можна stop:80год можливі тільки при окремо погодженому manual HCP плані створення/видалення ALB у межах вікна; зупинка задач сама не економить його оплату.

| Backend | 80год | +20% | 730год | +20% |
|---|---:|---:|---:|---:|
| ECS EC2 t3.micro (не пройшов RAM gate) | $23.41 | $28.09 | $55.07 | $66.08 |
| ECS EC2 t3.small | $24.26 | $29.12 | $62.68 | $75.21 |
| Fargate .25vCPU / .5GiB | $21.94 | $26.32 | $54.85 | $65.83 |
| Fargate .25vCPU /1GiB | $22.12 | $26.54 | $56.48 | $67.77 |
| Fargate .5vCPU /1GiB | $22.93 | $27.51 | $63.87 | $76.64 |
| EC2 Compose t3.small з ALB | $24.26 | $29.12 | $62.68 | $75.21 |

ECS small рекомендовано як навчально-інфраструктурний варіант, не як математично найдешевший compute. Fargate .25/1 може бути дешевшим, але memory/cold-start невідомі. Micro з reserved512 і task1024 фізично не вміщується; його ціна не означає працездатність. CPU ECS/Compose — burst credits Standard; Fargate — fixed allocation. RAM для реальної PyTorch моделі не виміряна.

## Рекомендований ECS small: складові
| Стаття | 80год | 730год |
|---|---:|---:|
| backend_compute | $1.6640 | $15.1840 |
| backend_ebs | $1.6000 | $1.6000 |
| backend_ipv4 | $0.4000 | $3.6500 |
| alb_hourly_lcu_ipv4 | $2.6640 | $24.3090 |
| mysql_compute | $11.6800 | $11.6800 |
| mysql_storage | $2.3000 | $2.3000 |
| rds_managed_secret | $0.4050 | $0.4050 |
| s3_storage_requests | $0.1240 | $0.1240 |
| cloudfront_delivery | $0.9500 | $0.9500 |
| cloudfront_functions | $0.0010 | $0.0010 |
| ecr_5gb | $0.5000 | $0.5000 |
| cloudwatch | $0.8300 | $0.8300 |
| snapshots_10gb | $0.5000 | $0.5000 |
| dns_reserve | $0.5000 | $0.5000 |
| non_cdn_transfer | $0.0900 | $0.0900 |
| deployment_surge | $0.0560 | $0.0560 |

RDS managed secret: $0.40/secret-month + умовні1000 API calls $0.005. DB20GB gp3,7днів backup; без надлишку RDS backup allowance, без Extended Support/CPU overage у baseline. EC2 MySQL alternative — **окремий** private t3.small30GB, не безкоштовна БД на micro host. У матриці db_schedule=persistent рахує DB730год, with_backend рахує80/730 compute; storage/secret завжди повний місяць. RDS автоматично стартує після7днів stop, тому scheduled row не є гарантією економії без окремого контролю.

Для ECS small + RDS при узгоджених80год DB compute: $13.86, із20% $16.64. Це conditional сценарій, не поточна автоматизація. Якщо ALB лишається730год при backend80год, додати близько $21.65 до $24.26. З default application_window_open=false ALB/service відсутні, але після дозволеного apply RDS/S3/ECR та storage можуть оплачуватися; це не «вся система вимкнена за $0».

## AI
Private EC2, без IPv4:
| Тип | Compute80 /730 | EBS20GB весь місяць | RAM |
|---|---:|---:|---:|
| t3.small | $1.664 /15.184 | $1.60 | 2GiB |
| t3.medium | $3.328 /30.368 | $1.60 | 4GiB |
| t3.large (лише benchmark потреба) | $6.656 /60.736 | $1.60 | 8GiB |

AI off — жодного instance/EBS у початковому apply. AI demo80 для backend730 додає small $3.264 або medium $4.928; image/model storage може зрости. Повний рекомендований ECS small з AI small80: $27.53/80год або $65.94/730год, із резервом $33.03/$79.13. ECS AI окремим CP додав би agent/endpoint/bootstrap overhead, не менший compute тариф. GPU/навчання не включені й не запускаються.

## ALB / без ALB
Офіційна ставка us-east-1: $0.0225/год + $0.008/LCU-год. За припущення0.1 LCU і мінімальних2 public IPv4: $2.664/80год, $24.309/730год. Це 2AZ subnet coverage, а не2×ALB hourly fee. Масштабування IP, dominant max LCU dimension/піки й cross-zone/cross-service transfer можуть збільшити рахунок. TLS ACM non-exportable для ALB не має окремої certificate issuance fee; DNS/domain й інші типи сертифікатів — окремо.

Compose small без ALB, ізRDSpersistent: $21.60/80год, $38.37/730год, із20% $25.92/$46.04. Потрібен власний перевірений HTTPS origin/reverse proxy/health/rollback; цей альтернативний deployment у root не реалізовано. Fargate без ALB не має спроєктованого stable origin у цій конфігурації: такі CSV рядки позначені cost-only, не готові deployment сценарії.

Додатковий ECS host: 4 releases ×30хв =2год small+IPv4+pro-rated EBS ≈$0.056. Це умовний контрольований surge; втрата/зависання другого host може коштувати повний місяць. max2 дозволяється окремо; default max1 має downtime. Fargate surge —4×5хв додаткової task capacity з IPv4 за вибраним network mode. 20% резерв не гарантує покриття великих відхилень.

## NAT / endpoints
| Мережа | 80год | 730год | Примітка |
|---|---:|---:|---|
| No NAT, host IPv4 | $0 додатково | $0 додатково | Host IP уже в backend рядку, S3 gateway без hourly |
| NAT GW,10GB | $4.45 | $36.95 | .045/h + .005 IPv4/h + .045/GB |
| NAT GW,50GB | $6.25 | $38.75 | Не включає сторонній data transfer |
| NAT GW,100GB | $8.50 | $41.00 | Один gateway/AZ dependency |
| NAT Instance nano8GB | $1.456 | $8.086 | .0052/h +IPv4 +.64disk |
| NAT Instance micro8GB | $1.872 | $11.882 | .0104/h +IPv4 +.64disk |
| 5 interface endpoints,10GB | $4.10 | $36.60 | ECR2 +Logs1 +SSM/ssmmessages2, одна AZ |

Для private ECS AI додаткові3 ECS endpoints можуть збільшити fixed endpoint cost до8×.01/h: $6.50/$58.50 із10GB processing. Перевірити service/region/agent requirements. Endpoints не дають Open-Meteo internet. Matrix endpoints5 лишає backend public для weather, тобто це додаткові endpoints для private компонента, не «заміна всього інтернету». Дві AZ endpoints множать hourly ENI fee; NAT gateway у двох AZ подвоює fixed hourly/IP, не обов'язково загальний processed traffic. Один NAT Instance — SPOF і операційні витрати, throughput/CPU credits не виміряні. При NAT мережі модель прибирає backend public IPv4, а для no-ALB private origin ставить invalid limitation.

## S3, CloudFront та тарифні плани
База: S3 Standard5GB×$0.023 +1000PUT/LIST×$0.005/1000 +10000GET×$0.0004/1000 = $0.124. ECR5GB $0.50, CloudWatch1GB ingestion/archive+3alarms $0.83, snapshots10GB billed blocks $0.50, DNS reserve $0.50. Це обсяги, не ліміти AWS. Versioning/старі assets/AMI, PyTorch layers і дані можуть збільшити storage. Немає state bucket: HCP state не має S3 hourly/storage рядка.

CloudFront PAYG консервативно10GB US/EU×$0.085 +100000 HTTPS requests×$0.01/10000 = $0.95. Не віднімаємо можливий1TB/10M Free Tier: його доступність/використання акаунта не перевірено. AWS origins→CloudFront data transfer окремо не дублюється; non-CDN egress reserve1GB×$0.09. Окремо консервативно10 000 viewer function calls ×$0.10/million = $0.001, без віднімання allowance. Інші географії, запити, logging/invalidation понад allowance перерахувати.

Flat-rate plans за [офіційними умовами](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/flat-rate-pricing-plan.html): Free $0/1M requests/100GB, Pro $15/10M/50TB, Business $200/125M/50TB, Premium від$1000. Це не те саме, що PAYG Free Tier. Потрібні eligibility/compatibility review, WAF web ACL association, account quota (до3 Free plans), scope included services. Значне тривале перевищення allowance може впливати на performance; «no overage» не поширюється на EC2/ALB/RDS. Поточний код створює PAYG distribution без enrollment/WAF, Free enrollment не застосовано. Conditional Free CSV лише зменшує CF delivery до0, консервативно не списує інші storage credits/allowances. Paid plans не обирати за $100 без окремого рішення.

## Повна матриця й відтворення
`scripts/aws_architecture_costs.py` — offline standard-library calculator, без AWS calls. `reports/aws-architecture-cost-matrix.csv`: **4800 оцінок** backend×hours×ALB×DB×AI×network×CF×DB schedule; усі component costs,20% та limitations окремо. Не всі комбінації працездатні: micro RAM, direct Fargate і private no-ALB origins явно позначені. `reports/aws-ecs-cost-summary.json` містить rates/examples. Модель не є Terraform plan, не доводить runtime sizing і не замінює AWS Calculator перед apply.

## $100 Credits, HCP та budget gates
Для рекомендованого AI-off з20%: $100/$29.12 ≈3.43 демонстраційних місяця або $100/$75.21 ≈1.33 місяця24/7. З AI small80: ≈3.03 або1.26. Це арифметика при сталих обсягах, eligible charges та невичерпаному строку кредиту, не гарантія. Непідтверджені додаткові $100 дали б удвічі довший арифметичний горизонт; у гарантованому бюджеті їх немає.

HCP Free умовно$0 в межах500 managed resources/organization й1 concurrent run; інші проєкти/обидва workspaces ділять ліміт. Платні upgrade/Europe plans/advanced governance, GitHub minutes/artifacts, domains/taxes та непокриті AWS services не оплачуються автоматично AWS credits. Account credits eligibility/expiration перевіряє людина перед ресурсами. GPU, NAT, additional regions, support/advanced monitoring заборонені без нового кошторису.

Запропонований gross monthly budget $35 для80год ECS+AIoff/за потребиsmallAI80 з20% (перевірити конкретний профіль); попередження50/80/100%+forecast. Окремий cumulative ledger $100, інтервенція при$80 витраченого eligible credit із$20 запасом; net unpaid budget$1. IncludeCredit=false для gross, не плутати з net budget. Budgets не hard cap, billing затримується; зупинка EC2 не видаляє EBS/IPv4 allocations/ALB/RDS/S3. Немає автоматичного scheduler або дозволу auto-destroy. Поточний HCP не підключений, жодні буджети/ресурси не створені.

## Офіційні джерела, перевірено24.11.2026
- [EC2 regional primary map](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20%28N.%20Virginia%29/Linux/index.json), selected rates реально збережені в aws-ecs-ec2-price-evidence.json.
- [Fargate unit rates у AWS cost example](https://docs.aws.amazon.com/solutions/latest/prebid-server-deployment-on-aws/cost1.html), [Fargate pricing](https://aws.amazon.com/fargate/pricing/).
- [ALB](https://aws.amazon.com/elasticloadbalancing/pricing/), [VPC/NAT/IPv4](https://aws.amazon.com/vpc/pricing/), [PrivateLink](https://aws.amazon.com/privatelink/pricing/).
- [RDS primary catalog](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-1/index.json) та попередній aws-price-evidence.json з актуальними одиничними цінами. [MySQL support](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/MySQL.Concepts.VersionMgmt.html):8.0 standard support закінчилася31.07.2026, root8.4.13 ще потребує region/class/schema validation.
- [CloudFront](https://aws.amazon.com/cloudfront/pricing/), [S3](https://aws.amazon.com/s3/pricing/), [ECR](https://aws.amazon.com/ecr/pricing/), [EBS](https://aws.amazon.com/ebs/pricing/), [CloudWatch](https://aws.amazon.com/cloudwatch/pricing/), [Secrets Manager](https://aws.amazon.com/secrets-manager/pricing/).
- [HCP plans](https://developer.hashicorp.com/terraform/cloud-docs/overview), [AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html).
