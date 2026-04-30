---
name: extract-repository-structure
description: Consolidated extraction skill - deterministically parses repository structure, Go types, CRDs, and builds dependency graph
type: skill
category: extraction
phase: documentation-generation
---

# Extract Repository Structure

## Purpose

Single consolidated skill that performs ALL deterministic repository extraction:
- File discovery
- Go type parsing (structs, interfaces, methods)
- Kubernetes CRD extraction
- Dependency graph construction
- Controller pattern detection

**This skill replaces**:
- `list-files`
- `extract-go-structs`
- `extract-kubernetes-crds`
- `build-dependency-graph`
- `parse-kubernetes-controller-pattern`

## When to Use

- During `/create` command (Phase 1: Extraction)
- When fresh repository analysis is needed
- Before documentation synthesis

## Input

```yaml
repository_path: string  # Local path or will be cloned
scope: full | component | incremental
  # full: Entire repository
  # component: Specific component directories
  # incremental: Only changed files (requires git history)
exclusions:
  - ".git"
  - "vendor/"
  - "node_modules/"
  - "*.test.go"
```

## Output

```yaml
extraction_artifacts:
  files:
    total_files: integer
    go_files: integer
    yaml_files: integer
    
  go_analysis:
    packages:
      - path: string
        types:
          - name: string
            kind: struct | interface | type_alias
            fields: array
            methods: array
        imports: array<string>
    
  crds:
    - group: string
      version: string
      kind: string
      plural: string
      schema: object
      validation: object
      
  dependency_graph:
    nodes:
      - id: string  # package path
        label: string
        type: package | component | module
    edges:
      - source: string
        target: string
        type: import | dependency
        
  controllers:
    - name: string
      package: string
      reconcile_function: string
      watches:
        - resource: string
          kind: string
      finalizers: array<string>
      
  metrics:
    extraction_duration_seconds: float
    files_processed: integer
    parse_errors: integer
```

## Process

### Step 1: File Discovery

```bash
# List all files by type
find $repository_path -type f \
  -not -path "*/.git/*" \
  -not -path "*/vendor/*" \
  -not -path "*/node_modules/*"

# Categorize:
go_files=$(find . -name "*.go" -not -name "*_test.go")
yaml_files=$(find . -name "*.yaml" -o -name "*.yml")
```

### Step 2: Parse Go Files

For each `*.go` file:

```go
// Use Go AST parser
import (
    "go/parser"
    "go/ast"
    "go/token"
)

fset := token.NewFileSet()
node, err := parser.ParseFile(fset, filename, nil, parser.ParseComments)

// Extract:
// - Package name
// - Imports
// - Type declarations (structs, interfaces)
// - Functions and methods
// - Constants and variables

// Store in structured format
```

**Extract**:
- Package declarations
- Import statements
- Struct definitions (name, fields, tags)
- Interface definitions (name, methods)
- Type aliases
- Function signatures
- Method receivers and signatures

### Step 3: Parse Kubernetes CRDs

For each YAML file in directories: `config/crd/`, `deploy/crds/`, `manifests/`:

```python
import yaml

with open(yaml_file, 'r') as f:
    doc = yaml.safe_load(f)
    
if doc.get('kind') == 'CustomResourceDefinition':
    extract_crd_schema(doc)
```

**Extract**:
- `spec.group`
- `spec.versions[]` (name, schema, served, storage)
- `spec.names` (kind, plural, singular, shortNames)
- `spec.scope` (Namespaced | Cluster)
- `spec.validation.openAPIV3Schema`
- Status subresource configuration

### Step 4: Build Dependency Graph

```python
import networkx as nx

G = nx.DiGraph()

# Add nodes (packages)
for package in go_packages:
    G.add_node(package.path, label=package.name, type='package')

# Add edges (imports)
for package in go_packages:
    for import_path in package.imports:
        if import_path in local_packages:  # Only local imports
            G.add_edge(package.path, import_path, type='import')

# Detect components via community detection
from networkx.algorithms import community
communities = community.louvain_communities(G.to_undirected())

# Components are tightly coupled package clusters
components = []
for i, comm in enumerate(communities):
    components.append({
        'id': f'component-{i}',
        'packages': list(comm),
        'cohesion': calculate_modularity(G, comm)
    })
```

### Step 5: Detect Controller Patterns

For each Go package, search for controller patterns:

```python
controller_indicators = [
    'Reconcile(ctx context.Context, req reconcile.Request)',
    'SetupWithManager(mgr ctrl.Manager)',
    'controller-runtime/pkg/reconcile',
    'Watch(source.Kind',
]

for go_file in go_files:
    if contains_any(go_file, controller_indicators):
        extract_controller_structure(go_file)
```

**Extract**:
- Controller struct name
- Reconcile function signature
- Watched resources (from `Watch()` calls)
- Finalizers (from string literals or constants)
- RBAC markers (from `//+kubebuilder:rbac` comments)

### Step 6: Write Artifacts

```python
import json

output_dir = f"{repository_path}/.agentic-extraction/"
os.makedirs(output_dir, exist_ok=True)

# Write structured JSON artifacts
with open(f"{output_dir}/go-analysis.json", 'w') as f:
    json.dump(go_analysis, f, indent=2)

with open(f"{output_dir}/crds.json", 'w') as f:
    json.dump(crds, f, indent=2)

with open(f"{output_dir}/dependency-graph.json", 'w') as f:
    # NetworkX node-link format
    from networkx.readwrite import json_graph
    graph_data = json_graph.node_link_data(G)
    json.dump(graph_data, f, indent=2)

with open(f"{output_dir}/controllers.json", 'w') as f:
    json.dump(controllers, f, indent=2)

with open(f"{output_dir}/extraction-metadata.json", 'w') as f:
    json.dump({
        'timestamp': datetime.utcnow().isoformat(),
        'repository': repository_path,
        'scope': scope,
        'metrics': metrics
    }, f, indent=2)
```

## Error Handling

### Parse Errors
```
IF Go file fails to parse:
  - Log error with filename and line
  - Continue with remaining files
  - Include in metrics.parse_errors

IF YAML file invalid:
  - Log warning
  - Skip file
  - Continue
```

### Large Files
```
IF file size > 10MB:
  - Log warning
  - Skip file (likely generated code or binary)
  - Continue
```

### Missing Dependencies
```
IF import references non-existent package:
  - Mark as external dependency
  - Don't create graph edge to missing package
  - Log warning
```

## Verification

- [ ] All `*.go` files discovered (excluding test files if scope specifies)
- [ ] Go AST parsing successful for ≥95% of Go files
- [ ] All CRD YAML files in standard locations discovered
- [ ] Dependency graph has nodes for all local packages
- [ ] Controller patterns detected where `Reconcile()` function exists
- [ ] Output artifacts written to `.agentic-extraction/`

## Example Usage

```yaml
Input:
  repository_path: /repos/openshift/machine-api-operator
  scope: full
  exclusions:
    - vendor/
    - hack/

Process:
  1. Discover: 234 Go files, 47 YAML files
  2. Parse Go: 5 packages, 87 types, 234 functions
  3. Extract CRDs: 3 CRDs (Machine, MachineSet, MachineDeployment)
  4. Build graph: 5 nodes, 12 edges, modularity 0.65
  5. Detect controllers: 3 controllers found

Output:
  .agentic-extraction/
    go-analysis.json        (87 KB)
    crds.json               (23 KB)
    dependency-graph.json   (8 KB)
    controllers.json        (12 KB)
    extraction-metadata.json (2 KB)
```

## Performance

- **Typical repository** (500 Go files): ~10-15 seconds
- **Large repository** (2000+ Go files): ~30-45 seconds
- **Memory usage**: ~100-200 MB for typical repos

## Integration with Next Steps

This skill's output feeds into:
1. **synthesize-documentation** - Uses extracted types, CRDs, controllers
2. **generate-knowledge-graph** - Uses dependency graph + component clusters
3. **link-documentation** - Uses package relationships for cross-linking
