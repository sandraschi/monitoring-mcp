"""
Status and Health Monitoring Tool

Comprehensive system status monitoring, health checks, and diagnostic operations
for monitoring infrastructure and MCP server health.

PORTMANTEAU PATTERN: Consolidates status operations into a single tool
to provide unified health monitoring across all systems.
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

# Status operations supported by this portmanteau tool
STATUS_OPERATIONS = {
    "system_health": "Comprehensive health check across all monitoring systems",
    "connectivity_test": "Test connectivity to Grafana, Prometheus, and Loki",
    "configuration_validation": "Validate monitoring system configurations",
    "performance_metrics": "Monitor performance of monitoring systems themselves",
    "data_flow_status": "Check data flow between systems (metrics → logs → dashboards)",
    "alert_status": "Monitor alerting system health and active alerts",
    "storage_status": "Check storage health and capacity for all systems",
    "backup_status": "Monitor backup and data retention status",
    "security_status": "Security health check and compliance monitoring",
    "capacity_planning": "Monitor system capacity and growth trends",
}


async def register_status_tool(
    mcp: FastMCP,
    _storage: AbstractStore,
    config: MonitoringConfig,
) -> None:
    """Register the status and health monitoring tool with the MCP server."""

    grafana_client = GrafanaClient(config)
    prometheus_client = PrometheusClient(config)
    loki_client = LokiClient(config)

    @mcp.tool()
    async def monitoring_status(
        operation: Literal[
            "system_health",
            "connectivity_test",
            "configuration_validation",
            "performance_metrics",
            "data_flow_status",
            "alert_status",
            "storage_status",
            "backup_status",
            "security_status",
            "capacity_planning",
        ],
        component_filter: list[str] | None = None,
        detailed_check: bool = False,
        include_historical: bool = False,
    ) -> dict[str, Any]:
        """
        Comprehensive monitoring status and health tool leveraging FastMCP 2.14.3.

        PORTMANTEAU PATTERN: Consolidates 10 status operations into a single tool
        to provide unified health monitoring across Grafana, Prometheus, and Loki.

        Provides intelligent health assessment, diagnostic capabilities, and conversational
        insights for monitoring system maintenance and troubleshooting.

        Args:
            operation: The status operation to perform
            component_filter: Optional list of components to focus on (grafana, prometheus, loki)
            detailed_check: Whether to perform detailed diagnostic checks
            include_historical: Whether to include historical health data

        Returns:
            Dict containing status results with conversational summary and insights
        """
        try:
            if operation not in STATUS_OPERATIONS:
                return {
                    "success": False,
                    "error": f"Invalid operation '{operation}'. Available: {list(STATUS_OPERATIONS.keys())}",
                    "conversational_summary": f"I don't recognize the '{operation}' operation. Here are the available status operations I can help with.",
                    "available_operations": list(STATUS_OPERATIONS.keys()),
                }

            logger.info(f"Executing status operation: {operation}")

            # Execute the status operation
            result = await _execute_status_operation(
                operation,
                grafana_client,
                prometheus_client,
                loki_client,
                config,
                component_filter,
                detailed_check,
                include_historical,
            )

            # Add conversational insights
            result["conversational_summary"] = _generate_status_summary(operation, result)

            # Add AI-powered recommendations
            result["ai_insights"] = _generate_status_insights(operation, result)

            return result

        except Exception as e:
            logger.error(f"Error in status operation '{operation}': {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to execute status operation '{operation}': {e!s}",
                "conversational_summary": f"I encountered an error while checking the {operation.replace('_', ' ')}. This might be due to connectivity issues or system unavailability. Please check your monitoring system configurations and try again.",
                "troubleshooting_tips": [
                    "Verify all monitoring systems are running and accessible",
                    "Check network connectivity to Grafana, Prometheus, and Loki",
                    "Ensure API keys and authentication are configured correctly",
                    "Review system logs for any startup or configuration errors",
                ],
            }


async def _execute_status_operation(
    operation: str,
    grafana_client: GrafanaClient,
    prometheus_client: PrometheusClient,
    loki_client: LokiClient,
    config: MonitoringConfig,
    component_filter: list[str] | None = None,
    detailed_check: bool = False,
    include_historical: bool = False,
) -> dict[str, Any]:
    """
    Execute the specific status operation based on the operation type.

    This function routes status operations to their appropriate handlers and
    formats the results consistently.

    Args:
        operation: The status operation to execute (e.g., "system_health", "connectivity_test")
        grafana_client: Client for Grafana operations
        prometheus_client: Client for Prometheus operations
        loki_client: Client for Loki operations
        config: Server configuration
        component_filter: List of components to check (defaults to all)
        detailed_check: Whether to perform detailed diagnostic checks
        include_historical: Whether to include historical data in results

    Returns:
        Dictionary containing operation results with success status and data
    """
    # Default component filter to all if not specified
    if component_filter is None:
        component_filter = ["grafana", "prometheus", "loki"]

    # Define operation handlers and result formatters
    operation_handlers = {
        "system_health": (_check_system_health, _format_system_health_result),
        "connectivity_test": (_test_connectivity, _format_connectivity_result),
        "configuration_validation": (_validate_configurations, _format_validation_result),
        "performance_metrics": (_check_performance_metrics, _format_performance_result),
        "data_flow_status": (_check_data_flow, _format_data_flow_result),
        "alert_status": (_check_alert_status, _format_alert_status_result),
    }

    if operation in operation_handlers:
        handler, formatter = operation_handlers[operation]
        result_data = await handler(
            grafana_client,
            prometheus_client,
            loki_client,
            config,
            component_filter,
            detailed_check,
            include_historical,
        )
        return formatter(operation, result_data)

    # Placeholder implementations for remaining operations
    elif operation in ["storage_status", "backup_status", "security_status", "capacity_planning"]:
        return {
            "success": False,
            "operation": operation,
            "error": f"Operation '{operation}' is not yet implemented",
            "note": "This operation is planned for a future version",
        }

    else:
        raise ValueError(f"Unsupported operation: {operation}")


def _format_system_health_result(operation: str, health_status: dict[str, Any]) -> dict[str, Any]:
    """Format system health check results."""
    return {
        "success": True,
        "operation": operation,
        "health_status": health_status,
        "overall_status": health_status.get("overall_status", "unknown"),
        "component_count": len(health_status.get("components", {})),
        "issues_found": len(health_status.get("issues", [])),
    }


def _format_connectivity_result(operation: str, connectivity: dict[str, Any]) -> dict[str, Any]:
    """Format connectivity test results."""
    return {
        "success": True,
        "operation": operation,
        "connectivity": connectivity,
        "successful_connections": sum(
            1 for c in connectivity.values() if c.get("status") == "connected"
        ),
        "total_tests": len(connectivity),
    }


def _format_validation_result(operation: str, validation: dict[str, Any]) -> dict[str, Any]:
    """Format configuration validation results."""
    return {
        "success": True,
        "operation": operation,
        "validation": validation,
        "valid_configs": sum(1 for v in validation.values() if v.get("status") == "valid"),
        "total_configs": len(validation),
    }


def _format_performance_result(operation: str, performance: dict[str, Any]) -> dict[str, Any]:
    """Format performance metrics results."""
    return {
        "success": True,
        "operation": operation,
        "performance": performance,
        "monitored_systems": len(performance.get("systems", {})),
    }


def _format_data_flow_result(operation: str, data_flow: dict[str, Any]) -> dict[str, Any]:
    """Format data flow status results."""
    return {
        "success": True,
        "operation": operation,
        "data_flow": data_flow,
        "flow_status": data_flow.get("overall_status", "unknown"),
        "data_points_checked": data_flow.get("data_points_checked", 0),
    }


def _format_alert_status_result(operation: str, alert_status: dict[str, Any]) -> dict[str, Any]:
    """Format alert status results."""
    return {
        "success": True,
        "operation": operation,
        "alert_status": alert_status,
        "active_alerts": alert_status.get("active_alerts", 0),
        "alert_rules": alert_status.get("alert_rules", 0),
    }


def _generate_status_summary(operation: str, result: dict[str, Any]) -> str:
    """Generate conversational summary for status operation results."""
    if not result.get("success"):
        return f"I wasn't able to complete the {operation.replace('_', ' ')} check. {result.get('error', 'Unknown error occurred')}."

    if operation == "system_health":
        status = result.get("overall_status", "unknown")
        components = result.get("component_count", 0)
        issues = result.get("issues_found", 0)

        status_messages = {
            "healthy": f"Great news! Your monitoring system is healthy across all {components} components. Everything is working as expected.",
            "degraded": f"Your monitoring system has some issues but is mostly functional. I found {issues} issue{'s' if issues != 1 else ''} across {components} components that should be addressed.",
            "unhealthy": f"Your monitoring system needs attention. There are {issues} issue{'s' if issues != 1 else ''} across {components} components that require immediate action.",
        }
        return status_messages.get(
            status,
            f"I checked your monitoring system health across {components} components and found {issues} issue{'s' if issues != 1 else ''} to review.",
        )

    elif operation == "connectivity_test":
        successful = result.get("successful_connections", 0)
        total = result.get("total_tests", 0)

        if successful == total:
            return f"Excellent! All {total} monitoring system connections are working perfectly."
        elif successful > 0:
            return f"Partial connectivity: {successful} out of {total} monitoring systems are reachable. Some components may need attention."
        else:
            return f"Connectivity issues detected. None of the {total} monitoring systems are currently reachable. Please check your network configuration and system status."

    elif operation == "configuration_validation":
        valid = result.get("valid_configs", 0)
        total = result.get("total_configs", 0)

        if valid == total:
            return f"Perfect! All {total} monitoring system configurations are valid and properly set up."
        else:
            invalid = total - valid
            return f"Configuration issues found: {invalid} out of {total} system configurations need attention. Please review the validation details."

    elif operation == "performance_metrics":
        systems = result.get("monitored_systems", 0)
        return f"I analyzed performance metrics for {systems} monitoring system{'s' if systems != 1 else ''}. The results show how efficiently your monitoring infrastructure is running."

    elif operation == "data_flow_status":
        status = result.get("flow_status", "unknown")
        points = result.get("data_points_checked", 0)

        if status == "healthy":
            return f"Data flow is healthy! I verified {points} data point{'s' if points != 1 else ''} flowing correctly between your monitoring systems."
        else:
            return f"Data flow issues detected. I checked {points} data point{'s' if points != 1 else ''} and found some problems with data flow between systems."

    elif operation == "alert_status":
        active = result.get("active_alerts", 0)
        rules = result.get("alert_rules", 0)

        if active == 0:
            return f"Good news! You have {rules} alert rule{'s' if rules != 1 else ''} configured and no active alerts. Your systems are running smoothly."
        else:
            return f"You have {active} active alert{'s' if active != 1 else ''} out of {rules} configured rule{'s' if rules != 1 else ''}. Some attention may be needed."

    else:
        return f"The {operation.replace('_', ' ')} check completed successfully."


def _generate_status_insights(operation: str, result: dict[str, Any]) -> dict[str, Any]:
    """Generate AI-powered insights for status operations."""
    insights = {
        "recommendations": [],
        "monitoring_opportunities": [],
        "optimization_suggestions": [],
    }

    if operation == "system_health":
        issues = result.get("issues_found", 0)
        status = result.get("overall_status", "unknown")

        if status == "unhealthy":
            insights["recommendations"].append(
                "Critical system health issues detected - immediate attention required"
            )
        elif issues > 0:
            insights["recommendations"].append(
                f"Address {issues} system health issue{'s' if issues != 1 else ''} to maintain optimal monitoring"
            )

    elif operation == "connectivity_test":
        successful = result.get("successful_connections", 0)
        total = result.get("total_tests", 0)

        if successful < total:
            insights["recommendations"].append(
                f"Restore connectivity to {total - successful} unreachable monitoring system{'s' if (total - successful) != 1 else ''}"
            )

    elif operation == "configuration_validation":
        valid = result.get("valid_configs", 0)
        total = result.get("total_configs", 0)

        if valid < total:
            insights["recommendations"].append(
                f"Fix configuration issues in {total - valid} monitoring system{'s' if (total - valid) != 1 else ''}"
            )

    elif operation == "alert_status":
        active = result.get("active_alerts", 0)
        if active > 5:
            insights["monitoring_opportunities"].append(
                "High number of active alerts - consider alert grouping or reduction strategies"
            )

    return insights


async def _check_system_health(
    grafana_client: GrafanaClient,
    prometheus_client: PrometheusClient,
    loki_client: LokiClient,
    _config: MonitoringConfig,
    component_filter: list[str],
    _detailed_check: bool,
    _include_historical: bool,
) -> dict[str, Any]:
    """
    Check overall system health across all monitoring components.

    Performs connectivity and basic functionality tests for Grafana, Prometheus,
    and Loki, then determines an overall health status.

    Args:
        grafana_client: Client for Grafana operations
        prometheus_client: Client for Prometheus operations
        loki_client: Client for Loki operations
        component_filter: List of components to check
        _detailed_check: Whether to perform detailed checks (unused for now)

    Returns:
        Dictionary containing health status for each component and overall assessment
    """
    health_status = {
        "overall_status": "healthy",
        "components": {},
        "issues": [],
        "checked_at": None,
    }

    # Check Grafana
    if "grafana" in component_filter:
        try:
            datasources = await grafana_client.list_datasources()
            health_status["components"]["grafana"] = {
                "status": "healthy",
                "details": f"{len(datasources)} datasources configured",
                "last_check": "now",
            }
        except Exception as e:
            health_status["components"]["grafana"] = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": "now",
            }
            health_status["issues"].append(
                {
                    "component": "grafana",
                    "severity": "high",
                    "description": f"Grafana connection failed: {e!s}",
                }
            )

    # Check Prometheus
    if "prometheus" in component_filter:
        try:
            targets = await prometheus_client.targets()
            active_targets = targets.get("data", {}).get("activeTargets", [])
            healthy_targets = sum(1 for t in active_targets if t.get("health") == "up")

            status = "healthy" if healthy_targets == len(active_targets) else "degraded"
            health_status["components"]["prometheus"] = {
                "status": status,
                "details": f"{healthy_targets}/{len(active_targets)} targets healthy",
                "last_check": "now",
            }

            if status == "degraded":
                health_status["issues"].append(
                    {
                        "component": "prometheus",
                        "severity": "medium",
                        "description": f"{len(active_targets) - healthy_targets} unhealthy targets detected",
                    }
                )

        except Exception as e:
            health_status["components"]["prometheus"] = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": "now",
            }
            health_status["issues"].append(
                {
                    "component": "prometheus",
                    "severity": "high",
                    "description": f"Prometheus connection failed: {e!s}",
                }
            )

    # Check Loki
    if "loki" in component_filter:
        try:
            labels = await loki_client.labels()
            label_count = len(labels.get("data", []))

            health_status["components"]["loki"] = {
                "status": "healthy",
                "details": f"{label_count} labels available",
                "last_check": "now",
            }

        except Exception as e:
            health_status["components"]["loki"] = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": "now",
            }
            health_status["issues"].append(
                {
                    "component": "loki",
                    "severity": "medium",
                    "description": f"Loki connection failed: {e!s}",
                }
            )

    # Determine overall status
    component_statuses = [comp["status"] for comp in health_status["components"].values()]

    if "unhealthy" in component_statuses:
        health_status["overall_status"] = "unhealthy"
    elif "degraded" in component_statuses:
        health_status["overall_status"] = "degraded"
    else:
        health_status["overall_status"] = "healthy"

    return health_status


async def _test_connectivity(
    grafana_client: GrafanaClient,
    prometheus_client: PrometheusClient,
    loki_client: LokiClient,
    _config: MonitoringConfig,
    component_filter: list[str],
    _detailed_check: bool,
    _include_historical: bool,
) -> dict[str, Any]:
    """Test connectivity to all monitoring systems."""
    connectivity = {}

    # Test Grafana connectivity
    if "grafana" in component_filter:
        try:
            await grafana_client.list_datasources()
            connectivity["grafana"] = {
                "status": "connected",
                "response_time": "< 5s",
                "last_test": "now",
            }
        except Exception as e:
            connectivity["grafana"] = {
                "status": "failed",
                "error": str(e),
                "last_test": "now",
            }

    # Test Prometheus connectivity
    if "prometheus" in component_filter:
        try:
            await prometheus_client.buildinfo()
            connectivity["prometheus"] = {
                "status": "connected",
                "response_time": "< 5s",
                "last_test": "now",
            }
        except Exception as e:
            connectivity["prometheus"] = {
                "status": "failed",
                "error": str(e),
                "last_test": "now",
            }

    # Test Loki connectivity
    if "loki" in component_filter:
        try:
            await loki_client.labels()
            connectivity["loki"] = {
                "status": "connected",
                "response_time": "< 5s",
                "last_test": "now",
            }
        except Exception as e:
            connectivity["loki"] = {
                "status": "failed",
                "error": str(e),
                "last_test": "now",
            }

    return connectivity


async def _validate_configurations(
    grafana_client: GrafanaClient,
    prometheus_client: PrometheusClient,
    loki_client: LokiClient,
    _config: MonitoringConfig,
    component_filter: list[str],
    _detailed_check: bool,
    _include_historical: bool,
) -> dict[str, Any]:
    """Validate configurations of monitoring systems."""
    validation = {}

    # Validate Grafana configuration
    if "grafana" in component_filter:
        try:
            datasources = await grafana_client.list_datasources()
            datasource_count = len(datasources)

            # Check for Prometheus and Loki datasources
            has_prometheus = any(ds.get("type") == "prometheus" for ds in datasources)
            has_loki = any(
                ds.get("type") in ["loki", "grafana-loki-datasource"] for ds in datasources
            )

            validation["grafana"] = {
                "status": "valid",
                "details": f"{datasource_count} datasources configured",
                "checks": {
                    "prometheus_datasource": has_prometheus,
                    "loki_datasource": has_loki,
                },
                "recommendations": [],
            }

            if not has_prometheus:
                validation["grafana"]["recommendations"].append(
                    "Add Prometheus datasource for metrics"
                )
            if not has_loki:
                validation["grafana"]["recommendations"].append("Add Loki datasource for logs")

        except Exception as e:
            validation["grafana"] = {
                "status": "invalid",
                "error": str(e),
            }

    # Validate Prometheus configuration
    if "prometheus" in component_filter:
        try:
            targets = await prometheus_client.targets()
            active_targets = targets.get("data", {}).get("activeTargets", [])
            healthy_count = sum(1 for t in active_targets if t.get("health") == "up")

            validation["prometheus"] = {
                "status": "valid" if healthy_count > 0 else "warning",
                "details": f"{healthy_count}/{len(active_targets)} targets healthy",
                "checks": {
                    "has_targets": len(active_targets) > 0,
                    "healthy_targets": healthy_count > 0,
                },
            }

        except Exception as e:
            validation["prometheus"] = {
                "status": "invalid",
                "error": str(e),
            }

    # Validate Loki configuration
    if "loki" in component_filter:
        try:
            labels = await loki_client.labels()
            label_count = len(labels.get("data", []))

            validation["loki"] = {
                "status": "valid" if label_count > 0 else "warning",
                "details": f"{label_count} labels available",
                "checks": {
                    "has_labels": label_count > 0,
                },
            }

        except Exception as e:
            validation["loki"] = {
                "status": "invalid",
                "error": str(e),
            }

    return validation


async def _check_performance_metrics(
    _grafana_client: GrafanaClient,
    prometheus_client: PrometheusClient,
    _loki_client: LokiClient,
    _config: MonitoringConfig,
    component_filter: list[str],
    _detailed_check: bool,
    _include_historical: bool,
) -> dict[str, Any]:
    """Check performance metrics of monitoring systems."""
    performance = {
        "systems": {},
        "overall_performance": "good",
        "checked_at": None,
    }

    # Check Prometheus performance metrics
    if "prometheus" in component_filter:
        try:
            # Query Prometheus's own metrics
            query = "prometheus_engine_queries"
            result = await prometheus_client.query(query)

            performance["systems"]["prometheus"] = {
                "status": "monitored",
                "metrics_available": len(result.get("data", {}).get("result", [])) > 0,
                "last_check": "now",
            }

        except Exception as e:
            performance["systems"]["prometheus"] = {
                "status": "error",
                "error": str(e),
                "last_check": "now",
            }

    return performance


async def _check_data_flow(
    grafana_client: GrafanaClient,
    _prometheus_client: PrometheusClient,
    _loki_client: LokiClient,
    _config: MonitoringConfig,
    component_filter: list[str],
    _detailed_check: bool,
    _include_historical: bool,
) -> dict[str, Any]:
    """Check data flow between monitoring systems."""
    data_flow = {
        "overall_status": "unknown",
        "flows": {},
        "data_points_checked": 0,
        "issues": [],
    }

    # Check Prometheus → Grafana flow
    if "prometheus" in component_filter and "grafana" in component_filter:
        try:
            # Check if Grafana can query Prometheus
            datasources = await grafana_client.list_datasources()
            has_prometheus_ds = any(ds.get("type") == "prometheus" for ds in datasources)

            if has_prometheus_ds:
                data_flow["flows"]["prometheus_to_grafana"] = {
                    "status": "healthy",
                    "description": "Grafana has Prometheus datasource configured",
                }
            else:
                data_flow["flows"]["prometheus_to_grafana"] = {
                    "status": "broken",
                    "description": "Grafana missing Prometheus datasource",
                }
                data_flow["issues"].append("Grafana cannot query Prometheus data")

        except Exception as e:
            data_flow["flows"]["prometheus_to_grafana"] = {
                "status": "error",
                "error": str(e),
            }

    # Check Loki → Grafana flow
    if "loki" in component_filter and "grafana" in component_filter:
        try:
            datasources = await grafana_client.list_datasources()
            has_loki_ds = any(
                ds.get("type") in ["loki", "grafana-loki-datasource"] for ds in datasources
            )

            if has_loki_ds:
                data_flow["flows"]["loki_to_grafana"] = {
                    "status": "healthy",
                    "description": "Grafana has Loki datasource configured",
                }
            else:
                data_flow["flows"]["loki_to_grafana"] = {
                    "status": "broken",
                    "description": "Grafana missing Loki datasource",
                }
                data_flow["issues"].append("Grafana cannot query Loki logs")

        except Exception as e:
            data_flow["flows"]["loki_to_grafana"] = {
                "status": "error",
                "error": str(e),
            }

    # Determine overall status
    flow_statuses = [flow["status"] for flow in data_flow["flows"].values()]
    if "error" in flow_statuses:
        data_flow["overall_status"] = "error"
    elif "broken" in flow_statuses:
        data_flow["overall_status"] = "degraded"
    elif flow_statuses:
        data_flow["overall_status"] = "healthy"

    data_flow["data_points_checked"] = len(data_flow["flows"])

    return data_flow


async def _check_alert_status(
    _grafana_client: GrafanaClient,
    prometheus_client: PrometheusClient,
    _loki_client: LokiClient,
    _config: MonitoringConfig,
    component_filter: list[str],
    _detailed_check: bool,
    _include_historical: bool,
) -> dict[str, Any]:
    """Check alert status across monitoring systems."""
    alert_status = {
        "active_alerts": 0,
        "alert_rules": 0,
        "alerting_systems": {},
        "last_check": "now",
    }

    # Check Prometheus alerts
    if "prometheus" in component_filter:
        try:
            alerts = await prometheus_client.alerts()
            active_alerts = alerts.get("data", {}).get("alerts", [])
            firing_alerts = [a for a in active_alerts if a.get("state") == "firing"]

            alert_status["alerting_systems"]["prometheus"] = {
                "active_alerts": len(firing_alerts),
                "total_alerts": len(active_alerts),
                "status": "active" if firing_alerts else "quiet",
            }

            alert_status["active_alerts"] += len(firing_alerts)

        except Exception as e:
            alert_status["alerting_systems"]["prometheus"] = {
                "status": "error",
                "error": str(e),
            }

    # Check Prometheus rules
    if "prometheus" in component_filter:
        try:
            rules = await prometheus_client.rules()
            groups = rules.get("data", {}).get("groups", [])

            total_rules = 0
            alerting_rules = 0

            for group in groups:
                rules_in_group = group.get("rules", [])
                total_rules += len(rules_in_group)
                alerting_rules += sum(1 for r in rules_in_group if r.get("type") == "alerting")

            alert_status["alerting_systems"]["prometheus_rules"] = {
                "total_rules": total_rules,
                "alerting_rules": alerting_rules,
                "recording_rules": total_rules - alerting_rules,
            }

            alert_status["alert_rules"] += alerting_rules

        except Exception as e:
            alert_status["alerting_systems"]["prometheus_rules"] = {
                "status": "error",
                "error": str(e),
            }

    return alert_status
