.PHONY: help install install-dev test lint format clean output

# Default target
help:
	@echo "Agent Knowledge System"
	@echo "======================"
	@echo ""
	@echo "Setup:"
	@echo "  make install      - Install core dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make format       - Format code with black"
	@echo "  make lint         - Run linters (flake8, pylint, mypy)"
	@echo "  make test         - Run test suite"
	@echo "  make clean        - Remove build artifacts"
	@echo ""
	@echo "Usage:"
	@echo "  ./agentic /create <repo>      - Generate documentation"
	@echo "  ./agentic /validate <repo>    - Validate quality"
	@echo "  ./agentic /ask <question>     - Query documentation"
	@echo ""
	@echo "Examples:"
	@echo "  ./agentic /create https://github.com/openshift/installer"
	@echo "  ./agentic /create ."
	@echo "  ./agentic /validate ."
	@echo "  ./agentic /ask what components exist?"
	@echo ""

install:
	@echo "📦 Installing core dependencies..."
	pip install -r requirements.txt

install-dev:
	@echo "📦 Installing development dependencies..."
	pip install -r requirements-dev.txt

# Code quality
format:
	@echo "🎨 Formatting code with black..."
	black integrations/ utilities/ --exclude venv

lint:
	@echo "🔍 Running linters..."
	@echo "\n==> flake8"
	flake8 integrations/ utilities/ --exclude venv --max-line-length=100
	@echo "\n==> pylint"
	pylint integrations/ utilities/ --rcfile=pyproject.toml || true
	@echo "\n==> mypy"
	mypy integrations/ utilities/ --config-file=pyproject.toml || true

test:
	@echo "🧪 Running tests..."
	pytest tests/ -v

# Cleanup
clean:
	@echo "🧹 Cleaning build artifacts..."
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name 'htmlcov' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '.coverage' -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Cleanup cloned repositories
clean-repos:
	@echo "🧹 Cleaning cloned repositories..."
	@rm -rf /tmp/agentic-repos
	@echo "✅ Cloned repositories cleaned"

# Check environment
check-env:
	@echo "🔍 Checking environment..."
	@python --version
	@pip --version
	@which gh || echo "⚠️  GitHub CLI (gh) not found"
	@echo ""
	@if [ -f .env ]; then \
		echo "✅ .env file exists"; \
	else \
		echo "⚠️  .env file not found (optional)"; \
		echo "   Copy .env.example to .env and fill in tokens"; \
	fi
