# Verification status

Current 26.11.2026 results: [READINESS_REPORT](READINESS_REPORT.md), [verification.json](verification.json). The following is the historical pre-fix audit snapshot.

# Перевірки та межі аудиту

25.11.2026. Поточний source після вузького owner/account cleanup перевіряється окремо від baseline5f01e24. Машинні результати — [verification.json](verification.json).

Перевірено69resource blocks,74variables,48outputs,5locals,8data sources; у повному графі271вузол/729ребер. У підтримуваному reference graph немає cycles або unresolved traversals. Structural contains/module_source edges виключені з DAG test. Ці результати не враховують Terraform state, provider schema, destroy/create splitting чи фактичне розгортання count instances.

Для кожної із74variables і69resources наявна окрема таблиця. Шлях/рядок source перевірено відносно активного root; current graphs/reference nodes зіставлено з повторним build. До очищення21TF, після нього22TF за рахунок data.tf;19первинних TF-файлів, включно з усіма дочірніми модулями, залишилися byte-exact. Provider/variable.tf змінено лише для дозволеного owner/account cleanup, data.tf додано. Gates не відкривалися, root/module/resource labels та outputs не змінювалися.

Шість regression tests перевіряють comparison vs assignment, datasource traversal prefix, interpolation/comments/heredoc, indexed module outputs, actual input/output bindings та JSON round-trip. Загальний Python suite:69тестів,66PASS,3MySQL write integration SKIP. Ruff та source checker пройшли. Повторні frontend/browser checks не виконувалися: application code не змінювався.

Mermaid має11діаграм, найбільша150ребер; повний graph розділено на читабельні scopes замість однієї перевантаженої діаграми. Перевірено syntax conventions flowchart, визначення node IDs, endpoints ребер та Markdown links. DOT має271node definitions і729edges. Graphviz/Mermaid rendering engine не знайдено; фактичний рендер кожної діаграми в GitHub не виконувався, бо документи не опубліковано. Тому structural/source checks не названо renderer validation.

Graphify підтримує Terraform у встановленому коді, але його фактичний extractor дав порожній результат через відсутній tree_sitter_hcl. Пакети не встановлювали. Власний fallback позначено у всіх графах. Graphify-only structural attempt не використовував LLM;0tokens не стосується написання цього звіту.

Сканер перевіряє всі Git candidates, commit history та точний локальний credential match без виведення значень. Знайдені false positives — HCL variable references та дві українські документаційні анотації, а не credentials. JSON attributes представлені стандартними name/expression records без зміни даних; дві prose-only source annotations мають адресні пояснені pragmas. Глобальні scanner rules не змінювали. Підсумок: 246 Git candidates, історія та локальний credential check — 0 нерозвʼязаних знахідок; результат збережено у verification.json; offline heuristics не дають абсолютної гарантії відсутності секретів.

Не виконувалися: Terraform CLI, HCP runs/Plan/Apply, AWS STS/API чи provisioning, Docker, реальна MySQL, training, Word або push. Datasource aws_caller_identity лише додано до коду, не виконано. Наявна HCP авторизація/configuration не змінювалася. У фактичному HCP run ще можуть бути13старих required diagnostics до окремо погодженої публікації нового коду. Тексту самого HCP run не читали: відповідність13помилкам відтворено із declarations коміту5f01e24, із чітким застереженням.

## Git status і повний перелік змін

HEAD/main/origin/main лишаються5f01e24; нових комітів і push немає. Зміни нижче локальні й незакомічені.

```text
 M docs/HCP_TERRAFORM.md
 M docs/INFRASTRUCTURE.md
 M docs/ROADMAP.md
 M docs/TERRAFORM_GUIDE.md
 M infrastructure/terraform/README.md
 M infrastructure/terraform/provider.tf
 M infrastructure/terraform/variable.tf
 M scripts/check_infrastructure_sources.py
?? docs/terraform/ARCHITECTURE_GRAPH.md
?? docs/terraform/AUDIT_REPORT.md
?? docs/terraform/COST_AUDIT.md
?? docs/terraform/DEPENDENCY_GRAPH.md
?? docs/terraform/HOW_TERRAFORM_WORKS.md
?? docs/terraform/MODULES_REFERENCE.md
?? docs/terraform/NETWORK_GRAPH.md
?? docs/terraform/README.md
?? docs/terraform/REQUIRED_VARIABLES_AUDIT.md
?? docs/terraform/RESOURCES_AUDIT.md
?? docs/terraform/VARIABLES_REFERENCE.md
?? docs/terraform/VERIFICATION.md
?? docs/terraform/graphify-attempt.json
?? docs/terraform/graphify-method.json
?? docs/terraform/terraform-dependencies.dot
?? docs/terraform/terraform-inventory.json
?? docs/terraform/verification.json
?? infrastructure/terraform/data.tf
?? scripts/audit_terraform.py
?? scripts/document_terraform.py
?? scripts/terraform_audit_notes.py
?? tests/test_terraform_audit.py
```
