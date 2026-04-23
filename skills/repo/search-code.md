---
name: search-code
description: Search for code patterns, symbols, or text across repository
type: repo
category: access
---

# Search Code

## Overview
Performs grep-based searches across the repository to find code patterns, function definitions, type declarations, or text occurrences.

## When to Use
- Finding all usages of a function or type
- Locating specific patterns (e.g., "reconcile", "controller")
- Discovering API endpoints or handlers
- Identifying configuration references

## Process
1. Sanitize search query to prevent injection
2. Construct appropriate grep command with context
3. Execute search with file type filtering if specified
4. Parse results into structured format
5. Log search operation with query and result count
6. Return matches with file, line number, and context

## Verification
- [ ] Search query sanitized
- [ ] Results include file path and line numbers
- [ ] Search operation logged
- [ ] No false positives from binary files

## Input Schema
```yaml
query: string
case_sensitive: boolean
file_pattern: string | null
max_results: integer
include_context: boolean  # Include surrounding lines
```

## Output Schema
```yaml
success: boolean
matches: array<Match>
  - file: string
    line_number: integer
    line_content: string
    context_before: array<string>
    context_after: array<string>
total_matches: integer
```
