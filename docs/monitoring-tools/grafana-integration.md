# Grafana Integration Guide

This guide covers the comprehensive Grafana integration capabilities of the Monitoring MCP server.

## Overview

The Monitoring MCP provides full Grafana API integration through the `grafana_management` portmanteau tool, enabling AI-powered dashboard management, panel operations, and data source interactions.

## Authentication

### API Key Authentication (Recommended)

```bash
# Set environment variable
export MONITORING_MCP_GRAFANA_API_KEY="your_grafana_api_key_here"

# Or in .env file
MONITORING_MCP_GRAFANA_API_KEY=your_grafana_api_key_here
```

### Username/Password Authentication

```bash
# Set environment variables
export MONITORING_MCP_GRAFANA_USERNAME="admin"
export MONITORING_MCP_GRAFANA_PASSWORD="your_password_here"
```

## Dashboard Management

### Listing Dashboards

```python
# List all dashboards
result = await grafana_management(operation="list_dashboards")
print(f"Found {result['count']} dashboards")

# With conversational summary
print(result["conversational_summary"])
# Output: "I found 15 dashboards in your Grafana instance. You have quite a comprehensive monitoring setup!"
```

### Creating Dashboards

```python
# Create a new dashboard
dashboard_data = {
    "title": "API Performance Overview",
    "tags": ["api", "performance", "monitoring"],
    "timezone": "browser",
    "panels": [
        {
            "title": "Request Rate",
            "type": "graph",
            "targets": [
                {
                    "expr": "rate(http_requests_total[5m])",
                    "legendFormat": "{{method}} {{status}}"
                }
            ]
        }
    ],
    "time": {
        "from": "now-1h",
        "to": "now"
    }
}

result = await grafana_management(
    operation="create_dashboard",
    dashboard_data=dashboard_data
)

print(f"Dashboard created with UID: {result['data']['uid']}")
print(result["conversational_summary"])
```

### Dashboard Analysis

```python
# Analyze dashboard for optimization opportunities
result = await grafana_management(
    operation="analyze_dashboard",
    dashboard_uid="your_dashboard_uid"
)

print(f"Dashboard score: {result['analysis']['overall_score']}/10")
print(f"Recommendations: {len(result['ai_insights']['recommendations'])}")

# AI insights
for insight in result["ai_insights"]["recommendations"]:
    print(f"• {insight}")
```

## Data Source Operations

### Listing Data Sources

```python
# Get all configured data sources
result = await grafana_management(operation="list_datasources")

print(f"Found {result['count']} data sources:")
for ds in result["data"]:
    print(f"• {ds['name']} ({ds['type']}) - {'✓' if ds.get('isDefault') else ''}")
```

### Querying Data Sources

```python
# Query a data source directly
result = await grafana_management(
    operation="query_datasource",
    datasource_id=1,  # Prometheus datasource ID
    queries=[
        {
            "expr": "up",
            "format": "time_series",
            "intervalFactor": 1
        }
    ],
    time_range={
        "from": "now-1h",
        "to": "now"
    }
)

print(f"Query executed successfully: {result['success']}")
print(f"Result count: {len(result['data']['results'])}")
```

## Panel Operations

### Adding Panels to Dashboards

```python
# Add a new panel (placeholder for future implementation)
result = await grafana_management(
    operation="create_panel",
    dashboard_uid="your_dashboard_uid",
    panel_data={
        "title": "Error Rate",
        "type": "stat",
        "targets": [
            {
                "expr": "rate(http_requests_total{status=~'5..'}[$__rate_interval])",
                "refId": "A"
            }
        ]
    }
)

# Note: Panel operations are planned for future versions
print(result["conversational_summary"])
```

## Alert Management

### Creating Alert Rules

```python
# Create alert rules (placeholder for future implementation)
alert_rule = {
    "name": "High Error Rate",
    "condition": "C",
    "noDataState": "NoValue",
    "executionErrorState": "Alerting",
    "for": "5m",
    "frequency": "1m",
    "handler": 1,
    "rules": [
        {
            "expr": "rate(http_requests_total{status=~'5..'}[$__rate_interval]) > 0.1",
            "labels": {"severity": "warning"},
            "annotations": {
                "summary": "High error rate detected",
                "description": "Error rate is {{ $value }} which is above the threshold"
            }
        }
    ]
}

result = await grafana_management(
    operation="create_alert",
    alert_rule=alert_rule
)

print(result["conversational_summary"])
```

## Advanced Features

### Dashboard Search and Filtering

```python
# Search dashboards by title or tags
result = await grafana_management(
    operation="search_dashboards",
    search_query="api performance"
)

print(f"Found {result['count']} dashboards matching 'api performance'")
```

### Export and Import

```python
# Export dashboard as JSON
result = await grafana_management(
    operation="export_dashboard",
    dashboard_uid="your_dashboard_uid"
)

# Save to file
import json
with open("dashboard_backup.json", "w") as f:
    json.dump(result["data"], f, indent=2)

print("Dashboard exported successfully")
```

## Best Practices

### Dashboard Organization

1. **Use Consistent Naming**: Follow a naming convention like `[System]-[Component]-[Purpose]`
2. **Tag Strategically**: Use tags for environment, team, and component identification
3. **Folder Structure**: Organize dashboards into folders by team or system
4. **Template Variables**: Use variables for dynamic filtering and reusability

### Performance Optimization

1. **Query Efficiency**: Use appropriate time ranges and intervals
2. **Panel Limits**: Don't overload dashboards with too many panels
3. **Data Source Selection**: Choose the right data source for each query type
4. **Caching**: Leverage Grafana's query caching where appropriate

### Security Considerations

1. **API Key Management**: Rotate API keys regularly
2. **Permission Levels**: Use appropriate permission levels for different users
3. **Dashboard Permissions**: Set appropriate viewing and editing permissions
4. **Audit Logging**: Monitor dashboard access and changes

## Troubleshooting

### Common Issues

#### Authentication Errors
```python
# Check authentication setup
result = await grafana_management(operation="list_dashboards")
if not result["success"]:
    print(f"Authentication issue: {result['error']}")
    print("Check your GRAFANA_API_KEY or username/password settings")
```

#### Connection Issues
```python
# Test connectivity
result = await monitoring_status(operation="connectivity_test")
grafana_status = result["connectivity"]["grafana"]
if grafana_status["status"] != "connected":
    print(f"Grafana connection failed: {grafana_status['error']}")
    print("Verify Grafana URL and network connectivity")
```

#### Permission Issues
```python
# Check permissions on specific dashboard
result = await grafana_management(
    operation="get_dashboard_permissions",
    dashboard_uid="your_dashboard_uid"
)
print(f"Permissions: {result['data']}")
```

### Error Recovery

1. **Retry Logic**: The MCP automatically retries failed requests
2. **Graceful Degradation**: Operations continue even if some components fail
3. **Detailed Logging**: Check logs for detailed error information
4. **Health Checks**: Use status monitoring to identify issues proactively

## Integration Examples

### CI/CD Pipeline Integration

```python
# Create deployment dashboard after successful deployment
async def create_deployment_dashboard(version, environment):
    dashboard_data = {
        "title": f"Deployment {version} - {environment}",
        "tags": ["deployment", environment, version],
        "panels": [
            # Add relevant panels for deployment monitoring
        ]
    }

    result = await grafana_management(
        operation="create_dashboard",
        dashboard_data=dashboard_data,
        folder_name=f"Deployments/{environment}"
    )

    return result["data"]["url"]
```

### Automated Alert Setup

```python
# Set up alerts for new services
async def setup_service_alerts(service_name):
    alerts = [
        {
            "name": f"{service_name} - High Error Rate",
            "query": f'rate(http_requests_total{{service="{service_name}", status=~"5.."}}[5m]) > 0.05'
        },
        {
            "name": f"{service_name} - High Latency",
            "query": f'histogram_quantile(0.95, rate(http_request_duration_seconds{{service="{service_name}"}}[5m])) > 2'
        }
    ]

    for alert in alerts:
        await grafana_management(
            operation="create_alert",
            alert_rule=alert
        )
```

## API Reference

### Tool Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `operation` | string | Yes | Grafana operation to perform |
| `dashboard_uid` | string | Sometimes | Dashboard unique identifier |
| `dashboard_title` | string | Sometimes | Dashboard title |
| `dashboard_data` | dict | Sometimes | Dashboard JSON configuration |
| `folder_id` | int | No | Folder ID for organization |
| `search_query` | string | No | Search query for filtering |
| `datasource_id` | int | Sometimes | Data source identifier |
| `queries` | list | Sometimes | Query objects for execution |
| `time_range` | dict | Sometimes | Time range specification |
| `panel_data` | dict | Sometimes | Panel configuration |
| `alert_rule` | dict | Sometimes | Alert rule configuration |

### Response Structure

```python
{
    "success": bool,           # Operation success status
    "operation": string,       # Operation performed
    "data": dict,             # Operation-specific data
    "conversational_summary": string,  # Natural language summary
    "ai_insights": {          # AI-powered recommendations
        "recommendations": list,
        "alerting_opportunities": list,
        "optimization_suggestions": list
    }
}
```

## Related Documentation

- [Prometheus Integration Guide](prometheus-integration.md)
- [Loki Integration Guide](loki-integration.md)
- [Cross-System Correlation](correlation-analysis.md)
- [API Reference](../api/index.md)
- [Troubleshooting Guide](../troubleshooting.md)