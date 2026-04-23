---
name: list-files
description: List files in repository with optional filtering
type: repo
category: access
---

# List Files

## Overview
Discovers and lists files in the target repository with support for pattern matching, directory filtering, and file type selection.

## When to Use
- Initial repository discovery phase
- Finding files matching specific patterns (*.go, *.yaml, etc.)
- Identifying directories for component boundary analysis
- Locating specific file types for extraction

## Process
1. Accept directory path and optional filters (pattern, extension, exclude)
2. Use Bash find command to list files matching criteria
3. Filter out ignored paths (.git, node_modules, vendor, etc.)
4. Log discovery operation
5. Return structured file list with metadata

## Verification
- [ ] Filters applied correctly
- [ ] Ignored paths excluded
- [ ] File list returned with paths relative to repo root
- [ ] Discovery operation logged

## Input Schema
```yaml
directory: string
pattern: string | null  # e.g., "*.go", "*.yaml"
max_depth: integer | null
exclude_dirs: array<string>
```

## Output Schema
```yaml
success: boolean
files: array<FileInfo>
  - path: string
    size: integer
    modified: string
count: integer
```
