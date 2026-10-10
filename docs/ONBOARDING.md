# ONBOARDING — monitoring-mcp

Get from zero to a working Grafana + Prometheus + Loki assistant in ~15 minutes.

## What this is for

`monitoring-mcp` connects an AI assistant (Claude Desktop via stdio, or the
`web_sota` dashboard via HTTP) to your observability stack: query Prometheus
metrics (PromQL), search Loki logs (LogQL), manage Grafana dashboards, and
correlate incidents across all three in natural language.

## What you need

| Requirement | Why | Get it here |
|---|---|---|
| Python 3.13 + `uv` | MCP server runtime | `winget install astral-sh.uv` |
| Node.js 22 + npm | `web_sota` dashboard | `winget install OpenJS.NodeJS.LTS` |
| Grafana (URL + API key) | Dashboards/datasources | Local `http://localhost:3000` or Grafana Cloud |
| Prometheus (URL) | Metrics + targets + rules | Local `http://localhost:9090` |
| Loki (URL) | Logs | Local `http://localhost:3100` |
| Ollama (optional) | Local LLM for Chat page | `https://ollama.me`, then `ollama pull llama3.2:3b` |

No Grafana/Prometheus/Loki yet? The fastest path is the compose stack:
`docker compose up -d` (see `docs/PODMAN.md` for Podman notes).

## Setup

1. Copy env template: `Copy-Item .env.example .env`
2. Fill in at least:
   - `MONITORING_MCP_GRAFANA_URL` + `MONITORING_MCP_GRAFANA_API_KEY`
   - `MONITORING_MCP_PROMETHEUS_URL`
   - `MONITORING_MCP_LOKI_URL`
   - `MONITORING_MCP_ALERTMANAGER_URL` (only if you want silences + webhooks)
3. `uv sync --extra dev`
4. Sanity checks (expect all green):
   - `uv run --extra dev pytest -k "not slow" -q` (unit suite, 50% coverage gate)
   - `uv run python -m monitoring_mcp --stdio` (Ctrl+C after the ready log line)
   - Backend: `uv run uvicorn monitoring_mcp.server:app --port 10851`,
     then open `http://127.0.0.1:10851/api/health` (expect `{"status":"ok",...}`)
5. Full stack: `.\start.ps1` (backend :10851 + frontend :10850, browser opens
   when both are healthy). Backend only: `.\start.ps1 -BackendOnly`.

## Common pitfalls

- Chat page says the LLM is unreachable: Ollama is not running or the model is
  missing — `ollama serve` + `ollama pull llama3.2:3b`. Without any local LLM the
  Chat page still works but answers degrade to tool listings (declared fallback).
- Dashboard shows "Offline": backend not on :10851 — check nothing else owns the
  port (`start.ps1` clears zombies automatically).
- Grafana 401s: API key needs Viewer minimum (Editor for dashboard create/update).
- Alertmanager webhook 400s: payload must contain an `alerts` array
  (Alertmanager sends this natively — see `POST /api/webhooks/alertmanager`).
- Tauri desktop app: set `MONITORING_MCP_TAURI=1` is NOT needed for CORS anymore
  (the Tauri origin regex is unconditional); just build per `native/`.

## Next steps

- Tool reference: `docs/TOOLS.md`
- Config reference: `docs/CONFIGURATION.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`
