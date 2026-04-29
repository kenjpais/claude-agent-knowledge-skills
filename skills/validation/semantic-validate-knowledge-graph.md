---
name: semantic-validate-knowledge-graph
description: LLM-based validation of knowledge graph semantic quality, retrieval readiness, and traceability
type: validation
category: semantic
---

# Semantic Knowledge Graph Validation

## Overview
Validates that the knowledge graph at `agentic/knowledge-graph/graph.json` is semantically correct: edges describe real relationships, nodes are properly classified, retrieval paths produce useful context bundles, and no hallucinated content exists. Complements deterministic graph checks (schema, reachability, orphans) with semantic reasoning.

## When to Use
- After generating or updating the knowledge graph
- As part of semantic validation phase
- When retrieval quality is poor despite passing structural checks

## Process
Load graph from `agentic/knowledge-graph/graph.json` and read linked documents.

### Checks to Run (14 total)

**Structure & Classification**

1. **Edge Type Semantic Accuracy** — For each edge, read both connected documents. Verify the edge type (DECIDED_BY, DEEP_DIVE, RELATED, PLANNED_IN, EXPLAINED_BY, CONTAINS, NEXT, REFERENCES, INDEXES) correctly describes the actual relationship. Severity: FAIL.

2. **Node Type Classification** — Verify each node's type (Concept, Workflow, ADR, ExecutionPlan, Document, Section, EntryPoint) matches the actual content of the linked document. Severity: FAIL.

3. **Content-to-Graph Consistency** — Verify node metadata (title, description, attributes) accurately reflects the linked document's current content. Flag stale or misleading metadata. Severity: WARN.

4. **Node Label and Description Clarity** — Assess whether labels and descriptions are clear enough for the Retrieval Agent to correctly resolve queries. Flag ambiguous, jargon-heavy, or overly generic labels. Severity: WARN.

**Completeness & Redundancy**

5. **Missing Relationship Inference** — Identify semantic relationships that clearly exist between documents but have no edge. Prioritize: ADRs-to-concepts, concepts-to-workflows, and prose cross-references without graph edges. Severity: WARN.

6. **Semantic Redundancy** — Identify nodes representing the same concept under different names or variations. Look for synonym pairs and abbreviation mismatches. Recommend merge candidates. Severity: WARN.

7. **Concept Coverage Completeness** — Read the full documentation corpus under `agentic/`. Identify significant domain concepts discussed in docs that lack a corresponding Concept node in the graph. These are retrieval blind spots. Severity: WARN.

**Edge Quality**

8. **Edge Plausibility** — For each RELATED and REFERENCES edge, assess whether the relationship is genuinely meaningful and informative. Flag low-value edges that waste retrieval hops without adding useful context. Severity: WARN.

9. **Workflow Sequence Coherence** — For NEXT edge chains, read documents in order. Assess whether the sequence forms a logically coherent reading order with prerequisites before dependents. Flag illogical ordering. Severity: WARN.

10. **Progressive Disclosure Quality** — Trace paths from EntryPoint (AGENTS.md) through INDEXES and DEEP_DIVE edges. Assess whether each hop adds genuinely new detail rather than repeating parent content. Severity: WARN.

**Traceability & Accuracy**

11. **ADR Decision Traceability** — Verify each ADR node contains a clear, specific decision (not a discussion or placeholder). Verify DECIDED_BY edges point to concepts or features the ADR actually addresses. Severity: FAIL.

12. **Cross-Document Consistency** — For documents connected by edges, check for factual contradictions. Flag cases where connected docs make conflicting claims about the same topic. Severity: FAIL.

13. **Hallucination Detection** — For LLM-generated ADRs and execution plans, check for fabricated claims or unsubstantiated statements. Compare against source material referenced in provenance metadata. Severity: FAIL.

**Retrieval Simulation**

14. **Context Bundle Retrieval Quality** — Pick 3-5 sample queries (e.g., "How does X work?", "Why was Y decided?", "What is the workflow for Z?"). Traverse the graph as a Retrieval Agent would (start node → neighbors → rank → limit to 3 hops and <700 lines). Assess whether each bundle answers the query. Severity: WARN.

## Verification
- [ ] Graph loaded and all nodes/edges read
- [ ] Edge types verified against actual document relationships
- [ ] Node types verified against document content
- [ ] Missing relationships identified
- [ ] Redundant nodes flagged
- [ ] Retrieval simulation completed for 3-5 queries
- [ ] Hallucination check completed on generated content

## Input Schema
```yaml
graph_path: string  # agentic/knowledge-graph/graph.json
agentic_directory: string
retrieval_budget: integer  # Default: 700 lines
max_hops: integer  # Default: 3
sample_queries: array<string>  # Optional, auto-generated if omitted
```

## Output Schema
```yaml
passed: boolean
summary:
  checks_run: 14
  passed: integer
  failed: integer
  warnings: integer
findings: array<Finding>
  - check: string
    severity: string  # PASS, FAIL, WARN
    affected_nodes: array<string>
    affected_edges: array<string>
    evidence: string
    recommendation: string
retrieval_simulation:
  queries_tested: integer
  queries_answered: integer
  avg_hops: float
  avg_lines: integer
```

## Red Flags
- **Edge type mismatches**: Retrieval Agent will follow wrong paths — corrupts query results
- **Hallucinated content in ADR nodes**: Agents will act on fabricated architectural decisions
- **Retrieval simulation fails > 1 query**: Graph structure isn't serving its purpose
- **> 3 missing relationships found**: Graph is incomplete — agents miss connections
