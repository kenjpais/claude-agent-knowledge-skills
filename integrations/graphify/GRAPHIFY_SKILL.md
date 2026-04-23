---
name: graphify
description: Generate knowledge graphs from repository for enhanced navigation and querying
type: integration
category: knowledge-graph
---

# Graphify Integration

## Overview
Integrates the graphify tool (https://github.com/safishamsi/graphify) as a Claude skill for knowledge graph generation. Graphify transforms code, docs, images, and videos into queryable knowledge graphs with community clustering.

## Installation

### 1. Install Graphify
```bash
# Clone and install graphify
git clone https://github.com/safishamsi/graphify
cd graphify
pip install -e .

# Or via pip (when available)
pip install graphify
```

### 2. Install Claude Code Hook
```bash
# From within your target repository
graphify claude install
```

This installs a PreToolUse hook that surfaces `GRAPH_REPORT.md` before file searches, enabling structure-based navigation.

### 3. Update CLAUDE.md
Graphify automatically adds a section to the repository's CLAUDE.md with usage instructions.

## Usage in Documentation Generation

### During Extraction Phase
Run graphify after initial file discovery to enhance extraction:

```bash
# Generate knowledge graph for entire repository
graphify . --output graph.json

# Or for specific components
graphify pkg/controller/ --output controller-graph.json
```

### Output Artifacts
Graphify produces:
1. **graph.html** - Interactive visualization
2. **GRAPH_REPORT.md** - Analysis with god nodes, connections, suggested questions
3. **graph.json** - Queryable graph for programmatic access
4. **cache/** - SHA256 caching for efficient re-runs

### Integration Points

#### 1. Enhanced Component Boundary Detection
Use graphify's community detection to inform `infer-component-boundary` skill:

```python
# Load graphify output
with open('graph.json') as f:
    graph = json.load(f)

# Extract community clusters
communities = graph['communities']

# Use as input to component boundary inference
# Graphify's Leiden clustering provides high-quality boundaries
```

#### 2. Concept Extraction
Graphify extracts concepts from docs, code, and comments:

```python
# Extract concepts from graph
concepts = [node for node in graph['nodes'] if node['type'] == 'concept']

# Use to seed domain/concepts/ documentation
for concept in concepts:
    generate_concept_doc(concept['name'], concept['relationships'])
```

#### 3. Relationship Mapping
Use graphify's relationship extraction for linking:

```python
# Extract relationships
relationships = graph['edges']

# Filter by confidence
high_conf_rels = [r for r in relationships if r['confidence'] == 'EXTRACTED']

# Use for link-concepts-to-components skill
```

#### 4. Code Navigation Queries
Enable graphify querying in retrieval agent:

```bash
# Query knowledge graph
graphify query "what connects Machine to MachineController?"

# Find paths
graphify path "Machine CRD" "MachineController"

# Explain nodes
graphify explain "Reconciler"
```

## Graphify Skill Definition

### Input Schema
```yaml
target_path: string  # Directory or file to analyze
output_file: string  # Default: graph.json
include_types: array<string>  # [code, docs, images, video]
confidence_threshold: string  # EXTRACTED | INFERRED | AMBIGUOUS
```

### Output Schema
```yaml
success: boolean
graph_file: string
report_file: string
html_file: string
metrics:
  total_nodes: integer
  total_edges: integer
  communities: integer
  confidence_distribution:
    extracted: integer
    inferred: integer
    ambiguous: integer
```

### Integration with Agent Workflow

#### Extractor Agent Enhancement
After running standard extraction skills, run graphify:

1. Run extractor's parsing skills as normal
2. Run graphify on repository:
   ```
   graphify . --output extracted/knowledge-graph.json
   ```
3. Load graphify results
4. Merge with extraction artifacts:
   - Use graphify's community clusters to validate component boundaries
   - Use graphify's concept extraction to seed concept docs
   - Use graphify's relationships to enhance dependency graph

#### Synthesizer Agent Enhancement
When generating component docs, use graphify data:

1. Load knowledge graph from `extracted/knowledge-graph.json`
2. For each component:
   - Query graph for related nodes
   - Use relationship confidence scores
   - Include graph-derived insights in doc
3. Generate "Related" sections using graph traversal

#### Retrieval Agent Enhancement
Integrate graphify querying:

1. On retrieval query, check if graph exists
2. If yes:
   - Use `graphify query` to find related concepts
   - Traverse graph to find shortest paths
   - Use graph structure for recommendations
3. Return graph-informed results

## Graph Report Format
Graphify generates `GRAPH_REPORT.md`:

```markdown
# Knowledge Graph Report

Generated: 2026-04-23

## Statistics
- Nodes: 234
- Edges: 567
- Communities: 12

## God Nodes (High Centrality)
1. Machine (45 connections)
2. MachineController (38 connections)
3. Reconciler (32 connections)

## Surprising Connections
- Machine CRD → CloudProvider (via providerSpec)
- MachineController → GarbageCollector (finalizer pattern)

## Suggested Exploration Questions
1. What components interact with Machine resources?
2. How does the reconciliation loop work?
3. What are the failure modes for machine creation?

## Communities
### Cluster 1: Machine Management
- Machine, MachineSet, MachineDeployment
- MachineController, MachineSetController

### Cluster 2: Cloud Provider Integration
- AWSProvider, GCPProvider, AzureProvider
- ProviderSpec, MachineConfig
```

## Benefits for Documentation

### 1. Improved Component Boundaries
Graphify's Leiden clustering provides statistically sound component boundaries based on actual code relationships, not just directory structure.

### 2. Concept Discovery
Automatically discovers domain concepts from code, docs, and comments without manual curation.

### 3. Relationship Confidence
Tags relationships as EXTRACTED (definite), INFERRED (probable), or AMBIGUOUS (uncertain), allowing quality filtering.

### 4. Query Efficiency
Claims 71.5x fewer tokens per query vs reading raw files by enabling targeted graph traversal.

### 5. No Embeddings Required
Uses graph topology for clustering instead of vector embeddings, avoiding embedding model dependencies.

## Workflow Integration Example

```yaml
# Full Documentation Generation with Graphify
orchestrator:
  phases:
    1_discovery:
      - list-files
      - get-git-history
      
    2_extraction:
      - build-dependency-graph
      - extract-go-structs
      - extract-kubernetes-crds
      - run-graphify  # <-- Graphify integration
      
    3_synthesis:
      - infer-component-boundary  # Uses both dep-graph and graphify
      - classify-service-role
      - generate-component-doc  # Enhanced with graph relationships
      
    4_linking:
      - link-concepts-to-components  # Uses graphify relationships
      - generate-agents-md
      
    5_validation:
      - check-navigation-depth
      - check-quality-score
```

## Configuration

### graphify.yaml
```yaml
graphify_config:
  enabled: true
  output_directory: "extracted/"
  include_types:
    - code
    - docs
    - images
  confidence_threshold: "INFERRED"  # Include EXTRACTED and INFERRED
  cache_enabled: true
  cache_directory: "cache/"
  clustering:
    algorithm: "leiden"
    resolution: 1.0
```

## Monitoring
Log graphify operations:
```json
{
  "timestamp": "...",
  "agent_id": "extractor",
  "operation": "run-graphify",
  "resource": ".",
  "status": "success",
  "metadata": {
    "nodes": 234,
    "edges": 567,
    "communities": 12,
    "duration_ms": 45000
  }
}
```

## References
- Graphify GitHub: https://github.com/safishamsi/graphify
- Leiden Algorithm: Community detection for graph clustering
- Knowledge Graph best practices: Use for navigation, not as source of truth
