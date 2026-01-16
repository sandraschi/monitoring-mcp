# Monitoring MCP Server

[![CI](https://github.com/sandraschi/monitoring-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/sandraschi/monitoring-mcp/actions)
[![codecov](https://codecov.io/gh/sandraschi/monitoring-mcp/branch/main/graph/badge.svg)](https://codecov.io/gh/sandraschi/monitoring-mcp)
[![PyPI version](https://badge.fury.io/py/monitoring-mcp.svg)](https://pypi.org/project/monitoring-mcp/)
[![PyPI downloads](https://img.shields.io/pypi/dm/monitoring-mcp)](https://pypi.org/project/monitoring-mcp/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![FastMCP](https://img.shields.io/badge/FastMCP-2.14.3+-blue.svg)](https://github.com/jlowin/fastmcp)
[![Grafana](https://img.shields.io/badge/Grafana-Supported-orange.svg)](https://grafana.com)
[![Prometheus](https://img.shields.io/badge/Prometheus-Supported-orange.svg)](https://prometheus.io)
[![Loki](https://img.shields.io/badge/Loki-Supported-green.svg)](https://grafana.com/oss/loki/)

[![GitHub Repo stars](https://img.shields.io/github/stars/sandraschi/monitoring-mcp?style=social)](https://github.com/sandraschi/monitoring-mcp)
[![GitHub last commit](https://img.shields.io/github/last-commit/sandraschi/monitoring-mcp)](https://github.com/sandraschi/monitoring-mcp)
[![GitHub issues](https://img.shields.io/github/issues/sandraschi/monitoring-mcp)](https://github.com/sandraschi/monitoring-mcp/issues)

[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-purple.svg)](https://modelcontextprotocol.io/)
[![Status](https://img.shields.io/badge/status-active-success.svg)](https://github.com/sandraschi/monitoring-mcp/pulse)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

*A comprehensive FastMCP 2.14.3-powered monitoring server providing intelligent operations across Grafana, Prometheus, and Loki ecosystems with conversational AI assistance for DevOps workflows.*

## 🚀 Features

### **FastMCP 2.14.3 Integration**
- ✅ **Conversational Tool Returns** - AI-friendly responses with actionable insights
- ✅ **Sampling Capabilities** - Intelligent data sampling for large result sets
- ✅ **Persistent Storage** - DiskStore backend for configuration and state
- ✅ **Production-Ready** - Built for high-performance monitoring operations

### **Comprehensive Monitoring Tools**

#### 🔍 **Grafana Management** (`grafana_management`)
- **Dashboard Operations**: List, create, update, delete, and analyze dashboards
- **Data Source Queries**: Execute queries against configured data sources
- **Panel Management**: Add and modify dashboard panels
- **Alert Configuration**: Set up alerting rules for dashboard metrics
- **AI-Powered Analysis**: Intelligent dashboard optimization suggestions

#### 📊 **Prometheus Monitoring** (`prometheus_monitoring`)
- **Metric Queries**: Execute PromQL queries with intelligent sampling
- **Range Queries**: Time-series analysis with automatic optimization
- **Target Health**: Monitor scrape target status and connectivity
- **Alert Management**: List active alerts and manage alert rules
- **Performance Analysis**: Query optimization and bottleneck detection

#### 📝 **Loki Logging** (`loki_logging`)
- **Log Queries**: Execute LogQL queries with pattern recognition
- **Real-time Tailing**: Stream live logs with configurable limits
- **Anomaly Detection**: AI-powered log pattern analysis
- **Error Correlation**: Link error logs with system events
- **Request Tracing**: Follow request flows through log streams

#### 🔗 **Cross-System Correlation** (`cross_system_correlation`)
- **Incident Analysis**: Correlate metrics, logs, and traces for root cause analysis
- **Performance Correlation**: Link performance metrics with system events
- **Error Correlation**: Connect error patterns across systems
- **Health Assessment**: Comprehensive system health scoring
- **Predictive Insights**: AI-powered trend analysis and recommendations

#### 🏥 **Status & Health Monitoring** (`monitoring_status`)
- **System Health Checks**: Comprehensive health assessment across all systems
- **Connectivity Testing**: Verify connections to all monitoring components
- **Configuration Validation**: Validate system configurations and settings
- **Data Flow Monitoring**: Check data flow between monitoring systems
- **Alert Status**: Monitor alerting system health and active alerts

### **AI-Powered Intelligence**
- **Conversational Responses**: Natural language summaries and actionable insights
- **Intelligent Sampling**: Automatic data reduction for large datasets
- **Root Cause Analysis**: AI-assisted incident investigation
- **Optimization Recommendations**: Performance and configuration suggestions
- **Pattern Recognition**: Automated anomaly detection and trend analysis

### **Enterprise Features**
- **Persistent Configuration**: Encrypted storage with platform-aware paths
- **Rate Limiting**: Intelligent request throttling and error handling
- **Structured Logging**: JSON-formatted logs with rich context
- **Error Recovery**: Graceful degradation and automatic retry logic
- **Security**: Authentication support with API key management

## 🎯 Usage Examples

### Grafana Dashboard Management

```python
# List all dashboards
await grafana_management(operation="list_dashboards")

# Create a new dashboard
await grafana_management(
    operation="create_dashboard",
    dashboard_data={
        "title": "System Overview",
        "tags": ["system", "overview"],
        "panels": [...]
    }
)

# Analyze dashboard for optimization
await grafana_management(
    operation="analyze_dashboard",
    dashboard_uid="abc123"
)
```

### Prometheus Metrics Analysis

```python
# Query system CPU usage
await prometheus_monitoring(
    operation="query_metrics",
    query="100 - (avg by(instance) (irate(node_cpu_seconds_total{mode='idle'}[5m])) * 100)"
)

# Analyze performance bottlenecks
await prometheus_monitoring(
    operation="analyze_metrics",
    query="rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])",
    analysis_context={"service": "web-api"}
)
```

### Loki Log Analysis

```python
# Search for error patterns
await loki_logging(
    operation="search_errors",
    query='{job="web-api"} |= "ERROR" or "Exception"',
    start_time="now-1h",
    end_time="now"
)

# Analyze log patterns
await loki_logging(
    operation="analyze_logs",
    query='{job=~".*"}',
    analysis_context={"focus": "error_patterns"}
)
```

### Cross-System Incident Analysis

```python
# Correlate incident data
await cross_system_correlation(
    operation="correlate_incident",
    incident_description="API response times spiked",
    time_range={"start": "now-2h", "end": "now"}
)

# Find root cause
await cross_system_correlation(
    operation="find_root_cause",
    metric_query="rate(http_requests_total{status=~"5.."}[5m])",
    log_query='{job="web-api"} |= "ERROR"'
)
```

### Health Monitoring

```python
# Check overall system health
await monitoring_status(
    operation="system_health",
    detailed_check=True
)

# Test connectivity
await monitoring_status(
    operation="connectivity_test",
    component_filter=["grafana", "prometheus", "loki"]
)
```

## 📦 Installation

### Prerequisites
- Python 3.10+
- Access to Grafana, Prometheus, and Loki instances
- FastMCP 2.14.3+ (installed automatically)

### From PyPI (Recommended)

```bash
pip install monitoring-mcp
```

### From Source

```bash
git clone https://github.com/sandraschi/monitoring-mcp.git
cd monitoring-mcp
pip install -e .[dev]
```

### Configuration

Create a `.env` file or set environment variables:

```bash
# Monitoring endpoints
MONITORING_MCP_GRAFANA_URL=http://localhost:3000
MONITORING_MCP_PROMETHEUS_URL=http://localhost:9090
MONITORING_MCP_LOKI_URL=http://localhost:3100

# Authentication (optional)
MONITORING_MCP_GRAFANA_API_KEY=your_grafana_api_key
MONITORING_MCP_GRAFANA_USERNAME=your_username
MONITORING_MCP_GRAFANA_PASSWORD=your_password

# Performance settings
MONITORING_MCP_REQUEST_TIMEOUT=30
MONITORING_MCP_MAX_CONCURRENT_REQUESTS=10
MONITORING_MCP_MAX_RESULTS_LIMIT=1000

# Sampling configuration
MONITORING_MCP_ENABLE_SAMPLING=true
MONITORING_MCP_SAMPLING_THRESHOLD=10000
MONITORING_MCP_SAMPLING_RATE=0.1
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONITORING_MCP_GRAFANA_URL` | Grafana server URL | `http://localhost:3000` |
| `MONITORING_MCP_PROMETHEUS_URL` | Prometheus server URL | `http://localhost:9090` |
| `MONITORING_MCP_LOKI_URL` | Loki server URL | `http://localhost:3100` |
| `MONITORING_MCP_REQUEST_TIMEOUT` | Request timeout (seconds) | `30` |
| `MONITORING_MCP_MAX_RESULTS_LIMIT` | Maximum results per query | `1000` |
| `MONITORING_MCP_ENABLE_SAMPLING` | Enable intelligent sampling | `true` |

### Authentication

#### Grafana Authentication
- **API Key** (recommended): Set `MONITORING_MCP_GRAFANA_API_KEY`
- **Username/Password**: Set both `MONITORING_MCP_GRAFANA_USERNAME` and `MONITORING_MCP_GRAFANA_PASSWORD`

#### Prometheus & Loki
- Currently use direct HTTP access (no authentication required for local setups)
- For production deployments, configure reverse proxies with authentication

## 🚀 Quick Start

### 1. Start the Server

```bash
# Using the installed package
monitoring-mcp

# Or directly with Python
python -m monitoring_mcp
```

### 2. Configure Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "monitoring": {
      "command": "python",
      "args": ["-m", "monitoring_mcp"],
      "env": {
        "MONITORING_MCP_GRAFANA_URL": "http://your-grafana:3000",
        "MONITORING_MCP_PROMETHEUS_URL": "http://your-prometheus:9090",
        "MONITORING_MCP_LOKI_URL": "http://your-loki:3100"
      }
    }
  }
}
```

### 3. Test Connection

```python
# Check system health
result = await monitoring_status(operation="system_health")
print(f"System status: {result['health_status']['overall_status']}")

# Query a simple metric
result = await prometheus_monitoring(
    operation="query_metrics",
    query="up"
)
print(f"Found {result['result_count']} metric series")
```

## 📊 Monitoring Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Monitoring MCP Server                   │
│  ┌─────────────────────────────────────────────────┐    │
│  │             Portmanteau Tools                    │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │    │
│  │  │  Grafana    │ │ Prometheus  │ │    Loki     │ │    │
│  │  │Management   │ │ Monitoring  │ │   Logging   │ │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────┼───────────────────────────────────────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
┌───────▼─────┐ ┌─▼──────┐ ┌▼────────┐
│   Grafana   │ │Promethe│ │  Loki   │
│ Dashboards  │ │ us Met- │ │   Logs  │
│   & Panels  │ │ rics &  │ │Analysis │
│             │ │ Alerts  │ │         │
└─────────────┘ └────────┘ └─────────┘
                  ▲
                  │
     ┌────────────┼────────────┐
     │   Cross-System          │
     │   Correlation Engine    │
     │                         │
     │ • Incident Analysis     │
     │ • Root Cause Detection  │
     │ • Performance Insights  │
     │ • Health Assessment     │
     └─────────────────────────┘
```

## 🔍 Tool Reference

### Grafana Management (`grafana_management`)

| Operation | Description |
|-----------|-------------|
| `list_dashboards` | List all dashboards with metadata |
| `get_dashboard` | Retrieve specific dashboard |
| `create_dashboard` | Create new dashboard |
| `update_dashboard` | Modify existing dashboard |
| `delete_dashboard` | Remove dashboard |
| `search_dashboards` | Search dashboards by criteria |
| `list_datasources` | List configured data sources |
| `query_datasource` | Execute queries against data sources |
| `analyze_dashboard` | AI-powered dashboard analysis |

### Prometheus Monitoring (`prometheus_monitoring`)

| Operation | Description |
|-----------|-------------|
| `query_metrics` | Execute instant PromQL queries |
| `query_range` | Execute range PromQL queries |
| `list_targets` | List scrape targets and status |
| `get_target_health` | Check specific target health |
| `list_rules` | List alerting and recording rules |
| `list_alerts` | List active alerts |
| `analyze_metrics` | AI-powered metrics analysis |
| `optimize_queries` | Query optimization suggestions |

### Loki Logging (`loki_logging`)

| Operation | Description |
|-----------|-------------|
| `query_logs` | Execute instant LogQL queries |
| `query_range` | Execute range LogQL queries |
| `tail_logs` | Stream live logs |
| `analyze_logs` | AI-powered log pattern analysis |
| `detect_anomalies` | Identify unusual log patterns |
| `search_errors` | Find error messages and exceptions |
| `trace_requests` | Follow request traces |
| `get_labels` | List available log labels |

### Cross-System Correlation (`cross_system_correlation`)

| Operation | Description |
|-----------|-------------|
| `correlate_incident` | Analyze incident across systems |
| `find_root_cause` | AI-powered root cause analysis |
| `performance_correlation` | Link performance with events |
| `error_correlation` | Connect error patterns |
| `health_assessment` | Comprehensive system health |
| `service_dependency_map` | Map service relationships |

### Status Monitoring (`monitoring_status`)

| Operation | Description |
|-----------|-------------|
| `system_health` | Overall system health check |
| `connectivity_test` | Test system connectivity |
| `configuration_validation` | Validate configurations |
| `performance_metrics` | Monitor system performance |
| `data_flow_status` | Check data flow health |
| `alert_status` | Monitor alerting systems |

## 🔧 Development

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Type checking: mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](http://mypy-lang.org/)

[![pytest](https://img.shields.io/badge/testing-pytest-green.svg)](https://github.com/pytest-dev/pytest)
[![asyncio](https://img.shields.io/badge/asyncio-compatible-blue.svg)](https://docs.python.org/3/library/asyncio.html)
[![FastAPI](https://img.shields.io/badge/framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)

### Setup Development Environment

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run linting
ruff check .

# Format code
ruff format .

# Type checking
mypy src/
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=monitoring_mcp --cov-report=html

# Run specific test category
pytest tests/unit/ -v
pytest tests/integration/ -v
```

### Docker Development

```bash
# Build development image
docker build -t monitoring-mcp:dev -f Dockerfile.dev .

# Run with hot reload
docker run -p 8000:8000 -v $(pwd):/app monitoring-mcp:dev
```

## 📚 Documentation

### Guides and Documentation
- **[API Reference](docs/api/)** - Complete API documentation
- **[Grafana Integration](docs/grafana/)** - Grafana-specific guides
- **[Prometheus Queries](docs/prometheus/)** - PromQL best practices
- **[Loki Queries](docs/loki/)** - LogQL patterns and examples
- **[Correlation Analysis](docs/correlation/)** - Cross-system analysis techniques
- **[Troubleshooting](docs/troubleshooting/)** - Common issues and solutions

### Architecture Documentation
- **[System Architecture](docs/architecture/)** - System design and components
- **[Performance Guide](docs/performance/)** - Optimization and scaling
- **[Security](docs/security/)** - Security considerations and best practices
- **[Deployment](docs/deployment/)** - Production deployment guides

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with comprehensive tests
4. Run the full test suite: `make test-all`
5. Update documentation as needed
6. Submit a pull request

### Code Standards
- **FastMCP 2.14.3+**: Use latest features and patterns
- **Type Hints**: Full type coverage required
- **Async First**: All operations should be async where appropriate
- **Conversational**: Tool responses should be AI-friendly
- **Documentation**: Comprehensive docstrings and examples

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastMCP Team** - For the excellent MCP framework
- **Grafana Labs** - For Grafana, Prometheus, and Loki
- **OpenTelemetry Community** - For observability standards
- **Pydantic Team** - For powerful data validation

---

**Built with ❤️ using FastMCP 2.14.3 for intelligent monitoring operations**