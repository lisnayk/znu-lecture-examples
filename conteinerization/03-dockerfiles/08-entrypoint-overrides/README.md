# Перевизначення запуску

Команди виконуються в каталозі 08-entrypoint-overrides у Bash (Linux або WSL).

Очікуються «Привіт Docker», «Привіт студенти», «Інша програма».

```bash
docker build -t ep-demo:1.0 .
docker run --rm ep-demo:1.0
docker run --rm ep-demo:1.0 студенти
docker run --rm --entrypoint echo ep-demo:1.0 "Інша програма"
```

