# Monitoring MCP Server - Production image (uv)
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app/src
ENV UV_LINK_MODE=copy

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash monitoring

COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

RUN uv sync --no-dev \
    && chown -R monitoring:monitoring /app

USER monitoring

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD uv run python -c "import monitoring_mcp; print('healthy')" || exit 1

EXPOSE 10851

CMD ["uv", "run", "python", "-m", "monitoring_mcp"]
