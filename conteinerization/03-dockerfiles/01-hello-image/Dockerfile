# Базовий образ із явним тегом: latest змінюється без попередження.
FROM node:22-alpine

# Метадані образу; видно в docker image inspect.
LABEL org.opencontainers.image.title="hello-image" \
      org.opencontainers.image.description="Приклад лекції 3: власний образ із Dockerfile" \
      org.opencontainers.image.version="1.0"

# Каталог за замовчуванням для наступних інструкцій і для процесу контейнера.
WORKDIR /app

# Копіюється лише те, що потрібно для роботи; решту відсікає .dockerignore.
COPY server.js ./

# Значення за замовчуванням; змінюються ключем -e.
ENV PORT=3000 \
    APP_TITLE="Образ зібрано з Dockerfile"

# Документує порт. Публікує його ключ -p, не ця інструкція.
EXPOSE 3000

# Процес не працює від root; користувач node є в образі.
USER node

# Демон позначить контейнер healthy або unhealthy.
HEALTHCHECK --interval=10s --timeout=3s --start-period=2s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/healthz || exit 1

# Exec-форма — процес отримує сигнали без оболонки.
CMD ["node", "server.js"]
