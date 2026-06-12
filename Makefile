# Load variables from .env if it exists
ifneq (,$(wildcard .env))
include .env
export
endif

# Project variables
PART ?= patch  # can be overwritten with: make bump-version PART=minor
PY_SRC ?= src

# ============================================================================
# Environment
# ============================================================================

# Delete the virtual environment and force a full sync
venv:
	rm -rf .venv && \
	echo "Deleted virtual environment" && \
	uv sync --all-extras --group dev && \
	echo "Created virtual environment" && \
	uvx --from=toml-cli toml get --toml-path=pyproject.toml project.version

# Sync version from pyproject.toml to __init__.py and docs_source/conf.py
sync-version:
	uv run python scripts/update_version.py

# ============================================================================
# Versioning & Publishing
# ============================================================================

# Bump patch/minor/major version
bump-version:
	@v=$$(uvx --from=toml-cli toml get --toml-path=pyproject.toml project.version) && \
	echo "Current version: $$v" && \
	uvx --from bump2version bumpversion --allow-dirty --current-version "$$v" $(PART) pyproject.toml && \
	echo "Version bumped to new $(PART)"
	$(MAKE) sync-version

# Build python package
build: bump-version
	uv build

# Clean build artifacts
clean-artifacts:
	rm -rf dist *.egg-info build && \
	echo "Cleaned build artifacts"

# Clean all temporary files
clean: clean-artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

# Publish package on PyPI
publish: build
	uv publish

# Publish on TestPyPI
publish-test: build
	uv publish --repository testpypi

# ============================================================================
# Code Quality
# ============================================================================

# Run linting with ruff
lint:
	uv run ruff check src/ tests/

# Format code with ruff
format:
	uv run ruff format .

# Run type checking with mypy
type-check:
	uv run mypy src/

# Run security checks with bandit
security-check:
	uv run bandit -r src/

# Run all quality checks
check: lint format type-check security-check
	@echo "All checks completed"

# ============================================================================
# Testing
# ============================================================================

# Run tests
test:
	uv run pytest -v

# Run tests with coverage report
test-cov:
	uv run pytest --cov=src/ --cov-report=xml --cov-report=term --cov-report=html

# ============================================================================
# Installation
# ============================================================================

# Install project in development mode and configure git hooks
install:
	uv sync --all-extras --group dev
	git config core.hooksPath .githooks

# Install project with all optional dependencies
install-all:
	uv sync --all-extras

# ============================================================================
# Documentation
# ============================================================================

# Build documentation
docs:
	rm -rf docs/
	uv run sphinx-build -q docs_source docs

# Serve documentation locally
docs-serve: docs
	uv run python -m http.server 8000 --directory docs

# ============================================================================
# Utilities
# ============================================================================

# Open Python REPL with project environment
shell:
	uv run python

# Show project info
info:
	@echo "Project: advanced-automapper"
	@echo "Version: $$(uvx --from=toml-cli toml get --toml-path=pyproject.toml project.version)"
	@echo "Python: $$(uv run python --version)"
	@echo "Virtual env: $$(if [ -d .venv ]; then echo '.venv exists'; else echo '.venv not found'; fi)"

# Help
help:
	@echo "Available targets:"
	@echo "  venv          - Delete and recreate virtual environment"
	@echo "  install       - Install project dependencies and configure git hooks"
	@echo "  install-all   - Install with all optional dependencies"
	@echo "  bump-version  - Bump version (PART=patch|minor|major)"
	@echo "  build         - Build python package"
	@echo "  clean         - Remove all temporary files"
	@echo "  publish       - Publish package on PyPI"
	@echo "  publish-test  - Publish package on TestPyPI"
	@echo "  lint          - Run ruff linter"
	@echo "  format        - Run ruff formatter"
	@echo "  type-check    - Run mypy type checker"
	@echo "  security-check - Run bandit security checker"
	@echo "  check         - Run all quality checks"
	@echo "  test          - Run tests"
	@echo "  test-cov      - Run tests with coverage"
	@echo "  docs          - Build documentation"
	@echo "  docs-serve    - Serve documentation locally"
	@echo "  info          - Show project info"

.PHONY: venv sync-version bump-version build clean-artifacts clean publish publish-test \
        lint format type-check security-check check test test-cov install install-all \
        docs docs-serve shell info help
