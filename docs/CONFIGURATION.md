# Configuration

## Environment Variables

### Web Authentication (REQUIRED for web UI)

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_WEB_USER` | Web UI username | (required) |
| `MCP_WEB_PASSWORD` | Web UI password | (required) |

### Monitoring Endpoints

| Variable | Description | Default |
|----------|-------------|---------|
| `MONITORING_MCP_GRAFANA_URL` | Grafana server URL | `http://localhost:3000` |
| `MONITORING_MCP_PROMETHEUS_URL` | Prometheus server URL | `http://localhost:9090` |
| `MONITORING_MCP_LOKI_URL` | Loki server URL | `http://localhost:3100` |
| `MONITORING_MCP_ALERTMANAGER_URL` | Alertmanager URL (silences) | `http://localhost:9093` |

### Grafana Authentication

| Variable | Description |
|----------|-------------|
| `MONITORING_MCP_GRAFANA_API_KEY` | Grafana API key (recommended) |
| `MONITORING_MCP_GRAFANA_USERNAME` | Grafana username (alternative) |
| `MONITORING_MCP_GRAFANA_PASSWORD` | Grafana password (alternative) |

### Prometheus / Loki Authentication

| Variable | Description |
|----------|-------------|
| `MONITORING_MCP_PROMETHEUS_BEARER_TOKEN` | Prometheus bearer token |
| `MONITORING_MCP_PROMETHEUS_USERNAME` / `_PASSWORD` | Prometheus basic auth |
| `MONITORING_MCP_LOKI_BEARER_TOKEN` | Loki bearer token |
| `MONITORING_MCP_LOKI_USERNAME` / `_PASSWORD` | Loki basic auth |

### Performance

| Variable | Description | Default |
|----------|-------------|---------|
| `MONITORING_MCP_REQUEST_TIMEOUT` | HTTP request timeout (s) | `30` |
| `MONITORING_MCP_MAX_CONCURRENT_REQUESTS` | Max concurrent API calls | `10` |
| `MONITORING_MCP_MAX_RESULTS_LIMIT` | Max query results | `1000` |
| `MONITORING_MCP_ENABLE_SAMPLING` | Auto-sample large datasets | `true` |
| `MONITORING_MCP_SAMPLING_THRESHOLD` | Row count to trigger sampling | `10000` |
| `MONITORING_MCP_SAMPLING_RATE` | Fraction to sample | `0.1` |
| `MONITORING_MCP_ENABLE_CACHE` | In-memory response cache | `true` |
| `MONITORING_MCP_CACHE_TTL_SECONDS` | Cache TTL | `300` |

### Storage

| Variable | Description | Default |
|----------|-------------|---------|
| `MONITORING_MCP_STORAGE_PATH` | Persistent data directory | `~/.monitoring-mcp` |
| `MONITORING_MCP_ENCRYPTION_KEY` | HMAC key (auto-persisted under storage path if unset) | (generated) |

### Transport (MCP mode)

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_TRANSPORT` | `stdio`, `http`, or `sse` | `stdio` |
| `MCP_PORT` | HTTP listening port | `10851` |
| `MCP_HOST` | Bind address | `127.0.0.1` |
| `MCP_PATH` | HTTP endpoint path | `/mcp` |

CLI equivalents: `--stdio`, `--http`, `--sse`, `--host`, `--port`, `--path`, `--debug`.

### Frontend / ASGI

| Variable | Description | Default |
|----------|-------------|---------|
| `MONITORING_PORT` | Alternate backend port for some launchers | falls back to `MCP_PORT` |
| `MONITORING_HOST` | Backend bind address | `127.0.0.1` |

## .env File

```powershell
Copy-Item .env.example .env
```

Edit endpoints and secrets. Do not commit `.env`.

## Ports

| Port | Service |
|------|---------|
| 10850 | Frontend (Vite dev) |
| 10851 | Backend (FastAPI + MCP HTTP) |
| 10786 | Compose-published MCP HTTP (`host:10786` → container `10851`) |

## Container host URLs

| Runtime | Reach host services from the MCP container |
|---------|--------------------------------------------|
| Docker Desktop | `http://host.docker.internal:<port>` |
| Podman | `http://host.containers.internal:<port>` |
| Compose `--profile stack` | Service DNS (`http://grafana:3000`, etc.) |

See [PODMAN.md](PODMAN.md).
