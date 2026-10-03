# Багатоетапна збірка

Команди виконуються в каталозі 12-multistage у Bash (Linux або WSL).

Сторінка http://localhost:8080/. Розмір у байтах. У фінальному образі немає Node.js та /app.

```bash
docker build -t multistage:1.0 .
docker build -f Dockerfile.single -t singlestage:1.0 .
docker image inspect multistage:1.0 singlestage:1.0 --format '{{.RepoTags}} {{.Size}}'
docker run -d --name lecture3-multistage -p 8080:80 multistage:1.0
curl --retry 10 --retry-connrefused --retry-delay 1 http://localhost:8080/
docker exec lecture3-multistage sh -c 'command -v node || echo "Node.js відсутній"; test ! -d /app && echo "/app відсутній"'
docker stop lecture3-multistage
docker rm lecture3-multistage
```

