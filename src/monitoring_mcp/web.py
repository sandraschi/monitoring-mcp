import json
import logging
import os
import threading
import time

import httpx
from fastapi import Body, FastAPI, Response
from fastapi.responses import StreamingResponse
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


def _fleet_overview_dashboard() -> dict:
    """Grafana dashboard JSON provisioned by POST /api/grafana/provision/fleet-overview.

    Panels target the default Prometheus datasource (datasource: null) so the
    dashboard works right after provisioning against the unified-* stack
    (unified-prometheus / unified-loki). Tweak queries after import.
    """
    panels = [
        {
            "id": 1,
            "title": "Targets Up",
            "type": "stat",
            "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0},
            "targets": [{"expr": "sum(up)", "refId": "A"}],
        },
        {
            "id": 2,
            "title": "Targets Down",
            "type": "stat",
            "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0},
            "targets": [{"expr": "sum(up == 0)", "refId": "A"}],
        },
        {
            "id": 3,
            "title": "Scrape Health",
            "type": "timeseries",
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
            "targets": [{"expr": "up", "legendFormat": "{{job}} / {{instance}}", "refId": "A"}],
        },
        {
            "id": 4,
            "title": "Node CPU (non-idle %)",
            "type": "timeseries",
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
            "targets": [
                {
                    "expr": '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)',
                    "legendFormat": "{{instance}}",
                    "refId": "A",
                }
            ],
        },
        {
            "id": 5,
            "title": "Node Memory Used %",
            "type": "timeseries",
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
            "targets": [
                {
                    "expr": "100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))",
                    "legendFormat": "{{instance}}",
                    "refId": "A",
                }
            ],
        },
        {
            "id": 6,
            "title": "Error logs (Loki)",
            "type": "logs",
            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16},
            "targets": [{"expr": '{job=~".+"} |= "error"', "refId": "A"}],
        },
    ]
    return {
        "title": "Fleet Overview (monitoring-mcp)",
        "tags": ["monitoring-mcp", "fleet", "provisioned"],
        "timezone": "browser",
        "schemaVersion": 39,
        "version": 1,
        "refresh": "30s",
        "time": {"from": "now-1h", "to": "now"},
        "panels": panels,
    }


def setup_webapp(app: FastAPI, mcp_app: FastMCP):
    """Setup REST endpoints for the monitoring-mcp web dashboard."""
    from monitoring_mcp.config import MonitoringConfig
    from monitoring_mcp.tools.grafana_tool import GrafanaClient
    from monitoring_mcp.tools.loki_tool import LokiClient
    from monitoring_mcp.tools.prometheus_tool import PrometheusClient

    ai_router = AIRouter(mcp_app)
    cfg = MonitoringConfig()
    prom = PrometheusClient(cfg)
    loki = LokiClient(cfg)
    grafana = GrafanaClient(cfg)

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
                "POST /api/chat/stream",
                "POST /api/llm/chat",
                "POST /api/webhooks/alertmanager",
                "POST /api/shutdown",
                "GET /api/v1/diagnostics",
                "GET /api/monitoring/config",
                "GET /api/monitoring/overview",
                "GET /api/prometheus/targets",
                "GET /api/prometheus/alerts",
                "GET /api/prometheus/rules",
                "GET /api/prometheus/build",
                "POST /api/prometheus/query",
                "POST /api/prometheus/query_range",
                "GET /api/loki/labels",
                "GET /api/loki/label/{name}/values",
                "POST /api/loki/query",
                "POST /api/loki/query_range",
                "GET /api/grafana/dashboards",
                "GET /api/grafana/dashboard/{uid}",
                "GET /api/grafana/datasources",
                "GET /api/grafana/folders",
                "POST /api/grafana/folders",
                "POST /api/grafana/dashboards",
                "DELETE /api/grafana/dashboard/{uid}",
                "POST /api/grafana/provision/fleet-overview",
                "GET /api/correlation/health",
                "POST /api/correlation/incident",
            ],
            "features": {
                "chat": True,
                "chat_stream": True,
                "skills": False,
                "llm_providers": ["ollama", "lm_studio"],
                "llm_chat_proxy": True,
                "webhooks": True,
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

    @app.post("/api/chat/stream")
    async def chat_stream(query: str = Body(..., embed=True)):
        async def _events():
            try:
                response = await ai_router.process_command(query)
                reply = str(response.get("reply", ""))
            except Exception as exc:
                yield f"data: {json.dumps({'error': str(exc)})}\n\n"
                return
            for i in range(0, max(len(reply), 1), 200):
                yield f"data: {json.dumps({'delta': reply[i : i + 200]})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(_events(), media_type="text/event-stream")

    @app.post("/api/llm/chat")
    async def llm_chat(payload: dict = Body(...)):
        from fastapi import status as _status

        messages = payload.get("messages", []) if isinstance(payload, dict) else []
        if not messages:
            return Response(
                content=json.dumps({"error": "messages array is required"}),
                status_code=_status.HTTP_400_BAD_REQUEST,
                media_type="application/json",
            )
        provider = payload.get("provider", "ollama")
        model = payload.get("model", "llama3.2:3b")
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                if provider == "lm_studio":
                    r = await client.post(
                        "http://127.0.0.1:1234/v1/chat/completions",
                        json={"model": model, "messages": messages, "stream": False},
                    )
                    r.raise_for_status()
                    text = r.json()["choices"][0]["message"]["content"]
                else:
                    r = await client.post(
                        "http://127.0.0.1:11434/api/chat",
                        json={"model": model, "messages": messages, "stream": False},
                    )
                    r.raise_for_status()
                    text = r.json().get("message", {}).get("content", "")
            return {"reply": text, "provider": provider, "model": model}
        except Exception as exc:
            return Response(
                content=json.dumps({"error": f"LLM provider unreachable: {exc}", "provider": provider}),
                status_code=_status.HTTP_502_BAD_GATEWAY,
                media_type="application/json",
            )

    @app.post("/api/webhooks/alertmanager")
    async def alertmanager_webhook(payload: dict = Body(...)):
        from fastapi import status as _status

        alerts = payload.get("alerts") if isinstance(payload, dict) else None
        if not isinstance(alerts, list):
            return Response(
                content=json.dumps({"error": "Alertmanager payload must contain an 'alerts' array"}),
                status_code=_status.HTTP_400_BAD_REQUEST,
                media_type="application/json",
            )
        names = [a.get("labels", {}).get("alertname", "?") for a in alerts if isinstance(a, dict)]
        logger.warning("Alertmanager webhook: %d alert(s): %s", len(alerts), ", ".join(names[:5]))
        return {"status": "ok", "received": len(alerts), "alerts": names}

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

    # ---- Monitoring: config + overview (used by Dashboard hero) ----

    @app.get("/api/monitoring/config")
    async def monitoring_config():
        def _host(url: str) -> str:
            try:
                from urllib.parse import urlparse

                return urlparse(url).netloc or url
            except Exception:
                return url

        return {
            "grafana_url": cfg.grafana_url,
            "prometheus_url": cfg.prometheus_url,
            "loki_url": cfg.loki_url,
            "alertmanager_url": cfg.alertmanager_url,
            "stack": {
                "grafana": _host(cfg.grafana_url),
                "prometheus": _host(cfg.prometheus_url),
                "loki": _host(cfg.loki_url),
            },
        }

    @app.get("/api/monitoring/overview")
    async def monitoring_overview():
        """Best-effort rollup for the Dashboard: never 500s when one backend is down."""
        overview: dict = {
            "grafana": {"status": "unknown"},
            "prometheus": {"status": "unknown"},
            "loki": {"status": "unknown"},
            "alerts": {"firing": 0, "total": 0},
        }
        try:
            sources = await grafana.list_datasources()
            overview["grafana"] = {
                "status": "up",
                "datasources": len(sources),
                "types": sorted({str(s.get("type")) for s in sources if s.get("type")}),
            }
        except Exception as exc:
            overview["grafana"] = {"status": "down", "error": str(exc)[:300]}
        try:
            targets = await prom.targets()
            active = targets.get("data", {}).get("activeTargets", [])
            overview["prometheus"] = {
                "status": "up",
                "targets_total": len(active),
                "targets_up": sum(1 for t in active if t.get("health") == "up"),
                "targets_down": sum(1 for t in active if t.get("health") == "down"),
            }
        except Exception as exc:
            overview["prometheus"] = {"status": "down", "error": str(exc)[:300]}
        try:
            labels = await loki.labels()
            names = labels.get("data", [])
            overview["loki"] = {"status": "up", "label_count": len(names), "labels": names[:20]}
        except Exception as exc:
            overview["loki"] = {"status": "down", "error": str(exc)[:300]}
        try:
            alerts = await prom.alerts()
            items = alerts.get("data", {}).get("alerts", [])
            overview["alerts"] = {
                "firing": sum(1 for a in items if a.get("state") == "firing"),
                "pending": sum(1 for a in items if a.get("state") == "pending"),
                "total": len(items),
                "sample": [
                    {
                        "name": (a.get("labels") or {}).get("alertname", "?"),
                        "state": a.get("state"),
                        "activeAt": a.get("activeAt"),
                    }
                    for a in items[:10]
                ],
            }
        except Exception as exc:
            overview["alerts"] = {"firing": 0, "total": 0, "error": str(exc)[:300]}
        return overview

    # ---- Prometheus ----

    @app.get("/api/prometheus/targets")
    async def prom_targets():
        return await prom.targets()

    @app.get("/api/prometheus/alerts")
    async def prom_alerts():
        return await prom.alerts()

    @app.get("/api/prometheus/rules")
    async def prom_rules():
        return await prom.rules()

    @app.get("/api/prometheus/build")
    async def prom_build():
        return await prom.buildinfo()

    @app.post("/api/prometheus/query")
    async def prom_query(payload: dict = Body(...)):
        query = (payload or {}).get("query", "")
        if not query:
            return Response(
                content=json.dumps({"error": "query is required"}),
                status_code=400,
                media_type="application/json",
            )
        return await prom.query(query, time=(payload or {}).get("time"))

    @app.post("/api/prometheus/query_range")
    async def prom_query_range(payload: dict = Body(...)):
        body = payload or {}
        for key in ("query", "start", "end"):
            if not body.get(key):
                return Response(
                    content=json.dumps({"error": f"{key} is required"}),
                    status_code=400,
                    media_type="application/json",
                )
        return await prom.query_range(body["query"], body["start"], body["end"], body.get("step", "15s"))

    # ---- Loki ----

    @app.get("/api/loki/labels")
    async def loki_labels():
        return await loki.labels()

    @app.get("/api/loki/label/{name}/values")
    async def loki_label_values(name: str):
        return await loki.label_values(name)

    @app.post("/api/loki/query")
    async def loki_query(payload: dict = Body(...)):
        body = payload or {}
        if not body.get("query"):
            return Response(
                content=json.dumps({"error": "query is required"}),
                status_code=400,
                media_type="application/json",
            )
        return await loki.query(body["query"], limit=int(body.get("limit", 100)))

    @app.post("/api/loki/query_range")
    async def loki_query_range(payload: dict = Body(...)):
        body = payload or {}
        for key in ("query", "start", "end"):
            if not body.get(key):
                return Response(
                    content=json.dumps({"error": f"{key} is required"}),
                    status_code=400,
                    media_type="application/json",
                )
        return await loki.query_range(body["query"], body["start"], body["end"], limit=int(body.get("limit", 200)))

    # ---- Grafana (active: list + create + provision) ----

    @app.get("/api/grafana/dashboards")
    async def grafana_dashboards(q: str | None = None):
        boards = await grafana.list_dashboards()
        if q:
            needle = q.lower()
            boards = [
                b
                for b in boards
                if needle in str(b.get("title", "")).lower()
                or any(needle in str(t).lower() for t in (b.get("tags") or []))
            ]
        return {"dashboards": boards, "count": len(boards)}

    @app.get("/api/grafana/dashboard/{uid}")
    async def grafana_dashboard(uid: str):
        return await grafana.get_dashboard(uid)

    @app.get("/api/grafana/datasources")
    async def grafana_datasources():
        sources = await grafana.list_datasources()
        return {"datasources": sources, "count": len(sources)}

    @app.get("/api/grafana/folders")
    async def grafana_folders():
        folders = await grafana.list_folders()
        return {"folders": folders, "count": len(folders)}

    @app.post("/api/grafana/folders")
    async def grafana_create_folder(payload: dict = Body(...)):
        title = (payload or {}).get("title", "")
        if not title:
            return Response(
                content=json.dumps({"error": "title is required"}),
                status_code=400,
                media_type="application/json",
            )
        return await grafana.create_folder(title, (payload or {}).get("uid"))

    @app.post("/api/grafana/dashboards")
    async def grafana_create_dashboard(payload: dict = Body(...)):
        body = payload or {}
        dashboard = body.get("dashboard")
        if not isinstance(dashboard, dict):
            return Response(
                content=json.dumps({"error": "dashboard (object) is required"}),
                status_code=400,
                media_type="application/json",
            )
        return await grafana.create_dashboard(dashboard, body.get("folderId"))

    @app.delete("/api/grafana/dashboard/{uid}")
    async def grafana_delete_dashboard(uid: str):
        return await grafana.delete_dashboard(uid)

    @app.post("/api/grafana/provision/fleet-overview")
    async def grafana_provision_fleet():
        """Active setup: ensure 'Fleet' folder + Fleet Overview dashboard exist."""
        folder_id: int | None = None
        try:
            folders = await grafana.list_folders()
            for folder in folders:
                if str(folder.get("title", "")).lower() == "fleet":
                    folder_id = folder.get("id")
                    break
            if folder_id is None:
                created = await grafana.create_folder("Fleet")
                folder_id = created.get("id")
        except Exception:
            folder_id = None
        dashboard = _fleet_overview_dashboard()
        # Overwrite path: reuse create with overwrite semantics via update if UID known.
        saved = await grafana._make_request(
            "POST",
            "dashboards/db",
            {"dashboard": dashboard, "folderId": folder_id, "overwrite": True},
        )
        return {"status": "ok", "folderId": folder_id, "dashboard": saved}

    # ---- Correlation / incidents ----

    @app.get("/api/correlation/health")
    async def correlation_health():
        """Lightweight health assessment without running the full LLM correlation."""
        from monitoring_mcp.tools.status_tool import (
            _check_alert_status,
            _check_system_health,
        )

        health = await _check_system_health(grafana, prom, loki, cfg, ["grafana", "prometheus", "loki"], False, False)
        alerts = await _check_alert_status(grafana, prom, loki, cfg, ["prometheus"], False, False)
        return {"health": health, "alerts": alerts}

    @app.post("/api/correlation/incident")
    async def correlation_incident(payload: dict = Body(...)):
        """Run the MCP correlation tool's incident path via direct client calls.

        Keeps the webapp dependency-free from FastMCP tool invocation plumbing:
        metrics query + error-log search + target health, returned as one bundle.
        """
        from monitoring_mcp.tools.correlation_tool import _execute_correlation_operation

        body = payload or {}
        return await _execute_correlation_operation(
            "correlate_incident",
            grafana,
            prom,
            loki,
            time_range=body.get("time_range"),
            service_name=body.get("service_name"),
            incident_description=body.get("incident_description", ""),
            metric_query=body.get("metric_query", "up == 0"),
            log_query=body.get("log_query", '{job=~".+"} |= "error"'),
        )
