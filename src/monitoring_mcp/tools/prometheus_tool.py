"""
Prometheus Monitoring Portmanteau Tool

Comprehensive Prometheus operations including metrics querying,
alert management, rule configuration, and performance analysis.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Literal

import httpx
from fastmcp import FastMCP

from monitoring_mcp.config import MonitoringConfig
from monitoring_mcp.utils import ResponseCache, map_parallel, match_prometheus_target, sample_list

logger = logging.getLogger(__name__)

PROMETHEUS_OPERATIONS = {
    "query_metrics": "Execute PromQL queries with intelligent sampling",
    "query_range": "Execute range queries for time-series analysis",
    "list_targets": "List all Prometheus scrape targets and their status",
    "get_target_health": "Check health status of specific scrape targets",
    "list_rules": "List all alerting and recording rules",
    "get_rule_groups": "Get detailed rule group configurations",
    "create_alert_rule": "Create new alerting rules (via Grafana unified alerting)",
    "update_alert_rule": "Modify existing alerting rules (via Grafana unified alerting)",
    "delete_alert_rule": "Remove alerting rules (via Grafana unified alerting)",
    "list_alerts": "List active alerts with status and labels",
    "get_alert_details": "Get detailed information about specific alerts",
    "silence_alert": "Create alert silences via Alertmanager",
    "list_silences": "List active alert silences",
    "expire_silence": "Remove alert silences",
    "get_build_info": "Get Prometheus build and version information",
    "get_config": "Retrieve Prometheus configuration (if runtime config enabled)",
    "get_flags": "Get Prometheus command-line flags",
    "analyze_metrics": "AI-powered metrics analysis and anomaly detection",
    "optimize_queries": "Suggest query optimizations and performance improvements",
}


class PrometheusClient:
    """Prometheus / Alertmanager / Grafana-ruler API client."""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.base_url = config.prometheus_url.rstrip("/")
        self.alertmanager_url = config.alertmanager_url.rstrip("/")
        self.grafana_url = config.grafana_url.rstrip("/")
        self.timeout = config.request_timeout
        self.auth_headers = config.get_prometheus_auth() or {}
        self.grafana_headers = {
            **(config.get_grafana_auth() or {}),
            "Content-Type": "application/json",
        }
        self.cache = ResponseCache(
            ttl_seconds=config.cache_ttl_seconds,
            enabled=config.enable_cache,
        )

    async def _make_request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        *,
        use_cache: bool = False,
    ) -> dict[str, Any]:
        url = f"{self.base_url}/api/v1/{endpoint}"
        cache_key = ("prom", endpoint, params)
        if use_cache:
            cached = self.cache.get(*cache_key)
            if cached is not None:
                return cached

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params, headers=self.auth_headers)
            if response.status_code >= 400:
                error_msg = f"Prometheus API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise httpx.HTTPStatusError(error_msg, request=response.request, response=response)
            data = response.json()
            if use_cache:
                self.cache.set(*cache_key, value=data)
            return data

    async def _am_request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | list[Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.alertmanager_url}/api/v2/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(method, url, json=json_body, params=params, headers=self.auth_headers)
            if response.status_code >= 400:
                error_msg = f"Alertmanager API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise httpx.HTTPStatusError(error_msg, request=response.request, response=response)
            if response.status_code == 204 or not response.content:
                return {"status": "ok"}
            return response.json()

    async def _grafana_request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.grafana_url}/api/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(method, url, json=json_body, headers=self.grafana_headers)
            if response.status_code >= 400:
                error_msg = f"Grafana alerting API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise httpx.HTTPStatusError(error_msg, request=response.request, response=response)
            if response.status_code == 204 or not response.content:
                return {"status": "ok"}
            return response.json()

    async def query(self, query: str, time: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"query": query}
        if time:
            params["time"] = time
        return await self._make_request("query", params)

    async def query_range(self, query: str, start: str, end: str, step: str = "15s") -> dict[str, Any]:
        return await self._make_request(
            "query_range",
            {"query": query, "start": start, "end": end, "step": step},
        )

    async def targets(self) -> dict[str, Any]:
        return await self._make_request("targets", use_cache=True)

    async def rules(self) -> dict[str, Any]:
        return await self._make_request("rules", use_cache=True)

    async def alerts(self) -> dict[str, Any]:
        return await self._make_request("alerts")

    async def buildinfo(self) -> dict[str, Any]:
        return await self._make_request("buildinfo", use_cache=True)

    async def status_config(self) -> dict[str, Any]:
        return await self._make_request("status/config")

    async def status_flags(self) -> dict[str, Any]:
        return await self._make_request("status/flags")

    def sync_metadata(self, metric: str | None = None) -> dict[str, Any]:
        """Wire prometheus-api-client for metric metadata enrichment (sync)."""
        try:
            from prometheus_api_client import PrometheusConnect

            prom = PrometheusConnect(
                url=self.base_url,
                disable_ssl=self.base_url.startswith("http://"),
                headers=self.auth_headers or None,
            )
            if metric:
                return {"metric": metric, "metadata": prom.get_metadata(metric) or []}
            all_metrics = prom.all_metrics() or []
            return {"metric_count": len(all_metrics), "sample_metrics": all_metrics[:50]}
        except Exception as exc:
            logger.debug("prometheus-api-client metadata unavailable: %s", exc)
            return {"error": str(exc), "note": "prometheus-api-client enrichment unavailable"}


def register_prometheus_tool(
    mcp: FastMCP,
    _storage: object,
    config: MonitoringConfig,
) -> None:
    """Register the Prometheus portmanteau tool with the MCP server."""

    client = PrometheusClient(config)

    @mcp.tool()
    async def prometheus_monitoring(
        operation: Literal[
            "query_metrics",
            "query_range",
            "list_targets",
            "get_target_health",
            "list_rules",
            "get_rule_groups",
            "create_alert_rule",
            "update_alert_rule",
            "delete_alert_rule",
            "list_alerts",
            "get_alert_details",
            "silence_alert",
            "list_silences",
            "expire_silence",
            "get_build_info",
            "get_config",
            "get_flags",
            "analyze_metrics",
            "optimize_queries",
        ],
        query: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        step: str | None = None,
        target_name: str | None = None,
        rule_group: str | None = None,
        alert_name: str | None = None,
        silence_data: dict[str, Any] | None = None,
        silence_id: str | None = None,
        analysis_context: dict[str, Any] | None = None,
        alert_rule: dict[str, Any] | None = None,
        rule_uid: str | None = None,
    ) -> dict[str, Any]:
        """
        Comprehensive Prometheus monitoring portmanteau tool.

        Consolidates Prometheus, Alertmanager silences, and Grafana unified
        alerting rule CRUD into one tool.
        """
        try:
            if operation not in PROMETHEUS_OPERATIONS:
                return {
                    "success": False,
                    "error": f"Invalid operation '{operation}'. Available: {list(PROMETHEUS_OPERATIONS.keys())}",
                    "conversational_summary": f"I don't recognize the '{operation}' operation.",
                    "available_operations": list(PROMETHEUS_OPERATIONS.keys()),
                }

            logger.info("Executing Prometheus operation: %s", operation)
            result = await _execute_prometheus_operation(
                client,
                operation,
                query=query,
                start_time=start_time,
                end_time=end_time,
                step=step,
                target_name=target_name,
                rule_group=rule_group,
                alert_name=alert_name,
                silence_data=silence_data,
                silence_id=silence_id,
                analysis_context=analysis_context,
                alert_rule=alert_rule,
                rule_uid=rule_uid,
            )
            result["conversational_summary"] = _generate_prometheus_summary(operation, result)
            if operation in ["query_metrics", "query_range", "analyze_metrics", "list_alerts"]:
                result["ai_insights"] = _generate_prometheus_insights(operation, result)
            return result
        except Exception as e:
            logger.error("Error in Prometheus operation '%s': %s", operation, e, exc_info=True)
            return {
                "success": False,
                "error": f"Failed to execute Prometheus operation '{operation}': {e!s}",
                "conversational_summary": (
                    f"I encountered an error while trying to {operation.replace('_', ' ')}. "
                    "Check Prometheus/Alertmanager connectivity and credentials."
                ),
                "troubleshooting_tips": [
                    "Verify Prometheus is running and accessible",
                    "Check query syntax (PromQL can be tricky)",
                    "For silences, ensure Alertmanager is reachable at MONITORING_MCP_ALERTMANAGER_URL",
                    "For create/update/delete alert rules, Grafana unified alerting must be enabled",
                ],
            }


async def _execute_prometheus_operation(
    client: PrometheusClient,
    operation: str,
    *,
    query: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    step: str | None = None,
    target_name: str | None = None,
    rule_group: str | None = None,
    alert_name: str | None = None,
    silence_data: dict[str, Any] | None = None,
    silence_id: str | None = None,
    analysis_context: dict[str, Any] | None = None,
    alert_rule: dict[str, Any] | None = None,
    rule_uid: str | None = None,
) -> dict[str, Any]:
    """Execute the specific Prometheus operation."""
    cfg = client.config

    if operation == "query_metrics":
        if not query:
            raise ValueError("query is required for query_metrics")
        result = await client.query(query)
        series = result.get("data", {}).get("result", [])
        sampled, sample_meta = sample_list(
            series,
            enable_sampling=cfg.enable_sampling,
            sampling_threshold=cfg.sampling_threshold,
            sampling_rate=cfg.sampling_rate,
        )
        if sample_meta["sampled"]:
            result = {**result, "data": {**result.get("data", {}), "result": sampled}}
        return {
            "success": True,
            "operation": "query_metrics",
            "data": result,
            "query": query,
            "result_count": sample_meta["returned_count"],
            "sampling": sample_meta,
        }

    if operation == "query_range":
        if not query or not start_time or not end_time:
            raise ValueError("query, start_time, and end_time are required for query_range")
        step = step or "15s"
        result = await client.query_range(query, start_time, end_time, step)
        series = result.get("data", {}).get("result", [])
        sampled, sample_meta = sample_list(
            series,
            enable_sampling=cfg.enable_sampling,
            sampling_threshold=min(cfg.sampling_threshold, cfg.max_results_limit),
            sampling_rate=cfg.sampling_rate,
        )
        if sample_meta["sampled"]:
            result = {**result, "data": {**result.get("data", {}), "result": sampled}}
        return {
            "success": True,
            "operation": "query_range",
            "data": result,
            "query": query,
            "time_range": {"start": start_time, "end": end_time, "step": step},
            "result_count": sample_meta["returned_count"],
            "sampling": sample_meta,
        }

    if operation == "list_targets":
        result = await client.targets()
        targets = result.get("data", {}).get("activeTargets", [])
        return {
            "success": True,
            "operation": "list_targets",
            "data": result,
            "target_count": len(targets),
            "healthy_targets": sum(1 for t in targets if t.get("health") == "up"),
        }

    if operation == "get_target_health":
        result = await client.targets()
        targets = result.get("data", {}).get("activeTargets", [])
        if target_name:
            targets = [t for t in targets if match_prometheus_target(t, target_name)]
        health_summary = {
            "total": len(targets),
            "up": sum(1 for t in targets if t.get("health") == "up"),
            "down": sum(1 for t in targets if t.get("health") == "down"),
            "unknown": sum(1 for t in targets if t.get("health") == "unknown"),
            "matched_targets": [
                {
                    "job": (t.get("labels") or {}).get("job"),
                    "instance": (t.get("labels") or {}).get("instance"),
                    "health": t.get("health"),
                    "scrapeUrl": t.get("scrapeUrl"),
                }
                for t in targets[:50]
            ],
        }
        return {
            "success": True,
            "operation": "get_target_health",
            "data": result if not target_name else {"activeTargets": targets},
            "health_summary": health_summary,
            "target_filter": target_name,
        }

    if operation == "list_rules":
        result = await client.rules()
        groups = result.get("data", {}).get("groups", [])
        total_rules = sum(len(group.get("rules", [])) for group in groups)
        alert_rules = sum(len([r for r in group.get("rules", []) if r.get("type") == "alerting"]) for group in groups)
        return {
            "success": True,
            "operation": "list_rules",
            "data": result,
            "group_count": len(groups),
            "total_rules": total_rules,
            "alert_rules": alert_rules,
            "recording_rules": total_rules - alert_rules,
        }

    if operation == "get_rule_groups":
        result = await client.rules()
        groups = result.get("data", {}).get("groups", [])
        if rule_group:
            groups = [g for g in groups if g.get("name") == rule_group]
        return {
            "success": True,
            "operation": "get_rule_groups",
            "data": {"groups": groups},
            "group_count": len(groups),
            "filter": rule_group,
        }

    if operation == "list_alerts":
        result = await client.alerts()
        alerts = result.get("data", {}).get("alerts", [])
        alert_summary = {
            "total": len(alerts),
            "firing": sum(1 for a in alerts if a.get("state") == "firing"),
            "pending": sum(1 for a in alerts if a.get("state") == "pending"),
            "inactive": sum(1 for a in alerts if a.get("state") == "inactive"),
        }
        return {
            "success": True,
            "operation": "list_alerts",
            "data": result,
            "alert_summary": alert_summary,
        }

    if operation == "get_alert_details":
        result = await client.alerts()
        alerts = result.get("data", {}).get("alerts", [])
        if alert_name:
            alerts = [
                a
                for a in alerts
                if a.get("labels", {}).get("alertname") == alert_name or alert_name in str(a.get("labels", {}))
            ]
        return {
            "success": True,
            "operation": "get_alert_details",
            "data": {"alerts": alerts},
            "alert_count": len(alerts),
            "alert_filter": alert_name,
        }

    if operation == "get_build_info":
        result = await client.buildinfo()
        return {"success": True, "operation": "get_build_info", "data": result}

    if operation == "get_config":
        result = await client.status_config()
        return {"success": True, "operation": "get_config", "data": result}

    if operation == "get_flags":
        result = await client.status_flags()
        return {"success": True, "operation": "get_flags", "data": result}

    if operation == "list_silences":
        silences = await client._am_request("GET", "silences")
        active = [s for s in silences if isinstance(s, dict) and s.get("status", {}).get("state") == "active"]
        return {
            "success": True,
            "operation": "list_silences",
            "data": silences,
            "active_count": len(active),
            "total_count": len(silences) if isinstance(silences, list) else 0,
        }

    if operation == "silence_alert":
        if not silence_data:
            raise ValueError(
                "silence_data is required for silence_alert (matchers, startsAt, endsAt, createdBy, comment)"
            )
        created = await client._am_request("POST", "silences", json_body=silence_data)
        return {"success": True, "operation": "silence_alert", "data": created}

    if operation == "expire_silence":
        if not silence_id:
            raise ValueError("silence_id is required for expire_silence")
        result = await client._am_request("DELETE", f"silence/{silence_id}")
        return {"success": True, "operation": "expire_silence", "data": result, "silence_id": silence_id}

    if operation == "create_alert_rule":
        if not alert_rule:
            raise ValueError("alert_rule (Grafana unified alerting payload) is required for create_alert_rule")
        created = await client._grafana_request("POST", "v1/provisioning/alert-rules", json_body=alert_rule)
        return {
            "success": True,
            "operation": "create_alert_rule",
            "data": created,
            "note": "Created via Grafana unified alerting provisioning API",
        }

    if operation == "update_alert_rule":
        uid = rule_uid or (alert_rule or {}).get("uid")
        if not uid or not alert_rule:
            raise ValueError("rule_uid and alert_rule are required for update_alert_rule")
        updated = await client._grafana_request("PUT", f"v1/provisioning/alert-rules/{uid}", json_body=alert_rule)
        return {"success": True, "operation": "update_alert_rule", "data": updated, "rule_uid": uid}

    if operation == "delete_alert_rule":
        uid = rule_uid or alert_name
        if not uid:
            raise ValueError("rule_uid (or alert_name as UID) is required for delete_alert_rule")
        deleted = await client._grafana_request("DELETE", f"v1/provisioning/alert-rules/{uid}")
        return {"success": True, "operation": "delete_alert_rule", "data": deleted, "rule_uid": uid}

    if operation == "analyze_metrics":
        if not query:
            raise ValueError("query is required for analyze_metrics")
        result = await client.query(query)
        analysis = _analyze_metrics_data(result, analysis_context or {})
        metric_name = None
        series = result.get("data", {}).get("result", [])
        if series:
            metric_name = next(iter((series[0].get("metric") or {}).keys()), None)
        metadata = await asyncio.to_thread(client.sync_metadata, metric_name)
        analysis["prometheus_metadata"] = metadata
        return {
            "success": True,
            "operation": "analyze_metrics",
            "data": result,
            "analysis": analysis,
            "query": query,
        }

    if operation == "optimize_queries":
        if not query:
            raise ValueError("query is required for optimize_queries")
        return {
            "success": True,
            "operation": "optimize_queries",
            "query": query,
            "optimizations": _analyze_query_performance(query),
        }

    raise ValueError(f"Unsupported operation: {operation}")


def _generate_prometheus_summary(operation: str, result: dict[str, Any]) -> str:
    if not result.get("success"):
        return f"I wasn't able to complete the {operation.replace('_', ' ')} operation. {result.get('error', 'Unknown error occurred')}."

    if operation == "query_metrics":
        count = result.get("result_count", 0)
        sampled = (result.get("sampling") or {}).get("sampled")
        base = f"I executed your PromQL query and found {count} result{'s' if count != 1 else ''}."
        return base + (" Results were sampled due to size." if sampled else "")
    if operation == "query_range":
        count = result.get("result_count", 0)
        return f"Range query returned {count} time series."
    if operation == "list_targets":
        total = result.get("target_count", 0)
        healthy = result.get("healthy_targets", 0)
        return f"{healthy}/{total} scrape targets are healthy."
    if operation == "get_target_health":
        summary = result.get("health_summary", {})
        return (
            f"Target health: {summary.get('up', 0)} up, {summary.get('down', 0)} down (of {summary.get('total', 0)})."
        )
    if operation == "list_alerts":
        summary = result.get("alert_summary", {})
        return f"{summary.get('firing', 0)} firing / {summary.get('total', 0)} total alerts."
    if operation == "list_silences":
        return f"{result.get('active_count', 0)} active silences."
    return f"The {operation.replace('_', ' ')} operation completed successfully."


def _generate_prometheus_insights(operation: str, result: dict[str, Any]) -> dict[str, Any]:
    insights: dict[str, list[str]] = {
        "recommendations": [],
        "alerting_opportunities": [],
        "optimization_suggestions": [],
    }
    if operation == "list_targets":
        healthy = result.get("healthy_targets", 0)
        total = result.get("target_count", 0)
        if total > 0 and (healthy / total) < 0.9:
            insights["recommendations"].append("Review target configurations for unhealthy endpoints")
    elif operation == "list_alerts":
        if (result.get("alert_summary") or {}).get("firing", 0) > 5:
            insights["alerting_opportunities"].append("Consider silences for maintenance windows")
    elif operation == "query_metrics":
        count = result.get("result_count", 0)
        if count == 0:
            insights["optimization_suggestions"].append("Broaden time range or check metric name spelling")
        elif count > 1000:
            insights["optimization_suggestions"].append("Narrow selectors to reduce cardinality")
    return insights


def _series_stats(series: dict[str, Any]) -> dict[str, Any]:
    values = series.get("values") or []
    if series.get("value"):
        values = [series["value"]]
    nums = []
    for item in values:
        try:
            nums.append(float(item[1]))
        except (IndexError, TypeError, ValueError):
            continue
    return {
        "metric": series.get("metric", {}),
        "points": len(nums),
        "min": min(nums) if nums else None,
        "max": max(nums) if nums else None,
        "zeros": sum(1 for n in nums if n == 0),
    }


def _analyze_metrics_data(metrics_data: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
    result = metrics_data.get("data", {}).get("result", [])
    analysis: dict[str, Any] = {
        "total_series": len(result),
        "anomalies": [],
        "patterns": [],
        "summary": "Metrics analysis completed.",
        "recommendations": [],
    }
    stats = map_parallel(_series_stats, result)
    for item in stats:
        if item["points"] < 5:
            analysis["anomalies"].append(
                {
                    "type": "sparse_data",
                    "metric": item["metric"],
                    "description": f"Only {item['points']} data points found",
                }
            )
        elif item["points"] and item["zeros"] > item["points"] * 0.8:
            analysis["anomalies"].append(
                {
                    "type": "mostly_zero",
                    "metric": item["metric"],
                    "description": f"Mostly zero values ({item['zeros']}/{item['points']})",
                }
            )
    if analysis["anomalies"]:
        analysis["summary"] = f"Found {len(analysis['anomalies'])} potential issues in your metrics."
    else:
        analysis["summary"] = "No significant anomalies detected in the metrics data."
    return analysis


def _analyze_query_performance(query: str) -> list[dict[str, str]]:
    optimizations: list[dict[str, str]] = []
    if "rate(" in query and "[5m]" in query and "irate(" not in query:
        optimizations.append(
            {
                "type": "rate_vs_irate",
                "description": "Consider irate() for recent windows",
                "suggestion": query.replace("rate(", "irate("),
            }
        )
    if "sum(" in query and "by (" not in query:
        optimizations.append(
            {
                "type": "missing_grouping",
                "description": "sum() without by() may explode cardinality",
                "suggestion": "Add 'by (label)' clause",
            }
        )
    if len(query) > 200:
        optimizations.append(
            {
                "type": "complex_query",
                "description": "Complex query - consider recording rules",
                "suggestion": "Create recording rules for repeated expressions",
            }
        )
    if not optimizations:
        optimizations.append(
            {"type": "optimization", "description": "Query appears well-optimized", "suggestion": "No changes needed"}
        )
    return optimizations
