# Terraform: карта коду та довідник

Починайте з [підсумкового аудиту](AUDIT_REPORT.md), потім зіставляйте конкретні ресурси та inputs із графами. Це документація локального source, не результат HCP Plan або фактичного AWS deployment.

| Документ | Що містить |
|---|---|
| [ARCHITECTURE_GRAPH](ARCHITECTURE_GRAPH.md) | Загальна AWS-архітектура та пояснення восьми модулів |
| [DEPENDENCY_GRAPH](DEPENDENCY_GRAPH.md) | Девʼять Mermaid-проєкцій за Terraform scopes; реальні reference/input/output/depends_on ребра |
| [DOT](terraform-dependencies.dot) | Повний статичний граф:271вузол,729ребер із відокремленими structural edges |
| [JSON](terraform-inventory.json) | Blocks/nodes/edges, source file/line, evidence та HCL attribute expressions; не обчислені runtime values |
| [NETWORK_GRAPH](NETWORK_GRAPH.md) | Traffic та SG matrix; відрізняє дозволений шлях від непідключеного AI runtime |
| [RESOURCES_AUDIT](RESOURCES_AUDIT.md) | Окрема таблиця для кожного з69resource blocks, включно зroot/builtin gate |
| [VARIABLES_REFERENCE](VARIABLES_REFERENCE.md) | Кожна із74активних змінних:25root+49child, тип/default/required/sensitive/purpose/used-in/affects/example/recommendation |
| [MODULES_REFERENCE](MODULES_REFERENCE.md) | Усі8data sources,5locals і48outputs |
| [REQUIRED_VARIABLES_AUDIT](REQUIRED_VARIABLES_AUDIT.md) |13baselineinputs: причини errors; післяcleanup11required без default |
| [HOW_TERRAFORM_WORKS](HOW_TERRAFORM_WORKS.md) |20пунктів життєвого циклу, порядок, state, review/rollback/stop |
| [COST_AUDIT](COST_AUDIT.md) | Постійні витрати, умовні services, retained disks та відмінності від попереднього кошторису |
| [VERIFICATION](VERIFICATION.md) | Виконані перевірки та межі достовірності |

Graphify0.9.104 фактично запущено, але HCL extractor потребує відсутнього tree_sitter_hcl. Нічого не встановлювали. [Attempt](graphify-attempt.json) містить0nodes/0edges, [method](graphify-method.json) пояснює fallback. Статичний graph побудовано власним Python analyzer, без Terraform/AWS/API.

Відтворення з кореня репозиторію, лише offline Python:

```text
.venv/Scripts/python.exe scripts/audit_terraform.py
.venv/Scripts/python.exe scripts/document_terraform.py
.venv/Scripts/python.exe scripts/check_infrastructure_sources.py
```

Перші дві команди перезаписують тільки generated graph/reference outputs у цьому каталозі. Зміст людських annotations — scripts/terraform_audit_notes.py; ручні AUDIT/HOW/REQUIRED/NETWORK/COST документи не генеруються. Після regenerate перегляньте редакційне оформлення. Схема JSON відділяє назву атрибута від його source expression, щоб не змішувати синтаксичні посилання з runtime credentials; read_inventory відновлює внутрішні maps без втрати даних.

Owner та manual account input прибрано лише локально. ARN checks використовують caller identity з вже налаштованих credentials у майбутньому HCP run, який цей аудит не запускав. HCP не отримає новий код до окремо погодженого push. Наявна авторизація, HCP configuration, application, MySQL, ML, HRI та Word не змінювалися.
