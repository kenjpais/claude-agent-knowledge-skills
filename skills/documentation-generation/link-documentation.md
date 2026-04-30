---
name: link-documentation
description: Creates navigation structure, bidirectional links, generates AGENTS.md, enforces 3-hop constraint
type: skill
category: linking
phase: documentation-generation
---

# Link Documentation

## Purpose

Single consolidated skill that performs ALL documentation linking:
- Create bidirectional links between concepts and components
- Generate AGENTS.md primary entry point
- Create index files for navigation
- Enforce ≤3 hop navigation constraint
- Generate "Navigation by Intent" table

**This skill replaces**:
- `link-concepts-to-components`
- `generate-agents-md`
- Related linking operations

## When to Use

- During `/create` command (Phase 3: Linking)
- After synthesis phase completes
- After knowledge graph is generated

## Input

```yaml
repository_path: string
agentic_docs_path: string  # Path to agentic/ directory
knowledge_graph_path: string  # Path to agentic/knowledge-graph/graph.json
constraints:
  max_navigation_depth: 3
  agents_md_max_lines: 150
```

## Output

```yaml
linked_documentation:
  agents_md:
    file: AGENTS.md
    lines: integer
    navigation_table_entries: integer
  
  indexes:
    - file: agentic/design-docs/components/index.md
    - file: agentic/domain/concepts/index.md
    - file: agentic/domain/workflows/index.md
    - file: agentic/exec-plans/index.md
  
  cross_links:
    bidirectional_links_created: integer
    orphaned_docs_resolved: integer
  
  navigation_metrics:
    max_depth_from_agents_md: integer
    avg_depth: float
    unreachable_docs: array
    
  verification:
    navigation_constraint_met: boolean  # ≤3 hops
    agents_md_budget_met: boolean       # ≤150 lines
    zero_orphans: boolean
```

## Process

### Step 1: Load Synthesized Documentation

```python
import os
import yaml

docs_path = f"{repository_path}/agentic"

# Discover all generated docs
component_docs = glob.glob(f"{docs_path}/design-docs/components/*.md")
concept_docs = glob.glob(f"{docs_path}/domain/concepts/*.md")
workflow_docs = glob.glob(f"{docs_path}/domain/workflows/*.md")
exec_plan_docs = glob.glob(f"{docs_path}/exec-plans/completed/*.md")

# Parse frontmatter to extract metadata
all_docs = {}
for doc_path in component_docs + concept_docs + workflow_docs:
    with open(doc_path) as f:
        content = f.read()
        metadata = extract_frontmatter(content)
        all_docs[doc_path] = metadata
```

### Step 2: Create Bidirectional Concept-Component Links

```python
# Map concepts to implementing components
concept_to_components = {}

for component_path, metadata in all_docs.items():
    if 'component' in metadata:
        component_name = metadata['component']
        
        # Find related concepts (from frontmatter or content)
        related_concepts = metadata.get('related_concepts', [])
        
        for concept in related_concepts:
            if concept not in concept_to_components:
                concept_to_components[concept] = []
            concept_to_components[concept].append(component_name)

# Update component docs with concept links
for component_path in component_docs:
    add_section(component_path, "## Related Concepts", concept_links)

# Update concept docs with component links
for concept_path in concept_docs:
    concept_name = extract_name(concept_path)
    implementing_components = concept_to_components.get(concept_name, [])
    add_section(concept_path, "## Implemented By", component_links)
```

### Step 3: Generate Index Files

#### Components Index
```markdown
# Components Index

## Controllers
- [Machine Controller](components/machine-controller.md) - Reconciles Machine resources
- [MachineSet Controller](components/machineset-controller.md) - Manages MachineSets

## Operators
- [Machine API Operator](components/machine-api-operator.md) - Main operator

## Libraries
- [Provider Interface](components/provider-interface.md) - Cloud provider abstraction

## CLI Tools
- [Machine CLI](components/machine-cli.md) - Command-line utilities
```

#### Concepts Index
```markdown
# Concepts Index

## Core Resources
- [Machine](concepts/machine.md) - Represents a single machine instance
- [MachineSet](concepts/machineset.md) - Manages a set of Machines

## Patterns
- [Reconciliation](concepts/reconciliation.md) - Controller reconcile pattern
```

### Step 4: Generate AGENTS.md

```python
def generate_agents_md(components, concepts, build_commands, invariants):
    """
    Generate primary entry point following strict 150-line budget
    """
    
    template = """---
generated: true
last_updated: {timestamp}
---

# {Repository Name}

{1-2 sentence description from README or inferred from components}

## Quick Navigation by Intent

| I want to... | Start here |
|--------------|------------|
| Understand what this repo does | This file (AGENTS.md) |
| Set up development environment | [DEVELOPMENT.md](agentic/DEVELOPMENT.md) |
| Understand architecture | [DESIGN.md](agentic/DESIGN.md) |
| Find a specific component | [Components](agentic/design-docs/components/index.md) |
| Learn about a concept | [Concepts](agentic/domain/concepts/index.md) |
| See workflows | [Workflows](agentic/domain/workflows/index.md) |
| View execution plans | [Exec Plans](agentic/exec-plans/index.md) |
| Run tests | [TESTING.md](agentic/TESTING.md) |
| Security model | [SECURITY.md](agentic/SECURITY.md) |

## Repository Structure

```
{High-level directory tree - ASCII}
```

## Component Boundaries

```
{ASCII diagram showing component relationships}
```

## Core Concepts

| Concept | Description | Docs |
|---------|-------------|------|
{Table of top 5-10 concepts}

## Key Invariants

{Critical constraints from CRDs and validation rules}

## Critical Code Locations

| What | Where |
|------|-------|
{Table of important files/directories}

## Build & Test

```bash
{Essential commands from DEVELOPMENT.md}
```

---
Generated by Agent Knowledge System
"""

    agents_md = template.format(
        timestamp=datetime.utcnow().isoformat(),
        repository_name=get_repo_name(),
        ...
    )
    
    # Enforce 150-line budget
    if len(agents_md.splitlines()) > 150:
        agents_md = condense_to_budget(agents_md, max_lines=150)
    
    return agents_md
```

### Step 5: Validate Navigation Depth

```python
def check_navigation_depth(agents_md_path, all_docs):
    """
    BFS from AGENTS.md to ensure all docs reachable in ≤3 hops
    """
    from collections import deque
    
    # Build graph of document links
    G = build_doc_link_graph(all_docs)
    
    # BFS from AGENTS.md
    visited = {agents_md_path: 0}  # {doc: hop_count}
    queue = deque([(agents_md_path, 0)])
    
    while queue:
        doc, depth = queue.popleft()
        
        # Extract all markdown links from doc
        links = extract_markdown_links(doc)
        
        for link in links:
            link_path = resolve_link(doc, link)
            
            if link_path not in visited:
                visited[link_path] = depth + 1
                queue.append((link_path, depth + 1))
    
    # Check all docs reachable in ≤3 hops
    unreachable = []
    over_budget = []
    
    for doc in all_docs:
        if doc not in visited:
            unreachable.append(doc)
        elif visited[doc] > 3:
            over_budget.append((doc, visited[doc]))
    
    return {
        'max_depth': max(visited.values()) if visited else 0,
        'avg_depth': sum(visited.values()) / len(visited) if visited else 0,
        'unreachable': unreachable,
        'over_budget': over_budget
    }
```

### Step 6: Fix Navigation Violations

```python
def fix_navigation_violations(unreachable_docs, over_budget_docs, agents_md_path):
    """
    Resolve orphaned docs and excessive depth
    """
    
    # For unreachable docs: Add to nearest index
    for doc in unreachable_docs:
        doc_type = infer_type(doc)  # component, concept, workflow
        
        if doc_type == 'component':
            add_to_index('agentic/design-docs/components/index.md', doc)
        elif doc_type == 'concept':
            add_to_index('agentic/domain/concepts/index.md', doc)
        # ... etc
    
    # For docs >3 hops: Create intermediate index or add direct link
    for doc, depth in over_budget_docs:
        if depth == 4:
            # Create intermediate index page
            create_intermediate_index(doc)
        elif depth > 4:
            # Add direct link from AGENTS.md if high-value doc
            if is_high_value(doc):
                add_to_agents_md_navigation(doc)
```

## Example AGENTS.md Output

```markdown
---
generated: true
last_updated: 2026-04-30T10:15:23Z
---

# Machine API Operator

Manages lifecycle of virtual machine instances in OpenShift clusters through Kubernetes-native CRDs.

## Quick Navigation by Intent

| I want to... | Start here |
|--------------|------------|
| Understand what this repo does | This file (AGENTS.md) |
| Set up development environment | [DEVELOPMENT.md](agentic/DEVELOPMENT.md) |
| Understand architecture | [DESIGN.md](agentic/DESIGN.md) |
| Find a specific component | [Components](agentic/design-docs/components/index.md) |
| Learn about a concept | [Concepts](agentic/domain/concepts/index.md) |
| Run tests | [TESTING.md](agentic/TESTING.md) |

## Repository Structure

```
machine-api-operator/
├── cmd/               # Executables
├── pkg/
│   ├── apis/         # CRD definitions
│   ├── controller/   # Reconciliation logic
│   └── provider/     # Cloud provider implementations
└── config/           # Deployment manifests
```

## Component Boundaries

```
┌─────────────────────┐
│ Machine API Operator│
└─────────┬───────────┘
          │
    ┌─────┴─────┬─────────────┬──────────────┐
    │           │             │              │
┌───▼────┐ ┌───▼────┐ ┌──────▼─────┐ ┌─────▼─────┐
│Machine │ │MachineSet│ │Provider   │ │Webhooks   │
│Controller Controller│ │Interface  │ │           │
└────────┘ └─────────┘ └────────────┘ └───────────┘
```

## Core Concepts

| Concept | Description | Docs |
|---------|-------------|------|
| Machine | Single VM instance | [machine.md](agentic/domain/concepts/machine.md) |
| MachineSet | Set of identical Machines | [machineset.md](agentic/domain/concepts/machineset.md) |
| Provider | Cloud-specific integration | [provider.md](agentic/domain/concepts/provider.md) |

## Key Invariants

- Machine must have valid provider reference before reconciliation
- Finalizer `machine.openshift.io/machine-finalizer` prevents premature deletion
- MachineSet replica count must be ≥0

## Critical Code Locations

| What | Where |
|------|-------|
| CRD definitions | `config/crd/` |
| Machine controller | `pkg/controller/machine/` |
| Provider interface | `pkg/provider/interface.go` |

## Build & Test

```bash
# Build
make build

# Run tests
make test

# Deploy locally
make deploy
```

---
Generated by Agent Knowledge System
```

**Lines**: 142 (under 150 budget ✅)

## Verification

- [ ] AGENTS.md generated and ≤150 lines
- [ ] All index files created (components, concepts, workflows, exec-plans)
- [ ] Bidirectional links between concepts and components
- [ ] Navigation depth ≤3 hops from AGENTS.md
- [ ] Zero orphaned documents
- [ ] "Navigation by Intent" table complete and accurate

## Error Handling

```
IF AGENTS.md exceeds 150 lines:
  - Remove verbose descriptions
  - Use tables instead of prose
  - Link more aggressively
  - Re-check budget

IF orphaned docs found:
  - Add to appropriate index
  - Log resolution
  - Re-validate navigation

IF navigation depth >3:
  - Create intermediate indexes
  - Add direct links from AGENTS.md for critical docs
  - Re-validate
```

## Integration with Next Steps

This skill's output feeds into:
1. **validate-documentation** - Validates navigation depth, line budgets
2. **retrieve-from-graph** - Uses navigation structure for queries
3. Coding sub-agent - Uses AGENTS.md as entry point for all queries
