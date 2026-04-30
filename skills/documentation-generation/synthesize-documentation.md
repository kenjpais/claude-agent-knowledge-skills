---
name: synthesize-documentation
description: Consolidated synthesis skill - infers components, generates component/concept docs from extracted data + database
type: skill
category: synthesis
phase: documentation-generation
---

# Synthesize Documentation

## Purpose

Single consolidated skill that performs ALL documentation synthesis:
- Infer component boundaries from dependency graph
- Classify component roles (controller, library, CLI, operator)
- Generate component documentation
- Generate concept documentation
- Generate execution plans from GitHub PRs + JIRA
- Generate required documentation files (DESIGN.md, DEVELOPMENT.md, etc.)

**This skill replaces**:
- `infer-component-boundary`
- `classify-service-role`
- `generate-component-doc`
- Related synthesis operations

## When to Use

- During `/create` command (Phase 2: Synthesis)
- After extraction phase completes
- When re-generating docs from existing extracted data

## Input

```yaml
extraction_artifacts_path: string  # Path to .agentic-extraction/
database_path: string              # Path to ~/.agent-knowledge/data.db (optional)
repository_path: string
constraints:
  line_budgets:
    components: 100
    concepts: 75
  confidence_threshold: 0.5
```

## Output

```yaml
generated_documentation:
  components:
    - file: agentic/design-docs/components/{name}.md
      lines: integer
      confidence: float
  concepts:
    - file: agentic/domain/concepts/{name}.md
      lines: integer
  exec_plans:
    - file: agentic/exec-plans/completed/{name}.md
      source: github_pr | jira_issue
  required_files:
    - DESIGN.md
    - DEVELOPMENT.md
    - TESTING.md
    - RELIABILITY.md
    - SECURITY.md
    - QUALITY_SCORE.md (template only)
  metrics:
    components_generated: integer
    concepts_generated: integer
    exec_plans_generated: integer
    synthesis_duration_seconds: float
```

## Process

### Step 1: Load Extraction Artifacts

```python
import json

extraction_path = f"{repository_path}/.agentic-extraction/"

with open(f"{extraction_path}/go-analysis.json") as f:
    go_analysis = json.load(f)

with open(f"{extraction_path}/dependency-graph.json") as f:
    graph_data = json.load(f)
    
with open(f"{extraction_path}/crds.json") as f:
    crds = json.load(f)
    
with open(f"{extraction_path}/controllers.json") as f:
    controllers = json.load(f)
```

### Step 2: Infer Component Boundaries

```python
import networkx as nx
from networkx.algorithms import community

# Reconstruct graph
G = nx.node_link_graph(graph_data)

# Apply Louvain community detection
communities = community.louvain_communities(G.to_undirected())

# Infer components from communities
components = []
for i, comm in enumerate(communities):
    packages = list(comm)
    
    # Calculate confidence based on modularity
    modularity = nx.algorithms.community.modularity(
        G.to_undirected(), 
        [comm]
    )
    
    # Infer component name from package paths
    component_name = infer_name_from_packages(packages)
    
    components.append({
        'id': f'component-{i}',
        'name': component_name,
        'packages': packages,
        'confidence': modularity,
        'size': len(packages)
    })

# Filter by confidence threshold
components = [c for c in components if c['confidence'] >= 0.5]
```

### Step 3: Classify Component Roles

For each component:

```python
def classify_role(component, go_analysis, controllers):
    """
    Classify component as:
    - controller: Has Reconcile() function
    - operator: Has controller + CRD
    - library: Exported types, no main()
    - cli: Has main() function
    - webhook: Has admission webhook patterns
    """
    
    # Check for controller patterns
    is_controller = any(
        ctrl['package'] in component['packages']
        for ctrl in controllers
    )
    
    # Check for CRDs
    has_crds = any(
        crd['api_package'] in component['packages']
        for crd in crds
    )
    
    # Check for main()
    has_main = any(
        'func main()' in pkg['functions']
        for pkg in go_analysis['packages']
        if pkg['path'] in component['packages']
    )
    
    # Classify
    if is_controller and has_crds:
        return 'operator', 0.9
    elif is_controller:
        return 'controller', 0.85
    elif has_main:
        return 'cli', 0.8
    else:
        return 'library', 0.7
```

### Step 4: Generate Component Documentation

For each component:

```python
template = load_template('component-doc-template.md')

component_doc = template.format(
    name=component['name'],
    role=component['role'],
    packages=component['packages'],
    types=get_types_for_component(component, go_analysis),
    crds=get_crds_for_component(component, crds),
    controllers=get_controllers_for_component(component, controllers),
    dependencies=get_dependencies(component, G)
)

# Enforce line budget
if len(component_doc.splitlines()) > 100:
    component_doc = summarize_to_budget(component_doc, max_lines=100)

# Write to file
output_path = f"{repository_path}/agentic/design-docs/components/{component['name']}.md"
write_file(output_path, component_doc)
```

**Template structure**:
```markdown
---
component: {name}
type: {role}
confidence: {confidence}
packages: {packages}
---

# {Component Name}

## Overview
{One paragraph description based on role}

## Role
{controller | operator | library | cli}

## Architecture
| Element | Location | Purpose |
|---------|----------|---------|
{Table of key types/functions}

## Key Types
{List of important structs/interfaces}

## CRDs Managed
{If operator/controller: list CRDs}

## Dependencies
{Packages this component depends on}

## Entry Points
{main() or reconcile functions}
```

### Step 5: Generate Concept Documentation

Extract concepts from:
1. CRD kinds (Machine, MachineSet)
2. Core domain types
3. Frequently referenced terms

```python
concepts = []

# From CRDs
for crd in crds:
    concepts.append({
        'name': crd['kind'],
        'type': 'crd',
        'definition': crd['description'],
        'schema': crd['schema'],
        'source': crd['group']
    })

# From core types (heuristic: types with >5 references)
for type_def in go_analysis['types']:
    if type_def['reference_count'] > 5:
        concepts.append({
            'name': type_def['name'],
            'type': 'domain-type',
            'definition': type_def['godoc'],
            'fields': type_def['fields']
        })

# Generate concept docs
for concept in concepts:
    concept_doc = generate_concept_doc(concept)
    write_file(f"agentic/domain/concepts/{concept['name'].lower()}.md", concept_doc)
```

### Step 6: Generate Execution Plans from Database

```python
if database_path and os.path.exists(database_path):
    import sqlite3
    
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    # Fetch PRs with JIRA references
    cursor.execute("""
        SELECT pr.number, pr.title, pr.body, jira.key, jira.summary
        FROM github_prs pr
        LEFT JOIN jira_issues jira ON pr.jira_refs LIKE '%' || jira.key || '%'
        WHERE pr.merged_at IS NOT NULL
        ORDER BY pr.merged_at DESC
        LIMIT 50
    """)
    
    for row in cursor.fetchall():
        pr_number, pr_title, pr_body, jira_key, jira_summary = row
        
        exec_plan = generate_exec_plan_from_pr(
            pr_number=pr_number,
            pr_title=pr_title,
            pr_body=pr_body,
            jira_key=jira_key,
            jira_summary=jira_summary
        )
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        filename = f"agentic/exec-plans/completed/pr-{pr_number}-{timestamp}.md"
        write_file(filename, exec_plan)
```

### Step 7: Generate Required Documentation Files

#### DESIGN.md
```python
design_doc = f"""
# Design Documentation

## Architecture Overview
{Extract high-level architecture from component relationships}

## Component Boundaries
{List all components with roles}

## Key Invariants
{Extract from CRD validation rules and code comments}

## Layering Rules
{Derive from dependency graph - which layers can depend on which}
"""
write_file("agentic/DESIGN.md", design_doc)
```

#### DEVELOPMENT.md
```python
# Extract from Makefile, go.mod, README
development_doc = f"""
# Development Guide

## Prerequisites
{Parse from go.mod, Makefile}

## Build Commands
{Extract from Makefile targets}

## Running Tests
{Find test commands in Makefile or scripts}
"""
write_file("agentic/DEVELOPMENT.md", development_doc)
```

#### TESTING.md, RELIABILITY.md, SECURITY.md
Similar extraction from code patterns and existing docs.

## Line Budget Enforcement

```python
def enforce_line_budget(doc_content, max_lines):
    lines = doc_content.splitlines()
    
    if len(lines) <= max_lines:
        return doc_content
    
    # Summarization strategy:
    # 1. Keep frontmatter
    # 2. Keep section headers
    # 3. Truncate long tables
    # 4. Remove verbose prose
    # 5. Add links to code for details
    
    summarized = summarize(doc_content, target_lines=max_lines)
    return summarized
```

## Confidence Scoring

```python
def calculate_component_confidence(component, graph):
    """
    Confidence based on:
    - Modularity score (0-1): How tightly coupled the packages are
    - Size: Larger components more likely to be real
    - Clear naming: Package names suggest component purpose
    """
    
    modularity = calculate_modularity(graph, component['packages'])
    size_score = min(len(component['packages']) / 10, 1.0)
    
    # Name clarity: Do package names share common prefix?
    names = [p.split('/')[-1] for p in component['packages']]
    name_score = common_prefix_ratio(names)
    
    confidence = (modularity * 0.5) + (size_score * 0.3) + (name_score * 0.2)
    return confidence
```

## Error Handling

```
IF component confidence < threshold:
  - Generate doc anyway
  - Mark in frontmatter: confidence: <0.5
  - Add warning note

IF line budget exceeded:
  - Summarize content
  - Add links to source code
  - Log warning

IF database unavailable:
  - Skip exec-plan generation
  - Log info: "No database - skipping exec-plans"
  - Continue with code-based docs
```

## Verification

- [ ] All components with confidence ≥0.5 have documentation
- [ ] All component docs ≤100 lines
- [ ] All concept docs ≤75 lines
- [ ] Required files generated (DESIGN, DEVELOPMENT, TESTING, RELIABILITY, SECURITY)
- [ ] Exec-plans generated if database available
- [ ] All confidence scores logged

## Example Output

```
agentic/
├── design-docs/
│   ├── components/
│   │   ├── machine-controller.md (87 lines, confidence: 0.85)
│   │   ├── machine-api-operator.md (95 lines, confidence: 0.92)
│   │   └── ...
│   └── core-beliefs.md
├── domain/
│   ├── concepts/
│   │   ├── machine.md (68 lines)
│   │   ├── machineset.md (72 lines)
│   │   └── ...
│   └── workflows/
├── exec-plans/
│   └── completed/
│       ├── pr-1234-20260430-101523.md
│       └── ...
├── DESIGN.md
├── DEVELOPMENT.md
├── TESTING.md
├── RELIABILITY.md
├── SECURITY.md
└── QUALITY_SCORE.md (template)
```

## Integration with Next Steps

This skill's output feeds into:
1. **generate-knowledge-graph** - Uses generated docs to build graph
2. **link-documentation** - Uses component/concept relationships
3. **validate-documentation** - Validates line budgets, completeness
