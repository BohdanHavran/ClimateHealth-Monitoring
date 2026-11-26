# Required Variables Audit: чому HCP просить 13 значень

> Базовий аудит 25.11.2026. Висновки про 11 required inputs, відсутній TLS/ML URL та старі gates описують стан ДО виправлень. Поточні зміни й умовні inputs: [CONTROLLED_DEPLOYMENT](CONTROLLED_DEPLOYMENT.md), результати: [READINESS_REPORT](READINESS_REPORT.md). Старі числові оцінки не є новими вимірюваннями.

Аудит вихідного стану коміту 5f01e24, до дозволеного очищення owner/account. Самого тексту HCP run/log/plan не надано, HCP API не викликали: нижче відтворено **13 root declarations без default із коду**, а не процитовано 13 прочитаних diagnostics. Якщо конкретний run має інший commit/variable set, його повідомлення можуть відрізнятися.

Terraform збирає root inputs до обчислення resource count. Тому service_enabled=false або application_window_open=false НЕ скасовують required input без default. Авторизація забезпечує credentials для AWS API; вона не може самостійно обрати ваш домен, AMI, образ, Environment чи DB reader. Child module variables у цій таблиці не є окремими HCP inputs: їх заповнює main.tf.

| № | Root variable у 5f01e24 | Чому була required / де використовується | Справді потрібна мережі? | Дія цього аудиту / рекомендація |
|---|---|---|---|---|
|1|aws_account_id|ACM/SSM/IAM ARN account validation, без default|Ні|Видалити manual input; замінити на фактичний account з aws_caller_identity, зберігши перевірки. Це AWS read під час HCP run, не offline Plan.|
|2|owner|Лише default_tags.Owner|Ні|Видалити variable і тег, не вводити новий owner input.|
|3|environment|local.name та Environment tag|Так, для іменування навіть network|Залишити required:dev або production у відповідному HCP workspace. Не вгадувати середовище defaultdev.|
|4|aws_region|AWS provider, regional logging/ARN validation|Так|Залишити required. us-east-1 кошторисний кандидат, не затверджений default; інший region зараз відхилить validation.|
|5|name_suffix|Імена мережі/ролей/repositories і глобально унікальних buckets|Для naming усієї композиції|Залишити required; усвідомлено обрати унікальне значення. Зміна після deployment має великий replacement blast radius.|
|6|backend_image|Initial task definition створюється навіть без service; digest validation|Ні, deployment artifact|У поточному коді все ще required. Репозиторії створюються root, але image/digest має бути реально підготовлений окремо; не підставляти fake digest. Майбутнє відкладення task definition потребує окремого дизайну.|
|7|ecs_ami_id|Launch template існує навіть при ASGcapacity0|Ні, compute|У поточному коді required. Потрібний реальний reviewed AL2023 ECS image для region/x86; defaultlatest не додавати.|
|8|origin_hostname|CloudFront API origin створюється завжди; DNS alias conditional|Ні, frontend/API deployment|Залишається required. Має бути власний DNS і certificate coverage. CFconfig не створює ALB, якщо windowfalse.|
|9|origin_certificate_arn|ALB input і rootvalidation навіть при modulecount=0|Ні, тільки ALB/TLS|Залишається required цього етапу; кандидат на optionalnull з умовною validation при закритому window у майбутньому. Не прибирати TLS/account захист лише для зеленого Plan.|
|10|origin_verification_header|CloudFront custom header завжди; ALB rule conditional|Ні, origin protection|Залишається required/sensitive/min32. Потрібне приватне нове значення, не фіктивний default у Git; не user authentication.|
|11|runtime_secret_arns|Execution IAM та task definition secrets існують без активного service|Ні, runtime/reader|Залишається required: фактичні SSM parameter ARNs для DB_USER/DB_PASS; параметри створюються поза root. Це не plaintext credentials і не RDS master secret.|
|12|origin_zone_id|Route53 record count=window, але input без default|Ні, тільки DNS alias|Все ще required; кандидат на optionalnull лише з коректною conditional validation/ресурсом у майбутньому. Zone повинна реально існувати та відповідати domain.|
|13|permissions_boundary_arn|Boundary для 5 створюваних IAM roles, частина ролей без count|Ні, IAM workloads|Залишається required. Наявна авторизація Terraform не є boundary для нових workload roles. Потрібна реальна approved policy; не вигадувати ARN і не знімати boundary.|

## Після дозволеного очищення

Це локальні зміни, без push. HCP продовжить читати попередній Git-коміт, доки користувач окремо не погодить публікацію. Аудит не запускав повторний Plan і не заявляє, що diagnostics у наявному HCP run вже змінилися.

Стало **25 root variables, 11 required без default**. Відсутні owner/account diagnostics зникають, проте решта 11 не зникає від факту налаштованої авторизації. Якщо ці 11 уже задано у workspace/variable sets, повторно вводити їх не потрібно. Не змінювати поточний спосіб credentials і не додавати TFC_* authentication variables лише через старий шаблон документації.

Мінімальні network-specific inputs: environment/aws_region/name_suffix; vpc_cidr/public_subnet_cidrs/private_subnet_cidrs уже мають попередні безпечні defaults. Але **поточна композиція root не є network-only**: RDS, IAM, task definition, frontend створюються/описуються без привʼязки до service gate, тому мережевого набору недостатньо для валідного всього Plan. Новий режим root тут не створюється.

## Групування variables

| Група | Inputs |
|---|---|
|Обовʼязкові поточного root після очищення|environment,aws_region,name_suffix,backend_image,ecs_ami_id,origin_hostname,origin_certificate_arn,origin_verification_header,runtime_secret_arns,origin_zone_id,permissions_boundary_arn|
|Мережа|vpc_cidr,public_subnet_cidrs,private_subnet_cidrs; три naming/region inputs вище|
|ECS|backend_image,ecs_ami_id,backend_instance_type,task_memory_mib,service_enabled,allow_deployment_capacity,runtime_secret_arns,permissions_boundary_arn|
|ALB/DNS|application_window_open,origin_hostname,origin_zone_id,origin_certificate_arn,origin_verification_header|
|RDS/DB|database_mode; mysql_ami_id тільки EC2 variant. RDS class/engine/storage/retention фіксовані в модулі, readerARN у runtime_secret_arns|
|S3/CloudFront|environment/name_suffix для bucketnames; origin_hostname/origin_verification_header для API origin; решта cache/OAC/PAYGsettings фіксовані|
|AI|ai_enabled,ai_ami_id,ai_instance_type; sharedboundary/artifactbucket через rootbindings|
|Optional deployment-only кандидати на наступне погоджене спрощення|origin_certificate_arn/origin_zone_id при windowfalse; backendimage/AMI/runtimeARNs лише після відкладення відповідних task/LT/IAM блоків. Зараз їх defaults не змінено.|
|Невикористані child inputs|module.backend.listener_arn переданий, але не використовується всередині; видалення запропоновано, не виконано|

## Навмисні blockers та зовнішні передумови

- infrastructure_reviewed=false — error precondition terraform_data.review_gate. Review конфігурації/витрат виконується **до** дозволу першого Plan; конкретний Plan перевіряється знову **до** Apply. Не вмикати gate заради статусу.
- micro + taskmemory>256 MiB заборонено окремою precondition. Це не доказ того, що micro256 справді потягне NumPy/Pandas/Fuzzy workload.
- originheader<32, неправильні AMI/DNS/CIDR/environment/ARN відхиляють validations. Структурно валідний ARN/AMI не підтверджує існування, region availability або IAM access.
- EC2 DB mode без mysql_ami_id та enabled AI без ai_ami_id навмисно блокуються validation/preconditions. AI off/RDSmode допускають null цих optionalAMI.
- aws_caller_identity і решта data sources потребують працюючих credentials/мережевого AWSAPI. Налаштовану користувачем авторизацію не змінювали і не тестували зовнішніми AWS викликами.
- Реальні IAM boundary/SSM credentials/ACM/DNS zone/ECR image/pinned AMI root не створює. RDS8.4.13 є в офіційному переліку версій, але конкретну class/region/account availability не перевірено.

Повні типи/defaults/used-in/impact/example/recommendation для **кожної** змінної: [VARIABLES_REFERENCE](VARIABLES_REFERENCE.md).
