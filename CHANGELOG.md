# Changelog

## [Unreleased] - 2026-04-24

### Removed
- **MCP Support**: Removed all Model Context Protocol (MCP) references and integrations
  - Deleted `integrations/github/GITHUB_MCP_INTEGRATION.md`
  - Deleted `integrations/jira/JIRA_MCP_INTEGRATION.md`
  - Deleted `integrations/jira/SIMPLIFIED_SETUP.md`
  - Updated all documentation to reflect GitHub GraphQL API and JIRA REST API usage

- **Outdated Documentation Files**:
  - Deleted `QUICKSTART.md` - Outdated quick start with MCP references
  - Deleted `BUILD_SUMMARY.md` - Historical build documentation
  - Deleted `AUTOMATION.md` - Referenced non-existent automation code
  - Deleted `GOAL.md` - Historical goal document (goals achieved)
  - Deleted `RECENT_CHANGES.md` - Temporary change documentation
  - Deleted `CHANGES.md` - Redundant with git history
  - Deleted `SIMPLIFIED_SETUP_SUMMARY.md` - Outdated setup guide
  - Deleted `setup.sh` - Outdated setup script

### Changed
- **README.md**: Major update to reflect current architecture
  - Clarified 7 core skills (4 user-facing + 3 data/graph skills)
  - Added proper installation instructions with Makefile
  - Updated directory structure to match actual codebase
  - Added development section with build/test commands
  - Improved architecture explanation
  
- **GETTING_STARTED.md**: Complete rewrite
  - Added prerequisites and installation steps
  - Updated all skill descriptions
  - Added development and troubleshooting sections
  - Removed references to non-existent CLI commands

- **Data Ingestion**:
  - `integrations/storage/ingest_jira.py` - Updated to reference "public JIRA REST API"
  - `integrations/storage/README.md` - Removed MCP references, clarified GitHub GraphQL usage
  - `skills/ask-agentic-docs/SKILL.md` - Replaced MCP references with database integration

### Added
- **Development Tools**:
  - `Makefile` - Build, test, lint, format commands
  - `pyproject.toml` - Modern Python project configuration
  - `requirements.txt` - Core dependencies (PyYAML, python-dotenv)
  - `requirements-dev.txt` - Development dependencies (pytest, black, flake8, etc.)

- **Testing Infrastructure**:
  - `tests/` - Test suite with unit and integration tests
  - `.coverage` - Test coverage configuration

- **Comprehensive Documentation**:
  - `CORE_SKILLS.md` - Detailed skill reference
  - `SYSTEM_OVERVIEW.md` - Complete system architecture
  - `WORKFLOW_EXPLAINED.md` - Detailed workflow documentation
  - `USAGE.md` - Usage examples
  - `DEPENDENCY_MANAGEMENT.md` - Dependency information

### Technical Details

**GitHub Data Ingestion**:
- Uses GitHub GraphQL API for efficient data fetching
- Supports date range filtering (default: past year)
- Pagination with cursor-based navigation
- Single repository focus for optimal performance

**JIRA Integration**:
- Uses public JIRA REST API (issues.redhat.com)
- No authentication required for public instances
- Automatic correlation with GitHub PRs and issues
- Extracts JIRA keys from PR titles, bodies, and commit messages

**Knowledge Graphs**:
- Internal: NetworkX-based graph generation (recommended)
- External: Optional graphify tool integration
- Exports to JSON (node-link format)
- Supports ≤3 hop navigation constraint

**Quality Constraints**:
- AGENTS.md ≤150 lines
- Component docs ≤100 lines each
- Concept docs ≤75 lines each
- Navigation depth ≤3 hops
- Quality score ≥70/100 to pass

## Project Status

**Current State**: Production-ready skill library for Claude Code

**Core Skills**: 7 (4 user-invocable + 3 data/graph)

**Documentation**: 10 documentation files (down from 15+)

**Testing**: Comprehensive test suite with pytest

**Dependencies**: Minimal (PyYAML, python-dotenv for core; optional for GitHub ingestion)

## Migration Guide

### For Users

**Before** (non-existent CLI):
```bash
agentic /create <repo>  # This never existed
```

**After** (Claude Code skills):
```bash
# Install dependencies
make install

# Use in Claude Code
/create                    # In any repository
/validate
/evaluate
/ask what components exist?
```

### For Developers

**Setup**:
```bash
git clone https://github.com/kenjpais/claude-agent-knowledge-skills
cd claude-agent-knowledge-system-skills
make install-dev
make test
```

**Testing**:
```bash
make test          # Run tests
make lint          # Run linters
make format        # Format code
```

## Breaking Changes

- Removed non-existent `agentic` CLI (documentation incorrectly referenced it)
- Removed MCP server integrations (replaced with direct API calls)
- Removed setup.sh (replaced with Makefile)

## Credits

**Contributors**: Claude Sonnet 4.5

**Date**: 2026-04-24
