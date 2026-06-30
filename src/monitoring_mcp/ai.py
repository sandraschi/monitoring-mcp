import logging
from typing import Any

import httpx
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


class AIRouter:
    """AI router for monitoring MCP — calls Ollama / LM Studio for real responses."""

    def __init__(self, mcp_app: FastMCP):
        self.mcp = mcp_app
        self.provider = "ollama"
        self.base_url = "http://127.0.0.1:11434"
        self.model = "llama3.2:3b"

    async def process_command(self, query: str) -> dict[str, Any]:
        """Process a chat message via the local LLM provider."""
        try:
            if self.provider == "ollama":
                return await self._call_ollama(query)
            return await self._call_lm_studio(query)
        except Exception as e:
            logger.warning(f"AI call failed, returning tool list: {e}")
            return {
                "reply": f"I couldn't reach the LLM ({e}). Here are the tools I can use.",
                "tools": await self.get_tools_list(),
            }

    async def _call_ollama(self, query: str) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "prompt": f"You are a monitoring assistant. Answer concisely.\n\nUser: {query}\nAssistant:",
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(f"{self.base_url}/api/generate", json=payload)
            r.raise_for_status()
            data = r.json()
            return {"reply": data.get("response", ""), "provider": "ollama"}

    async def _call_lm_studio(self, query: str) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a monitoring assistant. Answer concisely."},
                {"role": "user", "content": query},
            ],
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(f"{self.base_url}/v1/chat/completions", json=payload)
            r.raise_for_status()
            data = r.json()
            text = data["choices"][0]["message"]["content"]
            return {"reply": text, "provider": "lm_studio"}

    async def get_tools_list(self) -> list[str]:
        tools = await self.mcp.list_tools()
        return [t.name for t in tools]
