# Terraform: безпечний початковий каркас

Статус: підготовлено локальні `main.tf`, `versions.tf`, `providers.tf`, `variables.tf`, `outputs.tf`, приклади backend/змінних і PR workflow. Провайдер закріплено за версією `2.109.0`, Terraform `>=1.11,<2`. Ресурси ще не створено; не встановлені reverse proxy, сервіси, секрети, моніторинг і backup бази. Схема Managed MySQL, Spaces та registry наразі є проєктом, не Terraform-ресурсами.

**Перевірки:** локальна команда `terraform fmt -check -recursive` пройшла з Terraform 1.10.2. `terraform init -backend=false -input=false` зупинилася на перевірці потрібної версії 1.11 до завантаження провайдера. `terraform validate`, план та CI ще не виконувались. Локальний binary — windows_386; перш ніж встановлювати іншу версію/провайдера, окремо перевірити сумісність платформи та отримати дозвіл. Немає `.terraform.lock.hcl`: створити його з checksum після погодженого `terraform init` і перевірити для локальної та CI-платформ перед комітом.

## Безпечне налаштування state

Порожній `backend "s3" {}` — partial конфігурація; файл `backend.spaces.hcl.example` містить лише приклад без секретів. Для dev/prod потрібні різні bucket або keys, доступи й журнали; використовувати окремі state, не один workspace для всіх. Bucket створюють і контролюють окремим погодженим bootstrap-процесом, з приватним доступом, versioning, журналом доступу, обмеженим доступом і перевіреним відновленням. State і plan можуть містити секрети. Backend credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) передавати безпосередньо як environment secrets, а не зберігати у HCL або командах shell.

DigitalOcean у [своєму посібнику](https://docs.digitalocean.com/products/spaces/reference/terraform-backend/) документує сумісність S3 backend і lockfile для Terraform `~>1.11`; приклад містить `skip_*`, `use_lockfile=true`, endpoint і `region=us-east-1` як конфігурацію S3-провайдера. Це документація можливості, а не підтверджена перевірка нашого bucket. До виробничого плану перевірити атомарне взаємне блокування двома ізольованими процесами, права на `.tflock`, versioning, відновлення і відсутність обходів через `-lock=false`. Якщо тест lockfile/атомарності не пройде, використати HCP Terraform з керованим blocking та окремими середовищами або інший backend із гарантованим server-side locking. Одного GitHub `concurrency` для кількох операторів недостатньо.

## Дії після погодження

1. Підготувати Terraform 1.11+ відповідної архітектури, ізольовані dev/prod, облікові записи з мінімальними правами; визначити region, IP-план, вузький SSH CIDR, fingerprint публічного ключа, перевірити вартість.
2. Прочитати та скоригувати `terraform.tfvars.example`; він має документаційну IP-адресу й placeholder і не є працездатними credentials. Реальні tfvars зберігати поза Git. Ніколи не додавати в репозиторій токени, приватні ключі, state або файли plan.
3. Для локальної статичної перевірки — `terraform fmt -check -recursive`, `terraform init -backend=false -input=false`, `terraform validate` за наявності зафіксованого провайдера. Ці дії не створюють інфраструктуру, але init завантажує провайдер.
4. Для довіреного середовища після налаштування state — `terraform init -backend-config=...`, `terraform plan -out=...`, `terraform show ...`; погодити **конкретний** збережений план, конфігурацію та зміну ресурсів. Артефакт плану чутливий, має бути захищений.
5. Лише після окремого дозволу — застосувати той самий перевірений plan, перевірити стан, health, SSH, приватний маршрут і правила firewall. `terraform destroy` автоматично не запускається і потребує окремого прямого дозволу. Повернення контейнерного образу не відкочує схему MySQL; резервна копія й окремий план міграції обов’язкові.

## CI/CD і production gate

`.github/workflows/terraform-ci.yml` запускає fmt, init без state і credentials, validate та Checkov на PR/manual; `contents: read`, actions прив’язані до SHA, GitHub-секрети не передаються в PR. Після init workflow завантажує зафіксований провайдер та встановлює Checkov у CI. Перевірки ще не запускались у GitHub, політики Checkov можуть обґрунтовано виявити відкриті 80/443 або вимкнені backup.

Окремий довірений plan/apply pipeline навмисно не активовано: конкретне приватне state-сховище, ідентифікатори середовищ, секрети, захист артефактів і право підтвердження ще не налаштовані. Перед створенням pipeline потрібна схема: plan лише з довіреної гілки з мінімальними правами → збережений зашифрований plan і хеш коміту/провайдера/inputs → незалежний перегляд → підтвердження → apply **того самого** plan, без повторного планування. Жодного секрету недовіреним PR. GitHub зазначає, що required reviewers на Free/Pro/Team доступні лише для публічних репозиторіїв; у приватному Free необхідний інший надійний approval механізм або контрольований ручний apply оператором, а не фіктивний environment gate: [документація](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments). Немає автоматичного apply або destroy.

## До першого застосування

Поточні правила дозволяють публічні 80/443 тільки для вебсервера, SSH лише admin CIDR і ML-порт лише з application Droplet. На сервері ML треба прив’язати API до приватного IP, налаштувати service identity/mTLS або інший перевірений механізм, таймаути та захист секретів. На application потрібно розгорнути HTTPS reverse proxy; у каркасі його немає. Доступ до MySQL, узгоджений backup і managed-доступ ще потрібно спроєктувати та протестувати. Виявлені можливі витрати — у `INFRASTRUCTURE.md`. **Неперевірений каркас не є готовою до production інфраструктурою.**
