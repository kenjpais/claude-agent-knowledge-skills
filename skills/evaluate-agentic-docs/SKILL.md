---
skill_id: evaluate-agentic-docs
name: Evaluate Agentic Documentation Quality
category: evaluation
version: 1.0.0
trigger: /evaluate
description: Evaluate agentic documentation by testing with coding agent simulation
agents: [evaluator]
inputs: [repository_path, test_scenarios]
outputs: [evaluation_report, metrics, recommendations]
---

# Evaluate Agentic Documentation Quality

**Trigger**: `/evaluate`  
**Purpose**: Test the value of agentic documentation by simulating coding agent scenarios

## Overview

This skill evaluates documentation quality by spawning a sub-agent ("coding agent") and testing whether it can complete real coding tasks using ONLY the agentic documentation.

## Input

**Repository Path or GitHub URL** (optional - defaults to current directory)

```
/evaluate [path/to/repository | github-url]
```

**Examples**:
```bash
/evaluate                                                  # Current directory
/evaluate /path/to/openshift-installer                   # Local repository path
/evaluate https://github.com/openshift/installer         # GitHub URL (auto-clones)
/evaluate github.com/openshift/installer                 # GitHub URL (auto-clones)
```

## Auto-Cloning

If a GitHub URL is provided and the repository is not already cloned:

1. **Parse GitHub URL**: Extract owner and repository name
2. **Clone locally**: `git clone <url> /tmp/agentic-repos/<repo-name>`
3. **Use cloned path**: Continue with evaluation in cloned repository
4. **Evaluate from**: `<cloned-repo>/agentic/` directory

**Clone location**: `/tmp/agentic-repos/<repo-name>/`

**Supported URL formats**:
- `https://github.com/owner/repo`
- `https://github.com/owner/repo.git`
- `github.com/owner/repo`
- `git@github.com:owner/repo.git`

## Test Scenarios

### 1. New Feature Implementation

**Task**: "Add support for ARM64 architecture scheduling"

**Evaluation**:
- Can agent find relevant components?
- Can agent understand architecture?
- Can agent identify where to add code?
- Time to retrieval: < 2 minutes
- Hops required: ≤ 3
- Confidence: ≥ 80%

### 2. Bug Fix

**Task**: "Fix memory leak in pod inspector"

**Evaluation**:
- Can agent locate pod inspector component?
- Can agent understand component responsibilities?
- Can agent identify related components?
- Time to retrieval: < 90 seconds
- Hops required: ≤ 2
- Confidence: ≥ 90%

### 3. Refactoring

**Task**: "Refactor image cache to use LRU eviction"

**Evaluation**:
- Can agent find image cache component?
- Can agent understand current implementation?
- Can agent identify dependencies?
- Time to retrieval: < 2 minutes
- Hops required: ≤ 3
- Confidence: ≥ 75%

### 4. Code Review

**Task**: "Review changes to cluster pod placement config"

**Evaluation**:
- Can agent find relevant documentation?
- Can agent understand component role?
- Can agent identify affected systems?
- Time to retrieval: < 90 seconds
- Hops required: ≤ 2
- Confidence: ≥ 85%

### 5. Architecture Understanding

**Task**: "Explain how multi-arch scheduling works"

**Evaluation**:
- Can agent navigate from AGENTS.md?
- Can agent find architecture overview?
- Can agent explain workflow?
- Time to retrieval: < 2 minutes
- Hops required: ≤ 3
- Confidence: ≥ 90%

## Execution Process

### Phase 1: Setup

1. Load test scenarios
2. Initialize metrics tracking
3. Prepare coding agent environment

### Phase 2: Scenario Execution

For each scenario:

1. **Spawn Sub-Agent** (coding agent role)
   - Constrained to ONLY use `ask-agentic-docs` skill
   - No direct code access
   - Must navigate documentation

2. **Prompt Scenario**
   - Give task description
   - Track start time
   - Monitor queries made

3. **Track Metrics**
   - Query count (hops)
   - Time spent
   - Information retrieved
   - Confidence level reported

4. **Evaluate Response**
   - Compare against success criteria
   - Score: 0-100 per scenario
   - Identify gaps in documentation

### Phase 3: Analysis

1. **Aggregate Metrics**
   ```yaml
   overall_score: 0-100
   scenarios_passed: count
   scenarios_failed: count
   average_hops: number
   average_time: seconds
   average_confidence: percentage
   ```

2. **Identify Issues**
   - Missing components
   - Unclear descriptions
   - Broken navigation paths
   - Insufficient detail

3. **Generate Recommendations**
   - Which components need better docs
   - Navigation improvements
   - Concept explanations needed

## Success Criteria

Documentation is high-quality if:

- ✅ 80% of scenarios pass
- ✅ Average hops ≤ 2.5
- ✅ Average time ≤ 120 seconds
- ✅ Average confidence ≥ 80%

## Output Schema

```yaml
evaluation_report:
  overall_score: 85/100
  scenarios:
    - scenario_id: "new-feature"
      task: "Add ARM64 support"
      passed: true
      metrics:
        hops: 2
        time_seconds: 95
        confidence: 85
        queries_made:
          - "what components exist?"
          - "how does scheduling work?"
      
    - scenario_id: "bug-fix"
      task: "Fix memory leak"
      passed: true
      metrics:
        hops: 2
        time_seconds: 75
        confidence: 90

  aggregate_metrics:
    scenarios_passed: 4/5
    average_hops: 2.4
    average_time: 98.5
    average_confidence: 82

  recommendations:
    - "Add more detail to image cache component"
    - "Create workflow diagram for scheduling"
    - "Link pod inspector to related concepts"
```

## Sub-Agent Constraints

The coding agent sub-agent:

- ✅ Can ONLY use `ask-agentic-docs` skill
- ✅ Cannot read source code directly
- ✅ Must navigate from AGENTS.md
- ✅ Limited to 3 hops recommended
- ✅ Must report confidence level

This ensures we're testing documentation quality, not coding ability.

## Metrics Tracked

### Retrieval Metrics
- **Hop count**: Number of queries made
- **Navigation path**: Which docs accessed
- **Time to answer**: Seconds spent
- **Coverage**: % of relevant docs found

### Quality Metrics
- **Confidence**: Agent's reported confidence (0-100)
- **Completeness**: Did agent get enough info?
- **Accuracy**: Was retrieved info correct?
- **Efficiency**: Time vs quality tradeoff

### Performance Metrics
- **Success rate**: % scenarios passed
- **Average time**: Mean time across scenarios
- **Average hops**: Mean hops across scenarios
- **Outliers**: Scenarios that took too long

## Integration

This skill integrates with:
- `ask-agentic-docs` - Used by sub-agent for retrieval
- `validate-agentic-docs` - Validation of structure
- `check-quality-score` - Quality scoring

## Usage

```bash
# Via CLI
agentic /evaluate <repository>

# Via Python
from lib.claude_orchestrator import ClaudeOrchestrator

orchestrator = ClaudeOrchestrator(project_root)
result = orchestrator.execute_workflow('evaluate', {
    'repo_path': '/path/to/repo',
    'test_scenarios': [...]
})
```

## Example Output

```
🧪 Evaluating Agentic Documentation
====================================

Running 5 test scenarios with coding agent...

Scenario 1: New Feature - Add ARM64 support
  ✅ PASS (2 hops, 95s, 85% confidence)
  
Scenario 2: Bug Fix - Fix memory leak
  ✅ PASS (2 hops, 75s, 90% confidence)
  
Scenario 3: Refactor - LRU cache eviction
  ⚠️  BORDERLINE (3 hops, 145s, 72% confidence)
  
Scenario 4: Code Review - Pod placement config
  ✅ PASS (1 hop, 60s, 90% confidence)
  
Scenario 5: Architecture - Multi-arch scheduling
  ✅ PASS (3 hops, 110s, 88% confidence)

====================================
Overall Score: 85/100 ✅ PASS
====================================

Aggregate Metrics:
  Scenarios Passed: 4/5 (80%)
  Average Hops: 2.2
  Average Time: 97s
  Average Confidence: 85%

Recommendations:
  1. Add workflow diagram for scheduling (scenario 3 struggled)
  2. Improve image cache documentation
  3. Create concept doc for LRU eviction pattern

Documentation quality: GOOD
Ready for production use.
```

---

*Based on "The Complete Guide to Building Skills for Claude" - Anthropic*
