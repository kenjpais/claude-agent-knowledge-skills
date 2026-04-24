---
skill_id: ingest-github-data
name: Ingest GitHub Data
category: data-ingestion
version: 1.0.0
description: Ingest GitHub repository PRs, issues, and JIRA references into SQLite database
inputs: [repository_url, since_date, until_date, pr_limit, issue_limit]
outputs: [database_path, statistics]
---

# Ingest GitHub Data

**Purpose**: Ingest GitHub PRs, issues, and linked JIRA references into local SQLite database for analysis

## Input Schema

```yaml
repository_url: string      # GitHub URL (e.g., https://github.com/openshift/installer)
since_date: string          # Start date (YYYY-MM-DD or "N-days-ago", default: 365-days-ago)
until_date: string          # End date (YYYY-MM-DD, default: today)
pr_limit: integer           # Max PRs to fetch (default: 1000)
issue_limit: integer        # Max issues to fetch (default: 1000)
jira_project: string        # Optional JIRA project key (e.g., OCPCLOUD)
```

## Output Schema

```yaml
database_path: string       # Path to SQLite database
statistics:
  github_prs: integer      # Number of PRs ingested
  github_issues: integer   # Number of issues ingested
  jira_issues: integer     # Number of JIRA issues fetched
  correlations: integer    # Number of GitHub ↔ JIRA correlations
```

## Implementation

Uses: `integrations/storage/ingest.py`

```bash
python integrations/storage/ingest.py <owner/repo> \
  --since <date> \
  --until <date> \
  --prs <limit> \
  --issues <limit> \
  --jira <project>
```

## Success Criteria

- ✅ Database created at ~/.agent-knowledge/data.db
- ✅ PRs and issues ingested within date range
- ✅ JIRA references extracted and correlated
- ✅ Statistics returned

## Example

```yaml
Input:
  repository_url: https://github.com/openshift/installer
  since_date: 90-days-ago
  pr_limit: 100
  issue_limit: 100
  jira_project: OCPCLOUD

Output:
  database_path: /Users/user/.agent-knowledge/data.db
  statistics:
    github_prs: 87
    github_issues: 95
    jira_issues: 12
    correlations: 45
```

## Related Skills

- `generate-knowledge-graph` - Next step: convert DB to knowledge graph
- `retrieve-from-graph` - Query the ingested data
