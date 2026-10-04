#!/usr/bin/env python3
"""Демонстрація EC2 Instance Metadata Service без зовнішніх залежностей."""
import argparse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import time
from urllib import error, parse, request

ROOT = Path(__file__).resolve().parent
IMDS = "http://169.254.169.254"
TOKEN_TTL = 21600
REFRESH_SECONDS = 60
MAX_REQUESTS = 512
MAX_SECONDS = 30
MAX_BYTES = 131072
HIDDEN = "Значення не запитується й не передається браузеру."


class MetadataError(Exception):
    pass


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class IMDSClient:
    def __init__(self, endpoint=IMDS):
        self.endpoint = endpoint.rstrip("/")
        self.opener = request.build_opener(request.ProxyHandler({}), NoRedirect())
        self.token = None
        self.expires = 0

    def send(self, path, method="GET", headers=None, timeout=2):
        req = request.Request(self.endpoint + path, method=method, headers=headers or {})
        with self.opener.open(req, timeout=timeout) as response:
            data = response.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                raise MetadataError("Відповідь перевищує 128 КіБ.")
            return data.decode("utf-8", errors="replace")

    def new_token(self, timeout):
        self.token = self.send("/latest/api/token", method="PUT", headers={
            "X-aws-ec2-metadata-token-ttl-seconds": str(TOKEN_TTL)
        }, timeout=timeout)
        if not self.token or "\n" in self.token or "\r" in self.token:
            raise MetadataError("IMDSv2 повернув некоректний токен.")
        self.expires = time.monotonic() + TOKEN_TTL - 60

    def read(self, path, timeout=2):
        try:
            if self.token is None or time.monotonic() >= self.expires:
                self.new_token(timeout)
            for attempt in range(2):
                try:
                    return self.send("/latest/" + path, headers={
                        "X-aws-ec2-metadata-token": self.token
                    }, timeout=timeout)
                except error.HTTPError as exc:
                    if exc.code == 401 and attempt == 0:
                        self.new_token(timeout)
                        continue
                    raise
        except error.HTTPError as exc:
            raise MetadataError("IMDS HTTP " + str(exc.code)) from None
        except (error.URLError, TimeoutError, OSError, ValueError):
            raise MetadataError("IMDS недоступний. Перевірте середовище EC2 та параметри IMDS.") from None


class DemoClient:
    def __init__(self):
        self.data = json.loads((ROOT / "demo-data.json").read_text(encoding="utf-8"))

    def read(self, path, timeout=2):
        if path not in self.data:
            raise MetadataError("IMDS HTTP 404")
        return self.data[path]


def hidden(path):
    return path == "user-data" or "security-credentials" in path.split("/")


def sanitize(value):
    """Додаткова фільтрація ключів секретів у JSON-відповідях."""
    secret_keys = {"accesskeyid", "secretaccesskey", "token", "password", "secret"}
    if isinstance(value, dict):
        return {key: "[приховано]" if key.lower().replace("_", "") in secret_keys
                else sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    return value


def collect(client, demo=False):
    started = time.monotonic()
    records, seen = [], set()
    count = 0
    truncated = False

    def visit(path, depth=0):
        nonlocal count, truncated
        if path in seen:
            return
        seen.add(path)
        if hidden(path):
            records.append({"path": path, "status": "hidden", "value": HIDDEN})
            return
        remaining = MAX_SECONDS - (time.monotonic() - started)
        if count >= MAX_REQUESTS or remaining <= 0 or depth > 12:
            truncated = True
            return
        count += 1
        try:
            value = client.read(path, timeout=min(2, max(0.05, remaining / 4)))
        except MetadataError as exc:
            records.append({"path": path, "status": "error", "value": str(exc)})
            return
        if path.endswith("/"):
            records.append({"path": path, "status": "directory", "value": value})
            for line in value.splitlines():
                child = line.strip()
                if not child:
                    continue
                if path == "meta-data/public-keys/" and "=" in child:
                    child = child.split("=", 1)[0] + "/"
                directory = child.endswith("/")
                segment = child.rstrip("/")
                if "/" in segment or segment in {".", ".."}:
                    records.append({"path": path + child, "status": "error",
                                    "value": "Некоректний елемент каталогу."})
                    continue
                visit(path + parse.quote(segment, safe=":") + ("/" if directory else ""), depth + 1)
        else:
            try:
                value = json.dumps(sanitize(json.loads(value)), ensure_ascii=False, indent=2)
            except (json.JSONDecodeError, TypeError):
                pass
            records.append({"path": path, "status": "ok", "value": value})

    for category in ("meta-data/", "dynamic/", "user-data"):
        visit(category)
    succeeded = any(record["status"] == "ok" for record in records)
    errors = any(record["status"] == "error" for record in records)
    state = "unavailable" if not succeeded else "partial" if errors or truncated else "ready"
    return {
        "state": state, "demo": demo,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_ms": round((time.monotonic() - started) * 1000),
        "requests": count, "truncated": truncated,
        "records": records,
    }


class Snapshot:
    def __init__(self, client, demo=False):
        self.client, self.demo = client, demo
        self.lock, self.wake = threading.Lock(), threading.Event()
        self.data = {"state": "loading", "demo": demo, "records": [], "updated_at": None}
        self.last_start = 0
        self.refreshing = False

    def get(self):
        with self.lock:
            return {**self.data, "refreshing": self.refreshing}

    def refresh(self):
        with self.lock:
            if self.refreshing or time.monotonic() - self.last_start < 30:
                return False
            self.wake.set()
            return True

    def run(self):
        while True:
            self.wake.clear()
            with self.lock:
                self.refreshing = True
                self.last_start = time.monotonic()
            try:
                result = collect(self.client, self.demo)
            except Exception:
                # Журнал не містить токена чи сирих відповідей IMDS.
                result = {"state": "unavailable", "demo": self.demo, "records": [],
                          "updated_at": datetime.now(timezone.utc).isoformat()}
            with self.lock:
                self.data, self.refreshing = result, False
            self.wake.wait(REFRESH_SECONDS)


def make_handler(snapshot):
    class Handler(BaseHTTPRequestHandler):
        def reply(self, status, body, content_type):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy",
                             "default-src 'self'; script-src 'self'; style-src 'self'; "
                             "connect-src 'self'; img-src 'self'; object-src 'none'; "
                             "base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def json_reply(self, status, data):
            self.reply(status, json.dumps(data, ensure_ascii=False).encode("utf-8"),
                       "application/json; charset=utf-8")

        def do_GET(self):
            route = parse.urlsplit(self.path).path
            if route == "/healthz":
                self.json_reply(200, {"status": "ok", "metadata": snapshot.get()["state"]})
            elif route == "/api/metadata":
                data = snapshot.get()
                self.json_reply(202 if data["state"] == "loading" else 200, data)
            elif route in {"/", "/app.js", "/style.css"}:
                name = {"/": "index.html", "/app.js": "app.js", "/style.css": "style.css"}[route]
                mime = {"/": "text/html", "/app.js": "text/javascript",
                        "/style.css": "text/css"}[route]
                self.reply(200, (ROOT / "static" / name).read_bytes(), mime + "; charset=utf-8")
            else:
                self.json_reply(404, {"error": "Ресурс не знайдено."})

        def do_POST(self):
            if self.path == "/api/refresh":
                accepted = snapshot.refresh()
                self.json_reply(202 if accepted else 429, {"accepted": accepted})
            else:
                self.json_reply(404, {"error": "Ресурс не знайдено."})
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--demo", action="store_true", help="Зразкові дані замість EC2 IMDS.")
    args = parser.parse_args()
    snapshot = Snapshot(DemoClient() if args.demo else IMDSClient(), demo=args.demo)
    threading.Thread(target=snapshot.run, daemon=True).start()
    server = ThreadingHTTPServer((args.host, args.port), make_handler(snapshot))
    print("EC2 Metadata Explorer: http://" + args.host + ":" + str(args.port), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
