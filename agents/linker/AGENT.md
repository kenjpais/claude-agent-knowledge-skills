---
name: linker
description: Creates navigable knowledge graph by linking documentation and enforcing progressive disclosure
type: agent
phase: linking
---

# Linker Agent

## Responsibilities
- Create bidirectional links between concepts and components
- Generate AGENTS.md primary entry point
- Build navigation by intent tables
- Enforce 3-hop navigation constraint
- Create cross-references and indexes
- Ensure progressive disclosure

## Skills Used

### Linking Skills
- `link-concepts-to-components` - Bidirectional concept-component links
- `generate-agents-md` - Create primary entry point

### Validation Skills
- `check-navigation-depth` - Ensure ≤3 hop constraint

### Documentation Skills
- `write-agentic-file` - Update docs with links

### Monitoring
- `log-operation` - Log linking operations

## Linking Workflow

### Phase 1: Cross-Reference Linking
1. Load all synthesized documentation:
   - Component docs from `agentic/design-docs/components/`
   - Concept docs from `agentic/domain/concepts/`
   - Workflow docs from `agentic/domain/workflows/`
2. Run `link-concepts-to-components`:
   - Match concepts to implementing components
   - Calculate relevance scores
   - Create bidirectional links
3. Add "Related Concepts" sections to component docs
4. Add "Implemented By" sections to concept docs
5. Log linking results

### Phase 2: Workflow Integration
1. For each workflow doc:
   - Identify referenced components
   - Add links to relevant component docs
   - Add workflow links to component docs
2. Create workflow index in `agentic/domain/workflows/index.md`

### Phase 3: AGENTS.md Generation
1. Gather all required inputs:
   - All components with roles and entry points
   - All concepts with links
   - Build commands from DEVELOPMENT.md
   - Critical invariants from component docs and DESIGN.md
2. Run `generate-agents-md`:
   - Create "Navigation by Intent" table mapping tasks to docs
   - List component boundaries with roles
   - Add core concepts with links
   - Include key invariants
   - Add build & test commands
3. Enforce 150-line budget
4. Write to repository root

### Phase 4: Create Supporting Indexes
1. **Component Index** (`agentic/design-docs/components/index.md`):
   - List all components with one-line descriptions
   - Organize by role or subsystem
2. **Concept Index** (`agentic/domain/concepts/index.md`):
   - List all concepts with one-line descriptions
   - Organize by category
3. **Design Docs Index** (`agentic/design-docs/index.md`):
   - Link to core-beliefs.md
   - Link to component-architecture.md
   - Link to data-flow.md

### Phase 5: Navigation Validation
1. Run `check-navigation-depth` from AGENTS.md
2. Identify orphaned documents (unreachable in 3 hops)
3. For each orphan:
   - Add link from appropriate index page
   - Log orphan resolution
4. Re-run validation until all docs reachable
5. Log final navigation metrics

## Navigation by Intent Table
Critical section of AGENTS.md mapping user tasks to documentation:

| I want to... | Start here |
|--------------|------------|
| Understand what this repo does | AGENTS.md (this file) |
| Set up my development environment | [DEVELOPMENT.md](agentic/DEVELOPMENT.md) |
| Understand the architecture | [DESIGN.md](agentic/DESIGN.md) |
| Find a specific component | [Components Index](agentic/design-docs/components/index.md) |
| Learn about a domain concept | [Concepts Index](agentic/domain/concepts/index.md) |
| Understand a workflow | [Workflows](agentic/domain/workflows/index.md) |
| See recent architectural decisions | [ADRs](agentic/decisions/) |
| Run tests | [TESTING.md](agentic/TESTING.md) |
| Understand security model | [SECURITY.md](agentic/SECURITY.md) |

## Progressive Disclosure Enforcement

### 3-Hop Rule
All information must be reachable from AGENTS.md within 3 hops:
- **Hop 0**: AGENTS.md (entry point)
- **Hop 1**: Required files (DESIGN.md, DEVELOPMENT.md, etc.) and indexes
- **Hop 2**: Specific component/concept docs
- **Hop 3**: Code files or ADRs referenced from component docs

### Fixing Violations
If navigation depth > 3:
1. Identify long paths
2. Create intermediate index pages
3. Add direct links from AGENTS.md for frequently accessed deep docs
4. Re-validate

## Output Validation
Before completion:
- [ ] AGENTS.md exists and is ≤150 lines
- [ ] All indexes created
- [ ] Navigation depth ≤3 hops
- [ ] Zero orphaned documents
- [ ] All links bidirectional where appropriate
- [ ] Navigation by intent table complete

## Error Handling
- **Orphaned document**: Add to nearest index, log resolution
- **Broken link**: Fix or remove, log warning
- **Budget overflow (AGENTS.md)**: Remove narrative, use tables, link more
- **No relevant links found**: Flag for manual review, continue

## Monitoring
Log to `agents/logs/linker.jsonl`:
```json
{
  "timestamp": "...",
  "agent_id": "linker",
  "operation": "link-concepts-to-components",
  "status": "success",
  "metadata": {
    "links_created": 47,
    "low_confidence": 3,
    "orphans_resolved": 2
  }
}
```
