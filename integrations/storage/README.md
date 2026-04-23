# GitHub and JIRA Data Storage & Retrieval

This system ingests GitHub and JIRA data using MCP servers, stores it in a local SQLite database, and maintains correlations between GitHub items (PRs, issues, commits) and JIRA issues.

---

## 🎯 Features

✅ **GitHub Ingestion** - PRs, issues, commits via GitHub MCP server  
✅ **JIRA Ingestion** - Issues via JIRA MCP server or public API  
✅ **Automatic Correlation** - Extracts JIRA keys from GitHub data  
✅ **Local SQLite Storage** - Lightweight, no external database required  
✅ **Fast Retrieval** - Indexed queries for agent use  
✅ **Relationship Tracking** - Links GitHub PRs to JIRA issues  
✅ **Parallel Batch Ingestion** - Process multiple repos efficiently  
✅ **Incremental Updates** - Keep data fresh without re-ingesting  

---

## 📖 Documentation

- **[EFFICIENT_INGESTION_GUIDE.md](EFFICIENT_INGESTION_GUIDE.md)** - **⭐ For ingesting ALL OpenShift repositories** (recommended for production)
- **This README** - Single repository ingestion and basic usage

---

## 🚀 Quick Start

### 1. Initialize Database

```bash
# Database is automatically created on first use
# Default location: ~/.agent-knowledge/data.db
```

### 2. Ingest Repository Data

```bash
# Unified ingestion (GitHub + JIRA)
python integrations/storage/ingest.py openshift/installer --jira OCPCLOUD

# This will:
# 1. Fetch GitHub PRs, issues, commits
# 2. Extract JIRA references (e.g., OCPCLOUD-123)
# 3. Fetch referenced JIRA issues
# 4. Store everything in database
# 5. Create correlations
```

### 3. Query Data

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

### Unified Ingestion (Recommended)

```bash
# Full ingestion with JIRA project
python integrations/storage/ingest.py openshift/installer \
  --jira OCPCLOUD \
  --prs 200 \
  --issues 100 \
  --commits 200

# GitHub only (will still fetch referenced JIRA issues)
python integrations/storage/ingest.py kubernetes/kubernetes \
  --prs 100

# Custom database location
python integrations/storage/ingest.py openshift/machine-api-operator \
  --jira OCPCLOUD \
  --db /path/to/custom.db
```

### GitHub Ingestion Only

```bash
# Ingest specific repository
python integrations/storage/ingest_github.py openshift/installer \
  --prs 100 \
  --issues 50 \
  --commits 100

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
from integrations.storage.ingest_github import GitHubIngester
from integrations.storage.ingest_jira import JiraIngester

# Initialize
db = KnowledgeDatabase()

# GitHub ingestion
github = GitHubIngester(db)
github.ingest_full_repository('openshift', 'installer')

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

### Commit Messages
```
commit abc123
Author: Dev
Date: 2024-01-01

    Fix bug in reconciler (OCPCLOUD-999)
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

# Get commits that reference a JIRA issue
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.sha, c.message, c.author_name, c.author_date
        FROM github_commits c
        JOIN github_jira_references ref ON ref.github_commit_sha = c.sha
        WHERE ref.jira_issue_key = ?
    """, ('OCPCLOUD-456',))
    
    commits = cursor.fetchall()
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
- GitHub PRs: by repo, number, state, author
- Commits: by repo, SHA, date
- Correlations: by PR, issue, commit, JIRA key

### Query Performance

| Query | Records | Time |
|-------|---------|------|
| Get PR by number | 1 | <1ms |
| Get PRs with JIRA | 100 | ~10ms |
| Get JIRA with PRs | 100 | ~15ms |
| Full statistics | All | ~20ms |

### Storage Size

| Data | Records | Size |
|------|---------|------|
| 100 PRs | - | ~2MB |
| 100 JIRA issues | - | ~1MB |
| 1000 commits | - | ~5MB |
| Total (typical) | - | ~10MB |

---

## 🧪 Testing

```bash
# Test ingestion with small dataset
python integrations/storage/ingest.py openshift/api \
  --prs 10 \
  --issues 10 \
  --commits 10

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
- **GitHub**: Optional, only for private repos and higher rate limits
- **JIRA**: Not needed for public instances (issues.redhat.com)
- **Storage**: Tokens NOT stored in database

### Data Retention
- **Manual cleanup**: Delete database file to clear all data
- **Selective deletion**: SQL queries to remove specific data

```sql
-- Delete old data
DELETE FROM github_pull_requests WHERE created_at < date('now', '-1 year');
DELETE FROM jira_issues WHERE created_at < date('now', '-1 year');
```

---

## 📘 Examples

See `examples/` directory for:
- Full ingestion workflow
- Custom queries
- Data export scripts
- Integration with agent system

---

## 🆘 Troubleshooting

### "gh: command not found"
Install GitHub CLI: https://cli.github.com

### "Rate limit exceeded"
Set GITHUB_TOKEN environment variable

### "Database locked"
Close other connections to the database

### "JIRA issue not found"
Issue may be private or project key incorrect

### "No correlations found"
GitHub data may not reference JIRA issues - check PR/commit messages

---

## 📚 References

- Database schema: `schema.sql`
- GitHub MCP: `../github/GITHUB_MCP_INTEGRATION.md`
- JIRA integration: `../jira/SIMPLIFIED_SETUP.md`
- Agent integration: `../../agents/extractor/AGENT.md`
