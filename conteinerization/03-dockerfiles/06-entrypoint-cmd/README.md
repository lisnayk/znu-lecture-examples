# ENTRYPOINT та CMD

Команди виконуються в каталозі 06-entrypoint-cmd у Bash (Linux або WSL).

Shell підставляє GREETING, exec друкує $GREETING. PID у docker top належать хосту. Проста команда Alpine ash може замінити оболонку через exec.

```bash
docker build -f Dockerfile.shell -t ep-shell:1.0 .
docker build -f Dockerfile.exec -t ep-exec:1.0 .
docker run --rm ep-shell:1.0
docker run --rm ep-exec:1.0
docker build -f Dockerfile.both -t ep-both:1.0 .
docker run --rm ep-both:1.0
docker run --rm ep-both:1.0 127.0.0.2
docker build -f Dockerfile.simple -t ep-simple:1.0 .
docker build -f Dockerfile.loop -t ep-loop:1.0 .
docker run -d --name lecture3-simple ep-simple:1.0
docker run -d --name lecture3-loop ep-loop:1.0
docker top lecture3-simple -eo pid,ppid,args
docker top lecture3-loop -eo pid,ppid,args
docker rm -f lecture3-simple lecture3-loop
```

