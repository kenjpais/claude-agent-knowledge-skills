# Simplified JIRA Integration

## Public JIRA Access (No Authentication Required!) ✅

For **public JIRA instances** like Red Hat's issues.redhat.com, **NO authentication is required**. The system can access public issues directly via REST API.

### Quick Start - Public JIRA

```python
from integrations.jira.public_jira_client import PublicJiraClient

# Initialize client (defaults to Red Hat JIRA)
client = PublicJiraClient()

# Or specify another public JIRA instance
client = PublicJiraClient("https://issues.apache.org")

# Search for issues
issues = client.search_issues(
    jql='project = OCPCLOUD AND type = Feature AND status = Done',
    fields=['summary', 'description', 'labels'],
    max_results=50
)

# Get specific issue
issue = client.get_issue('OCPCLOUD-1234')

# Get issue comments
comments = client.get_issue_comments('OCPCLOUD-1234')
```

### Supported Public JIRA Instances

✅ **Works out of the box** (no auth):
- https://issues.redhat.com (Red Hat)
- https://issues.apache.org (Apache)
- https://jira.mongodb.org (MongoDB)
- Any public JIRA instance with open issue access

### What You Can Access

With public JIRA access:
- ✅ Search issues with JQL
- ✅ Get issue details
- ✅ Read issue comments
- ✅ Get project information
- ✅ Read custom fields
- ❌ Create/update issues (read-only)
- ❌ Access private projects

This is **perfect** for documentation generation since we only need to READ issue data!

---

## Private JIRA Setup (Optional)

Only needed if accessing **private JIRA instances** or **private projects**.

### Environment Variables

```bash
export JIRA_URL=https://your-company.atlassian.net
export JIRA_EMAIL=your-email@company.com
export JIRA_API_TOKEN=your-api-token
```

### Get API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy token and set as `JIRA_API_TOKEN`

### Usage with Authentication

```python
import os
from jira import JIRA

# For private JIRA instances
jira = JIRA(
    server=os.getenv('JIRA_URL'),
    basic_auth=(os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN'))
)

# Now you can access private projects
issues = jira.search_issues('project = PRIVATE AND type = Bug')
```

---

## Integration with Agent Knowledge System

### Extractor Agent Usage

The extractor agent automatically detects and uses the appropriate JIRA client:

```python
# In extractor agent
if os.getenv('JIRA_API_TOKEN'):
    # Use authenticated client for private JIRA
    from jira import JIRA
    client = JIRA(...)
else:
    # Use public client (no auth)
    from integrations.jira.public_jira_client import PublicJiraClient
    client = PublicJiraClient()

# Extract features
features = client.search_issues(
    jql='project = OCPCLOUD AND type = Feature AND status = Done',
    fields=['summary', 'description', 'acceptance_criteria']
)
```

### Common JQL Queries for Documentation

```python
# Get features for a component
features = client.search_issues(
    jql='project = OCPCLOUD AND type = Feature AND component = "Machine API"',
    max_results=100
)

# Get recent bugs for reliability docs
bugs = client.search_issues(
    jql='project = OCPCLOUD AND type = Bug AND created >= -180d',
    fields=['summary', 'priority', 'resolution', 'labels']
)

# Get epics for design context
epics = client.search_issues(
    jql='project = OCPCLOUD AND type = Epic',
    fields=['summary', 'description', 'labels']
)
```

---

## Rate Limits

### Public JIRA
- No explicit rate limits for read operations
- Recommended: Max 100 requests/minute
- Use `maxResults` parameter to limit response size

### Private JIRA (Atlassian Cloud)
- Standard: ~100 requests/minute
- Premium: ~1000 requests/minute
- Implement backoff if you hit 429 responses

---

## Example: Extract Feature Specifications

```python
#!/usr/bin/env python3
"""Extract feature specifications from JIRA for documentation."""

from integrations.jira.public_jira_client import PublicJiraClient

def extract_feature_specs(project_key: str, component: str = None):
    """Extract feature specs for agentic documentation."""
    
    client = PublicJiraClient()
    
    # Build JQL query
    jql = f'project = {project_key} AND type = Feature AND status = Done'
    if component:
        jql += f' AND component = "{component}"'
    
    # Search for features
    features = client.search_issues(
        jql=jql,
        fields=['summary', 'description', 'labels', 'customfield_12345'],  # acceptance criteria
        max_results=50
    )
    
    # Process into documentation format
    feature_docs = []
    for feature in features:
        doc = {
            'jira_key': feature['key'],
            'title': feature['fields']['summary'],
            'description': feature['fields'].get('description', ''),
            'labels': feature['fields'].get('labels', []),
            'url': f"https://issues.redhat.com/browse/{feature['key']}"
        }
        feature_docs.append(doc)
    
    return feature_docs

# Usage
specs = extract_feature_specs('OCPCLOUD', 'Machine API')
print(f"Extracted {len(specs)} feature specifications")
```

---

## Comparison: Public vs Private

| Feature | Public JIRA | Private JIRA |
|---------|-------------|--------------|
| Authentication | ❌ None needed | ✅ API token required |
| Read Issues | ✅ Yes | ✅ Yes |
| Search (JQL) | ✅ Yes | ✅ Yes |
| Comments | ✅ Yes | ✅ Yes |
| Private Projects | ❌ No | ✅ Yes |
| Create/Update | ❌ No | ✅ Yes |
| Rate Limits | Relaxed | Stricter |
| Setup Time | 0 minutes | 5 minutes |

**For documentation generation**: Public access is sufficient! We only need to READ issue data.

---

## Troubleshooting

### "Connection refused" error
- **Cause**: JIRA URL incorrect or instance down
- **Fix**: Verify JIRA instance URL is correct and accessible

### "Issue not found" error
- **Cause**: Issue is private or doesn't exist
- **Fix**: Check issue key and project permissions

### Empty results from search
- **Cause**: JQL query too restrictive or no matching issues
- **Fix**: Simplify JQL, check project key is correct

### Slow responses
- **Cause**: Large result sets
- **Fix**: Use pagination, limit fields, reduce `maxResults`

---

## Summary

✅ **For OpenShift/Red Hat projects**: No JIRA setup needed!  
✅ **Public JIRA access**: Works out of the box  
✅ **Documentation generation**: Read-only access is sufficient  
⚙️ **Private JIRA**: Optional, 5-minute setup if needed  

The simplified approach makes it easy to get started without any authentication complexity for public JIRA instances.
