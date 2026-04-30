---
name: semantic-validate-content-consistency
description: LLM-based validation of cross-document semantic consistency and repo-specific content accuracy
type: validation
category: semantic
---

# Semantic Content Consistency Validation

## Overview
Detects semantic inconsistencies across the documentation corpus: glossary definitions that contradict concept docs, terminology drift between files, component roles that don't match across docs, and repo-specific content (OpenShift markers, enhancement references) that is inaccurate.

## When to Use
- After generating documentation across multiple files
- When multiple docs reference the same concepts
- As part of semantic validation phase

## Process

### Category C: Cross-Document Semantic Consistency (4 checks)

1. **Glossary-Concept Doc Alignment** — Compare each term in `agentic/domain/glossary.md` against its corresponding concept doc in `agentic/domain/concepts/`. Flag semantic mismatches where the glossary definition contradicts or diverges from the detailed concept doc. Glossary entries should be faithful 1-2 sentence summaries. Severity: FAIL.

2. **Terminology Consistency (Corpus-Wide)** — Scan all doc types (AGENTS.md, ARCHITECTURE.md, concept docs, workflow docs, component docs, exec-plans, glossary) for the same concept referred to by different names without established aliases. Example: "MCD" vs "MachineConfigDaemon" vs "the daemon" used inconsistently. Severity: WARN.

3. **Component-Workflow Coherence** — For each workflow doc in `agentic/domain/workflows/`: verify that the roles assigned to components match what the component docs describe as their responsibilities. Flag misaligned responsibility assignments. Severity: WARN.

4. **Index File Content Accuracy** — For each `index.md` file: verify that document descriptions and categorizations match actual document content. For `agentic/decisions/index.md`: verify ADR status listed in the index matches the `status` field in each ADR's frontmatter. Severity: WARN.

### Category E: Repo-Specific Content Relevance (3 checks)

5. **OpenShift Marker Accuracy** — *(OpenShift repos only)* For glossary terms with markers: verify `🔴` (OpenShift-specific), `⚫` (Kubernetes core), and `🟡` (extended ecosystem) are correctly assigned. Flag misclassified terms. Skip if no markers present. Severity: WARN.

6. **Enhancement-ADR Linkage** — *(OpenShift repos only)* For ADRs with `enhancement-refs` in frontmatter: verify the referenced OpenShift enhancement proposal matches the ADR's decision topic. Flag linkages where the ADR and enhancement discuss different subjects. Severity: WARN.

7. **Core Beliefs Relevance** — Verify `agentic/design-docs/core-beliefs.md` contains principles that are evidenced in the codebase (not generic platitudes). Check that "Example in this repo" references point to real, relevant code. Flag principles with no concrete evidence. Severity: WARN.

## Verification
- [ ] Glossary compared against concept docs
- [ ] Terminology scanned across all doc types
- [ ] Workflow component roles cross-checked
- [ ] Index descriptions verified against content
- [ ] OpenShift markers validated (if applicable)
- [ ] Enhancement-ADR links cross-referenced (if applicable)
- [ ] Core beliefs checked for codebase evidence

## Input Schema
```yaml
agentic_directory: string
glossary_path: string  # agentic/domain/glossary.md
is_openshift_repo: boolean  # Enables checks 5-6
```

## Output Schema
```yaml
passed: boolean
summary:
  checks_run: integer  # 4-7 depending on repo type
  passed: integer
  failed: integer
  warnings: integer
  skipped: integer  # OpenShift checks skipped for non-OpenShift repos
findings: array<Finding>
  - check: string
    severity: string  # PASS, FAIL, WARN, SKIP
    affected_files: array<string>
    evidence: string
    recommendation: string
```

## Red Flags
- **Glossary contradicts concept doc**: Agents will get conflicting answers depending on which doc they read
- **Same concept, 3+ names across docs**: Terminology drift — pick one canonical name, alias the rest in glossary
- **Core beliefs with no code evidence**: Generic filler — either ground in code or remove
