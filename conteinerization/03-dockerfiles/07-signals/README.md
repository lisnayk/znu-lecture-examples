# Сигнали

Команди виконуються в каталозі 07-signals у Bash (Linux або WSL).

SIGTERM і SIGINT дають код 0. Ігнорування SIGTERM у цьому прикладі призводить до SIGKILL і коду 137.

```bash
docker build -t lecture3-signals-review .
docker run -d --name lecture3-term lecture3-signals-review
until docker logs lecture3-term 2>&1 | grep -q READY; do sleep 0.1; done
docker stop --timeout 3 lecture3-term
docker logs lecture3-term
docker inspect --format '{{.State.ExitCode}}' lecture3-term
docker rm lecture3-term
docker run -d --name lecture3-int lecture3-signals-review
until docker logs lecture3-int 2>&1 | grep -q READY; do sleep 0.1; done
docker kill --signal SIGINT lecture3-int
docker wait lecture3-int
docker logs lecture3-int
docker rm lecture3-int
docker run -d --name lecture3-kill -e IGNORE_TERM=1 lecture3-signals-review
until docker logs lecture3-kill 2>&1 | grep -q READY; do sleep 0.1; done
docker stop --timeout 1 lecture3-kill
docker inspect --format '{{.State.ExitCode}}' lecture3-kill
docker rm lecture3-kill
```

