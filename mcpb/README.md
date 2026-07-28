# monitoring-mcp (MCPB Bundle)

FastMCP 3.4.4+ monitoring server for Grafana, Prometheus, Loki, and Alertmanager.

## Usage

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "monitoring-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "D:/Dev/repos/monitoring-mcp", "python", "-m", "monitoring_mcp"],
      "env": {
        "MONITORING_MCP_GRAFANA_URL": "http://localhost:3000",
        "MONITORING_MCP_PROMETHEUS_URL": "http://localhost:9090",
        "MONITORING_MCP_LOKI_URL": "http://localhost:3100",
        "MONITORING_MCP_ALERTMANAGER_URL": "http://localhost:9093"
      }
    }
  }
}
```

Or install the packaged `.mcpb` via Claude Desktop drag-and-drop.

## Tools

- `grafana_management`
- `prometheus_monitoring`
- `loki_logging`
- `cross_system_correlation`
- `monitoring_status`

Full operation list: [docs/TOOLS.md](../docs/TOOLS.md)

## Requirements

- Python 3.12+
- uv
