"""Перевірка образу багатоетапної збірки; URL передається аргументом."""
import subprocess
import sys
import urllib.error
import urllib.request

base = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080").rstrip("/")
image = sys.argv[2] if len(sys.argv) > 2 else "multistage:1.0"


def fetch(route):
    try:
        return urllib.request.urlopen(base + route, timeout=5)
    except urllib.error.HTTPError as error:
        return error


with fetch("/") as response:
    body = response.read().decode("utf-8")
    assert response.status == 200, response.status
    assert "Багатоетапна збірка" in body, body[:200]
    print("PASS 200 /")

with fetch("/missing.html") as response:
    assert response.status == 404, response.status
    print("PASS 404 /missing.html")

# У фінальному образі не повинно лишитися ані Node.js, ані вихідного коду.
node = subprocess.run(["docker", "run", "--rm", "--entrypoint", "node", image, "--version"],
                      capture_output=True, text=True)
assert node.returncode != 0, node.stdout
print("PASS у фінальному образі немає Node.js")

src = subprocess.run(["docker", "run", "--rm", "--entrypoint", "ls", image, "/app"],
                     capture_output=True, text=True)
assert src.returncode != 0, src.stdout
print("PASS у фінальному образі немає каталогу /app")
