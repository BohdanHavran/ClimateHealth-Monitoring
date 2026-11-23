# Звіт першої безпечної фази модернізації

Дата: 23.11.2026. Основна база — `Диплом 2.0`. Академічні Word/PDF, методичні матеріали й стара програмна директорія не редагувалися. Новий текст диплома в цій фазі не створювався відповідно до актуального завдання. Весь застосунок не переписано.

## Підтверджений стан

| Компонент | Статус | Межі підтвердження |
|---|---|---|
| Flask, Jinja, нечіткий HRI, MySQL-клієнт | Реалізовано / частково протестовано | 13 маршрутних тестів із mock БД/погоди, один справжній fuzzy розрахунок; реальні погодні виклики не перевірялись |
| Вхідна валідація, secrets, health, редагування помилок | Реалізовано / протестовано | Відмова для NaN/Inf, недійсних меж/режимів, захищене читання password file, таймаути, readiness 503 |
| MySQL | Протестовано читанням | Сервер 8.0.40, `climate_db`, чотири таблиці: `climate_data`, `ua_places`, `hri_cache`, `hri_impacts`; реальний `SELECT 1` через HTTP readiness успішний |
| HTTP запуск | Протестовано | Тимчасовий loopback сервер, п’ять відповідей 200: `/health/live`, `/health/ready`, `/`, `/map`, static helper; сервер після тесту завершено |
| Інтерфейс | Реалізовано точкові зміни / частково протестовано | Екранування HTML, відмова від автопрогрівання; 5 JS assertions; браузерний E2E не проводився |
| Якість даних | Реалізовано / протестовано | 6 тестів; CSV не змінено |
| ML contract prototype | Реалізовано / протестовано | 5 тестів та повний OpenAPI validation; HTTP-сервісу, ваг і прогнозу немає |
| Docker/Compose/CI/Terraform | Реалізовано файли / спроєктовано | Docker і remote CI не запускалися, Terraform має обмеження версії; ресурси не створено |
| SPA, ML inference service, CD | Заплановано | Не подавати як готові компоненти |

Пароль наданої БД прочитано з дозволеного локального джерела тільки в пам’ять. Він не записаний до коду, звітів або журналів. Початкова інспекція метаданих була ширшою за потрібну схему; збережений локальний звіт і повторний запит обмежено `climate_db`, чужі схеми не включено до документації. Даних користувачів не вибирали; DDL, INSERT, UPDATE, DELETE, TRUNCATE та GRANT на наданому сервері не виконували. Root використовувався лише для діагностики, новий користувач і постійні credentials застосунку не створені. Bootstrap не застосовано.

## Вибір архітектури

Рекомендовано поступово модулізувати **Flask/Python 3.12 + MySQL**, зберігаючи перевірювані fuzzy алгоритми й маршрути. Перевага іншого основного backend не доведена вимірами. Цільовий UI — **React + TypeScript + Vite**, Leaflet для карт і ECharts для дашбордів; SSR не є встановленою вимогою. Порівняння FastAPI, DRF, NestJS, Go і альтернатив UI/візуалізації — `TECH_STACK_DECISIONS.md` та ADR. Новий UI поки не реалізовано.

Окремий приватний **FastAPI/PyTorch** inference спроєктовано для другого CPU Droplet; основний Flask працює на application Droplet, MySQL зберігається. Offline training відокремлено від HTTP inference. Мережеві правила, auth/TLS, схеми ознак, версії, timeout і відмова без фальшивого прогнозу описані в архітектурі. Наявний Docker Compose за замовчуванням використовує зовнішній MySQL, додатковий сервер не запускає.

## Дані та ML

CSV: 53 рядки × 20 стовпців, 94 порожні значення, 9 текстових NAN, 7 Unknown, 21 порушення температурного порядку серед 32 повних трійок. Походження й ліцензія не підтверджені, медичної цілі немає. Це не навчальна вибірка для прогнозу здоров’я.

Кандидат задачі — прогноз агрегованого показника звернень/госпіталізацій за погодою й лагами **після погодження території, цілі, горизонту та легального набору**. Open-Meteo й CDC NHSN — досліджені кандидати джерел; американський weekly NHSN не підміняє українські дані. Ціль ще не затверджено. Починати з persistence/seasonal baseline і регуляризованої статистичної моделі, потім MLP; GRU/LSTM тільки за обґрунтованої послідовної вибірки. Календарний split, доступність ознак, train-only preprocessing, independent test і метрики зафіксовані в ML-плані. Причинність і медична придатність не встановлені.

Прототип повертає `model_unavailable`, `value=null`; синтетичні значення використовуються лише в тестах. Навчання й вигадані експериментальні результати відсутні.

## Реальні зміни файлів

- `climat.py`, `requirements.txt`: конфігурація, secrets, валідація API/кешу, health, таймаути, контрольовані помилки; 27 fuzzy правил збережено.
- `templates/map.html`, `templates/analyze.html`, `static/js/safe-html.js`: екранування динамічного HTML, обробка порожнього результату/помилок, вимкнений автоматичний прогрів.
- `climate_data_quality.py`, `ml_contract.py`, `scripts/profile_dataset.py`, `docs/api/ml.openapi.yaml`: якість даних і чесний контракт прогнозування.
- `scripts/inspect_mysql.py`, `scripts/smoke_read_only.py`, `scripts/run_local.py`, `scripts/build_code_graph.py`: безпечна діагностика, запуск і AST-аналіз.
- `tests/test_routes.py`, `test_data_quality.py`, `test_ml_contract.py`, `test_mysql_integration.py`, `test_frontend.cjs`: поточний набір перевірок.
- `Dockerfile`, `.dockerignore`, `compose.yaml`, `compose.mysql.yaml`, `infrastructure/docker/mysql-init/001_schema.sql`, `scripts/init_local_secrets.py`: контейнерний каркас; SQL лише для нової ізольованої БД.
- `.gitignore`, `.env.example`, `requirements-dev.txt`, `pyproject.toml`, `README.md`: локальна організація й перевірки.
- `.github/workflows/application-ci.yml`, `secret-check.yml`, `terraform-ci.yml`: початкові CI-файли без remote запуску чи deployment.
- `infrastructure/terraform/`: VPC, два Droplets, firewall, параметри й backend examples; без apply.
- `docs/`: аудит, порівняння стеків, архітектура з Mermaid, стратегія даних, ML-план, інфраструктура, Terraform, CI/CD, legacy review, roadmap, ADR, Graphify та звіти перевірок.

Первинний `climat.py` і два змінені шаблони збережено перед редагуванням у локальному архіві аудиту за межами проєкту. Архів містить старий секрет, не призначений для Git/image чи поширення. Первинний `course.zip` не змінений, виключений із Git/Docker. Ключ потрібно відкликати/замінити у провайдера.

## Виконані перевірки

1. `.venv`: Python 3.12.14, встановлення прямих runtime/dev залежностей лише локально; глобальні пакети не змінювалися. `pip check` — PASS.
2. `unittest discover`: **27 виявлено, 24 пройшли, 3 пропущено**. Пропущені MySQL integration fixtures призначені для одноразової CI БД, не для сервера користувача. Історичний AST-набір за межами проєкту застарів після зміни NaN-контракту; не заявляється як поточна зелена перевірка.
3. Ruff lint і format-check двох нових модулів — PASS. JavaScript helper — 5 assertions PASS. OpenAPI validator — PASS.
4. `pip-audit -r requirements.txt` — **відомих вразливостей не знайдено** на момент перевірки. Це не гарантія відсутності дефектів; Linux-only Gunicorn і image потребують Linux CI. Прямі версії pinned, транзитивного hash lock ще немає.
5. Реальні read-only MySQL metadata та HTTP smoke — PASS, без записів БД/погодних викликів.
6. Graphify AST та HTML export реально виконано: 162 вузли, 310 ребер, 15 спільнот. AST неповний для top-level Streamlit, шаблонів/SQL; ручні архітектурні схеми доповнюють граф. Точне покриття — `graphify/summary.json`.
7. `terraform fmt -check -recursive` — PASS на 1.10.2. Потрібен 1.11+, init зупиняється до provider download; validate не підтверджено. Upgrade/provider installation, plan/apply/destroy не виконувалися.

Машинні результати — `reports/verification.json`, `reports/dependency-audit.json`, `reports/http-smoke.json`. Локальна інспекція БД містить службові метадані й ігнорується Git. CI workflow definitions не є доказом пройденого GitHub-прогону. Docker/Trivy/Gitleaks/Checkov локально не запускались. Навантаження, браузер, реальна погода та відновлення backup не перевірені.

## Інфраструктура й інструменти

Підготовлено два CPU Droplets у VPC, application public HTTPS і ML port лише від application; фактичні TLS/service auth не налаштовані. Орієнтир бюджету за припущеннями `INFRASTRUCTURE.md`: $33,80/місяць із контейнерною MySQL, backup і Spaces; $48,95 із Managed MySQL. Це не рахунок і не фактичний Terraform plan: частина цих компонентів ще не описана ресурсами. Кошторис, офіційні посилання й додаткові витрати — у відповідному документі.

Старий публічний GitHub переглянуто лише читанням; корисні принципи — VPC, приватне сховище, параметризація й захист stateful даних. Код, секрети та широкі firewall-правила не переносилися; охоплення review — `LEGACY_INFRASTRUCTURE_REVIEW.md`.

Реально використано ECC-підходи через прочитані terminal-ops/terraform-patterns, статичний аналіз, командну розробку й окремий security review; Graphify API/CLI; локальні unittest/Node/Ruff/OpenAPI/pip-audit; PyMySQL, Werkzeug HTTP server; Terraform fmt/init перевірку; web для офіційних джерел. Headroom stats викликано, proxy недоступний, стиснення не застосовано. REA не викликався — достатньо вихідного коду. Нових MCP/плагінів/глобальних CLI не встановлено. `.venv` залежності встановлені після дозволу користувача.

## Ризики та наступне завдання

Немає production auth/rate limiting, DDL залишається у частині HTTP-маршрутів, погодні cache miss можуть витрачати квоту й писати в кеш; наявний HRI не медично валідований. TLS, міграції, backup/restore, приватний inference, remote CI і Linux image потребують окремої перевірки. Репозиторій Git не налаштовано; нічого не push/не опубліковано, платних ресурсів немає.

**Наступне конкретне завдання:** винести DDL з HTTP у контрольований механізм керування схемою, перевірити його на погодженій окремій тестовій схемі/backup, після чого підготувати й погодити MySQL account із мінімальними правами та інтеграційні тести. Перед публічним доступом додати quotas/rate limiting. Паралельно погодити реальний медичний набір і прогнозну ціль.
