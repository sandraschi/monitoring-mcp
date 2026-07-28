# monitoring-mcp — User Guide

## Quick Start

monitoring-mcp provides unified access to your Grafana, Prometheus, and Loki monitoring infrastructure through natural language conversations. To get started, ensure your monitoring services are running and accessible, then configure the environment variables pointing to each service's HTTP API. Once configured, run a health check to verify connectivity to all backends, then explore your metrics, logs, and dashboards through any of the five portmanteau tools.

**Basic setup:**
1. Set GRAFANA_URL, GRAFANA_API_KEY, PROMETHEUS_URL, and LOKI_URL environment variables to match your infrastructure
2. Run `monitoring_status(operation="health")` to verify all connections are working
3. Run `prometheus_monitoring(operation="query", query="up")` to check your monitoring targets
4. Explore available dashboards: `grafana_management(operation="dashboards")`
5. Browse log labels: `loki_logging(operation="labels")`

**First commands to get oriented:**
```
monitoring_status(operation="health")
monitoring_status(operation="status")
prometheus_monitoring(operation="targets")
```

## Tutorials

### Tutorial 1: Infrastructure Health Dashboard

Create a comprehensive health dashboard that displays key metrics from your entire infrastructure. This is the first dashboard to create when setting up monitoring for a new environment.

**Steps:**
1. Start by checking what Prometheus targets are being scraped and their health status:
   `prometheus_monitoring(operation="targets")`
   This will show you all configured scrape targets, their current health, last scrape duration, and labels.

2. Query key system metrics to understand what data is being collected:
   `prometheus_monitoring(operation="query", query="up")`
   This returns all UP targets with their instance labels and current status (1 for up, 0 for down).

3. Check CPU idle time as a baseline metric:
   `prometheus_monitoring(operation="query_range", query="avg(node_cpu_seconds_total{mode='idle'}) by (instance)", start="2h ago", end="now", step="5m")`
   This provides a multi-hour trend of CPU idle time for each node.

4. Review existing Grafana dashboards to see what visualizations already exist:
   `grafana_management(operation="dashboards")`
   Returns all dashboards with their UIDs, folder paths, and last modified dates.

5. Create a new health dashboard with proper panels:
   `grafana_management(operation="dashboards", dashboard_json={"title": "Infrastructure Health", "panels": [{"title": "CPU Usage", "type": "graph", "targets": [{"expr": "100 - (avg by(instance)(rate(node_cpu_seconds_total{mode='idle'}[5m])) * 100)"}]}]})`

6. Configure Prometheus as a datasource if not already added:
   `grafana_management(operation="datasources", datasource_type="prometheus")`

**Expected outcome:** A functioning Grafana dashboard displaying real-time infrastructure health metrics with CPU, memory, and disk panels.

### Tutorial 2: Incident Investigation Walkthrough

Walk through a structured incident investigation using all three observability pillars. This pattern helps identify root causes by correlating metrics, logs, and alert data.

**Steps:**
1. Detect anomalies by reviewing current firing alerts:
   `prometheus_monitoring(operation="alerts")`
   Shows all alert rules and their current state (firing, pending, inactive).

2. Investigate the suspicious time period with detailed metrics:
   `prometheus_monitoring(operation="query_range", query="rate(http_requests_total{status='5xx'}[5m])", start="30m ago", end="now", step="30s")`
   This provides a high-resolution view of error rates over the last 30 minutes.

3. Pull related logs from the affected services to find error messages:
   `loki_logging(operation="query", query='{service="api"} |= "error"', start="30m ago")`
   Returns all log entries containing "error" from the API service in the last 30 minutes.

4. Cross-correlate metrics and logs to identify temporal relationships:
   `cross_system_correlation(operation="metrics_logs", time_range="30m", sources=["prometheus", "loki"])`
   Automatically links metric anomalies with corresponding log entries by timestamp proximity.

5. Run a comprehensive correlation analysis across all data sources:
   `cross_system_correlation(operation="analyze", time_range="1h", sources=["prometheus", "loki", "grafana"])`
   Builds evidence chains showing the temporal sequence of events leading to the incident.

6. Document findings and create a dashboard snapshot for the postmortem:
   `grafana_management(operation="snapshot", dashboard_uid="incident-dashboard")`

**Expected outcome:** Root cause identification with supporting evidence chains linking metric anomalies, log patterns, and alert firings into a coherent incident timeline.

### Tutorial 3: Proactive Alert Configuration

Set up intelligent alerting that combines metric thresholds with log patterns to reduce false positives and improve detection accuracy.

**Steps:**
1. Analyze current alert rules to identify gaps and opportunities:
   `prometheus_monitoring(operation="rules")`
   Lists all recording and alerting rules with their expressions and evaluation intervals.

2. Explore Loki log labels to understand available log streams:
   `loki_logging(operation="labels")`
   Returns all label names across all log streams.

3. Create a log-based alert that triggers when error rates exceed thresholds:
   `loki_logging(operation="alerts", query='rate({service="api"} |~ "error|exception"[5m]) > 0.1')`
   This creates an alert that fires when the rate of error/exception log lines exceeds 0.1 per second.

4. Monitor the newly created alerts:
   `prometheus_monitoring(operation="alerts")`
   Verify the alert rules are properly configured and not immediately firing.

5. Correlate alert patterns across all systems over a longer window:
   `cross_system_correlation(operation="alerts", time_range="24h", sources=["prometheus", "grafana"])`
   Identifies which alerts tend to fire together and suggests consolidation opportunities.

**Expected outcome:** A set of intelligent alert rules combining metric thresholds with log patterns for higher signal-to-noise ratio and reduced operational burden.

### Tutorial 4: Performance Analysis Report

Generate a comprehensive performance analysis for a specific service, combining metrics, logs, and correlation data into a structured report.

**Steps:**
1. Query service performance metrics over the last 24 hours:
   `prometheus_monitoring(operation="query_range", query="histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))", start="24h ago", end="now", step="5m")`
   Shows P99 latency trends for HTTP requests over the full day.

2. Check request volume and error rates in parallel:
   `prometheus_monitoring(operation="query_range", query="rate(http_requests_total{service='api',status='5xx'}[5m])", start="24h ago", end="now", step="5m")`
   Provides error rate trends to identify periods of elevated failures.

3. Pull relevant logs for the slowest requests to understand root causes:
   `loki_logging(operation="query", query='{service="api"} | json | duration_seconds > 2', start="24h ago")`
   Extracts all requests that took longer than 2 seconds with their full log context.

4. Correlate performance metrics with infrastructure health:
   `cross_system_correlation(operation="analyze", time_range="24h", sources=["prometheus", "loki"])`
   Links performance degradation periods with infrastructure events for root cause analysis.

5. Create a dedicated performance dashboard to monitor ongoing trends:
   `grafana_management(operation="dashboards", dashboard_json={"title": "API Performance", "panels": [{"title": "Latency P99", "type": "graph"}, {"title": "Error Rate", "type": "graph"}, {"title": "Request Volume", "type": "graph"}]})`

**Expected outcome:** A structured performance report with metric trends, log evidence, and a dedicated visualization dashboard for ongoing monitoring.

### Tutorial 5: Multi-Service Dependency Mapping

Map dependencies between services using network metrics and log-based service-to-service communication patterns.

**Steps:**
1. Query network metrics to understand inter-service traffic:
   `prometheus_monitoring(operation="query", query="rate(node_network_receive_bytes_total{device='eth0'}[5m])")`
   Shows current network receive rates across all services.

2. Check service-to-service communication in logs:
   `loki_logging(operation="query", query='{app="frontend"} |= "backend"', start="6h ago")`
   Finds all log entries where the frontend service references backend communication.

3. Correlate latency patterns between dependent services:
   `cross_system_correlation(operation="metrics_logs", time_range="6h", sources=["prometheus", "loki"])`
   Identifies temporal relationships in latency between upstream and downstream services.

4. Organize and explore Grafana folders for dependency visualization:
   `grafana_management(operation="folders")`
   `grafana_management(operation="search", search_query="dependency")`

**Expected outcome:** A mapping of service dependencies with performance baselines for each connection path, identifying potential bottlenecks and single points of failure.

### Tutorial 6: Capacity Planning Analysis

Analyze resource usage trends over extended periods to plan infrastructure capacity and predict future needs.

**Steps:**
1. Query CPU and memory trends over a full week:
   `prometheus_monitoring(operation="query_range", query="avg(node_cpu_seconds_total{mode='idle'}) by (instance)", start="7d ago", end="now", step="1h")`
   Provides hourly CPU idle trends across all nodes for a full week.

2. Check disk usage growth rates:
   `prometheus_monitoring(operation="query_range", query="node_filesystem_avail_bytes{mountpoint='/'} / node_filesystem_size_bytes{mountpoint='/'} * 100", start="7d ago", end="now", step="6h")`
   Shows disk usage percentage trends at 6-hour intervals over 7 days.

3. Analyze log volume growth to plan Loki storage:
   `loki_logging(operation="stats", query='rate({job="nginx"}[1h])')`
   Returns hourly log ingestion rates for the nginx service.

4. Get a comprehensive capacity status overview:
   `monitoring_status(operation="status", component="capacity")`
   Aggregates all capacity-related metrics into a single status report.

5. Create a capacity planning dashboard for ongoing tracking:
   `grafana_management(operation="dashboards", dashboard_json={"title": "Capacity Planning", "panels": [{"title": "CPU Trends"}, {"title": "Disk Usage"}, {"title": "Memory Trends"}, {"title": "Log Volume Growth"}]})`

**Expected outcome:** Resource usage trends with growth projections, capacity recommendations, and a monitoring dashboard for ongoing capacity tracking.

### Tutorial 7: Log Forensics and Security Audit

Perform detailed log forensics for security incident investigation or compliance auditing across your infrastructure.

**Steps:**
1. Explore available log labels to understand your log data structure:
   `loki_logging(operation="labels")`
   Returns all label names that can be used for log filtering.

2. Query authentication-related logs:
   `loki_logging(operation="query", query='{job="auth"} |= "login"', start="48h ago")`
   Retrieves all log entries containing "login" from the authentication service.

3. Search for failed access attempts over an extended period:
   `loki_logging(operation="query", query='{job="auth"} |= "FAILED"', start="7d ago", limit=500)`
   Returns up to 500 failed authentication events from the last 7 days.

4. Cross-reference failed logins with system metrics for anomaly detection:
   `cross_system_correlation(operation="anomalies", time_range="7d", sources=["prometheus", "loki"])`
   Identifies unusual patterns in failed login rates correlated with system resource changes.

5. Create automated alert rules for suspicious activity patterns:
   `loki_logging(operation="alerts", query='rate({job="auth"} |= "FAILED"[15m]) > 10')`
   Sets up an alert that fires when the rate of failed authentication exceeds 10 per 15 minutes.

**Expected outcome:** A detailed forensic timeline of security events with automated alert rules for ongoing threat detection.

### Tutorial 8: Dashboards Lifecycle Management

Manage the full lifecycle of Grafana dashboards from creation through updates, organization, and sharing.

**Steps:**
1. List all existing dashboards to understand current state:
   `grafana_management(operation="dashboards")`
   Returns complete dashboard inventory with metadata.

2. Search for specific dashboards by keyword:
   `grafana_management(operation="search", search_query="production")`
   Finds all dashboards related to production environments.

3. Create shared snapshots for collaboration:
   `grafana_management(operation="snapshot", dashboard_uid="existing-dashboard")`
   Generates a shareable snapshot URL of the specified dashboard.

4. Organize dashboards into logical folders:
   `grafana_management(operation="folders", dashboard_json={"title": "Infrastructure"})`
   Creates a new folder for organizing related dashboards.

5. Validate the new dashboard folder is accessible:
   `grafana_management(operation="search", search_query="Infrastructure")`

**Expected outcome:** Well-organized dashboard library with appropriate folder structure and sharing configurations.

### Tutorial 9: Automated Remediation Workflow

Design monitoring configurations that enable or trigger automated remediation actions when specific failure patterns are detected.

**Steps:**
1. Identify common failure patterns by analyzing historical alert data:
   `cross_system_correlation(operation="analyze", time_range="7d", sources=["prometheus", "grafana"])`
   Reveals recurring alert patterns and common root causes.

2. Create precise alert rules targeting the identified failure patterns:
   `prometheus_monitoring(operation="rules")`
   Review existing rules before creating new ones.

3. Set up log-based triggers for known error signatures:
   `loki_logging(operation="alerts", query='rate({service="database"} |= "connection_pool_exhausted"[5m]) > 0')`
   Fires an alert the instant a connection pool exhaustion log line appears.

4. Verify all alert configurations are properly active:
   `prometheus_monitoring(operation="alerts")`
   Confirms all rule configurations are valid and evaluating.

5. Run full system diagnostics to validate the entire monitoring setup:
   `monitoring_status(operation="diagnostics")`
   Comprehensive validation of all monitoring integrations and configurations.

**Expected outcome:** A monitoring stack configured for automated detection of known failure patterns with appropriate alert routing and escalation.

### Tutorial 10: Multi-Cluster Observability

Monitor multiple Kubernetes clusters or data center environments through a unified observability interface.

**Steps:**
1. Check all Prometheus targets across all clusters:
   `prometheus_monitoring(operation="targets")`
   Identifies all scrape targets with their cluster labels.

2. Query global metrics aggregated across clusters:
   `prometheus_monitoring(operation="query", query="count(kube_node_info) by (cluster)")`
   Returns node counts per cluster for capacity visibility.

3. Aggregate logs from all clusters searching for error patterns:
   `loki_logging(operation="query", query='{cluster=~".+"} |= "error"', start="1h ago")'
   Searches for errors across all clusters simultaneously.

4. Run comprehensive cross-system correlation across all data sources:
   `cross_system_correlation(operation="analyze", time_range="6h", sources=["prometheus", "loki"])`
   Identifies cross-cluster patterns and dependencies.

5. Verify overall observability stack health:
   `monitoring_status(operation="status", detail_level="detailed")`
   Provides per-cluster health status for all monitoring components.

**Expected outcome:** A unified observability view covering multi-cluster infrastructure with centralized alerting and correlation.

## API Reference

### REST Endpoints
When running in HTTP mode, the server exposes the following endpoints:
- GET /health: Returns {"status": "ok"} indicating the server is running
- POST /mcp: FastMCP streamable HTTP endpoint for tool execution

### Tool API (MCP)
All tools are accessible via the MCP protocol through either stdio or HTTP transport. Each tool accepts an operation parameter that selects the specific action, plus optional parameters relevant to that operation. Responses always include success, message, and operation fields, with additional fields depending on the specific tool and operation.

## Troubleshooting

**Connection Issues:** When failing to connect to Prometheus, verify PROMETHEUS_URL is set correctly and the server is running. Use monitoring_status to check connectivity. For Grafana authentication errors, verify GRAFANA_API_KEY is valid and has required permissions. For empty Loki results, check label names with the labels operation and verify log data exists in the queried time range.

**Query Issues:** Empty PromQL results usually indicate incorrect metric names or label matchers. Use the series operation to discover valid metric combinations. For slow queries, reduce the time range or increase step intervals. For cross-system correlation taking too long, limit the number of source systems or use more specific metric and log queries.

**Configuration Issues:** Environment variables must be set before server startup and require a restart to take effect. Use monitoring_status to verify current configuration values. For storage errors, ensure the storage path is writable and the encryption key is consistent across restarts.

## FAQ

## Advanced Usage Patterns

### Pattern 1: Automated Dashboard Refresh Cycle
Set up a regular cadence for reviewing and updating monitoring dashboards. Start by listing all dashboards and identifying which ones are stale or no longer relevant. Use the search operation to find dashboards by team or service name. Create new dashboard versions for active projects and archive outdated ones by moving them to an Archive folder. After updating, create snapshots for sharing with stakeholders during review meetings.

### Pattern 2: Multi-Stage Incident Response
When an incident is detected, follow this structured response cycle. Stage one is detection and alert verification using prometheus_monitoring alerts operation to confirm the alert is firing and identify the affected services. Stage two is data gathering across all three pillars: query relevant metrics, pull logs from affected services, and check Grafana dashboards for visual context. Stage three is correlation analysis using cross_system_correlation to identify relationships between the symptoms. Stage four is dashboarding by creating or updating a dedicated incident dashboard with the relevant panels. Stage five is documentation through dashboard snapshots and recording the findings in your incident management system.

### Pattern 3: Trend Analysis and Reporting
For weekly or monthly reporting, establish a consistent analysis pattern. Query the same set of key metrics over the reporting period using prometheus_monitoring query_range. Compare the current period against the previous period by adjusting the time range. Pull relevant log statistics to show volume trends and error rate changes. Run correlation analysis to identify recurring patterns. Create or update a report dashboard that automatically reflects the latest data.

### Pattern 4: Monitoring Infrastructure Audit
Perform a quarterly audit of your monitoring infrastructure. Verify all datasources are correctly configured and reachable using the datasources operation. Check that all alert rules are firing correctly and none are stuck in invalid state. Review scrape targets to ensure all intended services are being monitored. Check that dashboards are organized properly in folders with appropriate permissions. Validate log collection by checking label cardinality and ingestion rates.

### Pattern 5: Capacity Threshold Alerting
Set up predictive alerting for capacity-related issues before they become critical. Create alerts that fire when disk usage exceeds 80 percent, when memory usage trends upward over 7 days, when CPU utilization stays above 70 percent for extended periods, and when log ingestion rates approach configured limits. Use the correlation tool to cross-reference capacity alerts with application performance metrics to understand the impact of resource pressure on service quality.

## Cross-System Correlation Deep Dive

The cross_system_correlation tool is the server's most powerful feature for incident investigation. It works by aligning data points across time from different monitoring systems and building evidence chains. Each evidence chain starts with an initial signal from one system (for example, a Prometheus alert), then automatically searches for related events in other systems within configurable time windows. Related log entries from Loki are fetched around the alert timestamp, and Grafana dashboard states are checked for any manual changes or annotations.

The confidence score for each correlation is calculated based on three factors: temporal proximity measured by the time difference between events in seconds, metric severity determined by the deviation from baseline values, and log relevance evaluated by keyword overlap between alert descriptions and log content. Correlations with confidence scores above 0.7 are considered strong and are highlighted in the results. Scores between 0.4 and 0.7 indicate moderate correlations that warrant investigation. Scores below 0.4 are low-confidence correlations that may be coincidental.

Results include specific recommendations for each strong correlation, such as "This metric spike correlates with error log entries from the same service. Consider investigating the deployment that occurred at this time." or "Repeated correlation pattern detected across 3 similar incidents. Consider creating a dedicated alert rule for this failure mode."

## Best Practices for Tool Usage

For monitoring_status, run a health check at the start of every monitoring session to verify all backends are reachable before performing other operations. Use the status operation for regular check-ins during longer analysis sessions to catch any connectivity issues that arise. The config operation is useful for verifying environment setup when first connecting to a new monitoring infrastructure.

For prometheus_monitoring, always use the series operation to validate metric names before building complex queries. Start with instant queries to verify the expression works before using range queries for trend analysis. Use appropriate step intervals for range queries: 15 to 30 seconds for recent data up to 1 hour, 1 to 5 minutes for data up to 24 hours, 5 to 15 minutes for data up to 7 days, and 1 hour for longer time ranges.

For loki_logging, use the labels operation to discover available streams before writing queries. Start queries with specific label selectors rather than broad ones to limit query scope. Use line filters after label selectors to further narrow results. For large queries, increase the limit parameter carefully as very large result sets can be slow to process.

For grafana_management, organize dashboards into folders by team or service for easier maintenance. Use search before creating duplicate dashboards. Create snapshots for sharing with users who don't have Grafana access. Test datasource connectivity after adding new connections.

For cross_system_correlation, start with shorter time ranges for faster results. Use specific metric and log queries rather than broad patterns to get more relevant correlations. Build evidence chains for confirmed incidents to document the full timeline. Use the alerts operation to identify recurrent patterns that could benefit from dedicated alert rules.

## Migration Guide

When migrating monitoring infrastructure, use the following workflow. First, verify new backend connectivity with monitoring_status. Test individual queries against the new infrastructure with prometheus_monitoring and loki_logging. Run cross_system_correlation to validate that data relationships are preserved. Migrate dashboards one at a time using grafana_management, creating them in the new instance based on exported JSON models. Migrate alert rules by recreating them with appropriate thresholds for the new environment. Finally, run full diagnostics to confirm all functionality is working correctly in the migrated environment.

## PromQL Quick Reference

Common PromQL expressions useful for monitoring include: up to check target availability returns 1 for healthy targets and 0 for down targets. rate(http_requests_total[5m]) to calculate request rate per second over a 5-minute window. histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) to calculate the 99th percentile of request latency. 100 - (avg by(instance)(rate(node_cpu_seconds_total{mode='idle'}[5m])) * 100) for CPU utilization percentage. node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100 for available memory percentage. rate(node_network_receive_bytes_total[5m]) for network receive throughput. predict_linear(node_filesystem_free_bytes[6h], 86400) to predict disk space exhaustion in the next 24 hours based on a 6-hour trend.

## LogQL Quick Reference

Common LogQL expressions include: {job="nginx"} to select all nginx logs. {service="api"} |= "error" to filter for lines containing "error". {app="frontend"} | json to parse JSON-formatted log lines and extract structured fields. rate({job="nginx"}[5m]) to calculate the log ingestion rate. sum by (level) (rate({app="api"} | json [5m])) to aggregate log counts by severity level. {namespace="production"} |= "panic" to find panic-level events in production. {cluster="prod-eu"} | logfmt to parse logfmt-formatted log lines.

## FAQ

**Q: Do I need all three monitoring systems running?** A: No. The server works with any combination of Grafana, Prometheus, and Loki. Unavailable systems are reported in health checks but don't block operations on available systems.

**Q: Can I use cloud-managed monitoring services?** A: Yes. The server connects to standard HTTP APIs compatible with Grafana Cloud, Amazon Managed Prometheus, and Grafana Loki. Configure the appropriate URLs and authentication tokens.

**Q: How are API keys secured?** A: They are read from environment variables at startup and never logged or exposed in responses. Persistent data can be encrypted via MONITORING_ENCRYPTION_KEY.

**Q: What's the maximum queryable time range?** A: Practical limits depend on your infrastructure. Prometheus typically has 30-day TSDB retention. Loki retention is configurable. Use increased step intervals for long-range queries to manage data volume.

**Q: Can I create dashboards programmatically?** A: Yes, through the grafana_management tool's dashboards operation with a JSON model parameter containing the complete Grafana dashboard definition.

**Q: How does cross-system correlation handle time zone differences?** A: All timestamps are normalized to UTC for correlation. Results are displayed in UTC by default.

**Q: What happens when a monitoring backend is unreachable?** A: The operation will return a partial result with data from reachable backends and clear error messages for unreachable ones.

**Q: Is there support for query history?** A: Yes, the DiskStore optionally persists query history for later reference and trend analysis.

**Q: How do I test a new monitoring setup?** A: Use the integration operation in monitoring_status to test each backend individually before running multi-system queries.

**Q: Can I export query results?** A: All tool responses are returned as structured JSON that can be logged, saved, or processed further.

**Q: How do I handle rate limiting from monitoring APIs?** A: The server implements automatic backoff and retry for rate-limited requests. For bulk operations, increase the time range step or reduce query frequency.
**Q: What monitoring data can be persisted?** A: Query history, correlation results, and dashboard configurations can be stored in the DiskStore backend with optional encryption.
**Q: How often should I run diagnostics?** A: Run diagnostics after configuration changes, after monitoring infrastructure updates, and on a regular schedule for proactive issue detection. Weekly diagnostics are recommended for production environments.
**Q: Can I use this with Prometheus federation?** A: Yes, the server connects to any Prometheus-compatible HTTP API including federated setups. Configure the federation endpoint URL as PROMETHEUS_URL.
**Q: How do I interpret correlation confidence scores?** A: Scores above 0.7 indicate strong correlations worth investigating immediately. Scores between 0.4 and 0.7 suggest moderate correlations that may be meaningful. Scores below 0.4 are weak correlations that may be coincidental. Consider temporal proximity, metric severity, and log context when evaluating correlations.
**Q: What is the difference between health and status operations?** A: health performs a quick connectivity check to all backends and returns immediately. status provides a comprehensive system overview including component versions, uptime, and configuration summaries. Use health for quick checks and status for detailed reporting.
**Q: How do I migrate dashboards between Grafana instances?** A: Use grafana_management to list dashboards from the source instance, then create new dashboards with the same JSON model on the target instance. Dashboard JSON can be exported and imported. Note that datasource UIDs may need to be updated for the new environment.
**Q: What happens when a query times out?** A: The operation returns a TIMEOUT_ERROR with details about which backend timed out. Reduce the query time range, increase the step interval, or check the backend's availability and performance.
**Q: Can I run multiple correlation analyses simultaneously?** A: Each correlation analysis runs independently. Multiple analyses can be run sequentially. For very large time ranges, consider analyzing shorter segments and combining results.

## Example Session Transcripts

### Session 1: Morning Health Check
User: "Check all my monitoring systems"
Assistant: Runs monitoring_status(operation="health") which probes Grafana, Prometheus, and Loki. Returns a summary showing all three are reachable with response times. Assistant reports: "All three monitoring systems are healthy. Grafana responds in 120ms, Prometheus in 85ms, Loki in 95ms."

### Session 2: Investigating a CPU Spike
User: "My application is slow. What happened in the last hour?"
Assistant: Runs prometheus_monitoring(query="rate(node_cpu_seconds_total{mode!='idle'}[5m])", start="1h ago") to check CPU usage trends. Then runs loki_logging(query='{service="api"} |= "slow"', start="1h ago") to find related log entries. Finally runs cross_system_correlation(operation="metrics_logs", time_range="1h") to link the findings. Returns: "CPU usage spiked to 85% at 14:30, correlating with 47 slow query log entries from the API service. The database connection pool was exhausted."

### Session 3: Dashboard Creation
User: "Create a dashboard showing my web server metrics"
Assistant: Uses grafana_management(operation="dashboards", dashboard_json={...}) to create a new dashboard with panels for HTTP request rate, error rate, latency P50/P95/P99, and active connections. Returns: "Dashboard 'Web Server Metrics' created with 4 panels."

## Monitoring Dashboard Design Patterns

When designing monitoring dashboards, follow these proven patterns for maximum effectiveness. The service overview dashboard should include request rate, error rate, latency percentiles, and saturation indicators for each service. The infrastructure dashboard should show CPU utilization, memory usage, disk I/O, and network throughput across all nodes. The business metrics dashboard should track application-level KPIs like user signups, order volume, and revenue. The alerting dashboard should display all active alerts grouped by severity and service, with links to relevant dashboards. The capacity planning dashboard should show resource usage trends with growth projections and predicted exhaustion dates.

## Data Source Configuration Guide

When configuring Grafana datasources through the grafana_management tool, specify the datasource_type parameter matching the backend type. For Prometheus, use "prometheus" with the URL pointing to the Prometheus server. For Loki, use "loki" with the Loki HTTP URL. Additional configuration options like access mode (proxy vs direct) and custom HTTP headers can be specified through the dashboard_json parameter with appropriate fields. The server automatically tests connectivity when adding new datasources.

## Command Reference Summary

This section provides a quick reference for every tool and its supported operations with typical use cases.

monitoring_status: health for quick connectivity check, status for comprehensive system overview, config for viewing current settings, integration for targeted component testing, diagnostics for full stack validation, version for service version information.

prometheus_monitoring: query for instant PromQL values, query_range for time-series data, alerts for active alert rule states, targets for scrape target health, rules for recording and alerting rule configurations, series for metric discovery via label matchers, metadata for metric HELP and type information, status for Prometheus server health.

loki_logging: query for LogQL execution with log entry results, labels for label name and value discovery, streams for log stream health and metadata, alerts for log-based alert rule creation, stats for query performance metrics, series for log-derived time series exploration.

grafana_management: dashboards for dashboard CRUD, datasources for connection management, alerts for alert rule administration, folders for dashboard organization, users for account management, search for resource discovery, snapshot for dashboard sharing.

cross_system_correlation: analyze for full cross-system analysis, metrics_logs for metric-to-log correlation, alerts for cross-system alert pattern analysis, anomalies for multi-signal anomaly detection, evidence for building incident evidence chains.

## Operation Parameters Quick Reference

All tools share common parameter patterns. The operation parameter is always required and must be one of the Literal values documented for that tool. The time_range parameter accepts human-readable durations like 15m, 1h, 6h, 24h, 7d, 30d. The start and end time parameters accept ISO 8601 timestamps like 2026-01-15T10:00:00Z or relative expressions like 2h ago. The sources parameter accepts a list of system names: prometheus, loki, grafana. The limit parameter controls result size with safe defaults and maximums documented per tool. The step parameter for range queries controls data point resolution and should be set based on the total time range to avoid excessive data points.

## Error Recovery Patterns

When a CONNECTION_ERROR occurs, first verify the backend URL is correct and the service is running. Check network connectivity between the server and the monitoring service. If using authentication, verify API keys are valid. For TIMEOUT_ERROR, reduce the query time range or increase the step interval. For particularly large queries, consider breaking them into smaller segments. When QUERY_ERROR occurs with PromQL, verify metric names using the series operation and check label matchers for typos. For LogQL errors, verify label names exist using the labels operation and check line filter syntax. AUTHENTICATION_ERROR typically requires generating new API keys in the monitoring service's administration interface and updating the environment variables.
