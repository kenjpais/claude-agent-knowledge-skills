# Core Skills - User Interface

The Agent Knowledge System provides three core skills that serve as the primary user interface for agentic documentation. These skills can be invoked via slash commands in Claude Code.

---

## 📋 Available Skills

### 1. `/create` - Create Agentic Documentation

**Purpose**: Generate complete agentic documentation for a repository

**Usage**:
```bash
/create                                    # Current directory
/create /path/to/repository               # Specific repository
```

**What it does**:
1. **Extraction** - Discovers components, APIs, dependencies
2. **Synthesis** - Generates component and concept documentation
3. **Linking** - Creates AGENTS.md and navigation structure
4. **Validation** - Ensures quality constraints are met

**Output**:
```
repository/
├── AGENTS.md                    # Entry point (≤150 lines)
└── agentic/
    ├── DESIGN.md
    ├── DEVELOPMENT.md
    ├── TESTING.md
    ├── RELIABILITY.md
    ├── SECURITY.md
    ├── QUALITY_SCORE.md
    ├── design-docs/components/
    ├── domain/concepts/
    └── exec-plans/
```

**Quality Guarantees**:
- ✅ Navigation depth ≤3 hops
- ✅ Line budgets respected (AGENTS.md ≤150, components ≤100, concepts ≤75)
- ✅ Quality score ≥70/100
- ✅ No broken links
- ✅ All required files present

**Example Session**:
```
User: /create

Agent: 🚀 Generating agentic documentation...

Phase 1: Extraction
  ✅ Discovered 5 components
  ✅ Extracted 12 CRDs
  ✅ Built dependency graph (23 packages)

Phase 2: Synthesis
  ✅ Generated 5 component docs
  ✅ Generated 8 concept docs
  ✅ Created required files

Phase 3: Linking
  ✅ Generated AGENTS.md (142 lines)
  ✅ Created 15 cross-links
  ✅ Max depth: 2 hops

Phase 4: Validation
  ✅ Quality score: 88/100
  ✅ All constraints met

✅ Documentation generated successfully!
   Location: ./agentic/
   Next: /validate to verify or /ask to query
```

---

### 2. `/validate` - Validate Agentic Documentation

**Purpose**: Validate existing documentation against repository content and framework constraints

**Usage**:
```bash
/validate                                  # Current directory
/validate /path/to/repository             # Specific repository
```

**What it validates**:
1. **Structure** - Required files and directories exist
2. **Navigation** - All docs reachable in ≤3 hops
3. **Line Budgets** - Documents within length limits
4. **Links** - No broken links
5. **Coverage** - All components documented
6. **Freshness** - Documentation recently updated
7. **Completeness** - Required sections present
8. **Quality Score** - Overall score ≥70/100

**Output**:
```markdown
# Validation Report

**Repository**: openshift-installer
**Date**: 2026-04-24
**Overall Score**: 88/100 ✅ PASS

## Summary
✅ All required files present
✅ Max navigation depth: 2 hops (limit: 3)
⚠️  1 component doc exceeds 100 lines
✅ No broken links
✅ Coverage: 87.5% (7/8 components)

## Quality Score: 88/100

- Coverage: 35/40
- Freshness: 18/20
- Completeness: 20/20
- Linkage: 10/10
- Navigation: 10/10

## Recommendations
1. Document missing component: validation
2. Reduce component X to ≤100 lines
```

**Example Session**:
```
User: /validate

Agent: 🔍 Validating agentic documentation...

Structure Check
  ✅ AGENTS.md exists
  ✅ All required files present

Navigation Check
  ✅ Max depth: 2 hops (limit: 3)
  ✅ No orphaned documents

Line Budget Check
  ✅ AGENTS.md: 142 lines (limit: 150)
  ⚠️  installer.md: 105 lines (limit: 100)
  ✅ All concept docs OK

Quality Score
  ✅ Coverage: 35/40 (87.5%)
  ✅ Freshness: 18/20 (90%)
  ✅ Completeness: 20/20 (100%)
  ✅ Linkage: 10/10 (100%)
  ✅ Navigation: 10/10 (100%)

Overall: 88/100 ✅ PASS

Recommendations:
  1. Document missing component: validation
  2. Reduce installer.md by 5 lines
```

---

### 3. `/ask` - Query Agentic Documentation

**Purpose**: Retrieve specific information from agentic documentation (retrieval agent)

**Usage**:
```bash
/ask what components exist?
/ask how does the installer work?
/ask what is the reconciliation pattern?
/ask show me the architecture
```

**Query Types**:

1. **Component Discovery**
   - "What components exist?"
   - "List all components"

2. **Component Details**
   - "How does {component} work?"
   - "What does {component} do?"

3. **Concept Lookup**
   - "What is {concept}?"
   - "Explain {concept}"

4. **Architecture**
   - "Show me the architecture"
   - "How is the system structured?"

5. **Development**
   - "How do I contribute?"
   - "How to run tests?"

6. **Relationships**
   - "What uses {component}?"
   - "How are A and B related?"

**Response Format**:
```markdown
## {Question}

**Answer**: {concise answer}

**Details**:
{relevant details from documentation}

**Related**:
- [Related Component](path/to/doc.md)
- [Related Concept](path/to/concept.md)

**Next Steps**:
- To learn more: /ask {related question}
- To see code: {file path}
```

**Example Session 1** - Component Discovery:
```
User: /ask what components exist?

Agent: ## Components in this repository

This repository contains 5 main components:

1. **Installer** - Orchestrates cluster installation
   [Details](agentic/design-docs/components/installer.md)

2. **Asset Generator** - Generates cluster configuration
   [Details](agentic/design-docs/components/asset-generator.md)

3. **Bootstrap** - Initializes control plane
   [Details](agentic/design-docs/components/bootstrap.md)

4. **Terraform Provider** - Infrastructure provisioning
   [Details](agentic/design-docs/components/terraform-provider.md)

5. **Validator** - Configuration validation
   [Details](agentic/design-docs/components/validator.md)

**Next Steps**:
- Learn about specific component: /ask how does installer work?
- See architecture: /ask show me the architecture
```

**Example Session 2** - Component Details:
```
User: /ask how does the installer work?

Agent: ## How the Installer Works

**Purpose**: Orchestrates the entire OpenShift cluster installation

**Key Responsibilities**:
1. Validates installation configuration
2. Generates cluster assets (manifests, configs)
3. Provisions infrastructure via Terraform
4. Bootstraps control plane
5. Waits for cluster ready state

**Dependencies**:
- Asset Generator - for manifest generation
- Terraform Provider - for infrastructure
- Validator - for config validation

**Flow**:
1. User provides install-config.yaml
2. Validator checks configuration
3. Asset Generator creates manifests
4. Terraform provisions infrastructure
5. Bootstrap initializes control plane
6. Installer monitors until ready

**Code**: `pkg/asset/installconfig/` and `pkg/installer/`

**Next Steps**:
- Deep dive: /ask explain the bootstrap process
- See workflow: /ask show installation workflow
```

**Example Session 3** - Concept Lookup:
```
User: /ask what is the reconciliation pattern?

Agent: ## Reconciliation Pattern

**Definition**: A control loop pattern where a controller continuously 
compares desired state (spec) with actual state (status) and takes 
action to reconcile differences.

**Why It Matters**:
- Core pattern in Kubernetes operators
- Enables self-healing and declarative configuration
- Used throughout OpenShift controllers

**When to Use**:
- Managing cluster resources
- Implementing operators
- Maintaining desired state over time

**Related Concepts**:
- [Controller Pattern](./controller-pattern.md)
- [Operator Pattern](./operator-pattern.md)

**Used By**:
- Machine API Operator
- Cluster Version Operator

**Next Steps**:
- See implementation: /ask how does machine-api use reconciliation?
- Learn operators: /ask what is the operator pattern?
```

---

## 🔄 Typical Workflows

### Workflow 1: Initial Documentation Generation

```bash
# 1. Generate documentation
/create

# 2. Validate quality
/validate

# 3. Query to verify
/ask what components exist?
/ask how does {component} work?
```

### Workflow 2: Documentation Maintenance

```bash
# 1. Validate current state
/validate

# 2. If score low, regenerate specific parts
/create

# 3. Re-validate
/validate
```

### Workflow 3: Using Documentation

```bash
# 1. Find components
/ask what components exist?

# 2. Learn about specific component
/ask how does {component} work?

# 3. Understand relationships
/ask what depends on {component}?

# 4. Learn concepts
/ask what is {concept}?
```

---

## 🎯 Design Principles

### Progressive Disclosure
- Start with high-level overview (AGENTS.md)
- Navigate to details as needed (≤3 hops)
- Load minimal context per query

### Quality Enforcement
- All documentation validated before completion
- Constraints enforced (navigation depth, line budgets)
- Quality score threshold (≥70/100)

### Skill-Based Intelligence
- All intelligence in atomic skills
- Core skills coordinate other skills
- Agents orchestrate skill execution

### User-Friendly Interface
- Simple slash commands (`/create`, `/validate`, `/ask`)
- No complex configuration required
- Clear, structured output

---

## 📊 Integration with Agents

| Skill | Primary Agent | Supporting Agents |
|-------|--------------|-------------------|
| `/create` | Orchestrator | Extractor, Synthesizer, Linker, Validator |
| `/validate` | Validator | Curator |
| `/ask` | Retrieval | - |

---

## 🔧 Technical Details

### Context Budgets

**`/create`**:
- No context limit (creates new content)
- Follows templates strictly
- Enforces output constraints

**`/validate`**:
- Reads all documentation
- Reports summary only
- Full results in QUALITY_SCORE.md

**`/ask`**:
- Max context: 500 lines per query
- Progressive disclosure
- Minimal loading (only what's needed)

### Logging

All skill invocations logged:
- `/create` → `agentic/exec-plans/completed/create-{timestamp}.md`
- `/validate` → `agentic/exec-plans/completed/validate-{timestamp}.md`
- `/ask` → `agentic/exec-plans/queries/{timestamp}.log`

### Error Handling

**Documentation Not Found** (`/validate`, `/ask`):
- Suggests running `/create` first

**Repository Not Found** (`/create`):
- Prompts for valid path

**Validation Failures** (`/create`):
- Lists specific issues
- Suggests fixes

---

## 📚 See Also

- **Skill Definitions**:
  - `skills/create-agentic-docs/SKILL.md`
  - `skills/validate-agentic-docs/SKILL.md`
  - `skills/ask-agentic-docs/SKILL.md`

- **Agent Definitions**:
  - `agents/orchestrator/AGENT.md`
  - `agents/validator/AGENT.md`
  - `agents/retrieval/AGENT.md`

- **Framework**:
  - `AGENT_KNOWLEDGE_FRAMEWORK.md` - Complete specification
  - `CLAUDE.md` - Implementation guide
  - `README.md` - Overview

---

## Summary

The three core skills provide a complete interface to the agentic documentation system:

✅ **`/create`** - Generate documentation  
✅ **`/validate`** - Ensure quality  
✅ **`/ask`** - Query information  

Together, they enable AI coding assistants to:
- Navigate systems in ≤3 hops
- Understand architectural intent
- Reuse patterns consistently
- Avoid violating invariants

**Get Started**: `/create` in any repository!
