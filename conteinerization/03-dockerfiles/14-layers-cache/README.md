# Шари та тимчасові файли

Команди виконуються в каталозі 14-layers-cache у Bash (Linux або WSL).

Резервний приклад. Видалення файла наступним RUN залишає його в попередньому шарі. Точні розміри залежать від бази та пакетів.

```bash
docker build -f Dockerfile.many -t layers-many:1.0 .
docker build -f Dockerfile.one -t layers-one:1.0 .
docker build -f Dockerfile.leak -t layers-leak:1.0 .
docker build -f Dockerfile.clean -t layers-clean:1.0 .
docker image inspect layers-many:1.0 layers-one:1.0 layers-leak:1.0 layers-clean:1.0 --format '{{.RepoTags}} layers={{len .RootFS.Layers}} bytes={{.Size}}'
```

