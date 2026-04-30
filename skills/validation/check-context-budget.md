---
name: check-context-budget
description: Simulate standard workflows and verify each stays within context budget
type: validation
category: quality
---

# Check Context Budget

## Overview
Simulates 5 standard agent workflows by following documentation navigation paths and summing the line counts of all documents that would be loaded. Each workflow must consume ≤700 lines total to stay within an agent's effective context budget.

## When to Use
- After generating or restructuring documentation
- As part of quality score calculation
- When validating documentation is agent-friendly

## Process

### 1. Define Workflows
Simulate these 5 representative workflows by following links from AGENTS.md:

**Workflow 1: Bug Fix (Simple)**
- Load: AGENTS.md → target component doc → 1 related concept
- Expected path: 3 documents

**Workflow 2: Bug Fix (Complex)**
- Load: AGENTS.md → ARCHITECTURE.md → target component doc → 2 related concepts → 1 workflow doc
- Expected path: 5-6 documents

**Workflow 3: Feature Implementation**
- Load: AGENTS.md → DESIGN.md → DEVELOPMENT.md → target component doc → 2 related concepts
- Expected path: 5-6 documents

**Workflow 4: Understanding System**
- Load: AGENTS.md → ARCHITECTURE.md → 3 component docs → glossary
- Expected path: 5-6 documents

**Workflow 5: Security Review**
- Load: AGENTS.md → SECURITY.md → RELIABILITY.md → 2 component docs
- Expected path: 4-5 documents

### 2. Simulate Each Workflow
For each workflow:
1. Start from AGENTS.md
2. Follow the defined navigation path
3. For each document in the path, count its non-empty lines
4. Sum total lines across all documents in the workflow
5. Compare against budget limit (default: 700 lines)

### 3. Evaluate Results
- **Pass**: All 5 workflows ≤ budget limit
- **Warning**: 1 workflow over budget
- **Fail**: 2+ workflows over budget

### 4. Identify Budget Violations
For workflows over budget:
- Report total lines consumed
- Report lines per document in the path
- Identify the largest document contributing to the overage
- Suggest which document to trim

## Verification
- [ ] All 5 workflows simulated
- [ ] Line counts accurate (non-empty lines)
- [ ] Total per workflow calculated
- [ ] Budget limit applied (default 700)
- [ ] Over-budget workflows identified
- [ ] Largest contributors flagged

## Input Schema
```yaml
repository_path: string
agentic_directory: string
budget_limit: integer  # Default: 700 lines
workflows:
  - name: string
    documents: array<string>  # Ordered list of doc paths to load
```

## Output Schema
```yaml
success: boolean
passed: boolean
budget_limit: integer
workflows:
  - name: string
    total_lines: integer
    within_budget: boolean
    documents:
      - path: string
        lines: integer
    over_by: integer  # 0 if within budget
    largest_document: string
metrics:
  workflows_within_budget: integer  # out of 5
  max_lines_consumed: integer
  avg_lines_consumed: float
```

## Red Flags
- **Any workflow > 900 lines**: Severely over budget — agent will lose context
- **AGENTS.md alone > 150 lines**: Entry point consuming too much budget
- **Single component doc > 100 lines**: Violates line budget and inflates every workflow touching it
- **All workflows near limit (650-700)**: No headroom — any doc growth will cause failures
