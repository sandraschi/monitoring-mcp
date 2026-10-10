"""
ASGI entry point for uvicorn (web_sota backend).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from monitoring_mcp.mcp_server import MonitoringMCPServer, mcp
from monitoring_mcp.web import setup_webapp

_server: MonitoringMCPServer | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Construct the server once so REST endpoints see registered tools."""
    global _server
    _server = MonitoringMCPServer()
    await _server.storage.setup()
    yield
    await _server._cleanup()


# FastAPI app with auto-generated Swagger docs (/docs, /redoc, /openapi.json)
app = FastAPI(
    title="monitoring-mcp",
    version="0.1.0",
    description="REST API for monitoring-mcp. MCP tools (PromQL, LogQL, Grafana, …) "
    "run via stdio (Claude Desktop) or on a separate MCP HTTP port.",
    lifespan=lifespan,
)

# Register REST routes
setup_webapp(app, mcp_app=mcp)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:10850",
        "http://localhost:10850",
        "http://127.0.0.1:10851",
        "http://localhost:10851",
        "tauri://localhost",
        "http://tauri.localhost",
        "https://tauri.localhost",
    ],
    allow_origin_regex=r"https?://tauri\.localhost(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "server": "monitoring-mcp", "version": "0.1.0"}


@app.get("/api/v1/diagnostics")
async def diagnostics():
    tools = await mcp.list_tools()
    return {
        "status": "ok",
        "server": "monitoring-mcp",
        "version": "0.1.0",
        "tools": {"total": len(tools)},
        "system": {"windows": True},
        "errors": [],
    }
