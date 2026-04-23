# Single Repository Ingestion with GitHub GraphQL API

This document describes the focused single-repository ingestion system using GitHub's GraphQL API with date range filtering.

---

## 🎯 Scope

**✅ Supported**: Single repository ingestion
- GitHub PRs and issues within a date range
- JIRA issues referenced in GitHub data
- Default date range: **Past 1 year**

**❌ Not Supported**: Multi-repository batch ingestion
- No discovery across multiple repos
- No parallel processing of repo lists
- No incremental updates across repos

---

## 🚀 Quick Start

### Basic Usage (Last Year)

```bash
# Ingest last year of data from a single repository
python integrations/storage/ingest.py openshift/installer --jira OCPCLOUD
```

This will:
1. Fetch all PRs created in the last 365 days
2. Fetch all issues created in the last 365 days
3. Extract JIRA references from PR/issue titles and bodies
4. Fetch referenced JIRA issues
5. Optionally fetch full JIRA project data
6. Store everything in `~/.agent-knowledge/data.db`

---

## 📅 Date Range Options

### Relative Dates

```bash
# Last 30 days
python ingest.py openshift/installer --since 30-days-ago

# Last 90 days
python ingest.py openshift/installer --since 90-days-ago --jira OCPCLOUD

# Last 180 days
python ingest.py openshift/installer --since 180-days-ago
```

### Specific Dates

```bash
# Specific year
python ingest.py openshift/installer \
  --since 2024-01-01 \
  --until 2024-12-31 \
  --jira OCPCLOUD

# Q1 2024
python ingest.py openshift/installer \
  --since 2024-01-01 \
  --until 2024-03-31

# Specific month
python ingest.py openshift/installer \
  --since 2024-06-01 \
  --until 2024-06-30
```

---

## 🔧 GitHub GraphQL API

### Why GraphQL Instead of REST?

**GraphQL Advantages**:
- ✅ **Efficient**: Only fetch needed fields
- ✅ **Fast**: Single request can fetch nested data
- ✅ **Pagination**: Cursor-based, handles large datasets
- ✅ **Flexible**: Easy to add/remove fields
- ✅ **Typed**: Built-in schema validation

**vs REST API**:
- ❌ REST: Multiple requests for related data
- ❌ REST: Over-fetching (get all fields, use few)
- ❌ REST: Page-based pagination (can miss items)
- ❌ REST: More API calls = slower, more rate limit usage

### Example GraphQL Query

```graphql
query($owner: String!, $repo: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequests(first: 100, after: $cursor, orderBy: {field: CREATED_AT, direction: DESC}) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        number
        title
        body
        state
        createdAt
        author { login }
        labels(first: 20) {
          nodes { name }
        }
      }
    }
  }
}
```

This single query fetches:
- PRs with pagination
- PR metadata (number, title, state, etc.)
- Author information
- Labels (up to 20)

In REST API, this would require:
1. GET `/repos/{owner}/{repo}/pulls` - Get PRs
2. For each PR: GET `/repos/{owner}/{repo}/pulls/{number}` - Get details
3. For each PR: GET `/repos/{owner}/{repo}/pulls/{number}/labels` - Get labels
= **1 + 2N requests** (vs 1 GraphQL request)

---

## 📊 Use Cases

### 1. Recent Development Activity

```bash
# Analyze last 30 days
python ingest.py openshift/installer --since 30-days-ago --jira OCPCLOUD

# Query recent PRs
python -c "
from integrations.storage.database import KnowledgeDatabase
db = KnowledgeDatabase()
prs = db.get_prs_with_jira(limit=20)
for pr in prs:
    print(f'PR #{pr[\"number\"]}: {pr[\"title\"]} - {pr[\"jira_keys\"]}')
"
```

### 2. Historical Analysis

```bash
# Analyze specific year
python ingest.py openshift/installer \
  --since 2023-01-01 \
  --until 2023-12-31 \
  --jira OCPCLOUD

# Query by date
python -c "
from integrations.storage.database import KnowledgeDatabase
db = KnowledgeDatabase()
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) as count, strftime('%Y-%m', created_at) as month
        FROM github_pull_requests
        WHERE created_at >= '2023-01-01' AND created_at < '2024-01-01'
        GROUP BY month
        ORDER BY month
    ''')
    for row in cursor.fetchall():
        print(f'{row[1]}: {row[0]} PRs')
"
```

### 3. Feature Tracking

```bash
# Ingest last quarter
python ingest.py openshift/installer --since 90-days-ago --jira OCPCLOUD

# Track features with PRs
python -c "
from integrations.storage.database import KnowledgeDatabase
db = KnowledgeDatabase()
issues = db.get_jira_issues_with_github(project_key='OCPCLOUD')
for issue in issues:
    if issue['pr_count'] > 0:
        print(f\"{issue['key']}: {issue['summary']}\")
        print(f\"  PRs: {issue['pr_numbers']} ({issue['pr_count']} total)\")
"
```

### 4. Documentation Generation

```bash
# Ingest last 6 months
python ingest.py openshift/installer --since 180-days-ago --jira OCPCLOUD

# Generate component docs from recent activity
python -c "
from integrations.storage.database import KnowledgeDatabase
db = KnowledgeDatabase()

# Get architectural PRs from last 6 months
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('''
        SELECT pr.*, GROUP_CONCAT(ref.jira_issue_key) as jira_keys
        FROM github_pull_requests pr
        LEFT JOIN github_jira_references ref ON ref.github_pr_id = pr.pr_id
        WHERE pr.labels LIKE '%architecture%'
        AND pr.created_at >= date('now', '-180 days')
        GROUP BY pr.pr_id
        ORDER BY pr.created_at DESC
        LIMIT 10
    ''')
    
    for pr in cursor.fetchall():
        print(f'## {pr[3]}')  # title
        print(f'PR: #{pr[2]}')  # number
        print(f'JIRA: {pr[-1]}')  # jira_keys
        print()
"
```

---

## 🔍 How It Works

### 1. Repository Metadata

```python
# GitHubGraphQLIngester.ingest_repository()
# Fetches: name, description, stars, forks, language, etc.
```

### 2. Pull Requests with Date Filter

```python
# GitHubGraphQLIngester.ingest_pull_requests(since_date, until_date)
# 1. Fetch PRs ordered by created_at DESC
# 2. Stop when reaching PRs before since_date
# 3. Skip PRs after until_date
# 4. Extract JIRA references from title and body
# 5. Store in database
```

### 3. Issues with Date Filter

```python
# GitHubGraphQLIngester.ingest_issues(since_date, until_date)
# Same as PRs but for issues
```

### 4. JIRA Correlation

```python
# JiraIngester.ingest_referenced_issues()
# 1. Get unique JIRA keys from github_jira_references table
# 2. Fetch each JIRA issue (deduplicated)
# 3. Update correlations with JIRA issue IDs
```

### 5. Optional: Full JIRA Project

```python
# JiraIngester.ingest_features_and_bugs(project_key)
# Fetch all features and bugs from JIRA project
```

---

## 📈 Performance

### GraphQL API Efficiency

| Metric | REST API | GraphQL API | Improvement |
|--------|----------|-------------|-------------|
| Requests for 100 PRs | 101-201 | 1-2 | 50-100x fewer |
| Data transferred | ~5MB | ~500KB | 10x less |
| Time to fetch | ~30s | ~3s | 10x faster |
| Rate limit usage | 101-201 | 1-2 | 50-100x less |

### Date Range Impact

| Date Range | PRs | Issues | Time | DB Size |
|------------|-----|--------|------|---------|
| 30 days | ~50 | ~100 | 30s | ~1MB |
| 90 days | ~150 | ~300 | 1min | ~3MB |
| 180 days | ~300 | ~600 | 2min | ~6MB |
| 365 days | ~600 | ~1200 | 5min | ~12MB |

*Estimates for a moderately active repository*

---

## ⚙️ Configuration

### CLI Options

```bash
python ingest.py REPOSITORY [OPTIONS]

Required:
  REPOSITORY          GitHub repository (owner/repo)

Optional:
  --jira PROJECT      JIRA project key (e.g., OCPCLOUD)
  --since DATE        Start date (YYYY-MM-DD or N-days-ago)
                      Default: 365-days-ago
  --until DATE        End date (YYYY-MM-DD)
                      Default: today
  --prs N             Max PRs to fetch (default: 1000)
  --issues N          Max issues to fetch (default: 1000)
  --db PATH           Database path
                      Default: ~/.agent-knowledge/data.db
```

### Examples

```bash
# Minimal (last year, no JIRA project)
python ingest.py openshift/installer

# With JIRA project
python ingest.py openshift/installer --jira OCPCLOUD

# Custom date range
python ingest.py openshift/installer \
  --since 2024-01-01 \
  --until 2024-06-30 \
  --jira OCPCLOUD

# High limits (comprehensive)
python ingest.py openshift/installer \
  --since 180-days-ago \
  --prs 2000 \
  --issues 1000 \
  --jira OCPCLOUD

# Custom database
python ingest.py openshift/installer \
  --db /path/to/custom.db \
  --jira OCPCLOUD
```

---

## 🎯 Best Practices

### 1. Choose Appropriate Date Range

**For recent activity analysis**:
```bash
python ingest.py openshift/installer --since 30-days-ago
```

**For quarterly review**:
```bash
python ingest.py openshift/installer --since 90-days-ago
```

**For annual analysis**:
```bash
python ingest.py openshift/installer --since 365-days-ago
```

**For historical research**:
```bash
python ingest.py openshift/installer \
  --since 2023-01-01 \
  --until 2023-12-31
```

### 2. Re-ingest Periodically

```bash
# Monthly: Get last 30-60 days
# This captures recent activity without re-ingesting everything
python ingest.py openshift/installer --since 60-days-ago
```

### 3. Optimize Limits

**Quick overview**:
```bash
python ingest.py openshift/installer --prs 100 --issues 50
```

**Comprehensive analysis**:
```bash
python ingest.py openshift/installer --prs 2000 --issues 1000
```

### 4. Backup Before Large Ingestion

```bash
# Backup database
cp ~/.agent-knowledge/data.db ~/.agent-knowledge/data.db.backup

# Run ingestion
python ingest.py openshift/installer --since 365-days-ago
```

---

## 🔒 Security & Privacy

### Data Privacy
- ✅ All data stored locally in SQLite
- ✅ No cloud sync or external services
- ✅ Read-only API access (no write operations)

### API Authentication
- GitHub: Optional `GITHUB_TOKEN` for higher rate limits
- JIRA: Not required for public instances (issues.redhat.com)

### Rate Limits
- **Without token**: 60 requests/hour
- **With token**: 5,000 requests/hour
- **GraphQL**: Counts as 1 request per query (vs multiple in REST)

---

## 🆘 Troubleshooting

### "gh: command not found"
```bash
# Install GitHub CLI
# macOS
brew install gh

# Linux
# See https://cli.github.com/manual/installation
```

### "Rate limit exceeded"
```bash
# Set GitHub token
export GITHUB_TOKEN=ghp_your_token_here
```

### "Database locked"
```bash
# Close other connections
# Or enable WAL mode
sqlite3 ~/.agent-knowledge/data.db "PRAGMA journal_mode=WAL;"
```

### GraphQL Errors
```bash
# Check authentication
gh auth status

# Verify repository access
gh repo view openshift/installer
```

---

## 📚 Further Reading

- **README.md** - Complete documentation with examples
- **schema.sql** - Database schema details
- **database.py** - Python API for querying data
- **ingest_github.py** - GraphQL implementation details
- **ingest_jira.py** - JIRA ingestion implementation

---

## Summary

This system provides **efficient single-repository ingestion** using:

✅ **GitHub GraphQL API** - 50-100x fewer requests than REST  
✅ **Date range filtering** - Focus on relevant time periods  
✅ **Automatic JIRA correlation** - Link PRs to JIRA issues  
✅ **Local SQLite storage** - Fast queries, no external dependencies  
✅ **Flexible date formats** - YYYY-MM-DD or "N-days-ago"  
✅ **Optimized for recent activity** - Default: past year  

**Perfect for**: Analyzing recent development, tracking features, generating documentation from code history.
