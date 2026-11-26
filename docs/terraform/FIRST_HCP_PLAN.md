# Перший HCP Plan — ClimateHealth-Monitoring

26.11.2026. Інструкція для наявного workspace організації `diploma-2025`, repository `BohdanHavran/ClimateHealth-Monitoring`, Working Directory `infrastructure/terraform`. Налаштована AWS-авторизація залишається без змін. Цей етап — review та локальний commit; push, HCP run і Apply агент не виконує.

## 1. Висновок фінального code review

Переглянуто diff від `09f2d79`, усі шість модулів, root callers/outputs, CI draft, tests та чотири звіти варіанта B. Статичних блокерів першого **plan-only** з app=false не знайдено. Це не підтвердження Terraform Validate, schema чи AWS deployability.

| Компонент | Що збережено / перевірено | Межі підтвердження |
|---|---|---|
| ECS/CP | Root module.backend count0 при appfalse; для наступного етапу emptyASG/count0 bootstrap, CP association, managed draining/scaling, IAM attachment/profile readiness, listener-rule readiness. HCP володіє task revisions. ASG desired_capacity делеговано CP; min/max HCP. | Перший Plan не створює ECS. Наступний count1 лише після перевірки CP. 1host/static8080 допускає перерву, max2 не гарантує zero-downtime. Нова AMI/LT не замінює host автоматично. |
| ALB | Count0; при API deployment HTTPS443, prefix-list ingress, default403, URL-safe origin32–128, SG-to-SG8080, TG/ready200. | Issued ACM, DNS SAN, quota prefix-list, AWS propagation та runtime health не перевірені. |
| CloudFront/S3 | Приватні2buckets, BPA4flags, SSE, versioning, ownership, TLSdeny, OACSourceArn-onlyfrontendread; HTTPSviewer, SPAfunction, assets cache. APIorigin/behavior відсутні при appfalse. | Після Apply без upload об’єктів frontend ще не працюватиме; відсутність файлів не дефект Plan. Видимість UI/тількиHTTPS виконуються runtime окремо. |
| RDS | Лише MySQL8.4, SingleAZ db.t4g.micro, private, encrypted20GBgp3, TLSrequired, backup7days, deletionprotection, finalsnapshot, preventdestroy. | Region/class/version availability і фактичний TLS/reader не доведені Plan. Mastersecret керує AWS, reader/SSM створюються окремим погодженим процесом. |
| Networking | Дві public/дві private subnet, IGW тільки publicdefault; S3Gateway;3SG/6rules; без NAT/SSH/AI. Publicsubnet output залежить від route/association. | PrivateSG не доводить готовність DB. Backend HTTPSegress0.0.0.0/0 — необхідний дозволений вихід, не domain allowlist. |
| IAM/outputs | ECS execution ECRrepo/SSMreader/logstream scopes збережені; ecr:GetAuthorizationToken Resource* потрібний цьому API. Host ECS/SSM managed policies + boundary, IMDSv2/encryptedEBS. Порожня taskrole вилучена.7rootmetadata outputs,6nullableAPI outputs. | Host managed policies ширші за execution scopes: boundary зміст перевірити перед API. Customer-managed SSM KMS key потребуватиме scoped kms:Decrypt; зараз його ARN/input/permission немає, тому до API використовувати погоджений AWS-managed SSM key або окремо доповнити policy. |

Вилучені компоненти — погоджені AI/EC2MySQL, їхні SG/ECR/IAM та зайві flags. Stateful RDS/S3/ECR/rootlogs не залежать від appgate. Шість старих rootoutputs service/ALB лишаються null при appfalse; вони не повинні містити secrets. Master password/origin header/credentials не виводяться rootoutputs. Default tags Project/Environment/ManagedBy та pinned provider6.74.0 збережено. `owner`/ручний `aws_account_id` не повернуто.

State перевірено раніше цього дня: явне No states saved/Resources0; це датоване read-only спостереження, не нове звернення HCP у цьому review. [Докази](STATE_VERIFICATION.md). Перед Plan повторити перевірку; якщо з’явилися адреси, зупинитися й переглянути міграцію.22moved blocks не потрібні лише для підтвердженого нового State.

## 2. Точні HCP Terraform variables

Перевірено declarations безпосередньо в [variable.tf](../../infrastructure/terraform/variable.tf): **15inputs, лише3без default**. Child variables заповнює root, їх не потрібно додавати до HCP UI.

| Variable | Default | HCP UI / перший Plan | Коли потрібна |
|---|---|---|---|
| `environment` | немає | Terraform variable,string,HCL Off; обрати `dev` для цього демонстраційного workspace або свідомо `production` | Завжди; дозволені лише dev/production. Назва workspace не визначає environment автоматично. |
| `aws_region` | немає | Terraform variable,string,HCL Off: `us-east-1`, якщо погоджуєте цей регіон | Завжди; validation наразі допускає тільки us-east-1. Інший регіон потребує нового review CA/цін/коду. |
| `name_suffix` | немає | Terraform variable,string,HCL Off: власний стабільний унікальний suffix, не AWSidentifier | Завжди;4–16lowercaseletters/digits/hyphens, alphanumeric ends, без consecutivehyphens. Не змінювати після deployment без replacementreview. |
| `vpc_cidr` | `"10.42.0.0/16"` | Можна не створювати UI variable | Якщо потрібно уникнути IPперетину; IPv4/16; public/24індекси0/1,private10/11 обчислюються. |
| `deploy_application` | `false` | Рекомендовано явно Terraform variable,HCL On: `false` | Лише після погодження API: true створює ALB/ECS/DNS/APIorigin. False НЕ вимикає базові ресурси. |
| `backend_desired_count` | `0` | Залишити default або Terraform number,HCL On: `0` | Спочатку apptrue/count0 для bootstrap; потім count1 окремим reviewedrun. При appfalse дозволено тільки0. |
| `backend_max_instances` | `1` | Залишити default | `2` лише для погодженого тимчасового rollingcapacity. Це стеля, не постійна кількість hosts. |
| `backend_image` | `null` | Не додавати до UI для першого Plan | Обов’язковий при apptrue: реальний backend ECRdigest цього account/region/environment, не tag. |
| `ecs_ami_id` | `null` | Не додавати | При apptrue: перевірений ECS-optimized AL2023x86_64 AMI. Regex перевіряє тільки синтаксис. |
| `origin_hostname` | `null` | Не додавати | При apptrue: власний погоджений DNSname без scheme/path/trailingdot. |
| `origin_zone_id` | `null` | Не додавати | При apptrue: існуюча Route53hostedzone, відповідна hostname. |
| `origin_certificate_arn` | `null` | Не додавати | При apptrue: issued regionalACMcertificate, правильний account/region/SAN. |
| `origin_verification_header` | `null` | Не додавати | При apptrue: sensitive HCP Terraform string; нове randomURLsafe32–128, без*?/whitespace/control. Не публікувати. |
| `runtime_secret_arns` | `{}` | Залишити default | При apptrue: Terraform map,HCL On, точні DB_USER/DB_PASS SSMparameterARNs окремого RDSreader. Лише references, не паролі. |
| `permissions_boundary_arn` | `null` | Не додавати | При apptrue: existingreviewedIAMboundary у фактичному account. Null не вимикає вимогу APIroles. Це не налаштування HCPauth. |

Таким чином, для першого Plan достатньо задати3stringvariables, решту залишити defaults; appfalse можна задати явно для наочності. Null не вводити рядком `"null"`: залишити variable відсутньою; якщо явно задаєте null/map/number/bool, використовувати HCL On. Невалідні ненульові runtime values можуть блокувати Plan навіть при appfalse; не заповнювати їх заглушками.

Перевірити workspace/project Variable Sets: старі Terraforminputs на кшталт infrastructure_reviewed/artifacts_provisioned/database_mode більше не оголошені й не повинні підміняти поточний contract. Їх можна прибрати з власних неактуальних Terraform settings після review користувачем. **Не видаляти/не змінювати чинні AWS authentication environment variables або shared Variable Sets навмання.** Credentials не налаштовувалися повторно.

## 3. Очікування першого Plan і критерії прийняття

Повна таблиця45addresses та costflags: [FIRST_PLAN_RESOURCES.md](FIRST_PLAN_RESOURCES.md); [машинний список](first-plan-resources.json).

- Якщо State досі порожній, очікується45create/0update/0destroy. Будь-який replace,delete,import або зміна наявного ресурсу — STOP до пояснення. Кількість сама по собі не замінює перегляд кожного diff.
- Жодних ECS/ASG/LT/EC2/EBShosts/ALB/TG/listeners/Route53origin/IAMroles при deploy_application=false. ALB/backend SG існують як правила майбутнього доступу, це не створення ALB/EC2.
- AI/EC2MySQL/NATGateway/NATInstance/Bastion/EKS/Kubernetes/RDSProxy/interfaceendpoints/domainpurchase/WAFплатнийplan відсутні. MySQL тільки один protectedprivateRDS. Немає S3TerraformStatebucket.
- VPC/16 і4непересічні/24 у двох AZ, publicIGW route лише на publictable.3SG/6rules: CFprefix→ALB443; ALB↔backend8080; backend↔RDS3306; backendout443. Немає inboundSSH або0.0.0.0/0→DB/host. S3Gatewayendpoint є погодженим ресурсом.
- Два S3privateBPAalltrue,versioning/SSE/ownership; OACalwaysSigV4, frontendpolicy з SourceArn, TLSdeny. CloudFrontпершийorigin тільки S3; немає APIbehavior/origin/header; HTTPSviewer/defaultcert,PriceClass100.
- RDS8.4.13/db.t4g.micro/SingleAZ/20GBgp3,max20,noPublicIP,TLSrequired,backup7,deletionprotection=true,skipfinalsnapshot=false,preventdestroy. Не приймати MultiAZ/більшийclass/storage без нового бюджету.
- Регіонus-east-1 і derivednames `climatehealth-${environment}-${name_suffix}` правильні. Defaulttags: ProjectClimateHealth,Environmentобраний,ManagedByTerraform.
- Rootoutputs — тільки VPC/CDN/bucket/ECR/DBendpointmetadata; APIoutputsnull зазвичай не відображаються у Stateoutputs. Жодного password/token/header/privatekey/mastersecretvalue чи несподіваного sensitiveoutput. Resourceattributes `(sensitive value)` або knownafterapply самі не означають витік; rawplan/state не публікувати.
- Не повинно бути AWS accesskeys у provider/planvariables. Calleridentity має відповідати вже налаштованому account; зміни auth не робити заради greenPlan.

## 4. Потенційні місячні витрати після Apply

**Сам Plan не створює ці AWS-ресурси і не запускає наведений compute/storage рахунок.** Можливі HCP runcredits залежать від вашого тарифу. Нижче — ціна майбутнього базового шару appfalse, без податків, FreeTier/credits/paidCDNplans не враховані.730годин у місяці,без CPUcreditoverage/backupoverage,порожні ECR/logs,мінімальне використання S3/CDN.

| Компонент | Формула USD | Місяць |
|---|---|---:|
| RDS db.t4g.micro |730×0.016|11.68|
| RDS20GBgp3 |20×0.115|2.30|
| AWS-managed mastersecret |1×0.40+APIзаusage|0.40+API|
| Мінімальна фіксована база |без traffic/storageіншихсервісів|**14.38+API**|
| S3приклад |1GB×0.023+1000PUT×0.005/1000+10000GET×0.0004/1000|0.032|
| CDNприклад без allowances |1GB×0.085+10000HTTPS(EU)×0.012/10000+10000Function×0.10/1000000|0.098|
| Малий демонстраційний usage |14.38+0.032+0.098|**≈14.51**|
| Плановий бюджет із запасом20% |14.51×1.20|**≈17.41**|

RDSставки заново отримано з публічного AWSкаталогу, publicationDate2026-11-26T15:30:47Z: [збережені дві SKU](../reports/first-plan-rds-prices.json), [AWS PriceList](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-1/index.json). S3unitrates зі збереженого кошторису24.11, чинна [pricingpage](https://aws.amazon.com/s3/pricing/) переглянута26.11. [SecretsManager](https://aws.amazon.com/secrets-manager/pricing/) і [CloudFrontPAYG](https://aws.amazon.com/cloudfront/pricing/pay-as-you-go/) перевірені26.11; allowances можуть зменшити CDNчастину, але не закладені як гарантовані. Немає нового CFflat-rateplan/WAFenrollment.

Це конкретний обмежений scenario, не верхня межа рахунку. RDS T4g працює Unlimited: CPUcredits понад baseline коштують додатково [0.075/vCPU-hour](https://aws.amazon.com/rds/mysql/pricing/). Storageversions/backup/snapshotoverage, APIcalls, transfer/crossAZ, CDNtraffic, images/logs, податки або сторонні існуючі AWSресурси — додатково. Немає ALB/EC2/AI/IPv4/NATcharge від першого набору. Навіть80годин демонстрацій не перетворюють RDSна80годин: root не зупиняє його автоматично. Захищені backup не видаляти заради економії.

## 5. Що з’ясується лише через remote Plan / runtime

Remote init/validate/Plan перевірить provider6.74.0 schema, HCLсемантику, variablevalidation/datareads, accountpermissions/dataavailability, currentStateaddresses/createchange/replacement, фактичні computedoutputs. Шаблон45не є гарантією успішного run. Providerlock/checksums ще не отримані погодженим remoteпроцесом.

Plan не гарантує APIcreationavailability(engine8.4.13/class/AZ), глобальну унікальність S3name при Apply, quotasenforcement/IAMpropagation, RDSCAchain/reader, ECSruntimeRAM/registration/bootstrap, DNS/ACMдовіру або мережевіhealthchecks. Вони потребують окремого read-onlyAWSreview/майбутніх контрольованих deploymenttests. Customer-managedKMSsecrets, AI та modelendpoint не вважаються готовими.

## 6. Дії користувача для Plan без Apply

1. Переглянути цей diff/commit. Поки код лише локально, HCP не може побачити його з GitHub. Окремо дозволити майбутній звичайний push; не змінювати історію.
2. **Перед push** у ClimateHealth-Monitoring перевірити Remoteexecution, WorkingDirectory `infrastructure/terraform`, sourcebranchmain, AutoApplyOff/AutoDestroyOff, вже налаштовану авторизацію. Перевірити States/Resources знову. Код/accountvars не замінюють цю перевірку. Не міняти auth.
3. До push встановити три погоджені Terraformstringvariables з таблиці; deploy_applicationfalse/count0. Переглянути VariableSetoverrides. Environmentdev — рекомендований вибір для першого demo, але користувач має свідомо обрати його і регіон.
4. Після окремо дозволеного push звірити commitSHA у GitHub/HCP. VCS може сам запустити normalrun до Applyconfirmation. Не створювати дублюючий run, якщо він уже є; переглянути його Plan і **не натискати Confirm & Apply**, далі DiscardPlan після збереження несекретного review.
5. Якщо потрібен окремий неприкладний run і немає активного: `+ New run` → **Plan only**; зберегти поточну підтримувану Terraformversion (раніше UI1.17.2), перевірити sourcecommit/configurationversion. `Start run` виконує користувач після свідомого рішення. Не вибирати Destroy/Refresh-only/TargetedApply.
6. Дочекатися remoteInit/Validate/Plan; переглянути45ресурсів/checklist/costs. При diagnostics не підставляти заглушки й не послаблювати protection. Передати лише sanitizeddiagnostics для виправлення.
7. Залишити Planonly завершеним без Apply або відхилити нормальний VCSPlan через DiscardPlan. Будь-який Apply потребує окремого дозволу на конкретний перевірений Plan. Жодних локальних Terraformкоманд не потрібно.

Офіційні [UI/VCS workflow та Plan only](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/run/ui) підтверджують відмінність speculativeplan та Confirm&Apply. Ця інструкція нічого не змінює у workspace автоматично.
