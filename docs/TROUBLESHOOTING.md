# Troubleshooting

## "Failed to fetch" in web UI

The frontend can't reach the backend. Check:

1. Backend is running: `uv run python -m monitoring_mcp --http --port 10851`
2. Port matches `web_sota` API base (`http://127.0.0.1:10851`)
3. CORS allows `http://127.0.0.1:10850` (frontend origin)
4. `MCP_WEB_USER` / `MCP_WEB_PASSWORD` are set if the UI uses basic auth

## Backend starts but tools return connection errors

The server can't reach Grafana/Prometheus/Loki/Alertmanager. Check:

- Are the services running? (`docker ps` or `podman ps`)
- `MONITORING_MCP_GRAFANA_URL` etc. point to the right host:port
- For Docker, use `host.docker.internal` instead of `localhost` to reach host services
- For Podman, use `host.containers.internal` (see [PODMAN.md](PODMAN.md))
- For Compose with `--profile stack`, use the service name (e.g. `http://grafana:3000`)

## Auth errors (401)

If `MCP_WEB_USER` / `MCP_WEB_PASSWORD` are not set, the web API may fail closed.
Set them in `.env` before starting the dashboard.

For Grafana/Prom/Loki API 401s, set the matching `MONITORING_MCP_*` API key or basic-auth vars ([CONFIGURATION.md](CONFIGURATION.md)).

## Silences fail

Silences require Alertmanager at `MONITORING_MCP_ALERTMANAGER_URL` (default `http://localhost:9093`).

## Loki tail returns few/no lines

`tail_logs` uses the Loki **WebSocket** API. If the WS upgrade fails (proxy, auth, or older Loki), the client falls back to a 2-minute `query_range`. Check `transport` in the tool result (`websocket` vs `query_range_fallback`).

## Alert rule create/update/delete

Prometheus itself does not expose a general rule write API. Create/update/delete go through **Grafana unified alerting** (`/api/v1/provisioning/alert-rules`). Loki ruler ops need the Loki ruler API enabled.

## Tests / coverage

```powershell
uv run --extra dev pytest
```

Gate is **50%** line coverage (`pyproject.toml`). If CI fails the gate, add mocked tool tests under `tests/unit/`.

## NSIS installer hangs on install/uninstall

The hooks in `native/windows/hooks.nsh` kill the backend process before install.
If a zombie process holds the port, run manually:

```powershell
taskkill /F /IM monitoring-mcp-backend.exe
taskkill /F /IM monitoring-mcp-native.exe
```

## Tauri WebView shows blank screen

Check `web_sota/dist/` exists and was built (`Set-Location web_sota; npm run build`).
Check `tauri.conf.json` `frontendDist` points to `../web_sota/dist`.

## Windows Defender flags PyInstaller .exe

Common false positive for onefile PyInstaller binaries. Add an exclusion or
submit to Microsoft for review. Building with `--onedir` (instead of `--onefile`)
can reduce false positive rate.
