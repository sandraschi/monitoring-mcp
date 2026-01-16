# Monitoring MCP Server - Production Docker Image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV PATH="/app/.venv/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Create virtual environment
RUN python -m venv .venv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -e .

# Copy source code
COPY src/ ./src/

# Create non-root user
RUN useradd --create-home --shell /bin/bash monitoring && \
    chown -R monitoring:monitoring /app
USER monitoring

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import monitoring_mcp; print('healthy')" || exit 1

# Expose port (if needed for health checks)
EXPOSE 8000

# Default command
CMD ["python", "-m", "monitoring_mcp"]