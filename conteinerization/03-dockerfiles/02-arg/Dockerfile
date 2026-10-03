FROM node:22-alpine
ARG APP_VERSION=1.0
LABEL org.opencontainers.image.version="${APP_VERSION}"
CMD ["node", "-e", "console.log(process.env.APP_VERSION ?? 'ARG відсутній')"]
