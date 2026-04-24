---
skill_id: create-agentic-docs
name: Create Agentic Documentation
category: synthesis
version: 1.0.0
trigger: /create
description: Generate complete agentic documentation for a repository following the Agent Knowledge Framework
agents: [orchestrator, extractor, synthesizer, linker, validator]
---

# Create Agentic Documentation

**Trigger**: `/create`  
**Purpose**: Generate complete agentic documentation for a repository following the Agent Knowledge Framework

## Overview

This skill orchestrates the full documentation generation pipeline, coordinating multiple agents to extract, synthesize, link, and validate documentation for any codebase.

## Input

**Repository Path or GitHub URL** (optional - defaults to current directory)

```
/create [path/to/repository | github-url]
```

**Examples**:
```bash
/create                                                    # Current directory
/create /path/to/openshift-installer                     # Local repository path
/create https://github.com/openshift/installer           # GitHub URL (auto-clones)
/create github.com/openshift/installer                   # GitHub URL (auto-clones)
```

## Auto-Cloning

If a GitHub URL is provided and the repository is not already cloned:

1. **Parse GitHub URL**: Extract owner and repository name
2. **Clone locally**: `git clone <url> /tmp/agentic-repos/<repo-name>`
3. **Use cloned path**: Continue with documentation generation in cloned repository
4. **Output location**: `<cloned-repo>/AGENTS.md` and `<cloned-repo>/agentic/`

**Clone location**: `/tmp/agentic-repos/<repo-name>/`

**Supported URL formats**:
- `https://github.com/owner/repo`
- `https://github.com/owner/repo.git`
- `github.com/owner/repo`
- `git@github.com:owner/repo.git`

## Process

### Phase 1: Extraction
**Agent**: Extractor  
**Skills Used**: 
- `read-file` - Read source files
- `list-files` - Discover repository structure
- `extract-go-structs` - Parse Go types (if Go repo)
- `extract-kubernetes-crds` - Parse CRD definitions
- `build-dependency-graph` - Build import graph

**Output**: Raw repository data (components, APIs, dependencies)

### Phase 2: Synthesis
**Agent**: Synthesizer  
**Skills Used**:
- `infer-component-boundary` - Detect component boundaries
- `classify-service-role` - Determine component roles
- `generate-component-doc` - Create component documentation
- `generate-concept-doc` - Create concept documentation

**Output**: Component docs, concept docs, required files

### Phase 3: Linking
**Agent**: Linker  
**Skills Used**:
- `link-concepts-to-components` - Create bidirectional links
- `generate-agents-md` - Create AGENTS.md entry point
- `create-navigation-links` - Build navigation structure

**Output**: AGENTS.md, cross-linked documentation

### Phase 4: Knowledge Graph Generation
**Agent**: Synthesizer  
**Skills Used**:
- `generate-knowledge-graph` - Create NetworkX graph with embedded content

**Output**: `agentic/knowledge-graph/graph.json`

**Critical Requirements**:
- Graph must be at `<repo>/agentic/knowledge-graph/graph.json`
- NetworkX node-link JSON format
- **All document content embedded in nodes** (no file I/O during retrieval)
- Includes documentation nodes, component nodes, concept nodes, PR/issue nodes

### Phase 5: Validation
**Agent**: Validator  
**Skills Used**:
- `check-navigation-depth` - Enforce ≤3 hop constraint
- `check-quality-score` - Calculate quality metrics
- `validate-line-budgets` - Check line count limits
- `validate-knowledge-graph` - Verify graph exists and is valid

**Output**: QUALITY_SCORE.md, validation report

## Output Structure

**All output generated in the repository directory itself** (not in a separate output/ directory):

```
<repository-path>/
├── AGENTS.md                    # Entry point (≤150 lines)
└── agentic/
    ├── DESIGN.md               # Design philosophy
    ├── DEVELOPMENT.md          # Dev setup
    ├── TESTING.md              # Test strategy
    ├── RELIABILITY.md          # SLOs and observability
    ├── SECURITY.md             # Security model
    ├── QUALITY_SCORE.md        # Quality metrics
    ├── knowledge-graph/        # ← Knowledge graph
    │   └── graph.json          # ← NetworkX graph (REQUIRED for /ask)
    ├── design-docs/
    │   ├── components/         # Component docs (≤100 lines each)
    │   └── core-beliefs.md
    ├── domain/
    │   ├── concepts/           # Domain concepts (≤75 lines each)
    │   └── workflows/
    ├── decisions/              # ADRs
    └── exec-plans/
        ├── active/
        └── completed/
```

**For GitHub URLs**: Documentation generated in `/tmp/agentic-repos/<repo-name>/`

## Quality Constraints

All generated documentation must meet:

| Constraint | Requirement | Validation |
|------------|-------------|------------|
| **Navigation Depth** | ≤3 hops from AGENTS.md | Automatic |
| **AGENTS.md Length** | ≤150 lines | Line count check |
| **Component Docs** | ≤100 lines each | Line count check |
| **Concept Docs** | ≤75 lines each | Line count check |
| **Required Files** | 7 files minimum | File existence |
| **Quality Score** | ≥70/100 | Comprehensive scoring |

## Usage

```bash
# In Claude Code
/create

# Or with path
/create /path/to/repository

# Or via direct invocation
make generate-docs /path/to/repository
```

## Implementation

When this skill is invoked:

1. **Validate Input**
   - Check repository path exists
   - Verify it's a valid git repository
   - Check language/framework (Go, Python, etc.)

2. **Create Execution Plan**
   - Create active execution plan in `agentic/exec-plans/active/`
   - Track progress through phases
   - Log all operations

3. **Run Extraction Phase**
   - Invoke Extractor agent
   - Extract all components (3-5 main components)
   - Build dependency understanding
   - Store extracted data

4. **Run Synthesis Phase**
   - Invoke Synthesizer agent
   - Generate component documentation
   - Generate concept documentation
   - Create required files (DESIGN.md, etc.)

5. **Run Linking Phase**
   - Invoke Linker agent
   - Generate AGENTS.md
   - Create cross-links between docs
   - Build navigation structure

6. **Run Validation Phase**
   - Invoke Validator agent
   - Check all quality constraints
   - Generate QUALITY_SCORE.md
   - Report any issues

7. **Complete Execution Plan**
   - Move plan to `completed/`
   - Log final statistics
   - Report results to user

## Error Handling

**Repository Not Found**:
- Error: "Repository not found at: {path}"
- Action: Prompt user for valid path

**Unsupported Language**:
- Warning: "Language {lang} not fully supported, using generic extraction"
- Action: Continue with available skills

**Validation Failures**:
- Warning: "Documentation quality score: {score}/100 (threshold: 70)"
- Action: List specific issues, suggest improvements

**Interrupted Generation**:
- Error: "Generation interrupted"
- Action: Save partial progress, create recovery plan

## Success Criteria

Documentation generation is successful when:

✅ All required files created  
✅ Navigation depth ≤3 hops  
✅ Line budgets respected  
✅ Quality score ≥70/100  
✅ No broken links  
✅ Execution plan marked complete  

## Logging

All operations logged to:
- `agentic/exec-plans/active/generate-{timestamp}.md` (during generation)
- `agentic/exec-plans/completed/generate-{timestamp}.md` (after completion)

## Templates

Uses templates from:
- `templates/agentic-structure/AGENTS.md.template`
- `templates/agentic-structure/component.md.template`
- `templates/agentic-structure/concept.md.template`
- `templates/agentic-structure/DESIGN.md.template`
- `templates/agentic-structure/DEVELOPMENT.md.template`
- `templates/agentic-structure/TESTING.md.template`
- `templates/agentic-structure/RELIABILITY.md.template`
- `templates/agentic-structure/SECURITY.md.template`

## Related Skills

**Uses**:
- All `repo/*` skills (repository access)
- All `parsing/*` skills (extraction)
- All `inference/*` skills (analysis)
- All `synthesis/*` skills (generation)
- All `linking/*` skills (navigation)
- All `validation/*` skills (quality checks)

**Used By**:
- Orchestrator agent (primary consumer)

## Example Session

```
User: /create