"""
Unit tests for the Monitoring MCP server.

Tests the core server functionality, configuration, and tool registration.
"""

from unittest.mock import AsyncMock, patch

import pytest

from monitoring_mcp.config import MonitoringConfig
from monitoring_mcp.mcp_server import MonitoringMCPServer


class TestMonitoringConfig:
    """Test the MonitoringConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = MonitoringConfig()

        assert config.grafana_url == "http://localhost:3000"
        assert config.prometheus_url == "http://localhost:9090"
        assert config.loki_url == "http://localhost:3100"
        assert config.request_timeout == 30
        assert config.max_results_limit == 1000
        assert config.enable_sampling is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = MonitoringConfig(
            grafana_url="http://custom-grafana:3000",
            prometheus_url="http://custom-prometheus:9090",
            request_timeout=60,
            max_results_limit=500,
        )

        assert config.grafana_url == "http://custom-grafana:3000"
        assert config.prometheus_url == "http://custom-prometheus:9090"
        assert config.request_timeout == 60
        assert config.max_results_limit == 500

    def test_grafana_auth_api_key(self):
        """Test Grafana API key authentication."""
        config = MonitoringConfig(grafana_api_key="test-api-key")

        auth = config.get_grafana_auth()
        assert auth is not None
        assert "Authorization" in auth
        assert "Bearer test-api-key" in auth["Authorization"]

    def test_grafana_auth_username_password(self):
        """Test Grafana username/password authentication."""
        config = MonitoringConfig(grafana_username="admin", grafana_password="password123")

        auth = config.get_grafana_auth()
        assert auth is not None
        assert "Authorization" in auth
        assert auth["Authorization"].startswith("Basic ")

    def test_config_validation(self):
        """Test configuration validation."""
        config = MonitoringConfig()
        errors = config.validate_endpoints()

        # Should not have errors for default localhost URLs
        # (though they won't be reachable, URLs should be valid)
        assert isinstance(errors, list)

    def test_storage_path_resolution(self):
        """Test storage path resolution."""
        config = MonitoringConfig()
        path = config.get_storage_path()

        assert path.exists() or path.parent.exists()  # Either path exists or parent does


class TestMonitoringMCPServer:
    """Test the MonitoringMCPServer class."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return MonitoringConfig(
            grafana_url="http://test-grafana:3000",
            prometheus_url="http://test-prometheus:9090",
            loki_url="http://test-loki:3100",
        )

    @pytest.fixture
    def server(self, config):
        """Create a test server instance."""
        return MonitoringMCPServer(config)

    def test_server_initialization(self, server):
        """Test server initialization."""
        assert server.config is not None
        assert hasattr(server, "mcp")
        assert hasattr(server, "storage")

    @patch("monitoring_mcp.mcp_server.register_grafana_tool")
    @patch("monitoring_mcp.mcp_server.register_prometheus_tool")
    @patch("monitoring_mcp.mcp_server.register_loki_tool")
    @patch("monitoring_mcp.mcp_server.register_correlation_tool")
    @patch("monitoring_mcp.mcp_server.register_status_tool")
    def test_tool_registration(
        self, mock_status, mock_correlation, mock_loki, mock_prometheus, mock_grafana, server
    ):
        """Test that all tools are registered."""
        # Reset mocks to check calls
        mock_grafana.reset_mock()
        mock_prometheus.reset_mock()
        mock_loki.reset_mock()
        mock_correlation.reset_mock()
        mock_status.reset_mock()

        # Re-initialize to trigger registration
        server._register_tools()

        # Verify all tools were registered
        mock_grafana.assert_called_once()
        mock_prometheus.assert_called_once()
        mock_loki.assert_called_once()
        mock_correlation.assert_called_once()
        mock_status.assert_called_once()

    @patch("monitoring_mcp.mcp_server.MonitoringMCPServer._cleanup")
    @patch("monitoring_mcp.mcp_server.MonitoringMCPServer.storage")
    async def test_server_lifecycle(self, mock_storage, mock_cleanup, server):
        """Test server startup and shutdown lifecycle."""
        # Mock the MCP run method
        with (
            patch.object(server.mcp, "run", new_callable=AsyncMock) as mock_run,
            patch.object(server.storage, "initialize", new_callable=AsyncMock) as mock_init,
        ):
            # Mock KeyboardInterrupt to exit cleanly
            mock_run.side_effect = KeyboardInterrupt()

            # Run the server
            await server.run()

            # Verify initialization and cleanup were called
            mock_init.assert_called_once()
            mock_cleanup.assert_called_once()

    async def test_cleanup_handles_errors(self, server):
        """Test that cleanup handles storage errors gracefully."""
        with patch.object(server.storage, "close", side_effect=Exception("Storage error")):
            # Should not raise exception
            await server._cleanup()

    def test_server_string_representation(self, server):
        """Test server string representation."""
        # Should not expose sensitive information
        str_repr = str(server.config)
        assert "MonitoringConfig" in str_repr
        assert "localhost:3000" in str_repr
        assert "localhost:9090" in str_repr
        assert "localhost:3100" in str_repr


class TestCreateMonitoringServer:
    """Test the convenience server creation function."""

    @patch("monitoring_mcp.mcp_server.MonitoringMCPServer")
    def test_create_server_with_defaults(self, mock_server_class):
        """Test creating server with default parameters."""
        from monitoring_mcp.mcp_server import create_monitoring_server

        create_monitoring_server()

        # Verify MonitoringMCPServer was called with default config
        mock_server_class.assert_called_once()
        call_args = mock_server_class.call_args
        config = call_args[0][0]

        assert config.grafana_url is None  # Should use defaults
        assert config.prometheus_url is None
        assert config.loki_url is None

    @patch("monitoring_mcp.mcp_server.MonitoringMCPServer")
    def test_create_server_with_custom_urls(self, mock_server_class):
        """Test creating server with custom URLs."""
        from monitoring_mcp.mcp_server import create_monitoring_server

        create_monitoring_server(
            grafana_url="http://custom-grafana:3000",
            prometheus_url="http://custom-prometheus:9090",
            loki_url="http://custom-loki:3100",
        )

        # Verify MonitoringMCPServer was called with custom config
        mock_server_class.assert_called_once()
        call_args = mock_server_class.call_args
        config = call_args[0][0]

        assert config.grafana_url == "http://custom-grafana:3000"
        assert config.prometheus_url == "http://custom-prometheus:9090"
        assert config.loki_url == "http://custom-loki:3100"


# Integration test placeholder
@pytest.mark.integration
class TestMonitoringMCPIntegration:
    """Integration tests for the Monitoring MCP server."""

    def test_full_server_initialization(self):
        """Test that server can be fully initialized (requires external services)."""
        # This test would require running Grafana, Prometheus, and Loki
        # For now, just verify the server can be created
        config = MonitoringConfig()
        server = MonitoringMCPServer(config)

        assert server is not None
        assert hasattr(server, "run")

    @pytest.mark.asyncio
    async def test_server_handles_graceful_shutdown(self):
        """Test that server handles shutdown signals gracefully."""
        config = MonitoringConfig()
        server = MonitoringMCPServer(config)

        # Mock the MCP to raise KeyboardInterrupt immediately
        with (
            patch.object(server.mcp, "run", side_effect=KeyboardInterrupt()),
            patch.object(server.storage, "initialize", new_callable=AsyncMock),
            patch.object(server, "_cleanup", new_callable=AsyncMock) as mock_cleanup,
        ):
            await server.run()
            mock_cleanup.assert_called_once()
