# monitoring-mcp — Agent Guide

## Overview

FastMCP **3.4.4+** monitoring MCP for Grafana, Prometheus, Loki, and Alertmanager.

## Standards

- Portmanteau tools with `operation` enum (see [docs/TOOLS.md](docs/TOOLS.md))
- Responses: structured dicts with `success`, `conversational_summary`, domain fields
- Dual transport: stdio (default) + HTTP (`MCP_TRANSPORT=http` / `--http`)
- Config prefix: `MONITORING_MCP_*` ([docs/CONFIGURATION.md](docs/CONFIGURATION.md))
- Fleet standards: [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs)

## Key Files

| Path | Role |
|------|------|
| `src/monitoring_mcp/mcp_server.py` | FastMCP app + tool registration |
| `src/monitoring_mcp/tools/` | grafana / prometheus / loki / correlation / status |
| `src/monitoring_mcp/config.py` | Pydantic settings |
| `src/monitoring_mcp/utils.py` | Cache, sampling, encryption helpers |
| `docs/TOOLS.md` | Operation reference (all implemented) |
| `docs/PODMAN.md` | Podman compose notes |

## Run

```powershell
uv sync --extra dev
uv run python -m monitoring_mcp --stdio
uv run --extra dev pytest
```

Install docs: follow `mcp-central-docs/standards/AGENT_INSTALL_REFERENCE.md`.
