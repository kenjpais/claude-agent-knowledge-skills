# Knowledge Graph Specification

## Overview

The knowledge graph is a NetworkX-based in-memory graph that stores all agentic documentation content for efficient retrieval without file I/O.

## Location

**Required Location**: `<repo>/agentic/knowledge-graph/graph.json`

This is the canonical location where:
- `/create` generates the graph
- `/ask` loads the graph
- `/validate` checks the graph

## Format

**Format**: NetworkX node-link JSON

**Schema**:
```json
{
  "directed": true,
  "multigraph": false,
  "graph": {},
  "nodes": [
    {
      "id": "node_identifier",
      "type": "NodeType",
      "name": "Node Name",
      "content": "Full content embedded here...",
      ...additional attributes
    }
  ],
  "links": [
    {
      "source": "node_id_1",
      "target": "node_id_2",
      "relationship": "RELATIONSHIP_TYPE"
    }
  ]
}
```

## Node Types

### 1. EntryPoint
**Represents**: AGENTS.md file

**Required Attributes**:
```python
{
  "id": "entrypoint_agents",
  "type": "EntryPoint",
  "name": "AGENTS.md",
  "content": "# AGENTS.md\n\n...",  # Full AGENTS.md content
  "file_path": "AGENTS.md",
  "line_count": 142
}
```

**Constraints**:
- Exactly ONE EntryPoint node per graph
- Must have `content` attribute with full AGENTS.md text
- All other nodes must be reachable within 3 hops

### 2. Document
**Represents**: Top-level documentation files (DESIGN.md, DEVELOPMENT.md, etc.)

**Required Attributes**:
```python
{
  "id": "doc_design",
  "type": "Document",
  "name": "DESIGN.md",
  "content": "# Design Philosophy\n\n...",  # Full content
  "file_path": "agentic/DESIGN.md",
  "line_count": 95,
  "doc_type": "design"  # design | development | testing | reliability | security
}
```

### 3. Component
**Represents**: Code components/services

**Required Attributes**:
```python
{
  "id": "component_installer",
  "type": "Component",
  "name": "Installer",
  "content": "# Installer\n\n...",  # Full component doc content
  "file_path": "agentic/design-docs/components/installer.md",
  "role": "orchestrator",  # orchestrator | controller | operator | etc.
  "purpose": "Orchestrates cluster installation...",
  "responsibilities": ["Validate config", "Generate assets", "Provision infra"],
  "dependencies": ["asset-generator", "terraform-provider"],
  "api_surface": ["Installer", "Config", "State"],
  "code_files": ["pkg/installer/installer.go", "pkg/destroy/bootstrap.go"]
}
```

### 4. Concept
**Represents**: Domain concepts and patterns

**Required Attributes**:
```python
{
  "id": "concept_reconciliation",
  "type": "Concept",
  "name": "Reconciliation Pattern",
  "content": "# Reconciliation Pattern\n\n...",  # Full concept doc content
  "file_path": "agentic/domain/concepts/reconciliation-pattern.md",
  "description": "Control loop pattern for desired state management",
  "related_concepts": ["controller-pattern", "operator-pattern"]
}
```

### 5. Section
**Represents**: Document sections (from ## headers)

**Required Attributes**:
```python
{
  "id": "section_components",
  "type": "Section",
  "name": "Components",
  "content": "## Components\n\n...",  # Section content
  "parent_doc": "entrypoint_agents",
  "order": 2,
  "level": 2  # Header level (## = 2, ### = 3)
}
```

### 6. PullRequest (Optional)
**Represents**: GitHub pull requests

**Attributes**:
```python
{
  "id": "pr_729",
  "type": "PullRequest",
  "number": 729,
  "title": "Add ARM64 support",
  "state": "merged",
  "created_at": "2024-03-15",
  "merged_at": "2024-03-20",
  "author": "developer",
  "labels": ["enhancement", "architecture"],
  "files_changed": ["pkg/asset/machines/..."]
}
```

### 7. Issue (Optional)
**Represents**: GitHub issues

**Attributes**:
```python
{
  "id": "issue_23",
  "type": "Issue",
  "number": 23,
  "title": "Memory leak in pod inspector",
  "state": "open",
  "created_at": "2024-03-14",
  "labels": ["bug", "priority/high"]
}
```

### 8. JiraIssue (Optional)
**Represents**: JIRA tickets

**Attributes**:
```python
{
  "id": "jira_MULTIARCH_6002",
  "type": "JiraIssue",
  "key": "MULTIARCH-6002",
  "summary": "Add ARM64 support",
  "status": "Closed",
  "type": "Story",
  "priority": "High",
  "labels": ["arm64", "baremetal"]
}
```

## Relationship Types

### Documentation Structure

| Relationship | Source → Target | Meaning |
|--------------|-----------------|---------|
| `CONTAINS` | Document → Section | Document contains section |
| `NEXT` | Section → Section | Sequential reading order |
| `REFERENCES` | Document → Document | Cross-document reference |

### Navigation

| Relationship | Source → Target | Meaning |
|--------------|-----------------|---------|
| `DEEP_DIVE` | Section → Component/Concept | Link to detailed documentation |
| `LINKS_TO` | Component ↔ Concept | Bidirectional navigation link |

### Semantic Relationships

| Relationship | Source → Target | Meaning |
|--------------|-----------------|---------|
| `EXPLAINED_BY` | Component → Concept | Component implements concept |
| `DEPENDS_ON` | Component → Component | Code dependency |
| `MANAGES` | Component → Component | Lifecycle management |

### Historical (Optional)

| Relationship | Source → Target | Meaning |
|--------------|-----------------|---------|
| `CHANGED_IN` | Component → PullRequest | Component modified by PR |
| `DISCUSSED_IN` | Component → Issue | Component discussed in issue |
| `REFERENCES` | PR/Issue → JiraIssue | GitHub references JIRA |

## Critical Requirements

### 1. Content Embedding

**ALL document and component nodes MUST have content embedded**:

```python
# ✅ CORRECT
G.add_node(
    "component_installer",
    type="Component",
    name="Installer",
    content="# Installer\n\n**Role**: orchestrator\n\n...",  # Full content
    ...
)

# ❌ WRONG - No content embedded
G.add_node(
    "component_installer",
    type="Component",
    name="Installer",
    file_path="agentic/design-docs/components/installer.md",  # File path only
    ...
)
```

**Why**: The `/ask` skill retrieves ALL data from the in-memory graph with NO file I/O.

### 2. Navigation Constraint

**All nodes MUST be reachable within 3 hops from EntryPoint**:

```python
import networkx as nx

# Verify reachability
entry_point = "entrypoint_agents"
reachable = nx.single_source_shortest_path_length(G, entry_point, cutoff=3)

unreachable = [n for n in G.nodes() if n not in reachable]
assert len(unreachable) == 0, f"Unreachable nodes: {unreachable}"
```

### 3. Single Entry Point

**Graph MUST have exactly ONE EntryPoint node**:

```python
entry_points = [n for n, d in G.nodes(data=True) if d.get('type') == 'EntryPoint']
assert len(entry_points) == 1, f"Expected 1 EntryPoint, found {len(entry_points)}"
```

### 4. Required Node Types

**Graph MUST contain**:
- At least 1 EntryPoint
- At least 1 Component
- At least 1 Concept

### 5. Non-Empty Graph

**Graph MUST have**:
- Nodes > 0
- Edges > 0

## Loading the Graph

### In `/ask` skill:

```python
import json
import networkx as nx
from networkx.readwrite import json_graph
from pathlib import Path

# 1. Check graph exists
graph_path = Path.cwd() / "agentic" / "knowledge-graph" / "graph.json"

if not graph_path.exists():
    raise FileNotFoundError(
        f"Knowledge graph not found at {graph_path}. "
        "Run /create to generate it."
    )

# 2. Load JSON
with open(graph_path) as f:
    graph_data = json.load(f)

# 3. Create NetworkX graph
G = json_graph.node_link_graph(graph_data)

# 4. Validate
assert G.number_of_nodes() > 0, "Graph is empty"
assert G.number_of_edges() > 0, "Graph has no edges"

# 5. Use for retrieval (NO FILE I/O BEYOND THIS POINT)
result = query_graph(G, "how does the installer work?")
```

## Generating the Graph

### In `/create` skill:

```python
import json
import networkx as nx
from networkx.readwrite import json_graph
from pathlib import Path

# 1. Create graph
G = nx.DiGraph()

# 2. Add EntryPoint node with content
with open("AGENTS.md") as f:
    agents_content = f.read()

G.add_node(
    "entrypoint_agents",
    type="EntryPoint",
    name="AGENTS.md",
    content=agents_content,
    file_path="AGENTS.md",
    line_count=len(agents_content.split('\n'))
)

# 3. Add component nodes with content
for comp_file in Path("agentic/design-docs/components").glob("*.md"):
    with open(comp_file) as f:
        content = f.read()
    
    component_name = comp_file.stem.replace('-', ' ').title()
    
    G.add_node(
        f"component_{comp_file.stem}",
        type="Component",
        name=component_name,
        content=content,  # ← Critical: embed content
        file_path=str(comp_file),
        ...
    )

# 4. Add edges
G.add_edge("entrypoint_agents", "component_installer", relationship="DEEP_DIVE")

# 5. Save to canonical location
output_dir = Path.cwd() / "agentic" / "knowledge-graph"
output_dir.mkdir(parents=True, exist_ok=True)

data = json_graph.node_link_data(G)

with open(output_dir / "graph.json", 'w') as f:
    json.dump(data, f, indent=2)
```

## Validation

### Use `validate-knowledge-graph` skill:

```python
from skills.validate_knowledge_graph import validate

result = validate(Path.cwd())

if result["passed"]:
    print(f"✅ Graph valid: {result['statistics']['total_nodes']} nodes")
else:
    print(f"❌ Validation failed:")
    for issue in result["issues"]:
        print(f"  - {issue}")
```

## Size Considerations

### Typical Sizes:

- Small repository (5 components): ~500KB
- Medium repository (15 components): ~2MB
- Large repository (50 components): ~10MB

### With GitHub/JIRA data:
- +100 PRs: ~500KB
- +100 issues: ~300KB
- +50 JIRA tickets: ~200KB

**Total**: Usually 1-15MB depending on repository size and history

### Memory Usage:

Loading into NetworkX:
- Small graph (500KB): ~5MB RAM
- Large graph (15MB): ~50MB RAM

**Acceptable** for in-memory retrieval on modern systems.

## Best Practices

### 1. Always Embed Content

```python
# ✅ DO THIS
node_data = {
    "type": "Component",
    "name": "Installer",
    "content": full_content_string,  # Embed content
    "file_path": "agentic/design-docs/components/installer.md"  # Keep reference
}
```

### 2. Validate After Generation

```python
# Always validate after generating
result = validate_knowledge_graph(repo_path)
assert result["passed"], f"Graph validation failed: {result['issues']}"
```

### 3. Keep Graph Fresh

Regenerate when documentation changes:
```bash
/create  # Regenerates docs + graph
```

### 4. Use Graph for All Queries

```python
# ✅ CORRECT - Query from graph
answer = query_graph(G, question)

# ❌ WRONG - Don't read files during retrieval
with open("agentic/design-docs/components/installer.md") as f:
    content = f.read()  # NO! Content should come from graph
```

## Summary

**Key Points**:
1. ✅ Graph location: `<repo>/agentic/knowledge-graph/graph.json`
2. ✅ Format: NetworkX node-link JSON
3. ✅ Content: Embedded in nodes (no file I/O during retrieval)
4. ✅ Navigation: ≤3 hops from EntryPoint
5. ✅ Validation: Use `validate-knowledge-graph` skill
6. ✅ Usage: Load once, query many times from memory

**Date**: 2026-04-24  
**Version**: 1.0.0
