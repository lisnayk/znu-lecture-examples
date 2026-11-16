# Демо 3. Публічна й приватна мережі

Браузер або `curl` звертається до опублікованого порту шлюзу. Шлюз підключений до обох мереж. Він пересилає запит до `api` через мережу `private`. Контейнер `api` підключено лише до `private`.

```bash
docker compose up -d
curl -fsS http://127.0.0.1:8083/api/
docker compose ps
```

Очікувана відповідь — `{"service":"api","network":"private"}`. На хості має бути опубліковано лише порт шлюзу. Контейнер із мережі `public` не знайде адресу `api`.

```bash
docker run --rm --network demo-public-private_public alpine:3.22 nslookup api
docker compose down
```

У виводі перевірки DNS очікуйте відсутність адреси для `api`.
