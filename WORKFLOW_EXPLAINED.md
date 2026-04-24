# Complete Agentic Documentation Workflow Explained

This document explains **exactly** how the agentic documentation generation works, from the moment you run `agentic /create <repo>` to the final output.

---

## Overview: What Happens When You Run `/create`

```bash
$ agentic /create https://github.com/openshift/installer
```

**High-level flow:**
```
User Command
    ↓
CLI parses and validates
    ↓
ClaudeOrchestrator loads 14 skills
    ↓
Claude API executes 5-phase workflow
    ↓
Output: docs + database + knowledge graph + metrics
```

**Duration**: ~2-3 minutes for typical OpenShift repository  
**API Calls**: ~8-12 Claude API calls  
**Tokens**: ~40,000-60,000 tokens  
**Storage**: ~5-50MB depending on repository size

---

## Phase-by-Phase Breakdown

### PHASE 1: DATA INGESTION (GitHub & JIRA)

**Goal**: Build a comprehensive database of repository activity (PRs, issues, JIRA tickets)

#### Step 1.1: Extract Repository Information

**What happens:**
```python
# From the repository URL/path
repo_url = "https://github.com/openshift/installer"
↓
owner = "openshift"
repo_name = "installer"
```

#### Step 1.2: GitHub Data Ingestion via GraphQL API

**Skill used**: `ingest-github-data`

**What gets fetched:**

1. **Pull Requests** (default: last 365 days)
   ```graphql
   query {
     repository(owner: "openshift", name: "installer") {
       pullRequests(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
         nodes {
           number
           title
           body
           state
           createdAt
           mergedAt
           author { login }
           labels { nodes { name } }
           files { nodes { path } }
           commits { nodes { commit { message } } }
           reviews { nodes { state, author { login } } }
         }
       }
     }
   }
   ```

2. **Issues** (default: last 365 days)
   ```graphql
   query {
     repository(owner: "openshift", name: "installer") {
       issues(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
         nodes {
           number
           title
           body
           state
           createdAt
           labels { nodes { name } }
           comments { nodes { body } }
         }
       }
     }
   }
   ```

**Example data fetched:**
```
PR #4521: "OCPCLOUD-789: Add ARM64 support for baremetal platform"
  Created: 2024-03-15
  State: merged
  Labels: ["platform/baremetal", "architecture"]
  Files changed: ["pkg/asset/machines/baremetal/...", ...]
  
Issue #4520: "Memory leak in pod inspector component"
  Created: 2024-03-14
  State: open
  Labels: ["bug", "priority/high"]
```

#### Step 1.3: JIRA Reference Extraction

**How it works:**

The system scans all PR titles, PR bodies, issue titles, issue bodies, and commit messages for JIRA patterns.

**Pattern**: `[A-Z]+-[0-9]+` (e.g., `OCPCLOUD-789`, `OCPBUGS-123`)

**Example extraction:**
```
PR Title: "OCPCLOUD-789: Add ARM64 support"
                    ↑
              Extracted: OCPCLOUD-789

PR Body: "This implements OCPCLOUD-789 and also fixes OCPBUGS-456"
                              ↑                            ↑
                    Extracted: OCPCLOUD-789, OCPBUGS-456

Commit Message: "feat: implement ARM64 scheduling (OCPCLOUD-789)"
                                                        ↑
                                              Extracted: OCPCLOUD-789
```

**Filters out false positives:**
- `PR-123` (not a JIRA project)
- `HTTP-404` (not a JIRA project)
- `CVE-2023-1234` (security CVE, not JIRA)

#### Step 1.4: JIRA Issue Ingestion

**For each extracted JIRA key:**

```python
# Fetch from public Red Hat JIRA
jira_url = "https://issues.redhat.com/rest/api/2/issue/OCPCLOUD-789"

Response:
{
  "key": "OCPCLOUD-789",
  "fields": {
    "summary": "Add ARM64 support for baremetal platform",
    "description": "Need to support ARM64 architecture...",
    "status": { "name": "Closed" },
    "issuetype": { "name": "Story" },
    "created": "2024-02-01T10:00:00Z",
    "updated": "2024-03-20T15:30:00Z",
    "priority": { "name": "High" },
    "labels": ["arm64", "baremetal", "multi-arch"],
    "components": [{ "name": "installer" }]
  }
}
```

#### Step 1.5: Create Correlations

**Link GitHub items to JIRA issues:**

```sql
-- github_jira_references table
INSERT INTO github_jira_references (
  github_pr_id,
  jira_issue_key,
  found_in,      -- "title", "body", "commit"
  context        -- Surrounding text
) VALUES (
  4521,
  'OCPCLOUD-789',
  'title',
  'OCPCLOUD-789: Add ARM64 support for baremetal platform'
);
```

#### Step 1.6: Store in SQLite Database

**Location**: `~/.agent-knowledge/data.db`

**Schema**:
```
github_repositories
  ├─ repository_id, owner, name, description, stars, language

github_pull_requests
  ├─ pr_id, repo_id, number, title, body, state, created_at, merged_at
  ├─ author, labels, files_changed, commits_count

github_issues
  ├─ issue_id, repo_id, number, title, body, state, created_at
  ├─ labels, comments_count

jira_issues
  ├─ jira_id, key, summary, description, status, type
  ├─ created_at, updated_at, priority, labels

github_jira_references (correlation)
  ├─ github_pr_id → jira_issue_key
  ├─ github_issue_id → jira_issue_key
  └─ found_in, context
```

**Example statistics after ingestion:**
```
✅ GitHub Data:
   PRs: 87
   Issues: 95
   Commits: 423
   
✅ JIRA Data:
   Issues: 12
   
✅ Correlations:
   PR → JIRA: 45
   Issue → JIRA: 18
```

---

### PHASE 2: CODE EXTRACTION

**Goal**: Parse the codebase to understand structure, components, APIs, and dependencies

#### Step 2.1: Discover Repository Structure

**Skill used**: `list-files`

```bash
# Recursively list all Go files
find /repo -name "*.go" -not -path "*/vendor/*" -not -path "*/test/*"

Result:
pkg/asset/installconfig/installconfig.go
pkg/asset/machines/machines.go
pkg/installer/installer.go
pkg/terraform/terraform.go
...
(~500-2000 files)
```

**Categorize files:**
- **Package structure**: `pkg/`, `cmd/`, `internal/`
- **Config**: `config/`, YAML/JSON files
- **CRDs**: `manifests/`, `*.yaml` with `apiVersion: apiextensions.k8s.io`
- **Documentation**: `docs/`, `*.md`

#### Step 2.2: Extract Go Structs and Interfaces

**Skill used**: `extract-go-structs`

**For each Go file, extract:**

1. **Type Definitions**:
```go
// File: pkg/asset/installconfig/installconfig.go

type InstallConfig struct {
    TypeMeta   `json:",inline"`
    ObjectMeta `json:"metadata"`
    SSHKey     string              `json:"sshKey"`
    BaseDomain string              `json:"baseDomain"`
    Platform   Platform            `json:"platform"`
}
```

**Extracted:**
```yaml
package: github.com/openshift/installer/pkg/asset/installconfig
types:
  - name: InstallConfig
    kind: struct
    fields:
      - name: SSHKey
        type: string
        json_tag: sshKey
      - name: BaseDomain
        type: string
        json_tag: baseDomain
      - name: Platform
        type: Platform
        json_tag: platform
```

2. **Interfaces** (API surfaces):
```go
type Asset interface {
    Dependencies() []Asset
    Generate(ctx context.Context, dependencies Assets) error
    Name() string
}
```

**Extracted:**
```yaml
interfaces:
  - name: Asset
    methods:
      - name: Dependencies
        returns: []Asset
      - name: Generate
        params: [ctx context.Context, dependencies Assets]
        returns: error
      - name: Name
        returns: string
```

3. **Methods** (component behavior):
```go
func (ic *InstallConfig) Generate(ctx context.Context, deps Assets) error {
    // Implementation
}
```

**Extracted:**
```yaml
methods:
  - receiver: InstallConfig
    name: Generate
    interface: Asset
```

#### Step 2.3: Extract Kubernetes CRDs

**Skill used**: `extract-kubernetes-crds`

**Scans for**: `manifests/**/*.yaml` with `kind: CustomResourceDefinition`

**Example CRD:**
```yaml
# manifests/installer.openshift.io_installconfigs.yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: installconfigs.installer.openshift.io
spec:
  group: installer.openshift.io
  names:
    kind: InstallConfig
    plural: installconfigs
  versions:
    - name: v1
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                baseDomain:
                  type: string
                platform:
                  type: object
```

**Extracted:**
```yaml
crds:
  - name: InstallConfig
    group: installer.openshift.io
    version: v1
    schema:
      spec:
        baseDomain: string
        platform: object
```

#### Step 2.4: Build Dependency Graph

**Skill used**: `build-dependency-graph`

**Analyzes import statements:**

```go
// File: pkg/installer/installer.go
package installer

import (
    "github.com/openshift/installer/pkg/asset/installconfig"
    "github.com/openshift/installer/pkg/asset/machines"
    "github.com/openshift/installer/pkg/terraform"
)
```

**Builds graph:**
```
installer
  ├─ depends_on → installconfig
  ├─ depends_on → machines
  └─ depends_on → terraform
      └─ depends_on → aws-sdk
```

**Graph metrics:**
```yaml
total_packages: 45
total_dependencies: 178
external_dependencies: 23
internal_dependencies: 155
max_depth: 7
avg_dependencies_per_package: 3.9
```

#### Step 2.5: Parse Controller Patterns (OpenShift-specific)

**Skill used**: `parse-kubernetes-controller-pattern`

**Looks for reconciliation patterns:**

```go
// Detect reconcile function
func (r *Reconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    // 1. Fetch resource
    var obj v1.InstallConfig
    if err := r.Get(ctx, req.NamespacedName, &obj); err != nil {
        return ctrl.Result{}, err
    }
    
    // 2. Compare spec vs status
    if obj.Spec.Replicas != obj.Status.CurrentReplicas {
        // 3. Take action
        if err := r.reconcile(ctx, &obj); err != nil {
            return ctrl.Result{}, err
        }
    }
    
    // 4. Update status
    obj.Status.CurrentReplicas = obj.Spec.Replicas
    return ctrl.Result{}, r.Status().Update(ctx, &obj)
}
```

**Extracted pattern:**
```yaml
controller:
  name: InstallConfigReconciler
  reconciles: InstallConfig
  pattern: reconcile-loop
  steps:
    - Fetch resource
    - Compare spec vs status
    - Take corrective action
    - Update status
  watches:
    - InstallConfig
    - Machine
  predicates:
    - GenerationChanged
```

**Phase 2 Output Summary:**
```
✅ Extracted Data:
   Go packages: 45
   Go structs: 127
   Go interfaces: 23
   Kubernetes CRDs: 8
   Dependency edges: 178
   Controllers: 5
```

---

### PHASE 3: DOCUMENTATION SYNTHESIS

**Goal**: Convert raw extracted data into human and agent-readable documentation

#### Step 3.1: Infer Component Boundaries

**Skill used**: `infer-component-boundary`

**Analyzes:**
- Dependency graph clusters
- Package naming conventions
- Shared responsibilities

**Algorithm:**
```
1. Group packages by import patterns
2. Identify high-cohesion clusters
3. Name clusters based on primary package
4. Assign confidence scores
```

**Example inference:**
```yaml
components:
  - name: installer
    packages:
      - pkg/installer
      - pkg/destroy
    files:
      - pkg/installer/installer.go
      - pkg/destroy/bootstrap.go
    confidence: 0.95
    reasoning: "Tightly coupled, shared Install/Destroy lifecycle"
    
  - name: asset-generator
    packages:
      - pkg/asset/installconfig
      - pkg/asset/machines
      - pkg/asset/manifests
    files: [...]
    confidence: 0.92
    reasoning: "All implement Asset interface, generate cluster resources"
```

#### Step 3.2: Classify Service Roles

**Skill used**: `classify-service-role`

**For each component, determine role:**

```yaml
installer:
  role: orchestrator
  confidence: 0.95
  signals:
    - "Coordinates other components"
    - "Main entry point (cmd/installer)"
    - "High fan-out in dependency graph"
    
asset-generator:
  role: generator
  confidence: 0.90
  signals:
    - "Implements Generator pattern"
    - "Produces artifacts (manifests, configs)"
    - "No external API exposure"
    
terraform-provider:
  role: infrastructure-provisioner
  confidence: 0.93
  signals:
    - "Uses Terraform SDK"
    - "Manages cloud resources"
    - "Interacts with AWS/Azure/GCP APIs"
```

**Possible roles** (OpenShift-specific):
- `orchestrator` - Coordinates workflow
- `controller` - Reconciles Kubernetes resources
- `operator` - Manages cluster state
- `api-server` - Exposes HTTP API
- `webhook` - Validates/mutates requests
- `generator` - Produces artifacts
- `cli` - Command-line tool
- `library` - Shared code
- `infrastructure-provisioner` - Manages cloud resources

#### Step 3.3: Generate Component Documentation

**Skill used**: `generate-component-doc`

**For each component, create** `agentic/design-docs/components/<component>.md`:

**Template:**
```markdown
# {Component Name}

**Role**: {role}  
**Confidence**: {confidence}

## Purpose

{1-2 sentence purpose}

## Key Responsibilities

1. {Responsibility 1}
2. {Responsibility 2}
3. {Responsibility 3}

## API Surface

### Public Interfaces
- `{Interface1}` - {description}
- `{Interface2}` - {description}

### Key Types
- `{Type1}` - {description}
- `{Type2}` - {description}

## Dependencies

**Direct Dependencies:**
- [{Component1}](./component1.md) - {why needed}
- [{Component2}](./component2.md) - {why needed}

**Dependency Graph:**
```
{component}
  ├─ {dep1}
  └─ {dep2}
      └─ {dep3}
```

## Related Concepts

- [{Concept1}](../../domain/concepts/concept1.md)
- [{Concept2}](../../domain/concepts/concept2.md)

## Key Files

- `{file1}` - {purpose}
- `{file2}` - {purpose}

## Usage Example

```go
{minimal code example}
```

## Related PRs/Issues

{If available from GitHub/JIRA data:}
- PR #4521: Add ARM64 support (OCPCLOUD-789)
- Issue #4520: Memory leak fix
```

**Constraint**: ≤100 lines per component doc

**Example** `agentic/design-docs/components/installer.md`:
```markdown
# Installer

**Role**: orchestrator  
**Confidence**: 95%

## Purpose

Orchestrates the complete OpenShift cluster installation process from configuration validation through infrastructure provisioning to cluster bootstrap.

## Key Responsibilities

1. Validate installation configuration
2. Generate cluster assets (manifests, configs)
3. Provision infrastructure via Terraform
4. Bootstrap control plane
5. Monitor cluster initialization to ready state

## API Surface

### Public Interfaces
- `Installer` - Main installation orchestrator

### Key Types
- `Config` - Installation configuration
- `State` - Installation state tracking

## Dependencies

**Direct Dependencies:**
- [Asset Generator](./asset-generator.md) - Generates cluster manifests
- [Terraform Provider](./terraform-provider.md) - Provisions infrastructure
- [Validator](./validator.md) - Validates configuration

**Dependency Graph:**
```
installer
  ├─ asset-generator
  ├─ terraform-provider
  │   └─ aws-sdk
  └─ validator
```

## Related Concepts

- [Installation Workflow](../../domain/concepts/installation-workflow.md)
- [Asset Generation](../../domain/concepts/asset-generation.md)

## Key Files

- `pkg/installer/installer.go` - Main orchestrator
- `pkg/destroy/bootstrap.go` - Cleanup logic

## Related PRs/Issues

- PR #4521: Add ARM64 support (OCPCLOUD-789)
- PR #4501: Fix timeout handling (OCPBUGS-234)
```

#### Step 3.4: Generate Concept Documentation

**Skill used**: `generate-component-doc` (also handles concepts)

**Identifies domain concepts from:**
- Code patterns (reconciliation loops, asset generation)
- Naming conventions (installer, provisioner, validator)
- Kubernetes-specific patterns (CRDs, operators, controllers)

**Example** `agentic/domain/concepts/reconciliation-pattern.md`:
```markdown
# Reconciliation Pattern

## Definition

A control loop pattern where a controller continuously compares desired state (spec) with actual state (status) and takes corrective action.

## Why It Matters

- Core pattern in Kubernetes operators
- Enables self-healing
- Declarative infrastructure management
- Used throughout OpenShift

## When to Use

- Managing Kubernetes resources
- Implementing operators
- Maintaining desired state over time
- Self-healing systems

## How It Works

1. Watch for resource changes
2. Fetch current spec (desired state)
3. Fetch current status (actual state)
4. Calculate diff
5. Apply changes to reconcile
6. Update status
7. Requeue if needed

## Implementation

```go
func (r *Reconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    // 1. Fetch resource
    var resource v1.MyResource
    if err := r.Get(ctx, req.NamespacedName, &resource); err != nil {
        return ctrl.Result{}, err
    }
    
    // 2. Compare spec vs status
    if !reflect.DeepEqual(resource.Spec, resource.Status) {
        // 3. Reconcile
        if err := r.reconcile(ctx, &resource); err != nil {
            return ctrl.Result{Requeue: true}, err
        }
    }
    
    // 4. Update status
    return ctrl.Result{}, r.Status().Update(ctx, &resource)
}
```

## Used By Components

- [Machine Controller](../components/machine-controller.md)
- [Cluster Operator](../components/cluster-operator.md)

## Related Concepts

- [Controller Pattern](./controller-pattern.md)
- [Operator Pattern](./operator-pattern.md)
```

**Constraint**: ≤75 lines per concept doc

#### Step 3.5: Generate Required Files

**Creates these standard files:**

1. **`agentic/DESIGN.md`** - Design philosophy and core beliefs
2. **`agentic/DEVELOPMENT.md`** - Development setup, build, test
3. **`agentic/TESTING.md`** - Test strategy and running tests
4. **`agentic/RELIABILITY.md`** - SLOs, observability, monitoring
5. **`agentic/SECURITY.md`** - Security model and considerations

**Populated from:**
- README.md (if exists)
- CONTRIBUTING.md (if exists)
- Makefile/package.json (for build commands)
- Test directories (for test commands)

#### Step 3.6: Create Cross-Links

**Skill used**: `link-concepts-to-components`

**Algorithm:**
```
For each concept:
  For each component:
    If concept_name in component_description OR
       concept_pattern in component_code:
      Create bidirectional link
      Add to concept: "Used by [Component](link)"
      Add to component: "Implements [Concept](link)"
```

**Example links:**
```
Reconciliation Pattern ←→ Machine Controller
Installation Workflow ←→ Installer
Asset Generation ←→ Asset Generator
```

#### Step 3.7: Generate AGENTS.md Entry Point

**Skill used**: `generate-agents-md`

**Creates**: `AGENTS.md` (≤150 lines)

**Structure:**
```markdown
# OpenShift Installer - Agent Documentation

> This documentation is designed for AI coding agents to navigate the codebase efficiently.

## Quick Start

**Purpose**: {1-2 sentence repository purpose}

**Key Commands**:
```bash
make build    # Build installer binary
make test     # Run test suite
make lint     # Run linters
```

## Components

This repository contains {N} main components:

### 1. [{Component 1}](agentic/design-docs/components/component1.md)
**Role**: {role}  
{1-line description}

### 2. [{Component 2}](agentic/design-docs/components/component2.md)
**Role**: {role}  
{1-line description}

...

## Domain Concepts

Key patterns and concepts:

- [{Concept 1}](agentic/domain/concepts/concept1.md) - {1-line description}
- [{Concept 2}](agentic/domain/concepts/concept2.md) - {1-line description}

## Architecture

See [Design Philosophy](agentic/DESIGN.md) for high-level architecture.

**Component Dependencies:**
```
{Component1}
  ├─ {Component2}
  └─ {Component3}
      └─ {External}
```

## Development

- [Development Setup](agentic/DEVELOPMENT.md)
- [Testing Guide](agentic/TESTING.md)
- [Reliability](agentic/RELIABILITY.md)
- [Security](agentic/SECURITY.md)

## Invariants

{Key system invariants extracted from code comments}

## Navigation

All documentation is reachable within 3 hops from this file.

**Quality Score**: {score}/100

---
*Generated by Agent Knowledge System*
```

**Phase 3 Output:**
```
✅ Generated Documentation:
   AGENTS.md (142 lines)
   Components: 5 docs (avg 87 lines)
   Concepts: 3 docs (avg 62 lines)
   Required files: 5 docs
   Cross-links: 23 bidirectional links
```

---

### PHASE 4: KNOWLEDGE GRAPH GENERATION

**Goal**: Convert documentation + database into queryable knowledge graph

#### Step 4.1: Load Source Data

**Skill used**: `generate-knowledge-graph`

**Inputs:**
1. SQLite database: `~/.agent-knowledge/data.db`
2. Agentic docs: `repo/agentic/`

#### Step 4.2: Create Nodes

**Node types:**

1. **Component Nodes** (from agentic docs):
```yaml
node_id: comp_installer
node_type: component
properties:
  name: installer
  role: orchestrator
  api_surface: [Installer, Config, State]
  dependencies: [asset-generator, terraform-provider, validator]
  file_paths: [pkg/installer/installer.go, pkg/destroy/bootstrap.go]
  doc_path: agentic/design-docs/components/installer.md
```

2. **Concept Nodes** (from agentic docs):
```yaml
node_id: concept_reconciliation
node_type: concept
properties:
  name: reconciliation-pattern
  description: "Control loop pattern..."
  related_concepts: [controller-pattern, operator-pattern]
  doc_path: agentic/domain/concepts/reconciliation-pattern.md
```

3. **PR Nodes** (from database):
```yaml
node_id: pr_4521
node_type: pr
properties:
  number: 4521
  title: "Add ARM64 support for baremetal platform"
  state: merged
  created_at: "2024-03-15"
  merged_at: "2024-03-20"
  author: developer123
  labels: [platform/baremetal, architecture]
  files_changed: [pkg/asset/machines/baremetal/...]
```

4. **Issue Nodes** (from database):
```yaml
node_id: issue_4520
node_type: issue
properties:
  number: 4520
  title: "Memory leak in pod inspector"
  state: open
  created_at: "2024-03-14"
  labels: [bug, priority/high]
```

5. **JIRA Nodes** (from database):
```yaml
node_id: jira_OCPCLOUD-789
node_type: jira
properties:
  key: OCPCLOUD-789
  summary: "Add ARM64 support for baremetal platform"
  status: Closed
  type: Story
  created_at: "2024-02-01"
  priority: High
  labels: [arm64, baremetal, multi-arch]
```

#### Step 4.3: Create Relationships

**Relationship types:**

1. **depends_on** (component → component):
```yaml
from: comp_installer
relationship: depends_on
to: comp_asset_generator
properties:
  reason: "Uses asset generation for manifests"
```

2. **implements** (component → concept):
```yaml
from: comp_machine_controller
relationship: implements
to: concept_reconciliation
properties:
  pattern: reconcile-loop
```

3. **references** (PR/issue → component):
```yaml
from: pr_4521
relationship: references
to: comp_asset_generator
properties:
  files_changed: [pkg/asset/machines/baremetal/machines.go]
  lines_added: 234
  lines_deleted: 45
```

4. **links_to** (concept → component, component → concept):
```yaml
from: concept_reconciliation
relationship: links_to
to: comp_machine_controller
properties:
  link_type: bidirectional
```

5. **correlates_with** (GitHub issue ↔ JIRA):
```yaml
from: pr_4521
relationship: correlates_with
to: jira_OCPCLOUD-789
properties:
  found_in: title
  context: "OCPCLOUD-789: Add ARM64 support..."
```

#### Step 4.4: Export to GraphML

**Format**: GraphML (XML-based graph format)

**Location**: `~/.agent-knowledge/graphs/installer-graph.graphml`

**Example GraphML:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph id="installer" edgedefault="directed">
    <!-- Nodes -->
    <node id="comp_installer">
      <data key="type">component</data>
      <data key="name">installer</data>
      <data key="role">orchestrator</data>
    </node>
    
    <node id="comp_asset_generator">
      <data key="type">component</data>
      <data key="name">asset-generator</data>
      <data key="role">generator</data>
    </node>
    
    <node id="pr_4521">
      <data key="type">pr</data>
      <data key="number">4521</data>
      <data key="title">Add ARM64 support</data>
    </node>
    
    <!-- Edges -->
    <edge source="comp_installer" target="comp_asset_generator">
      <data key="type">depends_on</data>
      <data key="reason">Uses for manifest generation</data>
    </edge>
    
    <edge source="pr_4521" target="comp_asset_generator">
      <data key="type">references</data>
      <data key="files_changed">pkg/asset/machines/...</data>
    </edge>
  </graph>
</graphml>
```

**Graph Statistics:**
```
✅ Knowledge Graph:
   Total nodes: 247
   Total edges: 412
   
   Node breakdown:
     Components: 45
     Concepts: 12
     PRs: 87
     Issues: 95
     JIRA: 8
   
   Edge breakdown:
     depends_on: 78
     implements: 45
     references: 182
     links_to: 89
     correlates_with: 18
   
   Graph file: ~/.agent-knowledge/graphs/installer-graph.graphml
   Size: 2.4 MB
```

---

### PHASE 5: VALIDATION

**Goal**: Ensure generated documentation meets all quality constraints

#### Step 5.1: Navigation Depth Check

**Skill used**: `check-navigation-depth`

**Algorithm:**
```
Start from AGENTS.md (hop 0)
For each link in AGENTS.md:
  Follow link (hop 1)
  For each link in that document:
    Follow link (hop 2)
    For each link in that document:
      Follow link (hop 3)
      For each link in that document:
        VIOLATION! (hop 4)
```

**Example traversal:**
```
AGENTS.md (hop 0)
  → agentic/design-docs/components/installer.md (hop 1)
      → agentic/domain/concepts/reconciliation-pattern.md (hop 2)
          → agentic/design-docs/components/machine-controller.md (hop 3)
              ✅ No further links OR
              ❌ → another-doc.md (hop 4 - VIOLATION!)
```

**Output:**
```yaml
check: navigation_depth
passed: true
metrics:
  max_depth: 3
  documents_at_hop_0: 1    # AGENTS.md
  documents_at_hop_1: 10   # Components, DESIGN, DEVELOPMENT, etc.
  documents_at_hop_2: 15   # Concepts, detailed component docs
  documents_at_hop_3: 5    # Deep technical details
  documents_unreachable: 0
violations: []
```

#### Step 5.2: Line Budget Check

**Validates:**
- AGENTS.md ≤150 lines
- Component docs ≤100 lines each
- Concept docs ≤75 lines each

**Example:**
```yaml
check: line_budgets
passed: true
files:
  - path: AGENTS.md
    lines: 142
    budget: 150
    passed: true
    
  - path: agentic/design-docs/components/installer.md
    lines: 87
    budget: 100
    passed: true
    
  - path: agentic/domain/concepts/reconciliation-pattern.md
    lines: 62
    budget: 75
    passed: true
```

#### Step 5.3: Quality Score Calculation

**Skill used**: `check-quality-score`

**Scoring breakdown:**

1. **Coverage** (40 points):
```
Components documented: 45 / 45 = 100%
Score: 40 * 1.0 = 40 points
```

2. **Freshness** (20 points):
```
Last updated: 2024-03-20 (today)
Days since update: 0
Score: 20 * 1.0 = 20 points
```

3. **Completeness** (20 points):
```
Required files present:
✅ AGENTS.md
✅ DESIGN.md
✅ DEVELOPMENT.md
✅ TESTING.md
✅ RELIABILITY.md
✅ SECURITY.md
✅ QUALITY_SCORE.md

Score: 7/7 = 20 points
```

4. **Linkage** (10 points):
```
Total links: 89
Broken links: 0
Score: 10 * 1.0 = 10 points
```

5. **Navigation** (10 points):
```
Max depth: 3 hops
Unreachable docs: 0
Score: 10 points
```

**Total Score**: 40 + 20 + 20 + 10 + 10 = **90/100** ✅

#### Step 5.4: Generate Quality Report

**Creates**: `agentic/QUALITY_SCORE.md`

```markdown
# Documentation Quality Score

**Overall Score**: 90/100 ✅

**Last Updated**: 2024-03-20

## Scoring Breakdown

### Coverage (40/40 points) ✅
- Components documented: 45/45 (100%)
- All major components have documentation

### Freshness (20/20 points) ✅
- Last updated: 0 days ago
- All documentation current

### Completeness (20/20 points) ✅
- Required files: 7/7 present
- All mandatory documentation exists

### Linkage (10/10 points) ✅
- Total links: 89
- Broken links: 0
- All cross-references valid

### Navigation (10/10 points) ✅
- Maximum navigation depth: 3 hops
- Unreachable documents: 0
- All content accessible from AGENTS.md

## Metrics

| Metric | Value |
|--------|-------|
| Total documents | 63 |
| Component docs | 45 |
| Concept docs | 12 |
| Average doc length | 78 lines |
| Total cross-links | 89 |
| Graph nodes | 247 |
| Graph edges | 412 |

## Recommendations

None - documentation meets all quality thresholds.

---
*Generated by Agent Knowledge System*
```

**Phase 5 Output:**
```
✅ Validation Complete:
   Navigation depth: PASS (3 hops max)
   Line budgets: PASS (all within limits)
   Quality score: 90/100 PASS (threshold: 70)
   Broken links: 0
   
   Issues found: 0
   Recommendations: 0
```

---

## Final Output

### Files Created

```
repository/
├── AGENTS.md                           (142 lines)
└── agentic/
    ├── DESIGN.md                       (95 lines)
    ├── DEVELOPMENT.md                  (78 lines)
    ├── TESTING.md                      (56 lines)
    ├── RELIABILITY.md                  (67 lines)
    ├── SECURITY.md                     (72 lines)
    ├── QUALITY_SCORE.md                (45 lines)
    ├── design-docs/
    │   └── components/
    │       ├── installer.md            (87 lines)
    │       ├── asset-generator.md      (93 lines)
    │       ├── terraform-provider.md   (82 lines)
    │       ├── validator.md            (76 lines)
    │       └── bootstrap.md            (81 lines)
    └── domain/
        └── concepts/
            ├── reconciliation-pattern.md  (62 lines)
            ├── installation-workflow.md   (68 lines)
            └── asset-generation.md        (59 lines)
```

### Database Created

```
~/.agent-knowledge/
└── data.db                             (15.3 MB)
    Tables:
    ├─ github_repositories (1 row)
    ├─ github_pull_requests (87 rows)
    ├─ github_issues (95 rows)
    ├─ jira_issues (12 rows)
    └─ github_jira_references (63 rows)
```

### Knowledge Graph Created

```
~/.agent-knowledge/
└── graphs/
    └── installer-graph.graphml         (2.4 MB)
        Nodes: 247
        Edges: 412
```

### Metrics Reported

```
✅ Workflow Complete
========================================

📊 Metrics:
   Duration: 127.3s
   API calls: 9
   Tokens: 48,234 in, 13,567 out
   Skills loaded: 14

📂 Output:
   /repo/AGENTS.md
   /repo/agentic/ (63 files)
   ~/.agent-knowledge/data.db
   ~/.agent-knowledge/graphs/installer-graph.graphml

📈 Quality:
   Overall score: 90/100 ✅
   Navigation depth: 3 hops ✅
   Coverage: 100% ✅
   Broken links: 0 ✅

💡 Next steps:
   agentic /validate /repo
   agentic /evaluate /repo
   agentic /ask what components exist?
```

---

## How Retrieval Works (Querying the Documentation)

When you run `agentic /ask "how does the installer work?"`:

### Step 1: Parse Query
```
Query: "how does the installer work?"
  ↓
Query type: component-details
Component: installer
```

### Step 2: Load Knowledge Graph
```
Load: ~/.agent-knowledge/graphs/installer-graph.graphml
  ↓
Nodes loaded: 247
Edges loaded: 412
```

### Step 3: Graph Traversal with Progressive Disclosure

**Hop 0** - Starting point:
```
node: comp_installer
properties:
  name: installer
  role: orchestrator
  doc_path: agentic/design-docs/components/installer.md
```

**Hop 1** - Immediate neighbors:
```
comp_installer
  ├─ depends_on → comp_asset_generator
  ├─ depends_on → comp_terraform_provider
  ├─ depends_on → comp_validator
  ├─ implements → concept_installation_workflow
  └─ referenced_by → pr_4501, pr_4521
```

**Hop 2** - Second-degree connections:
```
comp_asset_generator
  ├─ depends_on → comp_kubernetes_client
  └─ implements → concept_asset_generation
  
concept_installation_workflow
  ├─ implemented_by → comp_installer
  └─ related_to → concept_reconciliation
```

### Step 4: Relevance Scoring

Each node scored 0.0-1.0:
```
comp_installer: 1.0        (direct match, hop 0)
comp_asset_generator: 0.85 (dependency, hop 1)
comp_validator: 0.82       (dependency, hop 1)
concept_installation_workflow: 0.90 (concept, hop 1)
pr_4521: 0.65              (recent PR, hop 1)
```

### Step 5: Context Assembly (within 500 line budget)

```
1. Read comp_installer doc (87 lines)
2. Read concept_installation_workflow (68 lines)
3. Read comp_asset_generator summary (15 lines from doc)
4. Read comp_terraform_provider summary (12 lines from doc)
Total: 182 lines (within 500 budget)
```

### Step 6: Format Response

```markdown
## How the Installer Works

**Purpose**: Orchestrates the complete OpenShift cluster installation process.

**Key Responsibilities**:
1. Validate installation configuration
2. Generate cluster assets via Asset Generator
3. Provision infrastructure via Terraform Provider
4. Bootstrap control plane
5. Monitor cluster to ready state

**Dependencies**:
- [Asset Generator](./asset-generator.md) - Generates manifests
- [Terraform Provider](./terraform-provider.md) - Provisions infrastructure
- [Validator](./validator.md) - Validates config

**Workflow**: See [Installation Workflow](../concepts/installation-workflow.md)

**Recent Changes**:
- PR #4521: Added ARM64 support (OCPCLOUD-789)
- PR #4501: Fixed timeout handling (OCPBUGS-234)

**Navigation path**: AGENTS.md → Components → Installer (2 hops)
**Context retrieved**: 182 lines
**Query time**: 0.08s
```

---

## Summary: The Complete Flow

```
User: agentic /create https://github.com/openshift/installer

1. INGESTION (30s)
   ├─ Clone repo
   ├─ Fetch 87 PRs (GraphQL)
   ├─ Fetch 95 issues (GraphQL)
   ├─ Extract 63 JIRA references
   ├─ Fetch 12 JIRA issues
   └─ Store in SQLite (15.3 MB)

2. EXTRACTION (45s)
   ├─ Scan 1,234 Go files
   ├─ Extract 127 structs, 23 interfaces
   ├─ Parse 8 Kubernetes CRDs
   ├─ Build dependency graph (178 edges)
   └─ Identify 5 controllers

3. SYNTHESIS (35s)
   ├─ Infer 5 component boundaries
   ├─ Classify component roles
   ├─ Generate 5 component docs (avg 87 lines)
   ├─ Generate 3 concept docs (avg 62 lines)
   ├─ Generate AGENTS.md (142 lines)
   ├─ Create 23 cross-links
   └─ Generate 5 required files

4. KNOWLEDGE GRAPH (12s)
   ├─ Create 247 nodes (components, concepts, PRs, issues, JIRA)
   ├─ Create 412 edges (depends_on, implements, references, links_to)
   └─ Export to GraphML (2.4 MB)

5. VALIDATION (5s)
   ├─ Check navigation depth: PASS (3 hops)
   ├─ Check line budgets: PASS
   ├─ Calculate quality score: 90/100 PASS
   ├─ Check broken links: 0 PASS
   └─ Generate QUALITY_SCORE.md

Total: 127 seconds
Output: 63 files + database + knowledge graph
Result: ✅ Ready for agent navigation
```

---

**Key Innovation**: The entire workflow is **skill-driven** - no imperative code. Claude API loads skills and executes them according to their definitions. This makes the system extensible, auditable, and aligned with the Agent Knowledge Framework.
