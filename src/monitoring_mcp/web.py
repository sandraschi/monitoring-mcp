import logging
import os
import threading
import time

import httpx
from fastapi import Body, FastAPI, Response
from fastmcp import FastMCP

from .ai import AIRouter

logger = logging.getLogger(__name__)

_start_time = time.time()


async def _probe_llm_providers() -> dict:
    """Probe local LLM providers (Ollama :11434, LM Studio :1234) for reachability + models."""
    providers: dict = {"ollama": {"reachable": False, "models": []}, "lm_studio": {"reachable": False, "models": []}}
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get("http://127.0.0.1:11434/api/tags")
            if r.status_code == 200:
                data = r.json()
                providers["ollama"] = {
                    "reachable": True,
                    "models": [{"name": m["name"]} for m in data.get("models", [])],
                }
    except Exception:
        logger.debug("Ollama not reachable at 127.0.0.1:11434", exc_info=True)
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get("http://127.0.0.1:1234/v1/models")
            if r.status_code == 200:
                data = r.json()
                providers["lm_studio"] = {
                    "reachable": True,
                    "models": [{"name": m["id"]} for m in data.get("data", [])],
                }
    except Exception:
        logger.debug("LM Studio not reachable at 127.0.0.1:1234", exc_info=True)
    return providers


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

    @app.get("/api/capabilities")
    async def get_capabilities():
        tools = await mcp_app.list_tools()
        return {
            "server": "monitoring-mcp",
            "version": "0.1.0",
            "tools": [{"name": t.name, "description": (t.description or "")[:200]} for t in tools],
            "rest": [
                "GET /health",
                "GET /api/health",
                "GET /api/status",
                "GET /api/tools",
                "GET /api/capabilities",
                "GET /api/skills",
                "GET /api/skills/{name}",
                "GET /api/llm/discover",
                "GET /api/llm/providers",
                "GET /api/llm/models",
                "GET /api/llm/onboarding",
                "POST /api/chat",
                "POST /api/shutdown",
                "GET /api/v1/diagnostics",
            ],
            "features": {
                "chat": True,
                "skills": False,
                "llm_providers": ["ollama", "lm_studio"],
                "webhooks": False,
            },
        }

    @app.get("/api/skills")
    async def list_skills():
        return {"skills": []}

    @app.get("/api/skills/{name}")
    async def get_skill(name: str, response: Response):
        response.status_code = 404
        return {"error": f"Skill '{name}' not found", "skills": []}

    @app.get("/api/llm/discover")
    async def llm_discover():
        return await _probe_llm_providers()

    @app.get("/api/llm/providers")
    async def llm_providers():
        probed = await _probe_llm_providers()
        providers: dict = {"ollama": probed["ollama"]["models"], "lm_studio": probed["lm_studio"]["models"]}
        if not probed["ollama"]["reachable"] and not providers["ollama"]:
            providers["ollama"] = [{"name": "llama3.2:3b"}]
        return providers

    @app.get("/api/llm/models")
    async def llm_models():
        probed = await _probe_llm_providers()
        return {"models": {"ollama": probed["ollama"]["models"], "lm_studio": probed["lm_studio"]["models"]}}

    @app.get("/api/llm/onboarding")
    async def llm_onboarding():
        probed = await _probe_llm_providers()
        local_ready = probed["ollama"]["reachable"] or probed["lm_studio"]["reachable"]
        return {
            "fresh_install": not local_ready,
            "local_llm_ready": local_ready,
            "recommended_path": "Install Ollama (https://ollama.me) and pull llama3.2:3b, "
            "or point MONITORING_MCP_* env vars at your Grafana/Prometheus/Loki. "
            "See docs/ONBOARDING.md for the full checklist.",
            "facts": {
                "providers_probed": ["ollama (127.0.0.1:11434)", "lm_studio (127.0.0.1:1234)"],
                "chat_endpoint": "POST /api/chat",
                "docs": "docs/ONBOARDING.md",
            },
        }

    @app.post("/api/chat")
    async def chat(query: str = Body(..., embed=True)):
        response = await ai_router.process_command(query)
        return response

    @app.post("/api/shutdown")
    async def shutdown():
        threading.Timer(0.5, lambda: os._exit(0)).start()
        return {"status": "shutting_down", "message": "monitoring-mcp shutting down in ~500 ms"}

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
