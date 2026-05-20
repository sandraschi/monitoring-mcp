"""
ASGI entry point for uvicorn (web_sota backend).
"""

from monitoring_mcp.mcp_server import mcp

app = mcp.http_app()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}
