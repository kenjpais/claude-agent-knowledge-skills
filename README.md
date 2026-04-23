# Agent Knowledge System for OpenShift Documentation

An agent-based system for automatically generating and maintaining agentic documentation for Red Hat OpenShift repositories. This system enables AI coding assistants to navigate codebases efficiently through progressive disclosure and structured knowledge.

## Overview

This repository implements a complete framework for:
- **Extracting** structured data from OpenShift repositories (CRDs, controllers, dependencies)
- **Synthesizing** human and agent-readable documentation from extracted data
- **Linking** documentation into a navigable knowledge graph (≤3 hops from entry point)
- **Validating** documentation quality and enforcing structural constraints
- **Maintaining** documentation freshness through continuous monitoring

## Key Features

✅ **7 Specialized Agents** - Orchestrator, Extractor, Synthesizer, Linker, Validator, Curator, Retrieval  
✅ **20+ Skills** - Atomic, composable capabilities across repo access, parsing, inference, synthesis, linking, and validation  
✅ **Quality Enforcement** - Automatic validation of navigation depth (≤3 hops), line budgets, and coverage  
✅ **OpenShift Optimized** - Specialized skills for Kubernetes controllers, CRDs, operators, and reconcile loops  
✅ **GitHub & JIRA Integration** - Extract architectural context from PRs, issues, and requirements  
✅ **Knowledge Graphs** - Integration with graphify for enhanced navigation and querying  
✅ **Comprehensive Logging** - All operations logged for auditing and debugging  
✅ **Template-Based** - Structured templates for AGENTS.md, component docs, concept docs, and required files

## 🚀 Quick Start (5 Minutes!)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/claude-agent-knowledge-system-skills.git
cd claude-agent-knowledge-system-skills

# Run automated setup
./setup.sh
```

### 2. Set GitHub Token (Optional)

```bash
# For higher rate limits and private repos
export GITHUB_TOKEN=ghp_your_token_here
```

### 3. Generate Documentation

```bash
# Generate for any OpenShift repository
agentic-docs generate /path/to/openshift-installer

# That's it! ✅
```

**See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed instructions.**

---

## 📖 Learn More

### Architecture Documentation
- `AGENT_KNOWLEDGE_FRAMEWORK.md` - System architecture and design
- `CLAUDE.md` - Implementation guide and usage instructions
- `GOAL.md` - Project objectives and requirements
- `GETTING_STARTED.md` - **⭐ Start here for setup**

### Agent Definitions
Each agent has a detailed definition in `agents/{agent-name}/AGENT.md`:
- **Orchestrator** - Coordinates the documentation pipeline
- **Extractor** - Mines repository data deterministically  
- **Synthesizer** - Generates documentation from extracted data
- **Linker** - Creates navigation structure
- **Validator** - Enforces quality constraints
- **Curator** - Maintains documentation freshness
- **Retrieval** - Provides controlled documentation access

### 3. Browse Skills
Skills are organized by category in `skills/`:
- `repo/` - Repository access (read, list, search, git history)
- `parsing/` - Extraction (Go structs, CRDs, dependencies, controllers)
- `inference/` - Analysis (component boundaries, service roles)
- `synthesis/` - Generation (component docs, AGENTS.md)
- `linking/` - Navigation (cross-links, concept mapping)
- `validation/` - Quality (navigation depth, quality score)
- `documentation/` - File operations (write with validation)
- `openshift/` - OpenShift-specific patterns
- `monitoring/` - Logging and tracking

### 4. Use the System

To generate documentation for an OpenShift repository:

```bash
# Navigate to target repository
cd /path/to/openshift/repository

# Use Claude Code to invoke the orchestrator
# Claude prompt: "Run the orchestrator agent to generate agentic documentation"
```

The system will:
1. Extract all components, CRDs, and dependencies
2. Synthesize documentation following templates
3. Link documentation into navigable structure
4. Validate quality and enforce constraints
5. Output to `agentic/` directory

## Directory Structure

```
claude-agent-knowledge-system-skills/
├── agents/                  # Agent definitions (7 agents)
├── skills/                  # Skill definitions (20+ skills)
├── skill-registry/          # Skill index and mappings
├── templates/               # Documentation templates
│   ├── agentic-structure/  # Output templates
│   └── exec-plans/         # Execution plan templates
├── utilities/               # Supporting utilities
│   ├── logging/            # Structured logging
│   └── validation/         # Quality validation
├── integrations/            # External integrations
│   ├── github/             # GitHub MCP integration
│   ├── jira/               # JIRA MCP integration
│   └── graphify/           # Knowledge graph integration
├── AGENT_KNOWLEDGE_FRAMEWORK.md  # Architecture specification
├── GOAL.md                       # Project objectives
├── CLAUDE.md                     # Implementation guide
└── README.md                     # This file
```

## Generated Documentation Structure

When run on a target repository, the system generates:

```
target-repository/
├── AGENTS.md                    # Primary entry point (≤150 lines)
└── agentic/
    ├── DESIGN.md               # Design philosophy
    ├── DEVELOPMENT.md          # Dev setup
    ├── TESTING.md              # Test strategy
    ├── RELIABILITY.md          # SLOs and observability
    ├── SECURITY.md             # Security model
    ├── QUALITY_SCORE.md        # Quality metrics
    ├── design-docs/
    │   ├── components/         # Component documentation (≤100 lines each)
    │   └── core-beliefs.md
    ├── domain/
    │   ├── concepts/           # Domain concepts (≤75 lines each)
    │   └── workflows/          # Workflow documentation
    ├── decisions/              # Architecture Decision Records
    └── exec-plans/             # Execution tracking
        ├── active/
        └── completed/
```

## Quality Metrics

Documentation quality is scored across 5 dimensions:
- **Coverage** (40 points): % of components documented
- **Freshness** (20 points): Docs updated within 90 days  
- **Completeness** (20 points): Required files present
- **Linkage** (10 points): No broken links
- **Navigation** (10 points): All docs reachable in ≤3 hops

**Pass threshold**: 70/100

## Key Constraints

The system enforces strict constraints for agent-optimized documentation:

| Constraint | Requirement | Validation |
|------------|-------------|------------|
| **Navigation Depth** | ≤3 hops from AGENTS.md | Automatic validation |
| **AGENTS.md Length** | ≤150 lines | Line count check |
| **Component Doc Length** | ≤100 lines | Line count check |
| **Concept Doc Length** | ≤75 lines | Line count check |
| **Required Files** | 7 files (AGENTS.md + 6 in agentic/) | File existence check |
| **Broken Links** | 0 broken links | Link validation |

## Integration Points

### GitHub & JIRA Data Storage ⭐
Efficient single-repository ingestion using GitHub GraphQL API with date range filtering:
- **GitHub**: PRs and issues within specified date range (default: past year)
- **JIRA**: Automatic extraction and correlation of JIRA references
- **Storage**: Local SQLite database for fast queries
- **Date Filtering**: Flexible date ranges (YYYY-MM-DD or "N-days-ago")

**Quick Usage**:
```bash
# Ingest last year of data (default)
python integrations/storage/ingest.py openshift/installer --jira OCPCLOUD

# Ingest specific date range
python integrations/storage/ingest.py openshift/installer \
  --since 2024-01-01 \
  --until 2024-12-31

# Ingest last 90 days
python integrations/storage/ingest.py openshift/installer \
  --since 90-days-ago
```

**Benefits**:
- ✅ 50-100x fewer API requests vs REST (uses GraphQL)
- ✅ Date range filtering for targeted analysis
- ✅ Automatic GitHub ↔ JIRA correlation
- ✅ Local SQLite storage (~10MB per repo)

**See**: `integrations/storage/README.md` for complete documentation

### GitHub MCP Server ✅
Extract architectural context from:
- Pull request descriptions and reviews
- Commit messages and history
- Issue discussions
- Code review comments

**Setup**: Automatic via `./setup.sh`  
**Auth**: Optional (GITHUB_TOKEN for private repos)

See `integrations/github/GITHUB_MCP_INTEGRATION.md`

### JIRA - Simplified! 🎉
Extract product context from:
- Feature requirements and acceptance criteria
- Bug patterns and trends
- Epic descriptions
- Sprint planning

**Setup**: ✅ **No setup needed for public JIRA!**  
**Auth**: ❌ **Not required for issues.redhat.com and other public instances**  
**Private JIRA**: Optional authentication (see guide)

See `integrations/jira/SIMPLIFIED_SETUP.md`

### Graphify
Generate knowledge graphs for:
- Community detection (component boundaries)
- Concept extraction
- Relationship mapping
- Query-based navigation

See `integrations/graphify/GRAPHIFY_SKILL.md`

## Utilities

### Logging
All operations are logged with structured metadata:
```python
from utilities.logging.logger import get_logger

logger = get_logger("agent-name")
logger.log_start("operation", "resource")
logger.log_success("operation", "resource", duration_ms=100)
```

### Validation
Quality validation utilities:
```python
from utilities.validation.validator import QualityScoreCalculator

calculator = QualityScoreCalculator(repo_path, agentic_dir)
scores = calculator.calculate()
```

## Design Principles

1. **Progressive Disclosure** - Navigate hierarchically, load minimal context
2. **Skill-Based Intelligence** - All intelligence in skills, agents only coordinate
3. **Deterministic Extraction** - Parsing is deterministic, inference is confidence-scored
4. **Template Enforcement** - All docs follow strict templates with line budgets
5. **Validation First** - All outputs validated before considered complete
6. **Continuous Maintenance** - Documentation stays fresh through curator agent

## References

- **Agentic Docs Framework**: https://github.com/Prashanth684/agentic-docs-guide
- **Agent Skills Pattern**: https://github.com/addyosmani/agent-skills
- **Graphify**: https://github.com/safishamsi/graphify
- **Claude Skills Guide**: https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf

## License

[Specify license]

## Contributing

[Contribution guidelines if applicable]

## Authors

Built following GOAL.md requirements for automated agentic documentation generation for OpenShift repositories.
