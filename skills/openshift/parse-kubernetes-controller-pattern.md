---
name: parse-kubernetes-controller-pattern
description: Identify and extract Kubernetes controller pattern components from code
type: parsing
category: extraction
openshift: true
---

# Parse Kubernetes Controller Pattern

## Overview
Detects and extracts the standard Kubernetes controller pattern: Reconcile loop, client setup, watch predicates, event handlers, and status updates. Essential for OpenShift operator documentation.

## When to Use
- Documenting OpenShift operator behavior
- Understanding reconciliation logic
- Mapping CRDs to their controllers
- Identifying control loops and their triggers

## Process
1. Search for controller registration patterns:
   - controller-runtime SetupWithManager
   - client-go controller structures
   - Operator SDK patterns
2. Identify reconcile function:
   - Method name matching "Reconcile"
   - Signature matching controller-runtime interface
3. Extract watch configuration:
   - Primary resource watches
   - Secondary resource watches (Owns, Watches)
   - Event predicates and filters
4. Parse reconcile logic:
   - Resource fetch operations
   - Condition checks and status updates
   - Finalizer handling
   - Requeue behavior
5. Document observed resources and mutations
6. Return structured controller definition

## Verification
- [ ] Reconcile function identified
- [ ] Watched resources documented
- [ ] Status update locations found
- [ ] Finalizer logic extracted
- [ ] Requeue conditions documented
- [ ] Client initialization captured

## Input Schema
```yaml
controller_file: string
include_predicates: boolean
include_status_updates: boolean
```

## Output Schema
```yaml
success: boolean
controller:
  name: string
  reconcile_function: string
  primary_resource:
    group: string
    version: string
    kind: string
  watches: array<Watch>
    - resource: string
      type: string  # owns | watches
      predicates: array<string>
  finalizers: array<string>
  status_conditions: array<string>
  requeue_scenarios: array<Scenario>
    - condition: string
      requeue_after: string
      reason: string
```

## Rationalizations
| Excuse | Rebuttal |
|--------|----------|
| "I'll document the high-level flow only" | Precise extraction of watches and predicates is required for accurate docs. |
| "Reconcile logic is too complex to parse" | Extract structure only. Semantic understanding happens in synthesis phase. |
