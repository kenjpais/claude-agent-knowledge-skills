---
name: check-directory-structure
description: Validate required directories exist and follow naming conventions
type: validation
category: quality
---

# Check Directory Structure

## Overview
Validates that the `agentic/` directory contains all required subdirectories and that directory names follow conventions (lowercase, hyphens for word separation).

## When to Use
- After generating documentation
- As part of structural validation (Phase 1)
- Before running deeper content checks

## Process
1. Verify `agentic/` directory exists (not `docs/`)
2. Check all 12 required directories exist:
   - `agentic/design-docs/`
   - `agentic/design-docs/components/`
   - `agentic/domain/`
   - `agentic/domain/concepts/`
   - `agentic/domain/workflows/`
   - `agentic/exec-plans/`
   - `agentic/exec-plans/active/`
   - `agentic/exec-plans/completed/`
   - `agentic/product-specs/`
   - `agentic/decisions/`
   - `agentic/references/`
   - `agentic/generated/`
3. Scan all directories under `agentic/` for naming violations:
   - Must be lowercase
   - Must use hyphens for word separation (not underscores or spaces)
   - Must not contain special characters
4. Report missing directories and naming violations

## Verification
- [ ] `agentic/` exists (not `docs/`)
- [ ] All 12 required directories checked
- [ ] Missing directories listed
- [ ] Directory naming conventions verified
- [ ] Naming violations reported with fix suggestions

## Input Schema
```yaml
repository_path: string
agentic_directory: string  # Usually "agentic"
```

## Output Schema
```yaml
success: boolean
passed: boolean
metrics:
  required_directories: 12
  present_directories: integer
  missing_directories: array<string>
  naming_violations: array<NamingViolation>
    - directory: string
      issue: string  # "uppercase", "underscore", "space"
      suggested: string
```

## Red Flags
- **`docs/` used instead of `agentic/`**: Wrong directory convention
- **Missing `exec-plans/active/` or `exec-plans/completed/`**: Exec-plan lifecycle tracking broken
- **Underscore in directory name**: Convention violation, may break cross-repo tooling
