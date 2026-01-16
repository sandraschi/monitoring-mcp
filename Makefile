# Monitoring MCP Development Makefile

.PHONY: help install test lint format type-check check clean build docs

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install the package in development mode
	pip install -e .[dev]

install-prod: ## Install the package for production
	pip install .

test: ## Run the test suite
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=monitoring_mcp --cov-report=html --cov-report=term-missing

lint: ## Run linting checks
	ruff check .

format: ## Format code with ruff
	ruff format .

type-check: ## Run type checking with mypy
	mypy src/

check: ## Run all quality checks (lint, format, type-check, test)
	ruff check .
	ruff format --check .
	mypy src/
	pytest

clean: ## Clean up build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	python -m build

docs: ## Generate documentation (if applicable)
	@echo "Documentation generation not yet implemented"

run: ## Run the MCP server
	python -m monitoring_mcp

docker-build: ## Build Docker image
	docker build -t monitoring-mcp .

docker-run: ## Run Docker container
	docker run -p 8000:8000 monitoring-mcp

# Development setup
setup: ## Set up development environment
	pre-commit install
	pip install -e .[dev]

# Release helpers
bump-patch: ## Bump patch version
	@echo "Bumping patch version..."
	# Add version bumping logic here when ready

bump-minor: ## Bump minor version
	@echo "Bumping minor version..."
	# Add version bumping logic here when ready

bump-major: ## Bump major version
	@echo "Bumping major version..."
	# Add version bumping logic here when ready