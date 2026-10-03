"""
Monitor storage and history manager.
Supports in-memory state with thread-safe access.
"""

import uuid
import time
import threading
from typing import Dict, List, Optional, Any


class MonitorStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._monitors: Dict[str, Dict[str, Any]] = {}
        self._history: Dict[str, List[Dict[str, Any]]] = {}
        self._seed_default_targets()

    def _seed_default_targets(self):
        defaults = [
            {
                "name": "Cloudflare DNS",
                "url": "https://1.1.1.1",
                "expected_status": 200,
                "interval_seconds": 60,
                "timeout_seconds": 5.0,
                "latency_threshold_ms": 300.0,
                "tags": ["dns", "infrastructure"]
            },
            {
                "name": "Google Public",
                "url": "https://www.google.com",
                "expected_status": 200,
                "interval_seconds": 60,
                "timeout_seconds": 5.0,
                "latency_threshold_ms": 400.0,
                "tags": ["search", "cdn"]
            }
        ]
        for item in defaults:
            self.add_monitor(item)

    def list_monitors(self, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            items = list(self._monitors.values())
            if tag:
                items = [m for m in items if tag in m.get("tags", [])]
            return items

    def get_monitor(self, monitor_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._monitors.get(monitor_id)

    def add_monitor(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            m_id = str(uuid.uuid4())[:8]
            created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            record = {
                "id": m_id,
                "name": data.get("name", "Unnamed Monitor"),
                "url": data["url"],
                "expected_status": int(data.get("expected_status", 200)),
                "interval_seconds": int(data.get("interval_seconds", 60)),
                "timeout_seconds": float(data.get("timeout_seconds", 5.0)),
                "latency_threshold_ms": float(data.get("latency_threshold_ms", 500.0)),
                "tags": data.get("tags", []),
                "active": bool(data.get("active", True)),
                "last_check": None,
                "created_at": created_at
            }
            self._monitors[m_id] = record
            self._history[m_id] = []
            return record

    def record_check_result(self, monitor_id: str, result: Dict[str, Any]):
        with self._lock:
            if monitor_id not in self._monitors:
                return
            self._monitors[monitor_id]["last_check"] = result
            hist = self._history.setdefault(monitor_id, [])
            hist.append(result)
            # Keep max 50 historical logs per monitor
            if len(hist) > 50:
                hist.pop(0)

    def get_history(self, monitor_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        with self._lock:
            hist = self._history.get(monitor_id, [])
            return list(reversed(hist[-limit:]))

    def delete_monitor(self, monitor_id: str) -> bool:
        with self._lock:
            if monitor_id in self._monitors:
                del self._monitors[monitor_id]
                self._history.pop(monitor_id, None)
                return True
            return False

    def get_aggregate_summary(self) -> Dict[str, Any]:
        with self._lock:
            total_monitors = len(self._monitors)
            healthy_count = 0
            unhealthy_count = 0
            pending_count = 0
            latencies = []

            for m in self._monitors.values():
                lc = m.get("last_check")
                if lc is None:
                    pending_count += 1
                elif lc.get("healthy"):
                    healthy_count += 1
                    latencies.append(lc.get("latency_ms", 0.0))
                else:
                    unhealthy_count += 1
                    latencies.append(lc.get("latency_ms", 0.0))

            avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
            uptime_pct = round((healthy_count / (healthy_count + unhealthy_count)) * 100, 2) if (healthy_count + unhealthy_count) > 0 else 100.0

            return {
                "total_monitors": total_monitors,
                "healthy": healthy_count,
                "unhealthy": unhealthy_count,
                "pending": pending_count,
                "uptime_percentage": uptime_pct,
                "average_latency_ms": avg_latency
            }
