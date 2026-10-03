import unittest
from sentinel.checker import check_endpoint


class TestChecker(unittest.TestCase):
    def test_invalid_scheme(self):
        res = check_endpoint("ftp://example.com")
        self.assertFalse(res["healthy"])
        self.assertIn("Invalid URL scheme", res["error"])

    def test_unreachable_domain(self):
        res = check_endpoint("http://nonexistent-domain-xyz-123456789.test", timeout=1.0)
        self.assertFalse(res["healthy"])
        self.assertEqual(res["status_code"], 0)
        self.assertIsNotNone(res["error"])


if __name__ == "__main__":
    unittest.main()
