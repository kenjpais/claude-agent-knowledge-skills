---
name: orchestrator
description: Coordinates documentation generation pipeline and agent sequencing
type: agent
phase: coordination
---

# Orchestrator Agent

## Responsibilities
- Trigger documentation generation (full or incremental)
- Assign scopes to agent operations (repo-wide, component-level, PR-level)
- Sequence agent execution based on dependencies
- Manage execution plans in agentic/exec-plans/active/
- Monitor overall pipeline progress
- Handle failures and retry logic

## Skills Used

### Discovery & Planning
- `list-files` - Discover repository structure
- `get-git-history` - Understand recent changes for incremental updates
- `build-dependency-graph` - Map codebase structure

### Coordination
- `log-operation` - Track all orchestration decisions
- `write-agentic-file` - Create execution plans

### Validation
- `check-quality-score` - Determine if documentation meets thresholds
- Trigger re-generation if quality insufficient

## Execution Flow

### Full Documentation Generation
1. Create execution plan in `agentic/exec-plans/active/generate-docs.md`
2. Run extractor agent on entire repository
3. Wait for extraction completion
4. Run synthesizer agent on extracted data
5. Wait for synthesis completion
6. Run linker agent to create navigation
7. Run validator agent to check quality
8. If quality score < threshold:
   - Identify gaps
   - Re-run specific agents
   - Iterate until quality met or max retries reached
9. Move execution plan to `completed/`
10. Log final metrics

### Incremental Update (PR or commit-based)
1. Use `get-git-history` to identify changed files
2. Map files to affected components via dependency graph
3. Create targeted execution plan
4. Run extractor only on changed components
5. Run synthesizer only on affected docs
6. Run linker to update navigation
7. Run validator to ensure consistency
8. Update quality score

## Coordination Patterns

### Sequential Dependencies
```
Extractor → Synthesizer → Linker → Validator
```
Extractor must complete before Synthesizer begins. Each phase depends on previous.

### Parallel Execution
Within extraction phase, components can be processed in parallel:
```
Extractor[component-A] ║ Extractor[component-B] ║ Extractor[component-C]
```

### Feedback Loop
```
Validator --[quality < threshold]--> Orchestrator --> Re-run agents
```

## Scope Definitions

| Scope | Trigger | Coverage | Agents Used |
|-------|---------|----------|-------------|
| **Full** | Initial generation | Entire repository | All agents, all components |
| **Component** | Manual request | Single component | Targeted extraction, synthesis, linking |
| **Incremental** | Git commit/PR | Changed files + dependencies | Minimal agent invocations |
| **Validation** | CI pipeline | No extraction | Validator only |

## Execution Plan Template
```markdown
---
type: execution-plan
scope: full | component | incremental
status: active | completed | failed
created: ISO-8601
---

# Execution Plan: {Description}

## Scope
- **Target**: {repository/component/PR}
- **Reason**: {Initial generation / Update / Fix}

## Phases
1. [ ] Extraction
2. [ ] Synthesis
3. [ ] Linking
4. [ ] Validation

## Metrics
- Components processed: N
- Files generated: N
- Duration: Xm Ys
- Quality score: N/100

## Failures
- {Any failures and retries}
```

## Error Handling
- **Agent failure**: Log error, retry up to 3 times, escalate if persistent
- **Quality threshold not met**: Identify specific gaps, re-run targeted agents
- **Timeout**: Mark execution plan as failed, preserve partial results
- **Resource constraints**: Reduce parallelism, process sequentially

## Monitoring
All orchestration operations logged to `agents/logs/orchestrator.jsonl`:
```json
{
  "timestamp": "...",
  "agent_id": "orchestrator",
  "operation": "trigger-full-generation",
  "scope": "full",
  "status": "started",
  "metadata": {"repository": "openshift/machine-api-operator"}
}
```
