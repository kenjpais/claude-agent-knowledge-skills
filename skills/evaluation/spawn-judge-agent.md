---
name: spawn-judge-agent
description: Spawns judge sub-agent to evaluate coding agent output with strict adversarial scoring
type: skill
category: evaluation
phase: evaluation
---

# Spawn Judge Agent

## Purpose

Spawns the Judge Sub-Agent with:
- Original task description
- Agentic documentation provided to coding agent
- Coding agent's output
- Optional test results
- Strict scoring rubric (0-20 scale)

Returns adversarial evaluation with verdict (pass/fail).

## When to Use

- After coding sub-agent produces output
- During evaluation loops
- When assessing documentation quality via executor testing

## Input

```yaml
task:
  description: string
  type: implement | fix | debug | modify
  
agentic_docs:
  paths: array<string>
  content: array<object>  # The actual docs given to coding agent
  
coding_output:
  files: array<object>
  warnings: array<string>
  metadata: object
  
test_results:  # Optional
  unit_tests: object
  integration_tests: object
  validation: object
```

## Output

```yaml
judge_evaluation:
  scores:
    correctness: integer  # 0-5
    adherence: integer    # 0-5
    completeness: integer # 0-5
    robustness: integer   # 0-5
    
  total_score: integer    # 0-20
  max_score: 20
  percentage: float       # 0.0-100.0
  
  verdict: pass | fail    # pass if total_score >= 14
  
  issues: array<string>   # Specific problems found
  strengths: array<string>  # What was done correctly
  
  summary: string  # 1-2 sentence technical evaluation
  
  adherence_details:
    docs_followed_exactly: boolean
    deviations: array<string>
    unauthorized_features: array<string>
    
  validation_results:
    yaml_schema: pass | fail | n/a
    api_versions: pass | fail | n/a
    selector_consistency: pass | fail | n/a
```

## Process

### Step 1: Prepare Judge Context

```python
def prepare_judge_agent_context(task, agentic_docs, coding_output, test_results):
    """
    Build comprehensive evaluation context for judge
    """
    
    judge_prompt = f"""
You are a strict adversarial evaluator of OpenShift/Kubernetes code.

ORIGINAL TASK:
{task['description']}

DOCUMENTATION PROVIDED TO CODING AGENT:
{format_docs(agentic_docs)}

CODING AGENT OUTPUT:
{format_output(coding_output)}

YOUR JOB:
Evaluate the output strictly using this rubric:

1. Correctness (0-5): Does it solve the task?
2. Adherence (0-5): Did coding agent follow docs EXACTLY?
3. Completeness (0-5): Are all features implemented (no TODOs)?
4. Robustness (0-5): Valid K8s/OpenShift (correct APIs, schemas, security)?

SCORING RULES:
- Be adversarial and strict
- Do NOT assume missing intent
- Penalize hallucinations heavily
- Penalize deviations from docs
- Reward exact adherence

VERDICT:
- pass: total_score >= 14 (70%+)
- fail: total_score < 14

OUTPUT:
Return ONLY JSON in this exact format:
{{
  "scores": {{"correctness": X, "adherence": X, "completeness": X, "robustness": X}},
  "total_score": X,
  "verdict": "pass|fail",
  "issues": ["specific issue 1", "specific issue 2"],
  "strengths": ["strength 1", "strength 2"],
  "summary": "1-2 sentence technical evaluation"
}}
"""

    if test_results:
        judge_prompt += f"""

TEST RESULTS:
{format_test_results(test_results)}

Consider test results in your evaluation.
"""

    return judge_prompt
```

### Step 2: Spawn Judge via Agent Tool

```python
from anthropic import Agent

judge_agent = Agent(
    agent_definition='agents/sub-agents/judge-agent.md',
    prompt=judge_prompt,
    tools=['validate-yaml-schema', 'check-api-versions', 'verify-code-references'],
    model='claude-sonnet-4.5',
    output_format='json'  # Enforce JSON-only output
)

# Execute agent
result = judge_agent.run()
```

### Step 3: Parse Judge Output

```python
import json

def parse_judge_output(agent_result):
    """
    Parse and validate judge's JSON output
    """
    
    # Extract JSON from agent response
    try:
        evaluation = json.loads(agent_result.output)
    except json.JSONDecodeError as e:
        raise ValueError(f"Judge did not return valid JSON: {e}")
    
    # Validate required fields
    required = ['scores', 'total_score', 'verdict', 'issues', 'strengths', 'summary']
    for field in required:
        if field not in evaluation:
            raise ValueError(f"Judge evaluation missing required field: {field}")
    
    # Validate scores
    scores = evaluation['scores']
    for category in ['correctness', 'adherence', 'completeness', 'robustness']:
        if category not in scores:
            raise ValueError(f"Missing score for: {category}")
        if not (0 <= scores[category] <= 5):
            raise ValueError(f"Invalid score for {category}: {scores[category]} (must be 0-5)")
    
    # Calculate total
    calculated_total = sum(scores.values())
    if evaluation['total_score'] != calculated_total:
        raise ValueError(f"Total score mismatch: {evaluation['total_score']} != {calculated_total}")
    
    # Validate verdict
    if evaluation['verdict'] not in ['pass', 'fail']:
        raise ValueError(f"Invalid verdict: {evaluation['verdict']}")
    
    # Verify verdict matches score
    expected_verdict = 'pass' if calculated_total >= 14 else 'fail'
    if evaluation['verdict'] != expected_verdict:
        raise ValueError(f"Verdict '{evaluation['verdict']}' doesn't match score {calculated_total}")
    
    return evaluation
```

### Step 4: Run Validation Tools

Judge agent uses these skills during evaluation:

```python
# If YAML output, validate schema
if has_yaml_files(coding_output):
    for file in coding_output['files']:
        if file['type'] == 'yaml':
            validation = validate_yaml_schema(file['content'])
            # Judge incorporates validation into robustness score

# Check API versions
if has_k8s_resources(coding_output):
    api_check = check_api_versions(coding_output)
    # Judge penalizes deprecated APIs in robustness score

# Verify code references from docs were accurate
code_refs = extract_code_references(agentic_docs)
verification = verify_code_references(code_refs, repository_path)
# If docs referenced non-existent code, affects adherence score
```

### Step 5: Format Final Evaluation

```python
def format_evaluation_output(evaluation, validation_results):
    """
    Enhance evaluation with validation details
    """
    
    evaluation['adherence_details'] = {
        'docs_followed_exactly': evaluation['scores']['adherence'] == 5,
        'deviations': extract_deviations_from_issues(evaluation['issues']),
        'unauthorized_features': extract_unauthorized_features(evaluation['issues'])
    }
    
    evaluation['validation_results'] = validation_results
    
    evaluation['percentage'] = (evaluation['total_score'] / 20) * 100
    evaluation['max_score'] = 20
    
    return evaluation
```

## Example Evaluations

### Example 1: Perfect Score

```json
{
  "scores": {
    "correctness": 5,
    "adherence": 5,
    "completeness": 5,
    "robustness": 5
  },
  "total_score": 20,
  "max_score": 20,
  "percentage": 100.0,
  "verdict": "pass",
  "issues": [],
  "strengths": [
    "All requirements implemented correctly",
    "Exact adherence to docs (image version, port, finalizer name)",
    "Correct API version (apps/v1)",
    "Perfect selector/label consistency",
    "All required fields present"
  ],
  "summary": "Perfect implementation. All requirements met, docs followed exactly, valid Kubernetes manifest.",
  "adherence_details": {
    "docs_followed_exactly": true,
    "deviations": [],
    "unauthorized_features": []
  },
  "validation_results": {
    "yaml_schema": "pass",
    "api_versions": "pass",
    "selector_consistency": "pass"
  }
}
```

### Example 2: Failed Evaluation

```json
{
  "scores": {
    "correctness": 2,
    "adherence": 3,
    "completeness": 1,
    "robustness": 3
  },
  "total_score": 9,
  "max_score": 20,
  "percentage": 45.0,
  "verdict": "fail",
  "issues": [
    "TODO on line 15: Finalizer not implemented despite docs specifying it",
    "TODO on line 23: Reconcile logic incomplete",
    "Missing error handling on Get() call (line 12)",
    "Finalizer name 'machine-finalizer' doesn't match docs ('machine.openshift.io/machine-finalizer')",
    "Missing deletion timestamp check"
  ],
  "strengths": [
    "Correct function signature",
    "Correct Machine type reference"
  ],
  "summary": "Incomplete skeleton implementation. Critical features missing: finalizer handling, reconcile logic, error handling. TODOs indicate work not done.",
  "adherence_details": {
    "docs_followed_exactly": false,
    "deviations": [
      "Finalizer name incorrect: 'machine-finalizer' should be 'machine.openshift.io/machine-finalizer'"
    ],
    "unauthorized_features": []
  },
  "validation_results": {
    "yaml_schema": "n/a",
    "api_versions": "n/a",
    "selector_consistency": "n/a"
  }
}
```

### Example 3: Marginal Pass

```json
{
  "scores": {
    "correctness": 4,
    "adherence": 4,
    "completeness": 3,
    "robustness": 3
  },
  "total_score": 14,
  "max_score": 20,
  "percentage": 70.0,
  "verdict": "pass",
  "issues": [
    "Missing liveness probe in Deployment spec (line 23)",
    "Container image uses :latest tag instead of explicit version",
    "TODO comment on line 42: 'Add resource limits' should be implemented"
  ],
  "strengths": [
    "Correct matchLabels selector consistency",
    "Proper RBAC ServiceAccount defined",
    "All required fields present",
    "Follows documented workflow exactly"
  ],
  "summary": "Implementation is 70% complete. Missing health checks and using :latest tag. Core logic correct and follows docs exactly.",
  "adherence_details": {
    "docs_followed_exactly": true,
    "deviations": [],
    "unauthorized_features": []
  },
  "validation_results": {
    "yaml_schema": "pass",
    "api_versions": "pass",
    "selector_consistency": "pass"
  }
}
```

## Scoring Guidelines (for Judge)

### Correctness (0-5)

- **5**: Fully correct, all requirements implemented, compiles/validates
- **4**: 1 minor requirement missing
- **3**: 2-3 requirements missing  
- **2**: Major issues, <50% requirements met
- **1**: Fundamentally wrong approach
- **0**: Doesn't compile/validate

### Adherence (0-5)

- **5**: Perfect adherence, literal implementation of docs
- **4**: 1 minor deviation (cosmetic)
- **3**: 2-3 deviations or 1 moderate deviation
- **2**: Multiple deviations or major reinterpretation
- **1**: Largely ignored docs
- **0**: No evidence of reading docs

### Completeness (0-5)

- **5**: 100% complete, no TODOs in production code
- **4**: 90-99% complete, trivial TODOs only
- **3**: 75-89% complete
- **2**: 50-74% complete
- **1**: <50% complete
- **0**: Empty or skeleton

### Robustness (0-5)

- **5**: Perfect K8s/OpenShift patterns, secure defaults
- **4**: 1 minor issue
- **3**: 2-3 issues
- **2**: Major issues (wrong API, broken selectors)
- **1**: Critical issues (fails validation, security holes)
- **0**: Invalid YAML/Go, cannot deploy

## Error Handling

```
IF judge fails to spawn:
  - Log error
  - Return default: {verdict: 'fail', total_score: 0}

IF judge returns invalid JSON:
  - Log error
  - Ask judge to reformat
  - Retry once

IF judge scores don't sum correctly:
  - Log warning
  - Recalculate total_score
  - Use recalculated value

IF verdict doesn't match score:
  - Log error
  - Correct verdict based on score
  - Flag for review
```

## Verification

- [ ] Judge spawned with correct definition (judge-agent.md)
- [ ] All inputs provided (task, docs, output)
- [ ] Output is valid JSON
- [ ] All required fields present
- [ ] Scores in valid range (0-5 each)
- [ ] Total score calculated correctly
- [ ] Verdict matches score (≥14 = pass)
- [ ] Issues are specific (not vague)

## Integration

This skill is used by:
- **Main Agent** - In evaluation loop workflow
- Receives input from: **spawn-coding-agent** skill
- Output used for: Retry logic, recording evaluation
