"""
Endpoint health checker and latency watchdog.
"""

import time
import urllib.request
import urllib.error
from typing import Dict, Any, Optional


def check_endpoint(
    url: str,
    expected_status: int = 200,
    timeout: float = 5.0,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Perform a live HTTP(S) health check against a target URL.
    Measures latency in milliseconds, checks status code, and captures response metadata.
    """
    if not url.startswith(("http://", "https://")):
        return {
            "url": url,
            "healthy": False,
            "status_code": 0,
            "latency_ms": 0.0,
            "error": "Invalid URL scheme. Must start with http:// or https://",
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

    req_headers = {"User-Agent": "PySentinel-Watchdog/1.0"}
    if headers:
        req_headers.update(headers)

    req = urllib.request.Request(url, headers=req_headers, method="GET")
    start = time.perf_counter()

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            status_code = response.getcode()
            healthy = (status_code == expected_status)
            return {
                "url": url,
                "healthy": healthy,
                "status_code": status_code,
                "expected_status": expected_status,
                "latency_ms": latency_ms,
                "error": None if healthy else f"Expected status {expected_status}, got {status_code}",
                "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
    except urllib.error.HTTPError as exc:
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        healthy = (exc.code == expected_status)
        return {
            "url": url,
            "healthy": healthy,
            "status_code": exc.code,
            "expected_status": expected_status,
            "latency_ms": latency_ms,
            "error": None if healthy else f"HTTP {exc.code}: {exc.reason}",
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    except urllib.error.URLError as exc:
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "url": url,
            "healthy": False,
            "status_code": 0,
            "expected_status": expected_status,
            "latency_ms": latency_ms,
            "error": f"Connection error: {str(exc.reason)}",
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    except Exception as exc:
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "url": url,
            "healthy": False,
            "status_code": 0,
            "expected_status": expected_status,
            "latency_ms": latency_ms,
            "error": str(exc),
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
