# Contributing to Monitoring MCP

Thank you for your interest in contributing to the Monitoring MCP Server.

## Development Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Git
- Optional: Node.js 20+ (web UI), Docker/Podman (compose)

### Installation

```powershell
git clone https://github.com/sandraschi/monitoring-mcp.git
Set-Location monitoring-mcp
uv sync --extra dev
Copy-Item .env.example .env
```

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for full workflow.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make changes with tests under `tests/unit/`
4. Run quality checks:
   ```powershell
   uv run ruff check .
   uv run --extra dev pytest
   ```
5. Update docs if you change tools, config, or install paths (`docs/TOOLS.md`, `docs/CONFIGURATION.md`, `llms.txt`)
6. Open a Pull Request

## Code Quality Standards

### Linting and Formatting

- Code must pass `uv run ruff check .`
- Prefer type hints on public APIs

### Testing

- New tool operations need mocked unit tests
- Coverage gate: **50%** (`pyproject.toml`); aim not to regress the current suite (~74%)
- Run: `uv run --extra dev pytest`

### Documentation

- User-facing changes → `README.md` / `INSTALL.md` / `docs/*`
- New or changed operations → `docs/TOOLS.md` and `llms.txt`
- Agent-facing notes → `AGENTS.md` / `CLAUDE.md`

## Tool Design

Portmanteau tools with an `operation` enum. Returns should include `success` and a `conversational_summary`. See [docs/TOOLS.md](docs/TOOLS.md).

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).
