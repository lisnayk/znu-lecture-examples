"""Git clone/checkout у тимчасовому каталозі; пакети й systemd імітовано."""
import os
import re
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent


class BootstrapTest(unittest.TestCase):
    def test_git_source_pinned_revision_repeat_and_dirty_protection(self):
        with tempfile.TemporaryDirectory(prefix="ec2-bootstrap-") as temporary:
            temp = Path(temporary)
            remote, base, commands = temp / "remote", temp / "installation", temp / "bin"
            remote.mkdir()
            commands.mkdir()
            app = remote / "example"
            app.mkdir()
            for name in ("app.py", "requirements.txt", "ec2-rds-secrets.service", ".gitignore", ".gitattributes"):
                shutil.copyfile(ROOT / name, app / name)
            shutil.copytree(ROOT / "static", app / "static")
            def git(*args):
                return subprocess.check_output(["git", "-C", str(remote), *args], text=True).strip()
            git("init", "-b", "main")
            git("add", ".")
            git("-c", "user.name=Demo Test", "-c", "user.email=demo@example.invalid",
                "-c", "core.hooksPath=/dev/null", "commit", "-m", "Fixture")
            commit = git("rev-parse", "HEAD")
            git("-c", "user.name=Demo Test", "-c", "user.email=demo@example.invalid",
                "-c", "core.hooksPath=/dev/null", "commit", "--allow-empty", "-m", "Later revision")
            for tool in ("apt-get",):
                target = commands / tool
                target.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
                target.chmod(0o755)
            python = commands / "python3"
            python.write_text(
                "#!/bin/sh\n"
                "if [ \"$1\" = -m ] && [ \"$2\" = venv ]; then\n"
                "  mkdir -p \"$3/bin\"\n"
                "  printf '#!/bin/sh\\nexit 0\\n' > \"$3/bin/python\"\n"
                "  chmod +x \"$3/bin/python\"\n"
                "  exit 0\n"
                "fi\n"
                "exec /usr/bin/python3 \"$@\"\n", encoding="utf-8")
            python.chmod(0o755)
            curl = commands / "curl"
            curl.write_text("#!/bin/sh\nwhile [ $# -gt 0 ]; do\n"
                            " if [ \"$1\" = -o ]; then shift; printf 'fixture CA\\n' > \"$1\"; exit 0; fi\n"
                            " shift\ndone\nexit 1\n", encoding="utf-8")
            curl.chmod(0o755)
            # Системний менеджер імітується. Запущений ним застосунок працює реально.
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
            systemctl = commands / "systemctl"
            systemctl.write_text(
                "#!/bin/sh\n"
                "if [ \"$1\" = restart ]; then\n"
                "  if [ -f \"$TEST_BASE/pid\" ]; then kill \"$(cat \"$TEST_BASE/pid\")\" 2>/dev/null || true; fi\n"
                "  python3 \"$TEST_BASE/current/app.py\" --demo --port \"$TEST_PORT\" >\"$TEST_BASE/server.log\" 2>&1 &\n"
                "  echo $! >\"$TEST_BASE/pid\"\n"
                "fi\n", encoding="utf-8")
            systemctl.chmod(0o755)
            url = "https://example.invalid/ec2-demo.git"
            script = (ROOT / "user-data.sh").read_text(encoding="utf-8")
            script = re.sub(r'^REPO_URL=.*$', 'REPO_URL="' + url + '"', script, flags=re.MULTILINE)
            script = script.replace('GIT_REF="main"', 'GIT_REF="' + commit + '"')
            script = script.replace('APP_SUBDIR="it-infrastructure/examples/ec2-rds-secrets"', 'APP_SUBDIR="example"')
            script = script.replace('BASE="/opt/ec2-rds-secrets"', 'BASE="' + str(base) + '"')
            script = script.replace("/etc/systemd/system/ec2-rds-secrets.service", str(temp / "installed.service"))
            script = script.replace("http://127.0.0.1/healthz", "http://127.0.0.1:" + str(port) + "/healthz")
            script = script.replace('DB_SECRET_ARN="REPLACE_WITH_FULL_SECRET_ARN"',
                                    'DB_SECRET_ARN="arn:aws:secretsmanager:eu-central-1:123456789012:secret:fixture-ABCDEF"')
            script = script.replace('DB_HOST="REPLACE_WITH_RDS_ENDPOINT"', 'DB_HOST="db.example"')
            script = script.replace('CONFIG="/etc/ec2-rds-secrets.env"', 'CONFIG="' + str(temp / "config.env") + '"')
            script = script.replace("source /etc/os-release", 'ID=ubuntu; VERSION_ID=24.04')
            bootstrap = temp / "user-data.sh"
            bootstrap.write_text(script, encoding="utf-8")
            env = {**os.environ, "PATH": str(commands) + ":" + os.environ["PATH"],
                   "TEST_BASE": str(base), "TEST_PORT": str(port),
                   "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "url.file://" + str(remote) + ".insteadOf",
                   "GIT_CONFIG_VALUE_0": url}
            try:
                for attempt in range(2):
                    result = subprocess.run(["bash", str(bootstrap)], env=env, text=True,
                                            capture_output=True, timeout=20)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    current = subprocess.check_output(["git", "-C", str(base / "repository"),
                                                       "rev-parse", "HEAD"], text=True).strip()
                    self.assertEqual(current, commit)
                    self.assertEqual((base / "current" / "app.py").read_bytes(), (ROOT / "app.py").read_bytes())
                    self.assertIn("Вебзастосунок відповідає", result.stdout)
                    self.assertEqual((temp / "installed.service").read_bytes(),
                                     (ROOT / "ec2-rds-secrets.service").read_bytes())
                changed = base / "current" / "app.py"
                changed.write_text(changed.read_text(encoding="utf-8") + "\n# Локальна зміна\n", encoding="utf-8")
                result = subprocess.run(["bash", str(bootstrap)], env=env, text=True,
                                        capture_output=True, timeout=20)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("# Локальна зміна", changed.read_text(encoding="utf-8"))
            finally:
                pid_file = base / "pid"
                if pid_file.exists():
                    try:
                        os.kill(int(pid_file.read_text()), 15)
                    except ProcessLookupError:
                        pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
