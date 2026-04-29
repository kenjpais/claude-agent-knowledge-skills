---
skill_id: validate-agentic-docs
name: Validate Agentic Documentation
category: validation
version: 1.0.0
trigger: /validate
description: Validate existing agentic documentation against repository content and framework constraints
agents: [validator, curator]
---

# Validate Agentic Documentation

**Trigger**: `/validate`  
**Purpose**: Validate existing agentic documentation against repository content and framework constraints

## Overview

This skill validates that agentic documentation meets all quality constraints, is synchronized with code, and provides effective navigation for AI agents.

## Input

**Repository Path or GitHub URL** (optional - defaults to current directory)

```
/validate [path/to/repository | github-url]
```

**Examples**:
```bash
/validate                                                  # Current directory
/validate /path/to/openshift-installer                   # Local repository path
/validate https://github.com/openshift/installer         # GitHub URL (auto-clones)
/validate github.com/openshift/installer                 # GitHub URL (auto-clones)
```

## Auto-Cloning

If a GitHub URL is provided and the repository is not already cloned:

1. **Parse GitHub URL**: Extract owner and repository name
2. **Clone locally**: `git clone <url> /tmp/agentic-repos/<repo-name>`
3. **Use cloned path**: Continue with validation in cloned repository
4. **Validate from**: `<cloned-repo>/agentic/` directory

**Clone location**: `/tmp/agentic-repos/<repo-name>/`

**Supported URL formats**:
- `https://github.com/owner/repo`
- `https://github.com/owner/repo.git`
- `github.com/owner/repo`
- `git@github.com:owner/repo.git`

## Validation Checks

### 1. Structure Validation

**Check**: Required files exist

**Required Files**:
- ✅ `AGENTS.md` (root)
- ✅ `agentic/DESIGN.md`
- ✅ `agentic/DEVELOPMENT.md`
- ✅ `agentic/TESTING.md`
- ✅ `agentic/RELIABILITY.md`
- ✅ `agentic/SECURITY.md`
- ✅ `agentic/QUALITY_SCORE.md`

**Required Directories**:
- ✅ `agentic/design-docs/components/`
- ✅ `agentic/domain/concepts/`

### 2. Navigation Depth Validation

**Check**: All docs reachable in ≤3 hops from AGENTS.md

**Validation Method**:
1. Parse AGENTS.md for all links
2. Recursively follow links, tracking depth
3. Report any docs beyond 3 hops
4. Flag orphaned documents (unreachable)

**Skill Used**: `check-navigation-depth`

### 3. Line Budget Validation

**Check**: Document lengths within limits

| Document Type | Limit | Validation |
|---------------|-------|------------|
| AGENTS.md | ≤150 lines | Count non-empty lines |
| Component docs | ≤100 lines | Each file in components/ |
| Concept docs | ≤75 lines | Each file in concepts/ |

**Skill Used**: `validate-line-budgets`

### 4. Link Validation

**Check**: No broken links

**Validation Method**:
1. Extract all markdown links `[text](path)`
2. Check each target file exists
3. Check each anchor exists (if `#anchor` specified)
4. Report broken links

**Skill Used**: `validate-links`

### 5. Coverage Validation

**Check**: All components documented

**Validation Method**:
1. Scan repository for components (directories, packages, modules)
2. Check each component has corresponding doc in `design-docs/components/`
3. Calculate coverage percentage
4. Report undocumented components

**Scoring**: Coverage = (documented / total) × 40 points

### 6. Freshness Validation

**Check**: Documentation updated recently

**Validation Method**:
1. Get last modified date of each doc file
2. Get last modified date of corresponding source files
3. Check docs updated within 90 days of source changes
4. Calculate staleness percentage

**Scoring**: Freshness = (fresh / total) × 20 points

**Skill Used**: `check-freshness`

### 7. Completeness Validation

**Check**: All required sections present

**For Component Docs**:
- ✅ Purpose section
- ✅ Key responsibilities
- ✅ Dependencies
- ✅ Related components

**For Concept Docs**:
- ✅ Definition
- ✅ Why it matters
- ✅ When to use
- ✅ Related concepts

**Scoring**: Completeness = (complete / total) × 20 points

### 8. Quality Score Calculation

**Total Score**: 100 points

| Category | Points | Description |
|----------|--------|-------------|
| Coverage | 40 | % of components documented |
| Freshness | 20 | Docs updated within 90 days |
| Completeness | 20 | Required sections present |
| Linkage | 10 | No broken links |
| Navigation | 10 | All docs ≤3 hops |

**Pass Threshold**: ≥70/100

**Skill Used**: `check-quality-score`

### 9. Directory Structure Validation

**Check**: All 12 required subdirectories exist and follow naming conventions

**Required Directories**:
- ✅ `agentic/design-docs/`
- ✅ `agentic/design-docs/components/`
- ✅ `agentic/domain/`
- ✅ `agentic/domain/concepts/`
- ✅ `agentic/domain/workflows/`
- ✅ `agentic/exec-plans/`
- ✅ `agentic/exec-plans/active/`
- ✅ `agentic/exec-plans/completed/`
- ✅ `agentic/product-specs/`
- ✅ `agentic/decisions/`
- ✅ `agentic/references/`
- ✅ `agentic/generated/`

**Naming Convention**: Directories must be lowercase with hyphens (no underscores or spaces).

**Skill Used**: `check-directory-structure`

### 10. File Naming Validation

**Check**: All filenames follow conventions

| Rule | Scope | Pattern |
|------|-------|---------|
| Lowercase | All `.md` files (with exemptions) | `[a-z][a-z0-9-]*\.md` |
| Hyphens not underscores | All `.md` files | `word-word.md` not `word_word.md` |
| ADR naming | `agentic/decisions/` | `adr-NNNN-title.md` |
| Concept naming | `agentic/domain/concepts/` | `concept-name.md` |
| Workflow naming | `agentic/domain/workflows/` | `workflow-name.md` |
| Exec-plan naming | `agentic/exec-plans/active/` | `feature-name.md` |

**Exempted from lowercase**: `AGENTS.md`, `ARCHITECTURE.md`, `DESIGN.md`, `DEVELOPMENT.md`, `TESTING.md`, `RELIABILITY.md`, `SECURITY.md`, `QUALITY_SCORE.md`

**Skill Used**: `check-file-naming`

### 11. Placeholder & Reference Validation

**Check**: No unreplaced template artifacts

**Detects**:
- Unreplaced placeholders: `[REPO-NAME]`, `[Component#]`, `[TODO*]`, `[INSERT*]`, `[PLACEHOLDER*]`, `{{placeholder}}`
- Line numbers in code references: `file.go:42`, `file.go#L42`
- Absolute paths in links: `[text](/path)` (must use relative paths)
- External images in AGENTS.md: `![alt](image.png)` (must use ASCII diagrams)

**Skill Used**: `check-placeholders`

### 12. AGENTS.md & ARCHITECTURE.md Content Validation

**Check**: Required sections present, content follows rules

**AGENTS.md must contain** (8 required sections):
1. Repo description (1-2 sentences)
2. Quick navigation by intent
3. Repo structure overview
4. Component boundaries (ASCII diagram)
5. Core concepts table
6. Key invariants
7. Critical code locations
8. Build/test commands

**AGENTS.md must NOT contain**: Long prose paragraphs, code blocks > 10 lines, detailed design rationale.

**ARCHITECTURE.md** (if present): Prose ratio must be ≤50% (tables/lists, not narrative). Must contain critical code locations and data flow diagram.

**Skill Used**: `check-agents-md-sections`

### 13. Frontmatter Field Validation

**Check**: Document-type-specific YAML frontmatter fields present

| Document Type | Directory | Required Fields |
|---|---|---|
| Exec-plan | `exec-plans/active/`, `exec-plans/completed/` | `status`, `owner`, `created`, `target` |
| ADR | `decisions/` | `id`, `title`, `date`, `status`, `deciders` |
| Concept | `domain/concepts/` | `concept`, `type`, `related` |
| Product spec | `product-specs/` | `feature`, `status`, `owner` |
| Workflow | `domain/workflows/` | `workflow`, `components`, `related_concepts` |
| Component | `design-docs/components/` | `component`, `type`, `related` |

**Skill Used**: `check-frontmatter-fields`

### 14. Stale TODO Detection

**Check**: No stale TODO/FIXME/HACK/XXX comments

**Thresholds**:
- ⚠️ Warning: TODO in file not updated in > 30 days
- ❌ Error: More than 5 stale TODO files across `agentic/`

**Action**: Move stale items to `agentic/exec-plans/tech-debt-tracker.md` or resolve them.

**Skill Used**: `check-stale-todos`

### 15. Context Budget Validation

**Check**: Standard agent workflows stay within ≤700 lines

**Simulated Workflows**:
1. Bug Fix (Simple): AGENTS.md → component → concept (3 docs)
2. Bug Fix (Complex): AGENTS.md → ARCHITECTURE.md → component → 2 concepts → workflow (5-6 docs)
3. Feature Implementation: AGENTS.md → DESIGN.md → DEVELOPMENT.md → component → 2 concepts (5-6 docs)
4. Understanding System: AGENTS.md → ARCHITECTURE.md → 3 components → glossary (5-6 docs)
5. Security Review: AGENTS.md → SECURITY.md → RELIABILITY.md → 2 components (4-5 docs)

**Pass**: All 5 workflows ≤ 700 lines. **Warning**: 1 over. **Fail**: 2+ over.

**Skill Used**: `check-context-budget`

### 16. Semantic ADR Validation

**Check**: ADR content quality — faithfulness, reasoning, alternatives, coherence (LLM-based, 13 sub-checks)

**Evaluates**: Source faithfulness, reasoning soundness, decision-driver alignment, alternatives analysis quality, consequence completeness, context sufficiency, semantic coherence, decision actionability, terminology consistency, code reference accuracy, scope/granularity, cross-ADR redundancy, tone/objectivity.

**Severity**: Mix of FAIL (faithfulness, coherence, code accuracy) and WARN (reasoning, alternatives, tone).

**Skill Used**: `semantic-validate-adr`

### 17. Semantic Content Grounding Validation

**Check**: Documentation is grounded in actual code and serves its purpose (LLM-based, 6 sub-checks)

**Evaluates**: Code reference accuracy (do paths/functions exist?), concept definition accuracy (match CRDs/types?), component boundary accuracy (diagrams match imports?), navigation path completeness, repo description accuracy, invariants enforcement.

**Severity**: FAIL for code refs, concept defs, invariants. WARN for navigation, description, boundaries.

**Skill Used**: `semantic-validate-content-grounding`

### 18. Semantic Content Quality Validation

**Check**: Content minimalism and execution plan substance (LLM-based, 9 sub-checks)

**Evaluates**: Narrative detection, content duplication across files, prescriptive vs descriptive language, README/docs duplication, unnecessary tutorials, token efficiency, exec-plan goal clarity, plan-codebase alignment, plan completeness.

**Severity**: FAIL for plan-codebase alignment. WARN for all others.

**Skill Used**: `semantic-validate-content-quality`

### 19. Semantic Content Consistency Validation

**Check**: Cross-document semantic consistency (LLM-based, 4-7 sub-checks)

**Evaluates**: Glossary-concept doc alignment, corpus-wide terminology consistency, component-workflow coherence, index file accuracy. For OpenShift repos: marker accuracy, enhancement-ADR linkage, core beliefs relevance.

**Severity**: FAIL for glossary contradictions. WARN for terminology drift, index inaccuracy. SKIP for non-OpenShift checks.

**Skill Used**: `semantic-validate-content-consistency`

### 20. Semantic Knowledge Graph Validation

**Check**: Graph semantic quality and retrieval readiness (LLM-based, 14 sub-checks)

**Evaluates**: Edge type accuracy, node type classification, content-to-graph consistency, label clarity, missing relationships, semantic redundancy, concept coverage, edge plausibility, workflow sequence coherence, progressive disclosure, ADR traceability, cross-document consistency, hallucination detection, retrieval simulation (3-5 queries).

**Severity**: FAIL for edge types, node types, traceability, contradictions, hallucinations. WARN for others.

**Skill Used**: `semantic-validate-knowledge-graph`

## Output

### Validation Report

```markdown
# Validation Report

**Repository**: {repo-name}  
**Date**: {timestamp}  
**Overall Score**: {score}/100

## Summary

✅ **PASS** - Documentation meets quality standards
⚠️  **WARNING** - Some issues found but acceptable
❌ **FAIL** - Critical issues must be addressed

## Detailed Results

### Structure (Pass/Fail)
- ✅ All required files present
- ✅ All required directories present

### Navigation Depth (Pass/Fail)
- ✅ Max depth: 2 hops (limit: 3)
- ✅ No orphaned documents

### Line Budgets (Pass/Fail)
- ✅ AGENTS.md: 145 lines (limit: 150)
- ⚠️  Component X: 105 lines (limit: 100) - OVER BY 5
- ✅ All concept docs within limit

### Links (Pass/Fail)
- ✅ 0 broken links found

### Coverage (40 points)
- Score: 35/40 (87.5%)
- 7/8 components documented
- Missing: component-name

### Freshness (20 points)
- Score: 18/20 (90%)
- 9/10 docs fresh (updated within 90 days)
- Stale: old-component.md (180 days)

### Completeness (20 points)
- Score: 20/20 (100%)
- All docs have required sections

### Directory Structure (Pass/Fail)
- ✅ 12/12 required directories present
- ✅ No naming convention violations

### File Naming (Pass/Fail)
- ✅ All filenames follow conventions
- ✅ ADR naming patterns valid

### Placeholders & References (Pass/Fail)
- ✅ No unreplaced placeholders
- ✅ No line number references
- ✅ All links use relative paths

### AGENTS.md Sections (Pass/Fail)
- ✅ 8/8 required sections present
- ⚠️  ARCHITECTURE.md prose ratio: 55% (limit: 50%)

### Frontmatter Fields (Pass/Fail)
- ✅ All concept docs have required fields
- ⚠️  1 ADR missing `deciders` field

### Stale TODOs (Pass/Fail)
- ✅ 2 stale TODOs (limit: 5)

### Context Budget (Pass/Fail)
- ✅ All workflows within 700 lines
- Max: 620 lines (Feature Implementation)

### Semantic: ADR Quality (13 checks)
- ✅ 11 passed, 2 warnings
- ⚠️  ADR-0002: Alternatives Analysis — one alternative appears to be a strawman

### Semantic: Content Grounding (6 checks)
- ✅ 5 passed, 1 warning
- ⚠️  Component boundary diagram missing pkg/operator dependency

### Semantic: Content Quality (9 checks)
- ✅ 8 passed, 1 warning
- ⚠️  DESIGN.md duplicates README.md setup instructions

### Semantic: Content Consistency (4-7 checks)
- ✅ 4 passed, 0 warnings
- ⏭️  3 OpenShift checks skipped (not an OpenShift repo)

### Semantic: Knowledge Graph (14 checks)
- ✅ 12 passed, 2 warnings
- ⚠️  2 missing relationships: concept-to-workflow edges

### Quality Score: 88/100 ✅ PASS

## Recommendations

1. Document missing component: component-name
2. Update stale documentation: old-component.md
3. Reduce component X to ≤100 lines

## Next Steps

- Run `/create` to regenerate specific components
- Update stale docs manually or via curator
- Re-validate: `/validate`
```

### QUALITY_SCORE.md Update

Updates `agentic/QUALITY_SCORE.md` with latest scores:

```markdown
---
last_updated: {timestamp}
overall_score: 88
status: PASS
---

# Quality Score

**Overall**: 88/100 ✅

## Scores by Category

- **Coverage**: 35/40 (87.5%)
- **Freshness**: 18/20 (90%)
- **Completeness**: 20/20 (100%)
- **Linkage**: 10/10 (100%)
- **Navigation**: 10/10 (100%)

## Trend

| Date | Score | Status |
|------|-------|--------|
| 2026-04-24 | 88 | PASS ✅ |
| 2026-04-20 | 85 | PASS ✅ |
| 2026-04-15 | 72 | PASS ✅ |
```

## Usage

```bash
# In Claude Code
/validate

# Or with path
/validate /path/to/repository

# Or via Makefile
make validate /path/to/repository

# Or via Python utility
python utilities/validation/validator.py /path/to/repository
```

## Implementation

When this skill is invoked:

1. **Check Documentation Exists**
   - Verify `AGENTS.md` exists
   - Verify `agentic/` directory exists
   - Exit early if no docs found

2. **Run All Validations**
   - Structure validation (required files)
   - Navigation depth validation
   - Line budget validation
   - Link validation
   - Coverage validation
   - Freshness validation
   - Completeness validation
   - Directory structure validation
   - File naming validation
   - Placeholder & reference validation
   - AGENTS.md & ARCHITECTURE.md section validation
   - Frontmatter field validation
   - Stale TODO detection
   - Context budget validation
   - Semantic ADR validation
   - Semantic content grounding validation
   - Semantic content quality validation
   - Semantic content consistency validation
   - Semantic knowledge graph validation

3. **Calculate Quality Score**
   - Sum all category scores
   - Compare against threshold (70)
   - Determine status (PASS/WARNING/FAIL)

4. **Generate Reports**
   - Create validation report
   - Update QUALITY_SCORE.md
   - Log results

5. **Report to User**
   - Show summary (score, status)
   - List critical issues
   - Provide recommendations

## Error Handling

**No Documentation Found**:
- Error: "No agentic documentation found at: {path}"
- Action: Suggest running `/create` first

**Partial Documentation**:
- Warning: "Incomplete documentation structure"
- Action: Continue validation, report missing files

**Validation Script Errors**:
- Error: "Validation failed: {error}"
- Action: Report error, continue with other validations

## Success Criteria

Validation is successful when:

✅ All validations completed  
✅ Score calculated accurately  
✅ Reports generated  
✅ Results communicated to user  

## Configuration

**Thresholds** (configurable in validator):
- Quality score pass threshold: 70/100
- Freshness threshold: 90 days
- Max navigation depth: 3 hops
- Line budgets: AGENTS.md 150, components 100, concepts 75
- Context budget per workflow: 700 lines
- Stale TODO warning: 30 days
- Stale TODO error: > 5 stale files
- ARCHITECTURE.md prose ratio: ≤50%

## Logging

All validation operations logged to:
- `agentic/exec-plans/active/validate-{timestamp}.md` (during validation)
- `agentic/exec-plans/completed/validate-{timestamp}.md` (after completion)

## Related Skills

**Uses**:
- `check-navigation-depth` - Validate navigation structure
- `check-quality-score` - Calculate comprehensive score
- `validate-line-budgets` - Check document lengths
- `validate-links` - Check for broken links
- `check-freshness` - Check documentation staleness
- `check-directory-structure` - Validate required directories and naming
- `check-file-naming` - Validate filename conventions
- `check-placeholders` - Detect unreplaced placeholders, line numbers, absolute paths, images
- `check-agents-md-sections` - Validate AGENTS.md/ARCHITECTURE.md content
- `check-frontmatter-fields` - Validate per-type frontmatter requirements
- `check-stale-todos` - Detect stale TODO/FIXME comments
- `check-context-budget` - Simulate workflows and verify context budget
- `semantic-validate-adr` - LLM-based ADR quality validation (13 checks)
- `semantic-validate-content-grounding` - LLM-based code grounding validation (6 checks)
- `semantic-validate-content-quality` - LLM-based content minimalism validation (9 checks)
- `semantic-validate-content-consistency` - LLM-based cross-doc consistency validation (4-7 checks)
- `semantic-validate-knowledge-graph` - LLM-based graph quality validation (14 checks)
- `read-file` - Read documentation files
- `get-git-history` - Get file modification times

**Used By**:
- Validator agent (primary consumer)
- Curator agent (continuous validation)

## Integration

**With `/create`**:
- Run `/validate` after `/create` to verify generation
- Auto-runs during creation pipeline

**With Curator Agent**:
- Validator runs periodically to detect staleness
- Triggers regeneration when quality drops

**With CI/CD**:
- Can run as pre-commit hook
- Can run in CI pipeline to enforce quality

## Example Session

```
User: /validate