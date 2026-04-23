---
name: check-navigation-depth
description: Validate that any information is reachable within 3 hops from AGENTS.md
type: validation
category: quality
---

# Check Navigation Depth

## Overview
Enforces the critical ≤3 hop navigation constraint. All information must be reachable from AGENTS.md within three clicks.

## When to Use
- After generating or updating documentation
- Before marking documentation as complete
- As part of CI validation pipeline
- When validation agent performs quality checks

## Process
1. Start from AGENTS.md as root
2. Parse all markdown links in the document
3. For each linked document (hop 1):
   - Parse its links (hop 2)
   - Parse links from those documents (hop 3)
4. Identify all reachable files within 3 hops
5. List all markdown files in agentic/ directory
6. Find orphaned files (unreachable in 3 hops)
7. Report violations and navigation paths
8. Calculate navigation depth distribution

## Verification
- [ ] AGENTS.md exists and parsed
- [ ] All links followed recursively
- [ ] Depth correctly calculated
- [ ] Orphaned files identified
- [ ] Report generated with specific violations
- [ ] Pass/fail status determined

## Input Schema
```yaml
root_file: string  # Usually AGENTS.md
max_depth: integer  # Usually 3
agentic_directory: string
```

## Output Schema
```yaml
success: boolean
passed: boolean  # True if no violations
metrics:
  total_files: integer
  reachable_files: integer
  orphaned_files: integer
  max_depth_found: integer
violations: array<Violation>
  - file: string
    depth: integer | null  # null if orphaned
    path: array<string>  # Navigation path from root
navigation_distribution:
  depth_0: integer  # AGENTS.md
  depth_1: integer
  depth_2: integer
  depth_3: integer
  unreachable: integer
```

## Red Flags
- **Orphaned files > 0**: Documentation not linked from navigation
- **Max depth > 3**: Progressive disclosure violated
- **Depth 1 files > 15**: AGENTS.md likely over-linked, need intermediate index pages
