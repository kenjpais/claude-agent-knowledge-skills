---
name: check-placeholders
description: Detect unreplaced template placeholders, line number references, absolute paths, and external images
type: validation
category: quality
---

# Check Placeholders & References

## Overview
Detects content that should have been replaced during documentation generation: template placeholders, line-number code references (which rot quickly), absolute paths in links, and external images in AGENTS.md.

## When to Use
- After generating documentation from templates
- As part of content validation
- Before marking documentation as complete

## Process

### 1. Unreplaced Placeholder Detection
Scan all `.md` files in `agentic/` and `AGENTS.md` for these patterns:
- `[REPO-NAME]` or `[repo-name]`
- `[Component1]`, `[Component2]`, `[Component#]`
- `[Concept1]`, `[Concept2]`, `[Concept#]`
- `[YOUR-*]` (e.g., `[YOUR-ORG]`, `[YOUR-REPO]`)
- `[TODO*]` or `[TODO:*]`
- `[INSERT*]`
- `[PLACEHOLDER*]`
- `[TBD*]`
- `{{placeholder}}` mustache-style placeholders

For each match, report the file, line number, and matched text.

### 2. Line Number Reference Detection
Scan all `.md` files for code references containing line numbers:
- Pattern: `filename.ext:NNN` (e.g., `main.go:42`)
- Pattern: `filename.ext#LNNN` (e.g., `main.go#L42`)
- Pattern: `#L\d+` in link URLs

Line numbers change frequently and should not appear in documentation. Use file paths only.

### 3. Absolute Path Detection
Scan all markdown links `[text](path)` for absolute paths:
- Links starting with `/` (e.g., `[foo](/agentic/bar.md)`)
- All links must use relative paths (e.g., `[foo](./agentic/bar.md)`)
- Exclude HTTP/HTTPS URLs from this check

### 4. External Image Detection
Scan `AGENTS.md` specifically for external image references:
- `![alt](*.png)`, `![alt](*.jpg)`, `![alt](*.jpeg)`
- `![alt](*.gif)`, `![alt](*.svg)`, `![alt](*.webp)`
- Any `<img src=` tags
- AGENTS.md must use ASCII diagrams only, no external images

## Verification
- [ ] All `.md` files scanned for placeholders
- [ ] Placeholder patterns matched case-insensitively
- [ ] Line number references detected
- [ ] Absolute paths in links detected
- [ ] External images in AGENTS.md detected
- [ ] Each violation reports file, line, and matched text

## Input Schema
```yaml
repository_path: string
agentic_directory: string
agents_md_path: string  # Usually "AGENTS.md"
```

## Output Schema
```yaml
success: boolean
passed: boolean
metrics:
  total_files_scanned: integer
  placeholder_violations: integer
  line_number_violations: integer
  absolute_path_violations: integer
  external_image_violations: integer
violations: array<Violation>
  - file: string
    line: integer
    rule: string  # "placeholder", "line-number", "absolute-path", "external-image"
    matched: string
    suggestion: string
```

## Red Flags
- **Any unreplaced placeholder**: Documentation was generated but not customized — template artifacts remain
- **Line numbers in code refs**: Will rot on next code change — use file paths only
- **Absolute paths**: Break portability across clones and forks — use relative paths
- **Images in AGENTS.md**: External images are not renderable in all agent contexts — use ASCII diagrams
