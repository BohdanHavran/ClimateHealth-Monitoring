# Система моніторингу кліматичних умов

Основна програмна база — ця директорія (`Диплом 2.0`). Початкову стабілізацію виконано 23.11.2026. Поточний вебзастосунок: Flask/Jinja/Leaflet, MySQL, scikit-fuzzy, Matplotlib, OpenWeather та GeoNames. HRI є правиловим індексом, не навченою моделлю захворюваності. `app.py` — окремий Streamlit-прототип; до Flask image не входить.

## Поточний стан

**Фаза 2:** додано `climate_health/`, `/api/v1/`, React/TypeScript/Vite/ECharts та локальний FastAPI без моделі. DDL із HTTP прибрано. Усі runtime MySQL-з’єднання за замовчуванням `READ ONLY`, cache writes/seed/import вимкнено. Git ініціалізовано на `main`, origin — `git@github.com:BohdanHavran/ClimateHealth-Monitoring.git`; SSH підтвердив `BohdanHavran`, remote порожній. Push не виконано. Поточний звіт: [PHASE2_REPORT.md](docs/PHASE2_REPORT.md).

React: у `frontend/` виконати `npm ci`, `npm run dev`; Node 24 рекомендовано. Vite `127.0.0.1:5173` проксіює `/api` на Flask `127.0.0.1:8000`. Реалізовано історичні спостереження: фільтр року, keyset-пагінація, таблиця, ECharts і loading/error/empty. Походження та географію даних не підтверджено, UI це показує. React-карта поки не реалізована, старий Leaflet/Jinja збережено.

Локальний ML: `.venv/Scripts/python.exe -m uvicorn ml_service.app:app --host 127.0.0.1 --port 8001`. Обом процесам передати один випадковий `ML_SERVICE_TOKEN` через захищене оточення, Flask також `ML_SERVICE_URL=http://127.0.0.1:8001`. Uvicorn сам `.env` не завантажує. Токен не належить до Vite env. Без token — 401; валідний запит — 503 `model_unavailable`, без прогнозу. Автономна перевірка: `.venv/Scripts/python.exe scripts/smoke_ml_http.py` — лише синтетична технічна фікстура.

Локальне `.venv` створено, Python-залежності встановлено тільки в ньому. Наявний MySQL 8.0.40 доступний; читальні API перевірено без змін таблиць/даних. Постійний reader account ще не створено. Docker/Terraform/cloud у фазі 2 не запускати; Word/PDF не змінювалися.

## Локальний запуск після налаштування облікового запису

```powershell
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.venv/Scripts/python.exe scripts/run_local.py
```

При відсутньому `.venv` створити його наявним Python 3.12: `python -m venv .venv`. Перед запуском заповнити локальну `.env`: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS_FILE`; фактичний пароль зберігати в локальному файлі `.secrets/db_password` із обмеженим доступом або передати `DB_PASS` через оточення. `.env` та `.secrets/` ігноруються Git. Не записувати пароль у команди, документацію чи образ. `.env.example` не містить робочих облікових даних; `climate_app` поки є запропонованим ім’ям, не створеним користувачем. `OPENWEATHER_API_KEY` потрібен для реальної погоди, ключ у коді відсутній. `run_local.py` завантажує лише дозволені поля `.env`, слухає `127.0.0.1:8000`, debug/reloader вимкнено. Це сервер розробки; Linux image використовує Gunicorn.

Для тимчасової дозволеної діагностики є `scripts/inspect_mysql.py` і `scripts/smoke_read_only.py`. Вони читають пароль у пам’ять з окремого локального `.env` через `--secret-source`, не друкують його, не запускають bootstrap і не пишуть у БД. Inspection зберігає лише метадані `climate_db`; його локальний JSON ігнорується Git. Smoke запускає й завершує тимчасовий сервер самостійно. Звичайні функціональні маршрути ще можуть виконувати DDL/оновлювати кеш; вони не входять до read-only smoke.

## Docker Compose — відкладено

У фазі 2 Docker і Terraform не запускаються локально або активними CI jobs. Конфігурації збережено для наступної фази; команди зі старих інфраструктурних документів зараз не виконувати.

Типовий Compose підключається до **наявного зовнішнього MySQL**, не запускає нову БД. `.env` і `.secrets/db_password` потрібно налаштувати локально; Docker secrets монтує пароль у `/run/secrets/db_password`. Порт вебзастосунку відкритий лише на loopback 8000, процес не root, filesystem read-only з `/tmp`, capabilities видалено. Контекст image — allowlist вихідних файлів; архіви, CSV і секрети не копіюються. Працездатність image/Compose ще не підтверджена локальним Docker.

`compose.mysql.yaml` — **лише опціональний ізольований стенд**, не потрібний для вашого сервера. Bootstrap `infrastructure/docker/mysql-init/001_schema.sql` призначений винятково для нової порожньої тестової БД; не виконувати на наявній `climate_db`. Скрипт `scripts/init_local_secrets.py` створює паролі лише для цього опціонального стенду, без перезапису файлів. Його не запускали. Окремий MySQL-користувач, backup/restore і відокремлення DDL описані в `docs/ROADMAP.md`.

## Перевірки

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -v
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m ruff format --check climate_data_quality.py ml_contract.py
.venv/Scripts/python.exe -m openapi_spec_validator docs/api/ml.openapi.yaml
node tests/test_frontend.cjs
.venv/Scripts/python.exe -m pip_audit -r requirements.txt
```

Поточні результати — `docs/PHASE2_REPORT.md`. У frontend: `npm run lint`, `npm run typecheck`, `npm test`, `npm run build`. Тести з `RUN_MYSQL_TESTS=1` призначені лише для одноразового CI runner; не передавати їм реквізити робочої БД. Історичні тести за межами цієї директорії не є поточним набором CI. Browser smoke використовує наявні Playwright/Edge без завантаження браузерів; знімки з БД залишаються у виключеній `.local-verification/`.

## Документація

- [Звіт першої фази](docs/PHASE1_REPORT.md)
- [Технічний аудит](docs/TECHNICAL_AUDIT.md) та [вибір стеку](docs/TECH_STACK_DECISIONS.md)
- [Архітектура і схеми](docs/ARCHITECTURE.md), [інтерактивний AST-граф](docs/graphify/graph.html)
- [Стратегія даних](docs/DATA_STRATEGY.md), [ML-план](docs/ML_INTEGRATION_PLAN.md), [OpenAPI](docs/api/ml.openapi.yaml)
- [Інфраструктура й бюджет](docs/INFRASTRUCTURE.md), [Terraform](docs/TERRAFORM_GUIDE.md), [аналіз старої інфраструктури](docs/LEGACY_INFRASTRUCTURE_REVIEW.md)
- [CI/CD](docs/CI_CD_PIPELINE.md), [дорожня карта](docs/ROADMAP.md), [ADR](docs/adr)

Модель, решта SPA, production auth/TLS, backup/restore і deployment залишаються наступними етапами. Rate limiting та погодний кеш локальні для процесу, не distributed quotas. Прямі Python-залежності pinned; транзитивного hash lock поки немає. Первинний архів містить старий секрет: не публікувати його; ключ необхідно замінити у провайдера.
