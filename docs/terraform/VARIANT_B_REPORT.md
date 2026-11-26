# Реалізація Terraform варіанта B

Дата: 26.11.2026. Зміни лише локальні, без commit/push/provisioning. [Read-only HCP State evidence](STATE_VERIFICATION.md) передувало адресним змінам. У перевіреному workspace нема збережених State/managed resources. Це не аудит unmanaged AWS або інших організацій. Якщо до майбутнього Plan з’явиться State, перевірку повторити.

## Результат

33 → **15 root inputs**, 8 → **6 modules**, 70 → **55 AWS resource blocks**, 22 → **0 moved blocks**. Видалено speculative review/provision flags, EC2 MySQL і весь AI module; SG увійшли в networking. Ресурсні адреси змінено лише після перевірки відсутності збереженого State. Для нового перевіреного workspace moved не потрібні. Для іншого workspace вони не можуть бути видалені без аналізу його State.

Один app gate `deploy_application` керує API compute/ALB/DNS/CDN origin. RDS, ECR, два приватні S3, CloudFront та CloudWatch log group не залежать від нього; prevent_destroy збережено для RDS/storage/ECR/log group. Це свідомий постійний базовий шар з витратами, а не no-op bootstrap. AI не має ні модуля, ні optional input до реальної потреби; тому 15, а не штучно 16 inputs.

## Порядок майбутнього контрольованого розгортання

1. Погодити регіон (код наразі допускає лише кошторисний us-east-1), suffix та environment. У HCP переглянути Plan з `deploy_application=false`; обов’язкові тільки ці три inputs. Він передбачає мережу/SG/ECR/S3/CloudFront/RDS/logs та постійні витрати. Manual Apply лише після окремого дозволу.
2. Окремо погодити підготовку образу, публікацію ECR і CA у build; Actions повертає immutable digest. Наявна `.example` чернетка вимкнена й не є активним workflow. Підготувати issued origin ACM/DNS zone, reader у RDS і SSM DB_USER/DB_PASS (цей Terraform їх не створює), boundary, перевірений ECS AMI. RDS master secret не передається застосунку.
3. Перше API Apply: `deploy_application=true`, `backend_desired_count=0`, max_instances 1. Створюються ALB/DNS, ECS objects і **порожній ASG**, CP/association, service із нулем tasks. Це виконує рекомендацію AWS починати CP із порожнім ASG. Endpoint ще не готовий до користування.
4. Перевірити CP association, IAM propagation, routes, наявність image/reader/TLS і ALB certificate. Після окремого погодження count 1. Підвищення ASG min_size створює перший host після вже наявної CP association; service чекає ASG та steady state. Нові independent ресурси створюються паралельно, не в порядку тексту. Provider/runtime поведінку ще не перевірено.
5. HCP володіє усіма ECS revisions і service task reference. Новий backend_image digest → reviewed Plan → Manual Apply. Для max_instances=1 deployment 0/100 дозволяє коротку перерву. Max=2 змінює deployment на 100/200 і дозволяє CP scale-out; це додатковий бюджет, не гарантія zero-downtime. Static8080 означає один task на host.

AMI update змінює Launch Template для нових hosts; автоматичного Instance Refresh немає. Для заміни вже запущеного host потрібен окремий погоджений drain/recycle runbook. Circuit breaker може відкотити ECS runtime, тоді Terraform/state/config треба узгодити перед наступним run; жоден rollback не відновлює автоматично дані RDS.

## Завершення демонстрації

| Дія | Наслідок / витрати після неї |
|---|---|
| count=0 при app=true | Tasks зупиняються, ASG min0; CP eventual scale-in не гарантує миттєвого EC2=0. ALB все ще оплачується. Перевіряти фактичну capacity. |
| app=false і count0, після review Plan | Видаляються ephemeral service/task definitions/cluster/CP/ASG/hosts, ALB/TG/listener/DNS; API origin вилучається з постійного CloudFront. EBS host видаляється разом із host (не містить БД). Потрібно перевірити порядок drain/delete у майбутньому Plan/runtime. |
| RDS залишається | db.t4g.micro +20GBgp3, managed secret, backup/snapshots залишають витрати. Не знищувати заради економії; stop RDS — окремий дозволений процес, storage платне, auto-restart після 7 днів. |
| S3/ECR/logs/CloudFront залишаються | Зберігання, версії/старі images, запити/доставка/log ingestion продовжують коштувати залежно від використання. Log retention7днів; log group захищена. |
| AI | Відсутній, EC2/EBS та витрат AI від цього root немає. |

Не додано Budgets resources без дозволу; рекомендовано погодити budget notifications окремо. Старий кошторис — сценарна модель, не новий точний рахунок; див. COST_AUDIT. Не запускати загальний destroy: захист stateful ресурсів навмисно блокуватиме його.

## Безпека та потенційні replacement/destroy

Origin header: sensitive, лише `[A-Za-z0-9_-]`, 32–128. Regex не доводить випадковість; значення слід згенерувати приватно. Wildcards/whitespace/control/+slash/padding відхиляються regression tests. SG допускає лише CloudFront prefix list→ALB443, ALB SG→host8080, hostSG→RDS3306, host outboundHTTPS443. Public host без inboundSSH; MySQL private без internet route. OAC і TLS deny збережено. HTTPS egress не є domain allowlist.

RDS require_secure_transport ON, encrypted, backup7days, deletion protection/final snapshot/prevent_destroy. PyMySQL verify_identity/CA код не змінювався. IAM execution scoped до backend ECR, readerSSM та log group; host ECS/SSM managed policies з поточної реалізації залишені. Permissions boundary існуюча й потрібна API; її contents/HCP auth не змінено.

У перевіреному порожньому State немає адрес для replacement/destroy при цьому рефакторингу. Проте назва/suffix/CIDR/subnet/encryption/AMI зміни у майбутньому можуть спричиняти replacement. RDS і S3 protection — запобіжник, не backup від усіх способів втрати даних. Видалення декларації обходить конфігураційний prevent_destroy; такі зміни потребують нового review.

## Що ще не перевірено

Не виконано Terraform fmt/validate/provider-schema/Plan/Apply; HCL перевірено лише lexical/static. AWS доступність RDS8.4.13/AMI/quotas/boundary/сертифіката/reader/CA chain/реєстрації CP/rolling/drain не доведена. SG не доводить готовність інтеграції. HCP authorization лишилась незмінною. AI endpoint і навчена модель відсутні; app/ML код та model_unavailable не змінені.

Окремі dev/production workspaces лише запропоновані, не створені. Нові role/auth variables не вимагалися. Не створено cloud run, AWS ресурсів, commit або push; MySQL/reference/Word без змін.

## Джерела та артефакти

[AWS: empty ASG/CP](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/asg-capacity-providers.html), [managed scaling](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/managed-scaling-behavior.html), [ALB header limits](https://docs.aws.amazon.com/elasticloadbalancing/latest/APIReference/API_HttpHeaderConditionConfig.html).

[Reuse matrix](VARIANT_B_REUSE.md), [HCP inputs](../HCP_TERRAFORM.md), [variables](VARIABLES_REFERENCE.md), [resources](RESOURCES_AUDIT.md), [graph](DEPENDENCY_GRAPH.md), [verification](VERIFICATION.md). Попередні REFERENCE_COMPARISON/INDEPENDENT_REVIEW/SIMPLIFICATION_PROPOSAL збережено як review попередньої реалізації09f2d79; вони не описують поточні15inputs.
