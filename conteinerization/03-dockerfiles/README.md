# Приклади лекції 3. Dockerfile

Потрібні Docker із запущеним Engine, Bash (Linux або WSL), curl і tar. Для ECR також потрібні AWS CLI та дозволений обліковий запис.

Виконуйте приклади за номерами. Перейдіть у каталог прикладу та скопіюйте команди з README. Запуски не потребують .sh-скриптів. Імена контейнерів мають бути вільними, порти 3000 та 8080 доступними. Контейнери прибираються останніми командами, образи лишаються локально.

- [01-hello-image: Власний HTTP-образ](./01-hello-image/README.md)
- [02-arg: Параметри ARG](./02-arg/README.md)
- [03-add-archive: ADD та COPY архіву](./03-add-archive/README.md)
- [04-run-forms: Форми RUN](./04-run-forms/README.md)
- [05-adduser: Створення користувача](./05-adduser/README.md)
- [06-entrypoint-cmd: ENTRYPOINT та CMD](./06-entrypoint-cmd/README.md)
- [07-signals: Сигнали](./07-signals/README.md)
- [08-entrypoint-overrides: Перевизначення запуску](./08-entrypoint-overrides/README.md)
- [09-entrypoint-cmd-matrix: Матриця ENTRYPOINT та CMD](./09-entrypoint-cmd-matrix/README.md)
- [10-nginx-process-count: Nginx, htop та зупинка](./10-nginx-process-count/README.md)
- [11-cache-reuse: Кеш кроків](./11-cache-reuse/README.md)
- [12-multistage: Багатоетапна збірка](./12-multistage/README.md)
- [13-registry-push: Docker Hub та ECR](./13-registry-push/README.md)
- [14-layers-cache: Шари та тимчасові файли](./14-layers-cache/README.md)
- [15-process-count: Процеси sleep](./15-process-count/README.md)

```bash
cd 01-hello-image
# Виконайте команди README.md.
cd ../02-arg
# Продовжуйте за списком.
```

14 і 15 є резервними прикладами. 13 публікує образ зовні, виконуйте його лише у власному або дозволеному реєстрі.

