# Перевірка HCP State перед варіантом B

26.11.2026. Виконано read-only перегляд через уже авторизовану браузерну сесію користувача. Налаштування авторизації, workspaces та runs не змінювалися; повний state не завантажувався й не експортувався.

| Перевірка | Спостереження |
|---|---|
| Організація | diploma-2025, список показує2 workspaces |
| Відповідний workspace | ClimateHealth-Monitoring; repository BohdanHavran/ClimateHealth-Monitoring |
| Working Directory | infrastructure/terraform |
| States | **This workspace currently has no states saved** |
| Resources |0; **This workspace doesn't have any resources** |
| Поточні managed resource addresses | Відсутні у збереженому state цього workspace |
| Старі addresses22 moved blocks | Не існують у state цього workspace, оскільки немає state versions |
| Runs | All2, Errored2, Success0; новий run не запускався |
| Execution / version | Remote, Terraform1.17.2 |
| Auto Apply / Auto Destroy | UI/API/VCS Auto Apply Off, run-trigger Auto Apply Off, Auto Destroy Off |
| dev/production | climatehealth-dev і climatehealth-production відсутні у видимому списку. Це запропоновані майбутні workspaces, не перевірені окремі states |
| Інший workspace | Diploma повʼязаний з іншим репозиторієм BohdanHavran/Diploma; його state не досліджувався і не змінювався |

Джерела UI: [workspace](https://app.terraform.io/app/diploma-2025/workspaces/ClimateHealth-Monitoring), [States](https://app.terraform.io/app/diploma-2025/workspaces/ClimateHealth-Monitoring/states), [Runs](https://app.terraform.io/app/diploma-2025/workspaces/ClimateHealth-Monitoring/runs).

Висновок про відсутність state ґрунтується на явній сторінці States, а не на помилках Plan. У доступній історії немає успішних runs; це не універсальний доказ, що в AWS немає unmanaged resources, видалених states або іншої організації. Жодні AWS account APIs тут не викликалися.

Для цього ще не розгорнутого root дозволено спрощення адрес і вилучення22 speculative moved blocks без міграції state. Не застосовувати новий код до стороннього чи раніше створеного state без окремої перевірки. Перед майбутнім Plan повторно перевірити state, оскільки спостереження може застаріти. Збіги назв із unmanaged AWS resources залишаються ризиком першого deployment.
