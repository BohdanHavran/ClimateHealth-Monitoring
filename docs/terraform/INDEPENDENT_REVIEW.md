# Незалежний архітектурний review Terraform

26.11.2026. **Висновок: потрібне спрощення перед першим deployment, але не сліпа заміна всіх модулів референсом.** ECS EC2/ALB/private RDS/S3 OAC як набір сервісів логічні; надмірність переважно у control plane:11 booleans, дві DB реалізації, непідтверджені runtime contracts та широкі review dependencies. Це read-only аудит конфігурації, не звіт про реальні AWS ресурси.

## 1. Scope, інструкції та інструменти

- Перевірено global `C:/Users/danoh/.codex/AGENTS.md`; він відповідає наданим користувачем принципам простоти/reference-first/state safety. Додаткових AGENTS.md/AGENTS.override.md у workspace/проєкті/підкаталогах і перевірених батьківських директоріях не знайдено. Директорія `.agents`/runtime catalog сама по собі не додає прихованих дозволів. System/developer rules мають пріоритет, поточна пряма заборона користувача виключає commit/push/refactor/запуски.
- `karpathy-guidelines`: локальний SKILL.md прочитано; застосовано як compatible guidance, а не окрему executable перевірку. `ponytail-review`5.3.3 знайдено у plugin cache й прочитано; використано перевірку correctness/safety/lean з source evidence. Обидва не були перелічені у стартовому host catalog; доступність файлів не називаємо окремим runtime tool registration.
- `ecc:terraform-patterns` та `ecc:security-review` — доступні Skills, прочитано релевантні інструкції. Приклади env roots/S3 backend не застосовувалися, бо суперечили погодженому one root/HCP workflow. Security Audit прочитано в guidance mode для вузької пасивної IAM/network/secrets перевірки; повний app penetration workflow не запускався.
- Додатковий Codex агент типу security_reviewer справді викликаний і незалежно прочитав root/усі 8 modules/повʼязані TLS/ML clients/release draft. Він повернув source findings без запису файлів. Це додаткова незалежна перевірка, не новий сервіс і не доказ runtime validation.
- `graphify --version` реально викликано:0.9.104. У його власному interpreter `C:/Users/danoh/AppData/Roaming/uv/tools/graphifyy/Scripts/python.exe` tree_sitter_hcl відсутній; extractor `graphify/extractors/terraform.py:197–200` повертає missing grammar. Новий native graph не будувався. Використано наявний `scripts/audit_terraform.py.build` та зіставлено з 303 nodes/918 edges inventory. Graphify dependency не встановлювалася, результат не називається Graphify graph або Terraform Plan.
- Python stdlib/file search/Git read-only — inventory, source evidence, counts і hashes. Claude Mem використано для work-state/checkpoint; Headroom не викликався, бо targeted reads достатні. Не запускали UI/UX/документні Skills, Terraform/Docker/HCP/AWS/DB або application servers.

Baseline: `main=09f2d790f5668a40d17d2ae5960ca9e20ffc1d3c`, origin/main локально 5f01e24, ahead1, чисто на початку. Віддалені refs/state/UI не опитувалися. Значення реальних секретів не читалися/не копіювалися у звіт. Навантаження: короткі демонстрації, невелика кількість користувачів, без вимоги HA/zero-downtime, AI та навчена модель відсутні.

## 2. Findings — виправити перед відповідним сценарієм

### 1. Origin header допускає wildcard або завелике значення — P1 для API exposure

**Що це:** друга перевірка ALB після CloudFront prefix-list SG. **Проблема:** root variable.tf:101–108 перевіряє лише length>=32, але modules/alb/main.tf:59–69 передає його прямо у http_header.values. Наприклад,31 літера плюс один `*` проходять validation і задають prefix-pattern замість точного секретного значення;129 символів також проходять root validation, але перевищують API limit128. Приклад із 32 зірочок не слід називати доведеним bypass: AWS обмежує правило 6 wildcard characters, отже може відхилити такий input. У цьому аудиті ALB requests не виконувалися. Це source-confirmed некоректна допустима конфігурація, не доказ слабкого реального secret.

**Найменше виправлення:** генерований випадковий URL-safe рядок 32–128 символів без `*`, `?`, whitespace/control; зберегти sensitive state handling і SG prefix list. **Якщо не виправити:** випадковий pattern може послабити origin protection для некоректно обраного шаблону, або Apply завершиться помилкою. ALB condition порівнює value без урахування регістру, тому не рахувати mixed-case entropy як case-sensitive. Джерела: [AWS HttpHeaderConditionConfig](https://docs.aws.amazon.com/elasticloadbalancing/latest/APIReference/API_HttpHeaderConditionConfig.html), [ALB quotas](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-limits.html).

Код: [root validation](../../infrastructure/terraform/variable.tf#L101), [listener rule](../../infrastructure/terraform/modules/alb/main.tf#L59), [CloudFront header](../../infrastructure/terraform/modules/frontend/main.tf#L107). Код не змінено.

### 2. EC2 MySQL branch несумісна з поточним TLS contract — P1 лише при database_mode=ec2

**Що це:** альтернативний DB host. **Проблема:** mysql/main.tf:90 повертає private_ip, але ecs-backend/main.tf:219–221 завжди передає regional RDS CA та verify_identity. Власний MySQL cert на EC2 не довірений RDS CA, й IP зазвичай не збігається з DNS SAN. Вхідних параметрів custom DB CA/DNS у module contract немає. Це не спростовує RDS TLS path.

**Найменше виправлення:** для погодженого RDS target після read-only state inventory вилучити EC2 DB альтернативу та її IAM/AMI inputs. Якщо EC2 DB справді потрібна, потрібний окремий перевірений DNS/CA/backup contract. **Якщо не виправити:** дозволений Terraform mode не дає працездатного secure DB connection. [DB output](../../infrastructure/terraform/modules/mysql/main.tf#L90), [task TLS](../../infrastructure/terraform/modules/ecs-backend/main.tf#L219), [Python verification](../../climate_health/tls.py#L34).

## 3. Важливі покращення

### 3.11 gates — зайвий ручний workflow, не додатковий IAM захист

**Що це:** 5 persistent provisioning,3 activity,2 review й 1 surge booleans. **Проблема:** оператор має розрізняти створення, зупинку та видалення між 11 прапорцями; проста false для provisioned на stateful ресурсі блокує весь Plan. Формально 2048 boolean комбінацій, більшість не потрібна demo; це не 2048 валідних deployment states.

**Виправлення:** stable network/storage/RDS без щоденних creation switches; один `deploy_application`, один desired_count0/1, один explicit max_instances1/2, optional AI object. Manual Apply замість review boolean. **Наслідок без змін:** більше помилок конфігурації й важче читати Plan. Не відключати prevent_destroy/backup, щоб зменшити flags. Див. [main gates](../../infrastructure/terraform/main.tf#L6) та [proposal](SIMPLIFICATION_PROPOSAL.md).

### 4. Review resource додає широкі залежності й може приховувати Plan values

Усі 8 module calls мають depends_on=[terraform_data.review_gate] (main.tf:39–127). На першому Plan pending create review_gate може відкласти child AZ/prefix-list/managed-policy data reads до Apply. Це source-confirmed broad dependency; точний generated Plan не бачили. [HashiCorp](https://developer.hashicorp.com/terraform/language/meta-arguments/depends_on) рекомендує посилання на конкретні значення замість широкого module dependency.

Найменше рішення — HCP Manual Apply/permissions і предметні validation без review resource. Profile→IAM policy та subnet-output→routes dependencies залишити: вони мають реальний readiness сенс. Вже прибраний ALB-wide barrier не додавати назад. Символічний граф не має підтримуваних unresolved traversals/циклів; це не доказ коректного expanded Terraform graph.

### 5. Bootstrap Capacity Provider не гарантований одночасним увімкненням усіх flags

ASGdesired1 може запускати host до створення CP (ecs-backend:158–203). AWS рекомендує новий empty ASG, потім CP association, потім scale-out: [AWS CP](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/asg-capacity-providers.html). Поточний backend_provisioned=true/service_enabled=false bootstrap рухається у правильному напрямку, але обмеження не примушує оператора зробити два Apply. Це needs-runtime-validation ризик, не доведений збій.

Спрощений deploy_application=true/backend_desired_count=0 має спершу дати empty ASG з max>=1 і service desired0; після перевірки CP — desired1. Не створювати новий boolean тільки для такого runbook. ASG desired ignore_changes виправданий при managed scaling, але min/max повинні узгоджуватись із restart/stop протоколом. [Source](../../infrastructure/terraform/modules/ecs-backend/main.tf#L158).

### 6. Resource defaults не доводять rolling deployment

Static host8080 дозволяє лише 1 task на host. Dynamic hostPort0 розвʼязує port collision, але 2×1024 MiB+512 MiBreserve=2560 MiB>2048 MiB t3.small. CPU256 — container shares/reservation, не dedicated core; Standard CPU credits можуть throttling. `tmpfs` і peak imports треба виміряти.

Залишити fixed8080 й допустимий downtime для demo. Для rolling — тимчасовий другий t3.small, max2, min100/max200 після CP verification; не постійно більший host. Dynamic ports — альтернатива після memory benchmark і SG range review, не безкоштовний спосіб zero-downtime. AWS підтримує dynamic bridge registration instanceID:port: [ALB/ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/alb.html). LT update не виконує Instance Refresh автоматично; потрібний окремо погоджений draining/refresh test. [Source](../../infrastructure/terraform/modules/ecs-backend/main.tf#L214).

### 7. CI/CD ownership визначено, але узгодженого application deployment ще немає

Нині HCP керує task_definition у service:ecs-backend/main.tf234, ignore для цього поля відсутній. `.example` release draft із HOLD усе ще register-task-definition/update-service (lines89–112), але workflow disabled і не в.github/workflows. **Активного конфлікту зараз немає.** Його бездумна активація створить competing writers.

Для demo: Actions тестує/будує/push image до ECR, публікує digest; оператор змінює backend_image для HCP Plan/Manual Apply. Frontend Actions керує лише object uploads/cache headers/invalidation, Terraform — buckets/OAC/distribution/policies. AI deployment відкладено. Окремий hybrid із image-only app releases можливий пізніше, але потрібні погоджені templates/env/secrets reconciliation; одного ignore_changes недостатньо. [Draft](../../infrastructure/ci/application-release.yml.example#L1).

### 8. AI resources — не готова AI інтеграція

AI module має EC2/S3-read IAM/profile/power state, без private DNS/cert/TLS server/shared-token delivery/agent install. ML URL input і SG8001 — contracts, не готові сервіси. ai_runtime_reviewed=true перевіряє лише bool, а не AMI. При ai_provisioned=true/ai_enabled=false EC2 спочатку створюється running, потім stopped: це все ж compute запуск і retained20 GB EBS. [AI](../../infrastructure/terraform/modules/ai/main.tf#L43).

Рішення: AI object=null у demo, повертати unavailable як зараз. Перед ввімкненням узгодити AMI+privateDNS/TLS+token delivery+S3 reconciliation та CPU/RAM benchmark. Не додавати CloudMap/NAT/багато gates наперед. Не видаляти вже створений AI/stateful disk без state check.

### 9. Чистота contracts і перевірок

`module.alb.var.name` не має жодного consumer — обидва name_prefix фіксовані ch-. Прибрати unused input/argument у наступному рефакторингу. `listener_arn` — rule ARN; залежність корисна, назву уточнити. Root backend_instance_type допускає micro, але review gate його потім забороняє; task_memory validation допускає значення, які не пройдуть gate на small. Узгодити правила в одному місці.

Root subnet validation перевіряє синтаксис і різні строки, але не containment та overlap між public/private; наприклад public10.42.0.0/24 і private10.42.0.0/24 проходять поточні окремі checks. Це validation gap, не твердження про помилкові defaults. Простіше derive subnet CIDRs із VPC через cidrsubnet для фіксованої topology або додати явну перевірку. Зміна AZ/CIDR у наявному state потребує replacement review.

Validation backend_image перевіряє тільки закінчення `@sha256:<64hex>` (variable.tf:43), а не registry/account/repository. Вона не доводить, що digest належить погодженому ECR. До release узгодити registry/repository allowlist і перевірку існування digest; не називати поточний regex перевіркою походження образу.

19 root outputs і 29 child outputs самі не є проблемою вартості. Залишити endpoints/IDs, які реально використовує оператор/CI; майбутні role outputs можна відкласти разом із відповідними компонентами. Host/execution roles мають різні principals; не обʼєднувати їх заради count. Empty task role — кандидат на вилучення, доки app не викликає AWS API. Не створювати generic IAM factory для двох ролей.

## 4. Вісім модулів: чи потрібні

| Current module call / source | Функція | Рекомендація |
|---|---|---|
| networking /networking | VPC, subnets, routes, S3 endpoint | Залишити; адаптувати перевірені прості reference patterns |
| security /security | SG і правила | Зміст потрібний; можна обʼєднати з networking без зміни мережі |
| ecr /ecr | Image repository lifecycle | Залишити адаптований reference; AI repo умовно при AI |
| database /mysql | RDS або EC2 MySQL | Залишити RDS-only; не створювати 3 backup IAM resources для невикористаного EC2 mode |
| frontend /frontend | S3, OAC, CF, SPA/API routing | Залишити; розділяти storage/CDN лише при реальному reuse, не через умовніетапи |
| alb /alb | TG, HTTPS, originprotection | Залишити для ECS API; без нього потрібен TLS/proxy/стабільний endpoint на host |
| backend /ecs-backend | ECS, ASG, CP, LT, task, IAM | Звузити доодного EC2 workload; не додавати Fargate branch уцей модуль |
| ai /ai | Майбутній приватний host | Відкласти виклик до готовності runtime; existing state невідомий |

## 5. Network/security: налаштовано проти припущено

| Потік / контроль | Статично задано | Не доведено цим аудитом |
|---|---|---|
| Browser→CF | HTTPS/redirect viewer policies | Реальний distribution/браузерний smoke |
| CF→S3 | OAC SigV4, private BPA, SourceArn allow, TLSdeny | Actual bucket objects/IAM/доступ без CDN |
| CF→ALB | custom originHTTPS, ACMARN, originheader; SG CloudFront prefix list | Certificate issued/SAN/DNS, header secrecy та fixfinding1 |
| ALB→backend | SG8080, instance targets, container8000 | ECS registration/health/memory/CP/draining |
| backend→RDS | SG3306, private RDS, TLSrequired, verified CA inimage | Reader/schema/SSM values/KMS/restore та liveTLS |
| backend→AI | SG8001, HTTPS client/token reference | DNS certSAN/serverTLS/token delivery/модель |
| backend/host→internet | public hostIP+IGW, egress443 | ECRagent/logSSM/Open-Meteo IAM/runtime/quotas |
| AI/EC2 DB→S3 | Gatewayendpoint+S3 prefixSG+scopedIAM | S3 agent та signed update/backup restore |

No NAT є коректним для public ECS host у bridge mode і private RDS. AI без NAT може користуватися S3 endpoint, але не довільним internet, ECR API, SSM чи CloudWatch endpoints. Додавати interface endpoints/NAT без нового runtime requirement не слід. CloudFront prefixlist довіряє origin traffic усіх distributions, тому originheader не можна вважати зайвим. SG не виконує authentication або TLS.

IAM execution policy обмежує ECR repos/log group/SSM ARN; GetAuthorizationToken Resource* є API necessity, а не автоматично fullECR. Host AWS-managed ECS/SSM policies ширші, ніж app needs, але обмежені instance principal/boundary. Boundaries фактичні permissions не інспектувалися; ARN match не доводить leastprivilege. CMK encrypted SSM потребує scoped kms:Decrypt, якого currentexecutionpolicy не додає; deployment під таку конфігурацію — externalprerequisite. Secret values не зберігаються в Git, але originheader залишається у sensitiveHCPstate.

## 6. Повний review33 rootvariables

Root variables надходять із HCP/defaults; child variables — внутрішні module inputs, їх не треба задавати вдруге в UI. Нижче «HCP» означає Terraform input, не нову auth envvariable. «Обчислити» не означає, що read може виконуватися offline. Manual owner/aws_account_id не повертати; calleridentity використовується лише для ARN checks.

| Variable / код | Type | Default | Навіщо / target | HCP зараз | Обчислити / дублювання | Простіша конфігурація |
|---|---|---|---|---|---|---|---|---|
| [environment](../../infrastructure/terraform/variable.tf#L1) | `string` | `немає — required` | Naming і provider tags усіх taggable resources | Так, required | Не вгадувати із назви workspace | Залишити dev/production |
| [aws_region](../../infrastructure/terraform/variable.tf#L9) | `string` | `немає — required` | AWS provider, logging, ARN region checks | Так, required | Не брати ambient region; підтримано лише us-east-1 | Залишити explicit input; це не авторизація |
| [name_suffix](../../infrastructure/terraform/variable.tf#L19) | `string` | `немає — required` | local.name, S3 names, IAM names | Так, required | Random generator додав би зайвий provider/state | Залишити один стабільний naming suffix |
| [infrastructure_reviewed](../../infrastructure/terraform/variable.tf#L28) | `bool` | `false` | terraform_data.review_gate і всі module barriers | True після ручного review | Дублює Manual Apply process; не IAM boundary | Прибрати assertion із коду, зберегти review Plan у HCP |
| [service_enabled](../../infrastructure/terraform/variable.tf#L33) | `bool` | `false` | ECS desired_count, ASG min/max | При запуску backend | Частково перетинається з window, але desired0 корисний | Замінити backend_desired_count0/1 |
| [backend_image](../../infrastructure/terraform/variable.tf#L38) | `string` | `null` | aws_ecs_task_definition.initial image | При backend_provisioned | Digest має надавати build CI; не вигадувати | Залишити conditional immutable digest |
| [ecs_ami_id](../../infrastructure/terraform/variable.tf#L48) | `string` | `null` | aws_launch_template.host.image_id | При backend_provisioned | AL2023 SSM lookup можливий, але потрібні pin/refresh review | Залишити approved AMI або погоджений lookup protocol |
| [backend_instance_type](../../infrastructure/terraform/variable.tf#L58) | `string` | `"t3.small"` | Launch Template instance_type | Лише при override | Не визначається автоматично; micro суперечить gate | Спочатку local t3.small, input повернути після benchmark |
| [task_memory_mib](../../infrastructure/terraform/variable.tf#L67) | `number` | `1024` | Container hard memory і placement | Лише при override | RAM визначає вимірювання, не назва моделі | Local1024 MiB; змінювати за результатами benchmark |
| [allow_deployment_capacity](../../infrastructure/terraform/variable.tf#L76) | `bool` | `false` | ASG max1/2 та ECS deployment percentages | При rolling surge | Це capacity choice, не ще один review flag | Замінити backend_max_instances1/2 |
| [origin_hostname](../../infrastructure/terraform/variable.tf#L81) | `string` | `null` | Route53 alias та CloudFront API origin | При window | ALB DNS не замінить hostname, покритий ACM certificate | Залишити approved DNS hostname |
| [origin_certificate_arn](../../infrastructure/terraform/variable.tf#L91) | `string` | `null` | ALB HTTPS listener | При window | Lookup можливий, але кілька certs/status/domain неоднозначні | Залишити перевірений ARN та account/region checks |
| [origin_verification_header](../../infrastructure/terraform/variable.tf#L101) | `string` | `null` | ALB header rule і CloudFront custom header | При window, sensitive | Не обчислювати із публічних names; потрібне випадкове значення | Залишити 32–128 URL-safe символів без wildcards |
| [runtime_secret_arns](../../infrastructure/terraform/variable.tf#L112) | `map(string)` | `{}` | Execution SSM policy та ECS task secrets | DB reader при backend; ML token при ML URL | Values не обчислює Terraform; lookup paths можливий, явні ARNs прозоріші | Залишити map ARN; узгодити дозволені keys, не plaintext |
| [database_mode](../../infrastructure/terraform/variable.tf#L122) | `string` | `"rds"` | Counts RDS/EC2 DB та endpoint output | Лише якщо обрано EC2 | Зайва альтернатива для цільового RDS-only | Прибрати mode і EC2 branch після state inventory |
| [mysql_ami_id](../../infrastructure/terraform/variable.tf#L131) | `string` | `null` | aws_instance.mysql | Лише для EC2 DB | Для RDS не потрібна | Прибрати разом із EC2 DB branch |
| [ai_enabled](../../infrastructure/terraform/variable.tf#L140) | `bool` | `false` | aws_ec2_instance_state.power.state | При створеному AI | Power відрізняється від existence, але 3 AI flags зайві | ai.running у typed object; null не є stop |
| [ai_ami_id](../../infrastructure/terraform/variable.tf#L145) | `string` | `null` | AI aws_instance.this.ami | При ai_provisioned | Regex не перевіряє TLS/agent runtime | ai.ami_id лише перед фактичним AI deployment |
| [ai_instance_type](../../infrastructure/terraform/variable.tf#L154) | `string` | `"t3.small"` | AI EC2 instance_type | Лише при AI override | Автоматичний вибір неможливий без benchmark | ai.instance_type із reviewed default |
| [application_window_open](../../infrastructure/terraform/variable.tf#L163) | `bool` | `false` | ALB/DNS/service counts та CF API origin | Для API window | Перетинається з backend/edge/service flags | Один deploy_application для ephemeral API resources |
| [origin_zone_id](../../infrastructure/terraform/variable.tf#L169) | `string` | `null` | aws_route53_record.origin.zone_id | При window | Lookup можливий, але існують кілька zones/різні дозволи | Залишити existing zone ID, не купувати домен |
| [permissions_boundary_arn](../../infrastructure/terraform/variable.tf#L179) | `string` | `null` | Host/execution/task/AI/EC2 DB IAM roles | При створенні відповідних IAM roles | Governance policy не обчислюється з account ID | Погодити optional/required згідно governance; least privilege зберегти |
| [vpc_cidr](../../infrastructure/terraform/variable.tf#L189) | `string` | `"10.42.0.0/16"` | aws_vpc.this.cidr_block | Лише при override | Root і child defaults повторюються, але це не два HCP inputs | Один network input із предметною validation |
| [public_subnet_cidrs](../../infrastructure/terraform/variable.tf#L198) | `list(string)` | `["10.42.0.0/24", "10.42.1.0/24"]` | aws_subnet.public[*] | Лише при override | Можна derive через cidrsubnet для fixed2 AZ topology | Прибрати public input або додати containment/overlap checks |
| [private_subnet_cidrs](../../infrastructure/terraform/variable.tf#L207) | `list(string)` | `["10.42.10.0/24", "10.42.11.0/24"]` | aws_subnet.private[*] | Лише при override | Те саме; public і private CIDRs не семантичні дублікати | Derive окремі ranges; будь-яка state зміна через Plan review |
| [artifacts_provisioned](../../infrastructure/terraform/variable.tf#L218) | `bool` | `false` | ECR та S3 counts/for_each | Для першого створення | Не потрібний щоденний switch для persistent storage | Stable ECR/S3 без creation gate; prevent_destroy зберегти |
| [database_provisioned](../../infrastructure/terraform/variable.tf#L223) | `bool` | `false` | MySQL resource counts | Для першого DB provisioning | Це не команда RDS stop | Stable RDS, backups/deletion protection, окремий teardown |
| [edge_provisioned](../../infrastructure/terraform/variable.tf#L228) | `bool` | `false` | CloudFront/OAC/cache/function counts | Для CDN provisioning | Frontend CDN не потребує частого вимкнення | Stable CF; API origin за deploy_application |
| [backend_provisioned](../../infrastructure/terraform/variable.tf#L233) | `bool` | `false` | Усі backend resources count | Для backend base | Bootstrap можна описати desired0/1 без додаткового provision flag | Один app gate; retained logs поза destructive gate |
| [ai_provisioned](../../infrastructure/terraform/variable.tf#L238) | `bool` | `false` | AI role/profile/instance/power counts | Для AI existence | Optional existence осмислена, окремий bool не потрібний | ai=null або typed object, з state protection |
| [ai_runtime_reviewed](../../infrastructure/terraform/variable.tf#L243) | `bool` | `false` | Root review precondition | True після ручного AI review | Не перевіряє runtime; дублює процес погодження | Runbook acceptance criteria замість Terraform assertion |
| [ml_service_url](../../infrastructure/terraform/variable.tf#L248) | `string` | `null` | Task ML URL та allowed host | При підключенні ML | Не derive HTTPS із private IP, потрібний DNS/certificate | ai.service_url; external input тільки за нової вимоги |
| [ml_tls_ca_file](../../infrastructure/terraform/variable.tf#L257) | `string` | `null` | Task ML_TLS_CA_FILE | Лише при private CA | Довірений CA має бути у image, не derive із DNS | ai.ca_file; null для system trust |

### Gates: класифікація та спрощення

Persistent creation: artifacts/database/edge/backend/ai_provisioned (5). Runtime activity: service_enabled/application_window_open/ai_enabled (3). Human assertions: infrastructure_reviewed/ai_runtime_reviewed (2). Surge: allow_deployment_capacity (1). Вони не всі дублюють одне одного, але разом утворюють надмірний ручний workflow.

Stateful ресурси з prevent_destroy не потребують доступного оператору false для звичайної зупинки. Вимкнення API має торкатися ephemeral compute/ALB/DNS/API behavior; logs залишаються поза цим gate. Для існуючого state змінювати guards/addresses можна тільки після інвентаризації. Заміна 11 booleans на 16 root inputs загалом не означає, що прихована object complexity зникла: поля AI object показано у proposal явно.

## 7. Усі 22 moved blocks та state safety

Вони додані в 09f2d79, бо resources backend/frontend змінилися з unindexed на count[0]. Це конкретна syntactic migration rationale, але **наявність старих addresses у HCP state не встановлена**. Доступу до state через підключені read-only інструменти не отримано; HCP/UI/API не опитувалися. У новому доведено порожньому state ці 22 moves нічого не переносять і не потрібні для створення. Наявність локального Gitcommit не доводить, що відповідний state колись існував.

| From (повна module address) | To | Джерело | Старий state існував? |
|---|---|---|---|
| `module.backend.aws_ecs_cluster.this` | `module.backend.aws_ecs_cluster.this[0]` | [infrastructure/terraform/modules/ecs-backend/main.tf:273](../../infrastructure/terraform/modules/ecs-backend/main.tf#L273) | Неперевірено |
| `module.backend.aws_iam_role.host` | `module.backend.aws_iam_role.host[0]` | [infrastructure/terraform/modules/ecs-backend/main.tf:277](../../infrastructure/terraform/modules/ecs-backend/main.tf#L277) | Неперевірено |
| `module.backend.aws_iam_role_policy_attachment.agent` | `module.backend.aws_iam_role_policy_attachment.agent[0]` | [infrastructure/terraform/modules/ecs-backend/main.tf:281](../../infrastructure/terraform/modules/ecs-backend/main.tf#L281) | Неперевірено |
| `module.backend.aws_iam_role_policy_attachment.ssm` | `module.backend.aws_iam_role_policy_attachment.ssm[0]` | [infrastructure/terraform/modules/ecs-backend/main.tf:285](../../infrastructure/terraform/modules/ecs-backend/main.tf#L285) | Неперевірено |
| `module.backend.aws_iam_instance_profile.host` | `module.backend.aws_iam_instance_profile.host[0]` | [infrastructure/terraform/modules/ecs-backend/main.tf:289](../../infrastructure/terraform/modules/ecs-backend/main.tf#L289) | Неперевірено |
| `module.backend.aws_iam_role.execution` | `module.backend.aws_iam_role.execution[0]` | [infrastructure/terraform/modules/ecs-backend/main.tf:293](../../infrastructure/terraform/modules/ecs-backend/main.tf#L293) | Неперевірено |
| `module.backend.aws_iam_role.task` | `module.backend.aws_iam_role.task[0]` | [infrastructure/terraform/modules/ecs-backend/main.tf:297](../../infrastructure/terraform/modules/ecs-backend/main.tf#L297) | Неперевірено |
| `module.backend.aws_cloudwatch_log_group.backend` | `module.backend.aws_cloudwatch_log_group.backend[0]` | [infrastructure/terraform/modules/ecs-backend/main.tf:301](../../infrastructure/terraform/modules/ecs-backend/main.tf#L301) | Неперевірено |
| `module.backend.aws_iam_role_policy.execution` | `module.backend.aws_iam_role_policy.execution[0]` | [infrastructure/terraform/modules/ecs-backend/main.tf:305](../../infrastructure/terraform/modules/ecs-backend/main.tf#L305) | Неперевірено |
| `module.backend.aws_launch_template.host` | `module.backend.aws_launch_template.host[0]` | [infrastructure/terraform/modules/ecs-backend/main.tf:309](../../infrastructure/terraform/modules/ecs-backend/main.tf#L309) | Неперевірено |
| `module.backend.aws_autoscaling_group.host` | `module.backend.aws_autoscaling_group.host[0]` | [infrastructure/terraform/modules/ecs-backend/main.tf:313](../../infrastructure/terraform/modules/ecs-backend/main.tf#L313) | Неперевірено |
| `module.backend.aws_ecs_capacity_provider.host` | `module.backend.aws_ecs_capacity_provider.host[0]` | [infrastructure/terraform/modules/ecs-backend/main.tf:317](../../infrastructure/terraform/modules/ecs-backend/main.tf#L317) | Неперевірено |
| `module.backend.aws_ecs_cluster_capacity_providers.this` | `module.backend.aws_ecs_cluster_capacity_providers.this[0]` | [infrastructure/terraform/modules/ecs-backend/main.tf:321](../../infrastructure/terraform/modules/ecs-backend/main.tf#L321) | Неперевірено |
| `module.backend.aws_ecs_task_definition.initial` | `module.backend.aws_ecs_task_definition.initial[0]` | [infrastructure/terraform/modules/ecs-backend/main.tf:325](../../infrastructure/terraform/modules/ecs-backend/main.tf#L325) | Неперевірено |
| `module.frontend.aws_s3_bucket.frontend` | `module.frontend.aws_s3_bucket.frontend[0]` | [infrastructure/terraform/modules/frontend/main.tf:178](../../infrastructure/terraform/modules/frontend/main.tf#L178) | Неперевірено |
| `module.frontend.aws_s3_bucket.artifacts` | `module.frontend.aws_s3_bucket.artifacts[0]` | [infrastructure/terraform/modules/frontend/main.tf:183](../../infrastructure/terraform/modules/frontend/main.tf#L183) | Неперевірено |
| `module.frontend.aws_cloudfront_origin_access_control.this` | `module.frontend.aws_cloudfront_origin_access_control.this[0]` | [infrastructure/terraform/modules/frontend/main.tf:188](../../infrastructure/terraform/modules/frontend/main.tf#L188) | Неперевірено |
| `module.frontend.aws_cloudfront_cache_policy.assets` | `module.frontend.aws_cloudfront_cache_policy.assets[0]` | [infrastructure/terraform/modules/frontend/main.tf:193](../../infrastructure/terraform/modules/frontend/main.tf#L193) | Неперевірено |
| `module.frontend.aws_cloudfront_function.routes` | `module.frontend.aws_cloudfront_function.routes[0]` | [infrastructure/terraform/modules/frontend/main.tf:198](../../infrastructure/terraform/modules/frontend/main.tf#L198) | Неперевірено |
| `module.frontend.aws_cloudfront_distribution.this` | `module.frontend.aws_cloudfront_distribution.this[0]` | [infrastructure/terraform/modules/frontend/main.tf:203](../../infrastructure/terraform/modules/frontend/main.tf#L203) | Неперевірено |
| `module.frontend.aws_s3_bucket_policy.frontend` | `module.frontend.aws_s3_bucket_policy.frontend[0]` | [infrastructure/terraform/modules/frontend/main.tf:208](../../infrastructure/terraform/modules/frontend/main.tf#L208) | Неперевірено |
| `module.frontend.aws_s3_bucket_policy.artifacts` | `module.frontend.aws_s3_bucket_policy.artifacts[0]` | [infrastructure/terraform/modules/frontend/main.tf:213](../../infrastructure/terraform/modules/frontend/main.tf#L213) | Неперевірено |

Збереження коректних moves не створює AWS ресурс самостійно; видалення може спричинити recreate для старих stateaddresses. Для confirmedemptystate можна прибрати speculative migration baggage; якщо хоч один workspace міг застосовувати попередній код, лишити moves до перевірки всіхспоживачів. Майбутнє mergingnetwork/security чи rootloggroup потребує нового конкретного mapping, а неширокого шаблону state mv.

| Механізм | Фактичне використання | Ризик / оцінка |
|---|---|---|
| prevent_destroy | S3, ECR, RDS, EC2 DB, AI, backendlogs | Корисний blocker, але не backup/IAM. Видалення resourceblock прибирає guard; falsecount можеблокувативесь Plan |
| ignore_changes | ASGdesired_capacity | Обґрунтованоспільним CPownership; max/min ще TF керовані. Taskdefinitionignore відсутній |
| count | Provisionflags,2 subnets, conditionalALB/DNS/services | Зміна count0→1 має address[0]; зміна flags можевимагати destroy. Defaultsfalse неєдоказомвідсутнього state |
| for_each | ECRrepos,2 S3 buckets/securityS3 rules/ASGtags | Keys у current статичні/з inputs; непідтвердженого invalidfor_each нестверджуємо. Зміна repo/bucketkeys→replace |
| depends_on | Reviewgate, profilepolicy, routereadiness, ECSCP/policy | Прибратилише reviewbarriers; зберегтиреальнуприховануготовність |
| precondition | Reviewstages, AMIreadiness, listener readiness | Boolassertions недоводять AWSreadiness; listenerprecondition маєреальнезначенняз output |
| aws_ec2_instance_state | AIpower, running/stopped | Зупиняєпіслястворення, неприпиняє EBScharges. Неавтоматизує DBstop/modeldeployment |

Порядок create визначається атрибутними dependencies:VPC→subnets/routes/SG; ALB→listener/rule→DNS→CFAPIorigin; ASG→CPassociation→service; DBendpoint→taskdefinition. Незалежні ECR/DB/storage непотрібнозвʼязуватиодним serialpipeline. CloudFront→APIorigin неєдоказом, щосервіс healthy; listener зʼявляєтьсяранішепрацездатного Flask.

## 8. HCP і рівні доказів

| Рівень | Що підтверджено / що перевіряти |
|---|---|
| Статично | One root,8 local sources, provider pin, відсутність credentials/backend block;33/60 variables,22 moves, references; ownership та незмінність source hashes |
| Terraform Validate | Повна HCL grammar, schema Provider6.74, types/dynamic blocks, cross-variable validation, moved syntax. Не виконано |
| Remote Plan | AWS identity/read permissions/AMI/ACM/engine availability; фактичні state/moves/replacements/destroys; unknown values та кошторис. Не виконано |
| AWS runtime | ECS memory/CPU/CP bootstrap/scale-from-zero/rolling/refresh; RDS reader/schema/TLS/restore; AI DNS/TLS/token/agent. Не перевірено |

HCP підтримує модель одного VCS root; це не доводить, що конкретний код пройде Plan. Working Directory — infrastructure/terraform, окремі dev/production state/inputs/permissions, Manual Apply. Авторизація вже налаштована; нових auth environment variables не пропонуємо. Init/Validate/Plan/Apply не запускалися; UI/workspaces не читалися й не змінювалися.

Root .terraform.lock.hcl відсутній. Exact provider version pin є, але checksum lock ще не перевірений/не закомічений. Отримати його після погодженого HCP Init без локального Terraform. Це крок відтворюваності, а не встановлений runtime defect.

## 9. Вартість і пропорційність

70 resource blocks не доводять високу вартість: більшість VPC/SG/IAM/CP metadata не має власної hourly ставки. Основні charges — EC2/EBS/IPv4, ALB/LCU, RDS/storage/backups, S3/ECR/logs/CloudFront usage. Зменшення числа модулів 8→7 саме по собі не змінить AWS bill. Варіанти A/B/C і тарифні припущення — у [proposal](SIMPLIFICATION_PROPOSAL.md).

## 10. Перевірки та Git

Виконано source inventory22 current TF і 96 reference TF, existing static builder303 nodes/918 edges, module contract review, окрему незалежну перевірку агентом. Source checker успішний:22 TF files,8 module contracts,33 root inputs,4800 cost rows. Це не Validate або Plan.

Application suite попереднього коміту мав 78 PASS/3 SKIP та 18 ReactPASS. Це історичний результат, не повторний запуск цього review і не IaC validation. Застосунок, Terraform/Docker/HCP/AWS/DB у цьому аудиті не запускалися.

Фінально зіставлено SHA-256: усі253 tracked files ClimateHealth та132 reference TF/Markdown файли незмінні. Перевірено191 локальне посилання з номерами рядків,33 записи root variables та22 moved mappings. Порожні reference output/data files посилаються на файл без вигаданого рядка1. Source checker пройшов перевірку, евристичний secret scanner256 Git candidates не знайшов секретів; history у цьому review повторно не сканувалася, фактичні credentials не перевірялися.

Git status: лише3 нові Markdown reports, tracked diff порожній. HEAD `09f2d79` збережено, main ahead1 від локального origin/main; нового commit/push немає. Refactor не виконано.

**Verdict:** до API exposure виправити finding1; для цільового сценарію погодити RDS-only; до будь-якої зміни адрес отримати state inventory і переглянути Plan. Точний можливий line reduction невідомий без рефакторингового diff. Не перевірено: фактичний HCP state/permissions, provider semantics, remote Plan та AWS runtime.
