# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains the **Agent Knowledge Framework** - a specification for automatically generating and maintaining agentic documentation for OpenShift codebases. The goal is to enable coding agents to:

- Navigate systems in three hops or less
- Understand architectural intent, not just code structure  
- Reuse patterns consistently
- Avoid violating invariants

**Current State**: The system is now implemented with complete agent definitions, skills, templates, and utilities.

## High-Level Architecture

The framework defines a five-layer system:

1. **Orchestration Layer** - Triggers and coordinates documentation generation
2. **Extraction Agents** - Mine raw repository data (API surfaces, dependency graphs, CRDs)
3. **Synthesis Agents** - Convert extracted data into domain concepts and component descriptions
4. **Skill Layer** - Atomic, composable capabilities (all intelligence expressed here; agents only coordinate)
5. **Validation Layer** - Enforce navigation depth, context budgets, and structural completeness

**Core Pipeline**: Raw Code → Extract Signals → Infer Meaning → Synthesize Documents → Link Knowledge → Validate → Store in `agentic/`

## Agent Roles

- **Orchestrator**: Triggers generation, assigns scopes, sequences agents
- **Extractor**: Mines repository data using parsing skills only (no interpretation)
- **Synthesizer**: Converts extracted data into concepts, workflows, and descriptions
- **Linker**: Creates navigable knowledge graph via cross-links and AGENTS.md
- **Validator**: Enforces framework constraints (≤3 hop navigation, context budget, completeness)
- **Curator**: Maintains freshness, updates docs on code changes, prunes stale knowledge

## Skill Design Principles

All skills must follow strict guidelines:

- **Single responsibility** - One clear purpose per skill
- **Clear input/output schema** - Explicit contracts
- **No hidden state** - Stateless and deterministic where possible
- **Small context footprint** - Aggressive chunking required

Skill categories include: repo access, parsing (extract structure), inference (derive meaning), synthesis (generate docs), linking (create navigation), validation (enforce quality), and OpenShift-specific skills.

## OpenShift-Specific Considerations

The framework is optimized for Kubernetes-heavy OpenShift codebases and requires specialized skills for:

- Parsing controller patterns and reconcile loops
- Extracting CRDs and mapping them to controllers
- Inferring operator lifecycles
- Detecting cluster configuration flows

## Repository Structure

```
claude-agent-knowledge-system-skills/
├── agents/                  # Agent definitions
│   ├── orchestrator/       # Coordinates documentation generation
│   ├── extractor/          # Mines repository data
│   ├── synthesizer/        # Generates documentation from data
│   ├── linker/             # Creates navigation structure
│   ├── validator/          # Validates quality and structure
│   ├── curator/            # Maintains documentation freshness
│   └── retrieval/          # Provides documentation access
├── skills/                 # Skill definitions (atomic capabilities)
│   ├── repo/              # Repository access (read, list, search, git)
│   ├── parsing/           # Extract structure (Go structs, CRDs, dependencies)
│   ├── inference/         # Derive meaning (boundaries, roles)
│   ├── synthesis/         # Generate docs (components, AGENTS.md)
│   ├── linking/           # Create navigation (cross-links)
│   ├── validation/        # Quality checks (depth, score)
│   ├── documentation/     # File operations (write, update)
│   ├── openshift/         # OpenShift-specific (controller patterns)
│   └── monitoring/        # Logging and tracking
├── skill-registry/        # Skill index and mappings
│   └── index.yaml
├── templates/             # Documentation templates
│   ├── agentic-structure/ # Templates for generated docs
│   └── exec-plans/        # Execution plan templates
├── utilities/             # Supporting utilities
│   ├── logging/           # Structured logging (logger.py)
│   └── validation/        # Quality validation (validator.py)
├── integrations/          # External integrations
│   ├── github/            # GitHub MCP server integration
│   ├── jira/              # JIRA MCP server integration
│   └── graphify/          # Graphify knowledge graph integration
└── agentic/               # Generated documentation (created when run)
```

## Implementation Guidance

When building components of this system:

- **Progressive disclosure**: Start with directory structure, then component extraction, then concept synthesis
- **Continuous update model**: Generate diffs on changes and update only affected documentation
- **Validation first**: Every output must pass navigation depth (≤3 hops) and context budget checks
- **Execution plans**: Document generation itself follows the framework - create execution plans in `agentic/exec-plans/active/`
- **Quality tracking**: Maintain `agentic/QUALITY_SCORE.md` with metrics on coverage and staleness

## 🚀 Quick Setup

**TL;DR**: Clone, run `./setup.sh`, and start generating docs!

```bash
git clone <repo>
cd claude-agent-knowledge-system-skills
./setup.sh
export GITHUB_TOKEN=ghp_xxx  # Optional
agentic-docs generate /path/to/openshift-repo
```

**See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed setup guide.**

---

## How to Use This System

### Prerequisites
- **Python 3.9+** (for utilities) - Required
- **Claude Code** - Required - Install from https://claude.ai/code
- **Node.js/npm** (for GitHub MCP) - Optional
- **GitHub Token** - Optional (for private repos and higher limits)
- **JIRA** - ✅ **No auth needed for public JIRA!**
- **Graphify** - Optional (for knowledge graphs)

### Automated Setup (Recommended)

```bash
# Run the setup script
./setup.sh

# This automatically:
# ✅ Installs Python dependencies
# ✅ Configures MCP servers
# ✅ Creates CLI commands
# ✅ Sets up environment
```

### Manual Setup (if needed)

1. **Install Python dependencies**:
```bash
pip install pyyaml
```

2. **Configure MCP servers**:
```bash
# GitHub MCP (optional)
mkdir -p ~/.claude
cat > ~/.claude/mcp_servers.json << 'EOF'
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_TOKEN": "${GITHUB_TOKEN}"}
    }
  }
}
EOF
```

3. **Set environment variables**:
```bash
# GitHub (optional - for private repos)
export GITHUB_TOKEN=ghp_your_token_here

# JIRA - NOT NEEDED for public JIRA (issues.redhat.com)!
# Only set these for private JIRA instances:
# export JIRA_URL=https://your-jira.com
# export JIRA_EMAIL=your-email@company.com
# export JIRA_API_TOKEN=your-token
```

### Running Documentation Generation

#### For a Target OpenShift Repository

1. **Full Documentation Generation**:
```bash
# Navigate to target OpenShift repository
cd /path/to/openshift-repository

# Invoke Claude Code with orchestrator agent
# The orchestrator will:
# - Discover repository structure
# - Run extractor agent on all components
# - Run synthesizer agent to create docs
# - Run linker agent to create navigation
# - Run validator agent to check quality

# Claude prompt:
"Run the orchestrator agent to generate complete agentic documentation for this OpenShift repository"
```

2. **Incremental Update** (after code changes):
```bash
# Claude prompt:
"Run the curator agent to update documentation for recently changed components"
```

3. **Validation Only**:
```bash
# Claude prompt:
"Run the validator agent to check documentation quality"
```

### Agent Usage

#### Orchestrator
**Purpose**: Coordinate entire documentation pipeline
**When to use**: Initial generation, full regeneration
**Skills used**: discovery, coordination, validation

#### Extractor  
**Purpose**: Extract raw data from code
**When to use**: Processing source files, extracting CRDs, building dependency graphs
**Skills used**: read-file, extract-go-structs, extract-kubernetes-crds, build-dependency-graph

#### Synthesizer
**Purpose**: Generate documentation from extracted data
**When to use**: After extraction, to create component and concept docs
**Skills used**: infer-component-boundary, classify-service-role, generate-component-doc

#### Linker
**Purpose**: Create navigation structure
**When to use**: After synthesis, to create AGENTS.md and cross-links
**Skills used**: link-concepts-to-components, generate-agents-md, check-navigation-depth

#### Validator
**Purpose**: Enforce quality constraints
**When to use**: After linking, to validate structure and quality
**Skills used**: check-navigation-depth, check-quality-score

#### Curator
**Purpose**: Maintain documentation over time
**When to use**: Continuous monitoring, detecting staleness
**Skills used**: get-git-history, check-quality-score

#### Retrieval
**Purpose**: Provide controlled access to documentation
**When to use**: When agents need to query documentation
**Skills used**: read-file, search-code (all queries logged)

### Skill Reference

All skills documented in `skills/` directory. Key skills:

**Repository Access**:
- `read-file` - Read file contents
- `list-files` - Discover files  
- `search-code` - Search for patterns
- `get-git-history` - Extract commit history

**Parsing** (deterministic extraction):
- `extract-go-structs` - Parse Go types
- `extract-kubernetes-crds` - Parse CRD definitions
- `build-dependency-graph` - Build import graph
- `parse-kubernetes-controller-pattern` - Extract controller structure

**Inference** (probabilistic, confidence-scored):
- `infer-component-boundary` - Detect component boundaries
- `classify-service-role` - Determine component role

**Synthesis** (generate docs):
- `generate-component-doc` - Create component documentation
- `generate-agents-md` - Create AGENTS.md entry point

**Validation** (quality enforcement):
- `check-navigation-depth` - Enforce ≤3 hop constraint
- `check-quality-score` - Calculate comprehensive metrics

**Documentation**:
- `write-agentic-file` - Write/update docs with validation

**Monitoring**:
- `log-operation` - Log all operations (mandatory)

### Validation and Quality

Quality score calculated from:
- **Coverage** (40 points): % of components documented
- **Freshness** (20 points): Docs updated within 90 days
- **Completeness** (20 points): Required files present
- **Linkage** (10 points): No broken links
- **Navigation** (10 points): ≤3 hop depth

**Pass threshold**: 70/100

### Templates

All documentation templates in `templates/agentic-structure/`:
- `AGENTS.md.template` - Primary entry point (≤150 lines)
- `DESIGN.md.template` - Design philosophy
- `DEVELOPMENT.md.template` - Development setup
- `TESTING.md.template` - Test strategy
- `RELIABILITY.md.template` - SLOs and observability
- `SECURITY.md.template` - Security model
- `QUALITY_SCORE.md.template` - Quality metrics
- `component.md.template` - Component docs (≤100 lines)
- `concept.md.template` - Domain concepts (≤75 lines)

### Utilities

**Logging** (`utilities/logging/logger.py`):
```python
from utilities.logging.logger import get_logger

logger = get_logger("agent-name")
logger.log_start("operation", "resource")
logger.log_success("operation", "resource", duration_ms=100)
```

**Validation** (`utilities/validation/validator.py`):
```python
from pathlib import Path
from utilities.validation.validator import NavigationDepthChecker, QualityScoreCalculator

# Check navigation depth
checker = NavigationDepthChecker(Path("AGENTS.md"), max_depth=3)
result = checker.check(Path("agentic/"))

# Calculate quality score
calculator = QualityScoreCalculator(Path("."), Path("agentic/"))
scores = calculator.calculate()
```

### Integration with External Systems

**GitHub**: Extract PRs, issues, commits
- See `integrations/github/GITHUB_MCP_INTEGRATION.md`

**JIRA**: Extract features, bugs, requirements  
- See `integrations/jira/JIRA_MCP_INTEGRATION.md`

**Graphify**: Generate knowledge graphs
- See `integrations/graphify/GRAPHIFY_SKILL.md`

## Anti-Patterns to Avoid

- Generating full documentation in one pass (use incremental generation)
- Embedding interpretation inside parsing skills (separate extraction from inference)
- Skipping the linking phase (navigation is critical)
- Producing narrative-heavy docs without structure (enforce templates)
- Ignoring OpenShift-specific patterns like operators and reconcile loops
- Skipping logging (all operations must be logged)
- Exceeding line budgets (AGENTS.md ≤150, components ≤100, concepts ≤75)
