# Installation

## Quick Start (recommended)

```powershell
# Install just if you don't have it
winget install Casey.Just

git clone https://github.com/sandraschi/monitoring-mcp
cd monitoring-mcp
just
```

The interactive recipe dashboard opens in your browser. From there:

```powershell
just bootstrap   # install all dependencies
just serve       # start the server
just web         # start the frontend (if applicable)
```

> **Why not `pip install`?** MCP servers bundle webapps, configs, project scaffolding, and tooling that a flat Python package can't deliver. `just` gives you the complete, ready-to-run stack.

---

## Traditional Setup

If you prefer not to use `just`:

1. Install [Python 3.12+](https://python.org) and [uv](https://docs.astral.sh/uv/)
2. Clone and enter the repo:
   ```powershell
   git clone https://github.com/sandraschi/monitoring-mcp
   Set-Location monitoring-mcp
   ```
3. Install dependencies:
   ```powershell
   uv sync --all-extras
   ```
4. Copy env and edit endpoints / credentials:
   ```powershell
   Copy-Item .env.example .env
   ```
5. Start the server:
   ```powershell
   # stdio mode (Claude Desktop / Cursor MCP)
   uv run python -m monitoring_mcp

   # HTTP mode (web dashboard + MCP streamable HTTP)
   $env:MCP_TRANSPORT = "http"
   uv run python -m monitoring_mcp --http --port 10851
   ```
6. Open `http://127.0.0.1:10851` (or the Vite frontend on `10850`).

---

## Claude Desktop / MCPB

Drag the packaged `.mcpb` into Claude Desktop, or register:

```json
{
  "mcpServers": {
    "monitoring-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "D:/Dev/repos/monitoring-mcp", "python", "-m", "monitoring_mcp"],
      "env": {
        "MONITORING_MCP_GRAFANA_URL": "http://localhost:3000",
        "MONITORING_MCP_PROMETHEUS_URL": "http://localhost:9090",
        "MONITORING_MCP_LOKI_URL": "http://localhost:3100"
      }
    }
  }
}
```

---

## Containers (optional)

Not required for normal MCP use. Useful for packaging or a demo stack.

```powershell
docker compose up -d --build
# Podman: see docs/PODMAN.md
docker compose --profile stack up -d   # optional Grafana/Prom/Loki/Alertmanager
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `just` not found | `winget install Casey.Just` (or scoop / brew) |
| Port conflict | `just kill-all` to clear fleet ports (10700–11000) |
| Dependencies out of sync | `uv sync --all-extras` |
| Tools can't reach backends | Check [docs/CONFIGURATION.md](docs/CONFIGURATION.md) and [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) |
| Something else | [Open a GitHub issue](https://github.com/sandraschi/monitoring-mcp/issues) |

---

*See the main [README](README.md) for feature overview and documentation.*
