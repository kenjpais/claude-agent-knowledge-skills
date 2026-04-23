# ⚡ Quick Start - 5 Minutes to Agentic Documentation

Generate agent-optimized documentation for any OpenShift repository in 3 commands!

---

## 📦 Step 1: Clone and Setup (2 minutes)

```bash
# Clone the Agent Knowledge System
git clone https://github.com/your-org/claude-agent-knowledge-system-skills.git
cd claude-agent-knowledge-system-skills

# Run automated setup
./setup.sh
```

**What happens**:
- ✅ Checks Python 3.9+ installed
- ✅ Installs dependencies (pyyaml)
- ✅ Configures GitHub MCP server
- ✅ Creates `agentic-docs` CLI command
- ✅ Sets up environment

**Output**:
```
🚀 Agent Knowledge System - Setup
==================================

📋 Checking prerequisites...
✅ Prerequisites checked

📦 Installing Python dependencies...
✅ Python dependencies ready

⚙️  Configuring MCP servers...
✅ MCP servers configured

🛠️  Creating convenience scripts...
✅ Created 'agentic-docs' command

============================================
✅ Setup Complete!
============================================
```

---

## 🔑 Step 2: Set GitHub Token (Optional, 1 minute)

**For higher API rate limits and private repos**:

```bash
# Create token at: https://github.com/settings/tokens
# Scopes: repo, read:org

export GITHUB_TOKEN=ghp_your_token_here
```

**Skip this step if**:
- ✅ Generating docs for public repos only
- ✅ Don't mind 60 requests/hour limit (vs 5,000 with token)

---

## 🚀 Step 3: Generate Documentation (5 min - 3 hours)

```bash
# Option A: Quick demo (5 minutes, 3 components)
cd /tmp
git clone --depth 1 https://github.com/openshift/installer
agentic-docs generate installer

# Option B: Full generation (2-3 hours, all components)
agentic-docs generate /path/to/your/openshift-repo

# Option C: Initialize only (creates structure, no generation)
agentic-docs init /path/to/repo
```

**What it generates**:

```
your-repo/
├── AGENTS.md                    # 🎯 Entry point (≤150 lines)
└── agentic/
    ├── DESIGN.md                # Architecture
    ├── DEVELOPMENT.md           # Build & test commands
    ├── TESTING.md               # Test strategy
    ├── RELIABILITY.md           # SLOs
    ├── SECURITY.md              # Security model
    ├── QUALITY_SCORE.md         # Quality metrics (0-100)
    ├── design-docs/components/  # Component docs (≤100 lines each)
    └── domain/concepts/         # Domain concepts (≤75 lines each)
```

---

## ✅ Verify

```bash
# Check quality score
cat your-repo/agentic/QUALITY_SCORE.md

# Validate documentation
agentic-docs validate your-repo

# View entry point
cat your-repo/AGENTS.md
```

**Expected quality score**: 85-90/100 (full generation)

---

## 🎓 Usage Examples

### Example 1: OpenShift Installer

```bash
git clone https://github.com/openshift/installer
cd installer
agentic-docs generate .

# Result: 22 components documented
# Quality score: 87/100
# Time: 2-3 hours
```

### Example 2: Machine API Operator

```bash
git clone https://github.com/openshift/machine-api-operator
cd machine-api-operator
agentic-docs generate .

# Result: 15 components documented
# Quality score: 90/100
# Time: 1-2 hours
```

### Example 3: Quick Test

```bash
cd /tmp
git clone --depth 1 https://github.com/openshift/api
agentic-docs init api
# Structure created, ready for generation
```

---

## 🔧 CLI Commands

```bash
# Generate documentation
agentic-docs generate /path/to/repo

# Validate existing docs
agentic-docs validate /path/to/repo

# Initialize directory structure
agentic-docs init /path/to/repo

# Show help
agentic-docs help
```

---

## 🌟 Features

### Public JIRA - No Auth! 🎉

**Works automatically** for Red Hat JIRA (issues.redhat.com):

```bash
# NO configuration needed!
agentic-docs generate /path/to/openshift-repo

# System automatically:
# ✅ Accesses public JIRA issues
# ✅ Extracts features and bugs
# ✅ Links to requirements
```

**Other supported public JIRAs**:
- issues.apache.org
- jira.mongodb.org
- Any public JIRA instance

**Private JIRA**: See `integrations/jira/SIMPLIFIED_SETUP.md`

### GitHub Integration

**Automatic extraction**:
- ✅ PR descriptions and reviews
- ✅ Commit messages and history
- ✅ Issue discussions
- ✅ Architecture decisions from PRs

**Configuration**: Optional `GITHUB_TOKEN` for private repos

### Graphify Integration

**Knowledge graph generation**:
```bash
# Install graphify (optional)
pip install graphify

# Generate graph
cd your-repo
graphify .

# System automatically uses graph for:
# ✅ Component boundary detection
# ✅ Concept extraction
# ✅ Relationship mapping
```

---

## 🎯 What You Get

### Navigation by Intent

AGENTS.md provides **intent-based navigation**:

| I want to... | Start here |
|--------------|------------|
| Understand this repo | AGENTS.md |
| Set up dev environment | DEVELOPMENT.md |
| Find a component | Component boundaries table |
| Learn a concept | Core concepts list |
| Build the project | Build & test commands |

### Progressive Disclosure

**3-hop navigation** to any information:

```
AGENTS.md (hop 0)
  ↓
Component doc (hop 1)
  ↓
Code reference (hop 2)
```

**Example**:
```
Q: "How do I add a new cloud platform?"
A: AGENTS.md → Critical code locations
   → "pkg/infrastructure/{platform}/"
   
Hops: 1 ✅
```

### Quality Enforcement

**Automatic validation**:
- ✅ Line budgets (AGENTS.md ≤150, components ≤100)
- ✅ Required files (7 mandatory docs)
- ✅ Navigation depth (≤3 hops)
- ✅ Link validation
- ✅ Template compliance

---

## 📊 Performance

| Repository Size | Components | Time | Quality Score |
|----------------|------------|------|---------------|
| Small (5-10 pkgs) | 5-10 | 30 min | 85-90/100 |
| Medium (10-20 pkgs) | 10-20 | 1-2 hrs | 85-90/100 |
| Large (20+ pkgs) | 20+ | 2-3 hrs | 85-90/100 |

**Demo mode** (3 components): 5-15 minutes

---

## 🆘 Troubleshooting

### Setup Issues

**"claude: command not found"**
```bash
# Install Claude Code
# Visit: https://claude.ai/code
```

**"Python 3.9+ required"**
```bash
# macOS
brew install python3

# Ubuntu
sudo apt install python3.9
```

**"npx: command not found"**
```bash
# Install Node.js (optional, only for GitHub MCP)
# Visit: https://nodejs.org
```

### Generation Issues

**"Rate limit exceeded"**
```bash
# Set GitHub token
export GITHUB_TOKEN=ghp_your_token_here
```

**"Quality score below 70"**
```
This is normal for demo mode (3 components).
Full generation achieves 85-90/100.
```

**"Generation takes too long"**
```
- Check internet connection
- Ensure Claude Code is responsive
- Try demo mode first (faster)
```

---

## 🎓 Learn More

| Resource | Purpose |
|----------|---------|
| **GETTING_STARTED.md** | Detailed setup guide |
| **README.md** | System overview |
| **CLAUDE.md** | Implementation guide |
| **SIMPLIFIED_SETUP_SUMMARY.md** | What was simplified |
| **agents/*/AGENT.md** | Agent specifications |
| **skills/*/**.md** | Skill definitions |

---

## ✨ Success Checklist

After completing quick start, you should have:

- ✅ Agent Knowledge System cloned
- ✅ Setup completed (`./setup.sh` ran successfully)
- ✅ CLI command available (`which agentic-docs` returns path)
- ✅ MCP servers configured (`~/.claude/mcp_servers.json` exists)
- ✅ (Optional) GitHub token set
- ✅ Documentation generated for at least one repository
- ✅ Quality score ≥70/100 (or identified as demo limitation)

**All checked?** 🎉 **You're ready to generate agentic documentation!**

---

## 🚀 Next Steps

1. **Generate for your main OpenShift repo**
   ```bash
   agentic-docs generate /path/to/your/repo
   ```

2. **Review quality score**
   ```bash
   cat your-repo/agentic/QUALITY_SCORE.md
   ```

3. **Test with Claude Code**
   ```bash
   cd your-repo
   claude code
   # Ask: "How do I build this project?"
   # Claude will navigate using AGENTS.md
   ```

4. **Commit to repository**
   ```bash
   git add AGENTS.md agentic/
   git commit -m "Add agentic documentation"
   git push
   ```

5. **Share with team**
   - Documentation now available to all developers
   - AI assistants can navigate efficiently
   - Quality improves over time with curator agent

---

## 💡 Pro Tips

**Tip 1**: Start with demo mode (fast feedback)
```bash
# Generate 3 components first
agentic-docs generate --demo /path/to/repo
```

**Tip 2**: Use quality score to iterate
```bash
# Check score
cat agentic/QUALITY_SCORE.md

# Fix issues identified
# Re-run generation
agentic-docs generate .
```

**Tip 3**: Validate before committing
```bash
agentic-docs validate .
# Fix any warnings
git commit
```

**Tip 4**: Keep documentation fresh
```bash
# Re-run after major changes
agentic-docs generate .
# Curator agent detects what changed
```

---

## 📞 Support

- **Issues**: https://github.com/your-org/agent-knowledge-system/issues
- **Documentation**: See resources in "Learn More" section
- **Examples**: `/tmp/installer-agentic-demo/` (from test)

---

**Total Time**: 5 minutes setup + generation time = Production-ready documentation! ✅
