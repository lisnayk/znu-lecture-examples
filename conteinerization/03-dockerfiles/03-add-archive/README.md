# ADD та COPY архіву

Команди виконуються в каталозі 03-add-archive у Bash (Linux або WSL).

ADD створює /app/index.html, COPY залишає /copied/site.tar.

```bash
tar -cf site.tar -C site index.html
docker build -t lecture3-add-review .
docker run --rm lecture3-add-review
docker run --rm lecture3-add-review ls -l /app /copied
```

