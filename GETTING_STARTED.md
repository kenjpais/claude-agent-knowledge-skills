# Getting Started with Agent Knowledge System

A skill library for Claude Code that generates and maintains agentic documentation for OpenShift and Kubernetes repositories.

## Prerequisites

- Python 3.9 or higher
- Claude Code installed
- Git

## Installation

### 1. Clone This Repository

```bash
git clone https://github.com/kenjpais/claude-agent-knowledge-skills
cd claude-agent-knowledge-system-skills
```

### 2. Install Dependencies

```bash
# Install core dependencies
make install

# Optional: Install development dependencies (for testing/linting)
make install-dev
```

### 3. Optional: Configure GitHub Token

For higher rate limits when ingesting GitHub data (5,000 requests/hour vs 60):

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your GitHub token
# GH_API_TOKEN=ghp_your_token_here
```

Get a token at: https://github.com/settings/tokens (scopes: `repo`, `read:org`)

## Using Skills in Claude Code

### Generate Documentation

Open Claude Code in any repository and use the core skills:

```bash
# In Claude Code
/create                                                    # Current directory
/create /path/to/openshift-installer                     # Local repository
/create https://github.com/openshift/installer           # GitHub URL (auto-clones)

/validate                                                  # Current directory
/validate https://github.com/openshift/installer         # GitHub URL (auto-clones)

/evaluate                                                  # Current directory
/evaluate /path/to/openshift-installer                   # Local repository

/ask what components exist? /path/to/openshift-installer              # Local repository
/ask how does installer work? https://github.com/openshift/installer  # GitHub URL (auto-clones)
```

### Example Session

```bash
# Option 1: Use with local repository
cd /path/to/openshift-installer
# Type in Claude Code: /create

# Option 2: Use with GitHub URL (auto-clones to /tmp/agentic-repos/)
# Type in Claude Code: /create https://github.com/openshift/installer

# Claude generates:
# ✅ AGENTS.md (entry point, ≤150 lines)
# ✅ Component docs (≤100 lines each)
# ✅ Concept docs (≤75 lines each)
# ✅ Quality score report
# ✅ Knowledge graph

# 3. Validate quality
/validate
# Or: /validate https://github.com/openshift/installer
# ✅ Checks navigation depth (≤3 hops)
# ✅ Validates line budgets
# ✅ Calculates quality score (≥70/100)

# 4. Query documentation (repository path/URL REQUIRED)
/ask how does the installer work? /path/to/openshift-installer
# Or: /ask how does installer work? https://github.com/openshift/installer
# Returns: Purpose, responsibilities, dependencies, workflow

# 5. Evaluate with coding agent
/evaluate
# Or: /evaluate https://github.com/openshift/installer
# Spawns sub-agent to test documentation with 5 scenarios
```

## Core Skills

### 1. `/create` - Generate Agentic Documentation

Generates complete documentation following the Agent Knowledge Framework:

**Output:**
- `AGENTS.md` - Entry point (≤150 lines)
- `agentic/design-docs/components/` - Component documentation
- `agentic/domain/concepts/` - Domain concepts
- `agentic/QUALITY_SCORE.md` - Quality metrics
- Knowledge graph (NetworkX JSON format)

**Time:** ~2-3 minutes for typical OpenShift repository

### 2. `/validate` - Validate Documentation Quality

Validates existing documentation against quality constraints:

**Checks:**
- Structure (AGENTS.md exists, required files present)
- Navigation depth (≤3 hops from AGENTS.md)
- Line budgets (enforced for all docs)
- Broken links (0 required)
- Coverage (≥80% components documented)
- Freshness (updated <90 days)
- Quality score (≥70/100 to pass)

### 3. `/evaluate` - Test with Coding Agent

Spawns a sub-agent to test documentation quality with real scenarios:

**Test Scenarios:**
1. New feature - "Add ARM64 support"
2. Bug fix - "Fix memory leak in pod inspector"
3. Refactor - "Implement LRU cache eviction"
4. Code review - "Review pod placement config"
5. Architecture - "Explain multi-arch scheduling"

**Success Criteria:** 80% pass, avg ≤2.5 hops, ≤120s, ≥80% confidence

### 4. `/ask` - Query Documentation

Query documentation with progressive disclosure (≤3 hops, ≤500 lines context):

**Examples:**
```bash
/ask what components exist? /path/to/repo
/ask how does the installer work? https://github.com/openshift/installer
/ask what is the reconciliation pattern? github.com/openshift/installer
/ask show me the architecture /path/to/openshift-installer
```

**Note**: Repository path or GitHub URL is **required**. The skill queries `<repo>/agentic/knowledge-graph/graph.json`.

## Development

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
pytest tests/ -v --cov=integrations --cov=utilities --cov-report=html
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Clean build artifacts
make clean
```

## Next Steps

- Read [README.md](README.md) for complete overview
- See [CLAUDE.md](CLAUDE.md) for skill usage guidance
- Check [WORKFLOW_EXPLAINED.md](WORKFLOW_EXPLAINED.md) for detailed workflow
- Review [CORE_SKILLS.md](CORE_SKILLS.md) for skill reference
- Explore [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) for architecture

## Troubleshooting

### "Skill not found"

Make sure skills are accessible to Claude Code. The skills are in the `skills/` directory.

### "Documentation not found"

Run `/create` first to generate documentation before using `/validate`, `/evaluate`, or `/ask`.

### Low quality score

Run `/validate` to see specific issues. Common problems:
- Stale documentation (update with `/create`)
- Missing files (regenerate with `/create`)
- Broken links (check file paths)

### Rate limit errors (GitHub)

Add a GitHub token to `.env` file for higher rate limits (5,000/hour vs 60).

## Support

- **Issues**: https://github.com/kenjpais/claude-agent-knowledge-skills/issues
- **Documentation**: See README.md and other docs in this repository
