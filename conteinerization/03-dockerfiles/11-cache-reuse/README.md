# Кеш кроків

Команди виконуються в каталозі 11-cache-reuse у Bash (Linux або WSL).

Без змін кроки мають статус CACHED. Зміна app.js залишає кеш залежностей. Зміна вмісту package.json повторює npm ci та наступні кроки. Залежностей немає. Джерела не змінюються, тимчасовий каталог лишається в CACHE_DIR.

```bash
CACHE_DIR=$(mktemp -d)
cp Dockerfile package.json package-lock.json app.js "$CACHE_DIR/"
docker build --progress=plain --no-cache -t lecture3-cache:review "$CACHE_DIR"
docker build --progress=plain -t lecture3-cache:review "$CACHE_DIR"
printf "console.log('Версія 2')\n" > "$CACHE_DIR/app.js"
docker build --progress=plain -t lecture3-cache:review "$CACHE_DIR"
printf '\n' >> "$CACHE_DIR/package.json"
docker build --progress=plain -t lecture3-cache:review "$CACHE_DIR"
docker run --rm lecture3-cache:review
```

