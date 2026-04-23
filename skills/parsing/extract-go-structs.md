---
name: extract-go-structs
description: Parse Go files to extract struct definitions, methods, and interfaces
type: parsing
category: extraction
---

# Extract Go Structs

## Overview
Uses AST parsing to deterministically extract Go type definitions, struct fields, methods, and interface signatures from source files.

## When to Use
- Discovering API types and CRD structures in OpenShift
- Building data model documentation
- Identifying component interfaces and contracts
- Mapping reconciler types in operators

## Process
1. Read Go source file using read-file skill
2. Parse file into AST using go/parser
3. Walk AST to identify:
   - Type declarations (structs, interfaces, aliases)
   - Struct fields with tags and comments
   - Method receivers and signatures
   - Interface methods
4. Extract embedded documentation from comments
5. Capture package imports for dependency analysis
6. Return structured type information

## Verification
- [ ] All struct definitions extracted
- [ ] Field tags preserved (json, yaml, protobuf)
- [ ] Method receivers correctly associated
- [ ] Doc comments captured
- [ ] Interface signatures complete
- [ ] No interpretation added (pure extraction)

## Input Schema
```yaml
file_path: string
include_private: boolean  # Include unexported types
include_methods: boolean
include_comments: boolean
```

## Output Schema
```yaml
success: boolean
package: string
imports: array<string>
types: array<TypeDef>
  - name: string
    kind: string  # struct | interface | alias
    exported: boolean
    doc_comment: string
    fields: array<Field>  # For structs
      - name: string
        type: string
        tag: string
        comment: string
    methods: array<Method>  # For interfaces or struct methods
      - name: string
        signature: string
        doc_comment: string
```

## Rationalizations
| Excuse | Rebuttal |
|--------|----------|
| "I'll just use regex to parse the structs" | AST parsing is deterministic and handles edge cases. Regex breaks on nested types, comments, and complex syntax. |
| "I can infer field purposes from names" | This is a parsing skill. Inference happens in the synthesis phase. Stay in your lane. |
