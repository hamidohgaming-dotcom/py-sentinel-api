import unittest
from sentinel.metrics import get_system_telemetry, get_uptime_seconds


class TestMetrics(unittest.TestCase):
    def test_uptime_seconds(self):
        up = get_uptime_seconds()
        self.assertIsInstance(up, float)
        self.assertGreaterEqual(up, 0.0)

    def test_system_telemetry_structure(self):
        data = get_system_telemetry()
        self.assertIn("platform", data)
        self.assertIn("resources", data)
        self.assertIn("process", data)
        self.assertIn("timestamp", data)

        res = data["resources"]
        self.assertIn("disk", res)
        self.assertGreater(res["disk"]["total_gb"], 0)


if __name__ == "__main__":
    unittest.main()
