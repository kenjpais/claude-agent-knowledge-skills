---
skill_id: generate-knowledge-graph
name: Generate Knowledge Graph
category: synthesis
version: 1.0.0
description: Convert agentic documentation and GitHub/JIRA data into NetworkX knowledge graph
inputs: [repository_path, database_path, agentic_docs_path]
outputs: [graph_path, statistics, node_types, relationship_types]
output_location: <repo>/agentic/knowledge-graph/graph.json
---

# Generate Knowledge Graph

**Purpose**: Transform agentic documentation and GitHub/JIRA data into an in-memory queryable NetworkX knowledge graph

## Output Location

**Required Location**: `<repo>/agentic/knowledge-graph/graph.json`

This is the canonical location where `/ask` skill will load the graph from.

**Format**: NetworkX node-link JSON format

## Knowledge Graph Schema Overview

### Node Types (9 types)

**Documentation Structure:**
- `EntryPoint` - AGENTS.md root
- `Document` - Top-level docs (DESIGN.md, DEVELOPMENT.md, etc.)
- `Section` - Document sections (from ## headers)

**Domain Model:**
- `Component` - Code components/services
- `Concept` - Domain concepts and patterns
- `Workflow` - Process flows
- `ADR` - Architecture Decision Records
- `ExecutionPlan` - Feature implementation plans

**Historical/Development:**
- `PullRequest` - GitHub PRs
- `Issue` - GitHub Issues
- `JiraIssue` - JIRA tickets

### Edge Types (12 types)

**Documentation Structure:**
- `CONTAINS` - Document → Section
- `NEXT` - Section → Section (sequential)
- `DEEP_DIVE` - Section → Component/Concept
- `REFERENCES` - Document ↔ Document, PR/Issue → JIRA
- `RELATED` - Concept ↔ Concept

**Documentation Edges:**
- `EXPLAINED_BY` - Component → Concept
- `DECIDED_BY` - Component → ADR
- `PLANNED_IN` - Feature → ExecutionPlan

**Code Structure:**
- `DEPENDS_ON` - Component → Component
- `MANAGES` - Component → Component

**Historical:**
- `CHANGED_IN` - Component → PR
- `DISCUSSED_IN` - Component → Issue

## Input Schema

```yaml
database_path: string           # Path to SQLite database (from ingest-github-data)
agentic_docs_path: string       # Path to agentic/ documentation directory
graph_name: string              # Name for the graph (default: repo name)
include_code: boolean           # Include code snippets as nodes (default: false)
```

## Output Schema

```yaml
graph_path: string              # Path to generated graph file (NetworkX node-link JSON)
statistics:
  total_nodes: integer          # Total nodes created
  total_relationships: integer  # Total relationships created
  node_types:
    # Documentation Structure
    entrypoint: integer         # EntryPoint (AGENTS.md)
    document: integer           # Top-level docs
    section: integer            # Document sections
    # Domain
    component: integer          # Components
    concept: integer            # Concepts
    workflow: integer           # Workflows
    adr: integer                # Architecture Decision Records
    execution_plan: integer     # Execution plans
    # Historical
    pull_request: integer       # GitHub PRs
    issue: integer              # GitHub issues
    jira_issue: integer         # JIRA issues
  relationship_types:
    # Documentation structure
    CONTAINS: integer           # Document → Section
    NEXT: integer               # Section → Section
    DEEP_DIVE: integer          # Section → Component/Concept
    REFERENCES: integer         # Document → Document, PR/Issue → JIRA
    RELATED: integer            # Concept ↔ Concept
    # Documentation edges
    EXPLAINED_BY: integer       # Component → Concept
    DECIDED_BY: integer         # Component → ADR
    PLANNED_IN: integer         # Feature → ExecutionPlan
    # Code structure
    DEPENDS_ON: integer         # Component → Component
    MANAGES: integer            # Component → Component
    # Historical
    CHANGED_IN: integer         # Component → PR
    DISCUSSED_IN: integer       # Component → Issue
```

## Node Types

### Documentation Structure Nodes

#### EntryPoint
- **Source**: AGENTS.md root document
- **Properties**: name, description, file_path
- **Relationships**: REFERENCES (to top-level docs), CONTAINS (sections)
- **Purpose**: Starting point for all documentation navigation

#### Document
- **Source**: Top-level documentation files (DESIGN.md, DEVELOPMENT.md, TESTING.md, etc.)
- **Properties**: name, description, file_path, doc_type
- **Relationships**: CONTAINS (sections), REFERENCES (other docs)
- **Purpose**: Major documentation categories

#### Section
- **Source**: Extracted from document headers (## level)
- **Properties**: name, description, parent_doc, order
- **Relationships**: NEXT (sequential sections), DEEP_DIVE (to details), CONTAINS (subsections)
- **Purpose**: Granular navigation within documents

### Domain Nodes

#### Component
- **Source**: agentic/design-docs/components/*.md
- **Properties**: name, role, package, api_surface, dependencies, file_paths
- **Relationships**: DEPENDS_ON, MANAGES, EXPLAINED_BY, CHANGED_IN, DISCUSSED_IN
- **Purpose**: Represent code components/services

#### Concept
- **Source**: agentic/domain/concepts/*.md
- **Properties**: name, description, related_concepts, file_path
- **Relationships**: RELATED, EXPLAINED_BY (inverse)
- **Purpose**: Domain concepts and patterns

#### Workflow
- **Source**: Extracted from documentation workflows
- **Properties**: name, description, steps[]
- **Relationships**: CONTAINS (steps), REFERENCES (components/concepts)
- **Purpose**: Process flows and execution sequences

#### ADR (Architecture Decision Record)
- **Source**: agentic/adrs/*.md (if present)
- **Properties**: number, title, status, date, context, decision
- **Relationships**: DECIDED_BY (components/features reference ADRs)
- **Purpose**: Track architectural decisions

#### ExecutionPlan
- **Source**: Feature implementation plans
- **Properties**: name, status, phases[], timeline
- **Relationships**: PLANNED_IN (features/concepts reference plans)
- **Purpose**: Track planned work and roadmap

### Historical/Development Nodes

#### PullRequest
- **Source**: SQLite database (github_prs table)
- **Properties**: number, title, author, state, created_at, merged_at, labels
- **Relationships**: CHANGED_IN (modifies components), REFERENCES (JIRA)
- **Purpose**: Track code changes

#### Issue
- **Source**: SQLite database (github_issues table)
- **Properties**: number, title, state, created_at, labels
- **Relationships**: DISCUSSED_IN (affects components), REFERENCES (JIRA)
- **Purpose**: Track bugs and feature requests

#### JiraIssue
- **Source**: SQLite database (jira_issues table) or GitHub correlations
- **Properties**: key, summary, status, reference_count
- **Relationships**: REFERENCES (from PRs/Issues)
- **Purpose**: External issue tracking integration

## Relationship Types

### Documentation Structure Edges

| Relationship | Source → Target | Meaning | Example |
|--------------|-----------------|---------|---------|
| CONTAINS | Document → Section | Document contains section | AGENTS.md → Components section |
| NEXT | Section → Section | Sequential reading order | Quick Start → Components |
| DEEP_DIVE | Section → Component/Concept | Link to detailed documentation | Components section → Pod Placement Controller |
| REFERENCES | Document → Document | Cross-document reference | AGENTS.md → DESIGN.md |
| RELATED | Concept → Concept | Lateral conceptual link | Scheduling Gates ↔ Node Affinity Injection |

### Documentation Edges (Component ↔ Docs)

| Relationship | Source → Target | Meaning | Example |
|--------------|-----------------|---------|---------|
| EXPLAINED_BY | Component → Concept | Component implements concept | Pod Controller → Architecture-Aware Scheduling |
| DECIDED_BY | Component → ADR | Component's design decided by ADR | Image Inspector → ADR-003 (Caching Strategy) |
| PLANNED_IN | Feature → ExecutionPlan | Feature tracked in execution plan | ARM64 Support → Q3 Roadmap |

### Code Structure Edges

| Relationship | Source → Target | Meaning | Example |
|--------------|-----------------|---------|---------|
| DEPENDS_ON | Component → Component | Code dependency (imports/calls) | Pod Controller → Image Inspector |
| MANAGES | Component → Component | Lifecycle management | ClusterPodPlacementConfig → Pod Controller |

### Historical Edges

| Relationship | Source → Target | Meaning | Example |
|--------------|-----------------|---------|---------|
| CHANGED_IN | Component → PullRequest | Component modified by PR | Pod Controller → PR #729 |
| DISCUSSED_IN | Component → Issue | Component discussed in issue | Image Inspector → Issue #23 |
| REFERENCES | PR/Issue → JiraIssue | GitHub references JIRA | PR #729 → MULTIARCH-6002 |

## Implementation

**Technology**: NetworkX (Python library for graph creation and manipulation)

**Output Format**: NetworkX node-link JSON (standard format, easily loadable)

### Phase 1: Extract Nodes

1. **Documentation Structure**:
   - Create EntryPoint node from AGENTS.md
   - Create Document nodes for top-level docs (DESIGN.md, DEVELOPMENT.md, etc.)
   - Parse section headers (## level) to create Section nodes
   - Link sections sequentially with NEXT relationships
   - Link EntryPoint → Documents with REFERENCES

2. **Domain Elements**:
   - Parse agentic/design-docs/components/*.md → Component nodes
   - Parse agentic/domain/concepts/*.md → Concept nodes
   - Extract workflows from documentation → Workflow nodes
   - Parse agentic/adrs/*.md → ADR nodes (if present)
   - Extract execution plans → ExecutionPlan nodes (if present)

3. **Historical Data (from Database)**:
   - Query github_prs table → PullRequest nodes
   - Query github_issues table → Issue nodes
   - Query github_jira_refs table → JiraIssue nodes

### Phase 2: Create Relationships

1. **Documentation Structure**:
   - Document CONTAINS Section (parse section headers)
   - Section NEXT Section (sequential order)
   - Section DEEP_DIVE Component/Concept (from section → detail links)
   - Document REFERENCES Document (cross-doc links)
   - Concept RELATED Concept (lateral concept links)

2. **Documentation Edges**:
   - Component EXPLAINED_BY Concept (component implements concept)
   - Component DECIDED_BY ADR (design decisions)
   - Feature PLANNED_IN ExecutionPlan (roadmap tracking)

3. **Code Structure**:
   - Component DEPENDS_ON Component (from dependency graph)
   - Component MANAGES Component (lifecycle management)

4. **Historical Edges**:
   - Component CHANGED_IN PullRequest (parse PR titles/files for component mentions)
   - Component DISCUSSED_IN Issue (parse issue titles for component mentions)
   - PullRequest/Issue REFERENCES JiraIssue (from github_jira_refs table)

### Phase 3: Embed Content in Nodes

**CRITICAL**: Store document content in graph nodes for retrieval without file I/O

```python
# For each document node, embed the actual content
for doc_file in doc_files:
    with open(doc_file) as f:
        content = f.read()
    
    # Store content in node attributes
    G.add_node(
        node_id,
        type="Document",
        name=doc_name,
        file_path=str(doc_file),
        content=content,          # ← Full content embedded
        line_count=len(content.split('\n')),
        sections=extract_sections(content)
    )

# For component nodes
G.add_node(
    "component_installer",
    type="Component",
    name="Installer",
    role="orchestrator",
    content=component_doc_content,  # ← Full doc content
    purpose="Orchestrates cluster installation...",
    responsibilities=["Validate config", "Generate assets", ...],
    dependencies=["asset-generator", "terraform-provider"],
    api_surface=["Installer", "Config", "State"],
    file_paths=["pkg/installer/installer.go", ...]
)
```

### Phase 4: Generate and Save Graph

**Using NetworkX**:

```python
import networkx as nx
from networkx.readwrite import json_graph
import json
from pathlib import Path

# Create directed graph
G = nx.DiGraph()

# Add nodes with full content embedded (see Phase 3)
# Add edges with relationships

# Ensure output directory exists
output_dir = Path(repository_path) / "agentic" / "knowledge-graph"
output_dir.mkdir(parents=True, exist_ok=True)

# Export to canonical location
output_path = output_dir / "graph.json"
data = json_graph.node_link_data(G)

with open(output_path, 'w') as f:
    json.dump(data, f, indent=2)

print(f"✅ Knowledge graph saved to: {output_path}")
```

**Output Format**: NetworkX node-link JSON
- Standard format, widely compatible
- Easy to load: `G = json_graph.node_link_graph(data)`
- Human-readable, version-controllable
- **Contains all content** - no file I/O needed for retrieval

## Success Criteria

- ✅ All agentic components represented as nodes
- ✅ All concepts represented as nodes
- ✅ PRs and issues from database included
- ✅ Dependencies correctly mapped
- ✅ Cross-references preserved
- ✅ Graph queryable for navigation (≤3 hops)

## Quality Metrics

```yaml
completeness:
  components_covered: percentage    # % of components in graph
  concepts_covered: percentage      # % of concepts in graph
  prs_included: count
  issues_included: count

connectivity:
  avg_relationships_per_node: float
  isolated_nodes: count             # Should be 0
  max_depth: integer                # Should be ≤3 from AGENTS.md

retrieval_efficiency:
  avg_query_time: milliseconds
  index_size: bytes
```

## Example Output

```yaml
graph_path: /Users/user/.agent-knowledge/graphs/multiarch-tuning-operator-graph.json
statistics:
  total_nodes: 89
  total_relationships: 72
  node_types:
    entrypoint: 1          # AGENTS.md
    document: 7            # DESIGN.md, DEVELOPMENT.md, etc.
    section: 7             # Sections within documents
    component: 6           # Pod Controller, Image Inspector, etc.
    concept: 3             # Architecture-Aware Scheduling, etc.
    workflow: 2            # Pod Placement, Operand Lifecycle
    pull_request: 30       # Recent PRs
    issue: 18              # Open/closed issues
    jira_issue: 15         # Top referenced JIRA tickets
  relationship_types:
    CONTAINS: 7            # Documents contain sections
    NEXT: 6                # Sequential section navigation
    DEEP_DIVE: 11          # Sections link to details
    REFERENCES: 13         # Document cross-refs + GitHub→JIRA
    RELATED: 2             # Concept lateral links
    EXPLAINED_BY: 4        # Components implement concepts
    DEPENDS_ON: 1          # Component dependencies
    MANAGES: 2             # Component lifecycle
    CHANGED_IN: 20         # Components modified by PRs
    DISCUSSED_IN: 10       # Components discussed in issues
```

## Integration

This skill integrates with:
- `ingest-github-data` - Consumes database output
- `create-agentic-docs` - Consumes documentation output
- `retrieve-from-graph` - Downstream consumer for queries
- `validate-agentic-docs` - Validates graph completeness

## Usage

The knowledge graph is automatically generated as part of the 5-phase agentic documentation workflow:

**Phase 4: Knowledge Graph Generation** (in `/create` workflow)

```python
# Standalone graph generation script
python generate_knowledge_graph.py \
  --database ~/.agent-knowledge/data.db \
  --agentic-docs /path/to/repo/agentic \
  --components /tmp/components.json \
  --output ~/.agent-knowledge/graphs/repo-graph.json

# Or invoke via Claude Code skill
# The skill handles all phases automatically
```

**Output**: `~/.agent-knowledge/graphs/{repo-name}-graph.json`

The graph integrates:
1. Documentation structure (EntryPoint, Documents, Sections)
2. Domain model (Components, Concepts, Workflows)
3. Historical data (PRs, Issues, JIRA)
4. All relationships between entities

## Graph Query Examples

Once generated, the graph enables efficient queries using NetworkX:

```python
import json
import networkx as nx
from networkx.readwrite import json_graph

# Load graph
with open("multiarch-tuning-operator-graph.json") as f:
    data = json.load(f)
G = json_graph.node_link_graph(data)

# Find all components modified by a specific PR
pr_node = "pr_729"
changed_components = []
for u, v, attrs in G.in_edges(pr_node, data=True):
    if attrs.get('relationship') == 'CHANGED_IN':
        node_data = G.nodes[u]
        if node_data.get('type') == 'Component':
            changed_components.append(node_data['name'])

# Find concepts that explain a component
component_node = "component_pod_placement_controller"
concepts = []
for u, v, attrs in G.out_edges(component_node, data=True):
    if attrs.get('relationship') == 'EXPLAINED_BY':
        concepts.append(G.nodes[v]['name'])

# Navigate from AGENTS.md to a component (≤3 hops)
from networkx import shortest_path
path = shortest_path(G, "entrypoint_agents", "component_pod_placement_controller")
# Returns: ['entrypoint_agents', 'section_agents_components', 'component_pod_placement_controller']

# Find all PRs that reference a JIRA issue
jira_node = "jira_MULTIARCH_6002"
prs = []
for u, v, attrs in G.in_edges(jira_node, data=True):
    if attrs.get('relationship') == 'REFERENCES' and G.nodes[u]['type'] == 'PullRequest':
        prs.append(G.nodes[u]['name'])

# Get all sections in a document
doc_node = "doc_agents_md"
sections = []
for u, v, attrs in G.out_edges(doc_node, data=True):
    if attrs.get('relationship') == 'CONTAINS':
        sections.append(G.nodes[v]['name'])
```

## Related Skills

- `ingest-github-data` - Upstream: provides database
- `create-agentic-docs` - Upstream: provides documentation
- `retrieve-from-graph` - Downstream: queries the graph
- `check-navigation-depth` - Validates ≤3 hop constraint
