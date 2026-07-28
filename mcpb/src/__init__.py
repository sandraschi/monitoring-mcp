"""
Monitoring MCP Server

A FastMCP 2.14.3-powered monitoring server for comprehensive observability
across Grafana, Prometheus, and Loki ecosystems.

Provides intelligent monitoring operations with conversational AI assistance
for DevOps workflows, performance analysis, and system diagnostics.
"""

__version__ = "0.1.0"
__author__ = "Sandra Schi"
__email__ = "sandra.schi@example.com"

from .mcp_server import MonitoringMCPServer

__all__ = ["MonitoringMCPServer", "__author__", "__email__", "__version__"]
