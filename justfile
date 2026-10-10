set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]
import 'scripts/just/fleet.just'

# --- Dashboard ---

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# --- Quality ---

# Execute Ruff SOTA v13.1 linting
lint:
    Set-Location '{{justfile_directory()}}'; uv run ruff check .; Set-Location '{{justfile_directory()}}\web_sota'; npx @biomejs/biome ci .

# Execute Ruff SOTA v13.1 fix and formatting
fix:
    Set-Location '{{justfile_directory()}}'; uv run ruff check . --fix --unsafe-fixes; uv run ruff format .; Set-Location '{{justfile_directory()}}\web_sota'; npx @biomejs/biome check --write .

# Verify formatting without writing (CI gate)
fmt-check:
    Set-Location '{{justfile_directory()}}'; uv run ruff format . --check

# Run the unit suite (coverage gate 50% per pyproject)
test:
    Set-Location '{{justfile_directory()}}'; uv run --extra dev pytest -x --tb=short -k "not slow"

# Serve the FastAPI backend locally (port 10851 per fleet-start.config.ps1)
serve:
    Set-Location '{{justfile_directory()}}'; uv run uvicorn monitoring_mcp.server:app --host 127.0.0.1 --port 10851

# Playwright E2E (starts backend + frontend via webServer entries)
e2e:
    Set-Location '{{justfile_directory()}}\web_sota'; npx playwright test

# Full local gate: lint + format-check + unit tests
certify:
    Set-Location '{{justfile_directory()}}'; uv run ruff check .; uv run ruff format . --check; uv run --extra dev pytest -x --tb=short -k "not slow"

# Build the .mcpb bundle (wipe + fresh-copy src -> mcpb/src, then pack)
mcpb-pack:
    Set-Location '{{justfile_directory()}}'; powershell.exe -NoProfile -ExecutionPolicy Bypass -File '{{justfile_directory()}}\scripts\mcpb-pack.ps1' -RepoRoot '{{justfile_directory()}}'

# --- Hardening ---
check-sec:
    Set-Location '{{justfile_directory()}}'; uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    Set-Location '{{justfile_directory()}}'; uv run safety check

# Bootstrap: install dev deps + pre-commit hook
bootstrap:
    Set-Location '{{justfile_directory()}}'; uv sync --group dev; uv run pre-commit install; Write-Host "Pre-commit hooks installed." -ForegroundColor Green