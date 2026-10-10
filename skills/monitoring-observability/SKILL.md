# monitoring-observability

Runbook skill for the monitoring-mcp server: investigate incidents across
Grafana + Prometheus + Loki through the 6 portmanteau tools.

## When to use

- An alert fired and you need root cause across metrics AND logs.
- A dashboard looks wrong and you need to find out why.
- Someone asks "is the stack healthy?" — start with `monitoring_status`.

## Incident flow

1. `monitoring_status(operation="system_health")` — is it one system or everything?
2. `prometheus_monitoring(operation="list_alerts")` — what is firing right now?
3. `loki_logging(operation="search_errors", query="{app=\"<svc>\"}")` — errors in the window.
4. `cross_system_correlation(operation="correlate_incident",
   incident_description="<symptom>", time_range={"start": ..., "end": ...})`.
5. `grafana_management(operation="get_dashboard", ...)` — look at the service dashboard.

## PromQL recipes

- Error rate: `rate(http_requests_total{status=~"5.."}[5m])`
- Latency p95: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
- Saturated targets: `prometheus_monitoring(operation="get_target_health")`

## LogQL recipes

- Errors for a service: `{app="<svc>"} |= "error"`
- Trace a request: `loki_logging(operation="trace_requests", ...)`
- Compare with yesterday: `loki_logging(operation="compare_timeframes", ...)`

## Alerting

- Grafana unified-alerting rule CRUD goes through `prometheus_monitoring`
  (`create_alert_rule` / `update_alert_rule` / `delete_alert_rule`).
- Alertmanager silences: `silence_alert` / `list_silences` / `expire_silence`.
- Inbound Alertmanager posts land on `POST /api/webhooks/alertmanager`.

## Guardrails

- Read-only ops first (`system_health`, `query_*`, `search_*`); mutating ops
  (`create_*`, `delete_*`, `monitoring_shutdown`) only on explicit request.
- All tool docstrings carry `## Return Format` + `## Examples`; responses always
  include `success` + `conversational_summary`.
