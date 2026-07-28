# Development

## Prerequisites

- Python 3.12+ (3.13 OK)
- [uv](https://docs.astral.sh/uv/)
- Node.js 20+ (for `web_sota` frontend)
- Rust toolchain (for Tauri/NSIS builds — optional)
- Docker or Podman (optional; compose stack only)

## Setup

```powershell
uv sync --extra dev
Set-Location web_sota
npm install
Set-Location ..
Copy-Item .env.example .env
```

## Commands

```powershell
just lint        # Ruff (Python) + Biome (JS/TS)
just fix         # Auto-fix lint issues
uv run --extra dev pytest    # Unit tests (coverage gate: 50%)
Set-Location web_sota; npx tsc --noEmit   # TypeScript check
```

## Running Locally

```powershell
# Terminal 1 — MCP / backend (HTTP)
$env:MCP_TRANSPORT = "http"
uv run python -m monitoring_mcp --http --port 10851

# Terminal 2 — frontend
Set-Location web_sota
npm run dev
```

Then open `http://127.0.0.1:10850`.

stdio (for Claude Desktop / Cursor):

```powershell
uv run python -m monitoring_mcp --stdio
```

## Architecture

```
web_sota (React/Vite) ──HTTP──► backend (FastAPI/FastMCP) ──HTTP──► Grafana / Prometheus / Loki / Alertmanager
    :10850                       :10851
```

The backend exposes:

- REST endpoints (`/api/*`) for the web dashboard
- MCP HTTP endpoint (`/mcp`) for Cursor / Claude
- stdio mode for desktop MCP hosts

Portmanteau tools live under `src/monitoring_mcp/tools/`. Shared cache/sampling/crypto helpers are in `utils.py`.

## Testing

```powershell
uv run --extra dev pytest                       # Unit tests (~74% line coverage; gate 50%)
uv run --extra dev pytest tests/unit -k prom    # Subset
Set-Location web_sota; npx playwright test      # E2E (if configured)
uv run python scripts/cua-smoke.py              # NSIS installer smoke test (Windows)
```

Coverage config: `pyproject.toml` (`--cov-fail-under=50`). HTML report: `coverage_html/`.

## Containers

```powershell
docker compose up -d --build
docker compose --profile stack up -d
```

Podman notes: [PODMAN.md](PODMAN.md).

## Tauri/NSIS Build

```powershell
just build-native      # Full pipeline: frontend → PyInstaller → Tauri → NSIS
just cua-nsis-test     # Install → launch → verify → uninstall
```

## Code Standards

- **Python**: Ruff linting + formatting; type hints on public APIs
- **TypeScript**: Biome linting, strict TypeScript
- **FastMCP 3.4.4+**: Portmanteau tools with `operation` enum param
- **Tool returns**: Dict with `success`, conversational summary, and domain data
- **Fleet docs**: Align with `mcp-central-docs` when changing transports/packaging
