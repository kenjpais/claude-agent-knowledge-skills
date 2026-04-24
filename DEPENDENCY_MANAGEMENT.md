# Dependency Management

This document describes the dependency management setup for the Agent Knowledge System.

## 📦 Overview

The project uses modern Python packaging standards with multiple dependency files for different use cases:

| File | Purpose | Usage |
|------|---------|-------|
| `requirements.txt` | Core runtime dependencies | Production use |
| `requirements-dev.txt` | Development tools | Development and testing |
| `pyproject.toml` | Modern Python project config | Build metadata and tool config |
| `.env.example` | Environment variable template | Copy to `.env` for secrets |

---

## 🚀 Installation

### Quick Start

```bash
# Automated setup (recommended)
./setup.sh

# Or manual installation
pip install -r requirements.txt
```

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Or use make
make install-dev
```

---

## 📋 Dependencies

### Core Dependencies (requirements.txt)

**PyYAML** `>=6.0.1`
- YAML parsing for skill definitions and templates
- Required for: Skill registry, template processing
- License: MIT

**python-dotenv** `>=1.0.0`
- Environment variable management from `.env` files
- Required for: GitHub token loading, configuration
- License: BSD-3-Clause

### Development Dependencies (requirements-dev.txt)

**Testing:**
- `pytest>=7.4.0` - Testing framework
- `pytest-cov>=4.1.0` - Coverage reporting

**Code Quality:**
- `black>=23.7.0` - Code formatter
- `flake8>=6.1.0` - Style guide enforcement
- `pylint>=2.17.0` - Code linter
- `mypy>=1.5.0` - Static type checker

**Type Stubs:**
- `types-PyYAML>=6.0.12` - Type hints for PyYAML

---

## 🛠️ Development Tools

### Makefile Commands

```bash
# Installation
make install          # Install core dependencies
make install-dev      # Install development dependencies

# Code quality
make format          # Format code with black
make lint            # Run all linters
make test            # Run test suite

# Utilities
make clean           # Remove build artifacts
make help            # Show all commands
```

### Manual Commands

**Format code:**
```bash
black integrations/ utilities/ --line-length=100
```

**Run linters:**
```bash
flake8 integrations/ utilities/ --max-line-length=100
pylint integrations/ utilities/
mypy integrations/ utilities/
```

**Run tests:**
```bash
pytest tests/ -v
pytest tests/ --cov=integrations --cov=utilities
```

---

## 📝 Configuration

### pyproject.toml

Contains project metadata and tool configurations:

**Project metadata:**
- Name, version, description
- Python version requirements (>=3.9)
- Dependencies and optional dependencies
- Entry points and scripts

**Tool configurations:**
- `[tool.black]` - Code formatter settings
- `[tool.pytest]` - Test framework settings
- `[tool.mypy]` - Type checker settings
- `[tool.pylint]` - Linter settings
- `[tool.coverage]` - Coverage reporting settings

### Environment Variables (.env)

**Setup:**
```bash
# Copy template
cp .env.example .env

# Edit and add tokens
vim .env
```

**Variables:**
```bash
# GitHub token (recommended for higher rate limits)
GH_API_TOKEN=ghp_your_token_here

# JIRA (optional - only for private instances)
JIRA_URL=https://your-jira.com
JIRA_EMAIL=your@email.com
JIRA_API_TOKEN=your-token
```

**Security:**
- `.env` file is in `.gitignore`
- Never commit `.env` to version control
- Use `.env.example` as template

---

## 🧪 Testing

### Running Tests

```bash
# All tests
make test

# Specific test file
pytest tests/unit/test_jira_extraction.py -v

# With coverage report
pytest tests/ --cov=integrations --cov-report=html
```

### Test Structure

```
tests/
├── __init__.py
├── unit/                   # Unit tests (fast, isolated)
│   └── test_jira_extraction.py
└── integration/            # Integration tests (slower, external deps)
```

### Writing Tests

```python
# tests/unit/test_module.py
import pytest

class TestFeature:
    """Test suite for feature."""

    def test_basic_functionality(self):
        """Test description."""
        # Arrange
        input_data = "test"
        
        # Act
        result = function(input_data)
        
        # Assert
        assert result == expected
```

---

## 📊 Code Quality Standards

### Style Guide

- **Line length:** 100 characters
- **Style:** PEP 8 with black formatting
- **Docstrings:** Google style
- **Type hints:** Required for public APIs

### Pre-commit Checklist

Before committing code:

```bash
# 1. Format
make format

# 2. Lint
make lint

# 3. Test
make test

# 4. Review changes
git diff
```

---

## 🔄 Updating Dependencies

### Adding a New Dependency

**Core dependency:**
```bash
# 1. Add to requirements.txt
echo "package-name>=version" >> requirements.txt

# 2. Add to pyproject.toml dependencies list
vim pyproject.toml

# 3. Install
pip install -r requirements.txt

# 4. Commit both files
git add requirements.txt pyproject.toml
git commit -m "deps: add package-name for feature X"
```

**Development dependency:**
```bash
# 1. Add to requirements-dev.txt
echo "package-name>=version" >> requirements-dev.txt

# 2. Add to pyproject.toml [project.optional-dependencies] dev list
vim pyproject.toml

# 3. Install
pip install -r requirements-dev.txt
```

### Upgrading Dependencies

```bash
# Check outdated packages
pip list --outdated

# Upgrade specific package
pip install --upgrade package-name

# Update requirements file
pip freeze | grep package-name >> requirements.txt

# Test thoroughly
make test
```

---

## 🔒 Security

### Dependency Security

**Check for vulnerabilities:**
```bash
# Using pip-audit (install first: pip install pip-audit)
pip-audit

# Or use safety
pip install safety
safety check
```

### Best Practices

1. **Pin versions** - Use `>=` for flexibility, `==` for reproducibility
2. **Review updates** - Check changelogs before upgrading
3. **Test after updates** - Run full test suite
4. **Scan for vulnerabilities** - Use pip-audit or safety
5. **Keep .env secure** - Never commit tokens

---

## 📚 Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [pip documentation](https://pip.pypa.io/)
- [pyproject.toml specification](https://peps.python.org/pep-0621/)
- [pytest documentation](https://docs.pytest.org/)
- [black documentation](https://black.readthedocs.io/)

---

## Summary

The project uses modern Python dependency management with:

✅ **requirements.txt** - Core dependencies  
✅ **requirements-dev.txt** - Development tools  
✅ **pyproject.toml** - Modern project configuration  
✅ **Makefile** - Convenient development commands  
✅ **Tests** - Automated testing with pytest  
✅ **Linting** - Code quality with black, flake8, pylint, mypy  

**Installation:** `./setup.sh` or `pip install -r requirements.txt`  
**Development:** `make install-dev` then `make help`
