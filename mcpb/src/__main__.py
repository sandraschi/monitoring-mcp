#!/usr/bin/env python3
"""
Monitoring MCP Server - Command Line Interface

Entry point for running the Monitoring MCP server with FastMCP 2.14.3.

This module provides the command-line interface for starting the monitoring MCP server,
which provides intelligent operations across Grafana, Prometheus, and Loki ecosystems.

Usage:
    python -m monitoring_mcp
    monitoring-mcp (if installed)
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for development
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from monitoring_mcp.mcp_server import MonitoringMCPServer
except ImportError:
    # Fallback for when running as module
    from .mcp_server import MonitoringMCPServer


async def main():
    """
    Main entry point for the Monitoring MCP server.

    Initializes and starts the MonitoringMCPServer with default configuration.
    The server will run until interrupted (Ctrl+C) or an error occurs.
    """
    server = MonitoringMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
