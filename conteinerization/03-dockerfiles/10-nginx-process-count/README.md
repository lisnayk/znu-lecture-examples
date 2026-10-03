# Nginx, htop та зупинка

Команди виконуються в каталозі 10-nginx-process-count у Bash (Linux або WSL).

Вийдіть із htop клавішею q перед вимірюванням. Повторіть команди від docker run, змінюючи тег на simple-shell, wait-shell та explicit-shell.

Без htop у перевіреному Alpine очікуються 2, 2, 3 та 3 процеси. htop додає один процес. Direct і simple-shell завершуються швидко з кодом 0, варіанти з wait досягають таймаута 5 секунд і коду 137. Час включає витрати Docker CLI.

```bash
docker build -f Dockerfile.direct -t lecture3-nginx-direct:review .
docker build -f Dockerfile.simple-shell -t lecture3-nginx-simple-shell:review .
docker build -f Dockerfile.wait-shell -t lecture3-nginx-wait-shell:review .
docker build -f Dockerfile.explicit-shell -t lecture3-nginx-explicit-shell:review .
docker run -d --name lecture3-nginx lecture3-nginx-direct:review
docker top lecture3-nginx -eo pid,ppid,args
docker exec -it -e TERM=xterm lecture3-nginx htop --tree
time docker stop --signal SIGTERM --timeout 5 lecture3-nginx
docker inspect --format '{{.State.ExitCode}}' lecture3-nginx
docker rm lecture3-nginx
```

