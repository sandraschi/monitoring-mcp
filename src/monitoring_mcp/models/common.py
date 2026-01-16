"""
Common Models for Monitoring MCP

Shared Pydantic v2 models used across all monitoring tools.
"""

from typing import Any

from pydantic import BaseModel, Field


class TimeRange(BaseModel):
    """
    Time range specification for queries.

    Used to define temporal boundaries for metric and log queries across
    Grafana, Prometheus, and Loki.
    """

    start: str = Field(..., description="Start time (RFC3339 or unix timestamp)")
    end: str = Field(..., description="End time (RFC3339 or unix timestamp)")
    step: str | None = Field(None, description="Query resolution step (Prometheus format)")


class MetricData(BaseModel):
    """
    Generic metric data structure.

    Represents a single metric measurement with its value, timestamp,
    and associated metadata/labels.
    """

    name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    timestamp: str | None = Field(None, description="Timestamp (RFC3339 format)")
    labels: dict[str, str] = Field(default_factory=dict, description="Metric labels/dimensions")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class LogEntry(BaseModel):
    """Generic log entry structure."""

    timestamp: str = Field(..., description="Log timestamp")
    message: str = Field(..., description="Log message")
    level: str | None = Field(None, description="Log level")
    labels: dict[str, str] = Field(default_factory=dict, description="Log labels")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DashboardInfo(BaseModel):
    """Dashboard information structure."""

    uid: str = Field(..., description="Dashboard UID")
    title: str = Field(..., description="Dashboard title")
    tags: list[str] = Field(default_factory=list, description="Dashboard tags")
    folder: str | None = Field(None, description="Dashboard folder")
    panels: int = Field(..., description="Number of panels")
    last_modified: str | None = Field(None, description="Last modified timestamp")


class AlertInfo(BaseModel):
    """Alert information structure."""

    name: str = Field(..., description="Alert name")
    state: str = Field(..., description="Alert state (firing, pending, inactive)")
    severity: str | None = Field(None, description="Alert severity")
    description: str | None = Field(None, description="Alert description")
    labels: dict[str, str] = Field(default_factory=dict, description="Alert labels")
    annotations: dict[str, str] = Field(default_factory=dict, description="Alert annotations")
    active_since: str | None = Field(None, description="When alert became active")


class HealthStatus(BaseModel):
    """Health status structure."""

    component: str = Field(..., description="Component name")
    status: str = Field(..., description="Health status (healthy, degraded, unhealthy)")
    score: int | None = Field(None, description="Health score (0-100)")
    details: str | None = Field(None, description="Health details")
    last_check: str | None = Field(None, description="Last health check timestamp")
    issues: list[str] = Field(default_factory=list, description="Identified issues")
