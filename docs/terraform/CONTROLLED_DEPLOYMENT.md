# Контрольоване поетапне розгортання

Редакція 26.11.2026. Це реалізована конфігурація та протокол майбутньої перевірки, **не результат Terraform Plan/Apply**. AWS, HCP runs/configuration, локальна MySQL та Word не змінювалися. Існуючу авторизацію HCP збережено; нові authentication variables не потрібні.

## Етапи одного root

Working Directory `infrastructure/terraform`, 8 модулів, окремі HCP state для dev/production. Auto Apply має залишатися вимкненим. Після кожного погодженого етапу перевіряти конкретний remote Plan, Apply лише вручну. Не використовувати targeting для обходу перевірок.

| Етап | Увімкнути додатково, попередні provisioning flags лишаються true | Умовні inputs / реальна готовність |
|---|---|---|
| 1. Мережа й SG | infrastructure_reviewed=true після review | environment, aws_region, name_suffix; погодити CIDR. Лише us-east-1 наразі підтримано, регіон треба свідомо погодити |
| 2. Артефакти | artifacts_provisioned=true | ECR і приватні S3; образ, AMI, ACM та runtime credentials ще не потрібні |
| 3. MySQL | database_provisioned=true | RDS default не потребує AMI/контейнера. EC2 mode потребує mysql_ami_id і permissions_boundary_arn; не рекомендований без окремої перевірки TLS/backup |
| 4a. Frontend CDN | edge_provisioned=true | CloudFront S3 origin з OAC, без API origin; стандартний CloudFront HTTPS hostname |
| 4b. API edge | application_window_open=true | origin_hostname, origin_zone_id, origin_certificate_arn та sensitive origin_verification_header; реальні DNS/виданий ACM у правильному account/region |
| 5a. Backend конфігурація | backend_provisioned=true | backend_image з digest, ecs_ami_id, permissions_boundary_arn, runtime_secret_arns з DB_USER/DB_PASS. RDS reader/TLS/схема готові; ASG ще 0 при service_enabled=false |
| 5b. Запуск Backend | service_enabled=true та відкрите window | EC2/task почнуть споживати compute; smoke/readiness/реальні читальні API перевірити після окремого дозволу |
| 6. AI | ai_provisioned=true, ai_runtime_reviewed=true | Реальна ai_ami_id, permissions boundary, приватний DNS/TLS:8001, доставка shared token і S3 agent мають бути попередньо перевірені. ai_enabled=true запускає, false зупиняє існуючий host |

Спочатку всі gates false. Три required inputs дозволяють сформувати конфігурацію раннього етапу без фіктивних ARN/AMI; **review=false навмисно зупиняє Plan**. Авторизація потрібна і для раннього Plan: data sources читають AWS. Встановлення review=true не запускає Apply, проте схвалює підготовку мережі до створення.

Пряме перемикання з уже розгорнутого стану назад на defaults неприпустиме. Перед першим run звірити HCP state й workspace values, їх не перевірено дистанційно. Відсутні в state ресурси створюються за gates; прапорці не виявляють state автоматично.

## Захист даних і адрес

`artifacts_provisioned`, `database_provisioned`, `backend_provisioned` і `ai_provisioned` — прапорці створення, не щоденного вимкнення. RDS, EC2 MySQL/AI, S3, ECR та backend log group мають prevent_destroy. Для RDS збережено deletion protection, backup retention7 і final snapshot. Вимкнення відповідного count/for_each після створення повинно заблокувати destroy у Plan. **Видалення самого resource/lifecycle з коду або прямі AWS API обходять цей механізм**: він не замінює IAM/review/backup.

22 moved blocks зберігають старі unindexed addresses backend/frontend при додаванні count. Реальний state не переносився. Не схвалювати Plan із несподіваною заміною/видаленням; перевірити moved у HCP. Зміна database_mode після створення також блокується захистом старого DB.

CloudFront отримує API origin і `/api/*` behavior тільки разом із window; hostname посилається на реальний Route53 alias, який чекає listener rule. Закриття window видаляє ECS service, DNS alias та ALB і прибирає API origin; CDN/S3 залишаються. Це свідомий Manual Apply з downtime. Перед закриттям завершити активні запити; порядок оновлень на рівні AWS ще не перевірено.

## MySQL TLS

`CLIMATE_ENV=aws` або RDS hostname вмикає fail-closed TLS. `DB_TLS_MODE=verify_identity`, `DB_TLS_CA_FILE=/app/infrastructure/certificates/rds-us-east-1-bundle.crt`. SSLContext вимагає CERT_REQUIRED, hostname verification, TLS>=1.2. Публічний regional RDS CA включений у repo/image; це не секрет. Відсутній/неправильний CA дає конфігураційну помилку, handshake/hostname failure — окрему sanitized readiness503. Логи не містять credentials або CA path із exception.

PyMySQL1.2.4 з explicit SSLContext відмовляє серверу без TLS до передавання authentication packet (офлайн regression test). AWS DNS endpoint має відповідати сертифікату; не підставляти IP замість RDS hostname. У локальній розробці CLIMATE_ENV=local / DB_TLS_MODE=disabled зберігають попередній non-TLS доступ без змін сервера. AWS disabled відхиляється. Для EC2 MySQL потрібний власний довірений CA й DNS; поточний вбудований CA для RDS не підходить автоматично.

До backend Apply окремо створити погодженого DB reader та SSM parameters після дозволу адміністратора, підтвердити схему через контрольований процес. Цей root не створює таблиць чи користувача. RDS master credentials не передавати застосунку. KMS customer key для SSM потребуватиме окремого scoped decrypt дозволу: наявна execution policy його не додає.

## ECS і залежності

Backend default t3.small2GiB, hard task1024MiB, ECS_RESERVED_MEMORY512MiB; арифметично лишається512MiB, але RSS/пік імпортів matplotlib/scipy та OS/Agent треба виміряти на реальній AMI. t3.micro заблокований при provisioning. t3.medium допускає більший task до1536MiB після benchmark. Постійний default1 host, без автоматичного підвищення.

Static host port8080 не дозволяє дві backend revisions на одному host. Default deployment min0/max100 дозволяє downtime. `allow_deployment_capacity=true` дає max2 та min100/max200; це дозвіл на додаткову місткість, не гарантія успішного scale-from-zero чи zero-downtime. Перед rolling перевірити Agent/IAM/CP managed scaling і фактичну появу другого EC2; CPU credits standard можуть обмежити швидкість. ASG desired ігнорується Terraform через CP; min/max лишаються керованими. Window/service off ставлять min/max0, тож host прибирається навіть із ignore desired.

Під час тестового rolling врахувати додатково t3.small $0.0208/h + IPv4 $0.005/h + EBS, за попереднім кошторисом us-east-1. Після успіху повернути extra capacity false лише після перевірки draining/termination; це може перервати task, автоматичної безпечності не заявляємо. Один AZ/host не є HA.

Прибрано module-wide depends_on=[module.alb]; listener_arn тепер використовується в ECS precondition. Instance profiles чекають IAM policy/attachments, public subnet output — route+association; private output — association+S3 endpoint. Review gate повʼязаний з модулями явно, тому частина data sources може відкладатися до Apply при зміні gate. IAM eventual consistency залишається реальною AWS властивістю.

Теги EC2/EBS передані LT tag_specifications та ASG propagate_at_launch; AI має volume_tags. Політика backend egress443 залишена для Open-Meteo/ECR/logs/SSM, DB3306 та AI8001 scoped SG; AI/DB мають лише S3 egress443. Не додано NAT/платних endpoints. S3 endpoint не дає доступу до Open-Meteo чи SSM. Private AI AMI має бути автономною для дозволеного S3 workflow.

Task health live, ALB health ready, grace90s, stopTimeout60s, Gunicorn graceful25s збережено. IAM task_definition тепер належить HCP: ignore task_definition прибрано, щоб TLS/secret/env updates не залишались неактивними. Старий direct ECS UpdateService CD example залишено disabled з HOLD; до його активації погодити одного власника revisions, інакше виникне конфлікт HCP/CD.

**Не додано автоматичний Instance Refresh.** Оновлення LT саме не замінить існуючий host. Refresh із draining, захистом активного task та surge треба погодити й перевірити окремо; небезпечно вмикати його без runtime перевірки.

## Flask → ML

Root ml_service_url передається як ML_SERVICE_URL і точний ML_SERVICE_ALLOWED_HOST; токен — лише через runtime_secret_arns[ML_SERVICE_TOKEN]. ML_CONNECT_TIMEOUT=2, ML_READ_TIMEOUT=5 за runtime defaults, обидва bounded<=30s. Для private CA ml_tls_ca_file має вказувати реальний файл у погодженому image; Docker не генерує/не завантажує приватний CA автоматично.

AWS client приймає HTTPS до allowlisted hostname, verify=true/CA file, redirects=false; відхиляє HTTP навіть loopback, userinfo/path/query/fragment, NaN/Inf timeouts та некоректні ports. Погоджений DNS повинен бути приватним і відповідати сертифікату, порт8001 — чинній SG. Сам allowlist не доводить приватність DNS; це deployment review. Локальний non-AWS loopback HTTP збережено для тестів.

ML FastAPI вже порівнює bearer token; TLS termination, приватний DNS і доставка того самого токена на AI AMI ще **не реалізовані автоматично**. ai_runtime_reviewed=false утримує host вимкненим на рівні provisioning до їх фактичної перевірки. Без ML URL відповідь service_not_configured; недоступність/timeout/TLS failure повертає unavailable з null. При справному сервісі без моделі — model_unavailable. Навчання й вигадані прогнози відсутні.

## Що ще перевірити до Apply

Remote Init/Validate/Plan з AWS Provider6.74.0, moved state, всі count/dynamic/null branches та API availability engine8.4.13; provider schema тут не виконувався. Реальні AMI/image digest, ACM issuance/domain, IAM boundary contents/SSM KMS, reader/schema/restore, private AI TLS/DNS/token, runtime memory/CP rolling/stop. Наступний крок — review цієї конфігурації, дозвіл на push; HCP може автоматично почати Plan після push згідно вже налаштованого VCS trigger. Окремо погодити будь-який Apply.

Джерела: [AWS RDS TLS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL.html), [PyMySQL connection](https://pymysql.readthedocs.io/en/latest/modules/connections.html), [Terraform lifecycle](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle), [moved blocks](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring), [ASG Instance Refresh](https://docs.aws.amazon.com/autoscaling/ec2/userguide/instance-refresh-overview.html).
