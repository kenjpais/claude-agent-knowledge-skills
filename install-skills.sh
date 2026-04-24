#!/bin/bash
# Install Agent Knowledge System skills to Claude Code

set -e

REPO_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILLS_DIR="$HOME/.claude/skills"

echo "🔧 Installing Agent Knowledge System skills..."
echo ""

# Create skills directory if it doesn't exist
mkdir -p "$SKILLS_DIR"

# Install the 4 user-facing skills
skills=(
  "create-agentic-docs"
  "validate-agentic-docs"
  "evaluate-agentic-docs"
  "ask-agentic-docs"
)

for skill in "${skills[@]}"; do
  source_path="$REPO_DIR/skills/$skill"
  target_path="$SKILLS_DIR/$skill"

  # Remove existing symlink or directory
  if [ -L "$target_path" ]; then
    echo "  Removing existing symlink: $skill"
    rm "$target_path"
  elif [ -d "$target_path" ]; then
    echo "  ⚠️  Directory exists (not a symlink): $skill"
    echo "     Skipping. Remove manually if needed: rm -rf $target_path"
    continue
  fi

  # Create symlink
  ln -s "$source_path" "$target_path"
  echo "  ✅ Installed: $skill"
done

echo ""
echo "✅ Skills installed successfully!"
echo ""
echo "Installed skills:"
echo "  /create   - Generate agentic documentation"
echo "  /validate - Validate documentation quality"
echo "  /evaluate - Test with coding agent simulation"
echo "  /ask      - Query documentation"
echo ""
echo "Try it: Open Claude Code and type /create"
