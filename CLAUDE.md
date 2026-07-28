# monitoring-mcp — Claude Code Guide

## Overview

FastMCP **3.4.4+** monitoring MCP for Grafana, Prometheus, Loki, and Alertmanager.

## Standards

- Portmanteau tools with `operation` enum — full list in [docs/TOOLS.md](docs/TOOLS.md)
- Responses: structured dicts with `success`, `conversational_summary`, domain fields
- Dual transport: stdio (Claude Desktop) + HTTP (`MCP_TRANSPORT=http` / `--http`)
- Env prefix: `MONITORING_MCP_*` — see [docs/CONFIGURATION.md](docs/CONFIGURATION.md)
- Fleet standards: [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs)

## Key Files

- `README.md` — overview
- `docs/TOOLS.md` — operations
- `docs/PODMAN.md` — containers
- `pyproject.toml` — deps / coverage gate (50%)
- `AGENTS.md` — agent-oriented twin of this file
