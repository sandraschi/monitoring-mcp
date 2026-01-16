"""
Prometheus Monitoring Portmanteau Tool

Comprehensive Prometheus operations including metrics querying,
alert management, rule configuration, and performance analysis.

PORTMANTEAU PATTERN: Consolidates all Prometheus operations into a single tool
to avoid tool explosion while maintaining full functionality.
"""

import logging
from typing import Any, Literal

import httpx
from fastmcp import FastMCP
from py_key_value_aio import AbstractStore

from monitoring_mcp.config import MonitoringConfig

logger = logging.getLogger(__name__)

# Prometheus operations supported by this portmanteau tool
PROMETHEUS_OPERATIONS = {
    "query_metrics": "Execute PromQL queries with intelligent sampling",
    "query_range": "Execute range queries for time-series analysis",
    "list_targets": "List all Prometheus scrape targets and their status",
    "get_target_health": "Check health status of specific scrape targets",
    "list_rules": "List all alerting and recording rules",
    "get_rule_groups": "Get detailed rule group configurations",
    "create_alert_rule": "Create new alerting rules",
    "update_alert_rule": "Modify existing alerting rules",
    "delete_alert_rule": "Remove alerting rules",
    "list_alerts": "List active alerts with status and labels",
    "get_alert_details": "Get detailed information about specific alerts",
    "silence_alert": "Create alert silences to suppress notifications",
    "list_silences": "List active alert silences",
    "expire_silence": "Remove alert silences",
    "get_build_info": "Get Prometheus build and version information",
    "get_config": "Retrieve Prometheus configuration (if runtime config enabled)",
    "get_flags": "Get Prometheus command-line flags",
    "analyze_metrics": "AI-powered metrics analysis and anomaly detection",
    "optimize_queries": "Suggest query optimizations and performance improvements",
}


class PrometheusClient:
    """Prometheus API client with authentication and error handling."""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.base_url = config.prometheus_url.rstrip("/")
        self.timeout = config.request_timeout

    async def _make_request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make request to Prometheus API."""
        url = f"{self.base_url}/api/v1/{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)

            if response.status_code >= 400:
                error_msg = f"Prometheus API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise httpx.HTTPStatusError(error_msg, request=response.request, response=response)

            return response.json()

    async def query(self, query: str, time: str | None = None) -> dict[str, Any]:
        """Execute instant query."""
        params = {"query": query}
        if time:
            params["time"] = time
        return await self._make_request("query", params)

    async def query_range(
        self, query: str, start: str, end: str, step: str = "15s"
    ) -> dict[str, Any]:
        """Execute range query."""
        params = {
            "query": query,
            "start": start,
            "end": end,
            "step": step,
        }
        return await self._make_request("query_range", params)

    async def targets(self) -> dict[str, Any]:
        """Get all targets."""
        return await self._make_request("targets")

    async def rules(self) -> dict[str, Any]:
        """Get all rules."""
        return await self._make_request("rules")

    async def alerts(self) -> dict[str, Any]:
        """Get all alerts."""
        return await self._make_request("alerts")

    async def buildinfo(self) -> dict[str, Any]:
        """Get build information."""
        return await self._make_request("buildinfo")


async def register_prometheus_tool(
    mcp: FastMCP,
    _storage: AbstractStore,
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
    ) -> dict[str, Any]:
        """
        Comprehensive Prometheus monitoring portmanteau tool leveraging FastMCP 2.14.3.

        PORTMANTEAU PATTERN: Consolidates 19 Prometheus operations into a single tool
        to prevent tool explosion while maintaining comprehensive functionality.

        Provides intelligent PromQL assistance, performance analysis, and conversational
        insights for metrics data interpretation.

        Args:
            operation: The Prometheus operation to perform
            query: PromQL query string for query operations
            start_time: Start time for range queries (RFC3339 or unix timestamp)
            end_time: End time for range queries (RFC3339 or unix timestamp)
            step: Query resolution step (e.g., '15s', '1m', '1h')
            target_name: Target name for target-specific operations
            rule_group: Rule group name for rule operations
            alert_name: Alert name for alert operations
            silence_data: Silence configuration for silencing operations
            silence_id: Silence ID for silence management
            analysis_context: Additional context for AI analysis operations

        Returns:
            Dict containing operation results with conversational summary and insights
        """
        try:
            if operation not in PROMETHEUS_OPERATIONS:
                return {
                    "success": False,
                    "error": f"Invalid operation '{operation}'. Available: {list(PROMETHEUS_OPERATIONS.keys())}",
                    "conversational_summary": f"I don't recognize the '{operation}' operation. Here are the available Prometheus operations I can help with.",
                    "available_operations": list(PROMETHEUS_OPERATIONS.keys()),
                }

            logger.info(f"Executing Prometheus operation: {operation}")

            # Execute the requested operation
            result = await _execute_prometheus_operation(
                client,
                operation,
                query,
                start_time,
                end_time,
                step,
                target_name,
                rule_group,
                alert_name,
                silence_data,
                silence_id,
                analysis_context,
            )

            # Add conversational insights
            result["conversational_summary"] = _generate_prometheus_summary(operation, result)

            # Add AI-powered recommendations where appropriate
            if operation in ["query_metrics", "query_range", "analyze_metrics", "list_alerts"]:
                result["ai_insights"] = _generate_prometheus_insights(operation, result)

            return result

        except Exception as e:
            logger.error(f"Error in Prometheus operation '{operation}': {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to execute Prometheus operation '{operation}': {e!s}",
                "conversational_summary": f"I encountered an error while trying to {operation.replace('_', ' ')}. This might be due to connectivity issues with Prometheus or invalid query syntax. Please check your Prometheus configuration and try again.",
                "troubleshooting_tips": [
                    "Verify Prometheus is running and accessible",
                    "Check query syntax (PromQL can be tricky)",
                    "Ensure time ranges are valid",
                    "Validate metric names exist in your Prometheus instance",
                ],
            }


async def _execute_prometheus_operation(
    client: PrometheusClient,
    operation: str,
    query: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    step: str | None = None,
    target_name: str | None = None,
    rule_group: str | None = None,  # noqa: ARG001
    alert_name: str | None = None,  # noqa: ARG001
    silence_data: dict[str, Any] | None = None,  # noqa: ARG001
    silence_id: str | None = None,  # noqa: ARG001
    analysis_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute the specific Prometheus operation."""

    if operation == "query_metrics":
        if not query:
            raise ValueError("query is required for query_metrics")
        result = await client.query(query)
        return {
            "success": True,
            "operation": "query_metrics",
            "data": result,
            "query": query,
            "result_count": len(result.get("data", {}).get("result", [])),
        }

    elif operation == "query_range":
        if not query or not start_time or not end_time:
            raise ValueError("query, start_time, and end_time are required for query_range")
        step = step or "15s"
        result = await client.query_range(query, start_time, end_time, step)
        return {
            "success": True,
            "operation": "query_range",
            "data": result,
            "query": query,
            "time_range": {"start": start_time, "end": end_time, "step": step},
            "result_count": len(result.get("data", {}).get("result", [])),
        }

    elif operation == "list_targets":
        result = await client.targets()
        targets = result.get("data", {}).get("activeTargets", [])
        return {
            "success": True,
            "operation": "list_targets",
            "data": result,
            "target_count": len(targets),
            "healthy_targets": sum(1 for t in targets if t.get("health") == "up"),
        }

    elif operation == "get_target_health":
        result = await client.targets()
        targets = result.get("data", {}).get("activeTargets", [])

        if target_name:
            # Filter for specific target
            matching_targets = [
                t for t in targets if t.get("labels", {}).get("__name__") == target_name
            ]
            targets = matching_targets

        health_summary = {
            "total": len(targets),
            "up": sum(1 for t in targets if t.get("health") == "up"),
            "down": sum(1 for t in targets if t.get("health") == "down"),
            "unknown": sum(1 for t in targets if t.get("health") == "unknown"),
        }

        return {
            "success": True,
            "operation": "get_target_health",
            "data": result,
            "health_summary": health_summary,
            "target_filter": target_name,
        }

    elif operation == "list_rules":
        result = await client.rules()
        groups = result.get("data", {}).get("groups", [])
        total_rules = sum(len(group.get("rules", [])) for group in groups)
        alert_rules = sum(
            len([r for r in group.get("rules", []) if r.get("type") == "alerting"])
            for group in groups
        )

        return {
            "success": True,
            "operation": "list_rules",
            "data": result,
            "group_count": len(groups),
            "total_rules": total_rules,
            "alert_rules": alert_rules,
            "recording_rules": total_rules - alert_rules,
        }

    elif operation == "list_alerts":
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

    elif operation == "get_build_info":
        result = await client.buildinfo()
        return {
            "success": True,
            "operation": "get_build_info",
            "data": result,
        }

    # Placeholder implementations for operations not yet implemented
    elif operation in [
        "get_rule_groups",
        "create_alert_rule",
        "update_alert_rule",
        "delete_alert_rule",
        "get_alert_details",
        "silence_alert",
        "list_silences",
        "expire_silence",
        "get_config",
        "get_flags",
    ]:
        return {
            "success": False,
            "operation": operation,
            "error": f"Operation '{operation}' is not yet implemented",
            "note": "This operation is planned for a future version",
        }

    elif operation == "analyze_metrics":
        if not query:
            raise ValueError("query is required for analyze_metrics")
        result = await client.query(query)
        analysis = _analyze_metrics_data(result, analysis_context or {})
        return {
            "success": True,
            "operation": "analyze_metrics",
            "data": result,
            "analysis": analysis,
            "query": query,
        }

    elif operation == "optimize_queries":
        if not query:
            raise ValueError("query is required for optimize_queries")
        optimizations = _analyze_query_performance(query)
        return {
            "success": True,
            "operation": "optimize_queries",
            "query": query,
            "optimizations": optimizations,
        }

    else:
        raise ValueError(f"Unsupported operation: {operation}")


def _generate_prometheus_summary(operation: str, result: dict[str, Any]) -> str:
    """Generate conversational summary for Prometheus operation results."""
    if not result.get("success"):
        return f"I wasn't able to complete the {operation.replace('_', ' ')} operation. {result.get('error', 'Unknown error occurred')}."

    if operation == "query_metrics":
        count = result.get("result_count", 0)
        return f"I executed your PromQL query and found {count} result{'s' if count != 1 else ''}. {'Here are the metrics data:' if count > 0 else 'No results matched your query - you might want to check the metric name or time range.'}"

    elif operation == "query_range":
        count = result.get("result_count", 0)
        time_range = result.get("time_range", {})
        return f"I executed your range query from {time_range.get('start', 'unknown')} to {time_range.get('end', 'unknown')} and got {count} time series result{'s' if count != 1 else ''}. This gives you a temporal view of your metrics."

    elif operation == "list_targets":
        total = result.get("target_count", 0)
        healthy = result.get("healthy_targets", 0)
        health_rate = (healthy / total * 100) if total > 0 else 0
        return f"I found {total} scrape targets in your Prometheus setup. {healthy} are healthy ({health_rate:.1f}%), which indicates {'excellent' if health_rate > 95 else 'good' if health_rate > 80 else 'concerning'} target health."

    elif operation == "get_target_health":
        summary = result.get("health_summary", {})
        total = summary.get("total", 0)
        up = summary.get("up", 0)
        down = summary.get("down", 0)
        if total == 0:
            return "I didn't find any scrape targets matching your criteria. Please check the target name or configuration."
        return f"Target health status: {up}/{total} targets are up, {down} are down. {'Most targets are healthy.' if up > down else 'Some targets need attention.'}"

    elif operation == "list_rules":
        groups = result.get("group_count", 0)
        total = result.get("total_rules", 0)
        alerts = result.get("alert_rules", 0)
        recording = result.get("recording_rules", 0)
        return f"I found {groups} rule groups containing {total} total rules ({alerts} alerting, {recording} recording). This gives you {'comprehensive' if total > 10 else 'basic'} monitoring coverage."

    elif operation == "list_alerts":
        summary = result.get("alert_summary", {})
        firing = summary.get("firing", 0)
        pending = summary.get("pending", 0)
        total = summary.get("total", 0)
        if total == 0:
            return (
                "Great news! You have no active alerts. Your systems appear to be running smoothly."
            )
        return f"I found {total} alerts: {firing} firing, {pending} pending. {'Some alerts need immediate attention.' if firing > 0 else 'Some alerts are developing - keep an eye on them.'}"

    elif operation == "get_build_info":
        version = result.get("data", {}).get("data", {}).get("version", "unknown")
        return f"Your Prometheus instance is running version {version}. This helps ensure compatibility with queries and features."

    elif operation == "analyze_metrics":
        analysis = result.get("analysis", {})
        anomalies = len(analysis.get("anomalies", []))
        return f"I analyzed your metrics and found {anomalies} potential anomal{'ies' if anomalies != 1 else 'y'}. {analysis.get('summary', 'Review the detailed analysis for insights.')}"

    elif operation == "optimize_queries":
        optimizations = result.get("optimizations", [])
        count = len(optimizations)
        return f"I found {count} optimization opportunit{'ies' if count != 1 else 'y'} for your PromQL query. {'Here are the suggestions:' if count > 0 else 'Your query looks well-optimized already!'}"

    else:
        return f"The {operation.replace('_', ' ')} operation completed successfully."


def _generate_prometheus_insights(operation: str, result: dict[str, Any]) -> dict[str, Any]:
    """Generate AI-powered insights for Prometheus operations."""
    insights = {"recommendations": [], "alerting_opportunities": [], "optimization_suggestions": []}

    if operation == "list_targets":
        healthy = result.get("healthy_targets", 0)
        total = result.get("target_count", 0)
        if total > 0 and (healthy / total) < 0.9:
            insights["recommendations"].append(
                "Consider reviewing target configurations for unhealthy endpoints"
            )

    elif operation == "list_alerts":
        summary = result.get("alert_summary", {})
        firing = summary.get("firing", 0)
        if firing > 5:
            insights["alerting_opportunities"].append(
                "Consider creating alert silences for maintenance windows or known issues"
            )

    elif operation == "query_metrics":
        count = result.get("result_count", 0)
        if count == 0:
            insights["optimization_suggestions"].append(
                "Try broadening your time range or checking metric name spelling"
            )
        elif count > 1000:
            insights["optimization_suggestions"].append(
                "Consider narrowing your query with more specific selectors for better performance"
            )

    elif operation == "analyze_metrics":
        analysis = result.get("analysis", {})
        anomalies = analysis.get("anomalies", [])
        if anomalies:
            insights["alerting_opportunities"].append(
                f"Consider setting up alerts for {len(anomalies)} detected anomaly patterns"
            )

    return insights


def _analyze_metrics_data(metrics_data: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
    """Analyze metrics data for patterns and anomalies."""
    data = metrics_data.get("data", {})
    result = data.get("result", [])

    analysis = {
        "total_series": len(result),
        "anomalies": [],
        "patterns": [],
        "summary": "Metrics analysis completed.",
        "recommendations": [],
    }

    # Basic analysis - could be enhanced with statistical methods
    if result:
        # Check for missing data points
        for series in result:
            values = series.get("values", [])
            if len(values) < 5:  # Arbitrary threshold
                analysis["anomalies"].append(
                    {
                        "type": "sparse_data",
                        "metric": series.get("metric", {}),
                        "description": f"Only {len(values)} data points found - may indicate collection issues",
                    }
                )

        # Check for zero values that might indicate problems
        for series in result:
            values = series.get("values", [])
            zero_count = sum(1 for _, val in values if float(val) == 0)
            if zero_count > len(values) * 0.8:  # More than 80% zeros
                analysis["anomalies"].append(
                    {
                        "type": "mostly_zero",
                        "metric": series.get("metric", {}),
                        "description": f"Metric shows mostly zero values ({zero_count}/{len(values)} points)",
                    }
                )

    if not analysis["anomalies"]:
        analysis["summary"] = "No significant anomalies detected in the metrics data."
    else:
        analysis["summary"] = (
            f"Found {len(analysis['anomalies'])} potential issues in your metrics."
        )

    return analysis


def _analyze_query_performance(query: str) -> list[dict[str, str]]:
    """Analyze PromQL query for performance optimization opportunities."""
    optimizations = []

    # Basic PromQL optimization checks
    if (
        "rate(" in query and "[5m]" in query and "irate(" not in query
    ):  # irate is more appropriate for recent data
        optimizations.append(
            {
                "type": "rate_vs_irate",
                "description": "Consider using irate() instead of rate() for recent time ranges",
                "suggestion": query.replace("rate(", "irate("),
            }
        )

    if "sum(" in query and "by (" not in query:
        optimizations.append(
            {
                "type": "missing_grouping",
                "description": "High-cardinality sum() without 'by' clause may cause performance issues",
                "suggestion": "Add 'by (label)' clause to reduce cardinality",
            }
        )

    if len(query) > 200:
        optimizations.append(
            {
                "type": "complex_query",
                "description": "Query is quite complex - consider breaking into subqueries or using recording rules",
                "suggestion": "Consider creating recording rules for complex expressions",
            }
        )

    if not optimizations:
        optimizations.append(
            {
                "type": "optimization",
                "description": "Query appears well-optimized",
                "suggestion": "No optimizations needed",
            }
        )

    return optimizations
