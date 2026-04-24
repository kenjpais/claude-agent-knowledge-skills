# Agent Knowledge System - Complete Overview

## What is this?

A **fully automated system** for generating, validating, and maintaining agentic documentation for OpenShift codebases. The system uses Claude API to execute complex workflows automatically - no manual work required.

## Key Innovation

**All intelligence is expressed through composable skills. Agents only coordinate.**

This means:
- ✅ Skills are atomic, reusable capabilities
- ✅ Agents orchestrate skill execution
- ✅ Workflows are skill-driven, not imperative code
- ✅ System is extensible by adding skills

## Full Automation Flow

```
User runs: agentic /create <repo>
         ↓
CLI parses command and prepares context
         ↓
ClaudeOrchestrator loads skills and calls Claude API
         ↓
Claude API executes 5-phase workflow:
  1. Ingest GitHub/JIRA data
  2. Extract code structure
  3. Generate documentation
  4. Create knowledge graph
  5. Validate quality
         ↓
Results returned: docs + graph + metrics
```

## Architecture

### 1. Core Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **CLI** | `./agentic` | Parse commands, invoke orchestrator |
| **Orchestrator** | `lib/claude_orchestrator.py` | Load skills, call Claude API, track metrics |
| **Skills** | `skills/` | Atomic capabilities (40+ skills) |
| **Agents** | `agents/` | Coordinate skill execution (7 agents) |
| **Templates** | `templates/` | Documentation structure |
| **Storage** | `integrations/storage/` | GitHub/JIRA data ingestion |
| **Graphify** | `integrations/graphify/` | Knowledge graph integration |

### 2. The Seven Agents

| Agent | Purpose | Key Skills |
|-------|---------|------------|
| **Orchestrator** | Coordinate entire pipeline | discovery, coordination, validation |
| **Extractor** | Mine repository data | read-file, extract-go-structs, extract-kubernetes-crds |
| **Synthesizer** | Generate documentation | infer-component-boundary, generate-component-doc |
| **Linker** | Create navigation | link-concepts-to-components, generate-agents-md |
| **Validator** | Enforce quality | check-navigation-depth, check-quality-score |
| **Curator** | Maintain freshness | get-git-history, detect staleness |
| **Retrieval** | Provide access | read-file, retrieve-from-graph |
| **Evaluator** | Test quality | evaluate-agentic-docs, spawn sub-agents |

### 3. Skill Categories

**40+ skills organized by category:**

- **Core** (4 skills): `/create`, `/validate`, `/evaluate`, `/ask`
- **Repository** (4 skills): read-file, list-files, search-code, get-git-history
- **Parsing** (4 skills): extract-go-structs, extract-kubernetes-crds, build-dependency-graph, parse-kubernetes-controller-pattern
- **Inference** (2 skills): infer-component-boundary, classify-service-role
- **Synthesis** (2 skills): generate-component-doc, generate-agents-md
- **Linking** (1 skill): link-concepts-to-components
- **Validation** (2 skills): check-navigation-depth, check-quality-score
- **Documentation** (1 skill): write-agentic-file
- **Data Ingestion** (1 skill): ingest-github-data
- **Knowledge Graph** (2 skills): generate-knowledge-graph, retrieve-from-graph
- **Evaluation** (1 skill): evaluate-agentic-docs
- **Monitoring** (1 skill): log-operation

## Four Core Commands

### 1. `/create` - Generate Documentation (Automated)

**Command**: `agentic /create <repository>`

**What happens automatically**:

```
Phase 1: Data Ingestion
└─ Fetch GitHub PRs, issues (last year)
└─ Extract JIRA references
└─ Store in SQLite: ~/.agent-knowledge/data.db

Phase 2: Code Extraction
└─ Discover repository structure
└─ Parse Go structs, Kubernetes CRDs
└─ Build dependency graph
└─ Identify controllers

Phase 3: Documentation Synthesis
└─ Infer component boundaries
└─ Classify component roles
└─ Generate component docs (≤100 lines each)
└─ Generate AGENTS.md (≤150 lines)
└─ Create cross-links

Phase 4: Knowledge Graph
└─ Combine docs + database → graph
└─ Create nodes: components, concepts, PRs, issues
└─ Create relationships: depends_on, implements, references
└─ Store: ~/.agent-knowledge/graphs/<repo>-graph.graphml

Phase 5: Validation
└─ Check navigation depth (≤3 hops)
└─ Calculate quality score (target ≥70/100)
└─ Generate quality report
```

**Output**:
- `repo/AGENTS.md` - Entry point
- `repo/agentic/` - Documentation directory
- `~/.agent-knowledge/data.db` - GitHub/JIRA data
- `~/.agent-knowledge/graphs/` - Knowledge graph

**Constraints enforced**:
- ✅ AGENTS.md ≤150 lines
- ✅ Component docs ≤100 lines
- ✅ Concept docs ≤75 lines
- ✅ Navigation depth ≤3 hops
- ✅ Quality score ≥70/100

### 2. `/validate` - Validate Quality (Automated)

**Command**: `agentic /validate <repository>`

**What happens automatically**:

```
8 Validation Checks:
1. Structure Check
   └─ AGENTS.md exists
   └─ Required files present (DESIGN, DEVELOPMENT, TESTING, etc.)
   └─ Proper directory structure

2. Navigation Check
   └─ All docs reachable in ≤3 hops from AGENTS.md
   └─ No orphaned documents

3. Line Budget Check
   └─ AGENTS.md ≤150 lines
   └─ Component docs ≤100 lines
   └─ Concept docs ≤75 lines

4. Link Check
   └─ No broken internal links
   └─ All cross-references valid

5. Coverage Check
   └─ ≥80% components documented
   └─ Major features covered

6. Freshness Check
   └─ Docs updated within 90 days
   └─ No stale components

7. Completeness Check
   └─ All required sections present
   └─ Key invariants documented

8. Quality Score
   └─ Coverage: 40 points
   └─ Freshness: 20 points
   └─ Completeness: 20 points
   └─ Linkage: 10 points
   └─ Navigation: 10 points
```

**Output**:
```json
{
  "overall_score": 85,
  "passed": true,
  "checks": {
    "structure": "PASS",
    "navigation": "PASS",
    "line_budgets": "PASS",
    "links": "PASS",
    "coverage": "PASS",
    "freshness": "PASS",
    "completeness": "PASS",
    "quality": "PASS"
  },
  "issues": [],
  "recommendations": [
    "Update stale component X",
    "Add workflow diagram for Y"
  ]
}
```

### 3. `/evaluate` - Test with Coding Agent (Automated)

**Command**: `agentic /evaluate <repository>`

**What happens automatically**:

```
Main Claude Agent spawns Coding Sub-Agent for 5 scenarios:

Scenario 1: New Feature
└─ Task: "Add support for ARM64 architecture scheduling"
└─ Sub-agent uses ask-agentic-docs ONLY (no code access)
└─ Measures: hops, time, confidence, navigation path
└─ Success: ≤3 hops, <120s, ≥80% confidence

Scenario 2: Bug Fix
└─ Task: "Fix memory leak in pod inspector component"
└─ Success: ≤2 hops, <90s, ≥90% confidence

Scenario 3: Refactor
└─ Task: "Refactor image cache to use LRU eviction"
└─ Success: ≤3 hops, <120s, ≥75% confidence

Scenario 4: Code Review
└─ Task: "Review changes to cluster pod placement config"
└─ Success: ≤2 hops, <90s, ≥85% confidence

Scenario 5: Architecture
└─ Task: "Explain how multi-arch scheduling works"
└─ Success: ≤3 hops, <120s, ≥90% confidence

Evaluation:
└─ Aggregate metrics across all scenarios
└─ Compare against success criteria
└─ Generate recommendations
```

**Success Criteria**:
- ✅ 80% scenarios pass (4/5)
- ✅ Average hops ≤2.5
- ✅ Average time ≤120 seconds
- ✅ Average confidence ≥80%

**Output**:
```json
{
  "overall_score": 85,
  "scenarios_passed": 4,
  "scenarios_failed": 1,
  "aggregate_metrics": {
    "average_hops": 2.4,
    "average_time": 98.5,
    "average_confidence": 82
  },
  "recommendations": [
    "Add workflow diagram for scheduling",
    "Improve image cache documentation",
    "Create concept doc for LRU eviction"
  ]
}
```

### 4. `/ask` - Query Documentation

**Command**: `agentic /ask <question>`

**What happens**:

```
1. Parse question (identify query type)
2. Use retrieve-from-graph skill
3. Navigate knowledge graph (≤3 hops)
4. Return answer + context (≤500 lines)
5. Provide related links
```

**Query Types**:
- Component discovery: "what components exist?"
- Component details: "how does the installer work?"
- Concept lookup: "what is the reconciliation pattern?"
- Architecture: "show me the architecture"
- Development: "how do I run tests?"
- Relationships: "what depends on component X?"

**Example**:
```bash
$ agentic /ask how does the installer work?

## How the Installer Works

**Purpose**: Orchestrates OpenShift cluster installation

**Key Responsibilities**:
1. Validates install configuration
2. Generates cluster assets
3. Provisions infrastructure
4. Bootstraps control plane

**Dependencies**:
- Asset Generator
- Terraform Provider
- Validator

**Related**:
- [Bootstrap Component](./bootstrap.md)
- [Installation Workflow](../workflows/installation.md)

**Next Steps**:
- /ask explain the bootstrap process
```

## Knowledge Graph Integration

### Graph Structure

**Nodes** (247 total in example):
- **Components** (45): Installer, Asset Generator, Bootstrap, etc.
- **Concepts** (12): Reconciliation Pattern, Controller Pattern, etc.
- **PRs** (87): Recent pull requests with changes
- **Issues** (95): GitHub issues
- **JIRA** (8): Linked JIRA tickets

**Relationships** (412 total):
- **depends_on** (78): Component dependencies
- **implements** (45): Components implementing concepts
- **references** (182): PRs/issues affecting components
- **links_to** (89): Documentation cross-links
- **mentioned_in** (18): JIRA mentions

### Graph Querying

**Progressive Disclosure**:
- Start from AGENTS.md (hop 0)
- Expand to immediate neighbors (hop 1)
- Continue if needed (hop 2, 3)
- Never exceed 3 hops or 500 lines context

**Relevance Scoring** (0.0-1.0):
- Query match: 40%
- Proximity: 30% (fewer hops = higher)
- Centrality: 20% (hub nodes rank higher)
- Freshness: 10% (recent changes rank higher)

## Technology Stack

### Required
- **Python 3.9+** - Core system
- **Claude API** (Sonnet 4) - Automation engine
- **PyYAML** - Skill definitions
- **python-dotenv** - Configuration
- **anthropic** - Claude API client

### Optional
- **GitHub Token** - Higher rate limits (5000/hour vs 60)
- **JIRA Access** - Private JIRA instances (public JIRA works without auth)

### Data Storage
- **SQLite** - GitHub/JIRA data (`~/.agent-knowledge/data.db`)
- **GraphML** - Knowledge graphs (`~/.agent-knowledge/graphs/`)
- **Markdown** - Documentation (`repo/agentic/`)

## Setup (3 Minutes)

```bash
# 1. Clone
git clone <repo>
cd claude-agent-knowledge-system-skills

# 2. Install
./setup.sh

# 3. Configure
cp .env.example .env
# Edit .env:
#   ANTHROPIC_API_KEY=sk-ant-xxx  # Required
#   GH_API_TOKEN=ghp_xxx          # Optional

# 4. Use
agentic /create https://github.com/openshift/installer
```

## Metrics & Monitoring

### Tracked Automatically

**Per Workflow**:
- Duration (seconds)
- API calls count
- Tokens (input/output)
- Skills loaded
- Errors encountered

**Per Evaluation**:
- Scenarios passed/failed
- Average hops
- Average time
- Average confidence
- Navigation paths

### Example Output

```
✅ Workflow Complete
========================================

📊 Metrics:
   Duration: 125.3s
   API calls: 8
   Tokens: 45,231 in, 12,450 out
   Skills loaded: 14

📂 Output:
   /repo/AGENTS.md
   /repo/agentic/
   ~/.agent-knowledge/data.db
   ~/.agent-knowledge/graphs/installer-graph.graphml

💡 Next steps:
   agentic /validate /repo
   agentic /evaluate /repo
```

## Quality Guarantees

### Navigation Constraint
- ✅ Any information reachable in ≤3 hops from AGENTS.md
- ✅ No orphaned documents
- ✅ Clear navigation paths

### Context Budget
- ✅ AGENTS.md ≤150 lines (entry point)
- ✅ Component docs ≤100 lines each
- ✅ Concept docs ≤75 lines each
- ✅ Total context per query ≤500 lines

### Quality Score
- ✅ Coverage ≥80% (40 points)
- ✅ Freshness <90 days (20 points)
- ✅ Completeness 100% (20 points)
- ✅ Linkage no broken links (10 points)
- ✅ Navigation ≤3 hops (10 points)
- ✅ **Total ≥70/100 to pass**

## Extension Points

### Adding Skills

1. Create `skills/category/skill-name/SKILL.md`
2. Add frontmatter with schema
3. Document skill thoroughly
4. Add to `skill-registry/index.yaml`
5. Skill auto-loaded on next run

### Adding Agents

1. Create `agents/agent-name/AGENT.md`
2. Define role and skills used
3. Add to orchestrator workflow
4. Update agent skill mappings

### Adding Workflows

1. Add workflow type to orchestrator
2. Define skill loading
3. Define workflow message
4. Add CLI command

## Use Cases

### 1. Onboarding New Engineers
```bash
# New engineer exploring codebase
cd /path/to/openshift-repo
agentic /ask what components exist?
agentic /ask how does the installer work?
agentic /ask what is the reconciliation pattern?
```

### 2. Code Reviews
```bash
# Reviewer needs context
agentic /ask what depends on component X?
agentic /ask show me the architecture
```

### 3. Bug Fixes
```bash
# Developer debugging memory leak
agentic /ask how does pod inspector work?
agentic /ask what uses memory in pod inspector?
```

### 4. Architecture Understanding
```bash
# Tech lead planning changes
agentic /ask explain multi-arch scheduling
agentic /ask what are the main workflows?
```

### 5. Continuous Documentation
```bash
# After code changes
agentic /create .
agentic /validate .
agentic /evaluate .
```

## Documentation

### User Guides
- **[README.md](README.md)** - Quick start
- **[USAGE.md](USAGE.md)** - Detailed usage
- **[AUTOMATION.md](AUTOMATION.md)** - Automation architecture
- **[CORE_SKILLS.md](CORE_SKILLS.md)** - Skill reference
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Setup guide

### Architecture
- **[AGENT_KNOWLEDGE_FRAMEWORK.md](AGENT_KNOWLEDGE_FRAMEWORK.md)** - System design
- **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** - This file
- **[DEPENDENCY_MANAGEMENT.md](DEPENDENCY_MANAGEMENT.md)** - Dependencies

### Development
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute
- **[CLAUDE.md](CLAUDE.md)** - Claude Code guidance

### Integration
- **[integrations/storage/README.md](integrations/storage/README.md)** - GitHub/JIRA ingestion
- **[integrations/graphify/README.md](integrations/graphify/README.md)** - Knowledge graphs

## Design Principles

1. **Skill-Driven**: All intelligence in skills, agents coordinate
2. **Progressive Disclosure**: Start high-level, drill down as needed
3. **Context Budget**: Strict line limits on all documentation
4. **Navigation Constraint**: ≤3 hops from entry point
5. **Quality Enforcement**: Automated validation with metrics
6. **Continuous Update**: Documentation maintained with code
7. **Full Automation**: No manual work required

## Success Metrics

**Documentation Quality**:
- 85/100 quality score (exceeds 70 threshold)
- 90% component coverage
- 100% navigation compliance (≤3 hops)
- 0 broken links

**Evaluation Performance**:
- 4/5 scenarios pass (80%)
- 2.4 average hops (under 2.5 target)
- 98.5s average time (under 120s target)
- 82% average confidence (over 80% target)

**Usage Metrics**:
- <3 minutes setup time
- <2 seconds query response
- <130 seconds for full documentation generation
- Comprehensive metrics automatically tracked

## Questions?

- **Issues**: https://github.com/kenjpais/claude-agent-knowledge-skills/issues
- **Documentation**: See files listed above
- **Support**: Open an issue with logs and metrics

---

**Built with Claude API** | **Skill-Driven Architecture** | **Fully Automated**
