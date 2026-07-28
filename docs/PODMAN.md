# Podman notes for monitoring-mcp

This MCP is an HTTP client to Grafana / Prometheus / Loki / Alertmanager.
Podman vs Docker only matters for **how you run those backends** (and optionally this server).

## Run the MCP with Podman Compose

```powershell
podman machine start
podman compose -f docker-compose.yml up -d --build
```

On Podman, prefer host URLs like:

```powershell
$env:MONITORING_MCP_GRAFANA_URL = "http://host.containers.internal:3000"
$env:MONITORING_MCP_PROMETHEUS_URL = "http://host.containers.internal:9090"
$env:MONITORING_MCP_LOKI_URL = "http://host.containers.internal:3100"
$env:MONITORING_MCP_ALERTMANAGER_URL = "http://host.containers.internal:9093"
podman compose -f docker-compose.yml up -d
```

`docker-compose.yml` already maps both `host.docker.internal` and `host.containers.internal` via `extra_hosts`.

## Optional observability stack

```powershell
podman compose -f docker-compose.yml --profile stack up -d
```

When using the in-compose stack, point the MCP at service DNS names:

```powershell
$env:MONITORING_MCP_GRAFANA_URL = "http://grafana:3000"
$env:MONITORING_MCP_PROMETHEUS_URL = "http://prometheus:9090"
$env:MONITORING_MCP_LOKI_URL = "http://loki:3100"
$env:MONITORING_MCP_ALERTMANAGER_URL = "http://alertmanager:9093"
```

## Windows path mounts

Podman may need an explicit volume path mapping into the machine. If `./data` fails to mount, use an absolute path under a shared drive configured for `podman machine`.

## Not in scope

Container *lifecycle* control (start/stop pods) belongs to **podman-mcp**, not this repo.
