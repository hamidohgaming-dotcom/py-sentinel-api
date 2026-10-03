# PySentinel API & CLI Watchdog

[![CI Pipeline](https://github.com/USER/py-sentinel-api/actions/workflows/ci.yml/badge.svg)](https://github.com/USER/py-sentinel-api/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Code Style: Standard](https://img.shields.io/badge/code%20style-PEP8-green.svg)](https://pep8.org/)

> High-performance endpoint health watchdog, latency monitor, and host system telemetry service with a dual REST API and command-line interface.

---

## 🌟 Highlights & Features

- **🚀 Zero-Friction Setup:** Built using Python's robust standard library with zero mandatory external package installations needed to run out-of-the-box.
- **⏱️ Live Latency & Health Checks:** Real-time millisecond latency measurement, HTTP status code validation, and error classification.
- **🖥️ Host System Telemetry:** Live reports of CPU count/load, RAM/disk usage, architecture, and kernel version.
- **🛠️ Dual Interface (REST API + CLI):**
  - **REST API:** Full CRUD for monitor registration, history logging, and summary reporting.
  - **CLI:** Instant one-off diagnostics (`sentinel check <url>`), system telemetry inspection (`sentinel sysinfo`), and daemon runner.
- **🧪 Comprehensive Test Suite:** Unit and integration tests covering the checker engine, storage layer, CLI arguments, and HTTP REST routes.
- **📦 Matrix CI/CD:** GitHub Actions workflow verified across Python 3.10, 3.11, 3.12, and 3.13.

---

## 🏗️ Architecture

```
py-sentinel-api/
├── .github/
│   └── workflows/
│       └── ci.yml             # Matrix CI testing workflow
├── sentinel/                  # Core Python package
│   ├── __init__.py            # Version & package metadata
│   ├── __main__.py            # Executable module entry
│   ├── checker.py             # HTTP health probing & latency measurement
│   ├── metrics.py             # System telemetry & resource collector
│   ├── store.py               # Monitor management & historical log buffer
│   ├── server.py              # REST API server & HTTP request dispatcher
│   └── cli.py                 # Command-line interface parser & handlers
├── tests/                     # Test suite
│   ├── test_checker.py        # Network & URL validation tests
│   ├── test_store.py          # Storage CRUD & history tests
│   ├── test_metrics.py        # Telemetry collector tests
│   ├── test_api.py            # HTTP REST API integration tests
│   └── test_cli.py            # CLI command & argument parser tests
├── .gitignore
├── LICENSE                    # MIT License
├── pyproject.toml             # Modern Python project configuration
├── requirements.txt
└── README.md
```

---

## 🚀 Quickstart

### 1. Run with Python CLI
```bash
# Display host hardware & system telemetry
python -m sentinel sysinfo

# Check any live URL with latency measurement
python -m sentinel check https://httpbin.org/status/200

# List pre-configured watchdog monitors
python -m sentinel list

# Start the REST API server
python -m sentinel serve --port 8000
```

### 2. Run Automated Test Suite
```bash
python -m unittest discover -s tests -v
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | PySentinel service uptime and status |
| `GET` | `/api/v1/metrics` | Host telemetry (CPU cores, disk utilization, OS info) |
| `GET` | `/api/v1/summary` | Aggregate uptime %, healthy/unhealthy breakdown, avg latency |
| `GET` | `/api/v1/monitors` | List registered endpoint monitors (supports `?tag=`) |
| `GET` | `/api/v1/monitors/:id`| Retrieve monitor status and check history |
| `POST` | `/api/v1/monitors` | Register a new endpoint monitor |
| `POST` | `/api/v1/monitors/:id/check` | Trigger an instant probe and record history |
| `POST` | `/api/v1/ping` | Ad-hoc one-time URL ping check |
| `DELETE` | `/api/v1/monitors/:id` | Remove a monitor |

### Example: Ad-hoc Check
```bash
curl -X POST http://localhost:8000/api/v1/ping \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com", "expected_status": 200}'
```

---

## 🚢 Publishing to GitHub

```bash
# 1. Initialize local repository (already prepared)
git init
git add .
git commit -m "feat: initial commit for py-sentinel-api"

# 2. Add remote repository
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/py-sentinel-api.git

# 3. Push to GitHub
git push -u origin main
```

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
