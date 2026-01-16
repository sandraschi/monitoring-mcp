"""
Monitoring MCP Server - FastMCP 2.14.3 Implementation

A comprehensive monitoring server providing intelligent operations across
Grafana, Prometheus, and Loki ecosystems with conversational AI assistance.

Features:
- Portmanteau tools following database-mcp pattern to avoid tool explosion
- Conversational responses with structured data and natural language summaries
- Sampling capabilities for handling large datasets efficiently
- Persistent storage with DiskStore backend
- Modern Python with full type annotations and async patterns
"""

import logging

from fastmcp import FastMCP
from py_key_value_aio import DiskStore

from .config import MonitoringConfig
from .tools.correlation_tool import register_correlation_tool
from .tools.grafana_tool import register_grafana_tool
from .tools.loki_tool import register_loki_tool
from .tools.prometheus_tool import register_prometheus_tool
from .tools.status_tool import register_status_tool

# Configure structured logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MonitoringMCPServer:
    """
    FastMCP 2.14.3-powered monitoring server for Grafana, Prometheus, and Loki.

    Provides comprehensive observability tools with intelligent AI assistance
    for DevOps workflows, performance analysis, and system diagnostics.
    """

    def __init__(self, config: MonitoringConfig | None = None):
        """
        Initialize the Monitoring MCP server.

        Args:
            config: Optional configuration override. Defaults to environment-based config.
        """
        self.config = config or MonitoringConfig()
        self.mcp = FastMCP(
            name="monitoring-mcp",
            version="0.1.0",
            description="Intelligent monitoring operations for Grafana, Prometheus, and Loki",
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

        # Initialize persistent storage
        self.storage = DiskStore(
            path=self.config.storage_path / "monitoring_mcp",
            encryption_key=self.config.encryption_key,
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
        """
        Start the MCP server and begin listening for requests.

        This method handles the complete server lifecycle including
        startup, request processing, and graceful shutdown.
        """
        logger.info("Starting Monitoring MCP server...")

        try:
            # Initialize storage if needed
            await self.storage.initialize()

            # Start the MCP server
            await self.mcp.run()

        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Critical error in MCP server: {e}", exc_info=True)
            raise
        finally:
            # Cleanup resources
            await self._cleanup()

    async def _cleanup(self) -> None:
        """Clean up resources and close connections."""
        try:
            await self.storage.close()
            logger.info("Storage connections closed")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")


# Convenience function for direct usage
async def create_monitoring_server(
    grafana_url: str | None = None,
    prometheus_url: str | None = None,
    loki_url: str | None = None,
) -> MonitoringMCPServer:
    """
    Create a monitoring MCP server with custom endpoints.

    Args:
        grafana_url: Custom Grafana URL
        prometheus_url: Custom Prometheus URL
        loki_url: Custom Loki URL

    Returns:
        Configured MonitoringMCPServer instance
    """
    config = MonitoringConfig(
        grafana_url=grafana_url,
        prometheus_url=prometheus_url,
        loki_url=loki_url,
    )
    return MonitoringMCPServer(config)


if __name__ == "__main__":
    # Allow direct execution for development
    import asyncio

    server = MonitoringMCPServer()
    asyncio.run(server.run())
