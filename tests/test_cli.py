import unittest
from sentinel.cli import build_parser


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.parser = build_parser()

    def test_check_command_args(self):
        args = self.parser.parse_args(["check", "https://example.com", "--status", "200", "--timeout", "3.0"])
        self.assertEqual(args.command, "check")
        self.assertEqual(args.url, "https://example.com")
        self.assertEqual(args.status, 200)
        self.assertEqual(args.timeout, 3.0)

    def test_sysinfo_command_args(self):
        args = self.parser.parse_args(["sysinfo"])
        self.assertEqual(args.command, "sysinfo")

    def test_serve_command_args(self):
        args = self.parser.parse_args(["serve", "--port", "9000", "--host", "0.0.0.0"])
        self.assertEqual(args.command, "serve")
        self.assertEqual(args.port, 9000)
        self.assertEqual(args.host, "0.0.0.0")


if __name__ == "__main__":
    unittest.main()
