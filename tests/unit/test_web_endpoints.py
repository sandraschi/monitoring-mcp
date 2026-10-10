"""REST endpoint tests for the monitoring-mcp web backend (pass-2 D3 surface)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from monitoring_mcp.config import MonitoringConfig
from monitoring_mcp.mcp_server import MonitoringMCPServer, mcp
from monitoring_mcp.server import app

client = TestClient(app)


def test_health_200():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_api_health_shape():
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["server"] == "monitoring-mcp"
    assert "uptime_seconds" in body
    assert "tool_count" in body


def test_capabilities_shape():
    body = client.get("/api/capabilities").json()
    assert body["server"] == "monitoring-mcp"
    assert isinstance(body["tools"], list)
    assert "GET /api/capabilities" in body["rest"]
    assert "POST /api/shutdown" in body["rest"]
    assert body["features"]["chat"] is True


def test_skills_empty_but_present():
    body = client.get("/api/skills").json()
    assert body == {"skills": []}


def test_skill_detail_404():
    r = client.get("/api/skills/does-not-exist")
    assert r.status_code == 404
    assert "error" in r.json()


def test_llm_discover_keys():
    body = client.get("/api/llm/discover").json()
    assert set(body) == {"ollama", "lm_studio"}
    assert "reachable" in body["ollama"]
    assert "models" in body["lm_studio"]


def test_llm_models_keys():
    body = client.get("/api/llm/models").json()
    assert set(body["models"]) == {"ollama", "lm_studio"}


def test_llm_providers_compat_shape():
    body = client.get("/api/llm/providers").json()
    assert set(body) == {"ollama", "lm_studio"}


def test_llm_onboarding_keys():
    body = client.get("/api/llm/onboarding").json()
    assert "recommended_path" in body
    assert "facts" in body
    assert "local_llm_ready" in body


def test_shutdown_endpoint_responds_before_exit():
    with patch("monitoring_mcp.web.threading.Timer") as mock_timer:
        r = client.post("/api/shutdown")
    assert r.status_code == 200
    assert r.json()["status"] == "shutting_down"
    mock_timer.assert_called_once()


def test_chat_stream_ends_with_done():
    r = client.post("/api/chat/stream", json={"query": "are you there"})
    assert r.status_code == 200
    assert "text/event-stream" in r.headers["content-type"]
    assert "[DONE]" in r.text


def test_llm_chat_proxy_declared_behavior():
    r = client.post(
        "/api/llm/chat",
        json={"messages": [{"role": "user", "content": "hi"}], "provider": "ollama"},
    )
    assert r.status_code in (200, 502)
    body = r.json()
    assert ("reply" in body) or ("error" in body)


def test_llm_chat_rejects_empty_messages():
    r = client.post("/api/llm/chat", json={"messages": []})
    assert r.status_code == 400


def test_alertmanager_webhook_receipt():
    payload = {
        "alerts": [
            {"labels": {"alertname": "HighErrorRate"}, "status": "firing"},
            {"labels": {"alertname": "DiskFull"}, "status": "resolved"},
        ]
    }
    r = client.post("/api/webhooks/alertmanager", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["received"] == 2
    assert body["alerts"] == ["HighErrorRate", "DiskFull"]


def test_alertmanager_webhook_rejects_malformed():
    r = client.post("/api/webhooks/alertmanager", json={"foo": "bar"})
    assert r.status_code == 400


async def test_shutdown_tool_registered(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("MONITORING_MCP_STORAGE_PATH", str(tmp_path))
    MonitoringMCPServer(MonitoringConfig(enable_cache=False))
    tools = await mcp.list_tools()
    names = [t.name for t in tools]
    assert "monitoring_shutdown" in names
    for expected in (
        "grafana_management",
        "prometheus_monitoring",
        "loki_logging",
        "cross_system_correlation",
        "monitoring_status",
    ):
        assert expected in names


async def test_all_tools_carry_annotations(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("MONITORING_MCP_STORAGE_PATH", str(tmp_path))
    MonitoringMCPServer(MonitoringConfig(enable_cache=False))
    tools = await mcp.list_tools()
    by_name = {t.name: t for t in tools}
    assert by_name["cross_system_correlation"].annotations.readOnlyHint is True
    assert by_name["monitoring_status"].annotations.readOnlyHint is True
    assert by_name["monitoring_shutdown"].annotations.destructiveHint is True
    assert by_name["grafana_management"].annotations.openWorldHint is True
    for tool in tools:
        assert tool.annotations is not None


async def test_prompts_and_resource_registered(tmp_path: Path, monkeypatch):
    from monitoring_mcp.skills_prompts import register_skills_prompts

    monkeypatch.setenv("MONITORING_MCP_STORAGE_PATH", str(tmp_path))
    MonitoringMCPServer(MonitoringConfig(enable_cache=False))
    register_skills_prompts(mcp)
    prompts = await mcp.list_prompts()
    assert {"incident_triage", "dashboard_review"} <= {p.name for p in prompts}
    resources = await mcp.list_resources()
    assert any(str(r.uri) == "monitoring://capabilities" for r in resources)


async def test_shutdown_tool_docstring_compliance():
    from fastmcp import FastMCP

    from monitoring_mcp.tools.shutdown_tool import register_shutdown_tool

    fresh = FastMCP(name="probe")
    register_shutdown_tool(fresh)
    tools = await fresh.list_tools()
    matches = [t for t in tools if t.name == "monitoring_shutdown"]
    assert len(matches) == 1
    assert "## Return Format" in (matches[0].description or "")
    assert "## Examples" in (matches[0].description or "")
