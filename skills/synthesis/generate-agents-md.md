---
name: generate-agents-md
description: Create the primary AGENTS.md entry point with navigation structure
type: synthesis
category: documentation
---

# Generate AGENTS.md

## Overview
Synthesizes the primary entry point for agent navigation. Must be ≤150 lines and provide complete navigation to all documentation. This is the most critical file in the agentic documentation system.

## When to Use
- After all component documentation generated
- After concept and domain documentation created
- As final step in linking phase
- When updating navigation after changes

## Process
1. Gather inputs:
   - List of all components with roles
   - List of all domain concepts
   - Build commands from DEVELOPMENT.md
   - Critical invariants from component docs
2. Structure AGENTS.md with required sections:
   - **What This Repository Does** (3-4 sentences max)
   - **Navigation by Intent** (table mapping tasks to files)
   - **Repository Structure** (critical directories only)
   - **Component Boundaries** (table with component, role, entry point)
   - **Core Concepts** (list with links to domain/)
   - **Key Invariants** (5-7 most critical rules)
   - **Critical Code Locations** (table with common tasks)
   - **Build & Test** (essential commands only)
3. Enforce 150-line budget:
   - Use tables instead of paragraphs
   - Link extensively instead of explaining
   - Remove any narrative
4. Validate all links
5. Write to repository root as AGENTS.md

## Verification
- [ ] All 8 required sections present
- [ ] Line count ≤ 150
- [ ] All links valid and reachable
- [ ] Navigation by intent covers 80% of common tasks
- [ ] No duplicated information from other docs
- [ ] Tables used for dense information
- [ ] Written to repository root

## Input Schema
```yaml
components: array<Component>
concepts: array<Concept>
build_commands: array<Command>
invariants: array<string>
repository_purpose: string
```

## Output Schema
```yaml
success: boolean
file_path: string
line_count: integer
sections: array<string>
links: array<string>
warnings: array<string>  # Budget violations, missing sections
```

## Template Structure
```markdown
# AGENTS.md

## What This Repository Does
{3-4 sentences}

## Navigation by Intent
| I want to... | Start here |
|--------------|------------|

## Repository Structure
{Critical directories only}

## Component Boundaries
| Component | Role | Entry Point |
|-----------|------|-------------|

## Core Concepts
- [{Concept}](agentic/domain/concepts/{concept}.md)

## Key Invariants
1. {Critical rule}

## Critical Code Locations
| Task | Location |
|------|----------|

## Build & Test
{Essential commands}
```

## Rationalizations
| Excuse | Rebuttal |
|--------|----------|
| "I need more than 150 lines to explain everything" | You don't explain, you navigate. Link to details. |
| "The navigation table doesn't cover every scenario" | Cover 80% of common tasks. Edge cases follow links. |
