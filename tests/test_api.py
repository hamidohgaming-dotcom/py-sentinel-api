import unittest
import threading
import json
import urllib.request
from sentinel.store import MonitorStore
from sentinel.server import create_server


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = MonitorStore()
        # Bind to port 0 to get an OS-assigned ephemeral free port
        cls.server = create_server(host="127.0.0.1", port=0, store=cls.store)
        cls.port = cls.server.server_port
        cls.base_url = f"http://127.0.0.1:{cls.port}"

        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _request(self, method: str, path: str, data: dict = None):
        url = f"{self.base_url}{path}"
        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read().decode("utf-8")
                return resp.status, json.loads(raw)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            return exc.code, json.loads(raw)

    def test_health_endpoint(self):
        status, body = self._request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "healthy")
        self.assertEqual(body["service"], "py-sentinel-api")

    def test_metrics_endpoint(self):
        status, body = self._request("GET", "/api/v1/metrics")
        self.assertEqual(status, 200)
        self.assertTrue(body["success"])
        self.assertIn("platform", body["data"])

    def test_monitors_crud_flow(self):
        # Create
        status, body = self._request("POST", "/api/v1/monitors", {
            "name": "Integration Test Target",
            "url": "https://httpbin.org/status/200",
            "expected_status": 200
        })
        self.assertEqual(status, 201)
        m_id = body["data"]["id"]

        # Retrieve
        status, body = self._request("GET", f"/api/v1/monitors/{m_id}")
        self.assertEqual(status, 200)
        self.assertEqual(body["data"]["id"], m_id)

        # Delete
        status, body = self._request("DELETE", f"/api/v1/monitors/{m_id}")
        self.assertEqual(status, 200)

        # Confirm deleted
        status, _ = self._request("GET", f"/api/v1/monitors/{m_id}")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
