---
name: record-evaluation
description: Records evaluation results to database for metrics and analysis
type: skill
category: evaluation
phase: recording
---

# Record Evaluation

## Purpose

Persists evaluation results from the Main → Coding → Judge loop to a database for:
- Tracking success rates over time
- Identifying documentation quality issues
- Measuring coding agent performance
- Analyzing common failure patterns

## When to Use

- After judge sub-agent completes evaluation
- At end of evaluation loop (success or failure)
- When evaluation is aborted (timeout, error)

## Input

```yaml
task:
  id: string  # Auto-generated UUID
  description: string
  type: implement | fix | debug | modify
  
agentic_docs:
  paths: array<string>
  graph_query: string
  
coding_output:
  files: array<object>
  warnings: array<string>
  metadata: object
  
evaluation:
  scores: object
  total_score: integer
  verdict: pass | fail
  issues: array<string>
  strengths: array<string>
  summary: string
  
metadata:
  attempts: integer
  duration_seconds: float
  timestamp: string
  status: pass | fail | timeout | error
```

## Output

```yaml
record_result:
  task_id: string
  stored_at: string  # ~/.agent-knowledge/evaluations/{task_id}.json
  database_row_id: integer
```

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT UNIQUE NOT NULL,
    task_description TEXT NOT NULL,
    task_type TEXT NOT NULL,
    
    docs_provided TEXT,  -- JSON array of paths
    
    verdict TEXT NOT NULL,  -- pass | fail | timeout | error
    total_score INTEGER,
    correctness_score INTEGER,
    adherence_score INTEGER,
    completeness_score INTEGER,
    robustness_score INTEGER,
    
    attempts INTEGER,
    duration_seconds REAL,
    
    issues TEXT,  -- JSON array
    strengths TEXT,  -- JSON array
    summary TEXT,
    
    timestamp TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_evaluations_verdict ON evaluations(verdict);
CREATE INDEX idx_evaluations_timestamp ON evaluations(timestamp);
CREATE INDEX idx_evaluations_task_type ON evaluations(task_type);
```

## Process

### Step 1: Generate Task ID

```python
import uuid
from datetime import datetime

task_id = str(uuid.uuid4())
timestamp = datetime.utcnow().isoformat()
```

### Step 2: Write JSON File

```python
import json
import os

evaluation_data = {
    'task_id': task_id,
    'task': task,
    'agentic_docs': agentic_docs,
    'coding_output': coding_output,
    'evaluation': evaluation,
    'metadata': metadata,
    'timestamp': timestamp
}

output_dir = os.path.expanduser('~/.agent-knowledge/evaluations/')
os.makedirs(output_dir, exist_ok=True)

filepath = f"{output_dir}/{task_id}.json"
with open(filepath, 'w') as f:
    json.dump(evaluation_data, f, indent=2)
```

### Step 3: Insert into Database

```python
import sqlite3

db_path = os.path.expanduser('~/.agent-knowledge/data.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO evaluations (
        task_id, task_description, task_type,
        docs_provided, verdict,
        total_score, correctness_score, adherence_score,
        completeness_score, robustness_score,
        attempts, duration_seconds,
        issues, strengths, summary, timestamp
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    task_id,
    task['description'],
    task['type'],
    json.dumps(agentic_docs.get('paths', [])),
    metadata['status'],
    evaluation.get('total_score'),
    evaluation['scores'].get('correctness'),
    evaluation['scores'].get('adherence'),
    evaluation['scores'].get('completeness'),
    evaluation['scores'].get('robustness'),
    metadata['attempts'],
    metadata['duration_seconds'],
    json.dumps(evaluation.get('issues', [])),
    json.dumps(evaluation.get('strengths', [])),
    evaluation.get('summary'),
    timestamp
))

conn.commit()
row_id = cursor.lastrowid
conn.close()
```

### Step 4: Generate Metrics Summary

```python
def generate_metrics_summary():
    """
    Query database for aggregate metrics
    """
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Overall pass rate
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN verdict = 'pass' THEN 1 ELSE 0 END) as passed,
            ROUND(AVG(total_score), 2) as avg_score,
            ROUND(AVG(duration_seconds), 2) as avg_duration
        FROM evaluations
    """)
    
    total, passed, avg_score, avg_duration = cursor.fetchone()
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    # By task type
    cursor.execute("""
        SELECT 
            task_type,
            COUNT(*) as count,
            ROUND(AVG(total_score), 2) as avg_score
        FROM evaluations
        GROUP BY task_type
    """)
    
    by_type = cursor.fetchall()
    
    # Common failure issues
    cursor.execute("""
        SELECT issues
        FROM evaluations
        WHERE verdict = 'fail'
    """)
    
    all_issues = []
    for row in cursor.fetchall():
        all_issues.extend(json.loads(row[0]))
    
    from collections import Counter
    common_issues = Counter(all_issues).most_common(10)
    
    conn.close()
    
    return {
        'total_evaluations': total,
        'passed': passed,
        'pass_rate': pass_rate,
        'avg_score': avg_score,
        'avg_duration_seconds': avg_duration,
        'by_task_type': by_type,
        'common_issues': common_issues
    }
```

## Example Recorded Evaluation

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "task": {
    "description": "Create a Deployment for nginx with 2 replicas",
    "type": "implement"
  },
  "agentic_docs": {
    "paths": ["agentic/design-docs/components/nginx.md"]
  },
  "coding_output": {
    "files": [
      {
        "path": "deployment.yaml",
        "content": "...",
        "type": "yaml"
      }
    ],
    "warnings": ["Missing liveness probe"]
  },
  "evaluation": {
    "scores": {
      "correctness": 5,
      "adherence": 5,
      "completeness": 4,
      "robustness": 4
    },
    "total_score": 18,
    "verdict": "pass",
    "issues": ["Missing liveness probe"],
    "strengths": ["Correct selector consistency", "All required fields present"],
    "summary": "Good implementation, minor issue with missing health check."
  },
  "metadata": {
    "attempts": 1,
    "duration_seconds": 5.2,
    "timestamp": "2026-04-30T10:30:00Z",
    "status": "pass"
  }
}
```

## Metrics Dashboard Query Examples

### Pass Rate Over Time

```sql
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as total,
    SUM(CASE WHEN verdict = 'pass' THEN 1 ELSE 0 END) as passed,
    ROUND(100.0 * SUM(CASE WHEN verdict = 'pass' THEN 1 ELSE 0 END) / COUNT(*), 2) as pass_rate
FROM evaluations
WHERE timestamp >= date('now', '-30 days')
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

### Lowest Scoring Category

```sql
SELECT 
    'correctness' as category, ROUND(AVG(correctness_score), 2) as avg_score
FROM evaluations
UNION ALL
SELECT 'adherence', ROUND(AVG(adherence_score), 2) FROM evaluations
UNION ALL
SELECT 'completeness', ROUND(AVG(completeness_score), 2) FROM evaluations
UNION ALL
SELECT 'robustness', ROUND(AVG(robustness_score), 2) FROM evaluations
ORDER BY avg_score ASC;
```

## Integration

This skill is used by:
- **Main Agent** - After each evaluation loop completion
- Analytics tools - For metrics dashboards
