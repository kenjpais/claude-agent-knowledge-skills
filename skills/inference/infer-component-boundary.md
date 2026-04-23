---
name: infer-component-boundary
description: Analyze dependency graph and code structure to infer logical component boundaries
type: inference
category: analysis
---

# Infer Component Boundary

## Overview
Uses dependency graph, directory structure, and naming conventions to identify logical component boundaries within the codebase. Probabilistic but confidence-scored.

## When to Use
- After building dependency graph
- Before generating component documentation
- When repository lacks clear component structure
- To validate assumed architecture

## Process
1. Load dependency graph from build-dependency-graph
2. Apply community detection algorithms (Louvain, Leiden)
3. Analyze directory structure for natural boundaries
4. Check for architectural markers:
   - Separate package roots
   - API boundaries (client/server separation)
   - Clear interface definitions
   - Distinct CRD groups
5. Score confidence based on:
   - Graph modularity (0-1 scale)
   - Directory alignment
   - Naming consistency
6. Identify fuzzy boundaries (packages split across components)
7. Return component definitions with confidence scores

## Verification
- [ ] Dependency graph loaded successfully
- [ ] Community detection algorithm ran
- [ ] Confidence scores calculated
- [ ] Fuzzy boundaries flagged
- [ ] Component definitions include file lists
- [ ] Results logged with confidence metrics

## Input Schema
```yaml
dependency_graph: string  # Path to graph JSON
directory_structure: array<string>
min_confidence: float  # Minimum confidence threshold (0-1)
```

## Output Schema
```yaml
success: boolean
components: array<Component>
  - name: string
    description: string
    confidence: float  # 0-1
    packages: array<string>
    files: array<string>
    boundary_type: string  # clean | fuzzy
    reasoning: string
  - fuzzy_packages: array<string>  # Packages in multiple components
overall_modularity: float
```

## Red Flags
- **Confidence < 0.5**: Component boundaries unclear, may need manual review
- **High fuzzy_packages count**: Poor separation, consider ADR
- **Modularity < 0.3**: Monolithic structure, document as single component
