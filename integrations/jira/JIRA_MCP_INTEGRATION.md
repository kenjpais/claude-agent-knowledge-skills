# JIRA MCP Server Integration

## Overview
Integrates JIRA MCP server for efficient extraction of issue tracking data, sprint information, and requirement specifications. Essential for understanding feature context and linking documentation to product requirements.

## Setup

### 1. Install JIRA MCP Server
```bash
# Check if JIRA MCP server is available
mcp list-servers | grep jira

# Install if available
mcp install jira
```

**Note**: As of April 2026, check the MCP server registry for JIRA server availability. If not available, use JIRA REST API directly.

### 2. Configure Authentication
```bash
# Set JIRA credentials
export JIRA_URL=https://issues.redhat.com
export JIRA_EMAIL=your-email@redhat.com
export JIRA_API_TOKEN=your-api-token

# Or use OAuth (preferred for production)
export JIRA_OAUTH_TOKEN=your-oauth-token
```

### 3. Add to Claude Code MCP Servers
Edit `~/.claude/mcp_servers.json`:
```json
{
  "jira": {
    "command": "npx",
    "args": ["-y", "@your-org/mcp-server-jira"],
    "env": {
      "JIRA_URL": "${JIRA_URL}",
      "JIRA_EMAIL": "${JIRA_EMAIL}",
      "JIRA_API_TOKEN": "${JIRA_API_TOKEN}"
    }
  }
}
```

## Available Operations (via JIRA REST API)

### Issues
- `jira_get_issue` - Get issue details by key
- `jira_search_issues` - Search issues with JQL
- `jira_list_issue_comments` - Get issue comments
- `jira_get_issue_changelog` - Get issue history

### Projects and Boards
- `jira_get_project` - Get project information
- `jira_list_boards` - List available boards
- `jira_get_board_issues` - Get issues for board

### Sprints and Versions
- `jira_list_sprints` - List sprints for board
- `jira_get_sprint` - Get sprint details
- `jira_list_versions` - List project versions

### Metadata
- `jira_get_issue_types` - Get available issue types
- `jira_get_priorities` - Get priority levels
- `jira_get_statuses` - Get workflow statuses

## Usage in Documentation Generation

### Extraction Phase: Mining JIRA Data

#### 1. Link Features to Requirements
Map implemented features to JIRA issues:

```python
# Search for feature issues
features = jira_search_issues(
    jql="project = OCPCLOUD AND type = Feature AND status = Done",
    fields=["summary", "description", "components", "labels"],
    max_results=100
)

# For each feature, extract:
for feature in features:
    feature_spec = {
        "jira_key": feature.key,
        "title": feature.summary,
        "description": feature.description,
        "components": feature.components,
        "acceptance_criteria": extract_acceptance_criteria(feature)
    }
    # Generate product spec doc
```

#### 2. Extract Bug Patterns
Analyze bug trends for reliability documentation:

```python
# Search for bugs by component
bugs = jira_search_issues(
    jql="project = OCPCLOUD AND type = Bug AND component = 'Machine API'",
    fields=["summary", "priority", "resolution", "labels"],
    max_results=500
)

# Categorize bugs
bug_categories = categorize_by_labels_and_summary(bugs)

# Extract patterns for RELIABILITY.md:
# - Common failure modes
# - High-priority recurring issues
# - Component reliability metrics
```

#### 3. Map Sprints to Releases
Track feature development timeline:

```python
# Get sprint information
sprints = jira_list_sprints(board_id=BOARD_ID)

for sprint in sprints:
    sprint_issues = jira_get_board_issues(
        board_id=BOARD_ID,
        sprint_id=sprint.id
    )
    # Map completed issues to release notes
    # Use for understanding feature evolution
```

#### 4. Extract Design Context from Epics
Use epic descriptions for architectural context:

```python
# Get epics for project
epics = jira_search_issues(
    jql="project = OCPCLOUD AND type = Epic",
    fields=["summary", "description", "labels", "customfield_epic_link"]
)

for epic in epics:
    # Epic descriptions often contain design rationale
    # Use to seed domain/concepts/ documentation
    # Link to relevant ADRs
```

## Integration Points

### Orchestrator Agent
Use JIRA to prioritize documentation scope:

```yaml
orchestrator_jira_usage:
  - Query active sprints to prioritize current work
  - Check recent bug activity to identify high-priority components
  - Align documentation generation with release milestones
```

### Extractor Agent
Enrich extraction with JIRA metadata:

```yaml
extractor_jira_usage:
  - Extract feature requirements from JIRA issues
  - Link code components to JIRA components
  - Identify test coverage gaps from JIRA test issues
```

### Synthesizer Agent
Use JIRA data for context:

```yaml
synthesizer_jira_usage:
  - Reference JIRA keys in component docs
  - Document acceptance criteria from features
  - Include known issues from JIRA in RELIABILITY.md
```

### Curator Agent
Monitor JIRA for documentation triggers:

```yaml
curator_jira_usage:
  - Watch for new features (trigger doc updates)
  - Monitor bug trends (update reliability docs)
  - Track deprecation labels (update security/compliance docs)
```

## Data Extraction Patterns

### Pattern 1: Feature Specification Generation
```
1. Query: jira_search_issues for type=Feature, status=Done
2. For each feature:
   - Get description and acceptance criteria
   - Get linked issues (dependencies, blockers)
   - Get comments for additional context
3. Generate product spec:
   - agentic/product-specs/{jira-key}-{feature-name}.md
   - Include JIRA link, description, acceptance criteria
   - Link to implementing components
```

### Pattern 2: Reliability Metrics from Bugs
```
1. Query: jira_search_issues for type=Bug, resolved in last 6 months
2. Group by:
   - Component
   - Priority
   - Root cause labels
3. Calculate metrics:
   - Bug rate per component
   - MTTR (mean time to resolution)
   - Recurring issues
4. Document in RELIABILITY.md:
   - Known issues
   - Reliability SLOs
   - Troubleshooting guides
```

### Pattern 3: Compliance Tracking
```
1. Query: jira_search_issues for labels=security,compliance
2. Extract:
   - Security requirements from issues
   - Compliance obligations
   - Audit trails
3. Document in SECURITY.md:
   - Required security controls
   - Compliance status
   - Audit references
```

## JQL Query Examples

### Find Features for Component
```
project = OCPCLOUD AND 
type = Feature AND 
component = "Machine API" AND 
status = Done
ORDER BY created DESC
```

### Find High-Priority Bugs
```
project = OCPCLOUD AND 
type = Bug AND 
priority IN (Critical, High) AND 
status NOT IN (Resolved, Closed)
ORDER BY priority DESC, created ASC
```

### Find Documentation Issues
```
project = OCPCLOUD AND 
labels = documentation AND 
status = Open
```

### Find Deprecation Notices
```
project = OCPCLOUD AND 
labels = deprecated AND 
(status = Open OR resolved >= -90d)
```

## Rate Limiting

JIRA Cloud rate limits:
- Standard: ~100 requests per minute per user
- Premium: ~1000 requests per minute per user

**Best Practices**:
- Use pagination for large result sets
- Cache responses when possible
- Use JQL to filter server-side instead of client-side
- Batch related queries

## Error Handling

```python
from utilities.logging.logger import get_logger

logger = get_logger("extractor")

try:
    issues = jira_search_issues(jql=query, max_results=100)
except JIRAAPIError as e:
    if e.status_code == 400:
        logger.log_error("jira_search", query, f"Invalid JQL: {e.message}")
    elif e.status_code == 429:
        logger.log_warning("jira_search", query, "Rate limit hit, retrying...")
        # Implement backoff and retry
    else:
        logger.log_error("jira_search", query, str(e))
        raise
```

## Monitoring

Log all JIRA API calls:
```json
{
  "timestamp": "...",
  "agent_id": "extractor",
  "operation": "jira_search_issues",
  "resource": "project=OCPCLOUD",
  "status": "success",
  "metadata": {
    "issues_fetched": 45,
    "jql": "type=Feature AND status=Done",
    "rate_limit_remaining": 95
  }
}
```

## Security

**DO**:
- Use API tokens instead of passwords
- Store credentials in environment variables or vaults
- Use service accounts with minimal permissions
- Audit API token usage

**DON'T**:
- Commit credentials to repository
- Use personal accounts for automation
- Grant unnecessary permissions
- Share API tokens

## Example: Complete JIRA Data Extraction

```python
from utilities.logging.logger import get_logger

logger = get_logger("extractor")

def extract_jira_data(project_key: str, component_name: str):
    """Extract comprehensive JIRA data for documentation."""
    
    logger.log_start("extract_jira_data", f"{project_key}/{component_name}")
    
    # Get features
    features = jira_search_issues(
        jql=f'project = {project_key} AND type = Feature AND component = "{component_name}" AND status = Done',
        fields=["summary", "description", "labels", "customfield_acceptance_criteria"],
        max_results=50
    )
    
    # Get bugs
    bugs = jira_search_issues(
        jql=f'project = {project_key} AND type = Bug AND component = "{component_name}"',
        fields=["summary", "priority", "status", "resolution", "created", "resolved"],
        max_results=200
    )
    
    # Get epics for context
    epics = jira_search_issues(
        jql=f'project = {project_key} AND type = Epic AND component = "{component_name}"',
        fields=["summary", "description", "labels"],
        max_results=20
    )
    
    logger.log_success(
        "extract_jira_data",
        f"{project_key}/{component_name}",
        metadata={
            "features": len(features),
            "bugs": len(bugs),
            "epics": len(epics)
        }
    )
    
    return {
        "features": features,
        "bugs": bugs,
        "epics": epics
    }
```

## Integration with GitHub

Combine JIRA and GitHub data for comprehensive context:

```python
def cross_reference_jira_github(jira_key: str, github_owner: str, github_repo: str):
    """Find GitHub PRs and commits referencing JIRA issue."""
    
    # Search GitHub for JIRA key
    prs = github_search_code(
        q=f'{jira_key} type:pr repo:{github_owner}/{github_repo}'
    )
    
    commits = github_search_code(
        q=f'{jira_key} type:commit repo:{github_owner}/{github_repo}'
    )
    
    # Get JIRA issue details
    issue = jira_get_issue(jira_key)
    
    return {
        "jira_issue": issue,
        "related_prs": prs,
        "related_commits": commits
    }
```

## References
- JIRA REST API Documentation: https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- JQL Reference: https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/
- MCP Protocol: https://modelcontextprotocol.io
