import logging
import time

import httpx
from fastapi import Body, FastAPI
from fastmcp import FastMCP

from .ai import AIRouter

logger = logging.getLogger(__name__)

_start_time = time.time()


def setup_webapp(app: FastAPI, mcp_app: FastMCP):
    """Setup REST endpoints for the monitoring-mcp web dashboard."""
    ai_router = AIRouter(mcp_app)

    @app.get("/api/status")
    async def get_status():
        return {"status": "connected", "mcp": mcp_app.name}

    @app.get("/api/tools")
    async def list_tools():
        tools = await ai_router.get_tools_list()
        return {"tools": tools}

    @app.post("/api/chat")
    async def chat(query: str = Body(..., embed=True)):
        response = await ai_router.process_command(query)
        return response

    @app.get("/api/llm/providers")
    async def llm_providers():
        providers = {"ollama": [], "lm_studio": []}
        try:
            async with httpx.AsyncClient(timeout=3) as client:
                r = await client.get("http://127.0.0.1:11434/api/tags")
                if r.status_code == 200:
                    data = r.json()
                    providers["ollama"] = [{"name": m["name"]} for m in data.get("models", [])]
        except Exception:
            providers["ollama"] = [{"name": "llama3.2:3b"}]
        try:
            async with httpx.AsyncClient(timeout=3) as client:
                r = await client.get("http://127.0.0.1:1234/v1/models")
                if r.status_code == 200:
                    data = r.json()
                    providers["lm_studio"] = [{"name": m["id"]} for m in data.get("data", [])]
        except Exception:
            pass
        return providers

    @app.get("/api/health")
    async def api_health():
        tools = await mcp_app.list_tools()
        return {
            "status": "ok",
            "server": "monitoring-mcp",
            "version": "0.1.0",
            "uptime_seconds": int(time.time() - _start_time),
            "tool_count": len(tools),
        }
