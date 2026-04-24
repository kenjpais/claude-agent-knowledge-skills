# Usage Guide

Simple guide for using the agentic documentation system.

---

## Installation

```bash
# Clone repository
git clone https://github.com/kenjpais/claude-agent-knowledge-skills.git
cd claude-agent-knowledge-skills

# Install dependencies
pip install -r requirements.txt

# Add to PATH (optional, for global use)
export PATH="$PATH:$(pwd)"
# Or add to ~/.bashrc or ~/.zshrc for persistence
```

---

## Commands

The system provides one simple command with three slash commands:

```bash
agentic /create <repository>      # Generate documentation
agentic /validate <repository>    # Validate quality
agentic /ask <question>           # Query documentation
```

---

## `/create` - Generate Documentation

Generate complete agentic documentation for any repository.

### Usage

```bash
agentic /create <repository>
```

### Examples

**GitHub repository:**
```bash
agentic /create https://github.com/openshift/installer
agentic /create https://github.com/kubernetes/kubernetes
```

**Local repository:**
```bash
agentic /create /path/to/local/repo
agentic /create ~/projects/my-app
agentic /create .                          # Current directory
```

### What it does

1. **Extraction** - Discovers components, APIs, dependencies
2. **Synthesis** - Generates documentation from extracted data
3. **Linking** - Creates AGENTS.md and navigation structure
4. **Validation** - Ensures quality constraints are met

### Output

```
repository/
├── AGENTS.md                    # Entry point (≤150 lines)
└── agentic/
    ├── DESIGN.md               # Design philosophy
    ├── DEVELOPMENT.md          # Development setup
    ├── TESTING.md              # Test strategy
    ├── RELIABILITY.md          # SLOs and observability
    ├── SECURITY.md             # Security model
    ├── QUALITY_SCORE.md        # Quality metrics
    ├── design-docs/
    │   └── components/         # Component docs (≤100 lines each)
    ├── domain/
    │   └── concepts/           # Concept docs (≤75 lines each)
    └── exec-plans/             # Execution tracking
```

---

## `/validate` - Validate Documentation

Validate existing documentation against quality constraints.

### Usage

```bash
agentic /validate <repository>
```

### Examples

**GitHub repository:**
```bash
agentic /validate https://github.com/openshift/installer
```

**Local repository:**
```bash
agentic /validate /path/to/repo
agentic /validate .                        # Current directory
```

### What it validates

1. **Structure** - Required files exist
2. **Navigation** - All docs reachable in ≤3 hops
3. **Line Budgets** - Documents within limits (150/100/75)
4. **Links** - No broken links
5. **Coverage** - % of components documented
6. **Freshness** - Documentation updated recently
7. **Completeness** - Required sections present
8. **Quality Score** - Overall score ≥70/100

### Output

```
Validation Report
=================
Repository: openshift-installer
Overall Score: 88/100 ✅ PASS

Summary:
  ✅ All required files present
  ✅ Max navigation depth: 2 hops
  ✅ No broken links
  ✅ Coverage: 87.5% (7/8 components)

Quality Score Breakdown:
  Coverage: 35/40 (87.5%)
  Freshness: 18/20 (90%)
  Completeness: 20/20 (100%)
  Linkage: 10/10 (100%)
  Navigation: 10/10 (100%)

Recommendations:
  1. Document missing component: validator
  2. Update stale doc: old-component.md
```

---

## `/ask` - Query Documentation

Query documentation to retrieve specific information.

### Usage

```bash
agentic /ask <question>
```

**Note:** This command works in the repository directory where documentation exists.

### Examples

```bash
# First, navigate to a repository with documentation
cd /path/to/repo

# Then query
agentic /ask what components exist?
agentic /ask how does the installer work?
agentic /ask what is the reconciliation pattern?
agentic /ask show me the architecture
agentic /ask how to run tests?
agentic /ask what depends on the installer?
```

### Query Types

1. **Component Discovery**
   - "what components exist?"
   - "list all components"

2. **Component Details**
   - "how does {component} work?"
   - "what does {component} do?"

3. **Concept Lookup**
   - "what is {concept}?"
   - "explain {concept}"

4. **Architecture**
   - "show me the architecture"
   - "how is the system structured?"

5. **Development**
   - "how to contribute?"
   - "how to run tests?"

6. **Relationships**
   - "what uses {component}?"
   - "how are A and B related?"

### Response Format

```markdown
## {Question}

**Answer**: {concise answer}

**Details**:
{relevant details from documentation}

**Related**:
- [Related Component](path/to/doc.md)
- [Related Concept](path/to/concept.md)

**Next Steps**:
- To learn more: agentic /ask {related question}
- To see code: {file path}
```

---

## Typical Workflows

### Workflow 1: Initial Documentation Generation

```bash
# 1. Generate documentation
agentic /create https://github.com/openshift/installer

# 2. Validate quality
agentic /validate https://github.com/openshift/installer

# 3. Navigate to repository and query
cd /tmp/agentic-repos/installer
agentic /ask what components exist?
agentic /ask how does the installer work?
```

### Workflow 2: Local Repository

```bash
# 1. Generate for local repo
cd /path/to/my-project
agentic /create .

# 2. Validate
agentic /validate .

# 3. Query
agentic /ask what components exist?
```

### Workflow 3: Documentation Maintenance

```bash
# 1. Check current quality
cd /path/to/repo
agentic /validate .

# 2. If score is low, regenerate
agentic /create .

# 3. Re-validate
agentic /validate .
```

---

## Configuration

### GitHub Token (Optional)

For higher rate limits and private repositories:

```bash
# Copy example
cp .env.example .env

# Edit .env and add your token
# GH_API_TOKEN=ghp_your_token_here
```

**Get a token:** https://github.com/settings/tokens  
**Required scopes:** `repo`, `read:org`

**Benefits:**
- ✅ 5,000 requests/hour (vs 60 without token)
- ✅ Access to private repositories
- ✅ Better reliability

---

## Help

```bash
# Show usage information
agentic --help
agentic -h
agentic help
```

---

## Troubleshooting

### "Repository not found"

**Problem:** Path doesn't exist  
**Solution:** Check the path is correct

```bash
# Wrong
agentic /create /nonexistent/path

# Right
agentic /create /Users/name/projects/repo
```

### "No agentic documentation found"

**Problem:** Documentation doesn't exist  
**Solution:** Run `/create` first

```bash
# Create documentation first
agentic /create .

# Then validate or query
agentic /validate .
agentic /ask what components exist?
```

### "Failed to clone"

**Problem:** GitHub repository URL is incorrect  
**Solution:** Check the URL

```bash
# Wrong
agentic /create github.com/owner/repo

# Right
agentic /create https://github.com/owner/repo
```

### Permission errors

**Problem:** Can't write to directory  
**Solution:** Check permissions or use a different directory

```bash
# Use /tmp for GitHub repos (automatic)
agentic /create https://github.com/owner/repo

# Or clone manually first
git clone https://github.com/owner/repo ~/repos/repo
agentic /create ~/repos/repo
```

---

## Next Steps

- **Complete Guide:** [CORE_SKILLS.md](CORE_SKILLS.md)
- **Development:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Implementation:** [CLAUDE.md](CLAUDE.md)
- **Project Overview:** [README.md](README.md)

---

## Examples

### OpenShift Installer

```bash
# Generate
agentic /create https://github.com/openshift/installer

# Navigate
cd /tmp/agentic-repos/installer

# Query
agentic /ask what components exist?
agentic /ask how does the installer work?
agentic /ask what is the bootstrap process?
```

### Local Project

```bash
# Your project
cd ~/my-awesome-project

# Generate
agentic /create .

# Validate
agentic /validate .

# Query
agentic /ask what components exist?
agentic /ask how does X work?
```

### Validation Only

```bash
# Check existing documentation
cd /path/to/repo-with-docs
agentic /validate .

# Review quality score in output
# If score < 70, regenerate
agentic /create .
```

---

## Summary

Simple CLI with three commands:

```bash
agentic /create <repo>      # Generate docs
agentic /validate <repo>    # Check quality  
agentic /ask <question>     # Query docs
```

**Repository can be:**
- GitHub URL: `https://github.com/owner/repo`
- Local path: `/path/to/repo` or `.`

**That's it!** 🚀
