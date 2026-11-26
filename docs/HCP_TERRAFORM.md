# HCP Terraform — контрольоване поетапне розгортання

Оновлено 26.11.2026. GitHub та AWS-авторизацію користувач уже налаштував окремо; ми їх не змінювали та не вимагаємо нових authentication variables.

Єдиний Working Directory: `infrastructure/terraform`. Trigger pattern `/infrastructure/terraform/**` включає вкладені модулі. Dev/production мають окремі state, змінні та дозволи; цільові workspaces climatehealth-dev / climatehealth-production. Фактичні налаштування UI не інспектувалися. Auto Apply вимкнений, лише Manual Apply після перегляду конкретного Plan. State — у HCP, без S3 backend та без зайвого cloud block.

33 root inputs, лише 3 без default: environment, aws_region, name_suffix. Для проходження review guard додатково необхідне свідоме infrastructure_reviewed=true після перевірки кошторису/доступу. Це вже погодження потенційного створення базової мережі, не режим без ресурсів. Null conditional inputs не можна залишати null при ввімкненні відповідного етапу. Існуючі workspace values мають вищий пріоритет за defaults: перед Plan перевірити їх, особливо старі true gates.

Owner та ручний Account ID відсутні. `data.aws_caller_identity.current` використовує чинну AWS identity для трьох ARN-перевірок і потребує авторизації. Це не offline Plan і не очікуваний account allowlist.

| Terraform variable | Type | Default / required | Sensitive |
|---|---|---|---|
| `environment` | `string` | `REQUIRED` | false |
| `aws_region` | `string` | `REQUIRED` | false |
| `name_suffix` | `string` | `REQUIRED` | false |
| `infrastructure_reviewed` | `bool` | `false` | false |
| `service_enabled` | `bool` | `false` | false |
| `backend_image` | `string` | `null` | false |
| `ecs_ami_id` | `string` | `null` | false |
| `backend_instance_type` | `string` | `"t3.small"` | false |
| `task_memory_mib` | `number` | `1024` | false |
| `allow_deployment_capacity` | `bool` | `false` | false |
| `origin_hostname` | `string` | `null` | false |
| `origin_certificate_arn` | `string` | `null` | false |
| `origin_verification_header` | `string` | `null` | true |
| `runtime_secret_arns` | `map(string)` | `{}` | false |
| `database_mode` | `string` | `"rds"` | false |
| `mysql_ami_id` | `string` | `null` | false |
| `ai_enabled` | `bool` | `false` | false |
| `ai_ami_id` | `string` | `null` | false |
| `ai_instance_type` | `string` | `"t3.small"` | false |
| `application_window_open` | `bool` | `false` | false |
| `origin_zone_id` | `string` | `null` | false |
| `permissions_boundary_arn` | `string` | `null` | false |
| `vpc_cidr` | `string` | `"10.42.0.0/16"` | false |
| `public_subnet_cidrs` | `list(string)` | `["10.42.0.0/24", "10.42.1.0/24"]` | false |
| `private_subnet_cidrs` | `list(string)` | `["10.42.10.0/24", "10.42.11.0/24"]` | false |
| `artifacts_provisioned` | `bool` | `false` | false |
| `database_provisioned` | `bool` | `false` | false |
| `edge_provisioned` | `bool` | `false` | false |
| `backend_provisioned` | `bool` | `false` | false |
| `ai_provisioned` | `bool` | `false` | false |
| `ai_runtime_reviewed` | `bool` | `false` | false |
| `ml_service_url` | `string` | `null` | false |
| `ml_tls_ca_file` | `string` | `null` | false |

Child inputs не вводити вдруге у HCP UI. Значення секретів не вводяться у runtime_secret_arns: це лише ARN погоджених SSM параметрів читального DB-користувача/ML token. Origin header — sensitive значення, яке буде в захищеному state. Існуючу авторизацію зберегти без змін; credentials/токени не переносити у Git.

Детальний порядок, умовні inputs та обмеження: [контрольоване розгортання](terraform/CONTROLLED_DEPLOYMENT.md). Повний довідник: [VARIABLES_REFERENCE](terraform/VARIABLES_REFERENCE.md).
