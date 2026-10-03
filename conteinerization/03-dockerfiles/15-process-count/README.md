# Процеси sleep

Команди виконуються в каталозі 15-process-count у Bash (Linux або WSL).

Резервний приклад. Повторіть запуск із тегами simple-shell, wait-shell та explicit-shell. У перевіреному Alpine очікуються 1, 1, 2 та 2 процеси. Оптимізація простої команди залежить від оболонки.

```bash
docker build -f Dockerfile.direct -t lecture3-process-direct:review .
docker build -f Dockerfile.simple-shell -t lecture3-process-simple-shell:review .
docker build -f Dockerfile.wait-shell -t lecture3-process-wait-shell:review .
docker build -f Dockerfile.explicit-shell -t lecture3-process-explicit-shell:review .
docker run -d --name lecture3-process lecture3-process-direct:review
docker top lecture3-process -eo pid,ppid,comm
docker rm -f lecture3-process
```

