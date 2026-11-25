# ClimateHealth — перехід Terraform на AWS

24.11.2026. AWS — остаточна платформа. **Жодних Terraform-команд у поточному завданні не виконувати**, включно з fmt/init/validate/plan/apply/destroy. Нижче — порядок наступного погодженого етапу, не дозвіл його запуску.

## Стан файлів
Новий root: `infrastructure/terraform/aws/`. Провайдер **hashicorp/aws = 6.74.0**, перевірений через [Terraform Registry API](https://registry.terraform.io/v1/providers/hashicorp/aws) 24.11.2026; Terraform >=1.11,<2, S3 native locking. Провайдер не встановлювали, lockfile не створено. Будь-який future upgrade — окремий review, не автоматичний latest.

Історичні `.tf` та example-файли батьківського каталогу збережені незмінними. Їхня платформа не є цільовою, новий workflow до них не звертається. AWS не створюється простим перейменуванням ресурсів. Невідомий/історичний state спершу інвентаризують read-only за окремим дозволом; ARN/ідентичності іншої платформи не мають AWS відповідників для moved/import. Немає підстав стверджувати, що старий state або реальні ресурси існують.

## Поточний каркас і межі
- S3 bootstrap: versioning, SSE-S3/AES256 без окремого CMK, public-access block, TLS-only policy, BucketOwnerEnforced, force_destroy=false, prevent_destroy=true, явний bootstrap_approved=false за замовчуванням.
- Networking: VPC, app public subnet, дві private subnet у різних AZ, private route table без NAT/default internet route, gateway endpoint до окремого artifact bucket.
- Security: app-only доступ до ML/MySQL, public 80/443 лише на app; немає public SSH, ML або DB.
- Dev/production — окремі resource-free roots, account_id guard, приклади S3 backend. Модулі ще **не підключено**, workload EC2/RDS/ECR/IAM/deploy agent не реалізовано. Це не готовий план розгортання.

Module contracts і список необхідних inputs наведено в [AWS scaffold README](../infrastructure/terraform/aws/README.md). Окремі application/ml-server/mysql modules створювати після погодження сценарію, AMI/розмірів, RPO/RTO, домену й ролей; не імітувати готовність порожніми каталогами.

## Безпечний bootstrap S3 state
1. Погодити AWS account/region, залишок та придатність кредитів, owner і унікальне ім'я bucket. Людина входить через федеративну роль/SSO з MFA; root і long-term keys не використовуються.
2. Виділити bootstrap admin role тільки для state bucket та його policy/versioning/encryption/public-block. Workload CI не має права створювати/видаляти state bucket або змінювати його policy. Поточний HCL задає transport deny; повний identity allow-list — ще IAM gate, не автоматично налаштована роль.
3. Початковий bootstrap використовує захищений local state на зашифрованому диску. До майбутнього apply: окремо переглянути plan, ім'я/account і permissions; за замовчуванням approval guard блокує створення.
4. Після підтвердженого створення перевірити block public, versioning, TLS deny, SSE, доступи. Зберегти захищену резервну копію bootstrap state, узгоджено перенести його до окремого `bootstrap/terraform.tfstate`; dev/production не ділять цей key. Не видаляти local backup до перевірки відновлення.
5. Після окремого дозволу підключити environment backend example із реальним bucket/key; credentials надходять від federated identity/OIDC, не з HCL чи `-backend-config` secrets. Object state і plan потенційно містять секрети навіть при sensitive=true.

[S3 backend](https://developer.hashicorp.com/terraform/language/backend/s3): `encrypt=true`, `use_lockfile=true`; потрібні Get/Put для state та Get/Put/Delete для `.tflock`, без DeleteObject для самого state. [State IAM template](../infrastructure/ci/aws-state-policy.json.example) — вузький приклад для одного environment, не весь deploy policy. Не використовувати deprecated DynamoDB locking або S3 Object Lock як заміну native lockfile. State versioning має власне відновлення й не означає Object Lock.

## Поетапна міграція після погодження
1. Затвердити [ADR 0004](adr/0004-aws-infrastructure-and-credit-budget.md) у частині параметрів: A/B/C, us-east-1 чи інший регіон з новим кошторисом, data residency, $25 demo budget, життєвий цикл і backups. AWS як провайдер уже погоджено.
2. Після зняття заборони виконання: перевірити актуальний Terraform binary/архітектуру, форматування, init **без backend/credentials**, validate для bootstrap/modules/dev/prod; отримати checksum lockfile для Linux CI й потрібної локальної платформи. Нічого з цього не виконано зараз.
3. Перевірити network/SG contracts, IAM boundary, artifact bootstrap/AMI, параметри workload-модулів. Додати native Terraform/module tests та policy scanner у дозволеному ізольованому CI. Не називати поточний текстовий review provider-schema validation.
4. Погоджений S3 bootstrap → перевірка конкурентного native locking двома процесами, state version recovery, відсутність доступу чужого environment. Ніколи не обходити через -lock=false.
5. Довірена main → scoped plan role → збережений plan із commit/provider/inputs fingerprint → review конкретного переліку платних ресурсів і кошторису → явне окреме схвалення → apply **того самого** plan. Sensitive plan не публікується у PR/logs; коротке retention і доступ лише deploy-операторам.
6. Після інфраструктури — окремий container/release gate, TLS/service auth, secrets, health, rollback. Локальну MySQL не переносити й не змінювати без дозволу; хмарний імпорт потребує погодженого dataset/backup/restore.

Dev/production мають окремі credentials, backend keys і protected environments; Terraform workspace не підміняє цю ізоляцію. Destroy, видалення state/backup і ротація ключів — окремі контрольовані дії. Rollback контейнера не скасовує SQL-міграцію.

## CI зараз
`terraform-ci.yml` лишається manual-only та job if:false, але майбутні paths спрямовані лише на AWS. Немає дозволу вмикати цей job або Docker/deploy. Не стверджуємо, що каркас пройшов Terraform fmt/init/validate або був застосований.
