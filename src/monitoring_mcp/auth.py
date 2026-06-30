import os
import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


def _require_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise RuntimeError(f"Authentication not configured: set {key} environment variable")
    return val


def authenticate(credentials: HTTPBasicCredentials = Security(security)):
    """Basic auth via MCP_WEB_USER / MCP_WEB_PASSWORD env vars."""
    expected_user = _require_env("MCP_WEB_USER")
    expected_pass = _require_env("MCP_WEB_PASSWORD")

    if not (
        secrets.compare_digest(credentials.username, expected_user)
        and secrets.compare_digest(credentials.password, expected_pass)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
