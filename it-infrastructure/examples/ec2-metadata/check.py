#!/usr/bin/env python3
"""Дим-тест локального деморежиму з перевіркою expected.txt."""
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib import error, request

ROOT = Path(__file__).resolve().parent

def check():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = subprocess.Popen([sys.executable, str(ROOT / "app.py"), "--demo", "--port", str(port)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = "http://127.0.0.1:" + str(port)
    output = []
    try:
        for attempt in range(100):
            try:
                with request.urlopen(base + "/api/metadata", timeout=2) as response:
                    data = json.load(response)
                if data["state"] == "ready":
                    break
            except (error.URLError, TimeoutError):
                pass
            time.sleep(0.05)
        else:
            raise AssertionError("Застосунок не підготував метадані.")
        for route in ("/", "/healthz", "/api/metadata"):
            with request.urlopen(base + route, timeout=2) as response:
                assert response.status == 200
                output.append("GET " + route + " — 200")
        assert data["demo"] is True
        output.append("Деморежим — позначено")
        paths = {item["path"]: item for item in data["records"]}
        assert paths["meta-data/public-keys/0/openssh-key"]["status"] == "ok"
        assert paths["dynamic/instance-identity/document"]["status"] == "ok"
        output.append("Вкладені метадані — отримано")
        for path in ("meta-data/iam/security-credentials/",
                     "meta-data/identity-credentials/ec2/security-credentials/", "user-data"):
            assert paths[path]["status"] == "hidden"
        output.append("Секретні гілки — не передано")
        actual = "\n".join(output) + "\n"
        expected = (ROOT / "expected.txt").read_text(encoding="utf-8")
        if actual != expected:
            raise AssertionError("Вивід не збігається з expected.txt.\n" + actual)
        print(actual, end="")
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()

if __name__ == "__main__":
    check()
