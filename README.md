# ClimateHealth

Дослідницька система моніторингу кліматичних умов: Flask + MySQL, React/TypeScript/Vite, ECharts і React-Leaflet. HRI — наявні 27 нечітких правил, **не медично підтверджена ймовірність захворювання**. Прогнозна нейромережа ще не навчена; ML HTTP-сервіс чесно повертає `model_unavailable`.

Програмна система проєкту «Диплом». [Репозиторій](https://github.com/BohdanHavran/ClimateHealth-Monitoring), гілка `main`. Редизайн зафіксовано комітом `4b3033b`; [перевірки перед публікацією AWS-матеріалів](docs/AWS_PUBLICATION_CHECKS.md) описують наступний інфраструктурний етап. Фактичний статус кожного коміту перевіряти в [GitHub Actions](https://github.com/BohdanHavran/ClimateHealth-Monitoring/actions). Кожен push потребує окремого дозволу. Історичні звіти описують стан відповідної фази, не поточний Git status.

## Реалізований інтерфейс

- `/#dashboard` — поточна погода вибраного місця, джерело/час/якість, історичні графіки й таблиця, фільтр року та keyset-пагінація.
- `/#hri` — валідовані ручні входи або реальні погодні параметри, числовий HRI, шкала 0–1, effective inputs і повідомлення про clipping.
- `/#map` — MySQL-населені пункти, bounded markers, пошук/вибір міста, погода та HRI для вибраних координат. Оновлення області — явна дія користувача, не масове погодне завантаження.
- `/#history` — окремий перегляд історичних записів. Їхню географію та первинне джерело не підтверджено; до карти вони не приєднуються.

Jinja/Leaflet інтерфейс збережено на Flask `/`, `/map`, `/analyze`. `app.py` — окремий Streamlit-прототип, не частина нового React UI; CSV невідомого походження не публікується.

## Локальний запуск

Python 3.12; залежності лише в локальному `.venv`:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.venv/Scripts/python.exe scripts/run_local.py
```

Не перезаписувати наявні `.venv` або `.env`; перші кроки потрібні тільки за їх відсутності. Налаштувати DB_HOST/PORT/NAME/USER і password file у захищеній локальній конфігурації. `.env.example` не містить credentials, запропонований `climate_app` ще не створено. Привілейовані credentials допустимі лише для погодженої тимчасової read-only діагностики. Runtime відкриває `START TRANSACTION READ ONLY`, `DATABASE_WRITES_ENABLED=False`; DDL, seed/import і DB cache writes не виконуються. Наявну `climate_db` не ініціалізувати baseline SQL. Reader account і backup/restore потребують окремого погодження: [керівництво](docs/MYSQL_SCHEMA_GUIDE.md).

Frontend, другий термінал (Node 24 рекомендовано):

```powershell
cd frontend
npm ci
npm run dev
```

React: `http://127.0.0.1:5173`; Vite proxy `/api` → loopback Flask `:8000`. CORS `*` не використовується. npm/Node встановлюються й обираються користувачем, глобальна конфігурація цим проєктом не змінюється.

Погода за координатами — Open-Meteo без ключа, з перевіреними одиницями, timestamps та model-data attribution. Довідник MySQL і явно введені координати — окремі сценарії. [CC BY 4.0 data licence](https://open-meteo.com/en/licence), [free API тільки для non-commercial use та в межах квот](https://open-meteo.com/en/terms). Радіація — модельна shortwave_radiation, не станційне вимірювання. Legacy city OpenWeather API потребує локального OPENWEATHER_API_KEY і зберігає попередню апроксимацію за хмарністю. Секрети ніколи не належать до Vite env або bundle.

ML за потреби: `.venv/Scripts/python.exe -m uvicorn ml_service.app:app --host 127.0.0.1 --port 8001`; обом процесам передати один локальний випадковий ML_SERVICE_TOKEN, Flask — ML_SERVICE_URL. Uvicorn сам `.env` не завантажує. Сервіс не має моделі й не повертає фіктивний прогноз. Dataset pipeline/протокол — [ML_DATA_PROTOCOL](docs/ML_DATA_PROTOCOL.md).

## Перевірки

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -v
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m ruff format --check climate_health ml_service ml_pipeline climate_data_quality.py ml_contract.py
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m openapi_spec_validator docs/api/backend.openapi.yaml
.venv/Scripts/python.exe -m openapi_spec_validator docs/api/ml.openapi.yaml
.venv/Scripts/python.exe scripts/scan_secrets.py --staged --history
```

У `frontend`: `npm run lint`, `npm run typecheck`, `npm test`, `npm run build`. Прямі npm dependencies та lock закріплені; повного Python transitive hash lock поки немає. Synthetic fixtures використовуються лише в тестах. Три MySQL write tests локально пропускаються й призначені тільки для одноразового GitHub runner, не для домашньої БД.

Browser smoke: `scripts/browser_smoke_phase3.cjs` використовує вже наявні Playwright/Edge, нічого не завантажує; `PLAYWRIGHT_MODULE` може вказати встановлений пакет. Потрібні активні read-only Flask і Vite. Це реальна перевірка без підміни MySQL/погоди. Screenshots залишаються в ігнорованій `.local-verification/`. Для обмеженого середовища мережевий доступ до OSM tiles може потребувати окремого дозволу.

## AWS: архітектура та бюджет

[Рішення AWS](docs/adr/0005-ecs-cloudfront-hcp-terraform.md), [архітектура](docs/AWS_ARCHITECTURE.md), [кошторис $100](docs/AWS_COST_ESTIMATE.md), [Terraform-перехід](docs/TERRAFORM_GUIDE.md). Регіон/сценарій/запуск потребують погодження; заборона Docker/Terraform/cloud execution лишається чинною. Єдиний AWS root керується через HCP Terraform (VCS remote plan/manual apply), не S3 state. [HCP setup](docs/HCP_TERRAFORM.md), [власні модулі](docs/TERRAFORM_MODULE_REUSE.md). Історичні конфігурації збережені, не активні.

## Стан і подальша робота

[Звіт фази 3](docs/PHASE3_REPORT.md), [API](docs/api/backend.openapi.yaml), [архітектура](docs/ARCHITECTURE.md), [ML-протокол](docs/ML_DATA_PROTOCOL.md), [CI](docs/CI_CD_PIPELINE.md). Віддалені перевірки запускаються після окремо погодженого push.

Поточні quotas/cache — process-local: рестарт і декілька workers змінюють сумарний бюджет. Public auth/TLS, глобальні квоти, backup/restore та production deploy ще не реалізовані. Docker/Terraform jobs **вимкнені**, конфігурації збережені; локально ці інструменти не запускати. Цільова платформа — AWS; ресурси ще не створено. Kubernetes/EKS/Helm не використовуються. Word/PDF не змінюються.

`.env`, `.secrets`, `.venv`, архіви, приватні дані, DB metadata, screenshots і Terraform state/plans виключені з Git. Первинний архів містить старий API-ключ: його не публікувати; ключ у провайдера потрібно відкликати/замінити.
