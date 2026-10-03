"""
PySentinel REST API Server.
Built with standard library HTTP engine for 100% portable out-of-the-box operation,
with full JSON REST API compatibility.
"""

import json
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Optional

from .metrics import get_system_telemetry, get_uptime_seconds
from .checker import check_endpoint
from .store import MonitorStore


class SentinelRequestHandler(BaseHTTPRequestHandler):
    store: MonitorStore = None

    def _send_json(self, status_code: int, data: dict):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def _parse_body(self) -> dict:
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len == 0:
            return {}
        raw = self.rfile.read(content_len).decode("utf-8")
        return json.loads(raw)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if path == "":
            path = "/"

        # Health endpoint
        if path == "/health":
            return self._send_json(200, {
                "status": "healthy",
                "service": "py-sentinel-api",
                "uptime_seconds": get_uptime_seconds()
            })

        # System telemetry metrics
        if path == "/api/v1/metrics":
            telemetry = get_system_telemetry()
            return self._send_json(200, {"success": True, "data": telemetry})

        # Monitoring aggregate summary
        if path == "/api/v1/summary":
            summary = self.store.get_aggregate_summary()
            return self._send_json(200, {"success": True, "data": summary})

        # List all monitors
        if path == "/api/v1/monitors":
            qs = parse_qs(parsed.query)
            tag = qs.get("tag", [None])[0]
            monitors = self.store.list_monitors(tag=tag)
            return self._send_json(200, {"success": True, "count": len(monitors), "data": monitors})

        # Get single monitor by ID
        m = re.match(r"^/api/v1/monitors/([a-zA-Z0-9_-]+)$", path)
        if m:
            m_id = m.group(1)
            record = self.store.get_monitor(m_id)
            if not record:
                return self._send_json(404, {"success": False, "error": f"Monitor '{m_id}' not found"})
            history = self.store.get_history(m_id, limit=20)
            return self._send_json(200, {"success": True, "data": record, "history": history})

        return self._send_json(404, {"success": False, "error": "Endpoint not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        # Ad-hoc ping check
        if path == "/api/v1/ping":
            try:
                body = self._parse_body()
                url = body.get("url")
                if not url:
                    return self._send_json(400, {"success": False, "error": "Missing required 'url' parameter"})
                expected = int(body.get("expected_status", 200))
                timeout = float(body.get("timeout_seconds", 5.0))
                res = check_endpoint(url, expected_status=expected, timeout=timeout)
                return self._send_json(200, {"success": True, "result": res})
            except Exception as e:
                return self._send_json(400, {"success": False, "error": str(e)})

        # Create monitor
        if path == "/api/v1/monitors":
            try:
                body = self._parse_body()
                if "url" not in body:
                    return self._send_json(400, {"success": False, "error": "Missing required field 'url'"})
                created = self.store.add_monitor(body)
                return self._send_json(201, {"success": True, "data": created})
            except Exception as e:
                return self._send_json(400, {"success": False, "error": str(e)})

        # Trigger check for specific monitor
        m = re.match(r"^/api/v1/monitors/([a-zA-Z0-9_-]+)/check$", path)
        if m:
            m_id = m.group(1)
            record = self.store.get_monitor(m_id)
            if not record:
                return self._send_json(404, {"success": False, "error": f"Monitor '{m_id}' not found"})

            res = check_endpoint(
                url=record["url"],
                expected_status=record["expected_status"],
                timeout=record["timeout_seconds"]
            )
            self.store.record_check_result(m_id, res)
            return self._send_json(200, {"success": True, "result": res})

        return self._send_json(404, {"success": False, "error": "Endpoint not found"})

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        m = re.match(r"^/api/v1/monitors/([a-zA-Z0-9_-]+)$", path)
        if m:
            m_id = m.group(1)
            ok = self.store.delete_monitor(m_id)
            if not ok:
                return self._send_json(404, {"success": False, "error": f"Monitor '{m_id}' not found"})
            return self._send_json(200, {"success": True, "message": f"Monitor '{m_id}' deleted successfully"})

        return self._send_json(404, {"success": False, "error": "Endpoint not found"})

    def log_message(self, format, *args):
        # Suppress verbose standard HTTP request logging in test/clean output
        return


def create_server(host: str = "127.0.0.1", port: int = 8000, store: Optional[MonitorStore] = None) -> HTTPServer:
    if store is None:
        store = MonitorStore()
    handler_class = SentinelRequestHandler
    handler_class.store = store
    return HTTPServer((host, port), handler_class)


def run_server(host: str = "0.0.0.0", port: int = 8000):
    server = create_server(host=host, port=port)
    print(f"==================================================")
    print(f" PySentinel REST API running at http://{host}:{port}")
    print(f" Health check:  http://{host}:{port}/health")
    print(f" Telemetry:     http://{host}:{port}/api/v1/metrics")
    print(f" Monitors API:  http://{host}:{port}/api/v1/monitors")
    print(f" Summary API:   http://{host}:{port}/api/v1/summary")
    print(f"==================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down PySentinel server...")
        server.server_close()
