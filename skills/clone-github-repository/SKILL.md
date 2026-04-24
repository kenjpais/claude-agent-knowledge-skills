---
skill_id: clone-github-repository
name: Clone GitHub Repository
category: repo
version: 1.0.0
description: Clone a GitHub repository if not already present locally
inputs: [github_url]
outputs: [local_path, repository_name, owner]
---

# Clone GitHub Repository

**Purpose**: Clone a GitHub repository to a local path for processing by other skills

## Input Schema

```yaml
github_url: string              # GitHub repository URL
target_directory: string        # Optional: target directory (default: /tmp/agentic-repos/<repo-name>)
```

## Supported URL Formats

```bash
# HTTPS URLs
https://github.com/owner/repo
https://github.com/owner/repo.git

# HTTPS without protocol
github.com/owner/repo

# SSH URLs
git@github.com:owner/repo.git
git@github.com:owner/repo

# Short format
owner/repo
```

## Workflow

### Step 1: Parse GitHub URL

```python
import re
from urllib.parse import urlparse

def parse_github_url(url: str) -> tuple[str, str]:
    """
    Extract owner and repo name from GitHub URL.
    
    Returns: (owner, repo_name)
    """
    # Remove .git suffix if present
    url = url.rstrip('.git')
    
    # HTTPS format: https://github.com/owner/repo
    if 'github.com' in url:
        match = re.search(r'github\.com[:/]([^/]+)/([^/]+)', url)
        if match:
            return match.group(1), match.group(2)
    
    # Short format: owner/repo
    if '/' in url and 'github.com' not in url:
        parts = url.split('/')
        if len(parts) == 2:
            return parts[0], parts[1]
    
    raise ValueError(f"Invalid GitHub URL format: {url}")

# Example
owner, repo = parse_github_url("https://github.com/openshift/installer")
# Returns: ("openshift", "installer")
```

### Step 2: Check if Already Cloned

```python
from pathlib import Path

def get_clone_path(repo_name: str, target_dir: str = None) -> Path:
    """Get the path where repository should be cloned."""
    if target_dir:
        return Path(target_dir) / repo_name
    else:
        return Path("/tmp/agentic-repos") / repo_name

clone_path = get_clone_path(repo)

if clone_path.exists() and (clone_path / ".git").exists():
    print(f"✅ Repository already cloned at {clone_path}")
    return {
        "local_path": str(clone_path),
        "repository_name": repo,
        "owner": owner,
        "cloned": False
    }
```

### Step 3: Clone Repository

```python
import subprocess

def clone_repository(url: str, target_path: Path) -> bool:
    """
    Clone repository using git.
    
    Returns: True if successful, False otherwise
    """
    # Create parent directory
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Clone repository
    try:
        subprocess.run(
            ["git", "clone", url, str(target_path)],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Cloned {url} to {target_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to clone: {e.stderr}")
        return False

# Construct full GitHub URL
full_url = f"https://github.com/{owner}/{repo}.git"

# Clone
success = clone_repository(full_url, clone_path)

if not success:
    raise RuntimeError(f"Failed to clone {full_url}")
```

### Step 4: Return Local Path

```python
return {
    "local_path": str(clone_path),
    "repository_name": repo,
    "owner": owner,
    "cloned": True,
    "git_url": full_url
}
```

## Output Schema

```yaml
local_path: string              # Absolute path to cloned repository
repository_name: string         # Repository name (e.g., "installer")
owner: string                   # Repository owner (e.g., "openshift")
cloned: boolean                 # True if newly cloned, False if already existed
git_url: string                 # Full GitHub URL used for cloning
```

## Example Output

```yaml
local_path: /tmp/agentic-repos/installer
repository_name: installer
owner: openshift
cloned: true
git_url: https://github.com/openshift/installer.git
```

## Error Handling

### Invalid URL Format

```python
# Input: "not-a-url"
# Error: ValueError("Invalid GitHub URL format: not-a-url")
```

### Clone Failure

```python
# Repository doesn't exist
# Error: RuntimeError("Failed to clone https://github.com/owner/nonexistent.git")
```

### Network Issues

```python
# No network connection
# Error: RuntimeError("Failed to clone: Could not resolve host: github.com")
```

## Integration with Other Skills

This skill is called automatically by user-facing skills:

```python
# In /create skill
if is_github_url(user_input):
    result = clone_github_repository(user_input)
    repository_path = result["local_path"]
else:
    repository_path = user_input or os.getcwd()

# Continue with documentation generation
create_agentic_docs(repository_path)
```

## Usage Examples

### Example 1: Clone OpenShift Installer

```python
result = clone_github_repository("https://github.com/openshift/installer")

# Output:
# {
#   "local_path": "/tmp/agentic-repos/installer",
#   "repository_name": "installer",
#   "owner": "openshift",
#   "cloned": True,
#   "git_url": "https://github.com/openshift/installer.git"
# }
```

### Example 2: Check Already Cloned

```python
# First call - clones
result1 = clone_github_repository("openshift/installer")
# cloned: True

# Second call - already exists
result2 = clone_github_repository("openshift/installer")
# cloned: False, local_path: same path
```

### Example 3: Short Format

```python
result = clone_github_repository("openshift/installer")
# Expands to: https://github.com/openshift/installer.git
```

## Clone Location

**Default**: `/tmp/agentic-repos/<repo-name>/`

**Rationale**:
- Temporary location for processing
- Cleaned up automatically on system restart
- Doesn't clutter user's workspace
- Predictable location for all auto-cloned repos

**Structure**:
```
/tmp/agentic-repos/
├── installer/
│   ├── AGENTS.md                # Generated by /create
│   └── agentic/
├── multiarch-tuning-operator/
│   ├── AGENTS.md
│   └── agentic/
└── api/
    ├── AGENTS.md
    └── agentic/
```

## Advanced: Custom Clone Location

```python
result = clone_github_repository(
    "openshift/installer",
    target_directory="/custom/path"
)

# Clones to: /custom/path/installer/
```

## Related Skills

- `create-agentic-docs` - Uses this to clone repos from URLs
- `validate-agentic-docs` - Uses this to validate remote repos
- `ask-agentic-docs` - Uses this to query remote repos
- `evaluate-agentic-docs` - Uses this to evaluate remote repos
