# Фаза 2: практична модернізація програмної системи

23.11.2026. Основна база — `Диплом 2.0`. Виконано локальний програмний етап. Docker, Compose, Terraform, DigitalOcean та Kubernetes не запускалися. Word/PDF не змінювалися. Записи/DDL/міграції/створення користувачів на наявній MySQL не виконувалися.

## 1. GitHub

**Реалізовано / перевірено:** локальний Git, гілка `main`, один origin `git@github.com:BohdanHavran/ClimateHealth-Monitoring.git`. Повторне звичайне SSH-звернення без явного ключа підтвердило `BohdanHavran`. Окремий `git ls-remote origin` завершився з кодом 0, refs немає: remote порожній. Нового репозиторію не створено, remote не перезаписувався, SSH config і глобальний Git config не змінювалися. Через відмінність власника каталогу в середовищі інструмента використано лише разовий safe.directory для конкретного каталогу.

**Підготовлено:** перелік та index потрібних source/config/tests/docs. `scripts/scan_secrets.py` виконує offline detect-secrets і за потреби контекстну перевірку повного значення наданого локального DB secret. Значення не друкуються. Явні allowlist-коментарі — лише синтетичні тестові значення та одноразові CI-паролі. `.env`, `.venv`, `.secrets`, архів із первинним ключем, CSV невідомого походження, MySQL metadata, screenshots, generated graph, builds, state/plans/real tfvars виключено. Перелік index — `reports/phase2-staged-files.json`; фінальний scan — `reports/phase2-secret-scan.json`.

**Потребує відповіді:** ім’я/email автора коміту не налаштовані. Користувачу поставлено питання; реквізити не вигадувалися. Початковий коміт ще не створено. Історії для ретроспективної перевірки немає; CI підготовлено сканувати майбутню повну історію. **Push не виконано і потребує окремого підтвердження після створення локального коміту.** Віддалені Actions не запускалися. Поточний Git state — `reports/phase2-git-status.json`, інструкція — `GITHUB_SETUP.md`.

Старий ключ лишається в захищеному локальному первинному архіві поза Git/image. Його потрібно відкликати/замінити у провайдера; чинність не перевіряли.

## 2. MySQL

**Реально перевірено:** сервер MySQL 8.0.40, `climate_db`, потрібні стовпці чотирьох таблиць `climate_data`, `ua_places`, `hri_cache`, `hri_impacts`. Реальні HTTP-відповіді 200 для readiness, status, schema, observations, versioned places та старого places API. Обмежені вибірки історії/населених пунктів повернули по 5 записів; значення записів не включено до звіту чи logs. Browser перевірка отримала таблицю й застосувала фільтр року через цю саму БД.

**Реалізовано:** DDL-функції та їх виклики прибрано з `climat.py`. Runtime починає `START TRANSACTION READ ONLY`; `DATABASE_WRITES_ENABLED=False` не вмикається `.env`. Seed/import відмовляють до SQL, кеш БД не записується. Читання impacts/cache не робить commit. Погодний кеш тепер in-memory. Наявна схема й дані залишилися незмінними; root використаний лише в дозволеній тимчасовій діагностиці, сервери завершено.

**Підготовлено, не застосовано:** механізм schema preflight і керівництво контрольованих змін `MYSQL_SCHEMA_GUIDE.md`; існуючий SQL baseline для нової порожньої БД збережено окремо від HTTP. Baseline не є міграцією робочої climate_db. Новий SQL patch не потрібний для перевіреного reader contract і не запускався. Preflight перевіряє наявність стовпців, а не повну типову/індексну/семантичну еквівалентність.

Reader account із SELECT лише на чотири таблиці, host restriction і TLS — план для адміністратора після погодження. CREATE USER/GRANT не виконано, backup/restore не перевірено. Запис кешу можна дозволяти лише окремим рішенням і роллю; поточний код його не виконує.

## 3. Backend

**Відокремлено:** `climate_health/config.py`, `validation.py`, `fuzzy.py`, `rate_limit.py`, `weather.py`, `repository.py`, `services.py`, `api.py`, `ml_client.py`, `datasets.py`. Legacy entry point `climat.py` і Jinja/Leaflet збережено; це поступова модулізація, не повний application factory/refactor усіх маршрутів.

**Додано `/api/v1/`:** `status`, `schema`, `observations`, `places`, `weather`, `hri`, `predictions`. Історія обмежена 200 рядками, keyset cursor за id, фільтри year/month, параметризований SQL. Той самий API живить таблицю й графік; дублікати chart/climate endpoints не створювали. Географічну сутність регіону для таблиці climate_data не вигадано: джерело/територія записів не підтверджені.

JSON errors мають code/message, валідація відхиляє некоректні параметри й NaN/Inf. Новий HRI приймає лише JSON-числа, повідомляє про обрізання до діапазонів моделі й `medical_prediction=false`, не звертається до БД. Побудова нечітких правил AST-ідентична первинному знімку; 27 правил збережено. Обчислення захищене process-local lock.

**Ліміти:** 60 запитів/хв/IP на versioned API; 20 на дорогі legacy analysis/HRI. Спільний weather adapter — максимум 40 зовнішніх запитів/хв/процес, TTL 300 с, 256 keys, single-flight fill і таймаути. IP limiter обмежений 2048 entries. Скидання при restart, множення бюджету workers, відсутність розподіленої/місячної квоти залишаються обмеженнями. Public auth/TLS не реалізовано. Реальний OpenWeather ключ/квота не перевірялися; адаптер протестований mock-об’єктами. Радіація з хмарності є апроксимацією, не вимірюванням.

## 4. Frontend

**Реалізовано й перевірено:** React 19.3.1, TypeScript 6.0.3, Vite 8.3.8, ECharts 6.1.0, ESLint, Vitest, точний package-lock. Перший сценарій — історичні спостереження: layout, provenance notice, API client із runtime checks, фільтр року, keyset-пагінація, таблиця, графік, quality/missing flags, loading/error/empty/retry. Пропуски не замінюються нулем. Медичні прогнози не відображаються.

**Реальний browser smoke:** наявний Edge/Playwright, desktop 1440 px і mobile 390 px, справжній Vite proxy → Flask → MySQL без mock даних. Таблиця й year filter працюють, браузерних винятків і document horizontal overflow не виявлено. Знімок desktop переглянуто візуально; screenshots із даними тільки локальні, виключені з Git. Це не повний cross-browser/accessibility/performance аудит.

Leaflet поки залишається у Jinja; нову React-карту та решту сторінок не реалізовано. Vite dev proxy не заміняє production reverse proxy. Node/nvm wrapper у середовищі не мав активної версії: використано вже наявний bundled Node 24.22.3 і npm CLI з наявної інсталяції, без глобальних налаштувань/нового Node.

## 5. ML та дані

**Реалізовано:** мінімальний FastAPI HTTP-сервіс без моделі, auth token у середовищі, limit тіла 256 KiB, контракт/версія ознак `climate-v1`, недоступність 503. MLClient обмежує адресу loopback, забороняє redirects, має connect/read timeout, перевіряє status/value/model_version/data_quality, не приймає доступний прогноз несхваленої моделі. Не налаштований/недоступний/повільний сервіс повертає чесну відмову, не нульовий прогноз. Для non-loopback deployment потрібен окремий reviewed TLS/auth transport; нині його немає.

**Реально перевірено:** Flask → автентифікований FastAPI через loopback HTTP, технічна synthetic fixture, 503 `model_unavailable`, `value=null`, БД не задіяна. Unit/contract tests охоплюють auth, обсяг, версію, availability, timeout, недоступність і некоректну відповідь. OpenAPI оновлено; 200 prediction у ML contract лишається майбутньою схемою, сервіс його не видає.

`datasets.py`: byte SHA256 manifest завжди `training_ready=false`, UTC daily lag prototype з explicit event_time/available_at, пропусками й відмовою дублікатам/неоднозначному часу. Це технічна основа, не готова вибірка. Наявні SQL monthly rows не перетворюються автоматично на daily training observations. Перевірено лише synthetic fixtures.

Потрібні законний медичний target, територія, частота, одиниці, походження, timestamps доступності й достатня історія. HRI не підміняє медичні спостереження; CSV не має підтвердженої цілі. PyTorch не встановлено, тренування/ваг/accuracy немає. Модель обирається після data gate: baselines → MLP, потім обґрунтоване порівняння з GRU/LSTM.

## 6. CI та інфраструктурні файли

Активний CI підготовлено для Python/API/ML/ізольованої runner-only MySQL та frontend lint/types/tests/build/audit. Secrets workflow тепер Python, без Docker. Actions закріплено SHA; Node setup pin прочитано з офіційного remote. CI не має адреси/credentials домашньої БД. Container job збережений із `if: false`, Terraform job також, trigger Terraform лише manual. Жодного deployment/cloud operation.

Dockerfile/.dockerignore лише статично доповнено копіюванням нових imports. Наявні Docker/Terraform файли збережено, виконання/перевірка відкладені. YAML і умови неактивності job перевірено звичайним Python; **це не Docker/Terraform validation**. Віддалені workflows ще не запускалися.

## 7. Результати перевірок

| Перевірка | Фактичний результат |
|---|---|
| Python unittest | **49 виявлено: 46 PASS, 3 SKIP** |
| Ізольовані MySQL write tests | SKIP локально; лише майбутній одноразовий CI runner |
| Ruff lint / format нових модулів | PASS |
| pip check | PASS |
| Обидва OpenAPI validators | PASS |
| Vitest React | **6 PASS** |
| Legacy JS escaping | **5 assertions PASS** |
| ESLint / TypeScript / production build | PASS |
| Реальний read-only HTTP/MySQL | PASS, шість маршрутів; записів/DDL немає |
| Реальний React/Edge/MySQL | PASS table/filter/mobile; локальні screenshots |
| Реальний Flask → FastAPI HTTP | PASS чесного unavailable contract, не медичний результат |
| pip-audit runtime + ML | Відомих вразливостей не знайдено на момент перевірки |
| npm audit | 0 повідомлених вразливостей на момент перевірки |
| Secret scan candidates/index | Без невирішених евристичних знахідок; значення не друкуються |
| Статична перевірка CI | YAML parse і disabled infra jobs PASS; remote CI не запущено |
| Graphify AST + HTML export | **33 Python-файли, 280 вузлів, 615 ребер, 11 спільнот**; не повний runtime/JS/SQL граф |

Докази: `reports/phase2-verification.json`, `phase2-mysql-http.json`, `phase2-browser.json`, `phase2-ml-http.json`, `phase2-fuzzy-regression.json`, `phase2-dependency-audit.json`, `phase2-npm-audit.json`, `phase2-workflow-static.json`, `phase2-secret-scan.json`. Граф і scope: `graphify/GRAPH_REPORT.md`, `summary.json`.

Проміжні помилки виправлено: тест підрахунку генератора правил, цитування YAML OpenAPI та хибні keyword-знахідки тестових фікстур. У фінальному Python-прогоні помилок немає. Залишаються два попередження: production JS chunk приблизно 723 kB до gzip (потрібне майбутнє розбиття ECharts), Starlette повідомляє про майбутню заміну test-client httpx адаптера. Залежності сумісні за pip check; попередження не приховувалися. Linux-only Gunicorn/image, повний транзитивний Python hash lock, browser performance/coverage та backup/restore не перевірені.

## 8. Суттєві файли

- `climat.py`: DDL removal, read-only guard, shared weather, rate limiting, Blueprint registration, scoped JSON HTTP errors.
- `climate_health/*.py`: config, validation, fuzzy, repositories, services, API, weather/cache/limits, ML client, dataset preparation.
- `ml_service/app.py`, `requirements-ml.txt`, `requirements-dev.txt`: локальний FastAPI та локальні dev/test dependencies.
- `frontend/package*.json`, configs, `src/`: перший React scenario, ECharts, runtime API checks, UI tests і production build.
- `tests/test_api_v1.py`, `test_ml_http.py`, `test_datasets.py`, уточнений `test_routes.py`: нові/регресійні тести.
- `scripts/smoke_phase2.py`, `smoke_ml_http.py`, `browser_smoke.cjs`, `scan_secrets.py`, `run_local.py`, `build_code_graph.py`: відтворювані перевірки й запуск.
- `.github/workflows/*.yml`: кодовий CI; infra jobs вимкнені.
- `.gitignore`, `.gitattributes`, `.env.example`, Dockerfile/.dockerignore: exclusions, локальна конфігурація, статична сумісність майбутнього image.
- `docs/api/*.yaml`, `MYSQL_SCHEMA_GUIDE.md`, `GITHUB_SETUP.md`, оновлені README/ARCHITECTURE/ROADMAP/ML_INTEGRATION_PLAN/CI_CD_PIPELINE/graph report: актуальні факти й наступні етапи.

## 9. Інструменти та наступні кроки

Реально використано ECC terminal-ops/security-review як прочитані робочі інструкції, Git/SSH, локальні Python/Node/npm/Ruff/unittest/Vitest/OpenAPI/detect-secrets/pip-audit, наявний Playwright/Edge, PyMySQL і Graphify API/CLI. Headroom stats викликано, proxy недоступний, compression 0. REA не застосовувався: вихідного коду достатньо. Нових глобальних CLI/MCP/плагінів не встановлено; Python-пакети тільки `.venv`, frontend-пакети тільки node_modules.

Найближче: отримати ім’я/email → створити локальний коміт → показати hash/status → отримати **окремий дозвіл на push** → перевірити фактичний remote CI. Паралельно погодити reader account/backup та реальний медичний набір. Наступний програмний сценарій — React HRI або карта з контрактними й браузерними тестами. Перед публічним доступом потрібні auth/TLS, глобальні quotas, provenance та операційна перевірка. Docker/Terraform/DigitalOcean залишаються відкладеними.
