---
name: get-git-history
description: Extract git commit history for files, directories, or the entire repository
type: repo
category: access
---

# Get Git History

## Overview
Retrieves git commit history with support for filtering by path, date range, and author. Essential for understanding code evolution and extracting design rationale.

## When to Use
- Identifying when components were added or modified
- Extracting architectural decisions from commit messages
- Understanding code ownership and contribution patterns
- Detecting stale or frequently changing files for documentation prioritization

## Process
1. Construct git log command with appropriate filters
2. Execute git command and parse output
3. Extract commit hash, author, date, message, and files changed
4. Identify ADR-worthy commits (major refactors, architecture changes)
5. Log history extraction operation
6. Return structured commit history

## Verification
- [ ] Git history parsed correctly
- [ ] Date ranges applied if specified
- [ ] Path filtering works correctly
- [ ] Commit messages preserved in full
- [ ] Operation logged

## Input Schema
```yaml
path: string | null  # Specific file or directory
since: string | null  # Date or relative (e.g., "3 months ago")
until: string | null
author: string | null
max_commits: integer
include_stats: boolean  # Include file change statistics
```

## Output Schema
```yaml
success: boolean
commits: array<Commit>
  - hash: string
    author: string
    date: string
    message: string
    files_changed: array<string>
    stats: object | null
total_commits: integer
```
