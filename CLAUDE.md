# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository is a **skill library** for Claude Code containing 40+ skills for generating and maintaining agentic documentation for OpenShift codebases.

**Key principle**: All intelligence is expressed through composable skills. Claude Code loads and executes skills.

**No installation required** - This is a ready-to-use skill library.

## Core Skills (User-Invocable)

### `/create` - Generate Agentic Documentation

**Location**: `skills/create-agentic-docs/SKILL.md`

**What to do**: When the user types `/create`, invoke this skill using the Skill tool before doing anything else.

**Usage**:
```bash
# User types in Claude Code:
/create
```

**Workflow**:
1. Extract repository structure (list files, parse Go/CRDs)
2. Infer component boundaries and roles
3. Generate component documentation (≤100 lines each)
4. Generate AGENTS.md entry point (≤150 lines)
5. Create cross-links between docs
6. Validate ≤3 hop navigation and quality score

**Output**:
- `AGENTS.md` - Entry point
- `agentic/design-docs/components/` - Component docs
- `agentic/domain/concepts/` - Concept docs
- `agentic/QUALITY_SCORE.md` - Quality metrics

**Constraints**:
- AGENTS.md ≤150 lines
- Component docs ≤100 lines each
- Concept docs ≤75 lines each
- Navigation depth ≤3 hops
- Quality score ≥70/100

### `/validate` - Validate Documentation Quality

**Location**: `skills/validate-agentic-docs/SKILL.md`

**Usage**:
```bash
# User types in Claude Code:
/validate
```

**What to check**:
1. AGENTS.md exists and ≤150 lines
2. Required files present (DESIGN, DEVELOPMENT, TESTING, RELIABILITY, SECURITY)
3. Navigation depth ≤3 hops from AGENTS.md
4. No broken links
5. Component coverage ≥80%
6. Documentation freshness <90 days
7. Quality score ≥70/100

**Output**: Pass/fail with quality score and recommendations

### `/evaluate` - Test with Coding Agent Simulation

**Location**: `skills/evaluate-agentic-docs/SKILL.md`

**Usage**:
```bash
# User types in Claude Code:
/evaluate
```

**What to do**: Spawn a sub-agent using the Agent tool with these constraints:
- Sub-agent can ONLY use `ask-agentic-docs` skill
- Sub-agent CANNOT access source code directly
- Sub-agent must navigate documentation within ≤3 hops
- Sub-agent must stay within 500 line context budget

**Test scenarios**:
1. New feature: "Add ARM64 support"
2. Bug fix: "Fix memory leak in pod inspector"
3. Refactor: "Implement LRU cache eviction"
4. Code review: "Review pod placement config"
5. Architecture: "Explain multi-arch scheduling"

**Success criteria**: 80% scenarios pass, avg ≤2.5 hops, ≤120s, ≥80% confidence

### `/ask` - Query Documentation

**Location**: `skills/ask-agentic-docs/SKILL.md`

**Usage**:
```bash
# User types in Claude Code:
/ask what components exist?
/ask how does the installer work?
/ask what is the reconciliation pattern?
```

**How to answer**:
1. Parse query to identify query type (component, concept, architecture, etc.)
2. Start from AGENTS.md (hop 0)
3. Navigate to relevant documentation (≤3 hops)
4. Return answer with context (≤500 lines)
5. Include related links and navigation path

**Query types**:
- Component discovery
- Component details
- Concept lookup
- Architecture overview
- Development guidance
- Relationship queries

## Skill Categories

### Repository Access Skills (`skills/repo/`)
- `read-file` - Read file contents
- `list-files` - Discover files with filtering
- `search-code` - Search for code patterns
- `get-git-history` - Extract commit history

### Parsing Skills (`skills/parsing/`)
- `extract-go-structs` - Parse Go types (deterministic)
- `extract-kubernetes-crds` - Parse CRD definitions (deterministic)
- `build-dependency-graph` - Build import graph (deterministic)
- `parse-kubernetes-controller-pattern` - Extract controller structure

### Inference Skills (`skills/inference/`)
- `infer-component-boundary` - Detect component boundaries (probabilistic, confidence-scored)
- `classify-service-role` - Determine component role (probabilistic, confidence-scored)

### Synthesis Skills (`skills/synthesis/`)
- `generate-component-doc` - Create component documentation
- `generate-agents-md` - Create AGENTS.md entry point

### Linking Skills (`skills/linking/`)
- `link-concepts-to-components` - Create bidirectional cross-links

### Validation Skills (`skills/validation/`)
- `check-navigation-depth` - Enforce ≤3 hop constraint (critical)
- `check-quality-score` - Calculate comprehensive quality metrics (critical)

### Documentation Skills (`skills/documentation/`)
- `write-agentic-file` - Write/update files in agentic/ directory with validation

### Knowledge Graph Skills (`skills/knowledge-graph/`)
- `generate-knowledge-graph` - Create queryable graph from docs + database
- `retrieve-from-graph` - Graph-based retrieval with ≤3 hops, ≤500 lines context

### Data Ingestion Skills (`skills/data-ingestion/`)
- `ingest-github-data` - Fetch GitHub PRs, issues, JIRA references → SQLite

### Evaluation Skills (`skills/evaluation/`)
- `evaluate-agentic-docs` - Coding agent simulation with test scenarios

### Monitoring Skills (`skills/monitoring/`)
- `log-operation` - Log all operations (mandatory)

**Complete catalog**: See `skill-registry/index.yaml`

## Agent Definitions

Seven agents coordinate skill execution:

1. **Orchestrator** (`agents/orchestrator/`) - Coordinates entire pipeline
2. **Extractor** (`agents/extractor/`) - Mines repository data
3. **Synthesizer** (`agents/synthesizer/`) - Generates documentation
4. **Linker** (`agents/linker/`) - Creates navigation structure
5. **Validator** (`agents/validator/`) - Enforces quality constraints
6. **Curator** (`agents/curator/`) - Maintains documentation freshness
7. **Retrieval** (`agents/retrieval/`) - Provides controlled access to docs

**Note**: Agents only coordinate - all intelligence is in skills.

## Quality Guarantees

**Navigation Constraint**:
- ≤3 hops from AGENTS.md to any information
- No orphaned documents
- Clear navigation paths

**Context Budget**:
- AGENTS.md ≤150 lines
- Component docs ≤100 lines each
- Concept docs ≤75 lines each
- Query responses ≤500 lines total

**Quality Score** (0-100):
- Coverage: 40 points (≥80% components documented)
- Freshness: 20 points (updated <90 days)
- Completeness: 20 points (all required files present)
- Linkage: 10 points (no broken links)
- Navigation: 10 points (≤3 hop depth)
- **Pass threshold**: ≥70/100

## Templates

All documentation uses templates from `templates/agentic-structure/`:
- `AGENTS.md.template` - Entry point (≤150 lines)
- `component.md.template` - Component docs (≤100 lines)
- `concept.md.template` - Concept docs (≤75 lines)
- `DESIGN.md.template` - Design philosophy
- `DEVELOPMENT.md.template` - Development setup
- `TESTING.md.template` - Test strategy
- `RELIABILITY.md.template` - SLOs and observability
- `SECURITY.md.template` - Security model
- `QUALITY_SCORE.md.template` - Quality metrics

## How to Use This Repository

### When User Asks to Generate Documentation

1. **Invoke `/create` skill**:
   ```python
   Skill(skill="create-agentic-docs")
   ```

2. **Follow the skill workflow**:
   - Phase 1: Extraction (use repo/ and parsing/ skills)
   - Phase 2: Synthesis (use inference/ and synthesis/ skills)
   - Phase 3: Linking (use linking/ skills)
   - Phase 4: Validation (use validation/ skills)

3. **Report results**:
   - Files created
   - Quality score achieved
   - Issues found (if any)
   - Next steps (validate, evaluate, query)

### When User Asks to Validate Documentation

1. **Invoke `/validate` skill**:
   ```python
   Skill(skill="validate-agentic-docs")
   ```

2. **Run all 8 validation checks**:
   - Structure, navigation, line budgets, links, coverage, freshness, completeness, quality

3. **Report**:
   - Overall score (0-100)
   - Pass/fail per check
   - Specific issues
   - Recommendations

### When User Asks to Query Documentation

1. **Invoke `/ask` skill**:
   ```python
   Skill(skill="ask-agentic-docs", args="how does the installer work?")
   ```

2. **Navigate documentation** (≤3 hops):
   - Start from AGENTS.md
   - Follow links to relevant docs
   - Stay within 500 line context budget

3. **Return answer**:
   - Concise answer
   - Relevant details
   - Related links
   - Navigation path taken

### When User Asks to Evaluate Documentation

1. **Invoke `/evaluate` skill**:
   ```python
   Skill(skill="evaluate-agentic-docs")
   ```

2. **Spawn coding sub-agent** (using Agent tool):
   - Constrain to `ask-agentic-docs` skill only
   - Give test scenario
   - Measure: hops, time, confidence

3. **Run 5 test scenarios**:
   - New feature, bug fix, refactor, code review, architecture

4. **Report**:
   - Scenarios passed/failed
   - Aggregate metrics
   - Recommendations for improvement

## Optional Configuration

### GitHub Token (Optional)

For higher API rate limits when ingesting GitHub data:

```bash
cp .env.example .env
# Add: GH_API_TOKEN=ghp_your_token
```

Benefits:
- 5,000 requests/hour (vs 60 without)
- Access to private repositories

**Get token**: https://github.com/settings/tokens (scopes: `repo`, `read:org`)

### JIRA Access (Optional)

For private JIRA instances, add to `.env`:
```bash
JIRA_URL=https://your-jira.com
JIRA_EMAIL=your@email.com
JIRA_API_TOKEN=your-token
```

Public JIRA (issues.redhat.com) needs no authentication.

## Anti-Patterns to Avoid

- ❌ Generating documentation in one pass without extraction → synthesis → linking pipeline
- ❌ Embedding interpretation in parsing skills (separate extraction from inference)
- ❌ Skipping validation (always check navigation depth and quality score)
- ❌ Exceeding line budgets (enforce AGENTS.md ≤150, components ≤100, concepts ≤75)
- ❌ Creating documentation without cross-links (navigation is critical)
- ❌ Skipping logging (all operations must be logged via `log-operation` skill)
- ❌ Ignoring OpenShift patterns (controllers, operators, reconcile loops, CRDs)

## Key Workflows

### Full Documentation Generation

```
/create
  ↓
1. Extraction
   - list-files: Discover repository structure
   - extract-go-structs: Parse Go types
   - extract-kubernetes-crds: Parse CRDs
   - build-dependency-graph: Build import graph
   
2. Synthesis
   - infer-component-boundary: Detect components
   - classify-service-role: Determine roles
   - generate-component-doc: Create component docs
   - generate-agents-md: Create AGENTS.md
   
3. Linking
   - link-concepts-to-components: Create cross-links
   
4. Validation
   - check-navigation-depth: Verify ≤3 hops
   - check-quality-score: Calculate score
   
Output: Complete agentic documentation
```

### Incremental Update (Curator)

```
When code changes detected:
  ↓
1. get-git-history: Find changed files
2. Identify affected components
3. Re-extract only changed components
4. Re-synthesize affected docs
5. Update links
6. Re-validate
```

### Query Resolution

```
/ask "how does X work?"
  ↓
1. Read AGENTS.md (hop 0)
2. Find X in component list (hop 1)
3. Read component doc for X (hop 2)
4. Read related concepts if needed (hop 3)
5. Return answer with navigation path
```

## Integration with External Systems

### GitHub/JIRA Storage (`integrations/storage/`)
- Ingest GitHub PRs, issues
- Extract JIRA references from titles/bodies/commits
- Fetch JIRA issues
- Store in SQLite: `~/.agent-knowledge/data.db`
- See `integrations/storage/README.md`

### Graphify (`integrations/graphify/`)
- Generate knowledge graphs from documentation
- Enable graph-based retrieval
- See `integrations/graphify/README.md`

## Utilities

### Logging (`utilities/logging/logger.py`)
```python
from utilities.logging.logger import get_logger

logger = get_logger("agent-name")
logger.log_start("operation", "resource")
logger.log_success("operation", "resource", duration_ms=100)
```

### Validation (`utilities/validation/validator.py`)
```python
from utilities.validation.validator import NavigationDepthChecker, QualityScoreCalculator

# Check navigation
checker = NavigationDepthChecker(Path("AGENTS.md"), max_depth=3)
result = checker.check(Path("agentic/"))

# Calculate quality
calculator = QualityScoreCalculator(Path("."), Path("agentic/"))
scores = calculator.calculate()
```

## Documentation

- **[README.md](README.md)** - Quick start and overview
- **[WORKFLOW_EXPLAINED.md](WORKFLOW_EXPLAINED.md)** - Complete workflow explanation
- **[CORE_SKILLS.md](CORE_SKILLS.md)** - Detailed skill reference
- **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** - Complete system reference
- **[AGENT_KNOWLEDGE_FRAMEWORK.md](AGENT_KNOWLEDGE_FRAMEWORK.md)** - Architecture
- **[USAGE.md](USAGE.md)** - Usage examples
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contributing guidelines

---

**Ready to use** | **No installation** | **Skill-driven** | **Quality-first**
