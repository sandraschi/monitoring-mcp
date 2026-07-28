# MCP Tool Reference

All tools follow the **portmanteau pattern**: a single `@mcp.tool()` with an `operation` parameter
that selects the sub-operation. Operations listed below are **implemented** (stubs removed as of the 2026-07 wiring pass).

## `grafana_management`

| Operation | Description | Status |
|-----------|-------------|--------|
| `list_dashboards` | List all dashboards with metadata | Implemented |
| `get_dashboard` | Retrieve dashboard by UID | Implemented |
| `create_dashboard` | Create new dashboard from JSON | Implemented |
| `update_dashboard` | Modify existing dashboard | Implemented |
| `delete_dashboard` | Remove dashboard by UID | Implemented |
| `search_dashboards` | Filter dashboards by title/tag | Implemented |
| `list_datasources` | List configured Grafana datasources | Implemented |
| `query_datasource` | Run query against a datasource | Implemented |
| `analyze_dashboard` | Dashboard structure analysis + scoring | Implemented |
| `create_panel` | Add panel to dashboard | Implemented |
| `update_panel` | Modify panel config | Implemented |
| `create_alert` | Grafana unified alerting rule | Implemented |
| `export_dashboard` | Export as JSON | Implemented |
| `import_dashboard` | Import from JSON | Implemented |
| `list_folders` | List dashboard folders | Implemented |
| `create_folder` | Create dashboard folder | Implemented |
| `get_dashboard_permissions` | View permissions | Implemented |

## `prometheus_monitoring`

| Operation | Description | Status |
|-----------|-------------|--------|
| `query_metrics` | Instant PromQL query (with sampling) | Implemented |
| `query_range` | Range PromQL query | Implemented |
| `list_targets` | List scrape targets + health | Implemented |
| `get_target_health` | Health by job/instance/URL | Implemented |
| `list_rules` | Alerting + recording rules | Implemented |
| `get_rule_groups` | Rule group configs | Implemented |
| `list_alerts` | Active alerts with state summary | Implemented |
| `get_alert_details` | Filter alerts by name | Implemented |
| `get_build_info` | Prometheus version | Implemented |
| `get_config` | Runtime config | Implemented |
| `get_flags` | CLI flags | Implemented |
| `analyze_metrics` | Anomaly patterns + prometheus-api-client metadata | Implemented |
| `optimize_queries` | PromQL performance suggestions | Implemented |
| `create_alert_rule` | Via Grafana unified alerting | Implemented |
| `update_alert_rule` | Via Grafana unified alerting | Implemented |
| `delete_alert_rule` | Via Grafana unified alerting | Implemented |
| `silence_alert` | Alertmanager silences | Implemented |
| `list_silences` | Active silences | Implemented |
| `expire_silence` | Remove silence | Implemented |

## `loki_logging`

| Operation | Description | Status |
|-----------|-------------|--------|
| `query_logs` | Instant LogQL query | Implemented |
| `query_range` | Range LogQL | Implemented |
| `tail_logs` | WebSocket tail (query_range fallback) | Implemented |
| `get_labels` | List labels | Implemented |
| `get_label_values` | Values for a label | Implemented |
| `get_series` | Series matching selectors | Implemented |
| `analyze_logs` | Pattern recognition | Implemented |
| `detect_anomalies` | Error-rate / anomaly heuristics | Implemented |
| `search_errors` | ERROR/Exception patterns | Implemented |
| `trace_requests` | Correlation IDs in logs | Implemented |
| `create_alert_rule` | Loki ruler API | Implemented |
| `list_alerts` | Loki ruler rules | Implemented |
| `optimize_queries` | LogQL suggestions | Implemented |
| `export_logs` | json / csv / text | Implemented |
| `compare_timeframes` | Volume delta between windows | Implemented |
| `generate_report` | Combined patterns + errors report | Implemented |

## `cross_system_correlation`

| Operation | Description | Status |
|-----------|-------------|--------|
| `correlate_incident` | Cross-reference metrics + logs | Implemented |
| `find_root_cause` | Heuristic root cause | Implemented |
| `performance_correlation` | Latency vs perf logs | Implemented |
| `error_correlation` | Error clusters | Implemented |
| `health_assessment` | Combined health score | Implemented |
| `anomaly_correlation` | Metric anomalies vs error logs | Implemented |
| `service_dependency_map` | From Prometheus scrape topology | Implemented |
| `impact_analysis` | Affected services | Implemented |
| `predictive_insights` | Heuristic trend window | Implemented |
| `bottleneck_detection` | High latency + slow logs | Implemented |

## `monitoring_status`

| Operation | Description | Status |
|-----------|-------------|--------|
| `system_health` | Overall health | Implemented |
| `connectivity_test` | Reachability | Implemented |
| `configuration_validation` | URL / config checks | Implemented |
| `performance_metrics` | Engine query stats | Implemented |
| `data_flow_status` | Datasource links | Implemented |
| `alert_status` | Firing alerts + rules | Implemented |
| `storage_status` | Local disk + Prom TSDB | Implemented |
| `backup_status` | Retention / integrity token | Implemented |
| `security_status` | Auth + HTTPS posture | Implemented |
| `capacity_planning` | Disk free + head series | Implemented |
