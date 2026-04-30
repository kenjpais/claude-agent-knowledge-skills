---
name: semantic-validate-adr
description: LLM-based semantic validation of ADR quality, faithfulness, and reasoning
type: validation
category: semantic
---

# Semantic ADR Validation

## Overview
Reads each ADR in `agentic/decisions/` and evaluates semantic quality: whether claims are grounded in source material, reasoning is sound, alternatives are genuine, and the document serves as a useful architectural record. Requires LLM reasoning — not pattern matching.

## When to Use
- After generating or updating ADRs
- As part of semantic validation phase
- When ADRs are created from PR/Jira data

## Process
For each ADR file in `agentic/decisions/` (skip `adr-template.md`, `index.md`):

### Checks to Run (13 total)

1. **Source Faithfulness** — Compare claims against PR descriptions, Jira tickets, and code changes referenced in provenance. Flag fabricated details or unverifiable assertions. Severity: FAIL.

2. **Reasoning Soundness** — Evaluate the Rationale section for circular logic, unsupported assertions, and vague justifications like "it's the best approach." Severity: WARN.

3. **Decision-Driver Alignment** — Verify that stated decision drivers in Context logically connect to the chosen option in Decision. Flag disconnects. Severity: FAIL.

4. **Alternatives Analysis Quality** — Check that rejected alternatives are genuine contenders (not strawmen), evaluated against the same criteria, and rejected for substantive technical reasons. Severity: WARN.

5. **Consequence Completeness** — Verify positive and negative consequences are realistic and proportionate. Flag one-sided listings. For OpenShift repos, check operational impacts (upgrades, backward compat, CRD versioning). Severity: WARN.

6. **Context Sufficiency** — Assess whether a developer could understand the decision 6 months later without the original Jira. Flag unexplained acronyms and missing constraints. Severity: WARN.

7. **Semantic Coherence** — Verify Context → Decision → Rationale → Consequences → Implementation form a consistent narrative with no contradictions between sections. Severity: FAIL.

8. **Decision Actionability** — Check the Decision section is concrete and specific enough to act on (not "improve performance" but "replace X with Y in package Z"). Severity: WARN.

9. **Terminology Consistency** — Verify consistent term usage within the ADR. Cross-check against `agentic/domain/glossary.md` if it exists. Flag inconsistent abbreviations. Severity: WARN.

10. **Code Reference Accuracy** — Assess whether described behavior of referenced code paths is plausible given the PR context. This is semantic (does the description match what the code does?), not link validity. Severity: FAIL.

11. **Scope and Granularity** — Flag ADRs that conflate multiple unrelated decisions, document trivial implementation details, or contain decisions that should be split into separate ADRs. Severity: WARN.

12. **Cross-ADR Redundancy** — When multiple ADRs exist, compare semantically for overlap. Flag ADRs documenting essentially the same decision under different titles. Severity: WARN.

13. **Tone and Objectivity** — Verify the ADR reads as a factual record, not advocacy. Flag subjective language, emotional framing, promotional tone, and excessive hedging. Severity: WARN.

## Verification
- [ ] All ADR files read (skip templates/index)
- [ ] All 13 checks evaluated per ADR
- [ ] Cross-ADR checks run across the full set
- [ ] Each finding reports check name, severity, evidence quote, and recommendation

## Input Schema
```yaml
adr_directory: string  # agentic/decisions/
glossary_path: string  # agentic/domain/glossary.md (optional)
source_material: string  # PR/Jira context if available
```

## Output Schema
```yaml
passed: boolean
summary:
  adrs_validated: integer
  checks_run: 13
  passed: integer
  failed: integer
  warnings: integer
findings: array<Finding>
  - adr_file: string
    check: string
    severity: string  # PASS, FAIL, WARN
    evidence: string
    recommendation: string
cross_adr_findings: array<Finding>
```

## Red Flags
- **Any FAIL on Source Faithfulness**: ADR contains hallucinated content — must be corrected before use
- **Multiple ADRs failing Semantic Coherence**: Generator may be producing structurally correct but logically inconsistent documents
- **Cross-ADR Redundancy found**: Consolidate or supersede duplicates
