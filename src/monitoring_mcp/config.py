"""
Monitoring MCP Configuration

FastMCP 2.14.3-compatible configuration with Pydantic v2 settings
for monitoring server endpoints, authentication, and storage.
"""

import secrets
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class MonitoringConfig(BaseSettings):
    """
    Configuration for the Monitoring MCP server.

    Uses Pydantic v2 BaseSettings for automatic environment variable loading
    and validation with support for secrets management.

    All configuration can be set via environment variables with the prefix
    MONITORING_MCP_, or loaded from a .env file in the working directory.

    Attributes:
        grafana_url: URL of the Grafana server to connect to
        prometheus_url: URL of the Prometheus server to connect to
        loki_url: URL of the Loki server to connect to
        request_timeout: Timeout for HTTP requests in seconds
        max_concurrent_requests: Maximum number of concurrent requests
        max_results_limit: Maximum number of results to return from queries
        enable_sampling: Whether to enable intelligent data sampling
        sampling_threshold: Threshold above which sampling is applied
        sampling_rate: Rate at which to sample data (0.0-1.0)
        storage_path: Path for persistent storage
        encryption_key: Key for encrypting stored data
        cache_ttl: Time-to-live for cached data in seconds
    """

    # Model configuration
    model_config = SettingsConfigDict(
        env_prefix="MONITORING_MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server endpoints
    grafana_url: str = Field(default="http://localhost:3000", description="Grafana server URL")
    prometheus_url: str = Field(
        default="http://localhost:9090", description="Prometheus server URL"
    )
    loki_url: str = Field(default="http://localhost:3100", description="Loki server URL")

    # Authentication
    grafana_api_key: SecretStr | None = Field(
        default=None, description="Grafana API key for authentication"
    )
    grafana_username: str | None = Field(
        default=None, description="Grafana username (alternative to API key)"
    )
    grafana_password: SecretStr | None = Field(
        default=None, description="Grafana password (alternative to API key)"
    )

    # Storage configuration
    storage_path: Path = Field(
        default_factory=lambda: Path.home() / ".monitoring-mcp",
        description="Path for persistent storage",
    )
    encryption_key: str = Field(
        default_factory=lambda: secrets.token_hex(32),
        description="Encryption key for sensitive data storage",
    )

    # Performance settings
    request_timeout: int = Field(default=30, description="Request timeout in seconds", ge=5, le=300)
    max_concurrent_requests: int = Field(
        default=10, description="Maximum concurrent requests", ge=1, le=100
    )
    max_results_limit: int = Field(
        default=1000, description="Maximum results to return in queries", ge=10, le=10000
    )

    # Logging
    log_level: str = Field(
        default="INFO", description="Logging level", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )
    enable_structured_logging: bool = Field(
        default=True, description="Enable structured JSON logging"
    )

    # Sampling configuration for large datasets
    enable_sampling: bool = Field(
        default=True, description="Enable intelligent sampling for large result sets"
    )
    sampling_threshold: int = Field(
        default=10000, description="Threshold for triggering sampling", ge=100, le=100000
    )
    sampling_rate: float = Field(
        default=0.1, description="Sampling rate (0.0-1.0)", ge=0.01, le=1.0
    )

    # Cache settings
    enable_cache: bool = Field(default=True, description="Enable response caching")
    cache_ttl_seconds: int = Field(default=300, description="Cache TTL in seconds", ge=60, le=3600)

    def get_grafana_auth(self) -> dict[str, str] | None:
        """
        Get Grafana authentication credentials.

        Returns:
            Dict with auth credentials or None if not configured
        """
        if self.grafana_api_key:
            return {"Authorization": f"Bearer {self.grafana_api_key.get_secret_value()}"}
        elif self.grafana_username and self.grafana_password:
            import base64

            auth_string = f"{self.grafana_username}:{self.grafana_password.get_secret_value()}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            return {"Authorization": f"Basic {encoded_auth}"}
        return None

    def validate_endpoints(self) -> list[str]:
        """
        Validate that configured endpoints are accessible.

        Returns:
            List of validation error messages (empty if all valid)
        """

        errors = []

        # Basic URL validation
        for name, url in [
            ("Grafana", self.grafana_url),
            ("Prometheus", self.prometheus_url),
            ("Loki", self.loki_url),
        ]:
            try:
                # Simple URL parsing validation
                from urllib.parse import urlparse

                parsed = urlparse(url)
                if not parsed.scheme or not parsed.netloc:
                    errors.append(f"Invalid {name} URL format: {url}")
            except Exception as e:
                errors.append(f"Error validating {name} URL: {e}")

        return errors

    def get_storage_path(self) -> Path:
        """
        Get the resolved storage path with platform-specific handling.

        Returns:
            Resolved Path object for storage
        """
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        return self.storage_path.resolve()

    def __str__(self) -> str:
        """Safe string representation that doesn't expose secrets."""
        return (
            f"MonitoringConfig("
            f"grafana_url='{self.grafana_url}', "
            f"prometheus_url='{self.prometheus_url}', "
            f"loki_url='{self.loki_url}', "
            f"storage_path='{self.storage_path}', "
            f"log_level='{self.log_level}', "
            f"request_timeout={self.request_timeout}s, "
            f"max_results_limit={self.max_results_limit}"
            f")"
        )


# Create default config instance
default_config = MonitoringConfig()
