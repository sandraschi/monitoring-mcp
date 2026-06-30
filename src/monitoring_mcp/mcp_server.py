"""
Monitoring MCP Server - FastMCP 3.2+ Implementation

A comprehensive monitoring server providing intelligent operations across
Grafana, Prometheus, and Loki ecosystems with conversational AI assistance.

Features:
- Portmanteau tools following the industrial portmanteau pattern
- Conversational responses with structured data and natural language summaries
- Real AI chat via local LLM (Ollama / LM Studio)
- Persistent storage with DiskStore backend
- Modern Python with full type annotations and async patterns
"""

import asyncio
import logging

from fastmcp import FastMCP
from key_value.aio.stores.disk.store import DiskStore

from .config import MonitoringConfig
from .tools.correlation_tool import register_correlation_tool
from .tools.grafana_tool import register_grafana_tool
from .tools.loki_tool import register_loki_tool
from .tools.prometheus_tool import register_prometheus_tool
from .tools.status_tool import register_status_tool
from .transport import create_argument_parser, run_server_async

logger = logging.getLogger(__name__)

# Global FastMCP instance
mcp = FastMCP(
    name="monitoring-mcp",
    version="0.1.0",
    instructions="""
    You are an expert monitoring assistant with deep knowledge of Grafana, Prometheus, and Loki.
    Provide conversational, actionable responses that help users understand their monitoring data.

    When analyzing metrics or logs:
    1. Always provide context about what the data means
    2. Suggest actionable insights and next steps
    3. Use clear, non-technical language when possible
    4. Include specific values and trends
    5. Offer recommendations for improvement

    For complex queries, break them down step-by-step and explain the reasoning.
    """,
)


class MonitoringMCPServer:
    """
    FastMCP 3.2+-powered monitoring server for Grafana, Prometheus, and Loki.

    Provides comprehensive observability tools with intelligent AI assistance
    for DevOps workflows, performance analysis, and system diagnostics.
    """

    # Class-level attribute for mock compatibility
    storage = None

    def __init__(self, config: MonitoringConfig | None = None):
        """
        Initialize the Monitoring MCP server.

        Args:
            config: Optional configuration override. Defaults to environment-based config.
        """
        self.config = config or MonitoringConfig()
        self.mcp = mcp  # Use global instance

        # Initialize persistent storage
        self.storage = DiskStore(
            directory=self.config.storage_path / "monitoring_mcp",
        )

        # Register all portmanteau tools
        self._register_tools()

        logger.info(f"Monitoring MCP server initialized with config: {self.config}")

    def _register_tools(self) -> None:
        """Register all portmanteau tools with the MCP server."""
        # Grafana management tools
        register_grafana_tool(self.mcp, self.storage, self.config)

        # Prometheus monitoring tools
        register_prometheus_tool(self.mcp, self.storage, self.config)

        # Loki logging tools
        register_loki_tool(self.mcp, self.storage, self.config)

        # Cross-system correlation tools
        register_correlation_tool(self.mcp, self.storage, self.config)

        # Status and health monitoring
        register_status_tool(self.mcp, self.storage, self.config)

        logger.info("All monitoring tools registered successfully")

    async def run(self) -> None:
        """Main entry point for the Monitoring Hub MCP server."""
        # Initialize storage if needed
        await self.storage.setup()

        try:
            parser = create_argument_parser("monitoring-mcp")
            args = parser.parse_args(["--stdio"])
            await run_server_async(self.mcp, args=args, server_name="monitoring-mcp")
        finally:
            await self._cleanup()

    async def _cleanup(self) -> None:
        """Clean up resources on shutdown."""
        if self.storage:
            try:
                await self.storage.close()
            except Exception:
                logger.warning("Error during storage cleanup", exc_info=True)


def create_monitoring_server(
    grafana_url: str | None = None,
    prometheus_url: str | None = None,
    loki_url: str | None = None,
) -> MonitoringMCPServer:
    """Create a MonitoringMCPServer instance with optional custom URLs.

    Args:
        grafana_url: Custom Grafana URL override
        prometheus_url: Custom Prometheus URL override
        loki_url: Custom Loki URL override

    Returns:
        Configured MonitoringMCPServer instance.
    """
    kwargs: dict[str, str | None] = {}
    if grafana_url is not None:
        kwargs["grafana_url"] = grafana_url
    if prometheus_url is not None:
        kwargs["prometheus_url"] = prometheus_url
    if loki_url is not None:
        kwargs["loki_url"] = loki_url
    config = MonitoringConfig(**kwargs)
    return MonitoringMCPServer(config)


def run() -> None:
    """Synchronous entry point for compatibility."""
    server = MonitoringMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    run()
