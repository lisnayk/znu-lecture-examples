"""Контракти AWS, кеш, відмови доступу та HTTP без зовнішніх ресурсів."""
from contextlib import nullcontext
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import io
import json
import threading
import unittest
from unittest.mock import Mock, patch
from contextlib import redirect_stderr
import app


class DbError(Exception):
    def __init__(self, code):
        self.sqlstate = code
        super().__init__("PRIVATE_EXCEPTION_DATA")


class FakeAws:
    def __init__(self):
        self.reads = 0
        self.password = "TEST_ONLY_" + "CREDENTIAL"
    def identity(self):
        return "arn:aws:sts::123456789012:assumed-role/ec2-rds-demo/i-example"
    def read_secret(self, arn):
        self.reads += 1
        return {"SecretString": json.dumps({"username": "ec2_rds_app", "password": self.password})}


class Connection:
    def __init__(self):
        self.closed = False
        self.query_error = None
    def execute(self, query):
        cursor = Mock()
        if "pg_stat_ssl" in query:
            cursor.fetchone.return_value = {"name": "infrastructure", "username": "ec2_rds_app",
                                          "ssl": True, "tls_version": "TLSv1.3"}
        else:
            if self.query_error:
                raise self.query_error
            cursor.fetchall.return_value = [{"id": 1, "message": "Навчальний рядок"}]
        return cursor
    def close(self):
        self.closed = True


class DiagnosticsTest(unittest.TestCase):
    def setUp(self):
        self.aws = FakeAws()
        self.now = 100
        self.db = Connection()
        self.connect = Mock(return_value=self.db)
        self.service = app.Diagnostics(
            app.Settings("eu-central-1", "secret-arn", "db.example", "infrastructure", "/tmp/ca.pem"),
            aws=self.aws, connector=self.connect, tcp=lambda *args, **kwargs: nullcontext(),
            clock=lambda: self.now)

    def test_success_uses_tls_and_does_not_return_secret(self):
        result = self.service.snapshot()
        self.assertTrue(result["ok"])
        self.assertNotIn(self.aws.password, json.dumps(result))
        self.assertNotIn("password", result)
        self.assertEqual(self.connect.call_args.kwargs["sslmode"], "verify-full")
        self.assertEqual(self.connect.call_args.kwargs["password"], self.aws.password)
        self.assertTrue(self.db.closed)

    def test_cache_expiry_and_explicit_refresh(self):
        self.service.snapshot()
        self.service.snapshot()
        self.assertEqual(self.aws.reads, 1)
        self.now += 61
        self.service.snapshot()
        self.assertEqual(self.aws.reads, 2)
        self.service.snapshot(refresh=True)
        self.assertEqual(self.aws.reads, 3)

    def test_rotation_reloads_once_on_password_rejection(self):
        self.connect.side_effect = [DbError("28P01"), self.db]
        result = self.service.snapshot()
        self.assertTrue(result["ok"])
        self.assertTrue(result["credential_reloaded"])
        self.assertEqual(self.aws.reads, 2)
        self.assertEqual(self.connect.call_count, 2)

    def test_password_rejection_does_not_retry_forever_or_leak(self):
        self.connect.side_effect = DbError("28P01")
        result = self.service.snapshot()
        self.assertFalse(result["ok"])
        self.assertEqual(self.connect.call_count, 2)
        self.assertEqual(result["stages"][3]["status"], "error")
        self.assertNotIn("PRIVATE_EXCEPTION_DATA", json.dumps(result))

    def test_secret_failure_stops_before_database(self):
        from botocore.exceptions import ClientError
        self.aws.read_secret = Mock(side_effect=ClientError(
            {"Error": {"Code": "AccessDeniedException", "Message": "PRIVATE_EXCEPTION_DATA"}}, "GetSecretValue"))
        result = self.service.snapshot()
        self.assertEqual(result["stages"][1]["status"], "error")
        self.assertEqual(result["stages"][2]["status"], "skipped")
        self.connect.assert_not_called()
        self.assertNotIn("PRIVATE_EXCEPTION_DATA", json.dumps(result))

    def test_invalid_secret_is_not_cached(self):
        self.aws.read_secret = Mock(return_value={"SecretString": '["PRIVATE_EXCEPTION_DATA"]'})
        result = self.service.snapshot()
        self.assertEqual(result["stages"][1]["status"], "error")
        self.assertIsNone(self.service.cached)

    def test_network_failure_is_separate_from_authentication(self):
        self.service.tcp = Mock(side_effect=TimeoutError)
        result = self.service.snapshot()
        self.assertEqual(result["stages"][2]["status"], "error")
        self.assertEqual(result["stages"][3]["status"], "skipped")
        self.connect.assert_not_called()

    def test_sql_denied_keeps_successful_connection_stage(self):
        self.db.query_error = DbError("42501")
        result = self.service.snapshot()
        self.assertEqual(result["stages"][3]["status"], "ok")
        self.assertEqual(result["stages"][4]["status"], "error")
        self.assertTrue(self.db.closed)

    def test_refresh_failure_discards_old_credentials(self):
        self.service.snapshot()
        self.aws.read_secret = Mock(side_effect=RuntimeError("PRIVATE_EXCEPTION_DATA"))
        result = self.service.snapshot(refresh=True)
        self.assertEqual(result["stages"][1]["status"], "error")
        self.assertIsNone(self.service.cached)


class AwsContractTest(unittest.TestCase):
    def test_sdk_request_is_scoped_to_current_secret(self):
        import boto3
        from botocore.stub import Stubber
        client = boto3.client("secretsmanager", region_name="eu-central-1",
                             aws_access_key_id="fixture", aws_secret_access_key="fixture")
        with Stubber(client) as stub:
            stub.add_response("get_secret_value", {"SecretString": '{"username":"u","password":"p"}'},
                              {"SecretId": "secret-arn", "VersionStage": "AWSCURRENT"})
            access = app.AwsAccess("eu-central-1")
            access.clients["secretsmanager"] = client
            self.assertIn("SecretString", access.read_secret("secret-arn"))
            stub.assert_no_pending_responses()

    def test_static_aws_keys_are_rejected(self):
        access = app.AwsAccess("eu-central-1")
        access.session = Mock()
        access.session.get_credentials.return_value.method = "env"
        access.clients["sts"] = Mock()
        with self.assertRaises(app.SafeError):
            access.identity()
        access.clients["sts"].get_caller_identity.assert_not_called()


class HttpTest(unittest.TestCase):
    def test_static_allowlist_refresh_origin_and_no_request_logging(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), app.handler_for(app.Demo()))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with redirect_stderr(io.StringIO()) as logs:
                connection = HTTPConnection("127.0.0.1", server.server_port)
                connection.request("GET", "/../app.py?PRIVATE_QUERY")
                response = connection.getresponse()
                self.assertEqual(response.status, 404)
                response.read()
                connection.request("POST", "/api/refresh")
                response = connection.getresponse()
                self.assertEqual(response.status, 403)
                response.read()
                connection.request("POST", "/api/refresh", headers={
                    "X-Demo-Request": "1", "Origin": "https://other.example"})
                response = connection.getresponse()
                self.assertEqual(response.status, 403)
                response.read()
                connection.request("POST", "/api/refresh", headers={"X-Demo-Request": "1"})
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                self.assertEqual(response.getheader("Cache-Control"), "no-store")
                self.assertTrue(json.loads(response.read())["ok"])
                connection.close()
                self.assertEqual(logs.getvalue(), "")
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main(verbosity=2)
