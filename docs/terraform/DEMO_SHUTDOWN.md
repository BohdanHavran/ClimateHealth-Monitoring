# Завершення демонстрації та залишкові витрати

26.11.2026. Це процедура майбутнього контрольованого Manual Apply, зараз нічого не зупинялося/видалялося в AWS.

Спочатку завершити користувацькі сесії, перевірити backup/restore та поточний state. Залишити вже застосовані provisioning flags=true. Змінити service_enabled=false, application_window_open=false, allow_deployment_capacity=false, ai_enabled=false. Переглянути Plan: очікується видалення service/ALB/DNS alias та ASG capacity0, **не RDS/S3/ECR/AI instance**. Якщо є інші destruction/replacement — не підтверджувати. CloudFront API behavior прибирається, frontend CDN залишається. Наступний запуск повторно відкриває window й capacity після перевірок.

| Компонент | Дія | Збережено | Залишкова вартість |
|---|---|---|---|
| Backend ASG | min/max0; EC2 terminated | Cluster/IAM/LT/task definition | EC2/IP після фактичного termination0; можливі logs/storage |
| Backend root EBS | видаляється разом із ephemeral host | Дані повинні бути в DB/S3 |0 після видалення; snapshots окремо |
| ALB | видаляється при window=false | Terraform конфігурація | hourly/IPv4/LCU припиняються лише після фактичного видалення |
| AI EC2 | stopped через окремий power state | Instance і20GB gp3 | compute0, приблизно $1.60/міс EBS; старт створеного instance спочатку оплачується навіть при кінцевому stopped |
| RDS | продовжує працювати | DB20GB, backups, master secret | db.t4g.micro приблизно $11.68 compute +$2.30 storage +$0.40 secret = $14.38/730h без додаткових I/O/backup/transfer |
| EC2 MySQL alternative | автоматично не зупиняється | DB host+30GB disk | compute $0.0208/h + приблизно$2.40/міс EBS; потребує окремої погодженої stop процедури |
| ECR | лишається | Images; попередня lifecycle policy для untagged збережена | $0.10/GB-місяць,5GB≈$0.50; не видаляти потрібні rollback digests |
| S3 versioning | лишається | Обʼєкти, попередні versions/backups/model artifacts | Standard≈$0.023/GB-місяць + requests/transfer; versions теж оплачуються |
| Snapshots | зберігати | Дані для відновлення | EBS standard≈$0.05/GB-місяць; RDS backup понад allowance окремо |
| CloudWatch | log group лишається, retention7 | Logs до expiry |≈$0.03/GB-місяць retained+ingestion; не дорівнює нулю автоматично |
| CloudFront | S3 frontend продовжує обслуговування | CDN і HTTPS | Usage/requests/functions/transfer згідно тарифу; не припускати Free Tier |
| VPC/SG/S3 Gateway endpoint | лишаються | Мережеві ресурси | Немає окремої hourly за ці типи; повʼязані data transfer окремо |

Це орієнтири попереднього [кошторису](../AWS_COST_ESTIMATE.md) us-east-1, не live billing і не нова перевірка тарифів. Резерв20%. Навіть при stopped AI мінімально лишається RDS≈$14.38 + AI disk$1.60 + ECR$0.50 + usage/backups, тобто понад$16.48/місяць. AWS charges рахуються за фактичним часом/обсягом; 80h backend не означає80h RDS. Перевірити Cost Explorer після кожного stop.

Ручний RDS stop не є постійним вимкненням: сервіс може автоматично стартувати через7днів. Terraform gate не використовувати як заміну stop — prevent_destroy має заблокувати втрату DB. Для остаточного teardown потрібне окреме погодження, перевірений backup/restore та явне керування deletion protection/final snapshot. Backup, snapshots і S3 versions не видаляти автоматично для економії.

AWS Budgets поки лише пропозиція: місячний budget з actual50/80/100% і forecast100%, окремі dev/production tags, погоджений email/SNS. Budgets alerts не hard cap і можуть запізнюватися; не підключати automatic destructive actions. AWS credits не покривають усі можливі external/HCP charges; перевіряти eligibility та expiry окремо. Будь-яке створення budget/notification ресурсів — після дозволу.
