# Демо 5. Конфігурація та секрет для MySQL

Файл `app.ini` задає хост і назву бази, а також ім’я користувача. Compose монтує його в контейнері `app` через `configs`. Пароль лежить у локальному файлі, який Compose надає контейнерам `app` і `db` через `secrets`.

Підготуйте локальний пароль один раз. Для генерації потрібна команда `openssl`.

```bash
install -d -m 700 .local
if [ ! -s .local/db-password.txt ]; then
  openssl rand -hex 24 > .local/db-password.txt
  chmod 0444 .local/db-password.txt
fi
```

Каталог `.local` виключено з Git. Права на каталог приховують файл від інших користувачів хоста. Сам файл доступний для читання в контейнері, зокрема процесу MySQL зі своїм UID.

```bash
docker compose up -d --wait --wait-timeout 120 db
docker compose run --rm app
docker compose down
```

Очікуваний результат — `MySQL: shop`. PHP виконує запит, використовуючи налаштування з `/etc/demo/app.ini` і пароль із `/run/secrets/db_password`. У журналі виводиться тільки назва бази.

Якщо потрібно змінити пароль і повторити ініціалізацію, спочатку виконайте `docker compose down --volumes`. Команда видаляє дані демонстраційної бази. Зміна локального файла сама собою не змінює пароль у вже ініціалізованій базі.
