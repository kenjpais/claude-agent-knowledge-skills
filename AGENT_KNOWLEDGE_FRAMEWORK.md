SYSTEM GOAL

Automatically generate and maintain agentic documentation for an existing OpenShift codebase such that coding agents can:

- Navigate the system in three hops or less
- Understand architectural intent, not just code structure
- Reuse patterns consistently
- Avoid violating invariants

The system continuously converts raw repository signals into structured knowledge artifacts.

---

HIGH-LEVEL ARCHITECTURE

The system consists of five layers:

1. Orchestration Layer
2. Extraction Agents (source-of-truth mining)
3. Synthesis Agents (structure + meaning)
4. Skill Layer (atomic capabilities)
5. Validation and Quality Enforcement Layer

All intelligence is expressed through composable skills. Agents only coordinate.

---

REPOSITORY EXTENSION

repository/
├── agents/
│   ├── orchestrator/
│   ├── extractor/
│   ├── synthesizer/
│   ├── linker/
│   ├── validator/
│   └── curator/
│
├── skills/
│   ├── repo/
│   ├── parsing/
│   ├── inference/
│   ├── synthesis/
│   ├── linking/
│   ├── validation/
│   └── documentation/
│
├── skill-registry/
│   └── index.yaml
│
├── agentic/
│   └── (generated documentation lives here)

---

CORE IDEA

The pipeline is:

Raw Code → Extract Signals → Infer Meaning → Synthesize Documents → Link Knowledge → Validate → Store in agentic/

This is not a one-shot generation. It is iterative and self-correcting.

---

AGENT ROLES

ORCHESTRATOR AGENT

Responsible for:

- Triggering documentation generation (full or incremental)
- Assigning scopes (repo-wide, component-level, PR-level)
- Sequencing agents

Uses:

- discovery skills
- planning skills

---

EXTRACTOR AGENT

Responsible for:

- Mining raw repository data

Outputs structured intermediate artifacts such as:

- API surfaces
- dependency graphs
- call graphs
- config schemas
- CRDs (critical for OpenShift)
- Github Pull requests
- Github Issues
- JIRA references

Uses parsing skills only. No interpretation.
The github pull requests and github issues contain references to JIRA issues which also need to be ingested and correlated with the github pull requests and github issues and stored in SQLite database locally.
Refer github_jira_storage_retrieval.md file 

---

SYNTHESIZER AGENT

Responsible for:

- Converting extracted data into human/agent-readable concepts

Produces:

- domain concepts
- component descriptions
- workflows

Uses:

- inference skills
- synthesis skills

---

LINKER AGENT

Responsible for:

- Enforcing progressive disclosure
- Connecting documents into a navigable graph

Creates:

- AGENTS.md
- cross-links between concepts, components, ADRs

Uses linking skills.

---

VALIDATOR AGENT

Responsible for:

- Enforcing framework constraints

Checks:

- navigation depth ≤ 3
- context budget
- broken links
- structural completeness

Uses validation skills.

---

CURATOR AGENT

Responsible for:

- Maintaining freshness over time
- Updating docs on code changes
- pruning stale knowledge

---

SKILL DESIGN (CRITICAL)

All skills follow strict guidelines:

- Single responsibility
- Clear input/output schema
- No hidden state
- Deterministic where possible
- Small context footprint

---

KEY SKILL CATEGORIES

REPO SKILLS

- read_file
- list_files
- search_code
- get_git_history
- diff_commits

These are the only way to access code.

---

PARSING SKILLS

Convert raw code into structured representations.

Examples:

- extract_go_structs
- extract_kubernetes_crds
- extract_api_endpoints
- extract_operator_reconcile_loops
- build_dependency_graph
- extract_config_flags

These are especially important for OpenShift operators and controllers.

---

INFERENCE SKILLS

Turn structure into meaning.

Examples:

- infer_component_boundary
- classify_service_role
- detect_design_patterns
- infer_data_flow
- identify_control_loops

These are probabilistic but must output confidence scores.

---

SYNTHESIS SKILLS

Generate documentation artifacts.

Examples:

- generate_component_doc
- generate_concept_doc
- generate_workflow_doc
- generate_glossary_terms
- generate_architecture_overview

All outputs must follow strict templates aligned with agentic/ structure.

---

LINKING SKILLS

Create navigability.

Examples:

- generate_agents_md
- link_concepts_to_components
- attach_code_references
- resolve_document_paths
- enforce_three_hop_rule

---

DOCUMENTATION SKILLS

Write and update files.

Examples:

- write_agentic_file
- update_existing_doc
- create_adr_from_history
- generate_core_beliefs_from_patterns

---

VALIDATION SKILLS

Examples:

- check_navigation_depth
- check_context_budget
- check_required_files
- check_adr_coverage
- detect_orphan_docs

---

SPECIALIZED OPENSHIFT SKILLS

Because OpenShift is Kubernetes-heavy, include:

- parse_kubernetes_controller_pattern
- extract_reconcile_logic
- map_crd_to_controller
- infer_operator_lifecycle
- detect_cluster_configuration_flows

These are essential for meaningful documentation.

---

PIPELINE FLOW

1. Orchestrator triggers documentation generation
2. Extractor Agent:
  - list_files
  - extract_go_structs
  - extract_crds
  - build_dependency_graph
3. Synthesizer Agent:
  - infer_component_boundary
  - generate_component_doc
  - generate_concept_doc
4. Linker Agent:
  - generate_agents_md
  - link_concepts_to_components
5. Documentation Skills:
  - write files into agentic/
6. Validator Agent:
  - check_navigation_depth
  - check_structure
  - update_quality_score
7. Curator Agent:
  - monitors changes and re-runs partial pipeline

---

EXECUTION PLAN GENERATION (META-LAYER)

Even documentation generation itself follows the framework.

Before generating docs, the system creates:

agentic/exec-plans/active/generate-docs.md

This includes:

- scope (which OpenShift component)
- extraction strategy
- synthesis approach
- validation criteria

This ensures traceability of documentation generation itself.

---

CONTEXT MANAGEMENT

Strict progressive disclosure:

- Start from directory structure
- Then component-level extraction
- Then concept synthesis
- Only load ADRs if inconsistencies detected

Skills must chunk outputs aggressively.

---

QUALITY ENFORCEMENT

Validator Agent continuously updates:

agentic/QUALITY_SCORE.md

Metrics include:

- percent of components documented
- ADR coverage inferred from git history
- navigation depth violations
- stale document detection

---

CONTINUOUS UPDATE MODEL

On every PR or commit:

1. diff_commits skill identifies impacted areas
2. Extractor runs only on changed components
3. Synthesizer updates affected docs
4. Linker revalidates graph
5. Validator updates quality score

---

ANTI-PATTERNS

- Generating full documentation in one pass
- Embedding interpretation inside parsing skills
- Skipping linking phase
- Producing narrative-heavy docs without structure
- Ignoring OpenShift-specific patterns like operators

