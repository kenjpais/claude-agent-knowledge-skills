---
name: spawn-coding-agent
description: Spawns coding sub-agent with task and agentic-docs, enforces strict constraints
type: skill
category: evaluation
phase: execution
---

# Spawn Coding Agent

## Purpose

Spawns the Coding Sub-Agent with:
- Task description
- Agentic documentation (retrieved from knowledge graph)
- Strict execution constraints
- Isolation from main agent context

## When to Use

- During evaluation loops
- When user requests code implementation
- When testing documentation quality with executor

## Input

```yaml
task:
  description: string  # e.g., "Implement Machine controller reconcile loop"
  type: implement | fix | debug | modify
  
agentic_docs:
  paths: array<string>  # Paths to relevant docs
  OR
  graph_query: string   # Query to retrieve docs from graph

constraints:
  must_use_retrieval: true
  strict_adherence: true
  no_hallucination: true
  output_format: code_only | code_with_tests | yaml_only

retry_context:  # Optional, for retries
  previous_attempt: object
  judge_feedback: array<string>
  attempt_number: integer
```

## Output

```yaml
coding_agent_result:
  status: success | failure | partial
  
  outputs:
    files:
      - path: string
        content: string
        type: go | yaml | bash | markdown
        
  metadata:
    retrieval_queries: array<string>  # All queries made to retrieve-from-graph
    docs_referenced: array<string>    # Docs actually used
    execution_time_seconds: float
    
  warnings: array<string>  # Any TODOs or partial implementations
```

## Process

### Step 1: Prepare Agent Context

```python
def prepare_coding_agent_context(task, agentic_docs, constraints):
    """
    Build isolated context for coding sub-agent
    """
    
    # Load docs if paths provided
    if 'paths' in agentic_docs:
        docs_content = []
        for path in agentic_docs['paths']:
            with open(path) as f:
                docs_content.append({
                    'path': path,
                    'content': f.read()
                })
    
    # OR retrieve from graph if query provided
    elif 'graph_query' in agentic_docs:
        docs_content = retrieve_from_graph(
            query=agentic_docs['graph_query'],
            graph_path='agentic/knowledge-graph/graph.json'
        )
    
    # Build agent prompt
    agent_prompt = f"""
You are a strict OpenShift/Kubernetes coding agent.

TASK:
{task['description']}

DOCUMENTATION PROVIDED:
{format_docs_for_agent(docs_content)}

CONSTRAINTS:
- MUST use retrieve-from-graph skill for ALL knowledge queries
- MUST follow docs EXACTLY (no deviations)
- MUST NOT hallucinate APIs or field names
- MUST output ONLY code (no explanations)
- If unclear, output TODO instead of guessing

OUTPUT FORMAT:
{constraints['output_format']}

IMPORTANT:
- Prefer correctness over creativity
- Conservative implementation only
- Follow agentic-docs literally
"""

    if retry_context:
        agent_prompt += f"""

PREVIOUS ATTEMPT FAILED WITH:
{format_judge_feedback(retry_context['judge_feedback'])}

FIX THESE ISSUES IN THIS ATTEMPT.
"""

    return agent_prompt
```

### Step 2: Spawn Agent via Agent Tool

```python
from anthropic import Agent

coding_agent = Agent(
    agent_definition='agents/sub-agents/coding-agent.md',
    prompt=agent_prompt,
    tools=['retrieve-from-graph', 'read-file', 'search-code', 'write-file'],
    isolation='worktree',  # Isolated git worktree
    model='claude-sonnet-4.5'
)

# Execute agent
result = coding_agent.run()
```

### Step 3: Monitor Agent Execution

```python
# Track all skill invocations
retrieval_log = []
docs_used = []

for tool_call in coding_agent.tool_calls:
    if tool_call.name == 'retrieve-from-graph':
        retrieval_log.append(tool_call.params['query'])
        docs_used.extend(tool_call.result['documents'])

# Verify agent used retrieval (REQUIRED)
if not retrieval_log:
    raise ConstraintViolation(
        "Coding agent did not use retrieve-from-graph skill (REQUIRED)"
    )
```

### Step 4: Extract Outputs

```python
def extract_agent_outputs(agent_result):
    """
    Parse agent outputs into structured format
    """
    
    outputs = {
        'files': [],
        'warnings': []
    }
    
    # Extract files written by agent
    for tool_call in agent_result.tool_calls:
        if tool_call.name == 'write-file':
            file_path = tool_call.params['file_path']
            content = tool_call.params['content']
            
            outputs['files'].append({
                'path': file_path,
                'content': content,
                'type': infer_file_type(file_path)
            })
    
    # Scan for TODOs (warnings)
    for file in outputs['files']:
        if 'TODO' in file['content']:
            todos = extract_todos(file['content'])
            outputs['warnings'].extend(todos)
    
    return outputs
```

### Step 5: Validate Agent Constraints

```python
def validate_coding_agent_constraints(agent_result, constraints):
    """
    Ensure agent followed all constraints
    """
    
    violations = []
    
    # Check: Used retrieve-from-graph
    if constraints['must_use_retrieval']:
        if not agent_used_skill(agent_result, 'retrieve-from-graph'):
            violations.append("Agent did not use retrieve-from-graph (REQUIRED)")
    
    # Check: No explanations in output (if code_only format)
    if constraints['output_format'] == 'code_only':
        for file in agent_result.outputs['files']:
            if contains_explanatory_text(file['content']):
                violations.append(f"File {file['path']} contains explanations (code_only format violated)")
    
    # Check: No obvious hallucinations (check against docs)
    for file in agent_result.outputs['files']:
        if file['type'] == 'yaml':
            hallucinations = detect_hallucinated_fields(file['content'], docs_used)
            violations.extend(hallucinations)
    
    if violations:
        raise ConstraintViolation(violations)
```

## Example Usage

### Scenario 1: Fresh Implementation

```python
result = spawn_coding_agent(
    task={
        'description': 'Create a Deployment for nginx with 2 replicas',
        'type': 'implement'
    },
    agentic_docs={
        'graph_query': 'nginx deployment configuration'
    },
    constraints={
        'must_use_retrieval': True,
        'strict_adherence': True,
        'output_format': 'yaml_only'
    }
)

# Result:
{
  'status': 'success',
  'outputs': {
    'files': [
      {
        'path': 'deployment.yaml',
        'content': '...',
        'type': 'yaml'
      }
    ]
  },
  'metadata': {
    'retrieval_queries': ['nginx deployment', 'deployment best practices'],
    'docs_referenced': ['agentic/design-docs/components/nginx.md'],
    'execution_time_seconds': 3.2
  },
  'warnings': []
}
```

### Scenario 2: Retry After Judge Failure

```python
result = spawn_coding_agent(
    task={
        'description': 'Create a Deployment for nginx with 2 replicas',
        'type': 'implement'
    },
    agentic_docs={
        'paths': ['agentic/design-docs/components/nginx.md']
    },
    constraints={
        'must_use_retrieval': True,
        'strict_adherence': True,
        'output_format': 'yaml_only'
    },
    retry_context={
        'previous_attempt': previous_result,
        'judge_feedback': [
            'Missing liveness probe',
            'Using :latest tag instead of explicit version'
        ],
        'attempt_number': 2
    }
)

# Agent now aware of what failed and can fix
```

## Error Handling

```
IF agent fails to spawn:
  - Log error
  - Return: {status: 'failure', error: message}

IF agent violates constraints:
  - Log violation
  - Return: {status: 'failure', violations: [list]}

IF agent produces no output:
  - Log warning
  - Return: {status: 'partial', outputs: {files: []}}

IF agent timeout (>5 minutes):
  - Terminate agent
  - Return partial results
  - Log timeout
```

## Verification

- [ ] Agent spawned with correct definition (coding-agent.md)
- [ ] Task and docs provided in prompt
- [ ] Constraints enforced (retrieval usage checked)
- [ ] Outputs extracted and structured
- [ ] Warnings (TODOs) identified
- [ ] Metadata logged (queries, docs, time)

## Integration

This skill is used by:
- **Main Agent** - In evaluation loop workflow
- Feeds output to: **spawn-judge-agent** skill
