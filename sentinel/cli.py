"""
PySentinel Command Line Interface.
Provides fast diagnostic checks, continuous monitoring, and system metrics reporting.
"""

import sys
import argparse
import time
from .checker import check_endpoint
from .metrics import get_system_telemetry
from .store import MonitorStore
from .server import run_server


def cmd_check(args):
    url = args.url
    print(f"[*] Probing endpoint: {url} (expected: {args.status}, timeout: {args.timeout}s)...")
    res = check_endpoint(url, expected_status=args.status, timeout=args.timeout)

    symbol = "[PASS]" if res["healthy"] else "[FAIL]"
    status_display = res["status_code"] if res["status_code"] else "N/A"
    print(f"{symbol} Status: {status_display} | Latency: {res['latency_ms']}ms | URL: {res['url']}")
    if res.get("error"):
        print(f"       Alert: {res['error']}")
    return 0 if res["healthy"] else 1


def cmd_sysinfo(args):
    data = get_system_telemetry()
    p = data["platform"]
    r = data["resources"]
    d = r["disk"]

    print("\n=== PySentinel Host Telemetry ===")
    print(f"OS Platform:   {p['system']} {p['release']} ({p['architecture']})")
    print(f"Python:        {p['python_version']}")
    print(f"CPU Cores:     {r['cpu_cores']}")
    print(f"Disk Usage:    {d['used_gb']} GB / {d['total_gb']} GB ({d['used_percent']}% used)")
    print(f"Free Disk:     {d['free_gb']} GB")
    print(f"Process PID:   {data['process']['pid']}")
    print(f"Uptime:        {data['process']['uptime_seconds']}s")
    print("==================================\n")
    return 0


def cmd_list(args):
    store = MonitorStore()
    monitors = store.list_monitors()
    print(f"\nConfigured Monitors ({len(monitors)}):")
    print("-" * 65)
    for m in monitors:
        print(f"[{m['id']}] {m['name']} -> {m['url']}")
        print(f"     Expected: {m['expected_status']} | Threshold: {m['latency_threshold_ms']}ms | Tags: {','.join(m['tags'])}")
    print("-" * 65 + "\n")
    return 0


def cmd_serve(args):
    run_server(host=args.host, port=args.port)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sentinel",
        description="PySentinel: Endpoint Health Watchdog & Telemetry REST API/CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # check
    p_check = subparsers.add_parser("check", help="Run a one-off endpoint health check")
    p_check.add_argument("url", help="Target URL (e.g., https://example.com)")
    p_check.add_argument("--status", type=int, default=200, help="Expected HTTP status (default: 200)")
    p_check.add_argument("--timeout", type=float, default=5.0, help="Request timeout seconds (default: 5.0)")
    p_check.set_defaults(func=cmd_check)

    # sysinfo
    p_sys = subparsers.add_parser("sysinfo", help="Display host hardware and system resource metrics")
    p_sys.set_defaults(func=cmd_sysinfo)

    # list
    p_list = subparsers.add_parser("list", help="List registered monitors")
    p_list.set_defaults(func=cmd_list)

    # serve
    p_serve = subparsers.add_parser("serve", help="Launch the REST API server")
    p_serve.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    p_serve.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    p_serve.set_defaults(func=cmd_serve)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
