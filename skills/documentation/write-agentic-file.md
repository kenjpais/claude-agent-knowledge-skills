---
name: write-agentic-file
description: Write or update files in the agentic/ documentation directory with validation
type: documentation
category: generation
---

# Write Agentic File

## Overview
Atomic operation for writing or updating documentation files in the agentic/ directory. Includes validation, logging, and git integration.

## When to Use
- When generating new documentation files
- When updating existing documentation
- After synthesis phase produces output
- When linking phase adds navigation

## Process
1. Validate inputs:
   - File path within agentic/ directory
   - Content is valid markdown
   - Frontmatter present if required
   - Line count within budget if specified
2. Check if file exists:
   - If exists: Create backup, preserve git history
   - If new: Ensure parent directory exists
3. Write content using Write tool
4. Validate written file:
   - Markdown syntax valid
   - Links are well-formed (not necessarily reachable yet)
   - Frontmatter parses correctly
5. Log write operation with file hash
6. Return status with validation results

## Verification
- [ ] Path validated (within agentic/)
- [ ] Content validated (valid markdown)
- [ ] Frontmatter validated if present
- [ ] File written successfully
- [ ] Backup created if updating existing file
- [ ] Operation logged
- [ ] File hash computed for change detection

## Input Schema
```yaml
file_path: string
content: string
frontmatter: object | null
validation_rules:
  max_lines: integer | null
  require_frontmatter: boolean
  allowed_sections: array<string> | null
create_backup: boolean
```

## Output Schema
```yaml
success: boolean
file_path: string
action: string  # created | updated
file_hash: string
line_count: integer
validation_results:
  markdown_valid: boolean
  frontmatter_valid: boolean
  links_valid: boolean
  budget_met: boolean
warnings: array<string>
```

## Frontmatter Schema
```yaml
---
title: string
type: string  # component | concept | adr | reference
last_updated: string  # ISO 8601
confidence: float | null  # For inferred content
tags: array<string>
---
```

## Rationalizations
| Excuse | Rebuttal |
|--------|----------|
| "I'll skip validation to save time" | Validation prevents broken docs from entering the system. Non-negotiable. |
| "I don't need to log file writes" | Logging is required for auditing and debugging. Always log. |
