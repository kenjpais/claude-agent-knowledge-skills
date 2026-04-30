---
name: check-frontmatter-fields
description: Validate document-type-specific YAML frontmatter fields
type: validation
category: quality
---

# Check Frontmatter Fields

## Overview
Validates that each document type in `agentic/` has the correct YAML frontmatter fields. Different document types require different fields — this check enforces per-type requirements.

## When to Use
- After generating documentation
- As part of content validation (Phase 4)
- When new documents are added to any `agentic/` subdirectory

## Process

### 1. Parse Frontmatter
For each `.md` file in `agentic/`, extract YAML frontmatter (content between opening `---` and closing `---` at the top of the file). If no frontmatter exists, flag as a violation.

### 2. Determine Document Type by Location
Map each file to its type based on directory:

| Directory | Document Type | Skip |
|---|---|---|
| `agentic/exec-plans/active/` | exec-plan | `template.md` |
| `agentic/exec-plans/completed/` | exec-plan | `template.md` |
| `agentic/decisions/` | ADR | `adr-template.md`, `index.md` |
| `agentic/domain/concepts/` | concept | `index.md` |
| `agentic/product-specs/` | product-spec | `index.md` |
| `agentic/domain/workflows/` | workflow | `index.md` |
| `agentic/design-docs/components/` | component | `index.md` |

### 3. Validate Required Fields by Type

**Exec-plans** (`agentic/exec-plans/active/`, `agentic/exec-plans/completed/`):
- `status` — required, string (e.g., "active", "completed", "paused")
- `owner` — required, string
- `created` — required, date (YYYY-MM-DD)
- `target` — required, date (YYYY-MM-DD)

**ADRs** (`agentic/decisions/`):
- `id` — required, string matching `adr-NNNN`
- `title` — required, string
- `date` — required, date (YYYY-MM-DD)
- `status` — required, string (e.g., "accepted", "proposed", "deprecated", "superseded")
- `deciders` — required, string or array

**Concept docs** (`agentic/domain/concepts/`):
- `concept` — required, string
- `type` — required, string
- `related` — required, array of strings

**Product specs** (`agentic/product-specs/`):
- `feature` — required, string
- `status` — required, string
- `owner` — required, string

**Workflow docs** (`agentic/domain/workflows/`):
- `workflow` — required, string
- `components` — required, array of strings
- `related_concepts` — required, array of strings

**Component docs** (`agentic/design-docs/components/`):
- `component` — required, string
- `type` — required, string
- `related` — required, array of strings

### 4. Report violations with file path, document type, and missing fields

## Verification
- [ ] All `.md` files in `agentic/` scanned
- [ ] Frontmatter parsed as valid YAML
- [ ] Document type determined from directory
- [ ] Template and index files skipped
- [ ] Required fields checked per type
- [ ] Missing fields reported with file path

## Input Schema
```yaml
agentic_directory: string
```

## Output Schema
```yaml
success: boolean
passed: boolean
metrics:
  total_files: integer
  files_with_frontmatter: integer
  files_missing_frontmatter: integer
  field_violations: integer
violations: array<Violation>
  - file: string
    document_type: string
    missing_fields: array<string>
    invalid_fields: array<InvalidField>
      - field: string
        expected_type: string
        actual_value: string
```

## Red Flags
- **No frontmatter at all**: File may be a template artifact or improperly generated
- **Missing `status` on ADR**: Cannot determine if decision is active or superseded
- **Missing `related` on concept/component**: Cross-linking will break — navigation suffers
- **Missing `owner` on exec-plan**: No accountability for execution tracking
