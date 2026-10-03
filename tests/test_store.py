import unittest
from sentinel.store import MonitorStore


class TestStore(unittest.TestCase):
    def setUp(self):
        self.store = MonitorStore()

    def test_initial_seeds(self):
        monitors = self.store.list_monitors()
        self.assertGreaterEqual(len(monitors), 2)

    def test_add_and_get_monitor(self):
        item = {
            "name": "Custom API",
            "url": "https://api.myproject.io/health",
            "expected_status": 200,
            "tags": ["prod", "custom"]
        }
        created = self.store.add_monitor(item)
        self.assertIn("id", created)
        self.assertEqual(created["name"], "Custom API")

        retrieved = self.store.get_monitor(created["id"])
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["url"], item["url"])

    def test_record_history(self):
        created = self.store.add_monitor({"url": "https://service.local"})
        m_id = created["id"]
        check_res = {"healthy": True, "latency_ms": 45.2, "status_code": 200}
        self.store.record_check_result(m_id, check_res)

        hist = self.store.get_history(m_id)
        self.assertEqual(len(hist), 1)
        self.assertEqual(hist[0]["latency_ms"], 45.2)

    def test_delete_monitor(self):
        created = self.store.add_monitor({"url": "https://delete-me.local"})
        m_id = created["id"]
        self.assertTrue(self.store.delete_monitor(m_id))
        self.assertIsNone(self.store.get_monitor(m_id))


if __name__ == "__main__":
    unittest.main()
