"""Prompts and resources for monitoring-mcp (Chat skill-first flow).

Registers reusable prompt templates plus a capabilities resource so Chat
clients can build skill-first system preprompts without hardcoding tool lists.
"""

from __future__ import annotations

import json

from fastmcp import FastMCP


def register_skills_prompts(mcp: FastMCP) -> None:
    """Register prompt templates and the capabilities resource."""

    @mcp.prompt()
    def incident_triage(service: str, symptom: str) -> str:
        """Build an incident-triage system preprompt for a service and symptom.

        Returns a ready-to-use prompt that walks the model through the
        monitoring-observability skill incident flow.
        """
        return (
            "You are triaging an incident with monitoring-mcp. "
            f"Service: {service}. Symptom: {symptom}.\n"
            "Follow the monitoring-observability skill incident flow: "
            "1) monitoring_status system_health, 2) prometheus_monitoring list_alerts, "
            "3) loki_logging search_errors for the service, "
            "4) cross_system_correlation correlate_incident with the symptom and time range. "
            "Read-only ops first; propose mutating ops, do not run them unasked."
        )

    @mcp.prompt()
    def dashboard_review(dashboard_uid: str) -> str:
        """Build a dashboard-review system preprompt for a Grafana dashboard UID."""
        return (
            "You are reviewing a Grafana dashboard with monitoring-mcp. "
            f"Dashboard UID: {dashboard_uid}.\n"
            "Run grafana_management analyze_dashboard, then report: panel count, "
            "unused template variables, missing alerts, and the top 3 concrete "
            "improvements. Keep it actionable, no fluff."
        )

    @mcp.resource("monitoring://capabilities")
    def capabilities_resource() -> str:
        """Machine-readable capability summary (tool names + REST routes)."""
        return json.dumps(
            {
                "server": "monitoring-mcp",
                "tools": [
                    "grafana_management",
                    "prometheus_monitoring",
                    "loki_logging",
                    "cross_system_correlation",
                    "monitoring_status",
                    "monitoring_shutdown",
                ],
                "prompts": ["incident_triage", "dashboard_review"],
                "rest": "GET /api/capabilities",
            }
        )
