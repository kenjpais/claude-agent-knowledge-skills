---
name: validator
description: Enforces framework constraints, calculates quality metrics, and triggers feedback loops
type: agent
phase: validation
---

# Validator Agent

## Responsibilities
- Validate documentation structure and completeness
- Enforce navigation depth ≤3 hops constraint
- Calculate quality scores across multiple dimensions
- Detect broken links and orphaned documents
- Trigger feedback loop to orchestrator if quality insufficient
- Update QUALITY_SCORE.md with metrics

## Skills Used

### Validation Skills
- `check-navigation-depth` - Enforce 3-hop constraint
- `check-quality-score` - Calculate comprehensive quality metrics

### Monitoring
- `log-operation` - Log validation results

### Documentation Skills
- `write-agentic-file` - Update QUALITY_SCORE.md

## Validation Workflow

### Phase 1: Structural Validation
1. Check required files exist:
   - [ ] AGENTS.md at repository root
   - [ ] agentic/DESIGN.md
   - [ ] agentic/DEVELOPMENT.md
   - [ ] agentic/TESTING.md
   - [ ] agentic/RELIABILITY.md
   - [ ] agentic/SECURITY.md
   - [ ] agentic/QUALITY_SCORE.md
2. Check required directories exist:
   - [ ] agentic/design-docs/
   - [ ] agentic/design-docs/components/
   - [ ] agentic/domain/concepts/
   - [ ] agentic/domain/workflows/
   - [ ] agentic/exec-plans/
3. Log structural validation results

### Phase 2: Navigation Validation
1. Run `check-navigation-depth`:
   - Start from AGENTS.md
   - Follow all links to depth 3
   - Identify orphaned documents
   - Flag navigation depth violations
2. Validate AGENTS.md budget (≤150 lines)
3. Validate component doc budgets (≤100 lines each)
4. Log navigation validation results

### Phase 3: Link Validation
1. Parse all markdown files in agentic/
2. Extract all markdown links
3. For each link:
   - Check if target file exists
   - Check if target anchor exists (for #section links)
   - Flag broken links
4. Check for bidirectional links:
   - Concept ↔ Component links
   - Workflow → Component links
5. Log link validation results

### Phase 4: Content Validation
1. Validate frontmatter:
   - All docs have required frontmatter
   - Frontmatter YAML is well-formed
   - Required fields present (title, type, last_updated)
2. Validate markdown syntax:
   - Tables formatted correctly
   - Code blocks closed
   - Headings properly nested
3. Validate confidence scores:
   - Flag low-confidence inferences (<0.5)
   - Document confidence distribution

### Phase 5: Quality Score Calculation
1. Run `check-quality-score`:
   - **Coverage**: % of components documented
   - **Freshness**: % of docs updated within 90 days
   - **Completeness**: Required files present
   - **Linkage**: Broken links count
   - **Navigation**: Depth violations count
2. Calculate overall score (0-100)
3. Update QUALITY_SCORE.md with results and timestamp

### Phase 6: Feedback Loop
1. Check if quality score meets threshold (default: 70/100)
2. If score < threshold:
   - Identify specific gaps:
     - Undocumented components
     - Broken links
     - Navigation violations
     - Missing required files
   - Generate remediation plan
   - Return feedback to orchestrator with specific actions needed
   - Orchestrator re-runs appropriate agents
3. If score ≥ threshold:
   - Mark validation as passed
   - Log success metrics
4. Log feedback loop results

## Quality Thresholds

### Pass Criteria (All must be met)
- Coverage ≥ 80%
- Stale docs ≤ 10%
- All 7 required files present (AGENTS.md + 6 in agentic/)
- Zero broken links
- Navigation depth ≤ 3 hops
- Zero orphaned documents

### Quality Score Calculation
```
Coverage Score (40 points):
  = (documented_components / total_components) * 40

Freshness Score (20 points):
  = (1 - stale_docs_ratio) * 20

Completeness Score (20 points):
  = (required_files_present / 7) * 20

Linkage Score (10 points):
  = max(0, 10 - broken_links)

Navigation Score (10 points):
  = (navigation_passed ? 10 : 0)

Total Score = sum of above (0-100)
```

## QUALITY_SCORE.md Format
```markdown
---
last_updated: 2026-04-23T10:30:00Z
overall_score: 87
status: passing
---

# Documentation Quality Score

**Overall Score**: 87/100
**Status**: ✅ Passing
**Last Updated**: 2026-04-23 10:30 UTC

## Metrics

### Coverage (35/40)
- Total components: 20
- Documented: 18
- Coverage: 90%
- **Undocumented**:
  - internal/legacy/adapter.go
  - cmd/deprecated-tool/

### Freshness (18/20)
- Total docs: 45
- Stale (>90 days): 3
- Staleness: 6.7%
- **Stale files**:
  - agentic/domain/concepts/legacy-api.md (120 days)

### Completeness (20/20)
- Required files: 7/7 present
- Required directories: All present

### Linkage (9/10)
- Total links: 234
- Broken links: 1
- Orphaned docs: 0
- **Broken links**:
  - agentic/design-docs/components/foo.md → ../missing.md

### Navigation (10/10)
- Max depth: 3 hops
- Violations: 0
- ✅ Navigation constraint met

## Remediation Required
- [ ] Document internal/legacy/adapter.go
- [ ] Update legacy-api.md or archive
- [ ] Fix broken link in foo.md
```

## Error Handling
- **Missing required file**: Log error, quality score = 0, fail validation
- **Broken link**: Log warning, decrement linkage score, continue
- **Navigation violation**: Log error, navigation score = 0, provide fix recommendations
- **Parse error**: Log error, skip file, flag for manual review

## Feedback to Orchestrator
```json
{
  "validation_passed": false,
  "quality_score": 65,
  "required_actions": [
    {
      "agent": "synthesizer",
      "operation": "generate-component-doc",
      "target": "internal/legacy/adapter.go",
      "reason": "Component not documented"
    },
    {
      "agent": "linker",
      "operation": "fix-broken-links",
      "target": "agentic/design-docs/components/foo.md",
      "reason": "Broken link detected"
    }
  ],
  "retry_count": 1
}
```

## Monitoring
Log to `agents/logs/validator.jsonl`:
```json
{
  "timestamp": "...",
  "agent_id": "validator",
  "operation": "validate-quality",
  "status": "completed",
  "metadata": {
    "quality_score": 87,
    "passed": true,
    "coverage": 0.90,
    "broken_links": 1,
    "navigation_violations": 0
  }
}
```
