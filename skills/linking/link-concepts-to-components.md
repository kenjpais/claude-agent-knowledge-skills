---
name: link-concepts-to-components
description: Create bidirectional links between domain concepts and components that implement them
type: linking
category: navigation
---

# Link Concepts to Components

## Overview
Establishes bidirectional navigation between abstract concepts (in agentic/domain/concepts/) and concrete implementations (in agentic/design-docs/components/). Critical for intent-based navigation.

## When to Use
- After generating both concept and component documentation
- Before generating AGENTS.md
- When updating documentation after code changes
- As part of linking phase

## Process
1. Load all concept documents from agentic/domain/concepts/
2. Load all component documents from agentic/design-docs/components/
3. For each concept:
   - Identify related components by:
     - Keyword matching in component descriptions
     - Type/struct name matching
     - CRD group/kind matching for OpenShift concepts
     - Import/dependency analysis
   - Calculate relevance scores
   - Keep top N most relevant components
4. For each component:
   - Identify related concepts by reverse mapping
   - Add "Related Concepts" section if not present
5. Update both concept and component docs with cross-links
6. Validate all links are bidirectional
7. Log linking operations

## Verification
- [ ] All concepts processed
- [ ] All components processed
- [ ] Links are bidirectional
- [ ] Relevance scores calculated
- [ ] Low-confidence links flagged for review
- [ ] Documents updated in place
- [ ] Operation logged

## Input Schema
```yaml
concepts_directory: string
components_directory: string
min_relevance_score: float  # 0-1, threshold for linking
max_links_per_doc: integer  # Avoid over-linking
```

## Output Schema
```yaml
success: boolean
links_created: integer
concepts_processed: integer
components_processed: integer
links: array<Link>
  - concept: string
    component: string
    relevance: float
    bidirectional: boolean
low_confidence_links: array<Link>
warnings: array<string>
```

## Linking Strategies
1. **Direct naming match**: Concept "Reconciler" → Component "machine-controller" containing Reconciler type
2. **CRD-based**: Concept "Machine" → Component managing Machine CRD
3. **Dependency-based**: Concept "Authentication" → Components importing auth packages
4. **Keyword extraction**: NLP-based matching on descriptions

## Red Flags
- **No links found for concept**: May indicate concept is too abstract or undocumented
- **Component with 0 concept links**: May be missing domain documentation
- **Many low-confidence links**: Review and potentially add explicit link markers in docs
