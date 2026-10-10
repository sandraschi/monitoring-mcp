# monitoring-mcp — GitHub Copilot Instructions

## Session Context

This repo is `monitoring-mcp`: a FastMCP 3.4.4 server bridging AI assistants to
Grafana + Prometheus + Loki (+ Alertmanager webhooks).

- MCP entry: `src/monitoring_mcp/mcp_server.py` — 6 portmanteau tools
  (`grafana_management`, `prometheus_monitoring`, `loki_logging`,
  `cross_system_correlation`, `monitoring_status`, `monitoring_shutdown`).
  Tool reference: `docs/TOOLS.md`.
- REST entry: `src/monitoring_mcp/server.py` (`monitoring_mcp.server:app`, :10851).
- Frontend: `web_sota/` (React + Vite + Tailwind, :10850).
- Tests: `uv run --extra dev pytest -k "not slow"` (coverage gate 50%).
- Lint: `uv run ruff check .`, `uv run ruff format . --check`.

When generating code here: portmanteau pattern with `operation` enum, tool
docstrings must include `## Return Format` and `## Examples` sections (never
`Args:` blocks — use `Annotated[..., Field(description=...)]`), returns carry
`success` + `conversational_summary`. Config lives in `MONITORING_MCP_*` env
vars (`docs/CONFIGURATION.md`). Setup checklist: `docs/ONBOARDING.md`.
