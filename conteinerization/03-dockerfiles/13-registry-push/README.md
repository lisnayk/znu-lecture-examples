# Docker Hub та ECR

Команди виконуються в каталозі 13-registry-push у Bash (Linux або WSL).

Спочатку виконайте 01-hello-image і створіть власний репозиторій hello-image у Docker Hub. Замініть Docker ID. У запиті пароля введіть access token. Push публікує образ зовні.

```bash
HUB_USER='your-docker-id'
docker login --username "$HUB_USER"
docker tag hello-image:1.0 "$HUB_USER/hello-image:1.0"
docker push "$HUB_USER/hello-image:1.0"
```

## Amazon ECR

Налаштуйте AWS CLI чинними тимчасовими credentials Learner Lab, включно з session token. Створіть репозиторій hello-image. Замініть ID облікового запису та регіон власними значеннями.

```bash
REGION='us-east-1'
AWS_ACCOUNT_ID='123456789012'
REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
aws sts get-caller-identity
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$REGISTRY"
docker tag hello-image:1.0 "$REGISTRY/hello-image:1.0"
docker push "$REGISTRY/hello-image:1.0"
```

