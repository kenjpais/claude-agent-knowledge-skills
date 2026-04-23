---
name: check-quality-score
description: Calculate and validate documentation quality metrics
type: validation
category: quality
---

# Check Quality Score

## Overview
Computes comprehensive quality metrics for agentic documentation: coverage, freshness, completeness, linkage, and navigation. Updates QUALITY_SCORE.md.

## When to Use
- After documentation generation or update
- Before releasing documentation to agents
- As final step in validation phase
- For continuous monitoring of documentation health

## Process
1. **Coverage Metrics**:
   - Count total components in codebase
   - Count documented components in agentic/design-docs/components/
   - Calculate coverage percentage
   - Identify undocumented components
2. **Freshness Metrics**:
   - Check git last-modified dates for code files
   - Check last-modified dates for documentation
   - Flag docs older than 90 days with recent code changes
3. **Completeness Metrics**:
   - Verify all 6 required files exist (DESIGN.md, DEVELOPMENT.md, etc.)
   - Check all required directories present
   - Validate AGENTS.md structure
4. **Linkage Metrics**:
   - Parse all markdown links
   - Identify broken links
   - Count orphaned documents
5. **Navigation Metrics**:
   - Run check-navigation-depth
   - Validate 3-hop constraint
6. Calculate overall quality score (0-100)
7. Update QUALITY_SCORE.md with results and timestamp

## Verification
- [ ] All metrics calculated
- [ ] Quality score computed (0-100)
- [ ] QUALITY_SCORE.md updated
- [ ] Warnings generated for failures
- [ ] Timestamp recorded
- [ ] Pass/fail thresholds applied

## Input Schema
```yaml
repository_path: string
agentic_directory: string
code_directories: array<string>
quality_thresholds:
  min_coverage: float  # e.g., 0.80
  max_stale_days: integer  # e.g., 90
  max_broken_links: integer  # e.g., 0
```

## Output Schema
```yaml
success: boolean
passed: boolean  # All thresholds met
quality_score: integer  # 0-100
metrics:
  coverage:
    total_components: integer
    documented_components: integer
    percentage: float
    undocumented: array<string>
  freshness:
    stale_docs: integer
    avg_age_days: float
    stale_files: array<StaleDoc>
  completeness:
    required_files_present: integer
    missing_files: array<string>
  linkage:
    total_links: integer
    broken_links: integer
    orphaned_docs: integer
  navigation:
    max_depth: integer
    violations: integer
timestamp: string
```

## Quality Score Formula
```
coverage_score = coverage_percentage * 40
freshness_score = (1 - stale_ratio) * 20
completeness_score = (required_files_present / 6) * 20
linkage_score = (1 - broken_ratio) * 10
navigation_score = (navigation_passed ? 10 : 0)

total_score = sum of above (0-100)
```

## Pass Thresholds
- Coverage ≥ 80%
- Stale docs ≤ 10%
- All required files present
- Zero broken links
- Navigation depth ≤ 3
