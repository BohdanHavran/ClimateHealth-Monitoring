# Фаза 3: Dashboard, HRI, карта та підготовка ML

23.11.2026. Початковий Git state: main, чистий, HEAD=origin/main=`312c47047ec58ca339fe39edf88769a13ea0606e`. Прочитано технічні звіти фаз 1–2 та аудит, використано вже наявний стек. Docker/Terraform/DigitalOcean/Kubernetes не запускалися; Word/PDF, схема й дані MySQL не змінювалися. Push цієї фази не виконувався.

## Реалізований Dashboard

Чотири hash views із адаптивною навігацією: Dashboard, HRI Analysis, Interactive Map, History. Dashboard поєднує поточні умови для явно вибраного місця та відокремлений історичний контекст. Історію винесено у повторно використовуваний HistoryPanel зі збереженням year filter, keyset-пагінації, ECharts і таблиці. Пропуски/некоректні значення не підміняються нулем, географія/первинне джерело climate_data не вигадуються.

WeatherPanel підтримує MySQL city search або явні координати користувача. Новий Flask coordinate path звертається до Open-Meteo без ключа, з реальними model current temperature/humidity/shortwave_radiation, перевіреними одиницями, UTC timestamps, finite/range checks, timeout і cache. На сторінці показані source/attribution, час показників, отримання, cache state та model-data caveat. Це не вимірювання станції, не медичні дані. Empty/loading/error/retry states не містять вигаданих спостережень.

## Реалізований HRI

Форма трьох обов’язкових числових входів із межами; ручний ввід або заповнення з реального координатного weather API. Виклик існуючого `/api/v1/hri`, індекс 0–1, meter, effective inputs і явний clipping notice. Редагування скасовує pending request і прибирає старий результат. Source/time/coordinates погодних входів збережені в поясненні.

`climate_health/fuzzy.py` у цій фазі не змінено, 27 правил збережено. Індекс не названо медичною ймовірністю, відсотком ризику або навченим прогнозом. Модельна радіація може виходити за domain нечіткої системи; показаний clipping не є доказом наукової валідності цього domain.

## Реалізована інтерактивна карта

React-Leaflet/Leaflet, OSM base tiles з видимою attribution, CircleMarker/Popup, пошук і вибір міст, flyTo, явне оновлення bounds та до 200 місць за запит. Доступний список перших 20 записів і fallback при недоступних tiles. Погода й HRI розраховуються тільки для явно вибраного place, не пакетно для всіх маркерів. У MySQL нічого не записується.

`/api/v1/places/search` читає name/asciiname через parameterized escaped LIKE, q 2–100 символів, limit≤20. Географія береться з ua_places, а не climate_data. Попередня Jinja `/map` збережена та повернула 200 при live check. Максимум маркерів не означає повноти довідника; потрібно збільшувати масштаб/оновлювати область.

## Реальні перевірки та обмеження середовища

На початку smoke наявний MySQL повернув code 2003/timeout, readiness 503. Змін на сервері не виконували. Після повідомлення користувача про відновлення сервера — readiness 200, city search 200 з реальними записами; browser сценарії пройшли. Дозволені root credentials використовувалися лише в тимчасовому read-only diagnostic server, не збережені у source/logs. Нового користувача, DDL або міграцій не створювали.

Browser smoke використовував існуючий Edge/Playwright без підміни мережі чи даних: Dashboard → MySQL history + city search → Open-Meteo → HRI; окремо React карта → MySQL markers → selected city → weather → HRI. Desktop 1440 і mobile 390 px, 0 browser exceptions, без document horizontal overflow для HRI/карти. У обмеженому середовищі OSM tiles не завантажилися; після дозволеного мережевого запуску tiles завантажилися й fallback notice не був потрібний. Знімки Dashboard/HRI/карти переглянуто; вони збережені лише локально у `.local-verification/`, поза Git.

## ML-підготовка

Перевірено CDC NHSN ua7e-t2fy metadata, licence USGOV_WORKS/Public Domain U.S. Government, weekly jurisdiction fields і агреговане охоплення: 21 976 рядків / 67 geographic labels, 08.08.2020–14.11.2026. Для FL і non-null `totalconfflunewadm` — 318 записів, 17.10.2020–14.11.2026. Це **не** підтвердження повноти, однакових reporting regimes або придатності до навчання. Повні raw медичні ряди не завантажені.

Конкретний кандидат: next complete weekly influenza admissions count у Florida (US), health lags 2–5, climate lags 1–4, explicit availability checks. Територія/ціль потребують погодження з керівником і не замінюють Україну автоматично. Розглянуто альтернативи ЦГЗ України/Eurostat з чесними ліцензійними та schema gates. Джерела/права/протокол: `ML_DATA_PROTOCOL.md`; evidence: `reports/phase3-public-sources.json`.

Створено `ml_pipeline/weekly.py`: UTC issue alignment, Saturday keys, duplicate checks, available_at gate, missing features як null; last-available count baseline prototype. Versioned `experiments/weekly_flu_v01.json`: порівняння baselines/regularized Poisson/MLP 16→8, seeds, rolling-origin, train-only preprocessing, MAE/RMSE/deviance і uncertainty protocol. Поки немає verified historical vintages/geo aggregation, `training_approved=false`. Немає training/tuning/scoring, PyTorch/ваг або оцінок точності. FastAPI продовжує повертати model_unavailable; synthetic fixtures — лише тести.

## Результати локальних перевірок

| Перевірка | Факт |
|---|---|
| Python unit/API/provider/pipeline/регресії | **61 виявлено: 58 PASS, 3 SKIP** |
| MySQL write fixtures | Локально SKIP; тільки одноразовий CI runner |
| React component tests | **16 PASS** |
| Legacy JS escaping | **5 assertions PASS** |
| ESLint / TypeScript / production build | PASS |
| Ruff lint / format / pip check | PASS |
| Backend + ML OpenAPI | PASS; CurrentWeather payload також перевірено JSON Schema |
| Real browser smoke | PASS: DB history/markers/search, Open-Meteo, HRI, tiles, mobile |
| Real read-only API + retained Jinja map | PASS після відновлення MySQL |
| Secret scan | Виконано перед локальними комітами; невирішених знахідок не залишено |

Машинні результати — `reports/phase3-verification.json`, `phase3-frontend-verification.json`, `phase3-browser.json`, `phase3-mysql-http.json`. Leaflet npm install auto-audit повідомив 0 vulnerabilities; нових Python-пакетів у фазі 3 не встановлювали. Starlette test-client deprecation warning із попередньої фази залишається. Повного accessibility/cross-browser/load/security audit не заявлено.

Lazy chunks: initial JS приблизно 247 kB, ECharts 494 kB і Leaflet 154 kB до gzip у перевіреній збірці. Це build sizes, не виміряне навантаження/latency. Попереднього warning >500 kB в актуальній збірці немає.

## Склад змін

- Frontend: App navigation/shell, HistoryPanel, HriPage, WeatherPanel/Details, PlaceSearch, MapPage/LeafletMap, typed monitoring API client, CSS, component tests, Leaflet pins/lock.
- Backend: OpenMeteoProvider, coordinate weather API, received_at metadata, MySQL place search; tests і OpenAPI. Нечіткі правила й Jinja templates незмінні.
- ML: pure weekly feature/baseline prototype, tests, experiment protocol, джерела й data gates.
- Tooling: реальні browser/public-source scripts, separate phase3 diagnostics/report, Graphify scope включає ml_pipeline. AST: 40 Python-файлів, 325 вузлів, 732 ребра, 14 спільнот; TS/SQL/runtime не охоплені повністю.
- Документація: актуальні README, architecture/CI/data/ML notes та ADR 0003. Звіти фаз 1–2 залишаються історичними snapshots.

GitHub Actions продовжує code-only перевірки; format check включає ml_pipeline, тести підхоплюються discovery. Container/TF jobs залишаються disabled, live/home DB не передається CI. Віддалені результати **цих нових комітів** не заявляються: push не дозволено на цьому етапі.

Наступний крок після локальних комітів: показати SHA/status, отримати окремий дозвіл на push і перевірити actual CI. Науковий наступний крок — погодити територію/target та отримати licensed raw snapshots із verified availability/coverage й правильною climate aggregation. До цього нейромережеве навчання не запускати. Production auth/TLS/global quotas і backup/restore залишаються окремими задачами.
