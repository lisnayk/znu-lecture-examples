# Власний HTTP-образ

Команди виконуються в каталозі 01-hello-image у Bash (Linux або WSL).

Сторінка http://localhost:3000/. На початку HEALTHCHECK може мати стан starting.

```bash
docker build -t hello-image:1.0 .
docker run -d --name lecture3-hello -p 3000:3000 hello-image:1.0
curl --retry 10 --retry-connrefused --retry-delay 1 http://localhost:3000/
docker exec lecture3-hello id
docker inspect --format '{{.State.Health.Status}}' lecture3-hello
docker stop lecture3-hello
docker rm lecture3-hello
```

