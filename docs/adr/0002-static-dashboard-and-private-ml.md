# ADR 0002: статичний dashboard і приватний ML-сервіс

Дата: 23.11.2026. Статус: спроєктовано.

Рішення: React/TypeScript/Vite для цільового SPA, Leaflet і ECharts; Flask REST API та окремий FastAPI/PyTorch ML API. Навчання відокремлене від запиту. До створення SPA зберігаються Jinja2-сторінки.

Два вузли: Application Droplet із proxy/static/backend і ML Droplet із CPU inference. MySQL доступна лише application-контурові. VPC не замінює TLS, ідентифікацію сервісів і тайм-аути. Відмова ML не підміняється HRI чи константним медичним прогнозом.

Наслідки: незалежний випуск моделі й сервісу, але потрібні сумісні контракти та захищений канал. Сьогодні HTTP inference, SPA й production-розгортання не реалізовані. Docker Compose і Terraform є засобами подальшого розгортання, не свідченням його завершення.
