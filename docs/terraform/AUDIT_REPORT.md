# Незалежний аудит Terraform ClimateHealth

> Базовий аудит 25.11.2026. Висновки про 11 required inputs, відсутній TLS/ML URL та старі gates описують стан ДО виправлень. Поточні зміни й умовні inputs: [CONTROLLED_DEPLOYMENT](CONTROLLED_DEPLOYMENT.md), результати: [READINESS_REPORT](READINESS_REPORT.md). Старі числові оцінки не є новими вимірюваннями.

25.11.2026. Початковий стан: main5f01e24, чиста й синхронізована з origin/main. Проаналізовано лише активний root infrastructure/terraform та всі вісім дочірніх модулів. Історичні scaffolds не вважаються активними ресурсами.

За повідомленням користувача, HCP уже підключений до GitHub, правильного root та AWS-авторизації. Її спосіб і фактичні IAM permissions не інспектувалися. HCP API/state/run logs, Terraform CLI, Docker та AWS API не викликалися. Немає створених ресурсів, змін workspaces або Git push.

## Метод та охоплення

Фактично викликано Graphify 0.9.104 CLI та Python detect/extract для всіх 21Terraform-файла. Код встановленої версії підтримує Terraform/HCL, detector розпізнав усі файли, але extractor повернув 0 nodes/0 edges: відсутня optional dependency tree_sitter_hcl. Пакети не встановлювалися. [Результат спроби](graphify-attempt.json), [опис методу](graphify-method.json). Створений Graphify sidecar винесено з root у.local-verification.

Реальні діаграми побудовано власним offline lexical/static HCL subset analyzer. Це НЕ Graphify-generated graph, НЕ terraform graph і НЕ Plan. Аналізатор розрізняє blocks/attributes, traversals/templates, count/for_each, depends_on та конкретні bindings inputs/outputs. У JSON кожне ребро має file/line/evidence. Structural contains/module_source edges не визначають порядок створення. Фактичні instance keys, provider schema, state та lifecycle expansion не обчислювалися. Graphify extraction не викликала LLM:0input/0output tokens; це не оцінка токенів написаного звіту.

Baseline:69 resource blocks(68 AWS+1terraform_data),76 variables(27 root+49 child),48 outputs,5locals,7 data sources,8module calls та один provider. Після дозволеного очищення: **74 variables(25 root+49 child),8 data sources**, ті самі 69 resource blocks та 48 outputs. Повні ресурси та variables мають окремі таблиці, а не лише дерево файлів.

## Критичні перед deployment

1. **DB TLS і reader не готові.** RDS вимагає require_secure_transport=ON, але PyMySQL connect у climat.py не налаштовує SSL/CA/hostname verification. Реальні reader credentials, DB initialization/import/restore перебувають поза root. Після service enable readiness може не пройти навіть за правильної мережі. Потрібне окреме погодження DB TLS/reader та application tests; secure transport не вимикали, Flask не змінювали.
2. **Compute capacity не перевірена експериментально.** Micro1 GiB не вміщує default container1024 MiB та reserved512 MiB. Обмеження micro<=256 — лише запобіжник, не доказ працездатності NumPy/Pandas/Fuzzy workload. Small2 GiB правдоподібніший, але потребує вимірювання OS/agent/tmpfs RAM. AWS описує початкове масштабування з нуля до двох instances, а default ASG max1. Початковий min1 може уникнути цього шляху, проте scheduler/rolling поведінку не можна гарантувати без тесту. ASG/CP тут не змінено.
3. **AI runtime integration відсутня.** SG дозволяє TCP8001, але backend task не отримує ML_SERVICE_URL/DNS/CA. Клієнт без URL повертає unavailable. Approved private AI AMI/agent/TLS/token/model не реалізовані цими ресурсами. При AI off це чесне обмеження; при очікуваному inference — deployment blocker. Дозволений порт не є готовою нейромережею.
4. **Немає гарантовано безкоштовного stop mode.** Application window не керує RDS, S3, CloudFront, ECR та IAM/log configuration. AI/EC2MySQL мають delete_on_termination=false: після termination/replacement можуть лишатися orphan EBS. Повторні цикли накопичують диски. Budget alerts та metric alarms не створюються root. Потрібен погоджений stop/retention/billing план, а не автоматичний destroy.

## Важливі покращення — лише пропозиції

| Факт у коді | Наслідок та рекомендація |
|---|---|
|module.backend depends_on=[module.alb] на весь модуль|IAM, cluster, LT та ASG очікують завершення всього ALB module. Розглянути вузький service/listener readiness barrier. Переданий listener_arn усередині backend не використовується.|
|ALB/ASG отримують subnet IDs без прямої залежності від route/association readiness|Subnet creation не гарантує готовий IGW/default route. Розглянути точні dependencies потрібних routes замість очікування всього networking module.|
|Host/AI/backup instance profile залежить від role, не від policy attachments|EC2 startup може початися до permissions propagation. Потрібні точні dependencies та retry в AMI. ECS service уже чекає execution inline policy — це збережено.|
|CloudFront origin — hostname string, не ALB/DNS reference|Terraform cycle немає, але немає й готового origin barrier. При windowfalse API через CloudFront може бути недоступним. Створена distribution не доводить здоровий API.|
|Task definition/LT/IAM/CloudFront існують без service count|Це причина deployment-only required inputs навіть при service off. Після видалення owner/account залишаються 11 required. Відкладення інших компонентів — окреме дизайн-рішення, тут не впроваджене.|
|Host ECS/SSM AWS-managed policies та execution pull для двох ECR repos|Можна звузити permissions після аналізу реальних потреб. Вміст зовнішньої permissions boundary невідомий. Resource* для ecr:GetAuthorizationToken є API особливістю, не автоматичною вразливістю.|
|ECS task trust без SourceAccount/SourceArn conditions|Рекомендовано service-trust hardening. Без аналізу фактичного IAM не стверджувати наявність конкретного cross-account exploit. Налаштовану HCP-авторизацію не змінювати.|
|S3 Gateway endpoint policy не звужена|IAM/bucket policies обмежують доступ, але endpoint не є allowlist лише двох buckets. Можливу нову policy треба перевірити й на ECR layer download; навмання не звужувати.|
|ASG tag лише AmazonECSManaged, LT без tag_specifications|Не гарантовано Project/Environment tags на EC2/volumes, створених ASG. Перевірити cost allocation/tag-based permissions і погодити propagation.|
|LT latest_version без instance_refresh|Нова AMI/userdata версія не означає автоматичне оновлення live host. Потрібен контрольований refresh/draining/rollback workflow.|
|ASG EC2 health та ignore desired_capacity; service ignore task_definition|Здоровий EC2 не означає здоровий task. HCP та application CD мають різні зони відповідальності. Не очікувати від HCP автоматичного відкату останнього image release.|
|Origin header та CloudFront prefix — не user auth|API лишається публічним для viewer. Header є у state/distribution config. Потрібні state access review/auth/quotas. Backend443 до 0.0.0.0/0 не є domain allowlist.|
|ALB→backend HTTP, private AI/DB мають S3-only egress|Немає end-to-end TLS до Flask. Немає підтвердженого SSM/ECR/pip/update шляху з private hosts. Approved AMI contract не дорівнює реалізованим оновленням.|
|Fixed final snapshot name, RDS deletion protection, DB EC2 prevent_destroy|Захист від втрати даних може блокувати delete/switch mode. Повторне snapshot name може конфліктувати. DB restore/retention потребує окремого плану.|
|review_gate не є залежністю AWS resources|False блокує нормальний повний Plan, але targeting може оминути цей вузол. Це не IAM заборона provisioning; не використовувати -target для обходу review.|
|CIDR validation перевіряє форму/кількість, не повне containment|Defaults перевірені. Custom subnets можуть перекриватися або виходити за VPC; потрібні окремі validation/review.|

## Необовʼязкове спрощення

Модулі загалом розділено логічно: networking, security, frontend та workloads. Різницю root call database/backend і каталогів mysql/ecs-backend задокументовано; перейменовувати state addresses заради естетики не потрібно.

Для однієї демонстрації S3/CloudFront+ALB+ASG/CP+RDS складніші за один EC2, але мають навчальну цінність керованого ECS deployment. ALB корисний для HTTPS/health/target registration, проте не є обовʼязковим для самого Flask. Варіант без нього потребує іншого TLS/reverse proxy/origin/deployment рішення. Просто видалити ALB з цього коду недостатньо.

AI інфраструктура не потрібна до benchmark. AI off збережено, але його ECR repo/SG та shared artifact bucket описані наперед. Empty task role можна переглянути як зайвий поточний ресурс без runtime AWS permissions, але видалення ролі та task_role_arn тут не виконано.

Дві public subnets потрібні для ALB, дві private — DB subnet group. Це не два compute/DB nodes: один ASG subnet і Single-AZ RDS лишаються SPOF. Парні ingress/egress SG rules не є випадковими дублікатами; два S3 buckets мають різні access policies. Tagged ECR/S3 noncurrent lifecycle, малі alarms/budget alerts та SPA trailing-slash behavior — подальші окремо погоджувані покращення.

## Цикли, variables та дозволене очищення

Підтримуваний статичний reference graph не показує циклів; structural contains/module_source edges виключено з DAG test. Backend залежить від DB.host, DB EC2 backup IAM — від artifact bucket; frontend не посилається на ALB ID або backend. Тому «CloudFront→API→DB→S3» у traffic diagram не є Terraform cycle. Динамічні instances, provider та state можуть додати залежності, яких цей аналіз не обчислює.

Owner variable та Owner tag видалено; Project/Environment/ManagedBy збережено. Manual aws_account_id замінено data.aws_caller_identity.current.account_id у трьох ARN validations. Data source використає чинні credentials лише під час майбутнього HCP run; зараз STS не викликали. Це не самостійний expected-account guard. Решта ресурсів, gates/defaults та авторизація не змінювалися.

## Навігація

- [AWS architecture](ARCHITECTURE_GRAPH.md), [dependency graph/DOT](DEPENDENCY_GRAPH.md), [network traffic](NETWORK_GRAPH.md).
- [Усі resource blocks](RESOURCES_AUDIT.md), [усі variables](VARIABLES_REFERENCE.md), [data sources/locals/outputs](MODULES_REFERENCE.md).
- [13 required diagnostics](REQUIRED_VARIABLES_AUDIT.md), [життєвий цикл](HOW_TERRAFORM_WORKS.md), [cost audit](COST_AUDIT.md).

Першоджерела: [ECS scaling](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/managed-scaling-behavior.html), [RDS versions](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/MySQL.Concepts.VersionMgmt.html), [Terraform graph](https://developer.hashicorp.com/terraform/internals/graph), [validation](https://developer.hashicorp.com/terraform/language/validate), [STS identity](https://docs.aws.amazon.com/STS/latest/APIReference/API_GetCallerIdentity.html), [AWS ASG provider docs](https://raw.githubusercontent.com/hashicorp/terraform-provider-aws/v6.74.0/website/docs/r/autoscaling_group.html.markdown). Конкретні file/line/evidence наведено в JSON та таблицях. Exact replacement/update/destroy визначить provider Plan, якого тут не запускали.

## Уточнення: декларації проти service-managed objects

Відсутні власні application/budget alarm blocks, але ECS managed scaling створює CloudWatch metrics/alarms/scaling policy та використовує service-linked role. ASG/ALB/RDS також створюють дочірні EC2/EBS/ENI/IP/secret objects, не представлені окремими HCL blocks. Тому69declarations не є повною кількістю AWS account objects чи bill dimensions. Це уточнення враховано в architecture та cost audit; resource dependency graph навмисно показує лише source declarations, не вигадані provider-side nodes. [Першоджерело](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/cluster-auto-scaling.html).
