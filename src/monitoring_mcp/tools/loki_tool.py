"""
Loki Logging Portmanteau Tool

Comprehensive Loki operations including log querying, analysis,
pattern detection, and log-based troubleshooting assistance.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Literal
from urllib.parse import urlencode, urlparse, urlunparse

import httpx
from fastmcp import FastMCP

from monitoring_mcp.config import MonitoringConfig
from monitoring_mcp.utils import ResponseCache, sample_list

logger = logging.getLogger(__name__)

LOKI_OPERATIONS = {
    "query_logs": "Execute LogQL queries with intelligent sampling",
    "query_range": "Execute range queries for temporal log analysis",
    "tail_logs": "Stream live logs via Loki WebSocket tail API",
    "analyze_logs": "AI-powered log analysis and pattern detection",
    "detect_anomalies": "Identify unusual log patterns and errors",
    "search_errors": "Find error messages and exceptions in logs",
    "trace_requests": "Follow request traces through log streams",
    "get_labels": "List available log labels and their values",
    "get_label_values": "Get values for specific log labels",
    "get_series": "Get series information for log streams",
    "create_alert_rule": "Create log-based alerting rules (Loki ruler)",
    "list_alerts": "List Loki ruler rules / alerting groups",
    "optimize_queries": "Suggest LogQL query optimizations",
    "export_logs": "Export logs in various formats for analysis",
    "compare_timeframes": "Compare log patterns between time periods",
    "generate_report": "Generate comprehensive log analysis reports",
}


class LokiClient:
    """Loki API client with auth, cache, and WebSocket tail."""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.base_url = config.loki_url.rstrip("/")
        self.timeout = config.request_timeout
        self.auth_headers = config.get_loki_auth() or {}
        self.cache = ResponseCache(
            ttl_seconds=config.cache_ttl_seconds,
            enabled=config.enable_cache,
        )

    async def _make_request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        *,
        method: str = "GET",
        json_body: dict[str, Any] | None = None,
        use_cache: bool = False,
    ) -> dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        cache_key = ("loki", method, endpoint, params, json_body)
        if use_cache and method == "GET":
            cached = self.cache.get(*cache_key)
            if cached is not None:
                return cached

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method,
                url,
                params=params,
                json=json_body,
                headers=self.auth_headers,
            )
            if response.status_code >= 400:
                error_msg = f"Loki API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise httpx.HTTPStatusError(error_msg, request=response.request, response=response)
            data = response.json()
            if use_cache and method == "GET":
                self.cache.set(*cache_key, value=data)
            return data

    async def query(
        self, query: str, limit: int = 100, time: str | None = None, direction: str = "backward"
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"query": query, "limit": limit, "direction": direction}
        if time:
            params["time"] = time
        return await self._make_request("loki/api/v1/query", params)

    async def query_range(
        self,
        query: str,
        start: str,
        end: str,
        limit: int = 1000,
        step: str = "1m",
        direction: str = "backward",
    ) -> dict[str, Any]:
        return await self._make_request(
            "loki/api/v1/query_range",
            {
                "query": query,
                "start": start,
                "end": end,
                "limit": limit,
                "step": step,
                "direction": direction,
            },
        )

    async def tail(
        self,
        query: str,
        *,
        limit: int = 100,
        duration_seconds: float = 5.0,
        delay_for: int = 0,
    ) -> dict[str, Any]:
        """
        Tail Loki via WebSocket ``/loki/api/v1/tail``.

        Falls back to a short query_range window if websockets is unavailable
        or the connection fails.
        """
        try:
            import websockets
            from websockets.exceptions import ConnectionClosed
        except ImportError:
            return await self._tail_fallback(query, limit=limit)

        parsed = urlparse(self.base_url)
        ws_scheme = "wss" if parsed.scheme == "https" else "ws"
        qs = urlencode({"query": query, "delay_for": delay_for, "limit": limit})
        ws_url = urlunparse((ws_scheme, parsed.netloc, "/loki/api/v1/tail", "", qs, ""))

        streams: dict[str, dict[str, Any]] = {}
        entries: list[dict[str, Any]] = []

        try:
            extra_headers = dict(self.auth_headers)
            async with websockets.connect(
                ws_url,
                additional_headers=extra_headers or None,
                open_timeout=self.timeout,
                close_timeout=5,
            ) as ws:
                deadline = asyncio.get_event_loop().time() + duration_seconds
                while asyncio.get_event_loop().time() < deadline and len(entries) < limit:
                    remaining = deadline - asyncio.get_event_loop().time()
                    if remaining <= 0:
                        break
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=min(remaining, 2.0))
                    except TimeoutError:
                        continue
                    except ConnectionClosed:
                        break
                    msg = json.loads(raw) if isinstance(raw, str) else json.loads(raw.decode())
                    for stream in msg.get("streams", []) or []:
                        labels = stream.get("stream") or {}
                        key = json.dumps(labels, sort_keys=True)
                        bucket = streams.setdefault(key, {"stream": labels, "values": []})
                        for value in stream.get("values", []) or []:
                            bucket["values"].append(value)
                            entries.append({"stream": labels, "value": value})
                            if len(entries) >= limit:
                                break
            return {
                "status": "success",
                "data": {"resultType": "streams", "result": list(streams.values())},
                "transport": "websocket",
            }
        except Exception as exc:
            logger.warning("Loki WebSocket tail failed (%s); falling back to query_range", exc)
            fallback = await self._tail_fallback(query, limit=limit)
            fallback["websocket_error"] = str(exc)
            return fallback

    async def _tail_fallback(self, query: str, *, limit: int = 100) -> dict[str, Any]:
        result = await self.query_range(query, "now-2m", "now", limit=limit, step="1s")
        result["transport"] = "query_range_fallback"
        result["note"] = "WebSocket tail unavailable; returned last 2 minutes via query_range"
        return result

    async def labels(self) -> dict[str, Any]:
        return await self._make_request("loki/api/v1/labels", use_cache=True)

    async def label_values(self, label: str) -> dict[str, Any]:
        return await self._make_request(f"loki/api/v1/label/{label}/values", use_cache=True)

    async def series(self, match: list[str], start: str | None = None, end: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = [("match[]", m) for m in match]
        if start:
            params.append(("start", start))
        if end:
            params.append(("end", end))
        # httpx accepts list of tuples for repeated keys
        url = f"{self.base_url}/loki/api/v1/series"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params, headers=self.auth_headers)
            if response.status_code >= 400:
                error_msg = f"Loki API error {response.status_code}: {response.text}"
                raise httpx.HTTPStatusError(error_msg, request=response.request, response=response)
            return response.json()

    async def ruler_rules(self) -> dict[str, Any]:
        return await self._make_request("loki/api/v1/rules")

    async def create_ruler_rule(self, namespace: str, group_yaml_or_json: dict[str, Any] | str) -> dict[str, Any]:
        """POST rule group to Loki ruler. Accepts JSON group or raw YAML string."""
        if isinstance(group_yaml_or_json, str):
            url = f"{self.base_url}/loki/api/v1/rules/{namespace}"
            headers = {**self.auth_headers, "Content-Type": "application/yaml"}
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, content=group_yaml_or_json, headers=headers)
                if response.status_code >= 400:
                    raise httpx.HTTPStatusError(
                        f"Loki ruler error {response.status_code}: {response.text}",
                        request=response.request,
                        response=response,
                    )
                return {"status": "ok", "namespace": namespace, "response": response.text}
        return await self._make_request(
            f"loki/api/v1/rules/{namespace}",
            method="POST",
            json_body=group_yaml_or_json,
        )


def register_loki_tool(
    mcp: FastMCP,
    _storage: object,
    config: MonitoringConfig,
) -> None:
    """Register the Loki portmanteau tool with the MCP server."""

    client = LokiClient(config)

    @mcp.tool()
    async def loki_logging(
        operation: Literal[
            "query_logs",
            "query_range",
            "tail_logs",
            "analyze_logs",
            "detect_anomalies",
            "search_errors",
            "trace_requests",
            "get_labels",
            "get_label_values",
            "get_series",
            "create_alert_rule",
            "list_alerts",
            "optimize_queries",
            "export_logs",
            "compare_timeframes",
            "generate_report",
        ],
        query: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: int | None = None,
        label_name: str | None = None,
        match_patterns: list[str] | None = None,
        analysis_context: dict[str, Any] | None = None,
        alert_rule: dict[str, Any] | str | None = None,
        rule_namespace: str | None = None,
        export_format: str | None = None,
        compare_start: str | None = None,
        compare_end: str | None = None,
        tail_duration_seconds: float | None = None,
    ) -> dict[str, Any]:
        """Comprehensive Loki logging portmanteau tool."""
        try:
            if operation not in LOKI_OPERATIONS:
                return {
                    "success": False,
                    "error": f"Invalid operation '{operation}'. Available: {list(LOKI_OPERATIONS.keys())}",
                    "conversational_summary": f"I don't recognize the '{operation}' operation.",
                    "available_operations": list(LOKI_OPERATIONS.keys()),
                }

            result = await _execute_loki_operation(
                client,
                operation,
                query=query,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
                label_name=label_name,
                match_patterns=match_patterns,
                analysis_context=analysis_context,
                alert_rule=alert_rule,
                rule_namespace=rule_namespace,
                export_format=export_format,
                compare_start=compare_start,
                compare_end=compare_end,
                tail_duration_seconds=tail_duration_seconds,
            )
            result["conversational_summary"] = _generate_loki_summary(operation, result)
            if operation in ["query_logs", "search_errors", "detect_anomalies"]:
                result["ai_insights"] = _generate_loki_insights(operation, result)
            return result
        except Exception as e:
            logger.error("Error in Loki operation '%s': %s", operation, e, exc_info=True)
            return {
                "success": False,
                "error": f"Failed to execute Loki operation '{operation}': {e!s}",
                "conversational_summary": f"Error during {operation.replace('_', ' ')}. Check Loki URL and auth.",
            }


async def _execute_loki_operation(
    client: LokiClient,
    operation: str,
    *,
    query: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    limit: int | None = None,
    label_name: str | None = None,
    match_patterns: list[str] | None = None,
    analysis_context: dict[str, Any] | None = None,
    alert_rule: dict[str, Any] | str | None = None,
    rule_namespace: str | None = None,
    export_format: str | None = None,
    compare_start: str | None = None,
    compare_end: str | None = None,
    tail_duration_seconds: float | None = None,
) -> dict[str, Any]:
    cfg = client.config
    limit = min(limit or 100, cfg.max_results_limit)

    if operation == "query_logs":
        if not query:
            raise ValueError("query is required for query_logs")
        result = await client.query(query, limit=limit)
        streams = result.get("data", {}).get("result", [])
        sampled, sample_meta = sample_list(
            streams,
            enable_sampling=cfg.enable_sampling,
            sampling_threshold=cfg.sampling_threshold,
            sampling_rate=cfg.sampling_rate,
        )
        if sample_meta["sampled"]:
            result = {**result, "data": {**result.get("data", {}), "result": sampled}}
        total_entries = sum(len(s.get("values", [])) for s in sampled)
        return {
            "success": True,
            "operation": "query_logs",
            "data": result,
            "query": query,
            "stream_count": len(sampled),
            "total_entries": total_entries,
            "sampling": sample_meta,
        }

    if operation == "query_range":
        if not query or not start_time or not end_time:
            raise ValueError("query, start_time, and end_time are required for query_range")
        result = await client.query_range(query, start_time, end_time, limit=limit)
        streams = result.get("data", {}).get("result", [])
        total_entries = sum(len(s.get("values", [])) for s in streams)
        return {
            "success": True,
            "operation": "query_range",
            "data": result,
            "query": query,
            "time_range": {"start": start_time, "end": end_time},
            "stream_count": len(streams),
            "total_entries": total_entries,
        }

    if operation == "tail_logs":
        if not query:
            raise ValueError("query is required for tail_logs")
        result = await client.tail(
            query,
            limit=min(limit, 50),
            duration_seconds=tail_duration_seconds or 5.0,
        )
        streams = result.get("data", {}).get("result", [])
        total_entries = sum(len(s.get("values", [])) for s in streams)
        return {
            "success": True,
            "operation": "tail_logs",
            "data": result,
            "query": query,
            "stream_count": len(streams),
            "total_entries": total_entries,
            "transport": result.get("transport"),
            "note": result.get("note") or "WebSocket tail completed",
        }

    if operation == "get_labels":
        result = await client.labels()
        labels = result.get("data", [])
        return {
            "success": True,
            "operation": "get_labels",
            "data": result,
            "label_count": len(labels),
            "labels": labels,
        }

    if operation == "get_label_values":
        if not label_name:
            raise ValueError("label_name is required for get_label_values")
        result = await client.label_values(label_name)
        values = result.get("data", [])
        return {
            "success": True,
            "operation": "get_label_values",
            "data": result,
            "label": label_name,
            "value_count": len(values),
        }

    if operation == "get_series":
        if not match_patterns:
            raise ValueError("match_patterns is required for get_series")
        result = await client.series(match_patterns, start_time, end_time)
        series = result.get("data", [])
        return {"success": True, "operation": "get_series", "data": result, "series_count": len(series)}

    if operation in ["analyze_logs", "detect_anomalies", "search_errors"]:
        if not query:
            raise ValueError(f"query is required for {operation}")
        result = await client.query_range(query, start_time or "now-1h", end_time or "now", limit=min(limit, 1000))
        if operation == "analyze_logs":
            analysis = _analyze_log_patterns(result, analysis_context or {})
        elif operation == "detect_anomalies":
            analysis = _detect_log_anomalies(result, analysis_context or {})
        else:
            analysis = _search_error_patterns(result, analysis_context or {})
        return {
            "success": True,
            "operation": operation,
            "data": result,
            "analysis": analysis,
            "query": query,
        }

    if operation == "trace_requests":
        if not query:
            raise ValueError("query is required for trace_requests")
        trace_query = f'{query} |~ "(?i)request.?id|trace.?id|correlation.?id|x-request-id"'
        result = await client.query_range(trace_query, start_time or "now-1h", end_time or "now", limit=min(limit, 500))
        return {
            "success": True,
            "operation": "trace_requests",
            "data": result,
            "analysis": _analyze_request_traces(result),
            "query": trace_query,
        }

    if operation == "list_alerts":
        try:
            rules = await client.ruler_rules()
            return {"success": True, "operation": "list_alerts", "data": rules}
        except Exception as exc:
            return {
                "success": False,
                "operation": "list_alerts",
                "error": str(exc),
                "note": "Loki ruler API may be disabled; enable ruler or use Grafana alerting",
            }

    if operation == "create_alert_rule":
        if not alert_rule:
            raise ValueError("alert_rule is required (ruler group JSON/YAML)")
        namespace = rule_namespace or "monitoring-mcp"
        created = await client.create_ruler_rule(namespace, alert_rule)
        return {"success": True, "operation": "create_alert_rule", "data": created, "namespace": namespace}

    if operation == "optimize_queries":
        if not query:
            raise ValueError("query is required for optimize_queries")
        return {
            "success": True,
            "operation": "optimize_queries",
            "query": query,
            "optimizations": _optimize_logql(query),
        }

    if operation == "export_logs":
        if not query:
            raise ValueError("query is required for export_logs")
        result = await client.query_range(
            query, start_time or "now-1h", end_time or "now", limit=min(limit, cfg.max_results_limit)
        )
        fmt = (export_format or "json").lower()
        exported = _export_logs(result, fmt)
        return {
            "success": True,
            "operation": "export_logs",
            "format": fmt,
            "export": exported,
            "entry_count": exported.get("entry_count", 0),
        }

    if operation == "compare_timeframes":
        if not query:
            raise ValueError("query is required for compare_timeframes")
        primary = await client.query_range(query, start_time or "now-1h", end_time or "now", limit=min(limit, 500))
        secondary = await client.query_range(
            query,
            compare_start or "now-2h",
            compare_end or "now-1h",
            limit=min(limit, 500),
        )
        return {
            "success": True,
            "operation": "compare_timeframes",
            "comparison": _compare_timeframes(primary, secondary),
            "primary_range": {"start": start_time or "now-1h", "end": end_time or "now"},
            "compare_range": {"start": compare_start or "now-2h", "end": compare_end or "now-1h"},
        }

    if operation == "generate_report":
        if not query:
            raise ValueError("query is required for generate_report")
        result = await client.query_range(query, start_time or "now-1h", end_time or "now", limit=min(limit, 1000))
        patterns = _analyze_log_patterns(result, analysis_context or {})
        anomalies = _detect_log_anomalies(result, analysis_context or {})
        errors = _search_error_patterns(result, analysis_context or {})
        return {
            "success": True,
            "operation": "generate_report",
            "report": {
                "query": query,
                "time_range": {"start": start_time or "now-1h", "end": end_time or "now"},
                "patterns": patterns,
                "anomalies": anomalies,
                "errors": errors,
                "summary": (
                    f"Report: {errors.get('error_count', 0)} errors, "
                    f"{len(anomalies.get('anomalies', []))} anomalies, "
                    f"{len(patterns.get('patterns', []))} patterns."
                ),
            },
        }

    raise ValueError(f"Unsupported operation: {operation}")


def _optimize_logql(query: str) -> list[dict[str, str]]:
    tips: list[dict[str, str]] = []
    if "{}" in query or query.strip() == "{}":
        tips.append(
            {
                "type": "unbounded_selector",
                "description": "Empty stream selector scans all streams",
                "suggestion": 'Add label matchers e.g. {job="api"}',
            }
        )
    if "|=" in query and "|~" in query:
        tips.append(
            {
                "type": "filter_order",
                "description": "Prefer line filters before parsers",
                "suggestion": "Put |= / |~ filters early to reduce volume",
            }
        )
    if "json" in query and "|=" not in query and "|~" not in query:
        tips.append(
            {
                "type": "parse_without_filter",
                "description": "Parsing all lines is expensive",
                "suggestion": "Filter with |= before | json",
            }
        )
    if not tips:
        tips.append({"type": "ok", "description": "Query looks reasonable", "suggestion": "No changes needed"})
    return tips


def _export_logs(log_data: dict[str, Any], fmt: str) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for stream in log_data.get("data", {}).get("result", []):
        labels = stream.get("stream", {})
        for ts, line in stream.get("values", []):
            rows.append({"timestamp": ts, "line": line, "labels": labels})
    if fmt == "csv":
        lines = ["timestamp,line,labels"]
        for row in rows:
            safe_line = row["line"].replace('"', '""')
            lines.append(f'{row["timestamp"]},"{safe_line}","{json.dumps(row["labels"])}"')
        return {"entry_count": len(rows), "csv": "\n".join(lines)}
    if fmt == "text":
        text = "\n".join(f"{r['timestamp']} {r['line']}" for r in rows)
        return {"entry_count": len(rows), "text": text}
    return {"entry_count": len(rows), "json": rows}


def _compare_timeframes(primary: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
    def count_entries(data: dict[str, Any]) -> int:
        return sum(len(s.get("values", [])) for s in data.get("data", {}).get("result", []))

    p = count_entries(primary)
    s = count_entries(secondary)
    delta = p - s
    pct = (delta / s * 100) if s else (100.0 if p else 0.0)
    return {
        "primary_entries": p,
        "compare_entries": s,
        "delta": delta,
        "percent_change": round(pct, 2),
        "interpretation": "volume_up" if delta > 0 else "volume_down" if delta < 0 else "stable",
    }


def _generate_loki_summary(operation: str, result: dict[str, Any]) -> str:
    if not result.get("success"):
        return f"I wasn't able to complete the {operation.replace('_', ' ')} operation. {result.get('error', '')}"
    if operation in ["query_logs", "query_range"]:
        return f"Found {result.get('total_entries', 0)} log entries across {result.get('stream_count', 0)} streams."
    if operation == "tail_logs":
        return f"Tailed {result.get('total_entries', 0)} entries via {result.get('transport', 'unknown')}."
    if operation == "generate_report":
        return (result.get("report") or {}).get("summary", "Report generated.")
    return f"The {operation.replace('_', ' ')} operation completed successfully."


def _generate_loki_insights(operation: str, result: dict[str, Any]) -> dict[str, Any]:
    insights: dict[str, list[str]] = {
        "recommendations": [],
        "alerting_opportunities": [],
        "optimization_suggestions": [],
    }
    if operation == "query_logs" and result.get("total_entries", 0) > 5000:
        insights["optimization_suggestions"].append("Narrow label selectors for better performance")
    if operation == "search_errors" and (result.get("analysis") or {}).get("error_count", 0) > 10:
        insights["alerting_opportunities"].append("Set up alerts for recurring error patterns")
    return insights


def _analyze_log_patterns(log_data: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
    streams = log_data.get("data", {}).get("result", [])
    all_messages = [msg for stream in streams for _, msg in stream.get("values", [])]
    analysis: dict[str, Any] = {"patterns": [], "frequency_analysis": {}, "summary": "Log pattern analysis completed."}
    error_patterns = ["ERROR", "Exception", "Failed", "Timeout", "Connection refused"]
    error_count = sum(1 for msg in all_messages if any(p.lower() in msg.lower() for p in error_patterns))
    if error_count:
        analysis["patterns"].append(
            {"type": "errors", "count": error_count, "description": f"{error_count} error-like messages"}
        )
    if analysis["patterns"]:
        analysis["summary"] = f"Identified {len(analysis['patterns'])} log patterns."
    else:
        analysis["summary"] = "No specific patterns detected."
    return analysis


def _detect_log_anomalies(log_data: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
    streams = log_data.get("data", {}).get("result", [])
    all_messages = [msg for stream in streams for _, msg in stream.get("values", [])]
    analysis: dict[str, Any] = {"anomalies": [], "severity_score": 0, "summary": "Anomaly detection completed."}
    error_messages = [m for m in all_messages if "ERROR" in m.upper() or "Exception" in m]
    if all_messages and len(error_messages) > len(all_messages) * 0.1:
        analysis["anomalies"].append(
            {
                "type": "high_error_rate",
                "severity": "high",
                "description": f"High error rate: {len(error_messages)}/{len(all_messages)}",
            }
        )
        analysis["severity_score"] += 3
    if not analysis["anomalies"]:
        analysis["summary"] = "No significant anomalies detected."
    else:
        analysis["summary"] = f"Detected {len(analysis['anomalies'])} anomalies."
    return analysis


def _search_error_patterns(log_data: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
    streams = log_data.get("data", {}).get("result", [])
    analysis: dict[str, Any] = {
        "error_count": 0,
        "error_types": {},
        "error_samples": [],
        "summary": "Error search completed.",
    }
    keywords = ["ERROR", "Exception", "Failed", "Timeout", "Connection refused", "500", "502", "503"]
    for stream in streams:
        for timestamp, message in stream.get("values", []):
            if any(k.lower() in message.lower() for k in keywords):
                analysis["error_count"] += 1
                if len(analysis["error_samples"]) < 5:
                    analysis["error_samples"].append(
                        {"timestamp": timestamp, "message": message[:200], "stream_labels": stream.get("stream", {})}
                    )
    analysis["summary"] = (
        f"Found {analysis['error_count']} error messages." if analysis["error_count"] else "No error messages found."
    )
    return analysis


def _analyze_request_traces(log_data: dict[str, Any]) -> dict[str, Any]:
    import re

    streams = log_data.get("data", {}).get("result", [])
    analysis: dict[str, Any] = {
        "request_traces": [],
        "trace_count": 0,
        "correlation_ids": set(),
        "summary": "Request trace analysis completed.",
    }
    patterns = [
        r"request.?id[:=]\s*([a-f0-9\-]+)",
        r"trace.?id[:=]\s*([a-f0-9\-]+)",
        r"correlation.?id[:=]\s*([a-f0-9\-]+)",
        r"x-request-id[:=]\s*([a-f0-9\-]+)",
    ]
    for stream in streams:
        trace_entries = []
        for timestamp, message in stream.get("values", []):
            for pattern in patterns:
                matches = re.findall(pattern, message, re.IGNORECASE)
                if matches:
                    analysis["correlation_ids"].update(matches)
                    trace_entries.append({"timestamp": timestamp, "message": message, "correlation_ids": matches})
        if trace_entries:
            analysis["request_traces"].append(
                {"stream_labels": stream.get("stream", {}), "entries": trace_entries, "entry_count": len(trace_entries)}
            )
    analysis["trace_count"] = len(analysis["request_traces"])
    analysis["unique_correlation_ids"] = len(analysis["correlation_ids"])
    analysis["correlation_ids"] = list(analysis["correlation_ids"])
    analysis["summary"] = (
        f"Found {analysis['trace_count']} traces with {analysis['unique_correlation_ids']} correlation IDs."
        if analysis["trace_count"]
        else "No request traces found."
    )
    return analysis
