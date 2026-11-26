> Актуальне уточнення 26.11.2026: реалізовано [варіант B](VARIANT_B_REPORT.md): 6 modules/15 root inputs, RDS-only, AI відкладено, HCP володіє ECS revisions. Старі gates та EC2 MySQL нижче — контекст попереднього етапу. Поточні inputs/runbook/графи наведено у звіті B. Наступний крок: review diff і окреме погодження публікації; потім дозволений remote validate/Plan, не автоматичний Apply.

# Cost audit: ресурси, gates та постійні витрати

> Базовий аудит 25.11.2026. Висновки про 11 required inputs, відсутній TLS/ML URL та старі gates описують стан ДО виправлень. Поточні зміни й умовні inputs: [CONTROLLED_DEPLOYMENT](CONTROLLED_DEPLOYMENT.md), результати: [READINESS_REPORT](READINESS_REPORT.md). Старі числові оцінки не є новими вимірюваннями.

Регіон порівняння us-east-1, USD, без податків/автоматичного списання credits або FreeTier. Джерело чисел — попередній offline кошторис 24.11.2026;25.11 повторно переглянуто офіційні ALB/VPC ціни. Це припущення про usage, не billing data або Terraform Plan. Акаунт/credit expiry/реальні invoices не читалися. [Повний кошторис](../AWS_COST_ESTIMATE.md) і CSV4800 варіантів не означають, що root реалізує всі ці варіанти.

| Компонент у code | Що спричиняє витрати | 80h / 730h або місячний орієнтир | Що лишається після stop/scale0 |
|---|---|---|---|
|VPC/subnets/route tables/SG/IGW|Окремої hourly для базових обʼєктів немає; traffic services окремо|$0 fixed hourly|Обʼєкти лишаються, але самі не є NAT bill|
|S3 Gateway endpoint|Без hourly; S3requests/storage оплачуються|$0 endpoint hourly|Маршрути лишаються; Open-Meteo доступ не забезпечує|
|ECS EC2 t3.small|EC2$0.0208/h + hostIPv4$0.005/h + gp3$0.08/GB-month|Compute$1.664/$15.184; IP$0.40/$3.65;20 GB за повний місяць$1.60|ECScontrolplane/ASG/LT без окремої compute fee; manualstopASGhost може бути автоматично відновлений|
|ALB|$0.0225/h + LCU$0.008/h + мінімум 2IPv4$0.005/h|При 0.1 LCU:≈$2.66/$24.31|ALB та його IP не зупиняються разом із backend; потрібен погоджений delete для припинення fixedfee|
|RDS db.t4g.micro Single-AZ|$0.016/h +20GBgp3$0.115/GB-month|Compute$1.28/$11.68, storage$2.30/міс|При app windowfalse RDS продовжує працювати. Нормальний persistentbaseline:compute730h, не 80h|
|RDS managed master secret|SecretsManagerstorage/API usage|У моделі≈$0.405/міс|ReaderSSMARNs окремі, RDS master не використовується Flask|
|PrivateEC2MySQLsmall|Та сама smallcompute +30GBgp3|$1.664/$15.184 compute +$2.40 storage/міс|prevent_destroy блокує простий delete; retainedrootvolume може оплачуватися далі|
|PrivateAI small/medium|small$0.0208/h або medium$0.0416/h +20GBEBS|small80h$1.664;medium80h$3.328; retainedEBS$1.60/міс|ai_enabled=false видаляє EC2, але delete_on_termination=false залишає disk|
|S3frontend/artifacts|GB-month,PUT/GET,noncurrentversions|Модель 5 GB+requests$0.124/міс|Versioning без expiry; старі assets/models/backups ростуть незалежно від EC2|
|CloudFront/functions|Traffic/requests/function invocations|Модель 10 GB+100kHTTPS≈$0.95,10kfunctions≈$0.001|При порожньому/неактивному site не слід приписувати usage fee наперед; distribution лишається public|
|ECR|Обсяг images/layers|5 GB≈$0.50/міс|Tagged releases не очищуються untagged14days policy, storage лишається|
|CloudWatchlogs|Ingestion/retention; group сам не має fixedfee|Модель 1GBingestion/archive≈$0.53, ще$0.30 зарезервовано на 3 alarms|Logs лишаються 7 днів; **3 alarms у цьому root не створюються**|
|Route53originrecord|Існуюча hostedzone/queries; aliasrecord не окремий fixedbill|Попередній$0.50DNSreserve, не Terraformcreatedzone|Root не купує domain/zone; existingaccountDNSexpenses перевірити окремо|
|Snapshots/backups|Обсяг billedstorageblocks|Модель 10 GB≈$0.50/міс|Snapshots можуть залишатися після DB/EC2; RDSfinalsnapshotidentifier повторно використовувати небезпечно|
|IAM/CP/task definition/cachepolicy/OAC|Немає окремої hourly за config|$0 config hourly|Не плутати з compute/logs/traffic, які вони забезпечують|

## Що у попередньому кошторисі слід читати обережно

- Профіль ECSsmall/RDSpersistent/AI off/noNAT із ALB80h дає$24.26 або$29.12 із 20%reserve;730h дає$62.68/$75.21. Це консервативний usage сценарій, не виміряна ціна поточного run. ALB80h передбачає реальне погоджене видалення/recreate між вікнами, не scale0tasks.
- Backend20GBEBS у моделі пораховано за місяць, хоча ASGhost rootdisk має delete_on_termination=true. При terminatedscale0 це завищує disk час; просто stoppedEC2 може залишати EBS і спричинити ASGreplacement. Не змінювати модель на нижчу ціну без фактичного графіка lifecycle.
- AI/DBretainedEBS модель враховує один volume. Повторні enable/disable/replacement можуть накопичити декілька unmanaged rootvolumes, тому навіть 20%reserve не гарантує покриття витрат. Потрібні окремий retention/cleanupaccounting та погоджений stopplan.
- CloudWatch3 alarms/AWSBudgets існують як рекомендація/резерв, **не як реалізовані Terraform ресурси**. Немає hardbudgetcap чи автоматики зупинки. Нова AI model/PyTorchimage може бути значно більшою за 5GBECRbaseline.
- Відсутні ресурси NATGateway/NATInstance/interfaceendpoints: не додавати їхню hourly до поточного root як фактичну витрату. Якщо така мережа буде погоджена, потрібен новий кошторис.
- Infrastructure_reviewed=false блокує нормальний Plan, тож зараз із цього аудиту нічого не створено. Але після його свідомого відкриття app window/service/AI=false **не** є no-cost mode: при RDSmode база створюється незалежно, приблизно$14.39/міс compute/storage/secret плюс usage/backup. Також створюються порожні S3/ECR/CF/IAM/logconfig; їх usage/retention не гарантовано нульові.

Фактична наявність$100credits та їхні eligiblecharges/expiry не перевірялися; арифметичні 3.43/1.33 місяця з попередньоїмоделі не є гарантією. HCP оплачується окремо за фактичними умовами organization; спосіб авторизації та тариф не змінювалися.

Джерела: [ALB](https://aws.amazon.com/elasticloadbalancing/pricing/), [VPC/IPv4](https://aws.amazon.com/vpc/pricing/), [попередні primarypriceevidence та повні припущення](../AWS_COST_ESTIMATE.md), [RDSversions](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/MySQL.Concepts.VersionMgmt.html). Version8.4.13 включено в офіційний список, але availability конкретного region/class не підтверджено API.

## Уточнення про автоматичні scaling alarms

Відсутність власних aws_cloudwatch_metric_alarm blocks не означає відсутність усіх CloudWatch alarms після Apply. ECS capacity provider із managed scaling керує metrics, двома alarms і scaling policy поза окремими ресурсами цього HCL. Попередній резерв на3alarms не є точним переліком цих objects або доведено достатньою monitoring сумою. Перевірити billing dimensions/кількість metrics/alarms у погодженому середовищі; не приписувати нульову ціну всім platform side effects. [AWS cluster auto scaling](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/cluster-auto-scaling.html).
