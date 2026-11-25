# ClimateHealth — AWS: кошторис і контроль $100

Перевірено 24.11.2026. Регіон **us-east-1, Northern Virginia**, Linux x86 On-Demand, USD, 730 год/місяць. Регіон запропоновано для порівняння тарифів, не погоджено для персональних/медичних даних. Гарантовано лише заявлені $100 кредитів; фактичний залишок, строк дії, тип AWS plan, перелік покритих послуг і податки в акаунті не перевірялися.

Оцінка не використовує Reserved/Savings Plans, Spot, додаткові кредити, promotional Free Tier або GPU. Вартість розрахована до кредитів і податків; 20% резерв не є лімітом рахунку. Це інженерна модель, не AWS invoice і не виміряний workload.

## Три сценарії 24/7
| Стаття, USD/місяць | A: мінімальна демонстрація | B: два EC2, MySQL на app | C: два EC2 + RDS MySQL |
|---|---:|---:|---:|
| Application EC2 | t3.medium 4 GiB: 30.37 | t3.medium 4 GiB: 30.37 | t3.small 2 GiB: 15.18 |
| AI EC2 | окремий процес на app: 0 | t3.small 2 GiB: 15.18 | t3.small 2 GiB: 15.18 |
| EBS gp3 | 40 GB: 3.20 | 40 + 20 GB: 4.80 | 20 + 20 GB: 3.20 |
| Один public IPv4 на app | 3.65 | 3.65 | 3.65 |
| RDS db.t4g.micro Single-AZ | 0 | 0 | 11.68 |
| RDS gp3 20 GB | 0 | 0 | 2.30 |
| S3 5 GB + запити | 0.124 | 0.124 | 0.124 |
| ECR private 2 GB | 0.20 | 0.20 | 0.20 |
| Internet egress: резерв 10 GB | 0.90 | 0.90 | 0.90 |
| CloudWatch logs + 3 alarms | 0.83 | 0.83 | 0.83 |
| EBS snapshots: 10 GB billed blocks | 0.50 | 0.50 | 0.50 |
| NAT / interface endpoints | 0 / 0 | 0 / 0 | 0 / 0 |
| **Сума, з неокруглених складових** | **39.77** | **56.56** | **53.75** |
| **Плановий резерв 20%: разом** | **47.73** | **67.87** | **64.50** |

A — мінімальний запропонований демонстраційний варіант, а не абсолютний тарифний мінімум AWS. RAM підібрана консервативніше за 1 GiB: MySQL, Flask/Matplotlib і майбутній PyTorch можуть не вміститися навіть у 4 GiB, доки це не виміряно. Для B app більший через MySQL; для C менший, бо БД винесено. Тому C тут трохи дешевший за B; при однаковому app t3.medium C становив би $68.94 до резерву. Ці розміри — кандидати, не результат benchmark. ARM у RDS прозорий для MySQL-протоколу; app/AI образи пропонуються x86, multi-arch не припускається.

**Рекомендація:** A за розкладом демонстрацій, без inference до появи погодженої моделі. За 80 активних годин/місяць (20 × 4 год), зі збереженням дисків/S3/ECR/backup весь місяць: **$9.48**, або **$11.38 з резервом**. Це потребує реальної дисципліни зупинки EC2 й відсутності збереженого EIP; автоматичний stop/TTL ще не реалізований. EBS, snapshots, S3 та ECR оплачуються і під час зупинки. Динамічний IPv4 зміниться після stop/start; для стабільного EIP враховувати повні $3.65/місяць, а не $0.40.

## Тарифи та припущення
- EC2: t3.small $0.0208/год, t3.medium $0.0416/год. Реально прочитано [публічний регіональний price map AWS](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20%28N.%20Virginia%29/Linux/index.json); selected rateCode збережені в `reports/aws-price-evidence.json`.
- RDS: $0.016/год та gp3 $0.115/GB-month; реально прочитано [AmazonRDS us-east-1 Price List](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-1/index.json), publicationDate 2026-11-20, effectiveDate 2026-11-01. SKU U4AUM7WC9VCSGAY9 та H4R2WBBMX6VRJG4S. Backup allowance активної RDS та excess/retained copies перевірити перед запуском; надлишкових RDS backup у базовому сценарії немає.
- [EBS](https://aws.amazon.com/ebs/pricing/): gp3 $0.08/GB-month у вибраному тарифному сценарії, baseline IOPS/throughput, без provisioned extras. Snapshots $0.05/GB-month ([AWS приклад](https://docs.aws.amazon.com/prescriptive-guidance/latest/optimize-costs-microsoft-workloads/ebs-migrate-ebs-snapshots.html)); 10 GB — припущення щодо сумарних billed blocks включно з AMI, не кількість snapshots. Зростання копій/AMI збільшить плату.
- [VPC pricing](https://aws.amazon.com/vpc/pricing/): IPv4 $0.005/год; одна адреса, AI/RDS приватні. NAT у базі відсутній; додавання одного NAT у us-east-1 орієнтовно $32.85/місяць + $3.65 IPv4 + $0.045/GB processing, тобто близько $36.95 з 10 GB processing, понад базовий рахунок. Не створюємо NAT «про всяк випадок».
- [S3 pricing](https://aws.amazon.com/s3/pricing/): Standard $0.023/GB-month; 5 GB сумарно state versions + releases/models + bounded logs/backup; 1 000 PUT/LIST за $0.005 і 10 000 GET за $0.004. Підтвердження [AWS storage example](https://aws.amazon.com/blogs/storage/monitor-data-transfer-costs-related-to-amazon-s3-replication/). Часте polling або великі моделі можуть перевищити ці обсяги. State bucket — без expiration поточних/старих state versions; окремі retention правила для release/logs/backup після погодження RPO.
- [ECR](https://aws.amazon.com/ecr/pricing/): $0.10/GB-month, ліміт планування 2 GB з lifecycle retention; старі rollback digests не видаляти до завершення rollback window.
- [CloudWatch](https://aws.amazon.com/cloudwatch/pricing/): 1 GB ingestion × $0.50 + 1 GB compressed archive × $0.03 + 3 standard alarms × $0.10 = $0.83. Це закладений обсяг/платний розрахунок без вирахування free allowances, не максимальна плата. Custom metrics, verbose logs, Logs Insights scans, dashboards і advanced/container insights не включені; не вмикати без оцінки. AI не має logs endpoint: схема передачі описана в AWS_ARCHITECTURE.
- Internet egress: у кошторисі консервативно 10 × $0.09 = $0.90. [AWS має загальний 100 GB/month allowance](https://aws.amazon.com/ec2/pricing/on-demand/), але невідомо, чи його споживають інші ресурси акаунта; при доступному allowance фактична сума може бути нижчою. Same-AZ приватні зв'язки; inter-AZ та cross-region трафік не закладені, при зміні topology перерахувати.
- [PrivateLink](https://aws.amazon.com/privatelink/pricing/): два ECR interface endpoints по $0.01/год в одній AZ = $14.60 плюс processing; S3 gateway endpoint без погодинної плати. У базі — S3 release delivery, не прямий ECR pull із AI.

Відтворювані неокруглені складові й підсумки: `reports/aws-cost-model.json`. Рахунок має календарну кількість годин, 730 — нормалізація. ALB, Route 53 hosted zone, домен/реєстрація, платний support, Secrets Manager, customer-managed KMS key, additional AMI/snapshots, VPN і платні сканери не входять до бази. Одноразові build/AMI instance hours, тимчасове подвоєння вузлів під час оновлення, GitHub minutes/artifact retention та оплачувані secret/scan integrations також потребують окремої оцінки; вони не приховані у фіксованому baseline. Не замовляти їх автоматично; домен/HTTPS перед запуском потребують окремого рішення. Для EC2 запропоновано Standard CPU credits: уникнення Unlimited overage означає throttling при вичерпанні кредитів. RDS burst CPU overages лишаються можливими.

## Особливий ризик RDS MySQL 8.0
[Стандартна підтримка RDS MySQL 8.0 завершилася 31.07.2026](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/MySQL.Concepts.VersionMgmt.html). Не копіювати локальну версію 8.0.40 у новий RDS-план без оцінки Extended Support. Базова оцінка передбачає підтримувану 8.4 LTS після compatibility/restore tests, точний minor визначається окремо. Локальну БД зараз не змінюємо.

## AWS Credits і Budgets
1. До будь-якого створення перевірити в Billing → Credits фактичні $100, залишок, expiration і eligible services. Можливі додаткові кредити не включати. Податки/непокриті послуги можуть вимагати реальної оплати навіть за позитивного залишку.
2. Погодити місячний gross cost budget **$25** для A-demo: IncludeCredit=false, без зменшення витрат кредитними записами; сповіщення actual 50/80/100% та forecast 100%. Для 24/7 A потрібен окремо погоджений бюджет щонайменше $48, B $68, C $65 з резервом.
3. Окремий net cost budget після кредитів: попередження вже при $1 фактичної/прогнозованої непокритої оплати. Саме net-only budget може мовчати, доки кредити витрачаються; gross budget потрібний паралельно. [CostTypes IncludeCredit](https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_budgets_CostTypes.html), [створення бюджету](https://docs.aws.amazon.com/cost-management/latest/userguide/create-cost-budget.html).
4. Місячний budget скидається й не відстежує весь $100. Вести сумарний ledger використаних credit-eligible витрат за весь строк: залишок кредиту звіряти з Billing, не оцінювати лише як 100 мінус усі gross charges. При витраті $50/$75/$90 — попередження; при $80 — рішення про зупинку/продовження із резервом $20 на затримку billing і незупинювані storage costs. Строк чинності кредиту може обмежити роботу раніше за розрахункові місяці.
5. Email одержувача погодити; нічого не надсилалося і Budgets не створювалися. Описані email-based cost budgets без actions не потребують платної оркестрації; [ціни Budgets](https://aws.amazon.com/aws-cost-management/aws-budgets/pricing/). Додатковий SNS/автоматичні дії оцінювати окремо.
6. [Budgets сповіщення надходять із затримкою й не зупиняють витрати](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html). IAM deny для GPU/NAT/ALB та непогоджених regions, теги Owner/Environment/ExpiresAt, мінімальні service quotas і ручний щоденний billing review зменшують ризик, але не утворюють гарантованої межі $100. TTL без виконуючого scheduler — лише тег, не автоматична зупинка.
7. Після завершення демонстрації — погоджений stop/retention audit: EBS, EIP, snapshots/AMI, S3 versions, ECR, alarms. RDS [автоматично запускається після 7 днів зупинки](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_StopInstance.html); не вважати stop постійним вимкненням. Destroy/видалення копій — лише за окремим дозволом і після перевірки backup.

Рекомендований запуск: тільки A-demo після регіону/ліцензій/доступів/backup/HTTPS та бюджетного погодження. B/C — наступний етап за фактичною потребою й виміряною пам'яттю моделі. GPU та навчання не плануються.
