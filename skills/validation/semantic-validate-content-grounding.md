---
name: semantic-validate-content-grounding
description: LLM-based validation that documentation content is grounded in actual code and serves its stated purpose
type: validation
category: semantic
---

# Semantic Content Grounding Validation

## Overview
Validates that non-ADR documentation is grounded in the actual codebase (file paths exist, definitions match code, diagrams reflect real structure) and that AGENTS.md functionally serves its navigation purpose. These checks require reading both docs and source code to compare.

## When to Use
- After generating documentation from code analysis
- When validating that docs haven't drifted from code
- As part of semantic validation phase

## Process

### Category A: Source Grounding & Hallucination Detection (3 checks)

1. **Code Reference Accuracy** — For every file path, function name, package name, and component name referenced in AGENTS.md, ARCHITECTURE.md, concept docs, workflow docs, and component docs: verify the reference actually exists in the target repo. Flag non-existent references. Severity: FAIL.

2. **Concept Definition Accuracy** — For each concept doc in `agentic/domain/concepts/`: compare the definition against underlying CRDs, type definitions, and actual code behavior. Verify that documented fields, states, and transitions actually exist. Severity: FAIL.

3. **Component Boundary Accuracy** — For ASCII diagrams and component relationship tables in AGENTS.md and ARCHITECTURE.md: compare against actual code structure (import graphs, package dependencies, controller registrations). Flag relationships that don't exist in code or missing relationships that do. Severity: WARN.

### Category F: AGENTS.md Functional Assessment (3 checks)

4. **Navigation Path Completeness** — Test each "Quick Navigation by Intent" path in AGENTS.md (understand system, implement feature, fix bug, understand concept). Follow the links and assess whether the path actually serves its stated intent. Flag paths that lead to irrelevant docs or dead ends. Severity: WARN.

5. **Repo Description Accuracy** — Compare the 1-2 sentence repo description in AGENTS.md against what the code actually does (check README.md, go.mod/package.json, main entry points). Flag descriptions that are inaccurate, vague, or aspirational. Severity: WARN.

6. **Invariants Accuracy** — For each item in "Key Invariants" section: verify it is actually enforced in the codebase via tests, webhooks, linting, CI checks, or assertions. Verify "Validated by" references exist. Flag aspirational invariants not enforced anywhere. Severity: FAIL.

## Verification
- [ ] All non-ADR docs scanned for code references
- [ ] Concept definitions compared against actual code
- [ ] Component diagrams compared against import structure
- [ ] AGENTS.md navigation paths followed and tested
- [ ] Repo description compared against actual codebase
- [ ] Invariants verified against enforcement mechanisms

## Input Schema
```yaml
repository_path: string
agentic_directory: string
agents_md_path: string
```

## Output Schema
```yaml
passed: boolean
summary:
  checks_run: 6
  passed: integer
  failed: integer
  warnings: integer
findings: array<Finding>
  - check: string
    severity: string  # PASS, FAIL, WARN
    affected_file: string
    evidence: string
    recommendation: string
```

## Red Flags
- **Code references to non-existent files**: Documentation was generated from stale analysis or hallucinated
- **Concept definitions contradicting CRDs**: Dangerous for agents acting on this information
- **Aspirational invariants**: Creates false confidence — agents may skip validation assuming enforcement exists
