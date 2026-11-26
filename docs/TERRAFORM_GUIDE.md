# Terraform — актуальний guide варіанта B

Один root `infrastructure/terraform`, 6 modules,15 root inputs. HCP VCS/Remote/Manual Apply, вже налаштована авторизація без змін; Terraform/Docker локально заборонено. Provider6.74.0, Core>=1.11<2. Немає cloud/S3 backend.

1. [State verification](terraform/STATE_VERIFICATION.md): підтверджена відсутність збереженого State у ClimateHealth-Monitoring; перед майбутнім Plan перевірити повторно.
2. [HCP inputs](HCP_TERRAFORM.md): три required для першого Plan; nullable runtimeinputs лише API deployment. False app gate не прибирає базові витрати.
3. [Поточний runbook](terraform/VARIANT_B_REPORT.md): базовий шар → image/cert/reader prerequisites → apptrue/count0 emptyASG/CP association → окремо count1.
4. [Resource/variable contracts](terraform/VARIABLES_REFERENCE.md), [reuse matrix](terraform/VARIANT_B_REUSE.md), [DAG](terraform/DEPENDENCY_GRAPH.md).

Plan/Apply лише після окремого дозволу. Статичні Python/source checks не замінюють provider validate/Plan. Другий workspace не повинен використовувати той самий State чи naming suffix. Переміщень state зараз немає. HCP володіє ECS revisions; GitHub draft тільки image digest/front objects.
