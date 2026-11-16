# Лекція 6. Docker Compose

Запуск багатоконтейнерного застосунку

## Приклади

### [`demo-01`](./demo-01/)

```bash
cd conteinerization/06-compose/demo-01
docker compose up -d
```

### [`demo-02`](./demo-02/)

```bash
cd conteinerization/06-compose/demo-02
cp .env.example .env
```

### [`demo-03`](./demo-03/)

```bash
cd conteinerization/06-compose/demo-03
docker compose up -d
```

### [`demo-04`](./demo-04/)

```bash
cd conteinerization/06-compose/demo-04
docker network create demo04-shared
```

### [`demo-05`](./demo-05/)

```bash
cd conteinerization/06-compose/demo-05
install -d -m 700 .local
```

### [`demo-06`](./demo-06/)

```bash
cd conteinerization/06-compose/demo-06
docker compose up -d --force-recreate
```
