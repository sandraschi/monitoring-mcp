# Contributing to Monitoring MCP

Thank you for your interest in contributing to the Monitoring MCP Server! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites
- Python 3.10+
- Git

### Installation
```bash
git clone https://github.com/sandraschi/monitoring-mcp.git
cd monitoring-mcp
pip install -e .[dev]
```

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes with comprehensive tests
4. Run the quality checks: `make check` or `ruff check . && ruff format . && mypy src/ && pytest`
5. Commit your changes: `git commit -m "Add your feature"`
6. Push to your fork: `git push origin feature/your-feature-name`
7. Create a Pull Request

## Code Quality Standards

### Linting and Formatting
- Code must pass `ruff check .` and `ruff format --check .`
- Type hints are required for all new code
- Follow PEP 8 style guidelines

### Testing
- All new features must include comprehensive tests
- Tests should achieve at least 80% code coverage
- Run tests with `pytest`

### Documentation
- Update README.md for any user-facing changes
- Add docstrings to all public functions and classes
- Update type hints as needed

## Pull Request Process

1. **Title**: Use a clear, descriptive title
2. **Description**: Explain what the PR does and why
3. **Tests**: Ensure all tests pass
4. **Documentation**: Update docs if needed
5. **Review**: Request review from maintainers

## Commit Message Guidelines

Use conventional commit format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `style:` for formatting
- `refactor:` for code refactoring
- `test:` for testing
- `chore:` for maintenance

Example: `feat: add prometheus alerting support`

## Architecture Guidelines

### Portmanteau Pattern
This project uses the "portmanteau tool" pattern to avoid tool explosion:
- Consolidate related operations into single tools
- Use operation parameters to route to specific functionality
- Maintain clean separation of concerns

### Async First
- All I/O operations should be async
- Use FastMCP's async capabilities
- Avoid blocking operations in tool implementations

### Error Handling
- Provide conversational error messages
- Include troubleshooting tips when possible
- Gracefully degrade when services are unavailable

## Issue Reporting

When reporting bugs or requesting features:
- Use the GitHub issue templates
- Provide clear reproduction steps
- Include relevant logs and configuration
- Specify your environment (Python version, OS, etc.)

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.