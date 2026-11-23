# CI: актуальний стан фази 2

Локальні файли workflow оновлено, remote push/Actions не виконані. Git/SSH/origin підготовлено. Активні jobs: Python 3.12, pip check, Ruff, unittest, JS helper, обидва OpenAPI, реальний loopback Flask → FastAPI smoke без моделі, pip-audit; окремий frontend job Node 24 → npm ci/lint/typecheck/test/build/audit. Actions закріплені SHA. MySQL 8.4 дозволена лише на одноразовому GitHub-hosted runner, не домашній сервер і не домашні credentials.

`secret-check.yml` тепер використовує Python detect-secrets 1.5.0 і `scripts/scan_secrets.py --staged --history`, без Docker, з виводом лише шляхів/рядків/правил. Точкові allowlist-коментарі стосуються перевірених синтетичних фікстур та одноразових CI-паролів; цілий каталог tests не виключається. Евристичний offline scan не гарантує відсутності секретів.

Container job збережений із `if: false`. Terraform workflow залишений тільки з manual trigger і `if: false` для job. Docker, Terraform, deployment і cloud зараз не виконуються. Dockerfile лише статично доповнено копіюванням витягнутих модулів; image не збирався. Після окремого дозволу на push потрібно перевірити фактичний GitHub CI; локальні тести не доводять його успіх.

## Подальша доставка

Після окремого дозволу на push перевірити фактичні Actions jobs/logs. Майбутній CD потребує staging, перевіреного image digest, backup/restore, незалежного схвалення production й rollback. Це лише проєктний протокол; deployment зараз не реалізовано. Інфраструктурні документи збережено, їх виконання відкладено.
