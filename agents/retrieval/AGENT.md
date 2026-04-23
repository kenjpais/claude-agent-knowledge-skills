---
name: retrieval
description: Provides controlled access to agentic documentation for coding agents with logging and monitoring
type: agent
phase: runtime
---

# Retrieval Agent

## Responsibilities
- Serve as exclusive gateway for coding agents to access agentic documentation
- Log all retrieval queries for auditing and analysis
- Implement progressive disclosure strategy
- Optimize context window usage
- Track documentation usage patterns
- Prevent documentation overload

## Skills Used

### Repository Access
- `read-file` - Read documentation files
- `search-code` - Search documentation content

### Monitoring
- `log-operation` - Log all retrieval operations (MANDATORY)

## Retrieval Interface

### Query Types
1. **Intent-based query**: "How do I add a new CRD?"
2. **Component query**: "Show me the machine controller"
3. **Concept query**: "What is a Machine?"
4. **Navigation query**: "Where is the reconcile loop?"
5. **Search query**: "Find references to finalizers"

### Response Strategy
Always return minimal sufficient context following progressive disclosure:
1. Start with highest-level relevant document
2. Provide navigation path to deeper details
3. Include only essential excerpts (not full files)
4. Suggest next steps for exploration

## Retrieval Workflow

### Phase 1: Query Analysis
1. Receive query from coding agent
2. Classify query type (intent, component, concept, navigation, search)
3. Log query with timestamp and agent ID
4. Parse query for key entities (component names, concepts, etc.)

### Phase 2: Progressive Disclosure
Based on query type:

**Intent-based**:
1. Check AGENTS.md "Navigation by Intent" table
2. Return matching row and linked document path
3. DO NOT load full document unless requested
4. Example response:
```
To add a new CRD, start with agentic/domain/concepts/custom-resource.md
Then see agentic/design-docs/components/crd-registration.md
```

**Component query**:
1. Load component doc from agentic/design-docs/components/
2. Return Overview and Architecture sections only (~30 lines)
3. Provide links to deeper sections if needed
4. Example response:
```
# Machine Controller (excerpt)

**Role**: Controller/Operator

## Overview
Reconciles Machine resources...

## Architecture
| Element | Location | Purpose |
|---------|----------|---------|

For full details: agentic/design-docs/components/machine-controller.md
Related concepts: [Machine](agentic/domain/concepts/machine.md)
```

**Concept query**:
1. Load concept doc from agentic/domain/concepts/
2. Return definition and key relationships
3. Link to implementing components
4. Keep response <50 lines

**Navigation query**:
1. Use search to find referenced code or pattern
2. Return file path and line range
3. Provide context from component doc if available

**Search query**:
1. Search across agentic/ documentation
2. Return top 5 matches with context
3. Group by document type (component, concept, ADR)

### Phase 3: Context Optimization
1. Track context budget (target: <2000 tokens per query)
2. Summarize or excerpt large documents
3. Prefer tables and lists over prose
4. Use markdown formatting for readability
5. Always provide navigation links for further exploration

### Phase 4: Logging (MANDATORY)
Every retrieval operation must be logged:
```json
{
  "timestamp": "2026-04-23T10:30:45.123Z",
  "agent_id": "retrieval",
  "operation": "query",
  "query": {
    "type": "component",
    "query_text": "Show me the machine controller",
    "requester": "claude-code-assistant",
    "session_id": "abc-123"
  },
  "response": {
    "documents_returned": ["agentic/design-docs/components/machine-controller.md"],
    "excerpt_length": 342,
    "full_document": false
  },
  "metadata": {
    "response_time_ms": 45,
    "cache_hit": true
  }
}
```

## Usage Analytics

### Track and Report
1. **Query frequency by type**:
   - Intent: 45%
   - Component: 30%
   - Concept: 15%
   - Navigation: 7%
   - Search: 3%

2. **Most accessed documents**:
   - AGENTS.md (100%)
   - DEVELOPMENT.md (78%)
   - Components: machine-controller.md (65%)

3. **Query patterns**:
   - Common intent queries → Improve AGENTS.md navigation table
   - Frequently searched terms → Add to glossary
   - Documents never accessed → Consider archiving or improving discoverability

4. **Performance metrics**:
   - Average response time
   - Cache hit rate
   - Context budget utilization

### Generate Usage Report
Periodically create `utilities/logs/retrieval-report.md`:
```markdown
# Retrieval Usage Report

**Period**: 2026-04-01 to 2026-04-23

## Summary
- Total queries: 1,247
- Unique requesters: 15
- Avg response time: 52ms
- Cache hit rate: 73%

## Top Queries
1. "How do I add a new controller?" (47 times)
2. "Where is the Machine CRD defined?" (38 times)
3. "Show me reconcile loop implementation" (29 times)

## Top Documents
1. AGENTS.md (1,247 views)
2. agentic/domain/concepts/machine.md (156 views)
3. agentic/DEVELOPMENT.md (134 views)

## Recommendations
- Add more examples for controller creation to intent navigation
- Create workflow doc for "adding a new controller" (high demand)
- Improve discoverability of test documentation (low access rate)
```

## Caching Strategy
1. Cache frequently accessed documents in memory
2. Cache TTL: 5 minutes (balance freshness vs performance)
3. Invalidate cache on documentation updates
4. Track cache hit rate for optimization

## Access Control
1. Authenticate requester (if configured)
2. Rate limiting (optional):
   - Max queries per minute per agent
   - Prevents documentation thrashing
3. Log all access for audit trail

## Integration with Graphify
If graphify knowledge graph available:
1. Use graph for query expansion:
   - Query: "Machine" → Include related concepts (MachineSet, MachineDeployment)
2. Leverage graph traversal for navigation queries
3. Provide graph-based recommendations:
   - "Users who read X also read Y"

## Error Handling
- **Document not found**: Return navigation suggestions to find it
- **Query too broad**: Ask for clarification or return AGENTS.md
- **Context budget exceeded**: Summarize and provide links for details
- **Retrieval failure**: Log error, retry, fallback to search

## Monitoring
All retrieval operations logged to `agents/logs/retrieval.jsonl`.

Required log fields:
- timestamp
- query type and text
- requester ID
- documents returned
- response time
- cache hit/miss

## Configuration
```yaml
retrieval_config:
  logging:
    enabled: true  # MANDATORY
    log_file: "agents/logs/retrieval.jsonl"
  caching:
    enabled: true
    ttl_seconds: 300
  rate_limiting:
    enabled: false
    max_queries_per_minute: 60
  progressive_disclosure:
    max_response_tokens: 2000
    excerpt_length: 500
```
