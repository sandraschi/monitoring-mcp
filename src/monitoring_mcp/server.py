"""
ASGI entry point for uvicorn (web_sota backend).
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from monitoring_mcp.mcp_server import mcp
from monitoring_mcp.web import setup_webapp

# FastAPI app with auto-generated Swagger docs (/docs, /redoc, /openapi.json)
app = FastAPI(
    title="monitoring-mcp",
    version="0.1.0",
    description="REST API for monitoring-mcp. MCP tools (PromQL, LogQL, Grafana, …) "
    "run via stdio (Claude Desktop) or on a separate MCP HTTP port.",
)

# Register REST routes
setup_webapp(app, mcp_app=mcp)

_tauri = os.environ.get("MONITORING_MCP_TAURI", "").lower() in ("1", "true", "yes")
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
    allow_origin_regex=r"https?://tauri\.localhost(:\d+)?" if _tauri else None,
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
