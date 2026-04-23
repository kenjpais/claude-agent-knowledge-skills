---
name: log-operation
description: Log agent operations with structured metadata for monitoring and auditing
type: monitoring
category: observability
---

# Log Operation

## Overview
Centralized logging for all agent operations. Every skill invocation, file access, and documentation generation must be logged for auditing and debugging.

## When to Use
- At the start of every skill execution
- When accessing repository files
- When generating or updating documentation
- On errors or failures
- For retrieval agent queries

## Process
1. Accept operation metadata
2. Enrich with context:
   - Timestamp (ISO 8601)
   - Agent ID
   - Operation type
   - Target resource
   - Success/failure status
   - Duration
3. Structure as JSON log line
4. Write to appropriate log file:
   - agents/logs/{agent-name}.jsonl
   - utilities/logs/operations.jsonl (aggregated)
5. Rotate logs if size exceeds threshold
6. Optionally emit to monitoring system

## Verification
- [ ] All required fields present
- [ ] Timestamp in ISO 8601 format
- [ ] Log written successfully
- [ ] File rotation handled if needed
- [ ] Sensitive data redacted

## Input Schema
```yaml
agent_id: string
operation: string
resource: string
status: string  # started | success | failure
metadata: object
  duration_ms: integer | null
  error: string | null
  input_summary: string | null
  output_summary: string | null
```

## Output Schema
```yaml
success: boolean
log_file: string
log_entry: object
```

## Log Entry Format
```json
{
  "timestamp": "2026-04-23T10:30:45.123Z",
  "agent_id": "extractor",
  "operation": "extract-go-structs",
  "resource": "pkg/apis/types.go",
  "status": "success",
  "duration_ms": 142,
  "metadata": {
    "structs_found": 5,
    "interfaces_found": 2
  }
}
```

## Log Levels
- **INFO**: Normal operations
- **WARN**: Degraded performance, low confidence scores
- **ERROR**: Operation failures
- **DEBUG**: Detailed execution traces

## Sensitive Data Redaction
Automatically redact:
- File contents (log hashes only)
- API tokens or secrets if accidentally captured
- User identifiers (unless explicitly allowed)
