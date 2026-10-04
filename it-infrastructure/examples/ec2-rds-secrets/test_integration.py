"""Справжній PostgreSQL/TLS; лише AWS API замінено тестовою реалізацією."""
import json
import os
from pathlib import Path
import unittest
import app

ENABLED = all(os.environ.get(name) for name in ("TEST_DB_HOST", "TEST_DB_CA", "TEST_DB_PASSWORD"))


class FixtureAws:
    def __init__(self, password):
        self.password = password
        self.reads = 0
    def identity(self):
        return "arn:aws:sts::123456789012:assumed-role/test-role/test-instance"
    def read_secret(self, arn):
        self.reads += 1
        return {"SecretString": json.dumps({"username": "ec2_rds_app", "password": self.password})}


@unittest.skipUnless(ENABLED, "Потрібен окремий тестовий PostgreSQL з TLS.")
class PostgresIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import psycopg
        from psycopg import sql
        cls.password = os.environ["TEST_DB_PASSWORD"]
        cls.host = os.environ["TEST_DB_HOST"]
        cls.ca = os.environ["TEST_DB_CA"]
        cls.admin = psycopg.connect(
            host=cls.host, dbname="infrastructure", user="postgres",
            password=cls.password, sslmode="verify-full", sslrootcert=cls.ca, autocommit=True)
        # Той самий setup.sql, але інтерактивний пароль замінено параметризованим SQL.
        source = (Path(__file__).parent / "setup.sql").read_text()
        source = "\n".join(line for line in source.splitlines()
                           if not line.startswith("\\") and "\\gexec" not in line)
        cls.admin.execute(source)
        cls.admin.execute(sql.SQL("ALTER ROLE ec2_rds_app PASSWORD {}").format(sql.Literal(cls.password)))
        cls.admin.execute("GRANT CONNECT ON DATABASE infrastructure TO ec2_rds_app")

    @classmethod
    def tearDownClass(cls):
        cls.admin.close()

    def setUp(self):
        self.aws = FixtureAws(self.password)
        self.service = app.Diagnostics(app.Settings(
            "eu-central-1", "fixture", self.host, "infrastructure", self.ca), aws=self.aws)

    def test_read_only_sql_and_tls(self):
        result = self.service.snapshot()
        self.assertTrue(result["ok"], result)
        self.assertEqual(len(result["records"]), 2)
        self.assertTrue(result["database"]["ssl"])
        self.assertNotIn(self.password, json.dumps(result))
        with self.service.connect({"username": "ec2_rds_app", "password": self.password}) as connection:
            import psycopg
            with self.assertRaises(psycopg.Error):
                connection.execute("INSERT INTO demo.messages (message) VALUES ('forbidden')")

    def test_revoke_select_keeps_connection_working(self):
        self.admin.execute("REVOKE SELECT ON demo.messages FROM ec2_rds_app")
        try:
            result = self.service.snapshot()
            self.assertFalse(result["ok"])
            self.assertEqual(result["stages"][3]["status"], "ok")
            self.assertEqual(result["stages"][4]["status"], "error")
        finally:
            self.admin.execute("GRANT SELECT ON demo.messages TO ec2_rds_app")

    def test_secret_change_and_explicit_refresh(self):
        from psycopg import sql
        self.assertTrue(self.service.snapshot()["ok"])
        new_password = self.password + "_rotated"
        self.admin.execute(sql.SQL("ALTER ROLE ec2_rds_app PASSWORD {}").format(sql.Literal(new_password)))
        try:
            stale = self.service.snapshot()
            self.assertFalse(stale["ok"])
            self.assertEqual(stale["stages"][3]["status"], "error")
            self.aws.password = new_password
            refreshed = self.service.snapshot(refresh=True)
            self.assertTrue(refreshed["ok"], refreshed)
            self.assertNotIn(new_password, json.dumps(refreshed))
        finally:
            self.admin.execute(sql.SQL("ALTER ROLE ec2_rds_app PASSWORD {}").format(sql.Literal(self.password)))

    def test_certificate_hostname_mismatch_is_rejected(self):
        import socket
        wrong_host = socket.gethostbyname(self.host)
        self.service.settings = app.Settings("eu-central-1", "fixture", wrong_host, "infrastructure", self.ca)
        result = self.service.snapshot()
        self.assertFalse(result["ok"])
        self.assertEqual(result["stages"][2]["status"], "ok")
        self.assertEqual(result["stages"][3]["status"], "error")


if __name__ == "__main__":
    unittest.main(verbosity=2)
