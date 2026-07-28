"""
Shared utilities for monitoring-mcp: caching, sampling, encryption, parallel helpers.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ResponseCache:
    """Simple in-memory TTL cache for API responses."""

    def __init__(self, ttl_seconds: int = 300, enabled: bool = True) -> None:
        self.ttl_seconds = ttl_seconds
        self.enabled = enabled
        self._store: dict[str, tuple[float, Any]] = {}

    def _key(self, *parts: Any) -> str:
        raw = json.dumps(parts, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, *parts: Any) -> Any | None:
        if not self.enabled:
            return None
        key = self._key(*parts)
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, *parts: Any, value: Any) -> Any:
        if self.enabled:
            key = self._key(*parts)
            self._store[key] = (time.monotonic() + self.ttl_seconds, value)
        return value

    def clear(self) -> None:
        self._store.clear()


def ensure_encryption_key(storage_path: Path, configured_key: str | None = None) -> str:
    """
    Persist encryption key across restarts.

    Prefer explicit config/env; otherwise load or create ``.encryption_key`` under storage_path.
    """
    key_file = storage_path / ".encryption_key"
    storage_path.mkdir(parents=True, exist_ok=True)

    if configured_key and not configured_key.startswith("ephemeral:"):
        # Persist env-provided key so restarts stay consistent when env is unset later
        if not key_file.exists():
            key_file.write_text(configured_key, encoding="utf-8")
        return configured_key

    if key_file.exists():
        return key_file.read_text(encoding="utf-8").strip()

    import secrets

    new_key = secrets.token_hex(32)
    key_file.write_text(new_key, encoding="utf-8")
    try:
        key_file.chmod(0o600)
    except OSError:
        pass
    return new_key


def seal_payload(payload: dict[str, Any] | str, key: str) -> str:
    """HMAC-sign a JSON payload (integrity + authenticity; not full encryption)."""
    body = payload if isinstance(payload, str) else json.dumps(payload, sort_keys=True, default=str)
    sig = hmac.new(key.encode(), body.encode(), hashlib.sha256).hexdigest()
    return json.dumps({"payload": body, "sig": sig})


def unseal_payload(sealed: str, key: str) -> dict[str, Any] | str:
    """Verify and unpack a sealed payload."""
    wrapper = json.loads(sealed)
    body = wrapper["payload"]
    sig = wrapper["sig"]
    expected = hmac.new(key.encode(), body.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        raise ValueError("Payload signature verification failed")
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body


def sample_list[T](
    items: list[T],
    *,
    enable_sampling: bool,
    sampling_threshold: int,
    sampling_rate: float,
) -> tuple[list[T], dict[str, Any]]:
    """
    Downsample large result lists according to config.

    Returns (possibly sampled list, meta dict).
    """
    meta: dict[str, Any] = {
        "original_count": len(items),
        "sampled": False,
        "returned_count": len(items),
        "sampling_rate": sampling_rate,
    }
    if not enable_sampling or len(items) <= sampling_threshold:
        return items, meta

    step = max(1, int(1 / sampling_rate))
    sampled = items[::step]
    meta.update(
        {
            "sampled": True,
            "returned_count": len(sampled),
            "step": step,
            "note": f"Sampled {len(sampled)}/{len(items)} items (rate={sampling_rate})",
        }
    )
    return sampled, meta


def map_parallel[T](fn: Callable[[T], Any], items: list[T], *, max_workers: int = 4) -> list[Any]:
    """
    Map ``fn`` over items, using loky when available for larger batches.

    Falls back to sequential map. loky is a process-pool executor (wired intentionally
    for CPU-bound sampling/analysis of large series).
    """
    if len(items) < 50:
        return [fn(item) for item in items]

    try:
        from loky import get_reusable_executor

        with get_reusable_executor(max_workers=max_workers, timeout=30) as executor:
            return list(executor.map(fn, items))
    except Exception as exc:
        logger.debug("loky parallel map unavailable (%s); using sequential", exc)
        return [fn(item) for item in items]


def match_prometheus_target(target: dict[str, Any], name: str) -> bool:
    """Match a scrape target by job, instance, or scrape URL (not __name__)."""
    needle = name.lower()
    labels = target.get("labels", {}) or {}
    discovered = target.get("discoveredLabels", {}) or {}
    candidates = [
        labels.get("job"),
        labels.get("instance"),
        discovered.get("job"),
        discovered.get("__address__"),
        target.get("scrapeUrl"),
        target.get("labels", {}).get("__address__"),
    ]
    return any(c and needle in str(c).lower() for c in candidates)
