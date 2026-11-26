> Актуальне уточнення 26.11.2026: реалізовано [варіант B](VARIANT_B_REPORT.md): 6 modules/15 root inputs, RDS-only, AI відкладено, HCP володіє ECS revisions. Старі gates та EC2 MySQL нижче — контекст попереднього етапу. Поточні inputs/runbook/графи наведено у звіті B. Наступний крок: review diff і окреме погодження публікації; потім дозволений remote validate/Plan, не автоматичний Apply.

# Як працює GitHub → HCP Terraform → AWS

Це пояснення поточного source workflow. За повідомленням користувача HCP уже читає потрібний commit/root і авторизація налаштована окремим способом. Її не досліджували через credential files, не змінювали, HCP configuration/runs/API не викликали. Не потрібно вводити нові authentication variables лише тому, що попередня документація містила OIDC приклад.

## 1–6. Від push до inputs та credentials

1. Git push оновлює repository branch. Підключений HCP VCS workspace отримує change event; чи буде queued plan, залежить від його branch/trigger settings. Тут новий push не виконувався. Після майбутньої публікації змін модулів HCP може запустити plan автоматично за вашими вже встановленими triggers.
2. HCP Working Directory має бути infrastructure/terraform. Підтверджено користувачем, що root читається правильно; UI settings не змінювали. Два workspaces можуть читати один код і мати незалежні state/variables/permissions. Auto Apply повинен лишатися вимкненим; audit його фактичний UI стан не перевіряв.
3. Init завантажує code snapshot; module sources ./modules/... є локальними відносно root. Немає звернення до чужого Windows каталогу або копіювання code під час run. Root calls database/backend відображаються на modules/mysql та modules/ecs-backend.
4. Root variables не створюють ресурси самі. Усі declarations без default потребують значень незалежно від count інших блоків. Після дозволеного cleanup залишиться 11 required; child variables передає main.tf, їх не треба дублювати у HCP UI.
5. Workspace Terraform Variables/variable sets доповнюють defaults. String/bool/list/map повинні мати правильний тип/HCL режим. Sensitive=true обмежує звичайне відображення, але секрети можуть потрапити до state; access до state/run artifacts захищають окремо. Не вставляти plaintext DB credentials замість ARN.
6. AWS provider отримує credentials через вже налаштоване HCP execution environment і стандартний AWS credential chain відповідного методу. Region береться з var.aws_region. Аудит не робить висновку, що ви використовуєте саме старі TFC_* приклади. Новий caller identity data source лише читає account існуючої identity у майбутньому run, не створює/замінює авторизацію.

## 7–9. Init, Validate, Plan

7. Init готує working directory, provider plugins, localmodule metadata та state/backend integration HCP. Коректний lockfile містить справжні checksums. Наявність required_providers не означає, що binary встановлено тут. State у HCP, S3 backend і cloud block для поточного VCS сценарію у source відсутні.
8. Validate перевіряє конфігурацію та типові schema/reference помилки з установленими providers/modules. Це не повна перевірка всіх AWS прав/AMI/certificates/runtime. Наш Python checker/lexical graph не є terraform validate. HCP run може повідомити configuration validation errors до actual plan; не вважати окрему UI фазу Validate гарантованою без run log.
9. Plan збирає root inputs, конфігурацію/state, читає потрібні data sources та refresh, оцінює count/for_each і preconditions, формує create/update/replace/delete diff. Requiredvariables errors виникають до можливості «просто вимкнути service». review_gate=false навмисно блокує звичайний Plan. Plan може виконувати AWS читання і потребує credentials, хоча ресурсів Apply ще не створює.

## 10–13. Як визначається порядок

10. Dependencies утворюють graph через attribute references, provider inheritance та explicit depends_on. Порядок файлів і порядок блоків у main.tf не є чергою виконання. Наші стрілки йдуть від prerequisite до consumer; Terraform native graph може мати інший напрям візуалізації.
11. Спочатку доступні root inputs/локальні обчислення, конфігурація provider і незалежні data reads. VPC, ECR, S3 buckets, ECS cluster/деякі IAM roles можуть створюватися паралельно за готовності власних inputs. Не гарантується, що VPC буде першим AWS API create у всьому root.
12. VPC → subnet/route tables/IGW і SG через vpc_id; конкретні associations та route залежать від відповідних IDs. ALB/TG, DB subnetgroup, ASG/AI/DBEC2 залежать від їхніх subnet/SG inputs. Але subnet ID не є автоматичним очікуванням завершення всіх route associations/IGW routes.
13. ALB/rootRoute53/ECSservice існують тільки при app windowtrue. Root module.backend має широке depends_on=[module.alb], тому цілий backend module очікує ALB module, не лише його service. RDS при mode=rds не залежить від ALB/serviceenabled. CloudFront залежить від S3/OAC/cache/function та originhostname STRING, але не від Route53/ALB resource: source не виражає DNS/TLS readiness. ECR та artifactsS3 незалежні від того, чи API ready. AI modeoff не створює EC2, а SG/репозиторій/artifactsbucket усе одно можуть існувати.

Статичний graph не містить state orphan nodes, destroy/create split edges, реальних instance keys, provider-internal semantics або lifecycle expansion. Точний порядок конкретного deployment сформує лише дозволений Terraform Plan/Apply. У [dependency graph](DEPENDENCY_GRAPH.md) structural contains не враховано як creation ordering.

## 14–18. Apply, state, зміни та rollback

14. Після Manual Apply HCP виконує конкретний reviewed run із доступними credentials, паралельно запускає незалежні graph operations та очікує AWS API completion. Успішний resource create не доводить здоровий Flask/DBTLS/AI runtime; потрібні окремі health/connectivity tests. Audit Apply не запускав.
15. State зберігається окремо у відповідному HCP workspace, містить IDs/configuration і може містити sensitive origin header. HCP state versions/run history не є MySQL backup або ECR image backup. Ручне редагування state не виконувалося.
16. Наступний Plan порівнює новий code/inputs/refresh зі state. Зміна поза Terraform може проявитися як drift; lifecycle ignore_changes для ASGdesired_capacity/service.task_definition навмисно приховує відповідні diff. Останню taskrevision контролює CD, решту serviceinfrastructure — HCP. LT version update не дорівнює автоматичному instance refresh.
17. CIDR/AZ/subnet/VPC/name/AMI та інші зміни можуть спричинити replacements залежно від provider schema/state. count=0 означає destroy керованих instances; RDSdeletionprotection та EC2MySQLprevent_destroy можуть заблокувати операцію. Ресурс, прибраний із code, не стає автоматично безпечною архівацією. Зміна environment/name_suffix має великий blast radius. Точну дію читати в Plan, а не в здогаді про ForceNew.
18. Git revert повертає code, але не AWS/data стан автоматично; HCP має сформувати новий Plan і manual Apply. ECS circuit breaker може повернути попередній успішний deployment, якщо він існує, але не schema/data/secrets/AMI або orphan volumes. Не відкочувати HCP state для «відновлення бази»; DB restore — окрема погоджена процедура. Без retained image та сумісного DBschema application rollback може бути неможливим.

## 19–20. Як завершувати демонстрацію та що оплачується далі

19. Не зупиняти ASG instance вручну в очікуванні довготривалої економії: ASG може відновити min/desiredcapacity. Для app window завершення потрібен reviewed change application_window_open=false/service_enabled=false та окремо дозволений HCP run/apply; Plan має показати ALB/service/DNS alias destruction та ASGcapacity0. Це опис майбутньої процедури, не команда до виконання зараз. Перед змінами перевірити backup, liveconnections та manageddraining. AI lifecycle окремий: ai_enabled=false може видалити instance, залишивши оплачуваний rootvolume. Terraform destroy не пропонується як routine stop.
20. Після EC2 stop продовжують оплачуватися EBS, allocatedIPv4/EIP за застосовними умовами, ALB/LCU/publicIPv4, RDS/DBstorage/backups/managedsecret, S3versions/requests, ECRimages, CloudWatchlogs, DNS та CloudFronttraffic. У цьому root немає NATGW/interfaceendpoints, тому їх hourly немає; S3Gateway без hourly. EC2MySQLprevent_destroy не дозволяє просто переключити DBmode для економії. RetainedAI/DBEBS може стати orphan, не показаним як окремий aws_ebs_volume у state. StopRDS має обмеження й автоматичне відновлення; постійну зупинку не припускати.

[Cost audit](COST_AUDIT.md) відокремлює фактичні ресурси від резервів попередньоїмоделі. HCP/workspace/auth не змінювалися; жодних commands/runs/deployments ця документація не виконувала.

## Первинні джерела

- [Terraform graph internals](https://developer.hashicorp.com/terraform/internals/graph): побудова та обхід graph, provider/explicit/implicit dependencies.
- [HCP VCS settings](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/settings/vcs): workingdirectory/triggers/manualapply; фактичні UI settings не зчитувалися.
- [Validation](https://developer.hashicorp.com/terraform/language/validate): input validation/preconditions блокують operations; Python lexicalcheck їх не виконує.
- [STS calleridentity](https://docs.aws.amazon.com/STS/latest/APIReference/API_GetCallerIdentity.html): account/identity береться з чинних credentials, не з локальної магічної константи.
