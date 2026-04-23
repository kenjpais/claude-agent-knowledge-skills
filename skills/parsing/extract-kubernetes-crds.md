---
name: extract-kubernetes-crds
description: Parse Kubernetes CRD YAML definitions and extract schema, validation, and metadata
type: parsing
category: extraction
openshift: true
---

# Extract Kubernetes CRDs

## Overview
Parses CustomResourceDefinition YAML files to extract API group, version, schema, validation rules, and subresources. Critical for documenting OpenShift operator APIs.

## When to Use
- Documenting operator-managed custom resources
- Building API reference for OpenShift components
- Mapping CRDs to controller implementations
- Extracting validation constraints for testing

## Process
1. Locate CRD YAML files using list-files with pattern "**/*crd*.yaml"
2. Read each CRD file
3. Parse YAML structure
4. Extract metadata:
   - Group, version, kind
   - Plural, singular, short names
   - Scope (Namespaced vs Cluster)
5. Extract schema from OpenAPIV3Schema
6. Identify subresources (status, scale)
7. Capture validation rules and defaults
8. Document printer columns for kubectl output
9. Return structured CRD definitions

## Verification
- [ ] All CRD files discovered
- [ ] Group/Version/Kind correctly extracted
- [ ] Schema structure preserved
- [ ] Validation rules captured
- [ ] Subresources identified
- [ ] No YAML parsing errors

## Input Schema
```yaml
directory: string  # Usually manifests/ or config/crd
recursive: boolean
```

## Output Schema
```yaml
success: boolean
crds: array<CRD>
  - api_version: string
    kind: string
    group: string
    versions: array<Version>
      - name: string
        served: boolean
        storage: boolean
        schema: object
        subresources: object
    scope: string
    names:
      plural: string
      singular: string
      kind: string
      short_names: array<string>
    printer_columns: array<object>
```

## Rationalizations
| Excuse | Rebuttal |
|--------|----------|
| "I can skip older API versions" | All versions must be documented. Deprecation happens in synthesis, not extraction. |
| "Schema is too complex to parse fully" | Full schema extraction is required for accurate API docs. Use YAML parser libraries. |
