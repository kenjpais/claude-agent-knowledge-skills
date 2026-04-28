---
name: check-file-naming
description: Validate file naming conventions across agentic documentation
type: validation
category: quality
---

# Check File Naming

## Overview
Validates that all files in `agentic/` follow naming conventions: lowercase with hyphens, and document-type-specific patterns for ADRs, concepts, workflows, and exec-plans.

## When to Use
- After generating or adding documentation files
- As part of content validation
- When new files are added to `agentic/`

## Process
1. List all `.md` files under `agentic/`
2. **Lowercase check**: All filenames must be lowercase, except these exempted files:
   - `AGENTS.md`, `ARCHITECTURE.md`
   - `DESIGN.md`, `DEVELOPMENT.md`, `TESTING.md`
   - `RELIABILITY.md`, `SECURITY.md`, `QUALITY_SCORE.md`
3. **Hyphen check**: Filenames must use hyphens for word separation, not underscores or spaces
4. **ADR naming pattern**: Files in `agentic/decisions/` (except `adr-template.md` and `index.md`) must match `adr-NNNN-*.md` where NNNN is a 4-digit zero-padded number
5. **Concept naming**: Files in `agentic/domain/concepts/` must match `[a-z][a-z0-9-]*\.md`
6. **Workflow naming**: Files in `agentic/domain/workflows/` must match `[a-z][a-z0-9-]*\.md`
7. **Exec-plan naming**: Files in `agentic/exec-plans/active/` must match `[a-z][a-z0-9-]*\.md`
8. Report all violations with suggested corrections

## Verification
- [ ] All `.md` files scanned
- [ ] Exempted uppercase files excluded from lowercase check
- [ ] Underscore and space violations detected
- [ ] ADR naming pattern validated
- [ ] Concept/workflow/exec-plan naming validated
- [ ] Fix suggestions provided for each violation

## Input Schema
```yaml
agentic_directory: string
exempted_uppercase_files:
  - AGENTS.md
  - ARCHITECTURE.md
  - DESIGN.md
  - DEVELOPMENT.md
  - TESTING.md
  - RELIABILITY.md
  - SECURITY.md
  - QUALITY_SCORE.md
```

## Output Schema
```yaml
success: boolean
passed: boolean
metrics:
  total_files: integer
  violations: integer
  details: array<NamingViolation>
    - file: string
      rule: string  # "lowercase", "underscore", "adr-pattern", "concept-pattern", etc.
      issue: string
      suggested: string
```

## Red Flags
- **Uppercase filenames** (outside exemptions): Inconsistent naming breaks convention
- **Underscores in filenames**: Use hyphens instead (`auth-controller.md` not `auth_controller.md`)
- **ADR without zero-padded number**: Must be `adr-0001-title.md` not `adr-1-title.md`
- **Generic names**: `controller.md` instead of `auth-controller.md` — names should be descriptive
