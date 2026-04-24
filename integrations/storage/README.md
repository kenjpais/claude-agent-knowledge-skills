# GitHub and JIRA Data Storage & Retrieval

This system ingests GitHub and JIRA data for a **single repository** using GitHub GraphQL API, stores it in a local SQLite database, and maintains correlations between GitHub items (PRs, issues) and JIRA issues.

---

## 🎯 Features

✅ **GitHub GraphQL API** - Efficient data ingestion with pagination  
✅ **Date Range Filtering** - Ingest data from specific time periods (default: past year)  
✅ **JIRA Ingestion** - Issues via public JIRA REST API  
✅ **Automatic Correlation** - Extracts JIRA keys from GitHub data  
✅ **Local SQLite Storage** - Lightweight, no external database required  
✅ **Fast Retrieval** - Indexed queries for agent use  
✅ **Relationship Tracking** - Links GitHub PRs to JIRA issues  

---

## 🚀 Quick Start

### 1. Setup Authentication (Recommended)

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your GitHub token
# GH_API_TOKEN=ghp_your_token_here
```

**Get a GitHub token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `read:org`
4. Copy the token to `.env` file

**Why use a token?**
- ✅ **5,000 requests/hour** (vs 60 without token)
- ✅ **Access private repositories**
- ✅ **Avoid rate limit errors**
- ✅ **Better reliability** during API issues

### 2. Initialize Database

```bash
# Database is automatically created on first use
# Default location: ~/.agent-knowledge/data.db
```

### 3. Ingest Repository Data

```bash
# Ingest last year of data (default)
python integrations/storage/ingest.py openshift/installer --jira OCPCLOUD

# Ingest specific date range
python integrations/storage/ingest.py openshift/installer \
  --since 2024-01-01 \
  --until 2024-12-31 \
  --jira OCPCLOUD

# Ingest last 90 days
python integrations/storage/ingest.py openshift/installer \
  --since 90-days-ago \
  --jira OCPCLOUD

# This will:
# 1. Fetch GitHub PRs and issues within date range
# 2. Extract JIRA references (e.g., OCPCLOUD-123)
# 3. Fetch referenced JIRA issues
# 4. Store everything in database
# 5. Create correlations
```

### 4. Query Data

```python
from integrations.storage.database import KnowledgeDatabase

db = KnowledgeDatabase()

# Get PRs with linked JIRA issues
prs = db.get_prs_with_jira(limit=10)

# Get JIRA issues with linked GitHub PRs
issues = db.get_jira_issues_with_github(project_key='OCPCLOUD')

# Get statistics
stats = db.get_statistics()
print(f"PRs: {stats['github_prs']}, JIRA issues: {stats['jira_issues']}")
```

---

## 📁 Database Schema

### GitHub Tables

- `github_repositories` - Repository metadata
- `github_pull_requests` - Pull requests with full details
- `github_issues` - GitHub issues
- `github_commits` - Commit history
- `github_pr_commits` - PR → Commits mapping
- `github_pr_reviews` - Code reviews
- `github_comments` - Comments on PRs/issues

### JIRA Tables

- `jira_projects` - JIRA projects
- `jira_issue_types` - Issue types (Epic, Story, Bug, etc.)
- `jira_issues` - JIRA issues with full details
- `jira_issue_links` - Issue relationships (blocks, relates to, etc.)
- `jira_comments` - Issue comments

### Correlation Table

- `github_jira_references` - Links GitHub items to JIRA issues
  - Tracks where reference was found (title, body, commit message)
  - Stores context around reference
  - Links to both GitHub item and JIRA issue

---

## 🔧 Usage

### Date Range Options

```bash
# Default: Last year
python ingest.py openshift/installer --jira OCPCLOUD

# Specific dates
python ingest.py openshift/installer \
  --since 2024-01-01 \
  --until 2024-12-31

# Relative dates (N-days-ago)
python ingest.py openshift/installer --since 90-days-ago
python ingest.py openshift/installer --since 180-days-ago

# Custom limits
python ingest.py openshift/installer \
  --prs 2000 \
  --issues 1000 \
  --jira OCPCLOUD
```

### GitHub Ingestion Only

```bash
# Ingest specific repository with GraphQL API
python integrations/storage/ingest_github.py openshift/installer \
  --since 2024-01-01 \
  --prs 1000 \
  --issues 500

# This automatically extracts JIRA references
```

### JIRA Ingestion Only

```bash
# Ingest referenced JIRA issues (from GitHub data)
python integrations/storage/ingest_jira.py referenced

# Ingest specific JIRA issues
python integrations/storage/ingest_jira.py keys OCPCLOUD-123 OCPCLOUD-456

# Ingest JIRA project
python integrations/storage/ingest_jira.py project OCPCLOUD --limit 100

# Ingest recent issues
python integrations/storage/ingest_jira.py recent OCPCLOUD --days 90 --limit 100
```

### Python API

```python
from integrations.storage.database import KnowledgeDatabase
from integrations.storage.ingest_github import GitHubGraphQLIngester
from integrations.storage.ingest_jira import JiraIngester
from datetime import datetime, timedelta

# Initialize
db = KnowledgeDatabase()

# GitHub ingestion with date range
github = GitHubGraphQLIngester(db)
since = datetime.now() - timedelta(days=365)
github.ingest_repository_full(
    'openshift', 'installer',
    since_date=since
)

# JIRA ingestion
jira = JiraIngester(db)
jira.ingest_referenced_issues()  # Fetch issues referenced in GitHub

# Query
prs_with_jira = db.get_prs_with_jira(limit=10)
for pr in prs_with_jira:
    print(f"PR #{pr['number']}: {pr['title']}")
    print(f"  JIRA: {pr['jira_keys']}")
```

---

## 🔍 JIRA Reference Extraction

The system automatically extracts JIRA keys from:

### GitHub PR Titles
```
Fix OCPCLOUD-123: Update machine controller
                   ↑ Extracted
```

### GitHub PR Bodies
```
This PR addresses OCPCLOUD-456 by implementing...
Related to OCPCLOUD-789
           ↑ Extracted
```

### GitHub Issue Titles and Bodies
```
Bug: OCPCLOUD-999 - Reconciler fails on edge case
     ↑ Extracted
```

### Pattern Recognition
- Format: `PROJECT-NUMBER` (e.g., `OCPCLOUD-123`)
- Common OpenShift projects: OCPCLOUD, OCPBUGS, OCPPLAN, SPLAT, CNV, ROSA
- Filters out false positives (PR-123, HTTP-404, etc.)

---

## 📊 Queries and Views

### Pre-built Views

```sql
-- PRs with linked JIRA issues
SELECT * FROM v_prs_with_jira;

-- JIRA issues with linked GitHub PRs
SELECT * FROM v_jira_with_prs;

-- Recent activity (GitHub + JIRA combined)
SELECT * FROM v_recent_activity ORDER BY activity_date DESC LIMIT 20;
```

### Custom Queries

```python
# Get all PRs for a specific JIRA issue
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pr.number, pr.title, pr.state, pr.merged_at
        FROM github_pull_requests pr
        JOIN github_jira_references ref ON ref.github_pr_id = pr.pr_id
        WHERE ref.jira_issue_key = ?
    """, ('OCPCLOUD-123',))
    
    prs = cursor.fetchall()

# Get PRs created in last 30 days
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT number, title, created_at, state
        FROM github_pull_requests
        WHERE created_at >= date('now', '-30 days')
        ORDER BY created_at DESC
    """)
    
    recent_prs = cursor.fetchall()
```

---

## 🔗 Integration with Agent System

### Extractor Agent Usage

The extractor agent uses the database to enrich documentation:

```python
from integrations.storage.database import KnowledgeDatabase

# In extractor agent
db = KnowledgeDatabase()

# Get features for component documentation
features = db.get_jira_issues_with_github(project_key='OCPCLOUD')

for feature in features:
    if feature['pr_count'] > 0:
        # Feature has implementing PRs
        # Include in component documentation
        component_doc += f"- {feature['summary']} (PRs: {feature['pr_numbers']})"
```

### Synthesizer Agent Usage

```python
# Generate ADRs from PR descriptions
prs = db.get_prs_with_jira(limit=100)

for pr in prs:
    if 'architecture' in pr['labels'].lower() or 'design' in pr['title'].lower():
        # This is an architectural PR
        # Extract ADR from PR + linked JIRA issue
        adr = generate_adr_from_pr(pr)
```

### Retrieval Agent Usage

```python
# Answer queries using database
def answer_query(query: str):
    if 'feature' in query.lower():
        # Get recent features
        features = db.get_jira_issues_with_github(project_key='OCPCLOUD')
        return format_features(features)
    
    elif 'pr' in query.lower():
        # Get recent PRs
        prs = db.get_prs_with_jira(limit=10)
        return format_prs(prs)
```

---

## ⚙️ Configuration

### Database Location

```python
# Default location
db = KnowledgeDatabase()  # ~/.agent-knowledge/data.db

# Custom location
db = KnowledgeDatabase('/path/to/custom.db')

# Environment variable
export AGENT_KNOWLEDGE_DB=/path/to/db.sqlite
```

### JIRA Configuration

```bash
# Public JIRA (default: Red Hat)
python ingest_jira.py project OCPCLOUD

# Custom public JIRA
python ingest_jira.py project MYPROJECT --jira-url https://issues.apache.org

# Private JIRA (requires authentication)
export JIRA_URL=https://your-jira.com
export JIRA_EMAIL=you@company.com
export JIRA_API_TOKEN=your-token
```

---

## 📈 Performance

### Indexing
All tables are indexed for fast queries:
- JIRA issues: by project, type, key, status
- GitHub PRs: by repo, number, state, author, created_at
- GitHub issues: by repo, number, state, created_at
- Correlations: by PR, issue, JIRA key

### Query Performance

| Query | Records | Time |
|-------|---------|------|
| Get PR by number | 1 | <1ms |
| Get PRs with JIRA | 100 | ~10ms |
| Get JIRA with PRs | 100 | ~15ms |
| Full statistics | All | ~20ms |
| Date range query | 1000 | ~50ms |

### GraphQL API Benefits

- **Efficient**: Only fetches needed fields
- **Pagination**: Cursor-based, handles large datasets
- **Fast**: Single request can fetch nested data
- **Reliable**: Built-in rate limiting and error handling

---

## 🧪 Testing

```bash
# Test ingestion with small date range
python integrations/storage/ingest.py openshift/api \
  --since 30-days-ago \
  --prs 50 \
  --issues 50

# Verify data
python -c "
from integrations.storage.database import KnowledgeDatabase
db = KnowledgeDatabase()
print(db.get_statistics())
"

# Test queries
python -c "
from integrations.storage.database import KnowledgeDatabase
db = KnowledgeDatabase()
prs = db.get_prs_with_jira(limit=5)
for pr in prs:
    print(f\"PR {pr['number']}: {pr['jira_keys']}\")
"
```

---

## 🔒 Security

### Data Privacy
- **Local storage**: All data stored locally in SQLite
- **No cloud sync**: Data never leaves your machine
- **Read-only**: Ingestion uses read-only APIs

### API Tokens
- **GitHub**: Token loaded from `.env` file (recommended for higher rate limits)
  - Create `.env` file in project root: `cp .env.example .env`
  - Add your token: `GH_API_TOKEN=ghp_your_token_here`
  - Get token at: https://github.com/settings/tokens
- **JIRA**: Not needed for public instances (issues.redhat.com)
- **Storage**: Tokens NOT stored in database, only in `.env` file
- **Security**: `.env` file is in `.gitignore` to prevent accidental commits

### Data Retention
- **Manual cleanup**: Delete database file to clear all data
- **Selective deletion**: SQL queries to remove specific data

```sql
-- Delete old data
DELETE FROM github_pull_requests WHERE created_at < date('now', '-1 year');
DELETE FROM jira_issues WHERE created_at < date('now', '-1 year');
```

---

## 🆘 Troubleshooting

### "gh: command not found"
Install GitHub CLI: https://cli.github.com

### "Rate limit exceeded"
Add GitHub token to `.env` file for higher limits (5000 req/hour):
```bash
# Create .env file
cp .env.example .env

# Add your token
echo "GH_API_TOKEN=ghp_your_token_here" > .env
```

### "Database locked"
Close other connections to the database

### "JIRA issue not found"
Issue may be private or project key incorrect

### "No correlations found"
GitHub data may not reference JIRA issues - check PR/issue titles and bodies

### GraphQL Errors
- Check query syntax if you see GraphQL errors
- Ensure `gh` CLI is authenticated: `gh auth status`
- Some fields may not be available for private repos

---

## 📚 References

- Database schema: `schema.sql`
- Agent integration: `../../agents/extractor/AGENT.md`

---

## 🎯 Best Practices

### 1. Use Date Ranges Effectively

```bash
# For recent development activity
python ingest.py openshift/installer --since 90-days-ago

# For historical analysis
python ingest.py openshift/installer --since 2023-01-01 --until 2023-12-31

# For continuous updates (run monthly)
python ingest.py openshift/installer --since 30-days-ago
```

### 2. Optimize Limits

```bash
# For quick overview
python ingest.py openshift/installer --prs 100 --issues 50

# For comprehensive analysis
python ingest.py openshift/installer --prs 2000 --issues 1000
```

### 3. Regular Updates

```bash
# Recommended: Monthly ingestion of last 30-60 days
# This keeps data fresh without re-ingesting everything
python ingest.py openshift/installer --since 30-days-ago
```

### 4. Backup Database

```bash
# Before large ingestions
cp ~/.agent-knowledge/data.db ~/.agent-knowledge/data.db.backup

# Use SQLite backup command
sqlite3 ~/.agent-knowledge/data.db ".backup '/path/to/backup.db'"
```

---

## 📖 Examples

### Example 1: Analyze Last Quarter

```bash
python ingest.py openshift/installer \
  --since 90-days-ago \
  --jira OCPCLOUD

# Query recent features
python -c "
from integrations.storage.database import KnowledgeDatabase
db = KnowledgeDatabase()
issues = db.get_jira_issues_with_github(project_key='OCPCLOUD')
for issue in issues[:10]:
    print(f\"{issue['key']}: {issue['summary']} ({issue['pr_count']} PRs)\")
"
```

### Example 2: Generate Documentation from Data

```python
from integrations.storage.database import KnowledgeDatabase

db = KnowledgeDatabase()

# Get architectural PRs
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pr.*, GROUP_CONCAT(ref.jira_issue_key) as jira_keys
        FROM github_pull_requests pr
        LEFT JOIN github_jira_references ref ON ref.github_pr_id = pr.pr_id
        WHERE pr.labels LIKE '%architecture%'
        AND pr.created_at >= date('now', '-180 days')
        GROUP BY pr.pr_id
        ORDER BY pr.created_at DESC
    """)
    
    architectural_prs = cursor.fetchall()
    
    # Generate ADR documentation
    for pr in architectural_prs:
        print(f"## ADR: {pr['title']}")
        print(f"**PR**: #{pr['number']}")
        print(f"**JIRA**: {pr['jira_keys']}")
        print(f"**Date**: {pr['created_at']}")
        print()
```

---

## Summary

This system provides **efficient single-repository ingestion** with:
- ✅ GitHub GraphQL API for optimal performance
- ✅ Date range filtering (default: past year)
- ✅ Automatic JIRA correlation
- ✅ Local SQLite storage
- ✅ Fast indexed queries
- ✅ Agent system integration

**Perfect for**: Analyzing recent repository activity, tracking feature development, correlating GitHub and JIRA work, generating documentation from code history.
