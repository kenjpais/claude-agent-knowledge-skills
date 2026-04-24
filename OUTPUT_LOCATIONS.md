# Generated Output Locations

## Previous Runs (Outside This Repository)

Your previous agentic documentation runs were scattered in different locations:

### 1. Agent Knowledge System Gemini

**Location**: `/Users/kpais/kpais-workspace/agent-knowledge-system-gemini/`

**Generated Documentation:**
- `docs_mtao/AGENTS.md` - Multiarch Tuning Operator documentation
- `docs_demo_mtao/AGENTS.md` - Demo version
- `docs_eval_mtao/AGENTS.md` - Evaluation version
- `docs_test/AGENTS.md` - Test version
- `docs_multi_repo/AGENTS.md` - Multi-repo version

**Issue**: These were generated with a different system (Gemini-based) and are minimal documentation (not full agentic docs with component/concept structure).

### 2. Other Scattered Locations

**Locations Found:**
- `/Users/kpais/kpais-workspace/agentic-docs-generator/output/`
  - `external-secrets-operator/agentic/`
  - `cert-manager-operator/agentic/`
  - `zero-trust-workload-identity-manager/agentic/`

- `/Users/kpais/kpais-workspace/claude-tmp/`
  - `agentic-akm/AGENTS.md`
  - `agentic-docs-wo-kg/output/` (various repos)

- `/Users/kpais/kpais-workspace/agent-knowledge-system-cgpt/docs_output/agentic/`

**Problem**: 
- ❌ Outputs scattered across multiple directories
- ❌ No consistent naming or structure
- ❌ Hard to find and track
- ❌ Not part of this repository

### 3. The Broken Links Issue

You mentioned: "The latest graph generated in `/tmp/agentic-repos/multiarch-tuning-operator/agentic/graphify-out/` contains broken links."

**Finding**: This directory doesn't exist. It may have been:
- Deleted automatically (temporary directory cleanup)
- Generated in a different session
- Never actually created at that path

**Root Cause**: The graphify tool (external) generates HTML with relative links that break when:
- Files are moved
- Documentation structure changes
- Temporary directories are cleaned up

## NEW: Centralized Output Directory (This Repository)

Going forward, **all generated outputs will be in this repository** under the `output/` directory.

### Directory Structure

```
claude-agent-knowledge-system-skills/
└── output/
    ├── README.md              # Output documentation
    ├── agentic/               # Generated documentation
    │   ├── .gitkeep
    │   └── {repo-name}/
    │       ├── AGENTS.md
    │       └── agentic/
    │           ├── design-docs/components/
    │           ├── domain/concepts/
    │           └── QUALITY_SCORE.md
    ├── graphs/                # Knowledge graphs
    │   ├── .gitkeep
    │   └── {repo-name}/
    │       ├── graph.json              # NetworkX format
    │       └── graphify-out/           # Graphify HTML (optional)
    │           ├── index.html
    │           └── GRAPH_REPORT.md
    └── databases/             # SQLite databases
        ├── .gitkeep
        └── {repo-name}.db              # GitHub/JIRA data
```

### How to Use

#### 1. Generate Documentation

```bash
# In Claude Code, navigate to target repository
cd /path/to/target-repository

# Run the skill
/create

# Output will be generated in:
# claude-agent-knowledge-system-skills/output/agentic/{repo-name}/
```

#### 2. View Generated Documentation

```bash
# Navigate to this repository
cd /Users/kpais/kpais-workspace/claude-agent-knowledge-system-skills

# View entry point
cat output/agentic/{repo-name}/AGENTS.md

# View components
ls output/agentic/{repo-name}/agentic/design-docs/components/

# View quality score
cat output/agentic/{repo-name}/agentic/QUALITY_SCORE.md
```

#### 3. View Knowledge Graph

```bash
# NetworkX JSON format (recommended - no broken links)
cat output/graphs/{repo-name}/graph.json

# Graphify HTML (optional - may have broken links)
open output/graphs/{repo-name}/graphify-out/index.html
```

#### 4. Query Database

```bash
# View GitHub/JIRA data
sqlite3 output/databases/{repo-name}.db "
SELECT COUNT(*) as prs FROM github_pull_requests;
SELECT COUNT(*) as issues FROM github_issues;
SELECT COUNT(*) as jira FROM jira_issues;
"
```

## Migration Guide

### Moving Existing Documentation

If you want to consolidate existing documentation into this repository:

```bash
cd /Users/kpais/kpais-workspace/claude-agent-knowledge-system-skills

# Copy from old locations
cp -r /Users/kpais/kpais-workspace/agentic-docs-generator/output/external-secrets-operator/agentic \
      output/agentic/external-secrets-operator/

cp -r /Users/kpais/kpais-workspace/agentic-docs-generator/output/cert-manager-operator/agentic \
      output/agentic/cert-manager-operator/

# etc...
```

### Regenerating Documentation

**Recommended**: Regenerate all documentation using the updated skills:

```bash
# 1. In Claude Code, navigate to each repository
cd /path/to/openshift/multiarch-tuning-operator

# 2. Run /create
/create

# 3. Output will be in:
# claude-agent-knowledge-system-skills/output/agentic/multiarch-tuning-operator/

# 4. Repeat for other repositories
```

## Benefits of New Approach

### ✅ Centralized
- All outputs in one place
- Easy to find and track
- Consistent structure

### ✅ Version Controlled
- Output structure is in git (directories + README)
- Generated content is git-ignored (keeps repo clean)
- Can selectively commit specific outputs with `git add -f`

### ✅ Organized
- By repository name
- Clear separation: agentic docs / graphs / databases
- README documentation for each section

### ✅ No Broken Links
- Internal NetworkX graphs don't have HTML link issues
- Graphify is optional and clearly marked
- All paths are relative to output directory

## Recommendations

### 1. Use the Internal Knowledge Graph

**Instead of**: Graphify HTML (breaks easily)
**Use**: NetworkX JSON (`output/graphs/{repo}/graph.json`)

**Advantages**:
- No broken links
- Programmatically queryable
- Reliable and version-controllable
- Works with `/ask` skill

### 2. Keep Graphify for Visualization Only

If you want pretty HTML visualizations:
- Use graphify for exploration
- Don't rely on it for programmatic access
- Store output in `output/graphs/{repo}/graphify-out/`
- Consider it ephemeral (can regenerate)

### 3. Commit Important Documentation

```bash
# Commit specific documentation you want to share
git add -f output/agentic/multiarch-tuning-operator/AGENTS.md
git add -f output/agentic/multiarch-tuning-operator/agentic/

# Or keep it local (default - already in .gitignore)
```

## Next Steps

### 1. Test the New Output Structure

```bash
# Create output directories
make output

# Verify structure
ls -la output/
```

### 2. Regenerate Documentation for Multiarch Tuning Operator

```bash
# In Claude Code
cd /path/to/multiarch-tuning-operator
/create

# Check output
cat /Users/kpais/kpais-workspace/claude-agent-knowledge-system-skills/output/agentic/multiarch-tuning-operator/AGENTS.md
```

### 3. Clean Up Old Locations (Optional)

Once you've verified the new outputs work:

```bash
# Archive or delete old scattered outputs
rm -rf /Users/kpais/kpais-workspace/agentic-docs-generator/output/
rm -rf /Users/kpais/kpais-workspace/claude-tmp/agentic-*
# etc...
```

## Summary

**Before**: 
- ❌ Outputs scattered across 5+ locations
- ❌ `/tmp/` directories that get cleaned up
- ❌ Broken graphify HTML links
- ❌ Hard to find documentation

**After**:
- ✅ All outputs in `claude-agent-knowledge-system-skills/output/`
- ✅ Organized by type: agentic / graphs / databases
- ✅ Organized by repository name
- ✅ NetworkX JSON graphs (no broken links)
- ✅ Easy to find, track, and share

**Date**: 2026-04-24  
**Created by**: Claude Sonnet 4.5
