# Демо 2. Відновлення MySQL із SQL-дампа

У новій копії прикладу створіть локальний файл `.env` із навчальними значеннями.

```bash
cp .env.example .env
docker compose config --quiet
docker compose up -d --wait --wait-timeout 120
docker compose exec db sh -c 'MYSQL_PWD="$MYSQL_PASSWORD" mysql -h 127.0.0.1 -u "$MYSQL_USER" "$MYSQL_DATABASE" -e "SELECT * FROM products ORDER BY id"'
```

Команда `docker compose config --quiet` перевіряє конфігурацію. За успішної перевірки виводу немає.

Compose читає `.env` і підставляє назву бази, користувача й пароль у секцію `environment`. Під час першого запуску MySQL виконує `backup.sql` у порожньому томі. Результат запиту містить два рядки, `USB-C cable` та `HDMI adapter`.

Зупинити проєкт і зберегти дані:

```bash
docker compose down
```

Зупинити проєкт і видалити демонстраційний том `data`:

```bash
docker compose down --volumes
```

Видалення тому стирає його дані. Після наступного запуску MySQL створить новий том і повторно застосує дамп.
