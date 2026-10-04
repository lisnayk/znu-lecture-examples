"""Перевірка протоколу IMDSv2, обходу дерева та вебзастосунку."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import unittest
from urllib import error, request

from app import collect, DemoClient, IMDSClient, make_handler, MetadataError, Snapshot

ROOT = Path(__file__).resolve().parent


class IMDSTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calls = []
        cls.tokens = 0
        cls.expire_once = False
        cls.data = json.loads((ROOT / "demo-data.json").read_text(encoding="utf-8"))
        class Mock(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def do_PUT(self):
                cls.calls.append(("PUT", self.path))
                if self.path != "/latest/api/token" or self.headers.get("X-aws-ec2-metadata-token-ttl-seconds") != "21600":
                    self.send_error(400)
                    return
                cls.tokens += 1
                self.send_response(200)
                self.end_headers()
                self.wfile.write(("test-token-" + str(cls.tokens)).encode())
            def do_GET(self):
                cls.calls.append(("GET", self.path))
                if cls.expire_once:
                    cls.expire_once = False
                    self.send_error(401)
                    return
                if self.headers.get("X-aws-ec2-metadata-token") != "test-token-" + str(cls.tokens):
                    self.send_error(401)
                    return
                if self.path == "/latest/meta-data/redirect":
                    self.send_response(302)
                    self.send_header("Location", "/should-never-be-read")
                    self.end_headers()
                    return
                value = cls.data.get(self.path.removeprefix("/latest/"))
                if value is None:
                    self.send_error(404)
                    return
                self.send_response(200)
                self.end_headers()
                self.wfile.write(value.encode("utf-8"))
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Mock)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.endpoint = "http://127.0.0.1:" + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        type(self).calls.clear()

    def test_recursive_collection_with_token_and_secret_exclusion(self):
        data = collect(IMDSClient(self.endpoint))
        self.assertEqual(data["state"], "ready")
        records = {item["path"]: item for item in data["records"]}
        self.assertEqual(records["meta-data/public-keys/0/openssh-key"]["status"], "ok")
        self.assertIn("10.0.1.25", records["meta-data/network/interfaces/macs/02:ab:cd:ef:01:24/local-ipv4s"]["value"])
        self.assertEqual(records["meta-data/security-groups"]["value"], "ec2-metadata-demo\nssh-from-teacher")
        self.assertEqual(records["user-data"]["status"], "hidden")
        self.assertEqual(records["meta-data/iam/security-credentials/"]["status"], "hidden")
        self.assertEqual(records["meta-data/identity-credentials/ec2/security-credentials/"]["status"], "hidden")
        self.assertFalse(any("security-credentials" in path or "user-data" in path for method, path in self.calls))
        self.assertEqual(sum(method == "PUT" for method, path in self.calls), 1)
        self.assertNotIn("test-token-", json.dumps(data))

    def test_expired_token_is_renewed(self):
        type(self).expire_once = True
        client = IMDSClient(self.endpoint)
        self.assertEqual(client.read("meta-data/instance-id"), "i-0123456789example")
        self.assertEqual(sum(method == "PUT" for method, path in self.calls), 2)

    def test_redirect_is_not_followed(self):
        with self.assertRaisesRegex(MetadataError, "302"):
            IMDSClient(self.endpoint).read("meta-data/redirect")
        self.assertFalse(any(path == "/should-never-be-read" for method, path in self.calls))

    def test_unavailable_metadata_has_explicit_state(self):
        class Unavailable:
            def read(self, path, timeout=2):
                raise MetadataError("IMDS HTTP 403")
        data = collect(Unavailable())
        self.assertEqual(data["state"], "unavailable")
        self.assertEqual(sum(item["status"] == "error" for item in data["records"]), 2)

    def test_partial_tree_preserves_good_values(self):
        class Partial(DemoClient):
            def read(self, path, timeout=2):
                if path == "meta-data/public-ipv4":
                    raise MetadataError("IMDS HTTP 404")
                return super().read(path, timeout)
        data = collect(Partial(), demo=True)
        self.assertEqual(data["state"], "partial")
        self.assertTrue(any(item["path"] == "meta-data/instance-id" and item["status"] == "ok" for item in data["records"]))

    def test_json_secret_fields_are_filtered(self):
        class Extra(DemoClient):
            def read(self, path, timeout=2):
                if path == "dynamic/instance-identity/document":
                    return '{"nested":{"SecretAccessKey":"TEST_SECRET","Token":"TEST_TOKEN"},"region":"eu-central-1"}'
                return super().read(path, timeout)
        data = collect(Extra())
        self.assertNotIn("TEST_SECRET", json.dumps(data))
        self.assertNotIn("TEST_TOKEN", json.dumps(data))


class WebTest(unittest.TestCase):
    def setUp(self):
        self.snapshot = Snapshot(DemoClient(), demo=True)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.snapshot))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.endpoint = "http://127.0.0.1:" + str(self.server.server_port)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def test_loading_ready_static_and_health_routes(self):
        with request.urlopen(self.endpoint + "/api/metadata") as response:
            self.assertEqual(response.status, 202)
        self.snapshot.data = collect(DemoClient(), demo=True)
        with request.urlopen(self.endpoint + "/api/metadata") as response:
            data = json.load(response)
        self.assertEqual(data["state"], "ready")
        self.assertTrue(data["demo"])
        for route in ("/", "/app.js", "/style.css", "/healthz"):
            with request.urlopen(self.endpoint + route) as response:
                self.assertEqual(response.status, 200)
                self.assertIn("no-store", response.headers["Cache-Control"])
                self.assertIn("default-src 'self'", response.headers["Content-Security-Policy"])
        with self.assertRaises(error.HTTPError) as exc:
            request.urlopen(self.endpoint + "/../app.py")
        self.assertEqual(exc.exception.code, 404)

    def test_refresh_is_throttled(self):
        import time
        self.snapshot.last_start = time.monotonic()
        with self.assertRaises(error.HTTPError) as exc:
            request.urlopen(request.Request(self.endpoint + "/api/refresh", method="POST"))
        self.assertEqual(exc.exception.code, 429)
        self.snapshot.last_start = 0
        with request.urlopen(request.Request(self.endpoint + "/api/refresh", method="POST")) as response:
            self.assertEqual(response.status, 202)


if __name__ == "__main__":
    unittest.main(verbosity=2)
