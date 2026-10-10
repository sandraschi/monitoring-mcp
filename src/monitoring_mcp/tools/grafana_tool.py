"""
Grafana Management Portmanteau Tool

Comprehensive Grafana operations including dashboard management,
panel creation, data source queries, and visualization assistance.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Annotated, Any, Literal

import httpx
from fastmcp import FastMCP
from pydantic import Field

from monitoring_mcp.config import MonitoringConfig
from monitoring_mcp.utils import ResponseCache

logger = logging.getLogger(__name__)

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
    """Grafana API client with auth, cache, and grafana-api enrichment."""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.base_url = config.grafana_url.rstrip("/")
        self.auth_headers = config.get_grafana_auth() or {}
        self.timeout = config.request_timeout
        self.cache = ResponseCache(
            ttl_seconds=config.cache_ttl_seconds,
            enabled=config.enable_cache,
        )

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        *,
        use_cache: bool = False,
    ) -> Any:
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        cache_key = ("grafana", method, endpoint, params, data)
        if use_cache and method == "GET":
            cached = self.cache.get(*cache_key)
            if cached is not None:
                return cached

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
            if response.status_code == 204 or not response.content:
                return {"status": "ok"}
            payload = response.json()
            if use_cache and method == "GET":
                self.cache.set(*cache_key, value=payload)
            return payload

    def sync_health(self) -> dict[str, Any]:
        """Wire grafana-api package for health/org enrichment (sync)."""
        try:
            from grafana_api.grafana_face import GrafanaFace

            api_key = None
            if self.config.grafana_api_key:
                api_key = self.config.grafana_api_key.get_secret_value()
            auth: Any = api_key
            if not auth and self.config.grafana_username and self.config.grafana_password:
                auth = (self.config.grafana_username, self.config.grafana_password.get_secret_value())
            parsed_host = self.base_url.split("://", 1)[-1].split("/")[0]
            face = GrafanaFace(
                auth=auth,
                host=parsed_host,
                protocol="https" if self.base_url.startswith("https") else "http",
            )
            org = face.organization.get_current_organization()
            return {"organization": org}
        except Exception as exc:
            logger.debug("grafana-api enrichment unavailable: %s", exc)
            return {"error": str(exc), "note": "grafana-api enrichment unavailable"}

    async def list_dashboards(self) -> list[dict[str, Any]]:
        return await self._make_request("GET", "search", params={"type": "dash-db"}, use_cache=True)

    async def get_dashboard(self, uid: str) -> dict[str, Any]:
        return await self._make_request("GET", f"dashboards/uid/{uid}")

    async def create_dashboard(self, dashboard: dict[str, Any], folder_id: int | None = None) -> dict[str, Any]:
        data: dict[str, Any] = {"dashboard": dashboard, "overwrite": False}
        if folder_id is not None:
            data["folderId"] = folder_id
        return await self._make_request("POST", "dashboards/db", data)

    async def update_dashboard(self, dashboard: dict[str, Any], uid: str, overwrite: bool = True) -> dict[str, Any]:
        dashboard = {**dashboard, "uid": uid}
        return await self._make_request("POST", "dashboards/db", {"dashboard": dashboard, "overwrite": overwrite})

    async def delete_dashboard(self, uid: str) -> dict[str, Any]:
        return await self._make_request("DELETE", f"dashboards/uid/{uid}")

    async def list_datasources(self) -> list[dict[str, Any]]:
        return await self._make_request("GET", "datasources", use_cache=True)

    async def query_datasource(
        self, datasource_id: int, queries: list[dict[str, Any]], time_range: dict[str, str]
    ) -> dict[str, Any]:
        data = {
            "queries": queries,
            "from": time_range.get("from", "now-1h"),
            "to": time_range.get("to", "now"),
        }
        return await self._make_request("POST", f"ds/query?dsid={datasource_id}", data)

    async def list_folders(self) -> list[dict[str, Any]]:
        return await self._make_request("GET", "folders", use_cache=True)

    async def create_folder(self, title: str, uid: str | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"title": title}
        if uid:
            body["uid"] = uid
        return await self._make_request("POST", "folders", body)

    async def get_dashboard_permissions(self, uid: str) -> list[dict[str, Any]]:
        return await self._make_request("GET", f"dashboards/uid/{uid}/permissions")

    async def import_dashboard(self, dashboard: dict[str, Any], folder_id: int | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "dashboard": dashboard.get("dashboard", dashboard),
            "overwrite": True,
            "inputs": dashboard.get("inputs", []),
        }
        if folder_id is not None:
            payload["folderId"] = folder_id
        return await self._make_request("POST", "dashboards/import", payload)

    async def create_alert_rule(self, alert_rule: dict[str, Any]) -> dict[str, Any]:
        return await self._make_request("POST", "v1/provisioning/alert-rules", alert_rule)


def register_grafana_tool(
    mcp: FastMCP,
    _storage: object,
    config: MonitoringConfig,
) -> None:
    """Register the Grafana portmanteau tool with the MCP server."""

    client = GrafanaClient(config)

    @mcp.tool(
        annotations={
            "title": "Grafana management",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": True,
        }
    )
    async def grafana_management(
        operation: Annotated[
            Literal[
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
            Field(description="Grafana operation to perform (see GRAFANA_OPERATIONS for per-op requirements)"),
        ],
        dashboard_uid: Annotated[
            str | None, Field(description="Dashboard UID for get/update/delete/export calls")
        ] = None,
        dashboard_title: Annotated[
            str | None, Field(description="Dashboard title filter or folder-title fallback")
        ] = None,
        dashboard_data: Annotated[
            dict[str, Any] | None, Field(description="Full dashboard JSON body for create/update/import calls")
        ] = None,
        search_query: Annotated[str | None, Field(description="Title/tag substring for search_dashboards")] = None,
        folder_id: Annotated[int | None, Field(description="Numeric folder id for create/import calls")] = None,
        datasource_id: Annotated[int | None, Field(description="Numeric datasource id for query_datasource")] = None,
        queries: Annotated[
            list[dict[str, Any]] | None, Field(description="Datasource query payloads for query_datasource")
        ] = None,
        time_range: Annotated[
            dict[str, str] | None, Field(description="Query window, e.g. {'from': 'now-1h', 'to': 'now'}")
        ] = None,
        panel_data: Annotated[
            dict[str, Any] | None, Field(description="Panel JSON for create_panel/update_panel")
        ] = None,
        panel_id: Annotated[int | None, Field(description="Numeric panel id for update_panel")] = None,
        alert_rule: Annotated[dict[str, Any] | None, Field(description="Alert-rule body for create_alert")] = None,
        folder_name: Annotated[str | None, Field(description="Folder title for create_folder")] = None,
        folder_uid: Annotated[str | None, Field(description="Optional folder UID for create_folder")] = None,
    ) -> dict[str, Any]:
        """Grafana management: dashboards, datasources, panels, folders, alert rules, AI analysis.

        PORTMANTEAU PATTERN: Consolidates 17 Grafana operations into a single tool.

        ## Return Format
        {"success": bool, "operation": str, "data": <payload>, "count": int (list/search ops only),
         "conversational_summary": str, "ai_insights": {...} (analyze_dashboard/list_dashboards only),
         "error": str (on failure only), "available_operations": [...] (on invalid operation only)}

        ## Examples
        grafana_management(operation="list_dashboards")
        grafana_management(operation="get_dashboard", dashboard_uid="abc123")
        grafana_management(operation="search_dashboards", search_query="payments")
        grafana_management(operation="create_folder", folder_name="SLOs")
        """
        try:
            if operation not in GRAFANA_OPERATIONS:
                return {
                    "success": False,
                    "error": f"Invalid operation '{operation}'",
                    "available_operations": list(GRAFANA_OPERATIONS.keys()),
                }

            result = await _execute_grafana_operation(
                client,
                operation,
                dashboard_uid=dashboard_uid,
                dashboard_title=dashboard_title,
                dashboard_data=dashboard_data,
                search_query=search_query,
                folder_id=folder_id,
                datasource_id=datasource_id,
                queries=queries,
                time_range=time_range,
                panel_data=panel_data,
                panel_id=panel_id,
                alert_rule=alert_rule,
                folder_name=folder_name,
                folder_uid=folder_uid,
            )
            result["conversational_summary"] = _generate_conversational_summary(operation, result)
            if operation in ["analyze_dashboard", "list_dashboards"]:
                result["ai_insights"] = _generate_ai_insights(operation, result)
            return result
        except Exception as e:
            logger.error("Error in Grafana operation '%s': %s", operation, e, exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "conversational_summary": (
                    f"Failed to {operation.replace('_', ' ')}. Check Grafana URL and credentials."
                ),
            }


async def _execute_grafana_operation(
    client: GrafanaClient,
    operation: str,
    *,
    dashboard_uid: str | None = None,
    dashboard_title: str | None = None,
    dashboard_data: dict[str, Any] | None = None,
    search_query: str | None = None,
    folder_id: int | None = None,
    datasource_id: int | None = None,
    queries: list[dict[str, Any]] | None = None,
    time_range: dict[str, str] | None = None,
    panel_data: dict[str, Any] | None = None,
    panel_id: int | None = None,
    alert_rule: dict[str, Any] | None = None,
    folder_name: str | None = None,
    folder_uid: str | None = None,
) -> dict[str, Any]:
    if operation == "list_dashboards":
        dashboards = await client.list_dashboards()
        return {"success": True, "operation": operation, "data": dashboards, "count": len(dashboards)}

    if operation == "get_dashboard":
        if not dashboard_uid:
            raise ValueError("dashboard_uid is required for get_dashboard")
        dashboard = await client.get_dashboard(dashboard_uid)
        return {"success": True, "operation": operation, "data": dashboard}

    if operation == "create_dashboard":
        if not dashboard_data:
            raise ValueError("dashboard_data is required for create_dashboard")
        result = await client.create_dashboard(dashboard_data, folder_id)
        return {"success": True, "operation": operation, "data": result}

    if operation == "update_dashboard":
        if not dashboard_data or not dashboard_uid:
            raise ValueError("dashboard_data and dashboard_uid are required for update_dashboard")
        result = await client.update_dashboard(dashboard_data, dashboard_uid)
        return {"success": True, "operation": operation, "data": result}

    if operation == "delete_dashboard":
        if not dashboard_uid:
            raise ValueError("dashboard_uid is required for delete_dashboard")
        result = await client.delete_dashboard(dashboard_uid)
        return {"success": True, "operation": operation, "data": result}

    if operation == "search_dashboards":
        dashboards = await client.list_dashboards()
        if search_query:
            q = search_query.lower()
            dashboards = [
                db
                for db in dashboards
                if q in db.get("title", "").lower() or any(q in t.lower() for t in db.get("tags", []))
            ]
        return {
            "success": True,
            "operation": operation,
            "data": dashboards,
            "count": len(dashboards),
            "search_query": search_query,
        }

    if operation == "list_datasources":
        datasources = await client.list_datasources()
        return {"success": True, "operation": operation, "data": datasources, "count": len(datasources)}

    if operation == "query_datasource":
        if not datasource_id or not queries:
            raise ValueError("datasource_id and queries are required for query_datasource")
        time_range = time_range or {"from": "now-1h", "to": "now"}
        result = await client.query_datasource(datasource_id, queries, time_range)
        return {
            "success": True,
            "operation": operation,
            "data": result,
            "datasource_id": datasource_id,
            "query_count": len(queries),
        }

    if operation == "export_dashboard":
        if not dashboard_uid:
            raise ValueError("dashboard_uid is required for export_dashboard")
        dashboard = await client.get_dashboard(dashboard_uid)
        return {
            "success": True,
            "operation": operation,
            "data": dashboard,
            "export": dashboard.get("dashboard"),
            "meta": dashboard.get("meta"),
        }

    if operation == "import_dashboard":
        if not dashboard_data:
            raise ValueError("dashboard_data is required for import_dashboard")
        result = await client.import_dashboard(dashboard_data, folder_id)
        return {"success": True, "operation": operation, "data": result}

    if operation == "list_folders":
        folders = await client.list_folders()
        return {"success": True, "operation": operation, "data": folders, "count": len(folders)}

    if operation == "create_folder":
        title = folder_name or dashboard_title
        if not title:
            raise ValueError("folder_name is required for create_folder")
        result = await client.create_folder(title, folder_uid)
        return {"success": True, "operation": operation, "data": result}

    if operation == "get_dashboard_permissions":
        if not dashboard_uid:
            raise ValueError("dashboard_uid is required for get_dashboard_permissions")
        perms = await client.get_dashboard_permissions(dashboard_uid)
        return {"success": True, "operation": operation, "data": perms, "count": len(perms)}

    if operation == "create_panel":
        if not dashboard_uid or not panel_data:
            raise ValueError("dashboard_uid and panel_data are required for create_panel")
        full = await client.get_dashboard(dashboard_uid)
        dashboard = full.get("dashboard", {})
        panels = list(dashboard.get("panels") or [])
        next_id = max((p.get("id", 0) for p in panels), default=0) + 1
        new_panel = {"id": next_id, "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}, **panel_data}
        panels.append(new_panel)
        dashboard["panels"] = panels
        saved = await client.update_dashboard(dashboard, dashboard_uid)
        return {"success": True, "operation": operation, "data": saved, "panel_id": next_id}

    if operation == "update_panel":
        if not dashboard_uid or panel_id is None or not panel_data:
            raise ValueError("dashboard_uid, panel_id, and panel_data are required for update_panel")
        full = await client.get_dashboard(dashboard_uid)
        dashboard = full.get("dashboard", {})
        panels = list(dashboard.get("panels") or [])
        found = False
        for i, panel in enumerate(panels):
            if panel.get("id") == panel_id:
                panels[i] = {**panel, **panel_data, "id": panel_id}
                found = True
                break
        if not found:
            raise ValueError(f"Panel id {panel_id} not found on dashboard {dashboard_uid}")
        dashboard["panels"] = panels
        saved = await client.update_dashboard(dashboard, dashboard_uid)
        return {"success": True, "operation": operation, "data": saved, "panel_id": panel_id}

    if operation == "create_alert":
        if not alert_rule:
            raise ValueError("alert_rule is required for create_alert")
        created = await client.create_alert_rule(alert_rule)
        return {"success": True, "operation": operation, "data": created}

    if operation == "analyze_dashboard":
        if not dashboard_uid:
            raise ValueError("dashboard_uid is required for analyze_dashboard")
        dashboard = await client.get_dashboard(dashboard_uid)
        analysis = _analyze_dashboard_structure(dashboard)
        org_info = await asyncio.to_thread(client.sync_health)
        analysis["grafana_org"] = org_info
        return {"success": True, "operation": operation, "data": dashboard, "analysis": analysis}

    raise ValueError(f"Unsupported operation: {operation}")


def _generate_conversational_summary(operation: str, result: dict[str, Any]) -> str:
    if not result.get("success"):
        return f"I wasn't able to complete the {operation.replace('_', ' ')} operation. {result.get('error', '')}"
    if operation == "list_dashboards":
        return f"Found {result.get('count', 0)} dashboards."
    if operation == "list_folders":
        return f"Found {result.get('count', 0)} folders."
    if operation == "export_dashboard":
        return "Dashboard exported as JSON."
    if operation == "create_panel":
        return f"Added panel id {result.get('panel_id')} to the dashboard."
    return f"The {operation.replace('_', ' ')} operation completed successfully."


def _generate_ai_insights(operation: str, result: dict[str, Any]) -> dict[str, Any]:
    insights: dict[str, list[str]] = {"recommendations": [], "optimization_opportunities": []}
    if operation == "analyze_dashboard":
        analysis = result.get("analysis", {})
        if analysis.get("panel_count", 0) > 20:
            insights["recommendations"].append("Split into focused dashboards for clarity")
        if not analysis.get("has_alerts"):
            insights["optimization_opportunities"].append("Add alerting on critical panels")
    elif operation == "list_dashboards" and result.get("count", 0) > 50:
        insights["recommendations"].append("Organize dashboards into folders")
    return insights


def _analyze_dashboard_structure(dashboard_data: dict[str, Any]) -> dict[str, Any]:
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
        "unused_variables": [],
        "overall_score": 5,
        "summary": "Dashboard structure analyzed.",
    }
    score = 5
    if panels:
        score += 1
    if templating:
        score += 1
    if analysis["has_alerts"]:
        score += 1
    if analysis["tags"]:
        score += 1
    if analysis["refresh_interval"]:
        score += 1
    analysis["overall_score"] = min(score, 10)
    analysis["summary"] = f"Score {analysis['overall_score']}/10 with {len(panels)} panels."
    return analysis
