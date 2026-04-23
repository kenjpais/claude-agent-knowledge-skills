# GitHub MCP Server Integration

## Overview
Integrates GitHub MCP server for efficient extraction of GitHub data including PRs, issues, commits, and code reviews. Essential for understanding development activity and extracting architectural decisions from GitHub history.

## Setup

### 1. Install GitHub MCP Server
```bash
# Install via npm
npm install -g @modelcontextprotocol/server-github

# Or using the MCP CLI
mcp install github
```

### 2. Configure Authentication
```bash
# Create GitHub personal access token
# Required scopes: repo, read:org

# Set token in environment
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxx

# Or configure in Claude Code settings
claude config set github.token $GITHUB_TOKEN
```

### 3. Add to Claude Code MCP Servers
Edit `~/.claude/mcp_servers.json`:
```json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_TOKEN": "${GITHUB_TOKEN}"
    }
  }
}
```

## Available Tools

### Repository Information
- `github_get_repo` - Get repository metadata
- `github_list_repos` - List repositories for user/org
- `github_search_repos` - Search repositories

### Issues and Pull Requests
- `github_list_issues` - List issues with filters
- `github_get_issue` - Get specific issue details
- `github_create_issue` - Create new issue
- `github_list_pulls` - List pull requests
- `github_get_pull` - Get PR details
- `github_get_pull_diff` - Get PR diff
- `github_list_pull_commits` - Get PR commits
- `github_list_pull_reviews` - Get PR reviews

### Commits and Files
- `github_get_commit` - Get commit details
- `github_list_commits` - List commits with filters
- `github_get_file_contents` - Read file from repo
- `github_search_code` - Search code in repository

### Releases and Tags
- `github_list_releases` - List repository releases
- `github_get_release` - Get specific release

## Usage in Documentation Generation

### Extraction Phase: Mining GitHub Data

#### 1. Extract Architectural Decisions from PRs
Use PR descriptions and reviews to identify architectural decisions:

```python
# Pseudo-code for skill usage
prs = github_list_pulls(
    owner="openshift",
    repo="machine-api-operator",
    state="closed",
    sort="created",
    direction="desc",
    per_page=100
)

# Filter PRs with architectural significance
arch_prs = [
    pr for pr in prs
    if any(keyword in pr.title.lower() for keyword in [
        "architecture", "design", "refactor", "breaking change"
    ])
]

# Extract decision context from PR description and reviews
for pr in arch_prs:
    reviews = github_list_pull_reviews(owner, repo, pr.number)
    # Generate ADR from PR data
```

#### 2. Identify Component Ownership
Use commit history and PR authorship:

```python
# Get commits for specific directory/component
commits = github_list_commits(
    owner="openshift",
    repo="machine-api-operator",
    path="pkg/controller/machine",
    since="2024-01-01"
)

# Identify primary contributors
contributors = analyze_contributors(commits)
# Use for component ownership documentation
```

#### 3. Extract Bug Patterns from Issues
Analyze issue patterns to document common failure modes:

```python
# Get closed bugs
bugs = github_list_issues(
    owner="openshift",
    repo="machine-api-operator",
    labels="kind/bug",
    state="closed",
    per_page=100
)

# Categorize by component and failure type
failure_modes = categorize_bugs(bugs)
# Use for RELIABILITY.md documentation
```

#### 4. Track Feature Development
Map features to PRs for understanding evolution:

```python
# Search for feature PRs
feature_prs = github_search_code(
    q="type:pr label:kind/feature repo:openshift/machine-api-operator"
)

# Build feature timeline
timeline = build_feature_timeline(feature_prs)
# Use for product specs and context
```

## Integration Points

### Orchestrator Agent
Use GitHub MCP to determine documentation scope:

```yaml
orchestrator_github_usage:
  - Check recent activity via github_list_commits
  - Identify changed components for incremental updates
  - Determine if major refactor occurred (trigger full regeneration)
```

### Extractor Agent
Enhance extraction with GitHub metadata:

```yaml
extractor_github_usage:
  - get_git_history skill enhanced with github_get_commit for rich metadata
  - Extract PR context for architectural decisions
  - Identify code ownership from commit history
```

### Synthesizer Agent
Use GitHub data for context:

```yaml
synthesizer_github_usage:
  - Reference PR numbers in generated ADRs
  - Include contributor information in component docs
  - Document known issues and workarounds from GitHub issues
```

### Curator Agent
Monitor GitHub for documentation triggers:

```yaml
curator_github_usage:
  - Poll github_list_commits for new changes
  - Detect breaking changes from PR labels
  - Trigger incremental updates on merge
```

## Data Extraction Patterns

### Pattern 1: ADR Generation from PRs
```
1. Query: github_list_pulls with label:architecture
2. For each PR:
   - Get description via github_get_pull
   - Get reviews via github_list_pull_reviews
   - Get diff via github_get_pull_diff
3. Synthesize into ADR:
   - Context: PR description
   - Decision: What was merged
   - Consequences: Review comments and concerns
   - Status: Accepted (merged) or Rejected (closed)
```

### Pattern 2: Component Activity Analysis
```
1. For each component directory:
   - Query: github_list_commits with path filter
   - Calculate commit frequency
   - Identify active vs stale components
2. Use for documentation prioritization:
   - High activity → Higher priority docs
   - Stale → Lower priority or archive candidate
```

### Pattern 3: Issue-Driven Documentation
```
1. Query: github_list_issues with label filters
2. Group by component (parse file paths from issue body)
3. For each component:
   - Extract common failure modes
   - Document troubleshooting steps from issue resolutions
   - Add to RELIABILITY.md
```

## Rate Limiting

GitHub API has rate limits:
- Authenticated: 5,000 requests/hour
- Unauthenticated: 60 requests/hour

**Best Practices**:
- Always use authentication
- Cache responses where possible
- Use conditional requests (ETags)
- Batch requests when possible

## Error Handling

```python
try:
    pr = github_get_pull(owner, repo, number)
except GitHubAPIError as e:
    if e.status_code == 404:
        logger.log_warning("get_pull", f"PR #{number}", "PR not found")
    elif e.status_code == 403:
        logger.log_error("get_pull", f"PR #{number}", "Rate limit exceeded")
        # Wait and retry
    else:
        raise
```

## Monitoring

Log all GitHub API calls:
```json
{
  "timestamp": "...",
  "agent_id": "extractor",
  "operation": "github_list_pulls",
  "resource": "openshift/machine-api-operator",
  "status": "success",
  "metadata": {
    "pulls_fetched": 50,
    "rate_limit_remaining": 4950
  }
}
```

## Security

**DO**:
- Use personal access tokens with minimal required scopes
- Store tokens in environment variables or secure vaults
- Rotate tokens regularly
- Use read-only tokens for documentation generation

**DON'T**:
- Commit tokens to repository
- Use tokens with write permissions unless necessary
- Share tokens between services

## Example: Complete GitHub Data Extraction

```python
from utilities.logging.logger import get_logger

logger = get_logger("extractor")

def extract_github_data(owner: str, repo: str):
    """Extract comprehensive GitHub data for documentation."""
    
    logger.log_start("extract_github_data", f"{owner}/{repo}")
    
    # Get repository info
    repo_info = github_get_repo(owner=owner, repo=repo)
    
    # Get recent activity
    recent_commits = github_list_commits(
        owner=owner,
        repo=repo,
        since="3 months ago",
        per_page=100
    )
    
    # Get architectural PRs
    arch_prs = github_list_pulls(
        owner=owner,
        repo=repo,
        state="closed",
        labels="architecture,refactor",
        per_page=50
    )
    
    # Get bug patterns
    bugs = github_list_issues(
        owner=owner,
        repo=repo,
        labels="kind/bug",
        state="closed",
        per_page=100
    )
    
    logger.log_success(
        "extract_github_data",
        f"{owner}/{repo}",
        metadata={
            "commits": len(recent_commits),
            "arch_prs": len(arch_prs),
            "bugs": len(bugs)
        }
    )
    
    return {
        "repo_info": repo_info,
        "commits": recent_commits,
        "architectural_prs": arch_prs,
        "bugs": bugs
    }
```

## References
- GitHub MCP Server: https://github.com/modelcontextprotocol/servers/tree/main/src/github
- GitHub API Documentation: https://docs.github.com/rest
- MCP Protocol: https://modelcontextprotocol.io
