"""
Cross-System Correlation Tool

Intelligent correlation of metrics, logs, and traces across Grafana, Prometheus, and Loki
for comprehensive system observability and root cause analysis.

PORTMANTEAU PATTERN: Consolidates correlation operations into a single tool
to provide unified insights across monitoring systems.
"""

import logging
from typing import Any, Literal

from fastmcp import FastMCP
from py_key_value_aio import AbstractStore

from monitoring_mcp.config import MonitoringConfig

from .grafana_tool import GrafanaClient
from .loki_tool import LokiClient
from .prometheus_tool import PrometheusClient

logger = logging.getLogger(__name__)

# Correlation operations supported by this portmanteau tool
CORRELATION_OPERATIONS = {
    "correlate_incident": "Correlate metrics, logs, and traces for incident analysis",
    "find_root_cause": "AI-powered root cause analysis across systems",
    "performance_correlation": "Correlate performance metrics with system events",
    "error_correlation": "Link error logs with relevant metrics and traces",
    "anomaly_correlation": "Connect anomalous metrics with log patterns",
    "service_dependency_map": "Map service dependencies and interactions",
    "impact_analysis": "Analyze the impact of changes or incidents",
    "predictive_insights": "Generate predictive insights from correlation patterns",
    "health_assessment": "Comprehensive system health assessment",
    "bottleneck_detection": "Identify performance bottlenecks across systems",
}


async def register_correlation_tool(
    mcp: FastMCP,
    _storage: AbstractStore,
    config: MonitoringConfig,
) -> None:
    """Register the cross-system correlation tool with the MCP server."""

    grafana_client = GrafanaClient(config)
    prometheus_client = PrometheusClient(config)
    loki_client = LokiClient(config)

    @mcp.tool()
    async def cross_system_correlation(
        operation: Literal[
            "correlate_incident",
            "find_root_cause",
            "performance_correlation",
            "error_correlation",
            "anomaly_correlation",
            "service_dependency_map",
            "impact_analysis",
            "predictive_insights",
            "health_assessment",
            "bottleneck_detection",
        ],
        time_range: dict[str, str] | None = None,
        service_name: str | None = None,
        incident_description: str | None = None,
        error_pattern: str | None = None,
        metric_query: str | None = None,
        log_query: str | None = None,
        correlation_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Intelligent cross-system correlation tool leveraging FastMCP 2.14.3.

        PORTMANTEAU PATTERN: Consolidates 10 correlation operations into a single tool
        to provide unified insights across Grafana, Prometheus, and Loki systems.

        Provides AI-powered correlation analysis, root cause detection, and conversational
        insights for comprehensive system observability.

        Args:
            operation: The correlation operation to perform
            time_range: Time range for analysis (start/end timestamps)
            service_name: Name of service to analyze
            incident_description: Description of incident for correlation
            error_pattern: Error pattern to correlate with metrics
            metric_query: PromQL query for metric correlation
            log_query: LogQL query for log correlation
            correlation_context: Additional context for correlation analysis

        Returns:
            Dict containing correlation results with conversational summary and insights
        """
        try:
            if operation not in CORRELATION_OPERATIONS:
                return {
                    "success": False,
                    "error": f"Invalid operation '{operation}'. Available: {list(CORRELATION_OPERATIONS.keys())}",
                    "conversational_summary": f"I don't recognize the '{operation}' operation. Here are the available correlation operations I can help with.",
                    "available_operations": list(CORRELATION_OPERATIONS.keys()),
                }

            logger.info(f"Executing correlation operation: {operation}")

            # Execute the correlation operation
            result = await _execute_correlation_operation(
                operation,
                grafana_client,
                prometheus_client,
                loki_client,
                time_range,
                service_name,
                incident_description,
                error_pattern,
                metric_query,
                log_query,
                correlation_context,
            )

            # Add conversational insights
            result["conversational_summary"] = _generate_correlation_summary(operation, result)

            # Add AI-powered recommendations
            result["ai_insights"] = _generate_correlation_insights(operation, result)

            return result

        except Exception as e:
            logger.error(f"Error in correlation operation '{operation}': {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to execute correlation operation '{operation}': {e!s}",
                "conversational_summary": f"I encountered an error while performing the {operation.replace('_', ' ')} analysis. This might be due to connectivity issues with your monitoring systems or insufficient data. Please check your configurations and try again.",
                "troubleshooting_tips": [
                    "Verify all monitoring systems (Grafana, Prometheus, Loki) are accessible",
                    "Ensure time ranges are valid and not too broad",
                    "Check that service names and queries are correct",
                    "Try narrowing your analysis scope if dealing with large datasets",
                ],
            }


async def _execute_correlation_operation(
    operation: str,
    grafana_client: GrafanaClient,
    prometheus_client: PrometheusClient,
    loki_client: LokiClient,
    time_range: dict[str, str] | None = None,
    service_name: str | None = None,
    incident_description: str | None = None,
    error_pattern: str | None = None,
    metric_query: str | None = None,
    log_query: str | None = None,
    correlation_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute the specific correlation operation."""

    # Set defaults
    time_range = time_range or {"start": "now-1h", "end": "now"}
    correlation_context = correlation_context or {}

    if operation == "correlate_incident":
        if not incident_description:
            raise ValueError("incident_description is required for correlate_incident")

        # Gather data from all systems
        start_time = time_range.get("start", "now-1h")
        end_time = time_range.get("end", "now")

        # Query metrics for the time range
        metrics_query = metric_query or f'up{{job=~"{service_name or ".*"}"}}'
        metrics_data = await prometheus_client.query_range(metrics_query, start_time, end_time)

        # Query logs for errors related to the incident
        logs_query = log_query or f'{{job=~"{service_name or ".*"}"}} |= "{incident_description}"'
        logs_data = await loki_client.query_range(logs_query, start_time, end_time)

        # Correlate the data
        correlation = _correlate_incident_data(metrics_data, logs_data, incident_description)

        return {
            "success": True,
            "operation": "correlate_incident",
            "correlation": correlation,
            "data_sources": {
                "metrics": {
                    "query": metrics_query,
                    "result_count": len(metrics_data.get("data", {}).get("result", [])),
                },
                "logs": {
                    "query": logs_query,
                    "stream_count": len(logs_data.get("data", {}).get("result", [])),
                },
            },
            "time_range": time_range,
        }

    elif operation == "find_root_cause":
        # Use AI-powered root cause analysis
        start_time = time_range.get("start", "now-1h")
        end_time = time_range.get("end", "now")

        # Gather comprehensive data
        metrics_data = await prometheus_client.query_range(
            metric_query or 'rate(http_requests_total{status=~"5.."}[5m]) > 0', start_time, end_time
        )

        logs_data = await loki_client.query_range(
            log_query or '{job=~".*"} |= "ERROR" or "Exception" or "Failed"', start_time, end_time
        )

        root_cause_analysis = _analyze_root_cause(metrics_data, logs_data, correlation_context)

        return {
            "success": True,
            "operation": "find_root_cause",
            "analysis": root_cause_analysis,
            "confidence_score": root_cause_analysis.get("confidence", 0),
            "time_range": time_range,
        }

    elif operation == "performance_correlation":
        # Correlate performance metrics with system events
        start_time = time_range.get("start", "now-1h")
        end_time = time_range.get("end", "now")

        # Get performance metrics
        perf_query = (
            metric_query
            or "rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])"
        )
        perf_data = await prometheus_client.query_range(perf_query, start_time, end_time)

        # Get related logs
        perf_logs_query = log_query or '{job=~".*"} |= "slow" or "timeout" or "performance"'
        perf_logs = await loki_client.query_range(perf_logs_query, start_time, end_time)

        correlation = _correlate_performance_data(perf_data, perf_logs)

        return {
            "success": True,
            "operation": "performance_correlation",
            "correlation": correlation,
            "performance_score": correlation.get("overall_performance_score", 0),
            "bottlenecks_identified": len(correlation.get("bottlenecks", [])),
            "time_range": time_range,
        }

    elif operation == "error_correlation":
        # Link error logs with relevant metrics
        start_time = time_range.get("start", "now-1h")
        end_time = time_range.get("end", "now")

        # Get error metrics
        error_metrics_query = metric_query or 'rate(http_requests_total{status=~"5.."}[5m])'
        error_metrics = await prometheus_client.query_range(
            error_metrics_query, start_time, end_time
        )

        # Get error logs
        error_logs_query = log_query or error_pattern or '{job=~".*"} |= "ERROR" or "Exception"'
        error_logs = await loki_client.query_range(error_logs_query, start_time, end_time)

        correlation = _correlate_error_data(error_metrics, error_logs)

        return {
            "success": True,
            "operation": "error_correlation",
            "correlation": correlation,
            "error_clusters": len(correlation.get("error_clusters", [])),
            "affected_services": correlation.get("affected_services", []),
            "time_range": time_range,
        }

    elif operation == "health_assessment":
        # Comprehensive system health assessment
        health_assessment = await _perform_health_assessment(
            grafana_client, prometheus_client, loki_client, time_range, service_name
        )

        return {
            "success": True,
            "operation": "health_assessment",
            "assessment": health_assessment,
            "overall_health_score": health_assessment.get("overall_score", 0),
            "critical_issues": len(health_assessment.get("critical_issues", [])),
            "recommendations": health_assessment.get("recommendations", []),
            "time_range": time_range,
        }

    # Placeholder implementations for remaining operations
    elif operation in [
        "anomaly_correlation",
        "service_dependency_map",
        "impact_analysis",
        "predictive_insights",
        "bottleneck_detection",
    ]:
        return {
            "success": False,
            "operation": operation,
            "error": f"Operation '{operation}' is not yet implemented",
            "note": "This operation is planned for a future version",
        }

    else:
        raise ValueError(f"Unsupported operation: {operation}")


def _generate_correlation_summary(operation: str, result: dict[str, Any]) -> str:
    """Generate conversational summary for correlation operation results."""
    if not result.get("success"):
        return f"I wasn't able to complete the {operation.replace('_', ' ')} analysis. {result.get('error', 'Unknown error occurred')}."

    if operation == "correlate_incident":
        correlation = result.get("correlation", {})
        insights = len(correlation.get("insights", []))
        return f"I analyzed the incident '{result.get('correlation', {}).get('incident_description', 'unknown')}' and found {insights} correlation insight{'s' if insights != 1 else ''}. Here's what I discovered about the relationships between your metrics and logs."

    elif operation == "find_root_cause":
        analysis = result.get("analysis", {})
        confidence = result.get("confidence_score", 0)
        root_causes = len(analysis.get("potential_root_causes", []))
        confidence_desc = "high" if confidence > 80 else "medium" if confidence > 60 else "low"
        return f"I performed root cause analysis and identified {root_causes} potential root cause{'s' if root_causes != 1 else ''} with {confidence_desc} confidence. Here's my assessment of what might be causing the issues."

    elif operation == "performance_correlation":
        correlation = result.get("correlation", {})
        score = result.get("performance_score", 0)
        bottlenecks = result.get("bottlenecks_identified", 0)
        perf_desc = (
            "excellent"
            if score > 90
            else "good"
            if score > 75
            else "concerning"
            if score > 50
            else "poor"
        )
        return f"I analyzed your system performance and found {bottlenecks} potential bottleneck{'s' if bottlenecks != 1 else ''}. Overall performance is {perf_desc} with a score of {score}/100."

    elif operation == "error_correlation":
        correlation = result.get("correlation", {})
        clusters = result.get("error_clusters", 0)
        services = len(result.get("affected_services", []))
        return f"I correlated errors across your systems and found {clusters} error cluster{'s' if clusters != 1 else ''} affecting {services} service{'s' if services != 1 else ''}. Here's the breakdown of what's going wrong."

    elif operation == "health_assessment":
        score = result.get("overall_health_score", 0)
        critical = result.get("critical_issues", 0)
        health_desc = (
            "excellent"
            if score > 90
            else "good"
            if score > 75
            else "fair"
            if score > 50
            else "poor"
        )
        return f"I performed a comprehensive health assessment and gave your system an overall score of {score}/100 ({health_desc}). There are {critical} critical issue{'s' if critical != 1 else ''} that need{'s' if critical == 1 else ''} attention."

    else:
        return f"The {operation.replace('_', ' ')} analysis completed successfully."


def _generate_correlation_insights(operation: str, result: dict[str, Any]) -> dict[str, Any]:
    """Generate AI-powered insights for correlation operations."""
    insights = {"recommendations": [], "alerting_opportunities": [], "investigation_priorities": []}

    if operation == "correlate_incident":
        correlation = result.get("correlation", {})
        insights_found = correlation.get("insights", [])
        if insights_found:
            insights["investigation_priorities"].append(
                f"Focus on the {len(insights_found)} correlation insights identified"
            )

    elif operation == "find_root_cause":
        confidence = result.get("confidence_score", 0)
        if confidence > 80:
            insights["recommendations"].append(
                "High-confidence root cause identified - consider immediate remediation"
            )

    elif operation == "performance_correlation":
        bottlenecks = result.get("bottlenecks_identified", 0)
        if bottlenecks > 0:
            insights["recommendations"].append(
                f"Address {bottlenecks} performance bottleneck{'s' if bottlenecks != 1 else ''} to improve system responsiveness"
            )

    elif operation == "error_correlation":
        clusters = result.get("error_clusters", 0)
        if clusters > 3:
            insights["alerting_opportunities"].append(
                f"Consider setting up alerts for the {clusters} error patterns identified"
            )

    elif operation == "health_assessment":
        score = result.get("overall_health_score", 0)
        critical = result.get("critical_issues", 0)
        if score < 70:
            insights["recommendations"].append(
                f"Overall health score of {score}/100 indicates immediate attention needed"
            )
        if critical > 0:
            insights["investigation_priorities"].append(
                f"Address {critical} critical issue{'s' if critical != 1 else ''} immediately"
            )

    return insights


def _correlate_incident_data(
    metrics_data: dict[str, Any], logs_data: dict[str, Any], incident_description: str
) -> dict[str, Any]:
    """Correlate metrics and logs for incident analysis."""
    correlation = {
        "incident_description": incident_description,
        "insights": [],
        "correlation_strength": "weak",
        "time_correlation": {},
        "summary": "Incident correlation analysis completed.",
    }

    # Analyze metrics for anomalies around incident time
    metrics_result = metrics_data.get("data", {}).get("result", [])
    if metrics_result:
        correlation["insights"].append(
            {
                "type": "metrics_context",
                "description": f"Found {len(metrics_result)} metric series related to the incident timeframe",
                "severity": "info",
            }
        )

    # Analyze logs for incident-related messages
    logs_result = logs_data.get("data", {}).get("result", [])
    total_log_entries = sum(len(stream.get("values", [])) for stream in logs_result)

    if total_log_entries > 0:
        correlation["insights"].append(
            {
                "type": "logs_context",
                "description": f"Found {total_log_entries} log entries related to the incident across {len(logs_result)} streams",
                "severity": "info",
            }
        )

    # Basic correlation strength assessment
    if len(metrics_result) > 0 and total_log_entries > 0:
        correlation["correlation_strength"] = "moderate"
        correlation["summary"] = "Found both metrics and logs correlated with the incident."
    elif len(metrics_result) > 0:
        correlation["correlation_strength"] = "metric-focused"
        correlation["summary"] = "Incident correlation based primarily on metrics data."
    elif total_log_entries > 0:
        correlation["correlation_strength"] = "log-focused"
        correlation["summary"] = "Incident correlation based primarily on log data."
    else:
        correlation["summary"] = "Limited correlation data found for the incident."

    return correlation


def _analyze_root_cause(
    metrics_data: dict[str, Any], logs_data: dict[str, Any], _context: dict[str, Any]
) -> dict[str, Any]:
    """AI-powered root cause analysis."""
    analysis = {
        "potential_root_causes": [],
        "confidence": 65,
        "evidence": [],
        "recommendations": [],
        "summary": "Root cause analysis completed.",
    }

    # Analyze metrics for patterns
    metrics_result = metrics_data.get("data", {}).get("result", [])
    error_rate_found = any(
        "error" in str(series.get("metric", {})).lower() for series in metrics_result
    )

    # Analyze logs for error patterns
    logs_result = logs_data.get("data", {}).get("result", [])
    error_logs_found = any(
        any(
            "ERROR" in str(entry[1]).upper() or "Exception" in str(entry[1])
            for entry in stream.get("values", [])
        )
        for stream in logs_result
    )

    # Determine root causes based on patterns
    if error_rate_found and error_logs_found:
        analysis["potential_root_causes"].append(
            {
                "cause": "Application errors",
                "confidence": 85,
                "evidence": ["High error rates in metrics", "Error messages in logs"],
                "recommendation": "Check application logs and error handling",
            }
        )
    elif error_logs_found:
        analysis["potential_root_causes"].append(
            {
                "cause": "Logging errors",
                "confidence": 70,
                "evidence": ["Error messages in logs"],
                "recommendation": "Review log aggregation and application error handling",
            }
        )

    if not analysis["potential_root_causes"]:
        analysis["potential_root_causes"].append(
            {
                "cause": "Insufficient monitoring data",
                "confidence": 50,
                "evidence": ["Limited correlation data available"],
                "recommendation": "Expand monitoring coverage and data collection",
            }
        )

    # Update confidence based on evidence strength
    if len(analysis["potential_root_causes"]) > 0:
        max_confidence = max(cause["confidence"] for cause in analysis["potential_root_causes"])
        analysis["confidence"] = max_confidence

    return analysis


def _correlate_performance_data(
    perf_data: dict[str, Any], perf_logs: dict[str, Any]
) -> dict[str, Any]:
    """Correlate performance metrics with system events."""
    correlation = {
        "overall_performance_score": 75,
        "bottlenecks": [],
        "performance_trends": [],
        "system_events": [],
        "summary": "Performance correlation analysis completed.",
    }

    # Analyze performance metrics
    perf_result = perf_data.get("data", {}).get("result", [])
    if perf_result:
        # Look for high latency indicators
        high_latency_series = [
            series
            for series in perf_result
            if any(float(point[1]) > 1.0 for point in series.get("values", []))  # > 1 second
        ]

        if high_latency_series:
            correlation["bottlenecks"].append(
                {
                    "type": "high_latency",
                    "description": f"Found {len(high_latency_series)} services with high latency",
                    "severity": "medium",
                }
            )

    # Analyze performance-related logs
    logs_result = perf_logs.get("data", {}).get("result", [])
    perf_issues = sum(
        len([entry for entry in stream.get("values", []) if "slow" in str(entry[1]).lower()])
        for stream in logs_result
    )

    if perf_issues > 0:
        correlation["bottlenecks"].append(
            {
                "type": "performance_logs",
                "description": f"Found {perf_issues} performance-related log entries",
                "severity": "low",
            }
        )

    # Calculate overall score
    bottleneck_count = len(correlation["bottlenecks"])
    if bottleneck_count == 0:
        correlation["overall_performance_score"] = 95
        correlation["summary"] = (
            "System performance appears healthy with no significant bottlenecks detected."
        )
    elif bottleneck_count <= 2:
        correlation["overall_performance_score"] = 80
        correlation["summary"] = (
            "System performance is acceptable with minor bottlenecks to address."
        )
    else:
        correlation["overall_performance_score"] = 60
        correlation["summary"] = "System performance has multiple bottlenecks requiring attention."

    return correlation


def _correlate_error_data(
    error_metrics: dict[str, Any], error_logs: dict[str, Any]
) -> dict[str, Any]:
    """Link error logs with relevant metrics."""
    correlation = {
        "error_clusters": [],
        "affected_services": [],
        "error_timeline": [],
        "correlation_strength": "weak",
        "summary": "Error correlation analysis completed.",
    }

    # Analyze error metrics
    metrics_result = error_metrics.get("data", {}).get("result", [])
    error_metrics_count = len(metrics_result)

    # Analyze error logs
    logs_result = error_logs.get("data", {}).get("result", [])
    error_logs_count = sum(len(stream.get("values", [])) for stream in logs_result)

    if error_metrics_count > 0:
        correlation["error_clusters"].append(
            {
                "type": "metrics_errors",
                "count": error_metrics_count,
                "description": f"Found {error_metrics_count} error metrics series",
            }
        )

    if error_logs_count > 0:
        correlation["error_clusters"].append(
            {
                "type": "log_errors",
                "count": error_logs_count,
                "description": f"Found {error_logs_count} error log entries",
            }
        )

    # Extract affected services from metrics
    for series in metrics_result:
        service_name = series.get("metric", {}).get("service", "unknown")
        if service_name not in correlation["affected_services"]:
            correlation["affected_services"].append(service_name)

    # Determine correlation strength
    if error_metrics_count > 0 and error_logs_count > 0:
        correlation["correlation_strength"] = "strong"
        correlation["summary"] = "Strong correlation found between error metrics and logs."
    elif error_metrics_count > 0 or error_logs_count > 0:
        correlation["correlation_strength"] = "moderate"
        correlation["summary"] = "Moderate correlation found in error data."
    else:
        correlation["summary"] = "No significant error patterns found in the analyzed data."

    return correlation


async def _perform_health_assessment(
    grafana_client: GrafanaClient,
    prometheus_client: PrometheusClient,
    loki_client: LokiClient,
    _time_range: dict[str, str],
    _service_name: str | None = None,
) -> dict[str, Any]:
    """Perform comprehensive system health assessment."""
    assessment = {
        "overall_score": 85,
        "critical_issues": [],
        "warning_issues": [],
        "system_components": {},
        "recommendations": [],
        "summary": "Health assessment completed.",
    }

    try:
        # Check Prometheus targets
        targets_data = await prometheus_client.targets()
        targets = targets_data.get("data", {}).get("activeTargets", [])
        healthy_targets = sum(1 for t in targets if t.get("health") == "up")
        total_targets = len(targets)

        if total_targets > 0:
            health_percentage = (healthy_targets / total_targets) * 100
            assessment["system_components"]["prometheus_targets"] = {
                "status": "healthy" if health_percentage > 90 else "degraded",
                "score": health_percentage,
                "details": f"{healthy_targets}/{total_targets} targets healthy",
            }

            if health_percentage < 80:
                assessment["critical_issues"].append(
                    {
                        "component": "prometheus_targets",
                        "issue": f"Only {health_percentage:.1f}% of targets are healthy",
                        "severity": "critical",
                    }
                )

    except Exception as e:
        assessment["critical_issues"].append(
            {
                "component": "prometheus",
                "issue": f"Unable to connect to Prometheus: {e!s}",
                "severity": "critical",
            }
        )

    try:
        # Check Loki labels
        labels_data = await loki_client.labels()
        label_count = len(labels_data.get("data", []))

        assessment["system_components"]["loki_labels"] = {
            "status": "healthy" if label_count > 0 else "degraded",
            "score": min(label_count * 10, 100),  # Rough scoring
            "details": f"{label_count} labels available",
        }

    except Exception as e:
        assessment["warning_issues"].append(
            {
                "component": "loki",
                "issue": f"Unable to connect to Loki: {e!s}",
                "severity": "warning",
            }
        )

    try:
        # Check Grafana datasources
        datasources = await grafana_client.list_datasources()
        datasource_count = len(datasources)

        assessment["system_components"]["grafana_datasources"] = {
            "status": "healthy" if datasource_count >= 2 else "warning",
            "score": min(datasource_count * 25, 100),
            "details": f"{datasource_count} datasources configured",
        }

    except Exception as e:
        assessment["warning_issues"].append(
            {
                "component": "grafana",
                "issue": f"Unable to connect to Grafana: {e!s}",
                "severity": "warning",
            }
        )

    # Calculate overall score
    component_scores = [
        comp.get("score", 0)
        for comp in assessment["system_components"].values()
        if isinstance(comp, dict) and "score" in comp
    ]

    if component_scores:
        assessment["overall_score"] = sum(component_scores) // len(component_scores)
    else:
        assessment["overall_score"] = 0

    # Generate recommendations
    if assessment["overall_score"] < 70:
        assessment["recommendations"].append(
            "Overall system health is concerning - review critical issues above"
        )

    if assessment["critical_issues"]:
        assessment["recommendations"].append(
            f"Address {len(assessment['critical_issues'])} critical issues immediately"
        )

    if assessment["overall_score"] >= 90:
        assessment["summary"] = "System health is excellent across all monitored components."
    elif assessment["overall_score"] >= 75:
        assessment["summary"] = "System health is good with some areas for improvement."
    elif assessment["overall_score"] >= 50:
        assessment["summary"] = "System health requires attention with multiple issues to address."
    else:
        assessment["summary"] = "System health is poor and requires immediate intervention."

    return assessment
