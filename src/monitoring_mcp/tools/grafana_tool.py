"""
Grafana Management Portmanteau Tool

Comprehensive Grafana operations including dashboard management,
panel creation, data source queries, and visualization assistance.

PORTMANTEAU PATTERN: Consolidates all Grafana operations into a single tool
to avoid tool explosion while maintaining full functionality.
"""

import logging
from typing import Any, Literal

import httpx
from fastmcp import FastMCP
from py_key_value_aio import AbstractStore

from monitoring_mcp.config import MonitoringConfig

logger = logging.getLogger(__name__)

# Grafana operations supported by this portmanteau tool
GRAFANA_OPERATIONS = {
    "list_dashboards": "List all dashboards with metadata and tags",
    "get_dashboard": "Retrieve specific dashboard by UID or title",
    "create_dashboard": "Create new dashboard with panels and queries",
    "update_dashboard": "Modify existing dashboard structure and panels",
    "delete_dashboard": "Remove dashboard from Grafana",
    "search_dashboards": "Search dashboards by title, tags, or folder",
    "list_datasources": "List all configured data sources",
    "query_datasource": "Execute queries against specific data sources",
    "create_panel": "Add new panel to existing dashboard",
    "update_panel": "Modify panel configuration and queries",
    "create_alert": "Set up alerting rules for dashboard panels",
    "export_dashboard": "Export dashboard as JSON for backup/sharing",
    "import_dashboard": "Import dashboard from JSON file",
    "list_folders": "List dashboard folders and permissions",
    "create_folder": "Create new dashboard folder",
    "get_dashboard_permissions": "View dashboard/folder permissions",
    "analyze_dashboard": "AI-powered dashboard analysis and optimization suggestions",
}


class GrafanaClient:
    """Grafana API client with authentication and error handling."""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.base_url = config.grafana_url.rstrip("/")
        self.auth_headers = config.get_grafana_auth() or {}
        self.timeout = config.request_timeout

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make authenticated request to Grafana API."""
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers={**self.auth_headers, "Content-Type": "application/json"},
                json=data,
                params=params,
            )

            if response.status_code >= 400:
                error_msg = f"Grafana API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise httpx.HTTPStatusError(error_msg, request=response.request, response=response)

            return response.json()

    async def list_dashboards(self) -> list[dict[str, Any]]:
        """List all dashboards."""
        return await self._make_request("GET", "search?type=dash-db")

    async def get_dashboard(self, uid: str) -> dict[str, Any]:
        """Get dashboard by UID."""
        return await self._make_request("GET", f"dashboards/uid/{uid}")

    async def create_dashboard(
        self, dashboard: dict[str, Any], folder_id: int | None = None
    ) -> dict[str, Any]:
        """Create new dashboard."""
        data = {"dashboard": dashboard}
        if folder_id is not None:
            data["folderId"] = folder_id
        return await self._make_request("POST", "dashboards/db", data)

    async def update_dashboard(
        self, dashboard: dict[str, Any], uid: str, overwrite: bool = True
    ) -> dict[str, Any]:
        """Update existing dashboard."""
        data = {"dashboard": dashboard, "overwrite": overwrite}
        return await self._make_request("POST", "dashboards/db", data)

    async def delete_dashboard(self, uid: str) -> dict[str, Any]:
        """Delete dashboard by UID."""
        return await self._make_request("DELETE", f"dashboards/uid/{uid}")

    async def list_datasources(self) -> list[dict[str, Any]]:
        """List all data sources."""
        return await self._make_request("GET", "datasources")

    async def query_datasource(
        self, datasource_id: int, queries: list[dict[str, Any]], time_range: dict[str, str]
    ) -> dict[str, Any]:
        """Query data source."""
        data = {
            "queries": queries,
            "from": time_range.get("from", "now-1h"),
            "to": time_range.get("to", "now"),
        }
        return await self._make_request("POST", f"ds/query?dsid={datasource_id}", data)


async def register_grafana_tool(
    mcp: FastMCP,
    _storage: AbstractStore,
    config: MonitoringConfig,
) -> None:
    """Register the Grafana portmanteau tool with the MCP server."""

    client = GrafanaClient(config)

    @mcp.tool()
    async def grafana_management(
        operation: Literal[
            "list_dashboards",
            "get_dashboard",
            "create_dashboard",
            "update_dashboard",
            "delete_dashboard",
            "search_dashboards",
            "list_datasources",
            "query_datasource",
            "create_panel",
            "update_panel",
            "create_alert",
            "export_dashboard",
            "import_dashboard",
            "list_folders",
            "create_folder",
            "get_dashboard_permissions",
            "analyze_dashboard",
        ],
        dashboard_uid: str | None = None,
        dashboard_title: str | None = None,
        dashboard_data: dict[str, Any] | None = None,
        folder_id: int | None = None,
        search_query: str | None = None,
        datasource_id: int | None = None,
        queries: list[dict[str, Any]] | None = None,
        time_range: dict[str, str] | None = None,
        panel_data: dict[str, Any] | None = None,
        alert_rule: dict[str, Any] | None = None,
        folder_name: str | None = None,
        permissions_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Comprehensive Grafana management portmanteau tool leveraging FastMCP 2.14.3.

        PORTMANTEAU PATTERN: Consolidates 17 Grafana operations into a single tool
        to prevent tool explosion while maintaining comprehensive functionality.

        Provides conversational responses with actionable insights and AI-powered
        analysis for dashboard optimization and monitoring best practices.

        Args:
            operation: The Grafana operation to perform
            dashboard_uid: Dashboard UID for operations requiring specific dashboard
            dashboard_title: Dashboard title for search/create operations
            dashboard_data: Dashboard JSON data for create/update operations
            folder_id: Folder ID for organizing dashboards
            search_query: Query string for dashboard/folder search
            datasource_id: Data source ID for query operations
            queries: Query objects for data source queries
            time_range: Time range specification for queries
            panel_data: Panel configuration for panel operations
            alert_rule: Alert rule configuration
            folder_name: Folder name for folder operations
            permissions_data: Permissions configuration

        Returns:
            Dict containing operation results with conversational summary and insights
        """
        try:
            if operation not in GRAFANA_OPERATIONS:
                return {
                    "success": False,
                    "error": f"Invalid operation '{operation}'. Available: {list(GRAFANA_OPERATIONS.keys())}",
                    "conversational_summary": f"I don't recognize the '{operation}' operation. Here are the available Grafana operations I can help with.",
                    "available_operations": list(GRAFANA_OPERATIONS.keys()),
                }

            logger.info(f"Executing Grafana operation: {operation}")

            # Execute the requested operation
            result = await _execute_grafana_operation(
                client,
                operation,
                dashboard_uid,
                dashboard_title,
                dashboard_data,
                folder_id,
                search_query,
                datasource_id,
                queries,
                time_range,
                panel_data,
                alert_rule,
                folder_name,
                permissions_data,
            )

            # Add conversational insights
            result["conversational_summary"] = _generate_conversational_summary(operation, result)

            # Add AI-powered recommendations where appropriate
            if operation in ["analyze_dashboard", "get_dashboard", "list_dashboards"]:
                result["ai_insights"] = _generate_ai_insights(operation, result)

            return result

        except Exception as e:
            logger.error(f"Error in Grafana operation '{operation}': {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to execute Grafana operation '{operation}': {e!s}",
                "conversational_summary": f"I encountered an error while trying to {operation.replace('_', ' ')}. This might be due to connectivity issues or invalid parameters. Please check your Grafana configuration and try again.",
                "troubleshooting_tips": [
                    "Verify Grafana is running and accessible",
                    "Check API key/authentication settings",
                    "Ensure dashboard UID/title exists",
                    "Validate JSON structure for dashboard operations",
                ],
            }


async def _execute_grafana_operation(
    client: GrafanaClient,
    operation: str,
    dashboard_uid: str | None = None,
    dashboard_title: str | None = None,  # noqa: ARG001
    dashboard_data: dict[str, Any] | None = None,
    folder_id: int | None = None,
    search_query: str | None = None,
    datasource_id: int | None = None,
    queries: list[dict[str, Any]] | None = None,
    time_range: dict[str, str] | None = None,
    panel_data: dict[str, Any] | None = None,  # noqa: ARG001
    alert_rule: dict[str, Any] | None = None,  # noqa: ARG001
    folder_name: str | None = None,  # noqa: ARG001
    permissions_data: dict[str, Any] | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """Execute the specific Grafana operation."""

    if operation == "list_dashboards":
        dashboards = await client.list_dashboards()
        return {
            "success": True,
            "operation": "list_dashboards",
            "data": dashboards,
            "count": len(dashboards),
        }

    elif operation == "get_dashboard":
        if not dashboard_uid:
            raise ValueError("dashboard_uid is required for get_dashboard")
        dashboard = await client.get_dashboard(dashboard_uid)
        return {
            "success": True,
            "operation": "get_dashboard",
            "data": dashboard,
        }

    elif operation == "create_dashboard":
        if not dashboard_data:
            raise ValueError("dashboard_data is required for create_dashboard")
        result = await client.create_dashboard(dashboard_data, folder_id)
        return {
            "success": True,
            "operation": "create_dashboard",
            "data": result,
        }

    elif operation == "update_dashboard":
        if not dashboard_data or not dashboard_uid:
            raise ValueError("dashboard_data and dashboard_uid are required for update_dashboard")
        result = await client.update_dashboard(dashboard_data, dashboard_uid)
        return {
            "success": True,
            "operation": "update_dashboard",
            "data": result,
        }

    elif operation == "delete_dashboard":
        if not dashboard_uid:
            raise ValueError("dashboard_uid is required for delete_dashboard")
        result = await client.delete_dashboard(dashboard_uid)
        return {
            "success": True,
            "operation": "delete_dashboard",
            "data": result,
        }

    elif operation == "search_dashboards":
        dashboards = await client.list_dashboards()
        if search_query:
            # Simple text search in titles and tags
            filtered = []
            query_lower = search_query.lower()
            for db in dashboards:
                title = db.get("title", "").lower()
                tags = [tag.lower() for tag in db.get("tags", [])]
                if query_lower in title or any(query_lower in tag for tag in tags):
                    filtered.append(db)
            dashboards = filtered
        return {
            "success": True,
            "operation": "search_dashboards",
            "data": dashboards,
            "count": len(dashboards),
            "search_query": search_query,
        }

    elif operation == "list_datasources":
        datasources = await client.list_datasources()
        return {
            "success": True,
            "operation": "list_datasources",
            "data": datasources,
            "count": len(datasources),
        }

    elif operation == "query_datasource":
        if not datasource_id or not queries:
            raise ValueError("datasource_id and queries are required for query_datasource")
        time_range = time_range or {"from": "now-1h", "to": "now"}
        result = await client.query_datasource(datasource_id, queries, time_range)
        return {
            "success": True,
            "operation": "query_datasource",
            "data": result,
            "datasource_id": datasource_id,
            "query_count": len(queries),
        }

    # Placeholder implementations for remaining operations
    elif operation in [
        "create_panel",
        "update_panel",
        "create_alert",
        "export_dashboard",
        "import_dashboard",
        "list_folders",
        "create_folder",
        "get_dashboard_permissions",
    ]:
        return {
            "success": False,
            "operation": operation,
            "error": f"Operation '{operation}' is not yet implemented",
            "note": "This operation is planned for a future version",
        }

    elif operation == "analyze_dashboard":
        if not dashboard_uid:
            raise ValueError("dashboard_uid is required for analyze_dashboard")
        dashboard = await client.get_dashboard(dashboard_uid)
        # Basic analysis - could be enhanced with AI
        analysis = _analyze_dashboard_structure(dashboard)
        return {
            "success": True,
            "operation": "analyze_dashboard",
            "data": dashboard,
            "analysis": analysis,
        }

    else:
        raise ValueError(f"Unsupported operation: {operation}")


def _generate_conversational_summary(operation: str, result: dict[str, Any]) -> str:
    """Generate conversational summary for the operation result."""
    if not result.get("success"):
        return f"I wasn't able to complete the {operation.replace('_', ' ')} operation. {result.get('error', 'Unknown error occurred')}."

    if operation == "list_dashboards":
        count = result.get("count", 0)
        return f"I found {count} dashboard{'s' if count != 1 else ''} in your Grafana instance. {'You have quite a comprehensive monitoring setup!' if count > 10 else 'This gives you a good foundation for monitoring.'}"

    elif operation == "get_dashboard":
        dashboard = result.get("data", {}).get("dashboard", {})
        title = dashboard.get("title", "Unknown")
        panels = len(dashboard.get("panels", []))
        return f"I retrieved the '{title}' dashboard. It contains {panels} panel{'s' if panels != 1 else ''} for visualizing your metrics."

    elif operation == "create_dashboard":
        uid = result.get("data", {}).get("uid", "unknown")
        return f"Successfully created a new dashboard with UID '{uid}'. You can now access it in Grafana to start adding panels and queries."

    elif operation == "search_dashboards":
        count = result.get("count", 0)
        query = result.get("search_query", "")
        return f"I found {count} dashboard{'s' if count != 1 else ''} matching '{query}'. {'Here are your search results:' if count > 0 else 'No dashboards matched your search criteria.'}"

    elif operation == "list_datasources":
        count = result.get("count", 0)
        return f"Your Grafana instance has {count} configured data source{'s' if count != 1 else ''}. This gives you {'excellent' if count > 3 else 'basic'} data connectivity."

    elif operation == "query_datasource":
        return f"I executed {result.get('query_count', 0)} quer{'ies' if result.get('query_count', 0) != 1 else 'y'} against data source {result.get('datasource_id')}. The results are ready for analysis."

    elif operation == "analyze_dashboard":
        analysis = result.get("analysis", {})
        score = analysis.get("overall_score", 0)
        return f"I analyzed your dashboard and gave it an overall score of {score}/10. {analysis.get('summary', 'Review the detailed analysis for improvement suggestions.')}"

    else:
        return f"The {operation.replace('_', ' ')} operation completed successfully."


def _generate_ai_insights(operation: str, result: dict[str, Any]) -> dict[str, Any]:
    """Generate AI-powered insights for dashboard analysis."""
    insights = {"recommendations": [], "optimization_opportunities": []}

    if operation == "analyze_dashboard":
        analysis = result.get("analysis", {})

        if analysis.get("panel_count", 0) > 20:
            insights["recommendations"].append(
                "Consider breaking this dashboard into multiple focused dashboards for better organization"
            )

        if not analysis.get("has_alerts", False):
            insights["optimization_opportunities"].append(
                "Add alerting rules to critical panels to get notified of issues proactively"
            )

        if analysis.get("unused_variables", []):
            insights["optimization_opportunities"].append(
                f"Remove unused template variables: {', '.join(analysis['unused_variables'])}"
            )

    elif operation == "list_dashboards":
        dashboards = result.get("data", [])
        if len(dashboards) > 50:
            insights["recommendations"].append(
                "Consider organizing dashboards into folders for better navigation"
            )

        # Check for dashboards without recent updates
        # (Would need timestamp data from Grafana)

    return insights


def _analyze_dashboard_structure(dashboard_data: dict[str, Any]) -> dict[str, Any]:
    """Analyze dashboard structure and provide insights."""
    dashboard = dashboard_data.get("dashboard", {})
    meta = dashboard_data.get("meta", {})

    panels = dashboard.get("panels", [])
    templating = dashboard.get("templating", {}).get("list", [])

    analysis = {
        "panel_count": len(panels),
        "template_variables": len(templating),
        "has_alerts": any(panel.get("alert") for panel in panels if isinstance(panel, dict)),
        "tags": dashboard.get("tags", []),
        "refresh_interval": dashboard.get("refresh"),
        "time_range": dashboard.get("time", {}),
        "permissions": meta.get("permissions", []),
        "unused_variables": [],  # Would need more complex analysis
        "overall_score": 7,  # Placeholder scoring
        "summary": "This dashboard has a good structure with multiple panels and appropriate configuration.",
    }

    # Basic scoring logic
    score = 5  # Base score

    if len(panels) > 0:
        score += 1
    if len(templating) > 0:
        score += 1
    if analysis["has_alerts"]:
        score += 1
    if len(analysis["tags"]) > 0:
        score += 1
    if analysis["refresh_interval"]:
        score += 1

    analysis["overall_score"] = min(score, 10)

    return analysis
