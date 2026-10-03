# Параметри ARG

Команди виконуються в каталозі 02-arg у Bash (Linux або WSL).

Очікуються 2.0 та «ARG відсутній».

```bash
docker build --build-arg APP_VERSION=2.0 -t lecture3-arg-review .
docker image inspect lecture3-arg-review --format '{{index .Config.Labels "org.opencontainers.image.version"}}'
docker run --rm lecture3-arg-review
```

