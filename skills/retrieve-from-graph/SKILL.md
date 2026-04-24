---
skill_id: retrieve-from-graph
name: Retrieve from Knowledge Graph
category: retrieval
version: 1.0.0
description: Query knowledge graph to retrieve documentation and related context with ≤3 hop navigation
inputs: [graph_path, query_type, query_params, max_hops]
outputs: [results, navigation_path, context, metrics]
---

# Retrieve from Knowledge Graph

**Purpose**: Efficient retrieval of documentation and context from knowledge graph with progressive disclosure

## Input Schema

```yaml
graph_path: string              # Path to knowledge graph file
query_type: string              # Query type (see Query Types below)
query_params: object            # Query-specific parameters
max_hops: integer               # Maximum navigation depth (default: 3)
include_context: boolean        # Include related nodes (default: true)
context_limit: integer          # Max lines of context (default: 500)
```

## Output Schema

```yaml
results: array                  # Query results
  - node_id: string
    node_type: string           # component, concept, pr, issue, jira, file
    name: string
    properties: object
    relevance_score: float      # 0.0-1.0

navigation_path: array          # Path taken to reach results
  - step: integer
    from_node: string
    relationship: string
    to_node: string

context: object                 # Related context
  dependencies: array           # Dependent components
  related_concepts: array       # Related concepts
  relevant_prs: array           # Relevant PRs/issues
  source_files: array           # Source file paths

metrics:
  query_time_ms: integer
  hops_used: integer            # Should be ≤3
  nodes_visited: integer
  results_returned: integer
  context_lines: integer        # Should be ≤500
```

## Query Types

### 1. component-lookup
**Purpose**: Find component by name or pattern
**Params**: 
```yaml
name: string                    # Component name or pattern
include_dependencies: boolean   # Include dependent components
```

**Example**:
```yaml
query_type: component-lookup
query_params:
  name: "pod-inspector"
  include_dependencies: true
```

### 2. concept-search
**Purpose**: Find concepts and implementing components
**Params**:
```yaml
concept_name: string            # Concept name or pattern
include_implementations: boolean # Include implementing components
```

### 3. pr-impact-analysis
**Purpose**: Find components affected by a PR
**Params**:
```yaml
pr_number: integer              # GitHub PR number
include_dependencies: boolean   # Include downstream impact
```

### 4. issue-context
**Purpose**: Get context for an issue (GitHub or JIRA)
**Params**:
```yaml
issue_id: string                # Issue number or JIRA key
source: string                  # "github" or "jira"
include_related: boolean        # Include related issues
```

### 5. architecture-path
**Purpose**: Find connection between two components
**Params**:
```yaml
from_component: string          # Source component
to_component: string            # Target component
relationship_types: array       # Filter by relationship types
```

### 6. free-text-search
**Purpose**: Search across all documentation
**Params**:
```yaml
query: string                   # Search query
node_types: array               # Filter by node types
limit: integer                  # Max results
```

## Progressive Disclosure Algorithm

Retrieval follows progressive disclosure to stay within context budget:

### Step 1: Initial Query (Hop 0)
- Execute primary query
- Return matched nodes with core properties
- Track context usage

### Step 2: First Hop (Optional)
- If context budget allows, expand to immediate neighbors
- Include direct dependencies and related concepts
- Track navigation path

### Step 3: Second Hop (Optional)
- If context budget allows and query needs more context
- Expand to second-degree connections
- Prioritize by relevance score

### Step 4: Third Hop (Maximum)
- Final expansion if needed and budget allows
- Never exceed 3 hops from starting point
- Never exceed 500 lines total context

## Context Budget Management

```python
context_budget = 500  # lines

for hop in range(max_hops):
    if current_context_lines >= context_budget:
        break
    
    # Expand to next hop
    neighbors = get_neighbors(current_nodes)
    
    # Score by relevance
    scored = score_relevance(neighbors, original_query)
    
    # Add highest-scoring neighbors until budget reached
    for node in sorted(scored, reverse=True):
        if current_context_lines + node.line_count <= context_budget:
            add_to_results(node)
            current_context_lines += node.line_count
```

## Relevance Scoring

Each node scored 0.0-1.0 based on:
- **Query match** (40%): Direct match vs query terms
- **Proximity** (30%): Hops from starting point (fewer = higher)
- **Centrality** (20%): Number of connections (hub nodes rank higher)
- **Freshness** (10%): Recent PRs/changes rank higher

## Success Criteria

- ✅ Query completes in <2 seconds
- ✅ Navigation depth ≤3 hops
- ✅ Context ≤500 lines total
- ✅ Relevant results returned (precision >80%)
- ✅ Navigation path clearly documented

## Implementation

Uses: `integrations/graphify/retrieve.py` or graph query engine

### Graph Query Execution

```python
def retrieve_from_graph(graph_path, query_type, query_params, max_hops=3):
    # Load graph
    graph = load_graph(graph_path)
    
    # Execute query based on type
    initial_nodes = execute_query(graph, query_type, query_params)
    
    # Progressive disclosure expansion
    results = []
    visited = set()
    context_lines = 0
    
    for hop in range(max_hops + 1):
        if context_lines >= 500:
            break
            
        # Get neighbors at this hop level
        neighbors = get_neighbors(graph, initial_nodes if hop == 0 else results)
        
        # Score and filter
        scored = score_nodes(neighbors, query_params)
        
        # Add to results within budget
        for node in scored:
            if node.id not in visited and context_lines + node.line_count <= 500:
                results.append(node)
                visited.add(node.id)
                context_lines += node.line_count
    
    return {
        'results': results,
        'navigation_path': build_path(results),
        'context': extract_context(results),
        'metrics': {
            'query_time_ms': elapsed_ms,
            'hops_used': hop,
            'nodes_visited': len(visited),
            'results_returned': len(results),
            'context_lines': context_lines
        }
    }
```

## Example Outputs

### Example 1: Component Lookup

**Input**:
```yaml
query_type: component-lookup
query_params:
  name: "pod-inspector"
  include_dependencies: true
max_hops: 2
```

**Output**:
```yaml
results:
  - node_id: "comp_pod_inspector"
    node_type: component
    name: pod-inspector
    properties:
      role: inspector
      api_surface: ["InspectPod", "GetPodStatus"]
      file_paths: ["pkg/inspector/pod_inspector.go"]
    relevance_score: 1.0
    
  - node_id: "comp_cluster_api"
    node_type: component
    name: cluster-api-client
    properties:
      role: api-client
    relevance_score: 0.85

navigation_path:
  - step: 0
    from_node: null
    relationship: "query"
    to_node: "comp_pod_inspector"
  - step: 1
    from_node: "comp_pod_inspector"
    relationship: "depends_on"
    to_node: "comp_cluster_api"

context:
  dependencies:
    - cluster-api-client
    - kubernetes-client
  related_concepts:
    - pod-lifecycle
    - resource-inspection
  relevant_prs:
    - {number: 1234, title: "Fix memory leak in pod inspector"}
  source_files:
    - pkg/inspector/pod_inspector.go
    - pkg/inspector/pod_status.go

metrics:
  query_time_ms: 45
  hops_used: 1
  nodes_visited: 8
  results_returned: 2
  context_lines: 287
```

### Example 2: Architecture Path

**Input**:
```yaml
query_type: architecture-path
query_params:
  from_component: "scheduler"
  to_component: "image-cache"
  relationship_types: ["depends_on", "implements"]
max_hops: 3
```

**Output**:
```yaml
results:
  - node_id: "comp_scheduler"
    node_type: component
    name: scheduler
    relevance_score: 1.0
    
  - node_id: "comp_pod_placement"
    node_type: component
    name: pod-placement-engine
    relevance_score: 0.9
    
  - node_id: "comp_image_cache"
    node_type: component
    name: image-cache
    relevance_score: 1.0

navigation_path:
  - step: 1
    from_node: "comp_scheduler"
    relationship: "depends_on"
    to_node: "comp_pod_placement"
  - step: 2
    from_node: "comp_pod_placement"
    relationship: "depends_on"
    to_node: "comp_image_cache"

metrics:
  query_time_ms: 67
  hops_used: 2
  nodes_visited: 15
  results_returned: 3
  context_lines: 412
```

## Integration

This skill integrates with:
- `generate-knowledge-graph` - Consumes generated graph
- `ask-agentic-docs` - Higher-level query interface
- `evaluate-agentic-docs` - Used by coding sub-agent for retrieval
- Coding agents - Primary consumers during development

## Constraints for Coding Agents

When used by coding agent sub-agents:
- ✅ MUST stay within ≤3 hops
- ✅ MUST stay within ≤500 lines context
- ✅ MUST report navigation path taken
- ✅ MUST report confidence level based on context retrieved

## Usage

```bash
# Via coding agent (in evaluation scenarios)
# Agent uses ask-agentic-docs which internally uses retrieve-from-graph

# Direct usage (for testing)
python integrations/graphify/retrieve.py \
  --graph ~/.agent-knowledge/graphs/installer-graph.graphml \
  --query-type component-lookup \
  --params '{"name": "pod-inspector", "include_dependencies": true}' \
  --max-hops 2
```

## Performance Optimization

- **Indexing**: Pre-index common query patterns
- **Caching**: Cache frequently accessed nodes
- **Lazy loading**: Load full content only when needed
- **Pruning**: Remove low-relevance branches early

## Related Skills

- `generate-knowledge-graph` - Upstream: creates the graph
- `ask-agentic-docs` - Wrapper: user-friendly query interface
- `evaluate-agentic-docs` - Consumer: uses for evaluation scenarios
- `check-navigation-depth` - Validator: ensures ≤3 hop constraint
