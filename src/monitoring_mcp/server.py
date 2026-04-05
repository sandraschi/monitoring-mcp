"""
ASGI entry point for uvicorn (web_sota backend).
"""

from monitoring_mcp.mcp_server import mcp

app = mcp.http_app()
