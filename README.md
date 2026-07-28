# monitoring-mcp

[![CI](https://github.com/sandraschi/monitoring-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/sandraschi/monitoring-mcp/actions)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.4+-purple)](https://github.com/jlowin/fastmcp)
[![Grafana](https://img.shields.io/badge/Grafana-Supported-orange)](https://grafana.com)
[![Prometheus](https://img.shields.io/badge/Prometheus-Supported-orange)](https://prometheus.io)
[![Loki](https://img.shields.io/badge/Loki-Supported-green)](https://grafana.com/oss/loki/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue)](https://python.org)

An MCP server that connects AI assistants to your Grafana + Prometheus + Loki
(+ Alertmanager) observability stack — local, Docker, Podman, or remote. Query
metrics, search logs, manage dashboards, silence alerts, and correlate incidents
through natural language.

> **Docs**: [INSTALL.md](INSTALL.md) · [Configuration](docs/CONFIGURATION.md) · [Tools](docs/TOOLS.md) · [Podman](docs/PODMAN.md) · [Development](docs/DEVELOPMENT.md) · [Troubleshooting](docs/TROUBLESHOOTING.md)

## Features

- **Grafana** — dashboards, panels, folders, datasources, unified alerting, export/import
- **Prometheus** — PromQL (instant + range), targets, rules, flags/config, sampling + cache
- **Alertmanager** — list/create/expire silences
- **Loki** — LogQL, WebSocket tail (with fallback), export, compare, ruler alerts
- **Cross-system correlation** — incident / root-cause / bottleneck / dependency heuristics
- **Health monitoring** — connectivity, storage, security posture, capacity signals
- **AI chat** — local LLM via Ollama / LM Studio in the web UI

## Quick Install

```powershell
git clone https://github.com/sandraschi/monitoring-mcp
cd monitoring-mcp
just
```

Or drag the `.mcpb` bundle into Claude Desktop. See [INSTALL.md](INSTALL.md) for all options.

## What You Can Do

| You say | The server does |
|---------|----------------|
| "Check system health" | Hits Grafana/Prometheus/Loki APIs; returns status per component |
| "Show my top 5 error log sources" | LogQL query across Loki; groups by label |
| "List Grafana dashboards tagged prod" | Searches Grafana API; filters by tag |
| "Correlate the 5xx spike at 14:30" | Cross-references Prometheus error rates with Loki error logs |
| "Silence HighError for 2 hours" | Creates an Alertmanager silence |

## Quick Start (Code)

```python
await monitoring_status(operation="system_health")
await prometheus_monitoring(operation="query_metrics", query="up")
await loki_logging(operation="query_logs", query='{job="api"} |= "ERROR"')
await grafana_management(operation="list_dashboards")
await cross_system_correlation(operation="correlate_incident", incident_description="5xx spike")
```

## Containers

```powershell
# MCP only (talks to host Grafana/Prom/Loki via host gateway)
docker compose up -d --build
# or: podman compose -f docker-compose.yml up -d --build

# Optional full stack
docker compose --profile stack up -d
```

See [docs/PODMAN.md](docs/PODMAN.md) for Podman host URLs (`host.containers.internal`).

## Project Structure

```
├── src/monitoring_mcp/       # Python MCP server
│   ├── tools/                # Portmanteau tools (grafana, prometheus, loki, correlation, status)
│   ├── config.py             # Pydantic v2 settings
│   ├── utils.py              # Cache, sampling, encryption helpers
│   ├── server.py             # ASGI entry point
│   └── web.py                # REST endpoints (/api/chat, /api/health, /api/tools)
├── web_sota/                 # React/Vite/Tailwind dashboard
├── native/                   # Tauri 2.0 NSIS wrapper
├── docker-compose.yml        # Docker / Podman Compose
└── docs/                     # Reference documentation
```

## Requirements

- Python **3.12+** (3.13 supported)
- FastMCP **3.4.4+**
- Optional: Grafana, Prometheus, Loki, Alertmanager reachable over HTTP
