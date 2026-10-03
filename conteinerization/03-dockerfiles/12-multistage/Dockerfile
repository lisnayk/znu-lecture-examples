# Етап збірки: тут є Node.js та все, що потрібно для генерації статики.
FROM node:22-alpine AS build
WORKDIR /app
COPY src/ ./src/
RUN node src/build.js

# Етап віддачі: у фінальний образ потрапляє лише результат збірки.
FROM nginx:1.30-alpine AS prod
COPY --from=build /app/dist/ /usr/share/nginx/html/
EXPOSE 80
# Nginx має працювати на передньому плані, інакше контейнер одразу завершиться.
CMD ["nginx", "-g", "daemon off;"]
