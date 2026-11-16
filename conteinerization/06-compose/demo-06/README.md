# Демо 6. Готовність сервісу й повторні запуски клієнта

Обидва файли Compose самодостатні. У кожному вебсервер запускається із затримкою в п’ять секунд, а клієнт робить один HTTP-запит на запуск. Політика `restart: "on-failure:8"` дозволяє Docker зробити до восьми повторних запусків після ненульового коду завершення.

Перший варіант використовує короткий запис `depends_on: [web]`.

```bash
docker compose up -d --force-recreate
docker compose logs client
docker compose ps -a
```

У журналі клієнта з’являться рядки `Connection refused`. Повторіть `docker compose logs client` за кілька секунд, щоб побачити `ready`. Зрештою клієнт завершується з кодом 0.

Якщо `web` уже працює, звичайний `up -d` може запустити клієнт після того, як сервер готовий. Параметр `--force-recreate` заново запускає п’ятисекундну затримку сервера. Стан `Exited (0)` означає, що одноразовий клієнт завершився після успішного запиту.

Другий варіант використовує `service_healthy`.

```bash
docker compose -f compose.ready.yaml up -d
docker compose -f compose.ready.yaml logs client
docker compose -f compose.ready.yaml ps -a
```

Compose чекає успішної HTTP-перевірки `web`. У журналі клієнта очікується `ready` з першої спроби. Команда `ps -a` показує клієнт навіть після його завершення. Файли задають різні імена проєктів, тому команда перегляду журналів має посилатися на потрібний файл.

Після демонстрації зупиніть обидва проєкти.

```bash
docker compose down
docker compose -f compose.ready.yaml down
```
