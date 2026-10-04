"""Дим-тест без AWS та зовнішньої БД."""
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
process = subprocess.Popen([sys.executable, str(ROOT / "app.py"), "--demo", "--port", str(port)],
                           stdout=subprocess.DEVNULL)
base = f"http://127.0.0.1:{port}"
try:
    for attempt in range(50):
        try:
            with urlopen(base + "/healthz", timeout=1) as response:
                assert json.load(response)["status"] == "ok"
            break
        except OSError:
            time.sleep(.05)
    else:
        raise AssertionError("Сервер не запустився.")
    for request in (base + "/api/status",
                    Request(base + "/api/refresh", method="POST", headers={"X-Demo-Request": "1"})):
        with urlopen(request, timeout=2) as response:
            value = json.load(response)
        assert value["mode"] == "demo" and value["ok"]
        assert len(value["stages"]) == 5 and value["records"]
    print("HTTP: OK")
    print("DEMO: 5 stages, SQL fixture")
    print("REFRESH: OK")
finally:
    process.terminate()
    process.wait(timeout=5)
