# Протокол реальних даних і майбутнього MLP-дослідження

Стан 23.11.2026: дослідницький кандидат і підготовчий код, **не навчена модель**. `training_approved=false`, HTTP ML-сервіс і далі повертає чесну недоступність. Немає оцінок accuracy/MAE/RMSE та підстав заявляти новизну чи причинний вплив.

## Перевірені джерела та альтернативи

| Джерело | Фактично перевірено | Обмеження |
|---|---|---|
| [CDC NHSN HRD, ua7e-t2fy](https://data.cdc.gov/Public-Health-Surveillance/Weekly-Hospital-Respiratory-Data-HRD-Metrics-by-Ju/ua7e-t2fy) | Metadata API: `USGOV_WORKS`, Public Domain U.S. Government; weekly, US national/region/state агрегати. API доступний, потрібні поля існують | Територія США, не Україна; reporting regimes/coverage змінюються, per-row історичний час доступності не верифіковано |
| [ЦГЗ України, грип/ГРВІ](https://phc.org.ua/kontrol-zakhvoryuvan/inshi-infekciyni-zakhvoryuvannya/zakhvoryuvanist-na-grip-ta-grvi-v-ukraini) | Офіційний архів тижневих бюлетенів, зокрема за 2026 рік | Не завантажено й не нормалізовано повну серію; ліцензія повторного використання та стабільна регіональна схема не підтверджені. Не оголошувати готовим ML dataset |
| [Eurostat demo_r_mwk_05](https://ec.europa.eu/eurostat/databrowser/view/demo_r_mwk_05/default/table) | Офіційний [каталог демографічних серій](https://ec.europa.eu/eurostat/documents/12743486/13006269/demography-population-stock-balance.pdf/59988f2d-7238-e8d0-8f7b-2b601aba1609) містить тижневі смерті за статтю/віком | Це інша ціль; географію, лаги публікації й конкретні умови серії треба перевірити. Загальна [політика reuse](https://ec.europa.eu/eurostat/help/copyright-notice) має винятки; повного аудиту серії не виконано |

Для CDC реально прочитано metadata та **агреговані статистики**, не повний набір медичних рядків: 21 976 записів, 67 jurisdiction labels (включно з агрегатами різного рівня), дати 08.08.2020–14.11.2026. Для `FL`, `totalconfflunewadm IS NOT NULL`: 318 тижнів, 17.10.2020–14.11.2026. Це кількість непорожніх записів, **не доказ повної/однорідної щотижневої історії**. Точний знімок фактів, одиниць і ліцензій — `reports/phase3-public-sources.json`; відтворення — `scripts/inspect_public_sources.py`.

Семантика перевірених CDC полів: `weekendingdate` — MMWR week end, `jurisdiction` — географічний рівень, `totalconfflunewadm` — нові госпіталізації з підтвердженим грипом за неділю–суботу, `totalconfflunewadmhosprep` і `totalconfflunewadmperchosprep` — reporting coverage. Не змішувати national/state/region як незалежні території; не вважати counts показником на 100 тисяч. [CDC методологія](https://www.cdc.gov/nhsn/psc/hospital-respiratory-reporting/data-methods.html) і [опис режиму звітності з листопада 2024](https://www.cdc.gov/respiratory-viruses/data/illness-severity.html) потрібні для визначення порівнюваного періоду.

## Конкретна прогнозна задача — кандидат до погодження

Передбачити **кількість нових госпіталізацій із підтвердженим грипом у штаті Florida, США, за наступний повний тиждень неділя–субота** за погодними агрегатами, календарем і лише фактично доступною історією госпіталізацій. Issue time: 00:00 UTC неділі на початку цільового тижня. Health lags 2–5 тижнів обрані консервативно через затримку звітності; навіть вони допустимі лише за перевіреного `available_at <= issue_time`. Погодний прогноз для майбутнього тижня не використовується без зафіксованих forecast vintages.

**Це не остаточна заміна української постановки.** Територію, ціль, горизонт і допустимість США потрібно погодити з керівником. Якщо потрібна Україна, пріоритет — легальна й відтворювана серія ЦГЗ або інше дозволене джерело, зі зміною protocol до експериментів. Наявні місячні climate_data без географії та CSV без медичної цілі до Florida не приєднуються. HRI не використовується як observed health target.

## Dataset pipeline

1. **Acquire — спроєктовано.** Для дозволених джерел зберегти незмінні raw snapshots, URL/params, UTC retrieval time, license/citation, SHA256. Raw data поза Git; manifests не містять ключів або персональних даних. У фазі 3 отримано тільки metadata/aggregate evidence.
2. **Validate — частково реалізовано.** Перевірити поля/одиниці, null/suppression, coverage, дублікати, зміни звітності й географічний рівень. Поточні pure functions перевіряють finite values, календар і доступність; перевіреного CDC-to-normalized adapter поки немає.
3. **Normalize — контракт.** Health: `region_id`, Saturday `week_end`, nonnegative `admissions`, timezone-aware `available_at`, provenance/snapshot ID, coverage. Weather: такий самий region/week, `mean_temp`, `mean_humidity`, перевірені одиниці, availability і provenance. Однієї глобальної дати оновлення metadata недостатньо для історичного `available_at`.
4. **Geo/time alignment — спроєктовано.** Погодні сітки агрегувати до того самого штату з перевіреними межами й вагами населення; одна точка Miami або Lviv не замінює штат. Перевірити календар MMWR, часову зону й правила агрегації. Для historical reanalysis не приписувати минулу оперативну доступність без доказу.
5. **Features — реалізований прототип** `ml_pipeline/weekly.py`: перевірені Saturday keys, унікальний region/week у snapshot, timezone-aware publication timestamps, доступні lagged health/climate features. Пропуски лишаються null; невідомі availability timestamps не вигадуються. `features_complete` не означає `training_approved`.
6. **Splits/fit — спроєктовано.** Rolling-origin за цілими тижнями, однакові folds для всіх моделей; preprocessing/imputation/scaling fit тільки на train. Тестові тижні не впливають на tuning, lag selection чи early stopping. Перевірити vintage labels і виключити ознаки, які опубліковані після issue.
7. **Artifacts — спроєктовано.** Dataset manifests, mapping, quality report, fold indices, fitted transforms, commit/software versions, seeds, конфігурація й передбачення зберігаються разом. Результати не перезаписують raw snapshots; промоція моделі до HTTP — лише після незалежної перевірки.

## Baseline → MLP та відтворюваність

Почати з last available count (pure prototype реалізовано), seasonal available week-52 count і регуляризованої Poisson regression. Мала MLP 16→8 розглядається як кандидат, не гарантовано краща модель. Сітку параметрів і п’ять seeds фіксувати до відкриття test. Порівнювати MAE/RMSE, Poisson deviance для коректних nonnegative predictions і парні block-bootstrap intervals; MAPE не робити головною метрикою через можливі нулі. Для baseline і MLP використовувати ті самі часові розбиття та доступні ознаки.

Проєктні мінімальні вікна: 52 train / 13 validation / 26 test тижнів, з повними lag features і перевіркою reporting regime. Це нижня технічна межа, не обґрунтування статистичної достатності: сезонів може бути замало, а 318 непорожніх тижнів не гарантують валідних examples. За браку даних відкласти MLP/послабити задачу після погодження, а не заявляти виграш. LSTM/GRU зараз не обґрунтовані.

Версійований протокол — `experiments/weekly_flu_v01.json`. У цьому етапі не виконано training, tuning, scoring або нейромережевий inference. Інфекційна сезонність, поведінка, демографія, вакцинація, reporting coverage й інші фактори можуть змішувати асоціацію; кореляція або прогнозна перевага не встановлює причинного впливу клімату.
