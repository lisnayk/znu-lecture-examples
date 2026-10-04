# EC2 Metadata Explorer

Демонстраційний вебзастосунок читає EC2 Instance Metadata Service через IMDSv2
і показує доступні поля інстанса. User data встановлює Git і Python,
завантажує застосунок із репозиторію та вмикає службу systemd.

## Запуск в EC2

1. Відкрийте [каталог демо у znu-lecture-examples](https://github.com/lisnayk/znu-lecture-examples/tree/main/it-infrastructure/examples/ec2-metadata)
   та скопіюйте повний текст [user-data.sh](user-data.sh).
2. Репозиторій і шлях уже задано в скрипті. `REPO_URL` дорівнює
   `https://github.com/lisnayk/znu-lecture-examples.git`,
   `GIT_REF` — `main`, `APP_SUBDIR` —
   `it-infrastructure/examples/ec2-metadata`.
   Для іншої версії задайте гілку, тег або повний SHA коміту в `GIT_REF`.
   Для окремого репозиторію з `app.py` у корені встановіть `APP_SUBDIR="."`.
3. Створіть інстанс з офіційним AMI Ubuntu Server 24.04 LTS або Amazon Linux 2023.
   Інстансу потрібен вихід до Git-сервера та репозиторіїв пакетів.
4. Для відкриття сторінки напряму з Інтернету виберіть підмережу з маршрутом
   до Internet Gateway і ввімкніть призначення публічної IPv4-адреси.
   У Security Group дозвольте TCP 80 зі своєї IP-адреси (`My IP`).
   Для діагностики через SSH додайте TCP 22 із тієї самої адреси та виберіть key pair.
5. У `Advanced details` увімкніть metadata endpoint і встановіть
   `IMDSv2 = Required`. Hop limit 1 достатній для запуску без контейнера.
   Для читання тегів увімкніть `Allow tags in instance metadata`.
6. Вставте повний текст `user-data.sh` у поле `User data` та створіть інстанс.
   Для цього демо не потрібно призначати IAM role.
7. Після завершення встановлення відкрийте `http://PUBLIC_IP/`.
   `PUBLIC_IP` означає публічну IPv4-адресу створеного інстанса.
   Адреса й перші поля сторінки мають відповідати цьому інстансу.

На першому запуску cloud-init виконує user data від root.
На подальших запусках застосунок піднімає systemd. Зміна user data в консолі
сама по собі не повторює встановлення. Для відтворюваної демонстрації
зафіксуйте commit SHA у `GIT_REF`.

## Що показує застосунок

Сервер отримує токен через `PUT /latest/api/token`, а потім обходить
`/latest/meta-data/` і `/latest/dynamic/`. Каталоги розгортаються рекурсивно;
список відкритих SSH-ключів у формі `0=ім'я` обробляється окремо.
Звичайні багаторядкові значення, зокрема security groups, лишаються значеннями.

На сторінці є основні параметри інстанса, категорії полів, пошук за шляхом
і значенням, розгортання відповіді та збереження JSON. Знімок оновлюється
кожні 60 секунд; ручне оновлення дозволене не частіше ніж раз на 30 секунд.
Відвідувачі читають спільний знімок і не запускають окремий обхід IMDS.

Токен IMDSv2 не передається браузеру. Ветви `security-credentials`
і `user-data` позначаються як приховані без запиту їхнього вмісту.
Поля ключів доступу в JSON також фільтруються. Решта метаданих, зокрема
мережеві адреси, account ID та увімкнені теги, доступна відвідувачам сторінки.

Відсутні категорії залежать від конфігурації EC2. Помилки окремих полів
показуються біля їхніх шляхів. Обхід обмежений 30 секундами, 512 запитами
та глибиною 12; при досягненні ліміту сторінка позначає знімок як частковий.
Служба працює від окремого динамічного користувача. Право на порт 80
надається через `CAP_NET_BIND_SERVICE`.

## Локальний перегляд

Потрібен Python 3.9 або новіший. Зовнішніх Python-пакетів немає.

```bash
python3 app.py --demo
```

Відкрийте `http://127.0.0.1:8080/`. Сторінка позначає зразкові дані як
деморежим. Запуск без `--demo` використовує справжній IMDS і поза EC2
показує його недоступність.

## Діагностика в EC2

```bash
sudo cloud-init status --wait
sudo systemctl status ec2-metadata --no-pager
sudo journalctl -u ec2-metadata -n 50 --no-pager
sudo tail -n 80 /var/log/cloud-init-output.log
curl -fsS http://127.0.0.1/healthz
curl -fsS http://127.0.0.1/api/metadata
git -C /opt/ec2-metadata/repository rev-parse HEAD
```

`/healthz` перевіряє вебсервер і окремо повідомляє стан метаданих.
Стан `loading` означає початковий збір даних, `ready` — успішний обхід,
`partial` — частковий знімок, `unavailable` — відсутність доступних значень.

## Перевірки

```bash
python3 -m unittest -v test_app.py test_bootstrap.py
python3 check.py
bash -n user-data.sh
node --check static/app.js
```

`check.py` запускає тимчасовий локальний сервер у деморежимі, перевіряє
HTTP-відповіді й порівнює результат із [expected.txt](expected.txt).
Тести IMDS використовують локальний сервер, який вимагає токен.
Тест завантаження виконує Git clone і checkout у тимчасовому каталозі;
встановлення пакетів і systemd замінені тестовими командами.

Запуск на справжньому EC2 та встановлення пакетів в AMI ще не перевірено.

## Джерела

Документацію перевірено 04.10.2026.

- [Доступ до метаданих EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html).
- [Категорії метаданих](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html).
- [Запуск команд через user data](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html).

Після демонстрації завершіть створений для неї інстанс і перевірте,
чи не залишилися окремі диски та інші ресурси цього запуску.
