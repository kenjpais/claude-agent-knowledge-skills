---
skill_id: validate-knowledge-graph
name: Validate Knowledge Graph
category: validation
version: 1.0.0
description: Validate that knowledge graph exists, is valid NetworkX format, and contains required data
inputs: [repository_path]
outputs: [validation_result, issues, recommendations]
---

# Validate Knowledge Graph

**Purpose**: Ensure knowledge graph exists at the correct location and is properly formatted for `/ask` skill

## Validation Checks

### 1. Graph File Exists

**Check**: `<repo>/agentic/knowledge-graph/graph.json` file exists

```python
from pathlib import Path

graph_path = Path(repository_path) / "agentic" / "knowledge-graph" / "graph.json"

if not graph_path.exists():
    return {
        "passed": False,
        "issue": "Knowledge graph file not found",
        "expected_location": str(graph_path),
        "recommendation": "Run /create to generate knowledge graph"
    }
```

### 2. Valid JSON Format

**Check**: File contains valid JSON

```python
import json

try:
    with open(graph_path) as f:
        data = json.load(f)
except json.JSONDecodeError as e:
    return {
        "passed": False,
        "issue": f"Invalid JSON format: {e}",
        "recommendation": "Regenerate knowledge graph with /create"
    }
```

### 3. Valid NetworkX Format

**Check**: JSON is valid NetworkX node-link format

```python
from networkx.readwrite import json_graph

try:
    G = json_graph.node_link_graph(data)
except Exception as e:
    return {
        "passed": False,
        "issue": f"Invalid NetworkX format: {e}",
        "recommendation": "Ensure graph was generated with generate-knowledge-graph skill"
    }
```

### 4. Graph Not Empty

**Check**: Graph contains nodes and edges

```python
if G.number_of_nodes() == 0:
    return {
        "passed": False,
        "issue": "Graph contains no nodes",
        "recommendation": "Regenerate with /create"
    }

if G.number_of_edges() == 0:
    return {
        "passed": False,
        "issue": "Graph contains no edges (isolated nodes)",
        "recommendation": "Regenerate with /create to build relationships"
    }
```

### 5. Required Node Types Present

**Check**: Graph contains essential node types

```python
node_types = {node_data.get('type') for _, node_data in G.nodes(data=True)}

required_types = ['EntryPoint', 'Component', 'Concept']
missing_types = [t for t in required_types if t not in node_types]

if missing_types:
    return {
        "passed": False,
        "issue": f"Missing required node types: {missing_types}",
        "node_types_found": list(node_types),
        "recommendation": "Regenerate with /create to include all node types"
    }
```

### 6. Entry Point Node Exists

**Check**: Graph has exactly one EntryPoint node (AGENTS.md)

```python
entry_points = [n for n, d in G.nodes(data=True) if d.get('type') == 'EntryPoint']

if len(entry_points) == 0:
    return {
        "passed": False,
        "issue": "No EntryPoint node found",
        "recommendation": "Graph must have EntryPoint node for AGENTS.md"
    }

if len(entry_points) > 1:
    return {
        "passed": False,
        "issue": f"Multiple EntryPoint nodes found: {entry_points}",
        "recommendation": "Graph should have exactly one EntryPoint"
    }
```

### 7. Nodes Have Content

**Check**: Document and component nodes have content embedded

```python
nodes_missing_content = []

for node_id, node_data in G.nodes(data=True):
    node_type = node_data.get('type')
    
    # These node types must have content
    if node_type in ['EntryPoint', 'Document', 'Component', 'Concept']:
        if 'content' not in node_data or not node_data['content']:
            nodes_missing_content.append({
                'id': node_id,
                'type': node_type,
                'name': node_data.get('name', 'unknown')
            })

if nodes_missing_content:
    return {
        "passed": False,
        "issue": f"{len(nodes_missing_content)} nodes missing embedded content",
        "nodes": nodes_missing_content[:5],  # Show first 5
        "recommendation": "Regenerate graph with content embedding enabled"
    }
```

### 8. Navigation Depth

**Check**: All nodes reachable within 3 hops from EntryPoint

```python
import networkx as nx

entry_point = entry_points[0]
reachable = nx.single_source_shortest_path_length(G, entry_point, cutoff=3)

unreachable_nodes = [n for n in G.nodes() if n not in reachable]

if unreachable_nodes:
    return {
        "passed": False,
        "issue": f"{len(unreachable_nodes)} nodes unreachable within 3 hops",
        "unreachable_sample": unreachable_nodes[:5],
        "recommendation": "Add links to make all nodes reachable from AGENTS.md"
    }
```

## Output Schema

```yaml
validation_result:
  passed: boolean
  total_checks: integer
  checks_passed: integer
  checks_failed: integer

checks:
  - name: string
    passed: boolean
    issue: string (if failed)
    recommendation: string (if failed)

statistics:
  graph_size_bytes: integer
  total_nodes: integer
  total_edges: integer
  node_types:
    EntryPoint: integer
    Document: integer
    Component: integer
    Concept: integer
    PullRequest: integer
    Issue: integer
    JiraIssue: integer
  nodes_with_content: integer
  max_depth_from_entry: integer

issues: array<string>      # List of all issues found
recommendations: array<string>  # List of recommendations
```

## Success Criteria

All checks must pass:
- ✅ Graph file exists at correct location
- ✅ Valid JSON format
- ✅ Valid NetworkX node-link format
- ✅ Contains nodes and edges
- ✅ Has required node types (EntryPoint, Component, Concept)
- ✅ Has exactly one EntryPoint node
- ✅ Document/component nodes have content embedded
- ✅ All nodes reachable within 3 hops from EntryPoint

## Example Output

```yaml
validation_result:
  passed: true
  total_checks: 8
  checks_passed: 8
  checks_failed: 0

checks:
  - name: "Graph file exists"
    passed: true
  - name: "Valid JSON format"
    passed: true
  - name: "Valid NetworkX format"
    passed: true
  - name: "Graph not empty"
    passed: true
  - name: "Required node types present"
    passed: true
  - name: "Entry point exists"
    passed: true
  - name: "Nodes have content"
    passed: true
  - name: "Navigation depth ≤3 hops"
    passed: true

statistics:
  graph_size_bytes: 524288
  total_nodes: 89
  total_edges: 127
  node_types:
    EntryPoint: 1
    Document: 7
    Component: 12
    Concept: 8
    PullRequest: 45
    Issue: 16
  nodes_with_content: 28
  max_depth_from_entry: 3

issues: []
recommendations: []
```

## Integration

This skill is called by:
- `/create` skill - After generating knowledge graph
- `/validate` skill - As part of overall validation
- `/ask` skill - Before loading graph for queries

## Usage

```python
# In /create workflow
result = validate_knowledge_graph(repository_path)

if not result["passed"]:
    print(f"❌ Knowledge graph validation failed:")
    for issue in result["issues"]:
        print(f"  - {issue}")
    
    print(f"\nRecommendations:")
    for rec in result["recommendations"]:
        print(f"  - {rec}")
    
    # Attempt to regenerate graph
    regenerate_knowledge_graph()
else:
    print(f"✅ Knowledge graph valid")
    print(f"   Nodes: {result['statistics']['total_nodes']}")
    print(f"   Edges: {result['statistics']['total_edges']}")
```

## Error Handling

If validation fails, the skill should:
1. Report specific issues found
2. Provide actionable recommendations
3. Return enough detail for automated fixes
4. Not fail silently - always return validation result

## Related Skills

- `generate-knowledge-graph` - Creates the graph being validated
- `retrieve-from-graph` - Uses validated graph for queries
- `ask-agentic-docs` - Requires validated graph to function
