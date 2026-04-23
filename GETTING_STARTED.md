# Getting Started - Agent Knowledge System

**Generate agentic documentation in 3 simple steps!**

---

## 🚀 Quick Start (5 minutes)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/claude-agent-knowledge-system-skills.git
cd claude-agent-knowledge-system-skills

# Run automated setup
./setup.sh
```

The setup script will:
- ✅ Check prerequisites (Python 3.9+)
- ✅ Install Python dependencies
- ✅ Configure MCP servers (GitHub)
- ✅ Create CLI commands
- ✅ Set up environment

**Time**: ~2 minutes

### Step 2: Configure GitHub Token (Optional)

For higher rate limits and private repos:

```bash
# Create token at: https://github.com/settings/tokens
# Required scopes: repo, read:org

export GITHUB_TOKEN=ghp_your_token_here

# Make it permanent
echo 'export GITHUB_TOKEN=ghp_your_token_here' >> ~/.bashrc
```

**Without GitHub token**: System works with public repos at lower rate limits (60 requests/hour)

**Time**: ~2 minutes

### Step 3: Generate Documentation

```bash
# Add CLI to PATH (if not already)
export PATH="$HOME/.local/bin:$PATH"

# Generate documentation for any OpenShift repository
agentic-docs generate /path/to/openshift-installer

# Or try a quick test
cd /tmp
git clone --depth 1 https://github.com/openshift/installer
agentic-docs generate installer
```

**Time**: 2-3 hours for full repository (or 15 minutes for demo with 3 components)

---

## 📋 What You Get

After generation completes, you'll have:

```
your-repository/
├── AGENTS.md                    # 🎯 Primary entry point
└── agentic/
    ├── DESIGN.md                # Architecture and philosophy
    ├── DEVELOPMENT.md           # Build, test, debug commands
    ├── TESTING.md               # Test strategy
    ├── RELIABILITY.md           # SLOs and observability
    ├── SECURITY.md              # Security model
    ├── QUALITY_SCORE.md         # Quality metrics (0-100)
    ├── design-docs/
    │   └── components/          # Component documentation
    │       ├── component-1.md
    │       ├── component-2.md
    │       └── ...
    └── domain/
        ├── concepts/            # Domain concepts
        └── workflows/           # Process workflows
```

---

## 🎓 Prerequisites

### Required
- **Python 3.9+** (for validation utilities)
- **Claude Code** - Install from https://claude.ai/code

### Optional (for enhanced features)
- **Node.js/npm** (for GitHub MCP server)
- **GitHub Token** (for private repos and higher rate limits)
- **Git** (for extracting git history)

### Check Prerequisites

```bash
python3 --version  # Should be 3.9+
which claude       # Should return path to Claude Code
```

---

## 🔧 Detailed Setup Options

### Option A: Automatic Setup (Recommended)

```bash
./setup.sh
```

This handles everything automatically!

### Option B: Manual Setup

If you prefer manual control:

1. **Install Python dependencies**:
   ```bash
   pip3 install pyyaml
   ```

2. **Configure MCP servers**:
   ```bash
   mkdir -p ~/.claude
   cat > ~/.claude/mcp_servers.json << 'EOF'
   {
     "mcpServers": {
       "github": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-github"],
         "env": {
           "GITHUB_TOKEN": "${GITHUB_TOKEN}"
         }
       }
     }
   }
   EOF
   ```

3. **Add CLI to PATH**:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   ```

---

## 🎯 Usage Examples

### Generate Documentation

```bash
# Full generation (all components)
agentic-docs generate /path/to/repository

# Initialize structure only (no generation)
agentic-docs init /path/to/repository

# Validate existing documentation
agentic-docs validate /path/to/repository
```

### Environment Variables

```bash
# GitHub (optional - for private repos and higher limits)
export GITHUB_TOKEN=ghp_your_token_here

# JIRA (optional - only for PRIVATE JIRA instances)
# Public JIRA like issues.redhat.com works WITHOUT authentication!
export JIRA_URL=https://your-jira.com
export JIRA_EMAIL=your-email@company.com
export JIRA_API_TOKEN=your-api-token

# System configuration
export AGENTIC_SYSTEM_DIR=$HOME/agent-knowledge-system
```

---

## 📊 JIRA Integration (Simplified!)

### Public JIRA (No Auth Required!) ✅

For **Red Hat JIRA** (issues.redhat.com) and other public instances:

```bash
# NO setup needed! Just run:
agentic-docs generate /path/to/openshift-repo

# The system automatically accesses public JIRA issues
# No API tokens, no authentication, no configuration!
```

**Supported public JIRA instances**:
- ✅ issues.redhat.com (Red Hat)
- ✅ issues.apache.org (Apache)
- ✅ jira.mongodb.org (MongoDB)
- ✅ Any public JIRA instance

### Private JIRA (Optional)

Only needed for **private JIRA instances**:

```bash
export JIRA_URL=https://your-company.atlassian.net
export JIRA_EMAIL=your-email@company.com
export JIRA_API_TOKEN=your-api-token
```

See `integrations/jira/SIMPLIFIED_SETUP.md` for details.

---

## 🧪 Test the System

### Quick Test (5 minutes)

```bash
# Clone a small test repository
cd /tmp
git clone --depth 1 https://github.com/openshift/api
cd api

# Initialize structure
agentic-docs init .

# Generate documentation (demo mode - 3 components)
agentic-docs generate .

# Validate
agentic-docs validate .
```

### Full Test (2-3 hours)

```bash
# Clone OpenShift installer
git clone https://github.com/openshift/installer
cd installer

# Generate complete documentation
agentic-docs generate .

# Check quality score
cat agentic/QUALITY_SCORE.md
```

---

## 🛠️ Troubleshooting

### "claude: command not found"
**Solution**: Install Claude Code from https://claude.ai/code

### "Python 3.9+ required"
**Solution**: 
```bash
# macOS
brew install python3

# Ubuntu/Debian
sudo apt install python3.9
```

### "npx: command not found"
**Solution**: Install Node.js from https://nodejs.org (optional, only needed for GitHub MCP)

### "GitHub API rate limit exceeded"
**Solution**: Set GITHUB_TOKEN environment variable

### Generation takes too long
**Solution**: 
- Use demo mode (processes 3 components instead of all)
- Ensure good internet connection
- Check Claude Code is responsive

### Quality score below 70
**Solution**: This is normal for demo mode. Full generation achieves 85-90/100.

---

## 📚 Next Steps

After successful setup:

1. **Generate documentation** for your OpenShift repository
2. **Review quality score** in `agentic/QUALITY_SCORE.md`
3. **Validate navigation** - ensure all docs reachable in ≤3 hops
4. **Commit to repository** - make docs available to team
5. **Test with agents** - have Claude Code navigate using AGENTS.md

---

## 🎓 Learning Resources

- **README.md** - System overview and architecture
- **CLAUDE.md** - Complete implementation guide
- **AGENT_KNOWLEDGE_FRAMEWORK.md** - Framework specification
- **EVALUATION_REPORT.md** - Test results and quality analysis
- **agents/*/AGENT.md** - Individual agent documentation
- **skills/*/**.md** - Skill specifications

---

## 🤝 Support

### Common Issues
- Check `troubleshooting` section above
- Review logs in `.openshift_install.log` (if applicable)
- Validate MCP servers: `claude config list`

### Getting Help
- **Documentation**: README.md, CLAUDE.md
- **Issues**: https://github.com/your-org/agent-knowledge-system/issues
- **Examples**: See `/tmp/installer-agentic-demo/` (from test)

---

## ✅ System Check

Run this to verify your setup:

```bash
# Check Python
python3 --version

# Check Claude Code
claude --version

# Check PATH includes CLI
which agentic-docs

# Check MCP servers
cat ~/.claude/mcp_servers.json

# Test public JIRA access (no auth needed!)
python3 integrations/jira/public_jira_client.py
```

All checks pass? **You're ready to generate documentation!** 🎉

---

## 🚀 Quick Start Summary

```bash
# 1. Setup (2 minutes)
git clone <repo>
cd claude-agent-knowledge-system-skills
./setup.sh

# 2. Configure (optional, 2 minutes)
export GITHUB_TOKEN=ghp_xxx  # Optional
export PATH="$HOME/.local/bin:$PATH"

# 3. Generate (2-3 hours)
agentic-docs generate /path/to/openshift-repo

# Done! ✅
```

**Total time**: 5 minutes setup + 2-3 hours generation = **Production-ready agentic documentation!**
