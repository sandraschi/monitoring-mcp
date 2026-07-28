# monitoring-mcp — MCP Server Capabilities

## Server Overview

monitoring-mcp is a comprehensive monitoring MCP server built on FastMCP 3.1 that provides intelligent observability operations across Grafana, Prometheus, and Loki ecosystems. It serves as a unified interface for DevOps workflows, performance analysis, system diagnostics, and cross-system correlation. The server uses a portmanteau tool pattern to consolidate related operations into discoverable interfaces, preventing tool explosion while maintaining full functionality across all monitoring domains.

The server integrates with three core observability platforms: Grafana for dashboard visualization and alerting, Prometheus for metrics collection and querying, and Loki for log aggregation and analysis. Each platform is accessed through a dedicated portmanteau tool that exposes between 6 and 12 distinct operations, enabling everything from simple health checks to complex cross-system correlation analysis. The server supports conversational AI assistance through structured responses with natural language summaries, making complex monitoring data accessible and actionable for both DevOps engineers and casual users.

Key features include portmanteau tools following the database-mcp pattern to avoid tool explosion while maintaining full discoverability of all operations. Each tool returns conversational responses with structured data and natural language summaries that provide context about what the data means, suggesting actionable insights and next steps. The server implements sampling capabilities via FastMCP's built-in context sampling for handling large datasets efficiently across long time ranges without overwhelming the LLM context window. Persistent storage with DiskStore backend provides optional encryption for storing query history, alert configurations, and correlation results. The server is built with modern Python including full type annotations, async patterns, and a FastAPI webapp bridge for visual dashboards.

## Tools

### cross_system_correlation

Cross-system correlation tool that enables intelligent analysis across Grafana, Prometheus, and Loki data sources. This is the server's differentiator, providing automatic linking of data points by timestamp across systems, building evidence chains that connect metric anomalies to log patterns and alert firings. Confidence scores indicate the strength of correlations.

**Operations:**
- analyze: Cross-system correlation analysis with time range, source systems, and correlation type parameters. Returns structured correlation results with confidence scores, evidence chains, and actionable recommendations. The analysis engine identifies temporal relationships between events across platforms, scoring each correlation by temporal proximity, metric severity, and log context relevance.
- metrics_logs: Directly correlate Prometheus metrics with Loki log streams for deep diagnostics. When a metric anomaly is detected at time T, this operation automatically fetches surrounding log entries to provide context for the deviation. Supports custom metric queries and log filters to narrow the correlation scope.
- alerts: Analyze alert patterns across systems to identify common root causes. Groups alerts by time windows, identifies co-firing patterns, and suggests upstream/downstream relationships.
- anomalies: Detect anomalous patterns by correlating multiple monitoring signals. Uses statistical baselines and cross-signal validation to identify genuine anomalies versus isolated spikes.
- evidence: Build evidence chains linking metrics, logs, and alerts for incident analysis. Each evidence chain is a temporal sequence of data points that together tell the story of an incident from first symptom to resolution.

**Parameters:** correlation_type Literal (required): analyze|metrics_logs|alerts|anomalies|evidence. time_range str (required, e.g. "1h", "24h", "7d"). sources list[str] optional (default all available): prometheus|loki|grafana. metric_queries list[str] optional to filter which metrics to correlate. log_queries list[str] optional to filter which log patterns to include. alert_filters dict optional for severity, state, or source filtering.

**Return Format:** success bool, correlation_id string, results list of correlated findings with timestamps, evidence_chain list of linked data points with confidence scores, confidence_score float between 0 and 1, recommendations list of actionable insights for each correlation, execution_time_ms int.

### grafana_management

Complete Grafana lifecycle management including dashboard CRUD, datasource configuration, alert rule management, folder organization, and user administration. Supports both API-driven management via Grafana's REST API and configuration-as-code workflows through JSON model import/export.

**Operations:**
- dashboards: List, create, update, and delete dashboards with full JSON model support. When creating, accepts a complete Grafana dashboard model. When listing, returns dashboard titles, UIDs, folder paths, and last modified dates.
- datasources: Manage Prometheus, Loki, and other datasource connections. Supports adding, testing, and removing datasources. Returns datasource status and connectivity test results.
- alerts: Create and manage alert rules with notification channels. Supports Grafana Alerting (v8+) rules including evaluation intervals, conditions, and notification routing.
- folders: Organize dashboards into hierarchical folder structures. Supports creating, listing, and deleting folders with permission inheritance.
- users: Manage Grafana user accounts, roles, and team memberships. Supports adding users, changing roles, and listing all accounts.
- search: Search dashboards, folders, and datasources by query string. Returns matching items with their full metadata and hierarchy information.
- snapshot: Create and manage dashboard snapshots for sharing. Supports creating shareable snapshot URLs with optional expiration.

**Parameters:** operation Literal (required): dashboards|datasources|alerts|folders|users|search|snapshot. dashboard_uid str optional. folder_id int optional. datasource_type str optional. alert_name str optional. search_query str optional. dashboard_json dict optional for create/update operations with complete dashboard model.

**Return Format:** success bool, operation string executed, message string with human-readable summary, result dict with dashboard details, datasource configuration, or alert status, next_steps list of suggested follow-up actions, execution_time_ms int.

### loki_logging

Powerful log querying and management interface for the Loki log aggregation system. Supports LogQL query construction, label exploration, stream management, log-based alerting, and query performance analysis. Designed for efficient forensic analysis and real-time monitoring with support for pagination, filtering, and structured log parsing.

**Operations:**
- query: Execute LogQL queries with time range and label filters. Supports log stream selectors, line filters, parser expressions, and metric queries. Returns results with proper pagination and progress tracking.
- labels: List and explore available log label names and values. Supports query-based filtering to find labels matching specific patterns or services.
- streams: Manage and inspect log streams across services. Shows stream metadata including active streams, cardinality, and ingestion rates.
- alerts: Create log-based alert rules from query patterns. Converts LogQL queries into alert rules with configurable evaluation frequency and thresholds.
- stats: Get query performance statistics and log volume metrics. Returns execution time, bytes scanned, stream count, and throughput information.
- series: Explore time series derived from log data. Shows unique metric series generated from log streams via LogQL metric queries.

**Parameters:** operation Literal (required): query|labels|streams|alerts|stats|series. query str optional with LogQL syntax for filtering. start_time str optional in ISO format. end_time str optional in ISO format. label_filters dict optional for label-based filtering. limit int optional (default 100, max 5000). stream_name str optional for stream-specific operations.

**Return Format:** success bool, operation string, result dict containing log entries with timestamps, labels, and content, or label information with value counts, or stream details with health status. query_stats dict with execution time, scanned bytes, and stream count. recommendations list for optimizing queries or investigating patterns.

### prometheus_monitoring

Comprehensive Prometheus metrics querying and management supporting PromQL queries, alert rule management, target discovery, recording rules, and service discovery integration. Designed for both ad-hoc querying by DevOps engineers and automated monitoring workflows through programmatic access.

**Operations:**
- query: Execute instant PromQL queries for point-in-time metric values. Supports all PromQL functions, aggregation operators, and label matchers.
- query_range: Execute range PromQL queries with configurable time windows and step intervals. Returns time-series data suitable for graphing and trend analysis.
- alerts: List and manage alerting rules and their current state. Shows alert names, expressions, duration, labels, annotations, and current state (firing, pending, etc.).
- targets: Discover and inspect scrape targets and their health. Returns target URLs, job names, last scrape times, scrape durations, and health status.
- rules: Manage recording and alerting rule configurations. Lists all rules with their PromQL expressions, evaluation intervals, and current state.
- series: Explore metric series matching provided label matchers. Useful for discovering available metric combinations before querying.
- metadata: Get metric metadata including type (counter, gauge, histogram) and HELP strings. Essential for understanding metric semantics before constructing queries.
- status: Check Prometheus server status, configuration, and build information. Returns TSDB stats, storage retention, and configuration hash.

**Parameters:** operation Literal (required): query|query_range|alerts|targets|rules|series|metadata|status. query str optional PromQL expression. start_time str optional ISO format. end_time str optional ISO format. step str optional range query resolution (default "15s"). alert_name str optional for specific alert details. target_job str optional for job-specific target listing. limit int optional (default 100, max 5000).

**Return Format:** success bool, operation string, result dict with query results including metric names, labels, values, and timestamps, or alert rule status, or target list with health information. metadata dict with metric type and HELP strings. pagination info for large result sets.

### monitoring_status

System health and status monitoring providing a comprehensive view of all connected monitoring infrastructure. This is the first tool to call when starting a monitoring session or diagnosing system issues. Returns operational status, configuration summary, data freshness metrics, and integration health for all configured backends.

**Operations:**
- health: Quick connectivity check for all monitoring backends. Returns per-service status (ok, error, unreachable) with response times.
- status: Comprehensive system status with component-level details including version information, uptime, and configuration summaries.
- config: View current server configuration and environment settings including all URLs and connection parameters (without exposing secret values).
- integration: Test and validate specific monitoring integrations. Useful for verifying connectivity after configuration changes.
- diagnostics: Run comprehensive diagnostic checks across the monitoring stack. Tests API connectivity, query execution, and data freshness for each service.
- version: Get version information for all connected services including Grafana, Prometheus, and Loki server versions.

**Parameters:** operation Literal (required): health|status|config|integration|diagnostics|version. component str optional to target a specific backend (prometheus|grafana|loki|all). detail_level str optional ("basic"|"standard"|"detailed", default "standard").

**Return Format:** success bool, operation string, status dict with per-component health results including reachability flags, response times, and error messages, config dict with current server settings, recommendations list for improving system health or resolving detected issues.

## Configuration

### Environment Variables
All configuration is done through environment variables set before server startup. Changes require a server restart.

- GRAFANA_URL: Grafana instance URL (default: http://localhost:3000). Must include protocol and port.
- GRAFANA_API_KEY: Grafana API token for authentication. Generate in Grafana Admin > API Keys with appropriate role permissions.
- PROMETHEUS_URL: Prometheus server URL (default: http://localhost:9090). Supports both instant and range query APIs.
- LOKI_URL: Loki server URL (default: http://localhost:3100). Supports LogQL query API.
- MONITORING_STORAGE_PATH: Path for DiskStore persistence (default: ./data/monitoring_mcp). Must be writable.
- MONITORING_ENCRYPTION_KEY: Optional key for encrypting stored data at rest.
- MONITORING_LOG_LEVEL: Logging verbosity level (INFO, DEBUG, WARNING, ERROR). Default INFO.
- MCP_TRANSPORT: Transport protocol for MCP communication (stdio or http). Default stdio.
- MCP_PORT: Port for HTTP transport mode when MCP_TRANSPORT=http.

### Storage System
The server uses DiskStore backend with optional encryption for persisting query history, alert configurations, and correlation results across sessions. Storage path is configurable via MONITORING_STORAGE_PATH and defaults to a data directory relative to the server root. When MONITORING_ENCRYPTION_KEY is set, all stored data is encrypted at rest using the provided key. The store handles automatic serialization of complex monitoring data structures including correlation results, dashboard configurations, and query templates.

## Data Sources

### Grafana Integration
Connects to the Grafana REST API for dashboard management, datasource configuration, alert rule management, and user administration. Authentication is handled via API tokens configured through GRAFANA_API_KEY. The integration supports Grafana 8.x through 11.x including the new Grafana Alerting system introduced in Grafana 9. All API calls include proper error handling for authentication failures, rate limiting, and network timeouts.

### Prometheus Integration
Connects to the Prometheus HTTP API for metric queries, target discovery, rule management, and server status. Supports both instant queries (GET /api/v1/query) and range queries (GET /api/v1/query_range). Compatible with Prometheus 2.x through the current version. The integration automatically handles query timeouts, connection errors, and malformed PromQL expressions with descriptive error messages.

### Loki Integration
Connects to the Loki HTTP API for log queries, label exploration, and stream management. Supports the full LogQL query language including stream selectors, line filters, label matchers, and metric queries. Compatible with Loki 2.x through 3.x. Log queries respect the configured limit parameter with a default of 100 and maximum of 5000 entries, with pagination support for larger result sets.

## Integration Patterns

The server enables multi-step workflows combining data from all three observability platforms. A typical incident investigation workflow might begin with a monitoring_status health check to verify connectivity to all backends. Next, use prometheus_monitoring to query relevant metrics around the incident time window, identifying anomalies in CPU, memory, or request rates. Cross-reference these findings with loki_logging to pull relevant log entries from affected services, using LogQL queries to filter for error patterns. Run cross_system_correlation to automatically identify temporal relationships between metric anomalies and log events, building evidence chains that tell the complete incident story. Finally, use grafana_management to create or update dashboards that visualize the findings, and set up alert rules based on the correlation patterns discovered.

For proactive monitoring, the server can be used to analyze historical data and set up intelligent alerting. Start by analyzing current alert rules with prometheus_monitoring to identify gaps in coverage. Explore Loki labels to understand what log data is available for alert generation. Create log-based alerts that trigger on error rate spikes correlated with metric anomalies. Validate the alert rules by checking their status and simulating firing conditions.

## Sampling Capabilities

For handling large datasets spanning extended time ranges, the server leverages FastMCP's built-in context sampling. This enables efficient processing of time-series data across periods of days or weeks without overwhelming the LLM context window. Sampling is automatically applied to large query results and correlation analyses, with configurable sample sizes and strategies.

## Prompt Templates

The server exposes several prompt templates for common monitoring workflows:
- incident-response: A guided incident investigation walkthrough that helps users systematically identify root causes
- performance-review: A performance analysis pattern that walks through metric selection, trend analysis, and reporting
- alert-tuning: Alert rule optimization guidance for reducing false positives and improving signal-to-noise ratio
- dashboard-design: Dashboard creation best practices including panel selection, layout, and data source configuration

## Resource URIs

- resource://monitoring-mcp/status: Current server and integration health status with all component states
- resource://monitoring-mcp/config: Current configuration values (excluding secrets) showing all environment settings
- resource://monitoring-mcp/capabilities: Full capability listing including all tools, their operations, and parameter schemas

## Error Handling

All tools return structured error responses with the following fields on failure: success boolean set to false, error string with human-readable description, error_type string with categorized error code for programmatic handling, recovery_options list of actionable recovery suggestions, and diagnostic_info dict with technical details for debugging (excluding sensitive information).

Common error types include CONNECTION_ERROR when backends are unreachable, AUTHENTICATION_ERROR when API keys are invalid or expired, QUERY_ERROR when PromQL or LogQL expressions are malformed, TIMEOUT_ERROR when operations exceed their configured timeout, NOT_FOUND when requested resources don't exist, and VALIDATION_ERROR when input parameters fail schema validation.

## Performance Characteristics

Query response times range from 200 milliseconds to 2 seconds depending on data volume and query complexity. Dashboard operations take 500 milliseconds to 3 seconds for creation and updates. Correlation analysis is the most intensive operation, requiring 1 to 5 seconds for cross-system analysis depending on the time range and number of sources. Health checks complete in 100 to 500 milliseconds per component. Storage operations via the DiskStore backend complete in 10 to 100 milliseconds.

## Security Considerations

API keys are stored exclusively in environment variables and are never logged or exposed in tool responses. For production deployments, all HTTP connections should use TLS to encrypt communication between the server and monitoring backends. The DiskStore can be configured with an encryption key for data at rest protection. Grafana API tokens should have the minimum permissions required for the intended operations. Authentication for the MCP server itself is handled by FastMCP's web_app integration layer.

## Rate Limiting and Pagination

Prometheus queries are subject to server-side timeouts configurable via the query timeout settings on the Prometheus server. Loki queries return paginated results with the limit parameter controlling page size (default 100, maximum 5000). Grafana API rate limits depend on the Grafana instance configuration and API key type. All tools support pagination via continuation tokens where applicable, with has_more flags indicating additional results are available.

## Integration Service Details

### Grafana REST API Reference

The Grafana integration communicates with the following REST API endpoints: GET /api/search for dashboard discovery returns dashboard titles, UIDs, and folder paths with support for query parameter filtering. POST /api/dashboards/db creates or updates dashboards from JSON models with the dashboard model nested under a dashboard key and optional overwrite flag. GET /api/dashboards/uid/{uid} retrieves a complete dashboard definition including panels, datasource references, and template variables. DELETE /api/dashboards/uid/{uid} removes a dashboard from the instance. GET /api/datasources lists all configured datasources with their types, URLs, and access modes. POST /api/datasources registers a new datasource connection. GET /api/datasources/{id} retrieves details for a specific datasource including its health check results. GET /api/ruler/grafana/api/v1/rules lists alert rules with their expressions, evaluation intervals, and current states. POST /api/ruler/grafana/api/v1/rules creates new alert rules with configurable conditions and notification settings. GET /api/folders lists all dashboard folders with their UIDs and parent folder relationships. POST /api/folders creates new folders for dashboard organization. GET /api/users lists Grafana users with their login, email, and role assignments. POST /api/users creates new user accounts with specified roles and authentication methods.

### Prometheus HTTP API Reference

The Prometheus integration communicates with the following endpoints. GET /api/v1/query executes instant PromQL queries returning the current value for the expression at the query timestamp. GET /api/v1/query_range executes range PromQL queries over a specified time window with configurable step resolution for graphing. GET /api/v1/alerts lists all alerting rules and their current states including firing alerts with their active time and pending alerts in evaluation. GET /api/v1/targets lists all configured scrape targets with their health status, last scrape timestamps, scrape durations, and labels. GET /api/v1/rules lists all recording and alerting rule configurations with their PromQL expressions and evaluation metadata. GET /api/v1/series finds time series matching specified label matchers for metric discovery. GET /api/v1/metadata returns metric metadata including type classification and HELP documentation strings. GET /api/v1/status/config returns the current Prometheus configuration YAML for validation. GET /api/v1/status/buildinfo returns server version, revision, and build timestamp.

### Loki HTTP API Reference

The Loki integration communicates with the following LogQL API endpoints. GET /api/v1/labels returns all label names across all log streams for label discovery. GET /api/v1/label/{name}/values returns all values for a specific label name. GET /api/v1/query_range executes LogQL range queries returning log entries with their timestamps, labels, and content for the specified time range and query expression. GET /api/v1/series finds time series matching log stream selectors for log stream discovery. GET /api/v1/tail streams log entries in real-time for live tailing. GET /api/v1/index/stats returns statistics about log volume and streams for capacity planning.

## Version Compatibility

The monitoring-mcp server maintains compatibility with the following version ranges through tested API contracts. Grafana 8.x through 11.x is supported with full feature coverage including the legacy dashboard API and the newer Grafana Alerting API introduced in version 9. Prometheus 2.x through the latest 3.x versions are supported with all query, rule, target, and metadata APIs. Loki 2.x through 3.x iterations are supported with the complete LogQL query language across both its classic and structured metadata features. When connecting to older versions of any service, the server automatically adapts its API calls to the compatible endpoint format based on feature detection during the health check phase.

## Multi-Tenancy and Access Control

The server supports Grafana organization filtering through the grafana_management tool's ability to specify organization IDs in API requests. Folder-based access control is respected when managing dashboards, with inherited permissions from parent folders applying automatically. For Prometheus and Loki multi-tenancy, configure access at the datasource level through separate URL and credential configurations for each tenant. The monitoring_status tool reports which tenants and organizations are accessible, allowing operators to verify access boundaries.

## Observability Use Cases by Role

For DevOps engineers performing daily operations, the primary workflow involves using prometheus_monitoring for quick metric checks and loki_logging for log investigation during incident response. SREs managing SLOs and error budgets benefit from cross_system_correlation to understand failure domains and dependency chains, combined with grafana_management for creating SLO tracking dashboards. Platform engineers configuring monitoring infrastructure rely on the full toolset: setting up datasources with grafana_management, validating scrape targets with prometheus_monitoring, configuring log collection with loki_logging, and establishing alert rules based on correlation patterns. Security analysts use loki_logging for log forensics and cross_system_correlation for anomaly detection across authentication, network, and application logs. Managers reviewing system health use monitoring_status for high-level health summaries and grafana_management for accessing shared dashboards and reports.

## Best Practices

When constructing PromQL queries, always verify metric names using the series operation before building alerts or dashboards to ensure the metric exists and has the expected labels. For Loki log queries, start with broad label selectors and narrow down with line filters to bound query scope and improve performance. Correlation analysis should use time windows of 1 to 6 hours for incident investigation and 24 hours to 7 days for pattern discovery. Dashboard management follows a lifecycle of planning the visualization layout, creating the dashboard from a JSON model, iterating on panel configurations through updates, and sharing results via snapshots for collaborative review. Regular health checks through monitoring_status should be part of any scheduled monitoring maintenance to catch integration drift before it affects operations.
