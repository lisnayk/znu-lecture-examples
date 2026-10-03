"""Перевірка образу, зібраного з Dockerfile; URL передається аргументом."""
import json
import subprocess
import sys
import urllib.error
import urllib.request

base = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:3000").rstrip("/")
container = sys.argv[2] if len(sys.argv) > 2 else "lecture3-hello"


def fetch(route):
    try:
        return urllib.request.urlopen(base + route, timeout=5)
    except urllib.error.HTTPError as error:
        return error


def docker(*args):
    return subprocess.run(["docker", *args], capture_output=True, text=True).stdout.strip()


with fetch("/") as response:
    body = response.read().decode("utf-8")
    assert response.status == 200, response.status
    assert "Образ зібрано з Dockerfile" in body, body[:200]
    print("PASS 200 /")

with fetch("/healthz") as response:
    assert response.status == 200, response.status
    assert json.load(response) == {"status": "ok"}
    print("PASS 200 /healthz")

with fetch("/missing") as response:
    assert response.status == 404, response.status
    print("PASS 404 /missing")

user = docker("exec", container, "id", "-un")
assert user == "node", user
print("PASS процес працює від node, а не від root")

# Стан залежить від моменту запуску, тому рядок виводу однаковий для обох
# допустимих значень: інакше він не збігався б з expected.txt.
health = docker("inspect", "--format", "{{.State.Health.Status}}", container)
assert health in ("healthy", "starting"), health
print("PASS HEALTHCHECK працює (healthy або starting)")
