---
name: check-agents-md-sections
description: Validate AGENTS.md and ARCHITECTURE.md contain required sections and follow content rules
type: validation
category: quality
---

# Check AGENTS.md & ARCHITECTURE.md Sections

## Overview
Validates that AGENTS.md contains all required section patterns (it should be a navigation map, not a manual) and that ARCHITECTURE.md uses structured format with minimal prose.

## When to Use
- After generating AGENTS.md or ARCHITECTURE.md
- As part of content validation
- When verifying documentation is navigation-oriented

## Process

### 1. AGENTS.md Required Sections
Parse AGENTS.md and verify presence of sections matching these patterns (headings or content blocks):

| Required Section | Pattern to Match |
|---|---|
| Repo description | 1-2 sentence description near the top, before first heading or under a "Description"/"Overview" heading |
| Quick navigation | Heading containing "navigation" or "quick start" or "intent" |
| Repo structure | Heading containing "structure" or "layout" or "organization" |
| Component boundaries | ASCII diagram using box-drawing characters (`+`, `-`, `\|`, `┌`, `─`, `│`) OR heading containing "component" and "boundar" |
| Core concepts | Heading containing "concept" or a markdown table with concept names |
| Key invariants | Heading containing "invariant" or "constraint" or "guarantee" |
| Critical code locations | Heading containing "critical" or "important" and "code" or "file" or "location" or "path" |
| Build/test commands | Heading containing "build" or "test" or "develop", or a code block with `make`, `go test`, `npm`, `pytest` etc. |

Report missing sections by name.

### 2. AGENTS.md Prohibited Content
Check AGENTS.md does NOT contain:
- Detailed explanations (paragraphs > 3 sentences outside of tables/lists)
- Long code examples (code blocks > 10 lines)
- Design rationale (paragraphs explaining "why" at length)

Flag as warnings — AGENTS.md should be a map, not a manual.

### 3. ARCHITECTURE.md Existence
Check that `ARCHITECTURE.md` exists at repository root.

### 4. ARCHITECTURE.md Structure
If ARCHITECTURE.md exists, validate:
- **Prose ratio**: Calculate ratio of prose lines (non-empty lines outside tables, lists, code blocks, headings) to total non-empty lines. Warn if prose > 50%. ARCHITECTURE.md should be tables and structured lists.
- **Required sections**: Check for patterns matching:
  - Critical/key/important code locations (table or list of file paths)
  - Data flow or architecture diagram (ASCII diagram or heading containing "data flow" or "architecture")

## Verification
- [ ] AGENTS.md parsed for all 8 required sections
- [ ] Missing sections reported by name
- [ ] Prohibited content patterns detected
- [ ] ARCHITECTURE.md existence checked
- [ ] ARCHITECTURE.md prose ratio calculated
- [ ] ARCHITECTURE.md required sections checked

## Input Schema
```yaml
agents_md_path: string  # Usually "AGENTS.md"
architecture_md_path: string  # Usually "ARCHITECTURE.md"
```

## Output Schema
```yaml
success: boolean
passed: boolean
agents_md:
  found: boolean
  required_sections_present: integer  # out of 8
  missing_sections: array<string>
  prohibited_content_warnings: array<Warning>
    - type: string  # "long-explanation", "long-code-block", "design-rationale"
      line: integer
      detail: string
architecture_md:
  found: boolean
  prose_ratio: float  # 0.0 to 1.0
  prose_ratio_warning: boolean  # true if > 0.50
  required_sections_present: integer  # out of 2
  missing_sections: array<string>
```

## Red Flags
- **Missing > 2 sections in AGENTS.md**: Navigation map is incomplete — agents won't find key information
- **AGENTS.md has long prose paragraphs**: It's becoming a manual, not a map
- **ARCHITECTURE.md prose ratio > 50%**: Should be tables and structured lists, not narrative
- **No ARCHITECTURE.md**: Missing critical structural documentation
