# Agent Knowledge System for Claude Code

A **skill library** for Claude Code that enables automatic generation and maintenance of agentic documentation for OpenShift and Kubernetes repositories. This system enables AI agents to navigate codebases efficiently through progressive disclosure and structured knowledge.

## Overview

This repository contains **7 core skills** that work directly with **Claude Code**. Skills are organized into focused categories for documentation generation, validation, evaluation, and querying.

**Key Features:**
- ✅ **Ready to use** - Works directly in Claude Code
- ✅ **7 Core Skills** - `/create`, `/validate`, `/evaluate`, `/ask`, `/ingest-github-data`, `/generate-knowledge-graph`, `/retrieve-from-graph`
- ✅ **4 User-Facing Skills** - `/create`, `/validate`, `/evaluate`, `/ask`
- ✅ **Quality Enforcement** - ≤3 hop navigation, line budgets, coverage
- ✅ **OpenShift Optimized** - Kubernetes controllers, CRDs, operators
- ✅ **GitHub & JIRA Integration** - GitHub GraphQL API for data ingestion
- ✅ **Knowledge Graphs** - NetworkX-based graph generation and retrieval

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.9+
- Claude Code installed

### 2. Installation

```bash
# Clone repository
git clone https://github.com/kenjpais/claude-agent-knowledge-skills
cd claude-agent-knowledge-system-skills

# Install dependencies
make install

# Install development dependencies (optional, for testing)
make install-dev
```

### 3. Configuration (Optional)

For GitHub data ingestion with higher rate limits:

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your GitHub token
# GH_API_TOKEN=ghp_your_token_here
```

### 4. Use Skills in Claude Code

Open Claude Code and use the core skills:

```bash
# In Claude Code
/create                    # Generate agentic documentation
/validate                  # Validate documentation quality
/evaluate                  # Test with coding agent simulation
/ask what components exist? <repo-path>  # Query documentation (requires repo path/URL)
```

---

## 🎯 Core Skills

### `/create` - Generate Documentation

**What it does**: Generates complete agentic documentation for a repository

**How to use**:
```bash
# In Claude Code
/create                                                    # Current directory
/create /path/to/openshift-installer                     # Local repository path
/create https://github.com/openshift/installer           # GitHub URL (auto-clones)
```

**What happens**:
1. **Extraction** - Discovers structure, parses Go/CRDs, builds dependency graph
2. **Synthesis** - Infers components, generates component/concept docs
3. **Linking** - Creates AGENTS.md, cross-links all documentation
4. **Validation** - Checks ≤3 hop navigation, line budgets, quality score

**Output**:
```
repository/
├── AGENTS.md                    # Entry point (≤150 lines)
└── agentic/
    ├── design-docs/components/  # Component docs (≤100 lines each)
    ├── domain/concepts/         # Domain concepts (≤75 lines each)
    └── QUALITY_SCORE.md
```

**Duration**: ~2-3 minutes for typical OpenShift repository

### `/validate` - Validate Quality

**What it does**: Validates existing agentic documentation

**How to use**:
```bash
# In Claude Code
/validate                                                  # Current directory
/validate /path/to/openshift-installer                   # Local repository path
/validate https://github.com/openshift/installer         # GitHub URL (auto-clones)
```

**Checks**:
- ✅ Structure (AGENTS.md exists, required files present)
- ✅ Navigation depth (≤3 hops from AGENTS.md)
- ✅ Line budgets (AGENTS.md ≤150, components ≤100, concepts ≤75)
- ✅ Broken links (all cross-references valid)
- ✅ Coverage (≥80% components documented)
- ✅ Freshness (updated within 90 days)
- ✅ Quality score (≥70/100 to pass)

### `/evaluate` - Test with Coding Agent

**What it does**: Spawns a coding sub-agent to test documentation quality

**How to use**:
```bash
# In Claude Code
/evaluate                                                  # Current directory
/evaluate /path/to/openshift-installer                   # Local repository path
/evaluate https://github.com/openshift/installer         # GitHub URL (auto-clones)
```

**Test scenarios** (5 total):
1. New feature - "Add ARM64 support"
2. Bug fix - "Fix memory leak in pod inspector"
3. Refactor - "Implement LRU cache eviction"
4. Code review - "Review pod placement config"
5. Architecture - "Explain multi-arch scheduling"

**Metrics tracked**:
- Hops (navigation depth)
- Time (query response time)
- Confidence (agent's confidence level)
- Retrieval quality

**Success criteria**: 80% scenarios pass, avg ≤2.5 hops, ≤120s, ≥80% confidence

### `/ask` - Query Documentation

**What it does**: Query agentic documentation with ≤3 hop navigation

**How to use**:
```bash
# In Claude Code - repository path/URL is REQUIRED
/ask what components exist? /path/to/openshift-installer              # Local repository
/ask how does the installer work? https://github.com/openshift/installer  # GitHub URL (auto-clones)
/ask what is reconciliation? github.com/openshift/installer            # GitHub URL (auto-clones)
```

**Query types**:
- Component discovery
- Component details
- Concept lookup
- Architecture overview
- Development guidance
- Relationship queries

**Note**: Repository path or GitHub URL is **required** - the skill queries the knowledge graph at `<repo>/agentic/knowledge-graph/graph.json`

---

## 📖 How It Works

### Skill-Driven Architecture

**Core principle**: All intelligence is expressed through composable skills. Claude Code loads and executes skills.

```
User types: /create
    ↓
Claude Code loads skill: skills/create-agentic-docs/SKILL.md
    ↓
Claude executes workflow defined in skill
    ↓
Output: Complete agentic documentation
```

### The 7 Core Skills

**User-Invocable Skills** (4):
- `/create` - `create-agentic-docs` - Generate complete agentic documentation
- `/validate` - `validate-agentic-docs` - Validate documentation quality
- `/evaluate` - `evaluate-agentic-docs` - Test with coding agent simulation
- `/ask` - `ask-agentic-docs` - Query documentation

**Data & Knowledge Graph Skills** (3):
- `ingest-github-data` - Fetch GitHub PRs/issues and JIRA references via GraphQL API
- `generate-knowledge-graph` - Create NetworkX-based knowledge graph from docs + database
- `retrieve-from-graph` - Graph-based retrieval with ≤3 hop navigation

**See**: `skill-registry/index.yaml` for complete skill catalog

---

## 🛠️ System Architecture

### Directory Structure

```
claude-agent-knowledge-system-skills/
├── skills/                      # Core skill definitions
│   ├── create-agentic-docs/    # /create skill
│   ├── validate-agentic-docs/  # /validate skill
│   ├── evaluate-agentic-docs/  # /evaluate skill
│   ├── ask-agentic-docs/       # /ask skill
│   ├── ingest-github-data/     # GitHub + JIRA data ingestion
│   ├── generate-knowledge-graph/ # Knowledge graph generation
│   ├── retrieve-from-graph/    # Graph-based retrieval
│   ├── documentation/          # Documentation utilities
│   ├── inference/              # Component inference
│   ├── linking/                # Cross-linking
│   ├── monitoring/             # Operation logging
│   ├── openshift/              # OpenShift-specific patterns
│   ├── parsing/                # Code parsing
│   ├── repo/                   # Repository access
│   ├── synthesis/              # Doc generation
│   └── validation/             # Quality validation
├── templates/                  # Documentation templates
│   └── agentic-structure/
├── skill-registry/             # Skill index
│   └── index.yaml
├── integrations/               # External integrations
│   ├── storage/                # GitHub/JIRA SQLite storage
│   └── graphify/               # Graphify tool integration
├── tests/                      # Test suite
│   ├── unit/
│   └── integration/
└── Makefile                    # Build and development commands
```

### Quality Guarantees

**Navigation Constraint**:
- ✅ Any information reachable in ≤3 hops from AGENTS.md
- ✅ No orphaned documents

**Context Budget**:
- ✅ AGENTS.md ≤150 lines
- ✅ Component docs ≤100 lines each
- ✅ Concept docs ≤75 lines each
- ✅ Total query context ≤500 lines

**Quality Score** (0-100):
- Coverage: 40 points (≥80% components documented)
- Freshness: 20 points (updated <90 days)
- Completeness: 20 points (all required files)
- Linkage: 10 points (no broken links)
- Navigation: 10 points (≤3 hop depth)
- **Pass threshold**: ≥70/100

---

## 📚 Documentation

### User Guides
- **[WORKFLOW_EXPLAINED.md](WORKFLOW_EXPLAINED.md)** - Complete workflow explanation
- **[CORE_SKILLS.md](CORE_SKILLS.md)** - Detailed skill reference
- **[USAGE.md](USAGE.md)** - Usage examples

### Architecture
- **[AGENT_KNOWLEDGE_FRAMEWORK.md](AGENT_KNOWLEDGE_FRAMEWORK.md)** - System design
- **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** - Complete system reference
- **[CLAUDE.md](CLAUDE.md)** - Claude Code guidance

### Development
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute
- **[DEPENDENCY_MANAGEMENT.md](DEPENDENCY_MANAGEMENT.md)** - Dependencies

### Integration
- **[integrations/storage/README.md](integrations/storage/README.md)** - GitHub/JIRA ingestion
- **[integrations/graphify/README.md](integrations/graphify/README.md)** - Knowledge graphs

---

## 🔧 Optional Configuration

### GitHub Token (Optional)

For higher API rate limits when ingesting GitHub data:

```bash
# Copy template
cp .env.example .env

# Add your GitHub token
echo "GH_API_TOKEN=ghp_your_token" >> .env
```

**Benefits**:
- 5,000 requests/hour (vs 60 without token)
- Access to private repositories

**Get token**: https://github.com/settings/tokens (scopes: `repo`, `read:org`)

### JIRA Access (Optional)

For private JIRA instances, add credentials to `.env`:

```bash
JIRA_URL=https://your-jira.com
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-token
```

Public JIRA (issues.redhat.com) requires no authentication.

---

## 💡 Example Session

```bash
# 1. Clone this repository
git clone <this-repo>
cd claude-agent-knowledge-system-skills

# 2. Open Claude Code in target repository
cd /path/to/openshift-installer

# 3. Use skills in Claude Code
# Type in Claude Code:
/create

# Claude generates documentation automatically:
# ✅ AGENTS.md created (142 lines)
# ✅ 5 component docs generated (avg 87 lines)
# ✅ 3 concept docs generated (avg 62 lines)
# ✅ Navigation depth: 3 hops
# ✅ Quality score: 90/100

# 4. Validate
/validate
# ✅ All checks passed
# ✅ Quality score: 90/100

# 5. Query
/ask how does the installer work?
# Returns: Purpose, responsibilities, dependencies, workflow
# Navigation path: AGENTS.md → Components → Installer (2 hops)

# 6. Evaluate
/evaluate
# ✅ 4/5 scenarios passed
# ✅ Average hops: 2.4
# ✅ Average time: 98.5s
# ✅ Average confidence: 82%
```

---

## 🎓 Key Concepts

### Progressive Disclosure

Information organized in layers:
- **Hop 0**: AGENTS.md (high-level overview)
- **Hop 1**: Component/concept lists
- **Hop 2**: Detailed documentation
- **Hop 3**: Implementation details

### Skill-Driven Architecture

All intelligence is expressed through composable skills:
```
User invokes skill → /create
                      ↓
Claude Code loads skill definition
                      ↓
Skill specifies workflow & constraints
                      ↓
Claude executes workflow
                      ↓
Output: Documentation + validation
```

### Quality-First Approach

Every output validated:
- Navigation depth checked (≤3 hops)
- Line budgets enforced (AGENTS.md ≤150, components ≤100, concepts ≤75)
- Quality score calculated (≥70/100 to pass)
- Broken links detected (0 broken links required)

---

## 🛠️ Development

### Building and Testing

```bash
# Format code
make format

# Run linters
make lint

# Run tests
make test

# Clean build artifacts
make clean
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_database.py -v

# Run with coverage
pytest tests/ -v --cov=integrations --cov=utilities --cov-report=html
```

---

## 🆘 Troubleshooting

### "Skill not found"

Make sure you're in the skills directory or Claude Code can access the skills:
```bash
# Check you're in the right directory
pwd  # Should show claude-agent-knowledge-system-skills

# Or reference skills explicitly
/create using skills/create-agentic-docs/SKILL.md
```

### "Documentation not found"

Run `/create` first to generate documentation:
```bash
/create
# Then you can use /validate, /evaluate, /ask
```

### Low quality score

Check specific issues:
```bash
/validate
# See which checks failed
# Common issues: stale docs, missing files, broken links
```

---

## 🤝 Contributing

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for guidelines.

**Adding new skills**:
1. Create `skills/category/skill-name/SKILL.md`
2. Add frontmatter with metadata
3. Document skill thoroughly
4. Add to `skill-registry/index.yaml`
5. Test with Claude Code

---

## 📄 License

See LICENSE file for details.

---

## 🔗 Links

- **Claude Code**: https://claude.ai/code
- **Agent Knowledge Framework**: See AGENT_KNOWLEDGE_FRAMEWORK.md
- **Skill Reference**: See CORE_SKILLS.md
- **Issues**: https://github.com/kenjpais/claude-agent-knowledge-skills/issues

---

**Ready to use** | **Skill-driven** | **Quality-first** | **OpenShift optimized**
