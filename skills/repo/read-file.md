---
name: read-file
description: Read file contents from the target repository
type: repo
category: access
---

# Read File

## Overview
Atomically reads file contents from the target OpenShift repository. This is the only authorized method for accessing source code.

## When to Use
- When you need to examine specific file contents
- Before performing any extraction or parsing operation
- When validating file existence before processing
- When checking file structure before modification

## Process
1. Verify file path is within repository boundaries
2. Use Read tool to access file contents
3. Log file access operation with timestamp and agent ID
4. Return file contents or error if file doesn't exist
5. Cache file hash for change detection

## Verification
- [ ] File path validated and sanitized
- [ ] Access operation logged to monitoring system
- [ ] File contents returned or appropriate error raised
- [ ] No sensitive data exposed in logs

## Output Schema
```yaml
success: boolean
file_path: string
content: string
content_hash: string
timestamp: string
error: string | null
```
