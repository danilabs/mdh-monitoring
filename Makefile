.PHONY: help install install-dev test lint security type-check clean all ci

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements.txt -r requirements-dev.txt

test:  ## Run tests with coverage
	pytest tests/ -v --cov=mdh_analyzer --cov-report=term-missing

test-integration:  ## Run integration tests
	python test_improvements.py

lint:  ## Run pylint code quality checks
	pylint mdh_analyzer/ --output-format=text --score=yes

lint-fix:  ## Auto-fix code formatting issues
	black mdh_analyzer/ tests/
	isort mdh_analyzer/ tests/

security:  ## Run security vulnerability scans
	@echo "Running Safety (dependency vulnerabilities)..."
	safety check --short-report
	@echo "\nRunning Bandit (security linter)..."
	bandit -r mdh_analyzer/ -f txt
	@echo "\nRunning Semgrep (static analysis)..."
	semgrep --config=auto mdh_analyzer/ --text

type-check:  ## Run type checking with MyPy
	mypy mdh_analyzer/ --ignore-missing-imports --show-error-codes --pretty

clean:  ## Clean up generated files
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf *.egg-info/
	rm -rf build/
	rm -rf dist/
	rm -rf test_data/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

all: lint type-check test security  ## Run all CI checks locally

ci: install-dev all test-integration  ## Run complete CI pipeline locally

format-check:  ## Check code formatting
	black --check mdh_analyzer/ tests/
	isort --check-only mdh_analyzer/ tests/

format:  ## Format code
	black mdh_analyzer/ tests/
	isort mdh_analyzer/ tests/

# Development workflow commands
dev-setup: install-dev  ## Set up development environment
	@echo "Development environment ready!"
	@echo "Run 'make help' to see available commands"

quick-check: lint test  ## Quick development checks (lint + test)

pre-commit: format lint type-check test  ## Run pre-commit checks