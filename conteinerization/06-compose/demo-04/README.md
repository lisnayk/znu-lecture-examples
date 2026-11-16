# Демо 4. Спільні MySQL і Memcached для трьох проєктів

Спочатку створіть спільну мережу й запустіть проєкт `demo-data`. Його контейнери мають фіксовані імена, які використовують два клієнтські проєкти в `external_links`.

```bash
docker network create demo04-shared
docker compose -f compose.data.yaml up -d --wait --wait-timeout 120
docker compose -f compose.catalog.yaml run --rm app
docker compose -f compose.report.yaml run --rm app
```

Обидва клієнти звертаються до MySQL за псевдонімом `db`, а до Memcached — за `cache`. Каталог виводить `MySQL: shop` і `Memcached: STORED`. Звіт читає запис, зроблений каталогом, і виводить `MySQL: shop` та `Memcached: shop`. Порти бази та кешу доступні в спільній мережі.

Після демонстрації виконайте наведені команди. Параметр `--volumes` видаляє демонстраційний том MySQL.

```bash
docker compose -f compose.catalog.yaml down
docker compose -f compose.report.yaml down
docker compose -f compose.data.yaml down --volumes
docker network rm demo04-shared
```
