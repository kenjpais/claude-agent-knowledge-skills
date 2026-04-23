---
name: generate-component-doc
description: Synthesize component documentation from extracted data and inferred meaning
type: synthesis
category: documentation
---

# Generate Component Doc

## Overview
Combines extraction outputs (structs, CRDs, dependencies) with inference results (boundaries, roles) to produce structured component documentation following agentic-docs template.

## When to Use
- After component boundaries inferred
- After service role classified
- When extraction phase complete for a component
- To create initial component documentation

## Process
1. Load inputs from previous phases:
   - Component boundary definition
   - Service role classification
   - Extracted types/APIs
   - Dependency information
2. Select appropriate template based on role:
   - Controller template for operators
   - Library template for shared packages
   - CLI template for command-line tools
3. Synthesize documentation sections:
   - **Overview**: Purpose and responsibilities (2-3 sentences)
   - **Architecture**: Key types, interfaces, entry points
   - **Dependencies**: Internal and external dependencies
   - **API Surface**: Public interfaces, CRDs, or commands
   - **Configuration**: Environment variables, flags, config files
   - **Key Invariants**: Critical rules that must not be violated
4. Add navigation links to:
   - Related components
   - Relevant concepts in domain/
   - ADRs if architectural decisions detected
5. Keep within 100-line budget per component doc
6. Write to agentic/design-docs/components/{component-name}.md

## Verification
- [ ] Correct template selected based on role
- [ ] All required sections present
- [ ] Navigation links valid
- [ ] 100-line budget not exceeded
- [ ] File written to correct location
- [ ] Markdown valid
- [ ] No interpretation beyond extracted facts

## Input Schema
```yaml
component: object  # From infer-component-boundary
role: object  # From classify-service-role
extracted_data:
  types: array
  crds: array
  dependencies: object
```

## Output Schema
```yaml
success: boolean
file_path: string
sections: array<string>  # Sections included
line_count: integer
links: array<string>
warnings: array<string>  # Budget violations, missing data
```

## Template Structure
```markdown
# Component: {Name}

**Role**: {Primary Role}
**Confidence**: {Score}

## Overview
{2-3 sentence purpose}

## Architecture
| Element | Location | Purpose |
|---------|----------|---------|

## Dependencies
**Internal**: {list}
**External**: {list}

## API Surface
{Interfaces, CRDs, or Commands}

## Key Invariants
- {Critical rules}

## Navigation
- Related: {links}
- Concepts: {links}
- Decisions: {links}
```

## Rationalizations
| Excuse | Rebuttal |
|--------|----------|
| "I'll add narrative explanations for clarity" | Stay mechanical. Narrative belongs in ADRs or concept docs, not component docs. |
| "100 lines isn't enough for complex components" | Progressive disclosure. Link to code for details, don't duplicate it. |
