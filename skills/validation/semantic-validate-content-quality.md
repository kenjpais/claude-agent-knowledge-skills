---
name: semantic-validate-content-quality
description: LLM-based validation of content minimalism, token efficiency, and execution plan quality
type: validation
category: semantic
---

# Semantic Content Quality Validation

## Overview
Detects content anti-patterns that inflate token cost without improving agent task success: narrative disguised as structure, duplicated information, prescriptive language, unnecessary tutorials, and low-substance execution plans. These require semantic judgment — not line counting.

## When to Use
- After generating documentation
- When docs feel verbose but pass line-budget checks
- As part of semantic validation phase

## Process

### Category B: Content Quality & Minimalism (6 checks)

1. **Narrative Detection** — Detect explanatory narrative disguised as structured content. Flag: bullet-pointed paragraphs (bullets > 2 sentences), multi-sentence table cells, "The system works by..." style prose in lists. Severity: WARN.

2. **Content Duplication** — Detect the same information repeated across multiple files. Example: identical component description appearing in AGENTS.md, ARCHITECTURE.md, AND the component doc. Recommend a single source of truth with links from other locations. Severity: WARN.

3. **Prescriptive vs. Descriptive** — Flag "always use X", "never do Y", "you must" instructions in any doc except Key Invariants in AGENTS.md. Agentic docs should describe what the codebase does, not prescribe developer behavior. Severity: WARN.

4. **README/Existing-Docs Duplication** — Compare agentic docs against the repo's README.md, CONTRIBUTING.md, and `docs/` directory. Flag content that duplicates existing documentation. Recommend replacing with `See: [existing doc](path)`. Severity: WARN.

5. **Unnecessary Tutorial Content** — Flag step-by-step tutorials, exhaustive code examples (more than 1-2 canonical examples), and verbose walkthroughs. These belong in `docs/` or a wiki, not agentic docs. Severity: WARN.

6. **Token Efficiency** — Assess whether each doc provides unique value proportional to its length. Flag verbose sections that could be removed or condensed without losing information an AI agent would use for tasks. Suggest concise alternatives. Severity: WARN.

### Category D: Execution Plan Quality (3 checks)

7. **Goal Clarity and Measurability** — Assess exec-plan goals in `agentic/exec-plans/active/`. Flag vague goals ("improve performance") vs. specific ones ("reduce P99 latency below 200ms on endpoint X"). Check for measurable success criteria. Severity: WARN.

8. **Plan-Codebase Alignment** — Verify exec-plans reference actual components, code paths, and packages in the target repo. Flag plans that describe work on non-existent systems or use wrong package names. Severity: FAIL.

9. **Plan Completeness** — Verify exec-plans cover required sections with substance: Goal, Context, Technical Approach, Implementation Phases, Testing Strategy. Flag boilerplate sections and generic phase descriptions copied from templates. Severity: WARN.

## Verification
- [ ] All non-ADR docs checked for narrative patterns
- [ ] Cross-file duplication detected
- [ ] Prescriptive language flagged (except Key Invariants)
- [ ] Comparison against README/docs/ completed
- [ ] Tutorial content identified
- [ ] Exec-plans evaluated for substance vs. boilerplate

## Input Schema
```yaml
repository_path: string
agentic_directory: string
readme_path: string  # Usually README.md
docs_directory: string  # Usually docs/
```

## Output Schema
```yaml
passed: boolean
summary:
  checks_run: 9
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
- **Same paragraph in 3+ files**: Clear duplication — consolidate immediately
- **Exec-plan referencing non-existent packages**: Plan was generated without reading the actual codebase
- **Entire section removable without agent impact**: Token waste — trim or remove
