"""
Loki Logging Portmanteau Tool

Comprehensive Loki operations including log querying, analysis,
pattern detection, and log-based troubleshooting assistance.

PORTMANTEAU PATTERN: Consolidates all Loki operations into a single tool
to avoid tool explosion while maintaining full functionality.
"""

import logging
from typing import Any, Literal

import httpx
from fastmcp import FastMCP
from py_key_value_aio import AbstractStore

from monitoring_mcp.config import MonitoringConfig

logger = logging.getLogger(__name__)

# Loki operations supported by this portmanteau tool
LOKI_OPERATIONS = {
    "query_logs": "Execute LogQL queries with intelligent sampling",
    "query_range": "Execute range queries for temporal log analysis",
    "tail_logs": "Stream live logs in real-time (limited duration)",
    "analyze_logs": "AI-powered log analysis and pattern detection",
    "detect_anomalies": "Identify unusual log patterns and errors",
    "search_errors": "Find error messages and exceptions in logs",
    "trace_requests": "Follow request traces through log streams",
    "get_labels": "List available log labels and their values",
    "get_label_values": "Get values for specific log labels",
    "get_series": "Get series information for log streams",
    "create_alert_rule": "Create log-based alerting rules",
    "list_alerts": "List active log-based alerts",
    "optimize_queries": "Suggest LogQL query optimizations",
    "export_logs": "Export logs in various formats for analysis",
    "compare_timeframes": "Compare log patterns between time periods",
    "generate_report": "Generate comprehensive log analysis reports",
}


class LokiClient:
    """Loki API client with authentication and error handling."""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.base_url = config.loki_url.rstrip("/")
        self.timeout = config.request_timeout

    async def _make_request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make request to Loki API."""
        url = f"{self.base_url}/{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)

            if response.status_code >= 400:
                error_msg = f"Loki API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise httpx.HTTPStatusError(error_msg, request=response.request, response=response)

            return response.json()

    async def query(
        self, query: str, limit: int = 100, time: str | None = None, direction: str = "backward"
    ) -> dict[str, Any]:
        """Execute instant log query."""
        params = {
            "query": query,
            "limit": limit,
            "direction": direction,
        }
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
        """Execute range log query."""
        params = {
            "query": query,
            "start": start,
            "end": end,
            "limit": limit,
            "step": step,
            "direction": direction,
        }
        return await self._make_request("loki/api/v1/query_range", params)

    async def tail(self, query: str, delay_for: int = 0, limit: int = 100) -> dict[str, Any]:
        """Tail logs (limited implementation)."""
        params = {
            "query": query,
            "delay_for": delay_for,
            "limit": limit,
        }
        return await self._make_request("loki/api/v1/tail", params)

    async def labels(self) -> dict[str, Any]:
        """Get all available labels."""
        return await self._make_request("loki/api/v1/labels")

    async def label_values(self, label: str) -> dict[str, Any]:
        """Get values for a specific label."""
        return await self._make_request(f"loki/api/v1/label/{label}/values")

    async def series(
        self, match: list[str], start: str | None = None, end: str | None = None
    ) -> dict[str, Any]:
        """Get series information."""
        params = {"match": match}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return await self._make_request("loki/api/v1/series", params)


async def register_loki_tool(
    mcp: FastMCP,
    _storage: AbstractStore,
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
        export_format: str | None = None,
        comparison_periods: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Comprehensive Loki logging portmanteau tool leveraging FastMCP 2.14.3.

        PORTMANTEAU PATTERN: Consolidates 16 Loki operations into a single tool
        to prevent tool explosion while maintaining comprehensive functionality.

        Provides intelligent LogQL assistance, pattern recognition, and conversational
        insights for log analysis and troubleshooting.

        Args:
            operation: The Loki operation to perform
            query: LogQL query string for log operations
            start_time: Start time for range queries (RFC3339 or unix timestamp)
            end_time: End time for range queries (RFC3339 or unix timestamp)
            limit: Maximum number of log entries to return
            label_name: Label name for label operations
            match_patterns: Stream selectors for series operations
            analysis_context: Additional context for AI analysis operations
            export_format: Format for log export operations
            comparison_periods: Time periods for comparison operations

        Returns:
            Dict containing operation results with conversational summary and insights
        """
        try:
            if operation not in LOKI_OPERATIONS:
                return {
                    "success": False,
                    "error": f"Invalid operation '{operation}'. Available: {list(LOKI_OPERATIONS.keys())}",
                    "conversational_summary": f"I don't recognize the '{operation}' operation. Here are the available Loki operations I can help with.",
                    "available_operations": list(LOKI_OPERATIONS.keys()),
                }

            logger.info(f"Executing Loki operation: {operation}")

            # Execute the requested operation
            result = await _execute_loki_operation(
                client,
                operation,
                query,
                start_time,
                end_time,
                limit,
                label_name,
                match_patterns,
                analysis_context,
                export_format,
                comparison_periods,
            )

            # Add conversational insights
            result["conversational_summary"] = _generate_loki_summary(operation, result)

            # Add AI-powered recommendations where appropriate
            if operation in [
                "query_logs",
                "query_range",
                "analyze_logs",
                "detect_anomalies",
                "search_errors",
            ]:
                result["ai_insights"] = _generate_loki_insights(operation, result)

            return result

        except Exception as e:
            logger.error(f"Error in Loki operation '{operation}': {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to execute Loki operation '{operation}': {e!s}",
                "conversational_summary": f"I encountered an error while trying to {operation.replace('_', ' ')}. This might be due to connectivity issues with Loki or invalid LogQL syntax. Please check your Loki configuration and try again.",
                "troubleshooting_tips": [
                    "Verify Loki is running and accessible",
                    "Check LogQL query syntax (it can be complex)",
                    "Ensure time ranges are valid",
                    "Validate label names exist in your logs",
                ],
            }


async def _execute_loki_operation(
    client: LokiClient,
    operation: str,
    query: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    limit: int | None = None,
    label_name: str | None = None,
    match_patterns: list[str] | None = None,
    analysis_context: dict[str, Any] | None = None,
    export_format: str | None = None,  # noqa: ARG001
    comparison_periods: dict[str, Any] | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """Execute the specific Loki operation."""

    limit = limit or 100

    if operation == "query_logs":
        if not query:
            raise ValueError("query is required for query_logs")
        result = await client.query(query, limit=limit)
        streams = result.get("data", {}).get("result", [])
        total_entries = sum(len(stream.get("values", [])) for stream in streams)

        return {
            "success": True,
            "operation": "query_logs",
            "data": result,
            "query": query,
            "stream_count": len(streams),
            "total_entries": total_entries,
        }

    elif operation == "query_range":
        if not query or not start_time or not end_time:
            raise ValueError("query, start_time, and end_time are required for query_range")
        result = await client.query_range(query, start_time, end_time, limit=limit)
        streams = result.get("data", {}).get("result", [])
        total_entries = sum(len(stream.get("values", [])) for stream in streams)

        return {
            "success": True,
            "operation": "query_range",
            "data": result,
            "query": query,
            "time_range": {"start": start_time, "end": end_time},
            "stream_count": len(streams),
            "total_entries": total_entries,
        }

    elif operation == "tail_logs":
        if not query:
            raise ValueError("query is required for tail_logs")
        # Limit tail duration for safety
        result = await client.tail(query, limit=min(limit, 50))
        streams = result.get("data", {}).get("result", [])
        total_entries = sum(len(stream.get("values", [])) for stream in streams)

        return {
            "success": True,
            "operation": "tail_logs",
            "data": result,
            "query": query,
            "stream_count": len(streams),
            "total_entries": total_entries,
            "note": "Tail operation limited to prevent excessive resource usage",
        }

    elif operation == "get_labels":
        result = await client.labels()
        labels = result.get("data", [])
        return {
            "success": True,
            "operation": "get_labels",
            "data": result,
            "label_count": len(labels),
            "labels": labels,
        }

    elif operation == "get_label_values":
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
            "values": values[:50],  # Limit for performance
        }

    elif operation == "get_series":
        if not match_patterns:
            raise ValueError("match_patterns is required for get_series")
        result = await client.series(match_patterns, start_time, end_time)
        series = result.get("data", [])
        return {
            "success": True,
            "operation": "get_series",
            "data": result,
            "match_patterns": match_patterns,
            "series_count": len(series),
        }

    elif operation in ["analyze_logs", "detect_anomalies", "search_errors"]:
        if not query:
            raise ValueError(f"query is required for {operation}")

        # Get logs first
        result = await client.query_range(
            query, start_time or "now-1h", end_time or "now", limit=min(limit or 1000, 1000)
        )

        # Analyze based on operation type
        if operation == "analyze_logs":
            analysis = _analyze_log_patterns(result, analysis_context or {})
        elif operation == "detect_anomalies":
            analysis = _detect_log_anomalies(result, analysis_context or {})
        elif operation == "search_errors":
            analysis = _search_error_patterns(result, analysis_context or {})

        return {
            "success": True,
            "operation": operation,
            "data": result,
            "analysis": analysis,
            "query": query,
        }

    elif operation == "trace_requests":
        if not query:
            raise ValueError("query is required for trace_requests")
        # Look for request IDs or correlation IDs in logs
        trace_query = f'{query} |~ "request.*id|trace.*id|correlation.*id"'
        result = await client.query_range(
            trace_query, start_time or "now-1h", end_time or "now", limit=min(limit or 500, 500)
        )

        trace_analysis = _analyze_request_traces(result)

        return {
            "success": True,
            "operation": "trace_requests",
            "data": result,
            "analysis": trace_analysis,
            "query": trace_query,
        }

    # Placeholder implementations for operations not yet implemented
    elif operation in [
        "create_alert_rule",
        "list_alerts",
        "optimize_queries",
        "export_logs",
        "compare_timeframes",
        "generate_report",
    ]:
        return {
            "success": False,
            "operation": operation,
            "error": f"Operation '{operation}' is not yet implemented",
            "note": "This operation is planned for a future version",
        }

    else:
        raise ValueError(f"Unsupported operation: {operation}")


def _generate_loki_summary(operation: str, result: dict[str, Any]) -> str:
    """Generate conversational summary for Loki operation results."""
    if not result.get("success"):
        return f"I wasn't able to complete the {operation.replace('_', ' ')} operation. {result.get('error', 'Unknown error occurred')}."

    if operation in ["query_logs", "query_range"]:
        streams = result.get("stream_count", 0)
        entries = result.get("total_entries", 0)
        time_info = ""
        if operation == "query_range":
            time_range = result.get("time_range", {})
            time_info = (
                f" from {time_range.get('start', 'unknown')} to {time_range.get('end', 'unknown')}"
            )

        if entries == 0:
            return f"I searched your logs{time_info} but didn't find any entries matching your query. You might want to check your LogQL syntax or expand your time range."
        elif entries == 1:
            return f"I found 1 log entry across {streams} stream{'s' if streams != 1 else ''}{time_info}. Here's the result:"
        else:
            return f"I found {entries} log entries across {streams} stream{'s' if streams != 1 else ''}{time_info}. Here's a sampling of the results:"

    elif operation == "tail_logs":
        entries = result.get("total_entries", 0)
        return f"I tailed your logs and captured {entries} recent entries. This gives you a live view of what's happening right now."

    elif operation == "get_labels":
        count = result.get("label_count", 0)
        return f"I found {count} label{'s' if count != 1 else ''} available in your Loki instance. Labels help you filter and organize your logs."

    elif operation == "get_label_values":
        count = result.get("value_count", 0)
        label = result.get("label", "unknown")
        return f"For the '{label}' label, I found {count} unique value{'s' if count != 1 else ''}. This helps you understand the scope of your labeled data."

    elif operation == "get_series":
        count = result.get("series_count", 0)
        return f"I found {count} log series matching your patterns. Each series represents a unique combination of label values."

    elif operation == "analyze_logs":
        analysis = result.get("analysis", {})
        patterns = len(analysis.get("patterns", []))
        return f"I analyzed your logs and identified {patterns} distinct pattern{'s' if patterns != 1 else ''}. {analysis.get('summary', 'Review the detailed analysis for insights.')}"

    elif operation == "detect_anomalies":
        analysis = result.get("analysis", {})
        anomalies = len(analysis.get("anomalies", []))
        return f"I scanned your logs for anomalies and found {anomalies} potential issue{'s' if anomalies != 1 else ''}. {analysis.get('summary', 'Review the detailed analysis for specific concerns.')}"

    elif operation == "search_errors":
        analysis = result.get("analysis", {})
        errors = analysis.get("error_count", 0)
        if errors == 0:
            return "Great news! I didn't find any error messages in the logs for your search criteria. Your systems appear to be running smoothly."
        else:
            return f"I found {errors} error message{'s' if errors != 1 else ''} in your logs. Here's what I discovered:"

    elif operation == "trace_requests":
        analysis = result.get("analysis", {})
        traces = len(analysis.get("request_traces", []))
        return f"I traced request flows through your logs and found {traces} request trace{'s' if traces != 1 else ''}. This helps you understand how requests flow through your system."

    else:
        return f"The {operation.replace('_', ' ')} operation completed successfully."


def _generate_loki_insights(operation: str, result: dict[str, Any]) -> dict[str, Any]:
    """Generate AI-powered insights for Loki operations."""
    insights = {"recommendations": [], "alerting_opportunities": [], "optimization_suggestions": []}

    if operation == "query_logs":
        entries = result.get("total_entries", 0)
        if entries > 5000:
            insights["optimization_suggestions"].append(
                "Consider narrowing your query with more specific label selectors for better performance"
            )
        elif entries == 0:
            insights["optimization_suggestions"].append(
                "Try broadening your time range or checking label names in your query"
            )

    elif operation == "search_errors":
        analysis = result.get("analysis", {})
        error_count = analysis.get("error_count", 0)
        if error_count > 10:
            insights["alerting_opportunities"].append(
                f"Consider setting up alerts for the {error_count} errors found in this search"
            )

    elif operation == "detect_anomalies":
        analysis = result.get("analysis", {})
        anomalies = analysis.get("anomalies", [])
        if anomalies:
            insights["recommendations"].append(
                f"Review {len(anomalies)} anomalous log patterns for potential issues"
            )

    return insights


def _analyze_log_patterns(log_data: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
    """Analyze log patterns for common themes and structures."""
    streams = log_data.get("data", {}).get("result", [])

    analysis = {
        "patterns": [],
        "frequency_analysis": {},
        "summary": "Log pattern analysis completed.",
    }

    # Basic pattern analysis
    all_messages = []
    for stream in streams:
        values = stream.get("values", [])
        for _, message in values:
            all_messages.append(message)

    # Look for common error patterns
    error_patterns = ["ERROR", "Exception", "Failed", "Timeout", "Connection refused"]
    error_count = sum(
        1
        for msg in all_messages
        if any(pattern.lower() in msg.lower() for pattern in error_patterns)
    )

    # Look for common HTTP status patterns
    http_patterns = ["200", "404", "500", "403", "502"]
    http_count = sum(1 for msg in all_messages if any(pattern in msg for pattern in http_patterns))

    if error_count > 0:
        analysis["patterns"].append(
            {
                "type": "errors",
                "count": error_count,
                "description": f"Found {error_count} messages containing error indicators",
            }
        )

    if http_count > 0:
        analysis["patterns"].append(
            {
                "type": "http_status",
                "count": http_count,
                "description": f"Found {http_count} messages with HTTP status codes",
            }
        )

    if not analysis["patterns"]:
        analysis["summary"] = "No specific patterns detected in the log sample."
    else:
        analysis["summary"] = f"Identified {len(analysis['patterns'])} log patterns for analysis."

    return analysis


def _detect_log_anomalies(log_data: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
    """Detect anomalous patterns in logs."""
    streams = log_data.get("data", {}).get("result", [])

    analysis = {
        "anomalies": [],
        "severity_score": 0,
        "summary": "Anomaly detection completed.",
    }

    # Basic anomaly detection
    all_messages = []
    timestamps = []

    for stream in streams:
        values = stream.get("values", [])
        for timestamp, message in values:
            all_messages.append(message)
            timestamps.append(float(timestamp))

    # Check for sudden spikes in error messages
    error_messages = [msg for msg in all_messages if "ERROR" in msg.upper() or "Exception" in msg]
    if len(error_messages) > len(all_messages) * 0.1:  # More than 10% errors
        analysis["anomalies"].append(
            {
                "type": "high_error_rate",
                "severity": "high",
                "description": f"High error rate detected: {len(error_messages)}/{len(all_messages)} messages contain errors",
                "recommendation": "Investigate the source of these errors",
            }
        )
        analysis["severity_score"] += 3

    # Check for connection issues
    connection_issues = [
        msg
        for msg in all_messages
        if any(term in msg.lower() for term in ["connection refused", "timeout", "unreachable"])
    ]
    if connection_issues:
        analysis["anomalies"].append(
            {
                "type": "connection_issues",
                "severity": "medium",
                "description": f"Found {len(connection_issues)} connection-related issues",
                "recommendation": "Check network connectivity and service availability",
            }
        )
        analysis["severity_score"] += 2

    # Check for timestamp anomalies (logs coming out of order)
    if timestamps and len(timestamps) > 1:
        sorted_timestamps = sorted(timestamps)
        if timestamps != sorted_timestamps:
            analysis["anomalies"].append(
                {
                    "type": "timestamp_anomaly",
                    "severity": "low",
                    "description": "Log entries appear out of chronological order",
                    "recommendation": "Verify log shipping configuration",
                }
            )
            analysis["severity_score"] += 1

    if not analysis["anomalies"]:
        analysis["summary"] = "No significant anomalies detected in the log sample."
    else:
        severity = (
            "high"
            if analysis["severity_score"] > 3
            else "medium"
            if analysis["severity_score"] > 1
            else "low"
        )
        analysis["summary"] = (
            f"Detected {len(analysis['anomalies'])} anomal{'ies' if len(analysis['anomalies']) != 1 else 'y'} with {severity} severity."
        )

    return analysis


def _search_error_patterns(log_data: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
    """Search for error patterns in logs."""
    streams = log_data.get("data", {}).get("result", [])

    analysis = {
        "error_count": 0,
        "error_types": {},
        "error_samples": [],
        "summary": "Error search completed.",
    }

    error_keywords = [
        "ERROR",
        "Exception",
        "Failed",
        "Timeout",
        "Connection refused",
        "Internal server error",
        "NullPointerException",
        "KeyError",
        "ValueError",
        "TypeError",
        "500",
        "502",
        "503",
        "504",
    ]

    for stream in streams:
        values = stream.get("values", [])
        for timestamp, message in values:
            if any(keyword.lower() in message.lower() for keyword in error_keywords):
                analysis["error_count"] += 1

                # Categorize error types
                if "timeout" in message.lower():
                    analysis["error_types"]["timeout"] = (
                        analysis["error_types"].get("timeout", 0) + 1
                    )
                elif "connection" in message.lower():
                    analysis["error_types"]["connection"] = (
                        analysis["error_types"].get("connection", 0) + 1
                    )
                elif "500" in message:
                    analysis["error_types"]["server_error"] = (
                        analysis["error_types"].get("server_error", 0) + 1
                    )
                elif "exception" in message.lower():
                    analysis["error_types"]["exception"] = (
                        analysis["error_types"].get("exception", 0) + 1
                    )
                else:
                    analysis["error_types"]["other"] = analysis["error_types"].get("other", 0) + 1

                # Collect sample errors (limit to 5)
                if len(analysis["error_samples"]) < 5:
                    analysis["error_samples"].append(
                        {
                            "timestamp": timestamp,
                            "message": message[:200] + "..." if len(message) > 200 else message,
                            "stream_labels": stream.get("stream", {}),
                        }
                    )

    if analysis["error_count"] == 0:
        analysis["summary"] = "No error messages found in the log sample."
    else:
        top_error_type = (
            max(analysis["error_types"].items(), key=lambda x: x[1])
            if analysis["error_types"]
            else ("unknown", 0)
        )
        analysis["summary"] = (
            f"Found {analysis['error_count']} error messages, with '{top_error_type[0]}' being the most common type."
        )

    return analysis


def _analyze_request_traces(log_data: dict[str, Any]) -> dict[str, Any]:
    """Analyze request traces through log streams."""
    streams = log_data.get("data", {}).get("result", [])

    analysis = {
        "request_traces": [],
        "trace_count": 0,
        "correlation_ids": set(),
        "summary": "Request trace analysis completed.",
    }

    # Look for correlation IDs and request patterns
    correlation_patterns = [
        r"request.?id[:=]\s*([a-f0-9\-]+)",
        r"trace.?id[:=]\s*([a-f0-9\-]+)",
        r"correlation.?id[:=]\s*([a-f0-9\-]+)",
        r"x-request-id[:=]\s*([a-f0-9\-]+)",
    ]

    import re

    for stream in streams:
        values = stream.get("values", [])
        trace_entries = []

        for timestamp, message in values:
            for pattern in correlation_patterns:
                matches = re.findall(pattern, message, re.IGNORECASE)
                if matches:
                    analysis["correlation_ids"].update(matches)
                    trace_entries.append(
                        {"timestamp": timestamp, "message": message, "correlation_ids": matches}
                    )

        if trace_entries:
            analysis["request_traces"].append(
                {
                    "stream_labels": stream.get("stream", {}),
                    "entries": trace_entries,
                    "entry_count": len(trace_entries),
                }
            )

    analysis["trace_count"] = len(analysis["request_traces"])
    analysis["unique_correlation_ids"] = len(analysis["correlation_ids"])

    if analysis["trace_count"] == 0:
        analysis["summary"] = "No request traces found in the log sample."
    else:
        analysis["summary"] = (
            f"Found {analysis['trace_count']} request trace{'s' if analysis['trace_count'] != 1 else ''} with {analysis['unique_correlation_ids']} unique correlation ID{'s' if analysis['unique_correlation_ids'] != 1 else ''}."
        )

    return analysis
