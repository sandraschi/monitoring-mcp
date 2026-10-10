"""Self-termination tool for orderly agent-driven shutdown.

Allows an agent (or the fleet launcher) to stop the monitoring-mcp process
gracefully after long-running flows checkpoint state. Mirrors the
``POST /api/shutdown`` REST endpoint for stdio-only clients.
"""

from __future__ import annotations

import logging
import os
import threading
from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

logger = logging.getLogger(__name__)


def register_shutdown_tool(mcp: FastMCP) -> None:
    """Register the self-termination tool with the MCP server."""

    @mcp.tool()
    async def monitoring_shutdown(
        delay_ms: Annotated[
            int, Field(description="Delay before exit in milliseconds (lets the response flush)")
        ] = 500,
    ) -> dict[str, Any]:
        """Shut down the monitoring-mcp server process in an orderly fashion.

        Responds immediately, then exits the process after ``delay_ms`` so depot
        writes and in-flight jobs can flush (same contract as POST /api/shutdown).

        ## Return Format
        {"success": bool, "message": str, "data": {}}

        ## Examples
        monitoring_shutdown()
        monitoring_shutdown(delay_ms=1000)
        """
        logger.warning("monitoring_shutdown requested - exiting in ~%d ms", delay_ms)
        threading.Timer(max(delay_ms, 0) / 1000.0, lambda: os._exit(0)).start()
        return {
            "success": True,
            "message": f"monitoring-mcp shutting down in ~{delay_ms} ms",
            "data": {},
        }
