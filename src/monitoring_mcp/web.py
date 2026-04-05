from fastapi import FastAPI, Body, Depends
from fastmcp import FastMCP
from .ai import AIRouter
from .auth import authenticate


def setup_webapp(app: FastAPI, mcp_app: FastMCP):
    """Setup standard SOTA web endpoints for System Monitoring Hub."""
    ai_router = AIRouter(mcp_app)

    @app.get("/api/status")
    async def get_status(user: str = Depends(authenticate)):
        return {"status": "connected", "user": user, "mcp": mcp_app.name}

    @app.get("/api/tools")
    async def list_tools(_user: str = Depends(authenticate)):
        tools = await ai_router.get_tools_list()
        return {"tools": tools}

    @app.post("/api/chat")
    async def chat(query: str = Body(..., embed=True), user: str = Depends(authenticate)):
        response = await ai_router.process_command(query)
        return response
