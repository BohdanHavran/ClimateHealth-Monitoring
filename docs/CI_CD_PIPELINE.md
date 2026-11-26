# CI/CD — варіант B

Активні Application checks та Secret check збережено без змін: Python/API/MLcontracts, Ruff, React/lint/TypeScript/build, disposable MySQL у GitHub-hosted job. Домашня MySQL не є CI target. Container job лишається if:false; Terraform source workflow перевіряє Python lexical/module contracts у `infrastructure/terraform`, не запускає Terraform.

`infrastructure/ci/application-release.yml.example` — НЕ активний workflow, додатково if:false. Після окремого дозволу майбутній release може збирати/публікувати backend image, перевіряти scan та повертати immutable RELEASE_IMAGE digest для review. Немає RegisterTaskDefinition/UpdateService чи HCP API викликів. HCP Terraform володіє ECS task definition і service reference: digest у backend_image → reviewed remote Plan → Manual Apply. ASG desired_capacity делеговано ECS CP; min/max задає HCP. Немає конкуруючого deployment owner.

Frontend object publication у draft лишається assets immutable → index no-store → invalidation; AI release прибрано до готової моделі/приватного runtime. Deploy IAM для майбутнього image publisher повинен мати лише ECR/scanning permissions; ECS PassRole/UpdateService не потрібні. Auth user не змінювали.

Working Directory HCP `infrastructure/terraform`, VCS trigger `/infrastructure/terraform/**`. HCP state/execution/versioning залишається єдиним infrastructure workflow. Push зараз не виконано; нові віддалені CI runs не запускалися. [Runbook](terraform/VARIANT_B_REPORT.md).
