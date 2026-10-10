"""PyInstaller entrypoint for monitoring-mcp HTTP sidecar."""

from __future__ import annotations

import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    base = Path(sys._MEIPASS)
else:
    base = Path(__file__).resolve().parent
if str(base / "src") not in sys.path:
    sys.path.insert(0, str(base / "src"))

os.environ.setdefault("MCP_TRANSPORT", "http")

if __name__ == "__main__":
    import uvicorn

    from monitoring_mcp.server import app

    host = os.environ.get("MONITORING_HOST", "127.0.0.1")
    # backend.rs sets PORT=<BACKEND_PORT>; bind that so the webview health check passes.
    # Default matches the fleet registry (fleet-start.config.ps1 BackendPort 10851).
    port = int(os.environ.get("MONITORING_PORT") or os.environ.get("MCP_PORT") or os.environ.get("PORT", "10851"))
    log_level = os.environ.get("MONITORING_LOG_LEVEL", "info")
    uvicorn.run(app, host=host, port=port, log_level=log_level)
