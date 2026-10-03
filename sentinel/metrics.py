"""
Host system resource and telemetry collector.
Uses standard library modules for universal compatibility across Linux, macOS, and Windows.
"""

import os
import platform
import shutil
import time
from typing import Dict, Any

START_TIME = time.time()


def get_uptime_seconds() -> float:
    """Return application uptime in seconds."""
    return round(time.time() - START_TIME, 2)


def get_system_telemetry() -> Dict[str, Any]:
    """
    Collect system resource utilization and hardware/OS platform metadata.
    """
    # Disk usage
    total, used, free = shutil.disk_usage(os.path.abspath(os.sep))
    disk_percent = round((used / total) * 100, 2) if total > 0 else 0.0

    # CPU load average (available on Unix, fallback on Windows)
    cpu_count = os.cpu_count() or 1
    load_avg = None
    if hasattr(os, "getloadavg"):
        try:
            load_avg = os.getloadavg()
        except OSError:
            pass

    return {
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        },
        "resources": {
            "cpu_cores": cpu_count,
            "load_average_1_5_15": load_avg,
            "disk": {
                "total_gb": round(total / (1024 ** 3), 2),
                "used_gb": round(used / (1024 ** 3), 2),
                "free_gb": round(free / (1024 ** 3), 2),
                "used_percent": disk_percent
            }
        },
        "process": {
            "pid": os.getpid(),
            "uptime_seconds": get_uptime_seconds()
        },
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
