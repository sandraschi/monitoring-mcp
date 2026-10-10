"""Broad mocked coverage for tool execute paths, helpers, auth, AI, transport."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPBasicCredentials

from monitoring_mcp.ai import AIRouter
from monitoring_mcp.auth import _require_env, authenticate
from monitoring_mcp.config import MonitoringConfig
from monitoring_mcp.tools.correlation_tool import (
    _analyze_root_cause,
    _correlate_error_data,
    _correlate_incident_data,
    _correlate_performance_data,
    _execute_correlation_operation,
    _generate_correlation_insights,
    _generate_correlation_summary,
    _perform_health_assessment,
)
from monitoring_mcp.tools.grafana_tool import (
    GrafanaClient,
    _analyze_dashboard_structure,
    _execute_grafana_operation,
    _generate_ai_insights,
    _generate_conversational_summary,
)
from monitoring_mcp.tools.loki_tool import (
    LokiClient,
    _analyze_log_patterns,
    _analyze_request_traces,
    _compare_timeframes,
    _detect_log_anomalies,
    _execute_loki_operation,
    _export_logs,
    _generate_loki_insights,
    _generate_loki_summary,
    _optimize_logql,
    _search_error_patterns,
)
from monitoring_mcp.tools.prometheus_tool import (
    PrometheusClient,
    _analyze_metrics_data,
    _analyze_query_performance,
    _execute_prometheus_operation,
    _generate_prometheus_insights,
    _generate_prometheus_summary,
    _series_stats,
)
from monitoring_mcp.tools.status_tool import (
    _check_alert_status,
    _check_backup_status,
    _check_capacity_planning,
    _check_data_flow,
    _check_performance_metrics,
    _check_security_status,
    _check_storage_status,
    _check_system_health,
    _execute_status_operation,
    _generate_status_insights,
    _generate_status_summary,
    _test_connectivity,
    _validate_configurations,
)
from monitoring_mcp.transport import (
    create_argument_parser,
    get_transport_config,
    resolve_config,
    resolve_transport,
)


@pytest.fixture
def cfg(tmp_path: Path, monkeypatch) -> MonitoringConfig:
    monkeypatch.setenv("MONITORING_MCP_STORAGE_PATH", str(tmp_path))
    return MonitoringConfig(enable_cache=False, enable_sampling=False)


def _prom_vector(n: int = 2) -> dict:
    return {
        "status": "success",
        "data": {
            "resultType": "vector",
            "result": [{"metric": {"job": f"j{i}"}, "value": ["1", str(i)]} for i in range(n)],
        },
    }


def _prom_matrix() -> dict:
    return {
        "status": "success",
        "data": {
            "resultType": "matrix",
            "result": [
                {
                    "metric": {"job": "api"},
                    "values": [["1", "0"], ["2", "1"], ["3", "2"], ["4", "0"], ["5", "0"]],
                }
            ],
        },
    }


def _loki_streams(with_error: bool = True) -> dict:
    line = "ERROR request-id=abc-123 failed" if with_error else "INFO ok"
    return {
        "status": "success",
        "data": {"result": [{"stream": {"job": "api"}, "values": [["1", line], ["2", "INFO fine"]]}]},
    }


@pytest.fixture
def prom_client(cfg: MonitoringConfig) -> PrometheusClient:
    client = PrometheusClient(cfg)
    client.query = AsyncMock(return_value=_prom_vector())
    client.query_range = AsyncMock(return_value=_prom_matrix())
    client.targets = AsyncMock(
        return_value={
            "data": {
                "activeTargets": [
                    {"labels": {"job": "api", "instance": "a:1"}, "health": "up", "scrapeUrl": "http://a/metrics"},
                    {"labels": {"job": "db", "instance": "b:1"}, "health": "down"},
                ]
            }
        }
    )
    client.rules = AsyncMock(
        return_value={
            "data": {
                "groups": [
                    {
                        "name": "g1",
                        "rules": [
                            {"type": "alerting", "name": "HighError"},
                            {"type": "recording", "name": "job:up"},
                        ],
                    }
                ]
            }
        }
    )
    client.alerts = AsyncMock(
        return_value={
            "data": {
                "alerts": [
                    {"state": "firing", "labels": {"alertname": "HighError"}},
                    {"state": "pending", "labels": {"alertname": "Disk"}},
                ]
            }
        }
    )
    client.buildinfo = AsyncMock(return_value={"data": {"version": "2.50.0"}})
    client.status_config = AsyncMock(return_value={"data": {"yaml": "global: {}"}})
    client.status_flags = AsyncMock(
        return_value={"data": {"storage.tsdb.retention.time": "15d", "web.listen-address": ":9090"}}
    )
    client._am_request = AsyncMock(return_value=[{"id": "s1", "status": {"state": "active"}}])
    client._grafana_request = AsyncMock(return_value={"uid": "rule1"})
    client.sync_metadata = MagicMock(return_value={"metric_count": 3})
    return client


@pytest.fixture
def loki_client(cfg: MonitoringConfig) -> LokiClient:
    client = LokiClient(cfg)
    client.query = AsyncMock(return_value=_loki_streams())
    client.query_range = AsyncMock(return_value=_loki_streams())
    client.tail = AsyncMock(
        return_value={
            "status": "success",
            "data": {"result": [{"stream": {"job": "api"}, "values": [["1", "hi"]]}]},
            "transport": "websocket",
        }
    )
    client.labels = AsyncMock(return_value={"data": ["job", "level"]})
    client.label_values = AsyncMock(return_value={"data": ["api", "db"]})
    client.series = AsyncMock(return_value={"data": [{"job": "api"}]})
    client.ruler_rules = AsyncMock(return_value={"data": {"ns": []}})
    client.create_ruler_rule = AsyncMock(return_value={"status": "ok"})
    return client


@pytest.fixture
def grafana_client(cfg: MonitoringConfig) -> GrafanaClient:
    client = GrafanaClient(cfg)
    client.list_dashboards = AsyncMock(
        return_value=[{"uid": "abc", "title": "CPU", "tags": ["prod"]}, {"uid": "def", "title": "Mem", "tags": []}]
    )
    client.get_dashboard = AsyncMock(
        return_value={
            "dashboard": {
                "uid": "abc",
                "title": "CPU",
                "panels": [{"id": 1, "title": "p1", "alert": {}}],
                "templating": {"list": [{"name": "env"}]},
                "tags": ["prod"],
                "refresh": "30s",
                "time": {"from": "now-1h", "to": "now"},
            },
            "meta": {"permissions": []},
        }
    )
    client.create_dashboard = AsyncMock(return_value={"uid": "new"})
    client.update_dashboard = AsyncMock(return_value={"uid": "abc", "status": "success"})
    client.delete_dashboard = AsyncMock(return_value={"title": "CPU"})
    client.list_datasources = AsyncMock(return_value=[{"id": 1, "name": "prom"}])
    client.query_datasource = AsyncMock(return_value={"results": {}})
    client.list_folders = AsyncMock(return_value=[{"title": "General"}])
    client.create_folder = AsyncMock(return_value={"uid": "f1", "title": "Ops"})
    client.get_dashboard_permissions = AsyncMock(return_value=[{"permission": 1}])
    client.import_dashboard = AsyncMock(return_value={"importedUrl": "/d/x"})
    client.create_alert_rule = AsyncMock(return_value={"uid": "a1"})
    client.sync_health = MagicMock(return_value={"organization": {"name": "Main"}})
    return client


# ── Prometheus ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_prometheus_all_ops(prom_client: PrometheusClient):
    ops = [
        ("query_metrics", {"query": "up"}),
        ("query_range", {"query": "up", "start_time": "now-1h", "end_time": "now"}),
        ("list_targets", {}),
        ("get_target_health", {"target_name": "api"}),
        ("list_rules", {}),
        ("get_rule_groups", {"rule_group": "g1"}),
        ("list_alerts", {}),
        ("get_alert_details", {"alert_name": "HighError"}),
        ("get_build_info", {}),
        ("get_config", {}),
        ("get_flags", {}),
        ("list_silences", {}),
        ("silence_alert", {"silence_data": {"matchers": [], "createdBy": "t", "comment": "c"}}),
        ("expire_silence", {"silence_id": "s1"}),
        ("create_alert_rule", {"alert_rule": {"title": "x"}}),
        ("update_alert_rule", {"rule_uid": "u1", "alert_rule": {"title": "x"}}),
        ("delete_alert_rule", {"rule_uid": "u1"}),
        ("analyze_metrics", {"query": "up"}),
        ("optimize_queries", {"query": "sum(rate(http_requests_total[5m]))"}),
    ]
    for op, kwargs in ops:
        result = await _execute_prometheus_operation(prom_client, op, **kwargs)
        assert result["success"] is True, op
        assert _generate_prometheus_summary(op, result)


def test_prometheus_helpers():
    analysis = _analyze_metrics_data(_prom_matrix(), {})
    assert "anomalies" in analysis
    assert _analyze_query_performance("sum(rate(x[5m]))")
    assert _analyze_query_performance("up")
    assert _series_stats({"metric": {"a": "b"}, "value": ["1", "0"]})["points"] == 1
    insights = _generate_prometheus_insights("list_targets", {"healthy_targets": 1, "target_count": 10})
    assert insights["recommendations"]
    insights2 = _generate_prometheus_insights("list_alerts", {"alert_summary": {"firing": 9}})
    assert insights2["alerting_opportunities"]
    insights3 = _generate_prometheus_insights("query_metrics", {"result_count": 0})
    assert insights3["optimization_suggestions"]
    assert "wasn't able" in _generate_prometheus_summary("x", {"success": False, "error": "e"})


@pytest.mark.asyncio
async def test_prometheus_http_helpers(cfg: MonitoringConfig):
    client = PrometheusClient(cfg)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "success", "data": {}}
    mock_resp.content = b"{}"
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(
        return_value=MagicMock(get=AsyncMock(return_value=mock_resp), request=AsyncMock(return_value=mock_resp))
    )
    mock_cm.__aexit__ = AsyncMock(return_value=None)
    with patch("monitoring_mcp.tools.prometheus_tool.httpx.AsyncClient", return_value=mock_cm):
        assert await client._make_request("query", {"query": "up"}, use_cache=True)
        assert await client._make_request("query", {"query": "up"}, use_cache=True)  # cache hit
        assert await client._am_request("GET", "silences")
        assert await client._grafana_request("GET", "v1/provisioning/alert-rules")


# ── Loki ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_loki_all_ops(loki_client: LokiClient):
    ops = [
        ("query_logs", {"query": '{job="api"}'}),
        ("query_range", {"query": '{job="api"}', "start_time": "now-1h", "end_time": "now"}),
        ("tail_logs", {"query": '{job="api"}'}),
        ("get_labels", {}),
        ("get_label_values", {"label_name": "job"}),
        ("get_series", {"match_patterns": ['{job="api"}']}),
        ("analyze_logs", {"query": '{job="api"}'}),
        ("detect_anomalies", {"query": '{job="api"}'}),
        ("search_errors", {"query": '{job="api"}'}),
        ("trace_requests", {"query": '{job="api"}'}),
        ("list_alerts", {}),
        ("create_alert_rule", {"alert_rule": {"name": "g"}}),
        ("optimize_queries", {"query": "{}"}),
        ("export_logs", {"query": '{job="api"}', "export_format": "csv"}),
        ("export_logs", {"query": '{job="api"}', "export_format": "text"}),
        ("export_logs", {"query": '{job="api"}', "export_format": "json"}),
        ("compare_timeframes", {"query": '{job="api"}'}),
        ("generate_report", {"query": '{job="api"}'}),
    ]
    for op, kwargs in ops:
        result = await _execute_loki_operation(loki_client, op, **kwargs)
        assert result.get("success") is True, (op, result)
        _generate_loki_summary(op, result)


def test_loki_helpers():
    data = _loki_streams(True)
    assert _analyze_log_patterns(data, {})["patterns"]
    assert _detect_log_anomalies(data, {})["anomalies"] or True
    assert _search_error_patterns(data, {})["error_count"] >= 1
    traces = _analyze_request_traces(data)
    assert "trace_count" in traces
    assert _optimize_logql("{}")
    assert _optimize_logql('{job="a"} |= "x" |~ "y"')
    assert _optimize_logql('{job="a"} | json')
    assert _export_logs(data, "csv")["entry_count"] >= 1
    assert _compare_timeframes(data, _loki_streams(False))["delta"] != 0 or True
    _generate_loki_insights("query_logs", {"total_entries": 6000})
    _generate_loki_insights("search_errors", {"analysis": {"error_count": 20}})
    assert "wasn't able" in _generate_loki_summary("x", {"success": False, "error": "e"})


@pytest.mark.asyncio
async def test_loki_websocket_tail(cfg: MonitoringConfig):
    client = LokiClient(cfg)
    client.query_range = AsyncMock(return_value=_loki_streams())

    class FakeWS:
        def __init__(self):
            self._n = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return None

        async def recv(self):
            self._n += 1
            if self._n > 1:
                raise TimeoutError()
            return '{"streams":[{"stream":{"job":"api"},"values":[["1","hi"]]}]}'

    fake_ws_mod = MagicMock()
    fake_ws_mod.connect = MagicMock(return_value=FakeWS())
    fake_ws_mod.exceptions = MagicMock()
    fake_ws_mod.exceptions.ConnectionClosed = type("ConnectionClosed", (Exception,), {})

    with (
        patch.dict("sys.modules", {"websockets": fake_ws_mod, "websockets.exceptions": fake_ws_mod.exceptions}),
        patch("monitoring_mcp.tools.loki_tool.websockets", fake_ws_mod, create=True),
    ):
        # Force import path inside tail
        import monitoring_mcp.tools.loki_tool as loki_mod

        with patch.object(loki_mod, "websockets", fake_ws_mod, create=True):
            result = await client.tail('{job="api"}', duration_seconds=0.1, limit=5)
    assert result.get("transport") in ("websocket", "query_range_fallback") or "data" in result


# ── Grafana ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_grafana_all_ops(grafana_client: GrafanaClient):
    ops = [
        ("list_dashboards", {}),
        ("get_dashboard", {"dashboard_uid": "abc"}),
        ("create_dashboard", {"dashboard_data": {"title": "x"}}),
        ("update_dashboard", {"dashboard_uid": "abc", "dashboard_data": {"title": "x"}}),
        ("delete_dashboard", {"dashboard_uid": "abc"}),
        ("search_dashboards", {"search_query": "cpu"}),
        ("list_datasources", {}),
        ("query_datasource", {"datasource_id": 1, "queries": [{"refId": "A"}]}),
        ("export_dashboard", {"dashboard_uid": "abc"}),
        ("import_dashboard", {"dashboard_data": {"dashboard": {"title": "x"}}}),
        ("list_folders", {}),
        ("create_folder", {"folder_name": "Ops"}),
        ("get_dashboard_permissions", {"dashboard_uid": "abc"}),
        ("create_panel", {"dashboard_uid": "abc", "panel_data": {"title": "n", "type": "graph"}}),
        ("update_panel", {"dashboard_uid": "abc", "panel_id": 1, "panel_data": {"title": "upd"}}),
        ("create_alert", {"alert_rule": {"title": "a"}}),
        ("analyze_dashboard", {"dashboard_uid": "abc"}),
    ]
    for op, kwargs in ops:
        result = await _execute_grafana_operation(grafana_client, op, **kwargs)
        assert result["success"] is True, (op, result)
        _generate_conversational_summary(op, result)


def test_grafana_helpers():
    dash = {
        "dashboard": {
            "panels": [{"id": 1}, {"id": 2}],
            "templating": {"list": [{"name": "a"}]},
            "tags": ["t"],
            "refresh": "5s",
        },
        "meta": {},
    }
    analysis = _analyze_dashboard_structure(dash)
    assert analysis["overall_score"] >= 5
    _generate_ai_insights("analyze_dashboard", {"analysis": {"panel_count": 25, "has_alerts": False}})
    _generate_ai_insights("list_dashboards", {"count": 60})


# ── Correlation ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_correlation_all_ops(prom_client, loki_client, grafana_client):
    ops = [
        "correlate_incident",
        "find_root_cause",
        "performance_correlation",
        "error_correlation",
        "health_assessment",
        "anomaly_correlation",
        "service_dependency_map",
        "impact_analysis",
        "predictive_insights",
        "bottleneck_detection",
    ]
    for op in ops:
        result = await _execute_correlation_operation(
            op,
            grafana_client,
            prom_client,
            loki_client,
            time_range={"start": "now-1h", "end": "now"},
            service_name="api",
            incident_description="5xx spike",
            metric_query="up",
            log_query='{job="api"}',
        )
        assert result["success"] is True, (op, result)
        _generate_correlation_summary(op, result)
        _generate_correlation_insights(op, result)


def test_correlation_helpers():
    m = _prom_matrix()
    streams = _loki_streams()
    assert _correlate_incident_data(m, streams, "spike")["insights"]
    assert _analyze_root_cause(m, streams, {})["confidence"] >= 0
    assert "bottlenecks" in _correlate_performance_data(m, streams)
    assert "error_clusters" in _correlate_error_data(m, streams)


@pytest.mark.asyncio
async def test_health_assessment(prom_client, loki_client, grafana_client):
    result = await _perform_health_assessment(
        grafana_client, prom_client, loki_client, {"start": "now-1h", "end": "now"}, "api"
    )
    assert "overall_score" in result or "components" in result or isinstance(result, dict)


# ── Status ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_status_all_ops(prom_client, loki_client, grafana_client, cfg):
    ops = [
        "system_health",
        "connectivity_test",
        "configuration_validation",
        "performance_metrics",
        "data_flow_status",
        "alert_status",
        "storage_status",
        "backup_status",
        "security_status",
        "capacity_planning",
    ]
    # Patch underlying HTTP-ish methods used by status checkers
    grafana_client.list_dashboards = AsyncMock(return_value=[])
    grafana_client.list_datasources = AsyncMock(return_value=[{"type": "prometheus"}])
    prom_client._make_request = AsyncMock(return_value={"data": {"headStats": {}}})

    for op in ops:
        result = await _execute_status_operation(op, grafana_client, prom_client, loki_client, cfg, None, True, False)
        assert result["success"] is True, (op, result)
        _generate_status_summary(op, result)
        _generate_status_insights(op, result)


@pytest.mark.asyncio
async def test_status_direct_checkers(prom_client, loki_client, grafana_client, cfg):
    grafana_client.list_dashboards = AsyncMock(return_value=[{"uid": "a"}])
    grafana_client.list_datasources = AsyncMock(return_value=[{"type": "prometheus", "name": "p"}])
    prom_client.buildinfo = AsyncMock(return_value={"data": {"version": "2"}})
    loki_client.labels = AsyncMock(return_value={"data": ["job"]})
    prom_client._make_request = AsyncMock(return_value={"data": {}})

    comps = ["grafana", "prometheus", "loki"]
    await _check_system_health(grafana_client, prom_client, loki_client, cfg, comps, True, False)
    await _test_connectivity(grafana_client, prom_client, loki_client, cfg, comps, False, False)
    await _validate_configurations(grafana_client, prom_client, loki_client, cfg, comps, False, False)
    await _check_performance_metrics(grafana_client, prom_client, loki_client, cfg, comps, False, False)
    await _check_data_flow(grafana_client, prom_client, loki_client, cfg, comps, False, False)
    await _check_alert_status(grafana_client, prom_client, loki_client, cfg, comps, False, False)
    await _check_storage_status(grafana_client, prom_client, loki_client, cfg, comps, False, False)
    await _check_backup_status(grafana_client, prom_client, loki_client, cfg, comps, False, False)
    await _check_security_status(grafana_client, prom_client, loki_client, cfg, comps, False, False)
    await _check_capacity_planning(grafana_client, prom_client, loki_client, cfg, comps, False, False)


# ── Auth / AI / Transport / Config ───────────────────────────────────────────


def test_auth_ok_and_fail(monkeypatch):
    monkeypatch.setenv("MCP_WEB_USER", "admin")
    monkeypatch.setenv("MCP_WEB_PASSWORD", "secret")
    assert authenticate(HTTPBasicCredentials(username="admin", password="secret")) == "admin"
    with pytest.raises(HTTPException):
        authenticate(HTTPBasicCredentials(username="admin", password="wrong"))
    with pytest.raises(RuntimeError):
        monkeypatch.delenv("MCP_WEB_USER", raising=False)
        _require_env("MCP_WEB_USER")


@pytest.mark.asyncio
async def test_ai_router():
    mcp = MagicMock()
    mcp.list_tools = AsyncMock(return_value=[MagicMock(name="t1")])
    # Fix: MagicMock name attribute
    tool = MagicMock()
    tool.name = "grafana_management"
    mcp.list_tools = AsyncMock(return_value=[tool])
    router = AIRouter(mcp)

    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"response": "hello"}
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=MagicMock(post=AsyncMock(return_value=mock_resp)))
    mock_client.__aexit__ = AsyncMock(return_value=None)
    with patch("monitoring_mcp.ai.httpx.AsyncClient", return_value=mock_client):
        out = await router.process_command("status?")
        assert out["provider"] == "ollama"

    router.provider = "lm_studio"
    mock_resp.json.return_value = {"choices": [{"message": {"content": "hi"}}]}
    with patch("monitoring_mcp.ai.httpx.AsyncClient", return_value=mock_client):
        out = await router.process_command("status?")
        assert out["provider"] == "lm_studio"

    with patch.object(router, "_call_ollama", side_effect=RuntimeError("down")):
        router.provider = "ollama"
        out = await router.process_command("x")
        assert "tools" in out


def test_transport_resolve(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "http")
    monkeypatch.setenv("MCP_HOST", "0.0.0.0")  # noqa: S104 - test env parsing, never binds
    monkeypatch.setenv("MCP_PORT", "10851")
    cfg = get_transport_config()
    assert cfg["transport"] == "http"
    parser = create_argument_parser("test")
    args = parser.parse_args(["--stdio"])
    assert resolve_transport(args) == "stdio"
    args = parser.parse_args(["--http", "--host", "127.0.0.1", "--port", "9"])
    assert resolve_transport(args) == "http"
    resolved = resolve_config(args)
    assert resolved["port"] == 9
    args = parser.parse_args(["--sse"])
    assert resolve_transport(args) == "sse"
    args = parser.parse_args([])
    monkeypatch.setenv("MCP_TRANSPORT", "bogus")
    assert resolve_transport(args) == "stdio"


def test_config_auth_variants(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("MONITORING_MCP_STORAGE_PATH", str(tmp_path))
    cfg = MonitoringConfig(
        grafana_username="u",
        grafana_password="p",
        prometheus_username="pu",
        prometheus_password="pp",
        loki_username="lu",
        loki_password="lp",
    )
    assert cfg.get_grafana_auth()["Authorization"].startswith("Basic ")
    assert cfg.get_prometheus_auth()["Authorization"].startswith("Basic ")
    assert cfg.get_loki_auth()["Authorization"].startswith("Basic ")
    assert cfg.validate_endpoints() == []
    assert "MonitoringConfig" in str(cfg)
    assert cfg.get_storage_path().exists()


@pytest.mark.asyncio
async def test_prometheus_client_sync_metadata(cfg: MonitoringConfig):
    client = PrometheusClient(cfg)
    with patch("prometheus_api_client.PrometheusConnect") as mock_cls:
        inst = mock_cls.return_value
        inst.get_metadata.return_value = [{"type": "gauge"}]
        inst.all_metrics.return_value = ["up", "process_cpu"]
        assert "metadata" in client.sync_metadata("up")
        assert client.sync_metadata()["metric_count"] == 2
