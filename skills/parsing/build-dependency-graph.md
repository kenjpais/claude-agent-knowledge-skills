---
name: build-dependency-graph
description: Construct module-level and package-level dependency graph from imports
type: parsing
category: extraction
---

# Build Dependency Graph

## Overview
Analyzes import statements across all source files to construct a dependency graph showing relationships between packages and modules. Foundation for component boundary detection.

## When to Use
- Identifying component boundaries in monorepos
- Detecting circular dependencies
- Understanding code layering and architecture
- Prioritizing documentation (start with leaf nodes)
- Finding high-centrality packages (god objects)

## Process
1. Use list-files to find all source files (*.go, *.py, *.js, etc.)
2. For each file:
   - Extract package/module declaration
   - Parse import statements
   - Identify internal vs external dependencies
3. Build directed graph:
   - Nodes: packages/modules
   - Edges: import relationships
4. Calculate graph metrics:
   - In-degree (dependents)
   - Out-degree (dependencies)
   - Centrality scores
5. Detect cycles using DFS
6. Export graph in multiple formats (JSON, DOT, adjacency list)

## Verification
- [ ] All source files processed
- [ ] Import statements correctly parsed
- [ ] Internal vs external dependencies distinguished
- [ ] Cycles detected and reported
- [ ] Graph exported successfully
- [ ] Metrics calculated correctly

## Input Schema
```yaml
root_directory: string
language: string  # go | python | javascript | typescript
include_external: boolean  # Include external dependencies
max_depth: integer | null
```

## Output Schema
```yaml
success: boolean
graph:
  nodes: array<Node>
    - id: string
      label: string
      type: string  # internal | external
      file_count: integer
      centrality: float
  edges: array<Edge>
    - source: string
      target: string
      import_count: integer
metrics:
  total_packages: integer
  total_edges: integer
  cycles: array<array<string>>
  high_centrality: array<string>
```

## Red Flags
- **Cycles detected**: May indicate architectural issues requiring ADR
- **Single package with >50% centrality**: God object that needs decomposition
- **Orphan packages**: Unused code to document or remove
