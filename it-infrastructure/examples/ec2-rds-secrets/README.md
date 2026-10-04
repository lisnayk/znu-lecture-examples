# EC2 → Secrets Manager → RDS PostgreSQL

Застосунок показує п'ять етапів доступу до бази. AWS SDK отримує тимчасові
credentials ролі EC2, читає пароль із Secrets Manager і передає його драйверу
PostgreSQL. Вебсторінка показує роль, стан перевірок і до десяти рядків
навчальної таблиці. Пароль, значення секрета та AWS credentials не потрапляють
до HTTP-відповідей або журналу застосунку.

Приклад призначено для окремого навчального EC2 з Ubuntu 24.04 LTS і RDS
PostgreSQL. Тут використовується парольна автентифікація PostgreSQL.
IAM-роль дає доступ до секрета; SQL-права користувача дають доступ до таблиці.
IAM database authentication у цьому прикладі не вмикають.

## Локальний перегляд

~~~bash
python3 app.py --demo --port 8766
~~~

Відкрити http://localhost:8766. Деморежим не потребує бібліотек, AWS або БД.
На сторінці явно позначено, що результати імітуються.

## 1. Мережа

Створити RDS PostgreSQL у тій самій VPC, що й EC2. Для RDS установити
Public access = No та Initial database name = infrastructure.
DB subnet group має містити підмережі щонайменше у двох зонах доступності;
для базового прикладу достатньо Single-AZ.

Використати окремі security groups.

| Група | Правило |
|---|---|
| EC2 application | Вхідний TCP 80 лише з IP викладача або навчальної мережі |
| RDS database | Вхідний TCP 5432 із security group EC2 application |
| EC2 application | Вихідний доступ до RDS 5432 та HTTPS 443 для зовнішніх API і завантажень |

Якщо вихідний трафік обмежено, також забезпечити DNS-резолюцію та маршрути.
SQL-порт не відкривають для 0.0.0.0/0. Роль IAM не замінює мережеве правило.
[Сценарії доступу до RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.Scenarios.html).

Для початкового запуску EC2 у публічній підмережі потрібні публічна IPv4-адреса
і маршрут через Internet Gateway. RDS залишається приватною.
Bootstrap завантажує код із GitHub, пакети Ubuntu, бібліотеки PyPI та CA AWS.

Для роботи у приватній підмережі API Secrets Manager можна зробити доступним
через interface VPC endpoint com.amazonaws.REGION.secretsmanager.
Цей застосунок також викликає регіональний STS GetCallerIdentity для діагностики
ролі; потрібен доступ до STS через endpoint або NAT.
Група endpoint дозволяє HTTPS 443 від групи EC2, private DNS увімкнено.
Служба задає AWS_STS_REGIONAL_ENDPOINTS=regional.
[Регіональний endpoint STS](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_sts_vpc_endpoint_create.html).
Сам endpoint Secrets Manager не забезпечує завантаження GitHub, PyPI та Ubuntu;
для bootstrap потрібен вихідний доступ або заздалегідь підготовлений образ.
[VPC endpoint Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/vpc-endpoint-overview.html).

## 2. Таблиця та користувач застосунку

Підключитися до infrastructure від адміністратора через psql із вузла,
якому дозволено доступ до RDS. Пароль адміністратора вводиться на запит.
Адміністративним вузлом може бути EC2 у цій VPC з дозволеною для RDS
security group. Якщо в Ubuntu немає psql, установити клієнт і завантажити
код прикладу.

~~~bash
sudo apt-get update
sudo apt-get install -y postgresql-client curl git
git clone https://github.com/lisnayk/znu-lecture-examples.git
cd znu-lecture-examples/it-infrastructure/examples/ec2-rds-secrets
curl --fail --show-error https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -o global-bundle.pem
~~~

Адміністративному вузлу потрібен вихідний HTTPS-доступ для цих завантажень.

~~~bash
psql "host=RDS_ENDPOINT port=5432 dbname=infrastructure user=ADMIN_USER sslmode=verify-full sslrootcert=global-bundle.pem" -W -f setup.sql
~~~

Замість RDS_ENDPOINT і ADMIN_USER підставити endpoint та адміністративного
користувача. setup.sql виконують один раз у новій навчальній базі.
Сценарій створює ec2_rds_app, просить задати його пароль командою psql
\password, створює demo.messages і два записи. Користувач отримує CONNECT,
USAGE на схемі та SELECT на таблиці. Адміністративний користувач використовується
лише для підготовки; застосунок працює як ec2_rds_app.

Клієнт завжди використовує sslmode=verify-full. Перевіряються ланцюжок
сертифіката й ім'я сервера, тому DB_HOST має бути endpoint RDS.
[TLS для RDS PostgreSQL](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/PostgreSQL.Concepts.General.SSL.html).

## 3. Секрет

У Secrets Manager створити секрет типу Other type of secret.
Додати два рядкові поля.

| Поле | Значення |
|---|---|
| username | ec2_rds_app |
| password | Пароль, заданий через setup.sql |

Вибрати той самий регіон, наприклад eu-central-1, ім'я
it-infrastructure/rds-demo і для базового прикладу ключ aws/secretsmanager.
Скопіювати повний ARN секрета разом із випадковим суфіксом.

Застосунок читає лише username і password. Endpoint і назва бази надходять
із конфігурації EC2. Додаткові поля секрета не змінюють адресу підключення.
Читання виконується з VersionStage=AWSCURRENT.
[Отримання секрета через Python SDK](https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets-python-sdk.html).

## 4. Роль EC2

В IAM створити роль для сервісу EC2. iam-trust-policy.json показує trust policy,
яка дозволяє EC2 використовувати роль.

У iam-policy.json замінити REPLACE_WITH_FULL_SECRET_ARN повним ARN створеного
секрета. Додати цю policy до ролі. Вона дозволяє лише GetSecretValue для одного
секрета. Призначити роль інстансу через IAM instance profile під час створення
EC2 або через Actions → Security → Modify IAM role.

Якщо секрет зашифровано власним KMS-ключем, додати до policy окремий дозвіл.

~~~json
{
  "Effect": "Allow",
  "Action": "kms:Decrypt",
  "Resource": "REPLACE_WITH_KMS_KEY_ARN"
}
~~~

Key policy KMS також має дозволяти цьому principal дешифрування.
Для aws/secretsmanager окремий kms:Decrypt у базовій policy не потрібний.
[Права на читання секрета](https://docs.aws.amazon.com/secretsmanager/latest/userguide/auth-and-access_iam-policies.html).

Для EC2 установити IMDSv2 Required та залишити metadata endpoint увімкненим.
Boto3 сам отримує й оновлює credentials instance profile.
Застосунок перевіряє credential provider iam-role; статичні AWS keys і профіль
користувача для цього демо відхиляються.
[Ролі EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html).

## 5. Запуск із Git

У user-data.sh заповнити AWS_REGION, DB_SECRET_ARN, DB_HOST і за потреби DB_NAME.
У скрипті вже вказано публічний репозиторій та шлях застосунку.
GIT_REF можна замінити повним SHA коміту для відтворюваного запуску.

Створити EC2 з Ubuntu 24.04 LTS, підготовленою роллю та security group.
Передати скрипт як user data. Він завантажує код із Git, встановлює бібліотеки
в окреме venv, завантажує CA bundle та запускає службу ec2-rds-secrets на порту 80.
Конфігурація зберігається в /etc/ec2-rds-secrets.env; у ній немає пароля або
AWS keys. Приклад заповнення міститься в config.env.example.

Порт 80 має бути вільним. Якщо на інстансі вже працює інший вебсервіс,
для цього демо використати окремий інстанс.

~~~bash
sudo systemctl status ec2-rds-secrets --no-pager
sudo journalctl -u ec2-rds-secrets --no-pager -n 50
sudo tail -n 50 /var/log/cloud-init-output.log
~~~

Відкрити http://EC2_PUBLIC_IP. /healthz перевіряє лише HTTP-службу.
Кнопка «Перевірити зв'язок» перевіряє роль, секрет, TCP, TLS/вхід і SELECT.

## 6. Кеш і зміна пароля

Значення секрета кешується в пам'яті процесу на 60 секунд.
«Перечитати секрет» примусово запитує AWSCURRENT. Якщо отримання нового секрета
не вдалося, старе значення вилучається з кешу.

Кожна перевірка відкриває нове з'єднання, виконує два короткі SELECT і закриває
його. При SQLSTATE 28P01 застосунок один раз перечитує секрет і повторює
підключення. Помилки клієнтської бібліотеки не завжди містять цей SQLSTATE,
тому TTL і явне перечитування залишаються основним механізмом оновлення.

Для демонстрації вручну змінити пароль ec2_rds_app через \password, потім
оновити password у Secrets Manager. Натиснути «Перечитати секрет».
Зміна лише значення секрета не змінює пароль у PostgreSQL.

Це ручна зміна пароля. Автоматична ротація потребує окремого налаштування
Secrets Manager, доступу функції ротації до БД та відповідної структури
секрета. Bootstrap автоматичну ротацію не створює.
[Ротація через Lambda](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html).

## 7. Досліди з відмовами

| Дія | Очікуваний результат |
|---|---|
| Прибрати IAM policy читання секрету й натиснути «Перечитати секрет» після поширення зміни IAM | Помилка на етапі Secrets Manager |
| Прибрати правило 5432 у SG RDS і повторити перевірку | Помилка TCP; перевірка відкриває нове з'єднання |
| Виконати REVOKE SELECT ON demo.messages FROM ec2_rds_app | TLS і вхід проходять, читання таблиці відхиляється |
| Повернути GRANT SELECT ON demo.messages TO ec2_rds_app | Записи знову доступні |
| Змінити пароль лише в БД | Роль і секрет доступні, PostgreSQL відхиляє пароль |
| Узгодити пароль у БД та секреті, перечитати секрет | Усі етапи проходять |

TCP-перевірка сама по собі не доводить правильність пароля.
Успішний вхід не доводить права SELECT. Успішне читання з кешу не доводить,
що роль досі має GetSecretValue; для такого досліду потрібне перечитування.

## Перевірка коду

~~~bash
python3 check.py
~~~

Вивід має збігтися з expected.txt. Для тестів установити залежності у venv.

~~~bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python3 -m unittest -v test_app test_bootstrap
~~~

test_integration.py перевіряє справжній PostgreSQL через TLS у тестовому
оточенні з TEST_DB_HOST, TEST_DB_CA та TEST_DB_PASSWORD. AWS API у цих тестах
імітуються. Без цих змінних інтеграційні тести пропускаються.
Локальні тести не підтверджують налаштування VPC, instance profile або RDS.

## Завершення

Видалити навчальні EC2, RDS і секрет; також видалити створені спеціально для
демо endpoints, snapshots, role та policies, якщо вони більше не потрібні.
Для RDS окремо перевірити збережені snapshots і automated backups.
Видалення instance не гарантує видалення всіх платних ресурсів.
RDS, EC2, Secrets Manager, endpoints і NAT можуть оплачуватися окремо.

Документацію AWS перевірено 04.10.2026. Запуск на справжніх EC2 і RDS
потребує перевірки в навчальному AWS-акаунті.
