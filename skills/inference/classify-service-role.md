---
name: classify-service-role
description: Infer the role of a component (controller, API server, webhook, CLI, library)
type: inference
category: analysis
openshift: true
---

# Classify Service Role

## Overview
Analyzes component characteristics to classify its role within the system. Essential for structuring component documentation appropriately.

## When to Use
- After identifying component boundaries
- Before generating component documentation
- To determine documentation template to use
- When organizing architecture diagrams

## Process
1. Analyze component characteristics:
   - Has main() function → Executable (vs library)
   - Imports controller-runtime → Likely controller/operator
   - Exposes HTTP endpoints → API server or webhook
   - Has CRD definitions → Operator
   - CLI flag parsing → Command-line tool
   - No main, only exports → Library
2. Check for role-specific patterns:
   - **Controller**: Reconcile loops, watches
   - **Webhook**: Validation/mutation handlers
   - **API Server**: REST handlers, OpenAPI
   - **CLI**: Command structure, flag definitions
   - **Library**: Public API, no runtime logic
3. Assign primary and secondary roles (components can be multi-role)
4. Calculate confidence based on pattern matches
5. Return classification with supporting evidence

## Verification
- [ ] All role patterns checked
- [ ] Primary role identified
- [ ] Secondary roles listed if applicable
- [ ] Confidence score calculated
- [ ] Evidence captured for verification
- [ ] Classification logged

## Input Schema
```yaml
component_name: string
files: array<string>
dependency_graph: string
```

## Output Schema
```yaml
success: boolean
classification:
  primary_role: string  # controller | webhook | api-server | cli | library | agent
  secondary_roles: array<string>
  confidence: float
  evidence: array<Evidence>
    - pattern: string
      location: string
      weight: float
  characteristics:
    is_executable: boolean
    has_api: boolean
    manages_crds: boolean
    has_reconcile_loop: boolean
```

## Role Definitions
- **Controller/Operator**: Manages Kubernetes resources via reconcile loops
- **Webhook**: Validates or mutates Kubernetes API requests
- **API Server**: Exposes REST API (often aggregated API server)
- **CLI**: Command-line interface for users or scripts
- **Library**: Reusable code with no runtime behavior
- **Agent**: Runs on nodes, collects data or enforces policy
