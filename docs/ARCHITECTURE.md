# Архітектура системи

## Поточний контур фази 3

```mermaid
flowchart LR
  Dashboard[React Dashboard / History] --> API[Flask /api/v1]
  HRI[React HRI] --> API
  Map[React Leaflet map] --> API
  Map --> Tiles[OpenStreetMap tiles]
  API -->|SELECT READ ONLY| DB[(MySQL)]
  API --> Weather[Open-Meteo current model data]
  API --> Rules[Unchanged 27 fuzzy rules]
  API --> ML[Existing FastAPI: model_unavailable]
  CDC[CDC metadata / aggregates] --> Offline[Weekly feature prototype]
  Offline --> Gate[Unapproved experiment gate]
```

Реалізовані Dashboard, History, HRI та Map з hash navigation. `HistoryPanel` повторно використовує reader API. `WeatherPanel` приймає MySQL place selection або явні координати, не приєднуючи до місця історію без географії. Карта завантажує до 200 місць за явним оновленням області; погода/HRI тільки для вибраного місця, не пакетно для всіх маркерів. Jinja/Leaflet збережено.

`open_meteo.py` — координатний адаптер без ключа, units/finite/time checks, TTL 300 с/256 keys, process-local 30/min і 9000/day. Restart і workers множать бюджет; це не production global quota. Новий шлях повертає модельну shortwave_radiation, legacy city OpenWeather зберігає попередню апроксимацію. HRI engine/правила не змінено. API `received_at` не підміняє provider `data_time`/`fetched_at` або час первинного історичного спостереження. `/places/search` — bounded parameterized escaped LIKE без записів/DDL.

JS client перевіряє форму відповіді, React екранує імена текстом. Leaflet/ECharts винесено в окремі chunks. `ml_pipeline/weekly.py` та experiment config — offline preparation, не predictor; missing values лишаються null, availability перевіряється до issue time, training_approved=false. Докладно: `ML_DATA_PROTOCOL.md`. Схеми нижче зберігають історичне та довгострокове обґрунтування; поточний стан визначає цей блок.

## Реалізовані уточнення фази 2

```mermaid
flowchart LR
  React[React TS Vite ECharts: історія] -->|Vite proxy /api/v1| API[Flask Blueprint]
  Jinja[Jinja Leaflet: збережено] --> Legacy[climat.py legacy routes]
  API --> Repo[ClimateRepository + schema_report]
  Repo -->|SELECT у READ ONLY transaction| DB[(Наявний MySQL)]
  Legacy -->|SELECT, DDL прибрано| DB
  API --> HRI[services + fuzzy: 27 правил, lock]
  Legacy --> HRI
  API --> Weather[Спільний WeatherProvider: TTL + quota]
  Legacy --> Weather
  API --> Client[MLClient: local auth + timeout + response checks]
  Client -->|loopback HTTP| ML[FastAPI: 503 model_unavailable]
```

`climate_health/`: `config.py` (secret reader), `validation.py`, `fuzzy.py`, `weather.py`, `rate_limit.py`, `repository.py`, `services.py`, `api.py`, `ml_client.py`, `datasets.py`. `ml_service/app.py` — окремий локальний HTTP-процес без моделі, `frontend/src/` — перший React-сценарій. `climat.py` залишається compatibility entry point; повний application factory і виділення legacy SQL/маршрутів ще попереду. Кеш БД не записується, seed/import вимкнені. Schema baseline не застосовувався.

Реально перевірені React → MySQL і Flask → ML відображені у `PHASE2_REPORT.md`. Погодний API не перевірявся реальним ключем. API-помилки мають JSON code/message, історія використовує keyset cursor й обмежену сторінку; окремого chart endpoint не створювали — той самий набір живить таблицю та ECharts. Таблиці не мають підтвердженої географії/медичної цілі, окремої сутності регіону не вигадано.

Versioned API: 60 запитів/60 с/IP/процес; дорогі legacy analysis/HRI — 20. Спільний weather adapter: 40 зовнішніх запитів/60 с/процес, TTL 300 с, до 256 cache keys, single-flight lock; limiter зберігає до 2048 IP. Це не розподілена/місячна квота; після restart state зникає, кілька workers множать бюджет. Не довіряємо X-Forwarded-For без налаштованого proxy. Public auth/TLS та глобальні quotas ще потрібні перед deployment.

Наведені нижче схеми й дерево описують початкову структуру та довгострокову ціль. Вони не означають, що вся цільова структура вже реалізована. Docker/Terraform/хмара у фазі 2 не виконуються.

23.11.2026. Основний застосунок — цей каталог. Фізичне перенесення всього коду не виконано. Поточний стан і проєктні компоненти нижче розділено явно.

## 1. Поточна структура

```mermaid
flowchart LR
  UI[Jinja2 + JS + Leaflet] --> W[climat.py Flask]
  W --> H[27 правил HRI]
  W --> M[(MySQL: climate_data / ua_places / hri_cache / hri_impacts)]
  W --> P[OpenWeather]
  G[GeoNames] --> W
  W --> V[Matplotlib PNG]
  CSV[CSV з невідомим походженням] --> S[Окремий Streamlit app.py]
```

Джерело MySQL для розробки надане користувачем; сервер у Docker за замовчуванням не запускається. Контрактні тести підміняють БД/API, а реальне підключення спочатку перевіряється лише читанням метаданих. DDL у старих функціях ще потребує відокремлення від запитів.

## 2. Цільовий контур — спроєктовано

```mermaid
flowchart LR
  U[React TS Vite: static SPA] -->|HTTPS REST| B[Модульний Flask]
  B --> H[HRI engine]
  B --> R[Репозиторії]
  R --> DB[(MySQL)]
  B --> D[Провайдери + якість + provenance]
  B -->|TLS, service auth, timeout| ML[FastAPI PyTorch: приватний inference]
  T[Окреме offline навчання] --> Q[Незалежна перевірка]
  Q --> A[Пакет: ваги + ознаки + версії]
  A --> ML
```

## 3. Компоненти

```mermaid
flowchart TB
  Routes[HTTP routes / validation] --> Services[Сценарії аналізу]
  Services --> Weather[WeatherProvider]
  Services --> Rules[HRI evaluator]
  Services --> Repository[MySQL repositories]
  Services --> Predictor[Predictor client]
  Weather --> Quality[Одиниці, finite, час, джерело]
  Predictor --> Contract[Контракт цілі, горизонту, якості]
```

У поточному коді більшість цих меж логічні. Нові climate_data_quality.py та ml_contract.py — ізольовані компоненти перевірок; вони не означають завершеного розділення моноліту або запуску ML HTTP.

## 4. Інформаційні потоки

```mermaid
flowchart LR
  A[Ручні значення / API / історія] --> B[Перевірка запиту]
  B --> C[Скінченність і фізичні межі]
  C --> D[Межі HRI та нейтральні сценарії]
  D --> E[Нечіткий індекс]
  E --> F[JSON / графік / карта]
  A --> P[Проєктне збереження сирого значення і походження]
```

HRI не є медичною міткою. Обмеження діапазону не доводить фізичну правильність. Проєктне розширення повинно зберігати сирий і обмежений вхід, ознаку заміни й метод оцінки радіації.

## 5. MySQL ER: наявне й проєктне

```mermaid
erDiagram
  UA_PLACES { bigint geoname_id PK
    string name
    double latitude
    double longitude
  }
  HRI_CACHE { double lat PK
    double lon PK
    datetime fetched_at
    double hri
  }
  CLIMATE_DATA { bigint id PK
    int year
    int month
    double avg_temp
    double solar_irradiance
    double humidity
  }
  HRI_IMPACTS { string level PK
    string impact
  }
```

Між цими чотирма наявними сутностями не вигадано foreign keys. Для нового порожнього ізольованого MySQL підготовлено bootstrap SQL; це не міграція існуючого сервера. Проєктне розширення: region → weather_daily/health_daily/forecast; model_version → forecast; dataset_version → experiment. Воно потребує окремої міграції, перевірки й резервної копії. Відомості фактичного сервера переважають припущення bootstrap.

## 6. ML pipeline — спроєктовано

```mermaid
flowchart LR
  S[Погоджені агрегати + погода] --> Q[Ліцензія / якість / available_at]
  Q --> C[Календар усередині території]
  C --> Split[Хронологічні train / validation / test]
  Split --> Fit[Перетворення тільки train]
  Fit --> Models[Seasonal / GLM / boosting / MLP]
  Models --> Eval[MAE RMSE + доступність]
  Eval --> Bundle[Перевірений пакет]
```

GRU/LSTM додаються за достатньої історії. Синтетичні fixtures перевіряють тільки програмний контракт. Реальних медичних даних і точності немає.

## 7. DigitalOcean — спроєктовано

```mermaid
flowchart LR
  Internet -->|443| App[Application Droplet: proxy, SPA, Flask]
  subgraph VPC
    App -->|TLS + auth| ML[ML CPU Droplet]
    App --> DB[(MySQL)]
  end
  Backup[Приватні backup / моделі] --> DB
  Admin[Адміністратор: trusted SSH CIDR] --> App
  Admin --> ML
```

Terraform-каркас описує лише VPC, два Droplets і firewalls. Сервіси, TLS, auth, MySQL, registry та backup-процедури не вважаються налаштованими ресурсами. Кошторис і стан перевірок — INFRASTRUCTURE.md.

## 8. CI/CD

```mermaid
flowchart LR
  Dev[Зміна] --> PR[Pull Request]
  PR --> CI[Lint / unit / MySQL CI / API]
  CI --> Security[Dependency / secret / image checks]
  Security --> Image[Образ за commit SHA]
  Image --> Review[Окреме рішення про публікацію й deployment]
  Review --> Deploy[DigitalOcean + health + rollback]
```

CI-файли створено, але віддалених запусків немає: локальний Git/remote поки не налаштовані. Публікації, SSH deployment, Terraform plan/apply і production gate ще потребують налаштування й дозволу. Докладно — CI_CD_PIPELINE.md.

## Цільова структура після перевірених етапів

```text
backend/       # маршрути, сервіси, domain, providers, repositories
frontend/      # React/TS після контракту API
ml-service/    # FastAPI inference після моделі
ml-training/   # відтворювані експерименти
infrastructure/docker/
infrastructure/terraform/
tests/
docs/adr/
scripts/
```

Ці каталоги не створено порожніми. Сьогодні climat.py, app.py і templates збережені на місці; наступне розділення виконується по одному сценарію після тестів.
