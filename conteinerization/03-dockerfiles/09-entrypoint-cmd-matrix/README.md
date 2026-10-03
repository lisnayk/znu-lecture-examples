# Матриця ENTRYPOINT та CMD

Команди виконуються в каталозі 09-entrypoint-cmd-matrix у Bash (Linux або WSL).

none/none очікувано повертає «no command specified». Решта конфігурацій лише створюються. app і tool є умовними програмами, їх не запускаємо.

```bash
for entry in none shell exec; do
  for cmd in none exec args shell; do
    image="lecture3-matrix-${entry}-${cmd}:review"
    docker build -q -f "Dockerfile.${entry}-${cmd}" -t "$image" .
    if [ "$entry/$cmd" = none/none ]; then
      docker create "$image"
    else
      cid=$(docker create "$image")
      docker inspect --format '{{json .Path}} {{json .Args}}' "$cid"
      docker rm "$cid"
    fi
  done
 done
```

