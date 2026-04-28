---
name: check-stale-todos
description: Detect stale TODO comments in agentic documentation
type: validation
category: quality
---

# Check Stale TODOs

## Overview
Detects TODO, FIXME, HACK, and XXX comments in agentic documentation that have not been updated within 30 days. Stale TODOs indicate unfinished work that should be moved to `tech-debt-tracker.md` or resolved.

## When to Use
- As part of freshness validation
- During CI validation runs
- When auditing documentation health

## Process
1. Scan all `.md` files under `agentic/` for lines matching (case-insensitive):
   - `TODO`
   - `FIXME`
   - `HACK`
   - `XXX`
   - `TBD`
2. For each matched line, determine file age:
   - Use `git log -1 --format="%ai" -- <file>` to get last modified date
   - Calculate days since last modification
3. **Warning threshold**: Flag files with TODO text not updated in > 30 days
4. **Error threshold**: If more than 5 files across `agentic/` have stale TODOs, escalate to error
   - Recommendation: move stale items to `agentic/exec-plans/tech-debt-tracker.md`
5. Report each stale TODO with file, line number, age in days, and matched text

## Verification
- [ ] All `.md` files scanned for TODO patterns
- [ ] Git last-modified date retrieved per file
- [ ] Staleness calculated in days
- [ ] Warning threshold (30 days) applied
- [ ] Error threshold (> 5 stale files) applied
- [ ] Recommendations generated

## Input Schema
```yaml
agentic_directory: string
warning_days: integer  # Default: 30
max_stale_count: integer  # Default: 5
```

## Output Schema
```yaml
success: boolean
passed: boolean  # false if stale_count > max_stale_count
metrics:
  total_files_scanned: integer
  files_with_todos: integer
  stale_todo_count: integer
  oldest_stale_days: integer
stale_todos: array<StaleTodo>
  - file: string
    line: integer
    text: string
    last_modified: string  # ISO date
    age_days: integer
    severity: string  # "warning" or "error"
```

## Red Flags
- **> 5 stale TODOs**: Systemic neglect — documentation is accumulating debt
- **TODO older than 90 days**: Likely forgotten — should be resolved or moved to tech-debt-tracker
- **FIXME in generated docs**: Generator produced incomplete output — investigate template
