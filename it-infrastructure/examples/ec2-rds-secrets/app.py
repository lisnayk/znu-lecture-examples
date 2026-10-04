"""Діагностика EC2 → Secrets Manager → PostgreSQL. Секрети лише в пам'яті."""
import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import socket
import threading
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
TTL = 60


class SafeError(Exception):
    """Повідомлення, яке дозволено віддати браузеру."""


@dataclass(frozen=True)
class Settings:
    region: str
    secret_arn: str
    host: str
    database: str
    ca_file: str
    port: int = 5432

    @classmethod
    def from_env(cls):
        names = ("AWS_REGION", "DB_SECRET_ARN", "DB_HOST", "DB_NAME", "DB_SSLROOTCERT")
        values = [os.environ.get(name, "").strip() for name in names]
        if not all(values):
            raise SafeError("Заповніть AWS_REGION, DB_SECRET_ARN, DB_HOST, DB_NAME і DB_SSLROOTCERT.")
        try:
            port = int(os.environ.get("DB_PORT", "5432"))
        except ValueError:
            raise SafeError("DB_PORT має бути числом.") from None
        if not 1 <= port <= 65535 or not Path(values[4]).is_file():
            raise SafeError("Перевірте DB_PORT та шлях до сертифіката CA.")
        return cls(*values, port=port)


class AwsAccess:
    def __init__(self, region):
        self.region = region
        self.session = None
        self.clients = {}

    def client(self, name):
        import boto3
        from botocore.config import Config
        if self.session is None:
            self.session = boto3.Session(region_name=self.region)
        if name not in self.clients:
            self.clients[name] = self.session.client(
                name, config=Config(connect_timeout=3, read_timeout=3,
                                    retries={"total_max_attempts": 2, "mode": "standard"}))
        return self.clients[name]

    def identity(self):
        client = self.client("sts")
        credentials = self.session.get_credentials()
        if credentials is None or credentials.method != "iam-role":
            raise SafeError("Потрібна роль EC2 через instance profile. Приберіть статичні AWS credentials.")
        return client.get_caller_identity()["Arn"]

    def read_secret(self, arn):
        return self.client("secretsmanager").get_secret_value(
            SecretId=arn, VersionStage="AWSCURRENT")


def aws_hint(error):
    if isinstance(error, SafeError):
        return str(error)
    code = getattr(error, "response", {}).get("Error", {}).get("Code", "")
    return {
        "AccessDeniedException": "Роль не має доступу. Перевірте GetSecretValue та KMS key policy.",
        "AccessDenied": "Доступ заборонено. Перевірте IAM policy.",
        "ResourceNotFoundException": "Секрет не знайдено. Перевірте ARN і регіон.",
        "DecryptionFailure": "Не вдалося розшифрувати секрет. Перевірте KMS.",
    }.get(code, "Перевірте роль EC2, IMDSv2 та HTTPS-доступ до API AWS.")


def db_hint(error):
    return {
        "28P01": "База відхилила пароль. Перевірте користувача та ротацію секрета.",
        "28000": "База відхилила автентифікацію користувача.",
        "42501": "Бракує SQL-прав. Перевірте CONNECT, USAGE та SELECT.",
        "42P01": "Таблицю не знайдено. Виконайте setup.sql у цій базі.",
        "3D000": "Базу не знайдено. Перевірте DB_NAME.",
        "57014": "Запит перевищив дозволений час виконання.",
    }.get(getattr(error, "sqlstate", None),
          "Перевірте endpoint, сертифікат CA, TLS і доступність PostgreSQL.")


def connect_postgres(**kwargs):
    import psycopg
    from psycopg.rows import dict_row
    return psycopg.connect(**kwargs, row_factory=dict_row)


class Diagnostics:
    def __init__(self, settings, aws=None, connector=connect_postgres,
                 tcp=socket.create_connection, clock=time.monotonic):
        self.settings = settings
        self.aws = aws or AwsAccess(settings.region)
        self.connector, self.tcp, self.clock = connector, tcp, clock
        self.cached = None
        self.expires = 0
        self.lock = threading.Lock()

    def secret(self, force=False):
        if force or self.cached is None or self.clock() >= self.expires:
            self.cached = None
            result = self.aws.read_secret(self.settings.secret_arn)
            try:
                value = json.loads(result["SecretString"])
                if not isinstance(value, dict):
                    raise ValueError
                username, password = value["username"], value["password"]
                if not all(isinstance(item, str) and item for item in (username, password)):
                    raise ValueError
            except (KeyError, TypeError, ValueError):
                raise SafeError("Секрет має містити JSON із непорожніми username та password.") from None
            self.cached = {"username": username, "password": password}
            self.expires = self.clock() + TTL
            return self.cached, "AWS AWSCURRENT"
        return self.cached, "Кеш у пам'яті"

    def connect(self, credentials):
        config = self.settings
        return self.connector(
            host=config.host, port=config.port, dbname=config.database,
            user=credentials["username"], password=credentials["password"],
            sslmode="verify-full", sslrootcert=config.ca_file, connect_timeout=5,
            application_name="ec2-rds-secrets-demo", autocommit=True,
            options="-c statement_timeout=5000 -c default_transaction_read_only=on")

    def snapshot(self, refresh=False):
        with self.lock:
            stages = [{"id": key, "title": title, "status": "waiting", "detail": ""}
                      for key, title in (
                          ("identity", "Роль EC2"),
                          ("secret", "Secrets Manager"),
                          ("network", "TCP до RDS"),
                          ("database", "TLS та вхід у PostgreSQL"),
                          ("query", "Читання таблиці"))]
            result = {"mode": "aws", "checked_at": datetime.now(timezone.utc).isoformat(),
                      "stages": stages, "records": [], "database": None,
                      "cache_seconds": 0, "credential_reloaded": False, "ok": False}
            def passed(index, detail):
                stages[index].update(status="ok", detail=detail)
            def failed(index, detail):
                stages[index].update(status="error", detail=detail)
                for stage in stages[index + 1:]:
                    stage.update(status="skipped", detail="Попередній етап не пройдено.")
                return result
            try:
                passed(0, self.aws.identity())
            except Exception as error:
                return failed(0, aws_hint(error))
            try:
                credentials, source = self.secret(force=refresh)
                passed(1, source)
                result["cache_seconds"] = max(0, int(self.expires - self.clock()))
            except Exception as error:
                return failed(1, aws_hint(error))
            try:
                with self.tcp((self.settings.host, self.settings.port), timeout=3):
                    pass
                passed(2, "TCP-з'єднання встановлено. Це ще не підтверджує TLS або пароль.")
            except OSError:
                return failed(2, "Немає TCP-з'єднання. Перевірте DNS, маршрути, SG, NACL і порт.")
            connection = None
            try:
                try:
                    connection = self.connect(credentials)
                except Exception as error:
                    if getattr(error, "sqlstate", None) != "28P01":
                        raise
                    try:
                        credentials, source = self.secret(force=True)
                        passed(1, source)
                        result["credential_reloaded"] = True
                        result["cache_seconds"] = TTL
                    except Exception as refresh_error:
                        return failed(1, aws_hint(refresh_error))
                    connection = self.connect(credentials)
                info = connection.execute(
                    "SELECT current_database() AS name, current_user AS username, "
                    "ssl, version AS tls_version FROM pg_stat_ssl "
                    "WHERE pid = pg_backend_pid()").fetchone()
                if not info or not info["ssl"]:
                    raise SafeError("З'єднання не підтвердило використання TLS.")
                result["database"] = dict(info)
                passed(3, "verify-full: перевірено CA та ім'я сервера.")
            except Exception as error:
                if connection is not None:
                    connection.close()
                return failed(3, str(error) if isinstance(error, SafeError) else db_hint(error))
            try:
                rows = connection.execute(
                    "SELECT id, message FROM demo.messages ORDER BY id LIMIT 10").fetchall()
                result["records"] = [dict(row) for row in rows]
                passed(4, f"SELECT виконано. Отримано записів: {len(rows)}.")
                result["ok"] = True
            except Exception as error:
                return failed(4, db_hint(error))
            finally:
                connection.close()
            return result


class Demo:
    def snapshot(self, refresh=False):
        return {
            "mode": "demo", "checked_at": datetime.now(timezone.utc).isoformat(), "ok": True,
            "cache_seconds": TTL, "credential_reloaded": False,
            "database": {"name": "infrastructure", "username": "ec2_rds_app",
                         "ssl": True, "tls_version": "TLSv1.3"},
            "records": [{"id": 1, "message": "Навчальний запис. У деморежимі AWS і БД не викликаються."}],
            "stages": [{"id": key, "title": title, "status": "ok", "detail": detail}
                       for key, title, detail in (
                           ("identity", "Роль EC2", "Імітація ролі ec2-rds-demo"),
                           ("secret", "Secrets Manager", "Імітація AWSCURRENT"),
                           ("network", "TCP до RDS", "Імітація мережевого з'єднання"),
                           ("database", "TLS та вхід у PostgreSQL", "Імітація verify-full"),
                           ("query", "Читання таблиці", "Імітація SELECT"))]}


def handler_for(service):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def send(self, status, body, content_type):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy",
                             "default-src 'self'; frame-ancestors 'none'; base-uri 'none'; object-src 'none'")
            self.end_headers()
            self.wfile.write(body)

        def json(self, status, value):
            self.send(status, json.dumps(value, ensure_ascii=False).encode(), "application/json; charset=utf-8")

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/healthz":
                return self.json(200, {"status": "ok"})
            if path == "/api/status":
                return self.json(200, service.snapshot())
            assets = {"/": "index.html", "/app.js": "app.js", "/style.css": "style.css"}
            if path not in assets:
                return self.json(404, {"error": "Не знайдено."})
            kind = {"/": "text/html", "/app.js": "text/javascript", "/style.css": "text/css"}[path]
            self.send(200, (ROOT / "static" / assets[path]).read_bytes(), kind + "; charset=utf-8")

        def do_POST(self):
            if self.path != "/api/refresh":
                return self.json(404, {"error": "Не знайдено."})
            origin = self.headers.get("Origin")
            if (self.headers.get("X-Demo-Request") != "1"
                    or (origin and urlsplit(origin).netloc != self.headers.get("Host"))):
                return self.json(403, {"error": "Запит має надходити зі сторінки демо."})
            if self.headers.get("Transfer-Encoding") or self.headers.get("Content-Length", "0") != "0":
                return self.json(400, {"error": "Тіло запиту не очікується."})
            self.json(200, service.snapshot(refresh=True))
    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    try:
        service = Demo() if args.demo else Diagnostics(Settings.from_env())
    except SafeError as error:
        parser.error(str(error))
    server = ThreadingHTTPServer((args.host, args.port), handler_for(service))
    print(f"EC2 → RDS: http://{args.host}:{server.server_port}; mode={'demo' if args.demo else 'aws'}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
