#!/bin/bash
# Agent Knowledge System - Automated Setup
# Initializes Claude Code, configures MCP servers, and prepares the system

set -e

echo "🚀 Agent Knowledge System - Setup"
echo "=================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

if ! command -v npx &> /dev/null; then
    echo "⚠️  npx not found. GitHub MCP server will not be available."
    echo "   Install Node.js to enable GitHub integration."
    GITHUB_AVAILABLE=false
else
    GITHUB_AVAILABLE=true
fi

echo "✅ Prerequisites checked"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -q pyyaml 2>/dev/null || echo "⚠️  PyYAML already installed or install failed"
echo "✅ Python dependencies ready"
echo ""

# Create .claude directory if it doesn't exist
CLAUDE_DIR="$HOME/.claude"
mkdir -p "$CLAUDE_DIR"

# Configure MCP servers
echo "⚙️  Configuring MCP servers..."

MCP_CONFIG="$CLAUDE_DIR/mcp_servers.json"

# Check if config exists and back it up
if [ -f "$MCP_CONFIG" ]; then
    echo "   Backing up existing MCP config..."
    cp "$MCP_CONFIG" "$MCP_CONFIG.backup.$(date +%s)"
fi

# Create MCP server configuration
cat > "$MCP_CONFIG" << 'EOF'
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      },
      "disabled": false
    }
  }
}
EOF

echo "✅ MCP servers configured"
echo ""

# Check for GitHub token
echo "🔑 Checking GitHub authentication..."
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN not set."
    echo "   For private repos and higher rate limits, set GITHUB_TOKEN:"
    echo "   export GITHUB_TOKEN=ghp_your_token_here"
    echo ""
    echo "   The system will work with public repos using unauthenticated access."
else
    echo "✅ GitHub token found"
fi
echo ""

# JIRA configuration info
echo "📊 JIRA Integration:"
echo "   For PUBLIC JIRA instances (like issues.redhat.com):"
echo "   ✅ No authentication required"
echo "   ✅ System will access public issues directly via REST API"
echo ""
echo "   For PRIVATE JIRA instances:"
echo "   Set these environment variables:"
echo "   export JIRA_URL=https://your-jira.com"
echo "   export JIRA_EMAIL=your-email@company.com"
echo "   export JIRA_API_TOKEN=your-api-token"
echo ""

# Create convenience scripts
echo "🛠️  Creating convenience scripts..."

# Create 'agentic-docs' command
cat > "$HOME/.local/bin/agentic-docs" << 'EOFSCRIPT'
#!/bin/bash
# Agent Knowledge System - CLI Wrapper

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEM_DIR="${AGENTIC_SYSTEM_DIR:-$HOME/agent-knowledge-system}"

if [ ! -d "$SYSTEM_DIR" ]; then
    echo "❌ Agent Knowledge System not found at: $SYSTEM_DIR"
    echo "   Set AGENTIC_SYSTEM_DIR or clone to ~/agent-knowledge-system"
    exit 1
fi

case "$1" in
    generate)
        shift
        "$SYSTEM_DIR/bin/generate-docs.sh" "$@"
        ;;
    validate)
        shift
        python3 "$SYSTEM_DIR/utilities/validation/validator.py" "$@"
        ;;
    init)
        shift
        "$SYSTEM_DIR/bin/init-repository.sh" "$@"
        ;;
    help|--help|-h|"")
        echo "Agent Knowledge System - CLI"
        echo ""
        echo "Usage: agentic-docs <command> [options]"
        echo ""
        echo "Commands:"
        echo "  generate <repo-path>  Generate agentic documentation for repository"
        echo "  validate <repo-path>  Validate existing agentic documentation"
        echo "  init <repo-path>      Initialize agentic/ structure in repository"
        echo "  help                  Show this help message"
        echo ""
        echo "Examples:"
        echo "  agentic-docs generate /path/to/openshift-installer"
        echo "  agentic-docs validate /path/to/openshift-installer"
        echo "  agentic-docs init /path/to/new-repo"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Run 'agentic-docs help' for usage information"
        exit 1
        ;;
esac
EOFSCRIPT

mkdir -p "$HOME/.local/bin"
chmod +x "$HOME/.local/bin/agentic-docs"

echo "✅ Created 'agentic-docs' command"
echo ""

# Create pipeline runner
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$SCRIPT_DIR/bin"

cat > "$SCRIPT_DIR/bin/generate-docs.sh" << 'EOFGEN'
#!/bin/bash
# Generate agentic documentation for a repository

set -e

REPO_PATH="${1:-.}"

if [ ! -d "$REPO_PATH" ]; then
    echo "❌ Repository not found: $REPO_PATH"
    exit 1
fi

echo "🚀 Generating Agentic Documentation"
echo "===================================="
echo ""
echo "Repository: $REPO_PATH"
echo ""

# Check if Claude Code is available
if ! command -v claude &> /dev/null; then
    echo "❌ Claude Code CLI not found."
    echo "   Please install Claude Code from https://claude.ai/code"
    exit 1
fi

# Create execution plan
EXEC_PLAN="$REPO_PATH/agentic/exec-plans/active/generate-docs-$(date +%s).md"
mkdir -p "$REPO_PATH/agentic/exec-plans/active"

cat > "$EXEC_PLAN" << EOF
---
type: execution-plan
scope: full
status: active
created: $(date -Iseconds)
---

# Execution Plan: Full Documentation Generation

## Scope
- **Target**: $REPO_PATH
- **Reason**: Initial generation
- **Triggered by**: CLI (agentic-docs generate)

## Phases
- [ ] Extraction
- [ ] Synthesis
- [ ] Linking
- [ ] Validation

## Status
Pipeline started: $(date)
EOF

echo "📋 Execution plan created: $EXEC_PLAN"
echo ""

# Invoke Claude Code with orchestrator prompt
echo "🤖 Invoking Orchestrator Agent via Claude Code..."
echo ""

cd "$REPO_PATH"

# Create prompt for Claude
PROMPT="I am the Orchestrator Agent from the Agent Knowledge System.

My task is to generate complete agentic documentation for this repository following the framework at: $HOME/agent-knowledge-system

Please execute the full documentation generation pipeline:

1. **EXTRACTION PHASE**:
   - Discover repository structure (list all packages in pkg/ or src/)
   - Identify primary language and framework
   - Extract key components (3-5 main components)
   - Build high-level dependency understanding

2. **SYNTHESIS PHASE**:
   - Infer component boundaries and roles
   - Generate component documentation (use template at templates/agentic-structure/component.md.template)
   - Generate concept documentation for key domain concepts
   - Create DESIGN.md, DEVELOPMENT.md, TESTING.md, RELIABILITY.md, SECURITY.md

3. **LINKING PHASE**:
   - Generate AGENTS.md (use template at templates/agentic-structure/AGENTS.md.template)
   - Link concepts to components (bidirectional)
   - Create navigation structure

4. **VALIDATION PHASE**:
   - Validate line budgets (AGENTS.md ≤150, components ≤100, concepts ≤75)
   - Check required files present
   - Generate QUALITY_SCORE.md

Output all documentation to ./agentic/ directory.

Reference the Agent Knowledge System at: $HOME/agent-knowledge-system
Use templates from: $HOME/agent-knowledge-system/templates/

Begin generation now."

# Run Claude Code
echo "$PROMPT" | claude code --directory "$REPO_PATH"

echo ""
echo "✅ Documentation generation complete!"
echo "   Output: $REPO_PATH/agentic/"
echo ""
echo "Next steps:"
echo "  1. Review generated documentation"
echo "  2. Run validation: agentic-docs validate $REPO_PATH"
echo "  3. Commit to repository"
EOFGEN

chmod +x "$SCRIPT_DIR/bin/generate-docs.sh"

# Create init script
cat > "$SCRIPT_DIR/bin/init-repository.sh" << 'EOFINIT'
#!/bin/bash
# Initialize agentic/ directory structure in a repository

REPO_PATH="${1:-.}"

if [ ! -d "$REPO_PATH" ]; then
    echo "❌ Repository not found: $REPO_PATH"
    exit 1
fi

echo "📁 Initializing agentic documentation structure..."
echo ""

mkdir -p "$REPO_PATH/agentic/design-docs/components"
mkdir -p "$REPO_PATH/agentic/domain/concepts"
mkdir -p "$REPO_PATH/agentic/domain/workflows"
mkdir -p "$REPO_PATH/agentic/decisions"
mkdir -p "$REPO_PATH/agentic/exec-plans/active"
mkdir -p "$REPO_PATH/agentic/exec-plans/completed"

# Copy templates
TEMPLATES_DIR="${AGENTIC_SYSTEM_DIR:-$HOME/agent-knowledge-system}/templates/agentic-structure"

if [ -d "$TEMPLATES_DIR" ]; then
    cp "$TEMPLATES_DIR/QUALITY_SCORE.md.template" "$REPO_PATH/agentic/QUALITY_SCORE.md"
    echo "✅ Created initial QUALITY_SCORE.md"
fi

echo "✅ Directory structure created at: $REPO_PATH/agentic/"
echo ""
echo "Structure:"
echo "$REPO_PATH/agentic/"
echo "├── design-docs/"
echo "│   └── components/"
echo "├── domain/"
echo "│   ├── concepts/"
echo "│   └── workflows/"
echo "├── decisions/"
echo "├── exec-plans/"
echo "│   ├── active/"
echo "│   └── completed/"
echo "└── QUALITY_SCORE.md"
echo ""
echo "Next: Run 'agentic-docs generate $REPO_PATH' to generate documentation"
EOFINIT

chmod +x "$SCRIPT_DIR/bin/init-repository.sh"

# Set environment variable helper
cat > "$SCRIPT_DIR/.env.example" << 'EOF'
# Agent Knowledge System - Environment Configuration

# GitHub Integration (Optional - increases rate limits and enables private repos)
# Create token at: https://github.com/settings/tokens
# Required scopes: repo, read:org
GITHUB_TOKEN=ghp_your_token_here

# JIRA Integration (Optional - only needed for PRIVATE JIRA instances)
# Public JIRA (like issues.redhat.com) works WITHOUT authentication
JIRA_URL=https://your-jira-instance.com
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-jira-api-token

# System Configuration
AGENTIC_SYSTEM_DIR=$HOME/agent-knowledge-system
EOF

echo "✅ Created .env.example for reference"
echo ""

# Final setup message
echo "============================================"
echo "✅ Setup Complete!"
echo "============================================"
echo ""
echo "📚 What was configured:"
echo "   ✅ MCP servers: $MCP_CONFIG"
echo "   ✅ CLI command: agentic-docs (in ~/.local/bin/)"
echo "   ✅ Pipeline scripts in ./bin/"
echo ""
echo "🚀 Quick Start:"
echo ""
echo "1. Add CLI to PATH (if not already):"
echo "   echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
echo "   source ~/.bashrc"
echo ""
echo "2. Set GitHub token (optional, for higher rate limits):"
echo "   export GITHUB_TOKEN=ghp_your_token_here"
echo ""
echo "3. Generate documentation for a repository:"
echo "   agentic-docs generate /path/to/openshift-repo"
echo ""
echo "   OR use the scripts directly:"
echo "   ./bin/generate-docs.sh /path/to/openshift-repo"
echo ""
echo "📖 For JIRA integration:"
echo "   - Public JIRA: No setup needed!"
echo "   - Private JIRA: Set JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN"
echo ""
echo "🔍 Example repositories to try:"
echo "   - github.com/openshift/installer"
echo "   - github.com/openshift/machine-api-operator"
echo "   - github.com/kubernetes/kubernetes"
echo ""
echo "📘 Documentation: See README.md and CLAUDE.md"
echo ""
