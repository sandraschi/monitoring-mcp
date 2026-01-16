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

## 💬 Conversational Usage Examples

These examples show how users interact with the Monitoring MCP server through natural language conversations, as you would in Claude Desktop or other MCP-enabled applications.

### **System Health Check Conversation**

**User:** "Check the overall health of my monitoring system"

**Monitoring MCP Response:**
> "I found your monitoring system is mostly healthy! ✅
>
> **System Status: Degraded** (3 out of 4 components healthy)
>
> **Grafana**: ✅ Healthy (12 dashboards, 3 data sources configured)
> **Prometheus**: ✅ Healthy (247 targets, 98% up)
> **Loki**: ❌ Unhealthy (Connection timeout - check if Loki service is running)
> **Overall**: ⚠️ 1 issue needs attention
>
> **Recommendation:** Start the Loki service and run connectivity tests to verify the fix."

---

### **Incident Investigation Conversation**

**User:** "Our API response times spiked at 3:15 PM today. Can you help me investigate what happened?"

**Monitoring MCP Response:**
> "I'll investigate the API response time spike at 3:15 PM. Let me correlate metrics, logs, and system events.
>
> **Timeline Analysis:**
> - **3:15 PM**: API latency jumped from 45ms to 890ms
> - **Metrics**: Memory usage spiked to 92% on web-01 server
> - **Logs**: Multiple "GC overhead limit exceeded" errors in web-api service
>
> **Root Cause Identified:** 🏆
> Memory pressure triggered garbage collection storms, causing response delays.
>
> **Evidence:**
> - Memory usage: 92% (threshold: 80%)
> - GC pause time: 450ms (normal: <50ms)
> - Error logs: 47 "GC overhead" exceptions in 5-minute window
>
> **Recommendations:**
> 1. Scale up web-01 instance (currently t3.medium)
> 2. Tune JVM GC settings (-XX:+UseG1GC -XX:MaxGCPauseMillis=100)
> 3. Add memory monitoring alerts at 75% threshold"

---

### **Performance Analysis Conversation**

**User:** "Why is our database query performance degraded this week?"

**Monitoring MCP Response:**
> "I've analyzed your database performance over the past week. Here's what I found:
>
> **Performance Trend:** 📈 23% degradation in query response times
>
> **Key Metrics:**
> - Average query time: 450ms (up from 320ms)
> - Slow queries (>1s): 15% of total (up from 8%)
> - Connection pool utilization: 89% (up from 72%)
>
> **Correlated Events:**
> - **Tuesday 2:30 PM**: Database restart (maintenance window)
> - **Wednesday**: Index rebuild completed (expected performance dip)
> - **Friday**: Connection pool exhausted multiple times
>
> **Performance Insights:**
> 1. **Connection Pool Contention**: 89% utilization suggests pool size needs increasing
> 2. **Index Fragmentation**: Recent rebuild shows 40% improvement potential
> 3. **Memory Pressure**: Buffer cache hit ratio dropped to 87%
>
> **Action Items:**
> - Increase connection pool size by 25%
> - Schedule regular index maintenance
> - Add monitoring for connection pool utilization >80%"

---

### **Log Analysis Conversation**

**User:** "I'm seeing authentication failures in my logs. Can you analyze the patterns?"

**Monitoring MCP Response:**
> "I've analyzed your authentication failure patterns across the last 24 hours:
>
> **Summary:** 🔍 1,247 failed login attempts detected
>
> **Top Failure Reasons:**
> - **Invalid Credentials**: 68% (851 attempts) - normal user errors
> - **Account Locked**: 22% (275 attempts) - brute force protection
> - **Expired Tokens**: 8% (100 attempts) - session timeouts
> - **IP Blocked**: 2% (21 attempts) - security measures
>
> **Suspicious Patterns Detected:** ⚠️
> - **IP 192.168.1.100**: 45 consecutive failures in 10 minutes
> - **User 'admin'**: Targeted by 89 different IPs
> - **Time Pattern**: Peak failures between 2-4 AM UTC
>
> **Security Recommendations:**
> 1. Block IP 192.168.1.100 temporarily (brute force attempt)
> 2. Implement progressive delays on failed logins
> 3. Add geo-blocking for suspicious regions
> 4. Enable MFA for admin accounts"

---

### **Dashboard Creation Conversation**

**User:** "Create a dashboard showing our service health overview"

**Monitoring MCP Response:**
> "I'll create a comprehensive service health dashboard for you! 📊
>
> **Dashboard Created:** 'Service Health Overview'
> **UID:** svc-health-2024
>
> **Panels Included:**
>
> 1. **Service Status Grid** - Real-time health of all services
> 2. **Error Rate Trends** - 1h, 24h, 7d error rate graphs
> 3. **Response Time Distribution** - P50, P95, P99 latency metrics
> 4. **Resource Utilization** - CPU, Memory, Disk, Network usage
> 5. **Alert Summary** - Active alerts by severity
> 6. **Top Error Sources** - Services generating most errors
>
> **Data Sources Connected:**
> - ✅ Prometheus (metrics)
> - ✅ Loki (logs)
> - ✅ Grafana (visualization)
>
> **Auto-Refresh:** 30 seconds
> **Time Range:** Last 1 hour
>
> **Access:** Available at `/d/svc-health-2024/service-health-overview`
>
> The dashboard is now live and will help you monitor service health at a glance!"

---

### **Configuration Validation Conversation**

**User:** "Validate that my monitoring configuration is correct"

**Monitoring MCP Response:**
> "Let me check your monitoring system configuration across all components:
>
> **Configuration Validation Results:** ✅ **All Valid**
>
> **Grafana (http://grafana:3000):**
> - ✅ API connectivity confirmed
> - ✅ 3 data sources configured (Prometheus, Loki, TestData)
> - ✅ 12 dashboards available
> - ✅ Admin permissions verified
>
> **Prometheus (http://prometheus:9090):**
> - ✅ Query API responding
> - ✅ 247 scrape targets configured
> - ✅ 98% target health (243/247 up)
> - ✅ 45 alerting rules active
>
> **Loki (http://loki:3100):**
> - ✅ LogQL API functional
> - ✅ 8 distinct log streams
> - ✅ 2.3GB logs ingested (last 24h)
> - ✅ Retention policy: 30 days
>
> **Cross-System Integration:**
> - ✅ Grafana can query Prometheus data
> - ✅ Grafana can query Loki logs
> - ✅ Alert routing configured
> - ✅ Dashboard links functional
>
> **Recommendations:**
> 1. **4 unhealthy targets** in Prometheus need investigation
> 2. **Consider increasing retention** if you need longer log history
> 3. **Add more alerting rules** for critical services
>
> Your monitoring stack is properly configured and operational! 🎉"

---

## 🔧 API Usage Examples

For developers integrating directly with the MCP tools:

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
```

### Prometheus Metrics Analysis

```python
# Query system CPU usage
await prometheus_monitoring(
    operation="query_metrics",
    query="100 - (avg by(instance) (irate(node_cpu_seconds_total{mode='idle'}[5m])) * 100)"
)
```

### Loki Log Analysis

```python
# Search for error patterns
await loki_logging(
    operation="search_errors",
    query='{job="web-api"} |= "ERROR" or "Exception"'
)
```

### Cross-System Incident Analysis

```python
# Correlate incident data
await cross_system_correlation(
    operation="correlate_incident",
    incident_description="API response times spiked"
)
```

### Health Monitoring

```python
# Check overall system health
await monitoring_status(operation="system_health")
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