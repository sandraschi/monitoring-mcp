"""Unit tests for utils, config persistence, and mocked tool clients."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from monitoring_mcp.config import MonitoringConfig
from monitoring_mcp.tools.prometheus_tool import PrometheusClient, _execute_prometheus_operation
from monitoring_mcp.utils import (
    ResponseCache,
    ensure_encryption_key,
    map_parallel,
    match_prometheus_target,
    sample_list,
    seal_payload,
    unseal_payload,
)


class TestUtils:
    def test_sample_list_below_threshold(self):
        items = list(range(10))
        out, meta = sample_list(items, enable_sampling=True, sampling_threshold=100, sampling_rate=0.1)
        assert out == items
        assert meta["sampled"] is False

    def test_sample_list_above_threshold(self):
        items = list(range(200))
        out, meta = sample_list(items, enable_sampling=True, sampling_threshold=100, sampling_rate=0.1)
        assert meta["sampled"] is True
        assert len(out) < len(items)
        assert meta["returned_count"] == len(out)

    def test_response_cache_ttl(self):
        cache = ResponseCache(ttl_seconds=60, enabled=True)
        cache.set("a", value={"ok": True})
        assert cache.get("a") == {"ok": True}
        cache.clear()
        assert cache.get("a") is None

    def test_encryption_key_persists(self, tmp_path: Path):
        key1 = ensure_encryption_key(tmp_path)
        key2 = ensure_encryption_key(tmp_path)
        assert key1 == key2
        assert (tmp_path / ".encryption_key").exists()

    def test_seal_unseal(self):
        sealed = seal_payload({"x": 1}, "secret-key")
        assert unseal_payload(sealed, "secret-key") == {"x": 1}
        with pytest.raises(ValueError):
            unseal_payload(sealed, "wrong-key")

    def test_match_prometheus_target_job_instance(self):
        target = {
            "labels": {"job": "api", "instance": "localhost:8080"},
            "scrapeUrl": "http://localhost:8080/metrics",
        }
        assert match_prometheus_target(target, "api")
        assert match_prometheus_target(target, "8080")
        assert not match_prometheus_target(target, "missing")

    def test_map_parallel_small(self):
        assert map_parallel(lambda x: x * 2, [1, 2, 3]) == [2, 4, 6]


class TestConfig:
    def test_encryption_key_on_config(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("MONITORING_MCP_STORAGE_PATH", str(tmp_path))
        cfg = MonitoringConfig()
        assert cfg.encryption_key
        assert (tmp_path / ".encryption_key").exists()

    def test_prometheus_auth_bearer(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("MONITORING_MCP_STORAGE_PATH", str(tmp_path))
        cfg = MonitoringConfig(prometheus_bearer_token="tok")
        auth = cfg.get_prometheus_auth()
        assert auth is not None
        assert auth["Authorization"] == "Bearer tok"

    def test_alertmanager_default(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("MONITORING_MCP_STORAGE_PATH", str(tmp_path))
        cfg = MonitoringConfig()
        assert "9093" in cfg.alertmanager_url


@pytest.mark.asyncio
class TestPrometheusOps:
    async def test_query_metrics_sampling(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("MONITORING_MCP_STORAGE_PATH", str(tmp_path))
        cfg = MonitoringConfig(
            enable_sampling=True,
            sampling_threshold=10,
            sampling_rate=0.5,
            enable_cache=False,
        )
        client = PrometheusClient(cfg)
        big = {
            "status": "success",
            "data": {"resultType": "vector", "result": [{"metric": {"i": str(i)}} for i in range(20)]},
        }
        client.query = AsyncMock(return_value=big)
        result = await _execute_prometheus_operation(client, "query_metrics", query="up")
        assert result["success"] is True
        assert result["sampling"]["sampled"] is True

    async def test_target_health_filter(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("MONITORING_MCP_STORAGE_PATH", str(tmp_path))
        cfg = MonitoringConfig(enable_cache=False)
        client = PrometheusClient(cfg)
        client.targets = AsyncMock(
            return_value={
                "data": {
                    "activeTargets": [
                        {"labels": {"job": "api", "instance": "a:1"}, "health": "up"},
                        {"labels": {"job": "db", "instance": "b:1"}, "health": "down"},
                    ]
                }
            }
        )
        result = await _execute_prometheus_operation(client, "get_target_health", target_name="api")
        assert result["health_summary"]["total"] == 1
        assert result["health_summary"]["up"] == 1

    async def test_get_config_flags(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("MONITORING_MCP_STORAGE_PATH", str(tmp_path))
        cfg = MonitoringConfig(enable_cache=False)
        client = PrometheusClient(cfg)
        client.status_config = AsyncMock(return_value={"data": {"yaml": "global: {}"}})
        client.status_flags = AsyncMock(return_value={"data": {"web.listen-address": "0.0.0.0:9090"}})
        cfg_result = await _execute_prometheus_operation(client, "get_config")
        flags_result = await _execute_prometheus_operation(client, "get_flags")
        assert cfg_result["success"] and flags_result["success"]


@pytest.mark.asyncio
async def test_loki_tail_fallback(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("MONITORING_MCP_STORAGE_PATH", str(tmp_path))
    from monitoring_mcp.tools.loki_tool import LokiClient

    cfg = MonitoringConfig(enable_cache=False)
    client = LokiClient(cfg)
    client.query_range = AsyncMock(
        return_value={"status": "success", "data": {"result": [{"stream": {"job": "x"}, "values": [["1", "hi"]]}]}}
    )
    with patch.dict("sys.modules", {"websockets": None}):
        # Force import error path by patching tail internals
        result = await client._tail_fallback('{job="x"}', limit=10)
    assert result["transport"] == "query_range_fallback"
    assert result["data"]["result"]


@pytest.mark.asyncio
async def test_grafana_export_panel(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("MONITORING_MCP_STORAGE_PATH", str(tmp_path))
    from monitoring_mcp.tools.grafana_tool import GrafanaClient, _execute_grafana_operation

    cfg = MonitoringConfig(enable_cache=False)
    client = GrafanaClient(cfg)
    client.get_dashboard = AsyncMock(
        return_value={
            "dashboard": {"uid": "abc", "panels": [{"id": 1, "title": "CPU"}]},
            "meta": {},
        }
    )
    client.update_dashboard = AsyncMock(return_value={"status": "success", "uid": "abc"})
    exported = await _execute_grafana_operation(client, "export_dashboard", dashboard_uid="abc")
    assert exported["success"]
    assert exported["export"]["uid"] == "abc"
    created = await _execute_grafana_operation(
        client,
        "create_panel",
        dashboard_uid="abc",
        panel_data={"title": "Mem", "type": "timeseries"},
    )
    assert created["panel_id"] == 2
