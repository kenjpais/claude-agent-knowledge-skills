# Efficient Ingestion for All OpenShift Repositories

This guide describes the most efficient way to ingest data from **all Red Hat OpenShift repositories** into the knowledge system.

---

## 🎯 Strategy Overview

**3-Phase Pipeline** for maximum efficiency:

1. **Discovery** (5 min) - Find and prioritize all OpenShift repos
2. **Batch Ingestion** (2-4 hours) - Parallel processing with checkpointing
3. **Incremental Updates** (10 min/day) - Keep data fresh

**Key Features**:
- ✅ Parallel processing (5-10 workers)
- ✅ Rate limit coordination
- ✅ Checkpoint/resume capability
- ✅ JIRA deduplication
- ✅ Incremental updates
- ✅ Progress tracking

---

## 📊 Expected Results

### Scale
- **Repositories**: ~100-150 OpenShift repos
- **Data Volume**:
  - PRs: ~50,000+
  - Issues: ~100,000+
  - Commits: ~500,000+
  - JIRA Issues: ~10,000+
  - Correlations: ~50,000+

### Performance
- **Initial Ingestion**: 2-4 hours (with 5 workers)
- **Daily Updates**: 5-10 minutes
- **Database Size**: ~500MB - 1GB
- **API Requests**: ~4,500/hour (stays under GitHub limit)

### Storage
- **Database**: ~/.agent-knowledge/data.db
- **Size**: 500MB - 1GB for all OpenShift repos
- **Performance**: SQLite handles this easily (tested to 1TB+)

---

## 🚀 Complete Workflow

### Phase 1: Repository Discovery

**Purpose**: Find all OpenShift repos and prioritize them

```bash
# Discover all OpenShift repositories
cd integrations/storage
python discover_openshift_repos.py --min-stars 5 --min-activity-days 180

# This creates: openshift_repos.json
```

**Output**: `openshift_repos.json`
```json
{
  "generated_at": "2026-04-23T10:00:00",
  "total_repos": 142,
  "repositories": [
    {
      "full_name": "openshift/installer",
      "priority_score": 12543,
      "stars": 543,
      "forks": 2000,
      ...
    },
    ...
  ]
}
```

**Customization**:
- `--min-stars N` - Only repos with N+ stars (default: 10)
- `--min-activity-days N` - Only repos active in last N days (default: 180)
- `--output FILE` - Custom output file

**Priority Algorithm**:
1. High-priority repos (installer, machine-api, etc.) → +10,000
2. Stars → +1 per star
3. Forks → +2 per fork
4. Open issues → +0.5 per issue

---

### Phase 2: Batch Ingestion

**Purpose**: Ingest all repos in parallel with checkpointing

```bash
# Run batch ingestion
python batch_ingest.py openshift_repos.json \
  --workers 5 \
  --prs 500 \
  --issues 200 \
  --commits 500 \
  --jira OCPCLOUD OCPBUGS OCPPLAN SPLAT

# This will:
# 1. Process repos in parallel (5 workers)
# 2. Extract JIRA references from all GitHub data
# 3. Ingest referenced JIRA issues
# 4. Ingest full JIRA projects (OCPCLOUD, OCPBUGS, etc.)
# 5. Save checkpoints (resume if interrupted)
```

**Options**:
- `--workers N` - Parallel workers (default: 5, max: 10)
- `--prs N` - Max PRs per repo (default: 500)
- `--issues N` - Max issues per repo (default: 200)
- `--commits N` - Max commits per repo (default: 500)
- `--jira PROJECT [PROJECT...]` - JIRA projects to ingest
- `--db PATH` - Custom database path
- `--no-skip-completed` - Re-ingest already completed repos

**Checkpoint/Resume**:
If interrupted (Ctrl+C, network error, etc.), just run the same command again:
```bash
# Resume from checkpoint
python batch_ingest.py openshift_repos.json --workers 5 --jira OCPCLOUD
```

Checkpoints saved in `.ingestion_checkpoint.json`:
```json
{
  "openshift/installer": {
    "status": "completed",
    "completed_at": "2026-04-23T12:00:00",
    "stats": {"prs": 500, "issues": 200, "commits": 500}
  },
  "openshift/machine-api-operator": {
    "status": "completed",
    ...
  }
}
```

**Rate Limiting**:
- Automatic coordination across workers
- Stays under 4,500 requests/hour (GitHub limit is 5,000)
- Waits intelligently if limit approached

**Output**:
- `ingestion_stats.json` - Overall statistics
- `.ingestion_checkpoint.json` - Resume state

---

### Phase 3: Incremental Updates

**Purpose**: Keep data fresh without re-ingesting everything

#### Daily Updates (Recommended)

```bash
# Update all repositories (only fetch new data)
python incremental_update.py all

# This runs daily via cron:
# - Fetches PRs/issues/commits created since last update
# - Extracts new JIRA references
# - Ingests new JIRA issues
# - Takes ~5-10 minutes
```

#### Update Single Repository

```bash
# Update specific repo
python incremental_update.py repo openshift/installer

# Force full re-ingestion
python incremental_update.py repo openshift/installer --force-full
```

#### Update JIRA Only

```bash
# Just update JIRA issues for new references
python incremental_update.py jira
```

**Automation with Cron**:
```bash
# Add to crontab (daily at 2am)
0 2 * * * cd /path/to/integrations/storage && python incremental_update.py all
```

---

## 📊 Monitoring & Statistics

### Real-Time Progress

During batch ingestion:
```
📊 Progress: 25/142 (17.6%)

📦 Ingesting: openshift/installer
   Priority Score: 12543
   ✅ Ingested 500 pull requests
   ✅ Ingested 200 issues
   ✅ Ingested 500 commits
   🔗 Extracted 234 JIRA references
```

### Final Statistics

```json
{
  "total_repos": 142,
  "processed": 142,
  "success": 140,
  "failed": 2,
  "elapsed_hours": 3.2,
  "jira_stats": {
    "referenced": {"success": 2341, "failed": 12},
    "projects": {
      "OCPCLOUD": {"success": 543},
      "OCPBUGS": {"success": 1234}
    }
  }
}
```

### Database Statistics

```bash
# Check database stats
python -c "
from database import KnowledgeDatabase
db = KnowledgeDatabase()
stats = db.get_statistics()
for key, value in stats.items():
    print(f'{key}: {value:,}')
"
```

Output:
```
github_repos: 142
github_prs: 54,231
github_issues: 103,421
github_commits: 523,112
jira_issues: 9,876
correlations: 52,341
jira_issues_referenced: 8,234
```

---

## ⚡ Performance Optimization

### Worker Count Tuning

**Low-end machine** (2-4 cores):
```bash
python batch_ingest.py openshift_repos.json --workers 2
```

**High-end machine** (8+ cores):
```bash
python batch_ingest.py openshift_repos.json --workers 10
```

**Rate limit is the bottleneck**, not CPU, so:
- More workers = faster until rate limit hit
- Optimal: 5-8 workers
- Max useful: ~10 workers

### Limit Tuning

**Fast initial ingestion** (lower limits):
```bash
python batch_ingest.py openshift_repos.json \
  --prs 100 \
  --issues 50 \
  --commits 100
```

**Comprehensive ingestion** (higher limits):
```bash
python batch_ingest.py openshift_repos.json \
  --prs 1000 \
  --issues 500 \
  --commits 1000
```

**Recommended for OpenShift**:
- PRs: 500 (gets recent ~2 years)
- Issues: 200 (high-priority only)
- Commits: 500 (recent ~6 months)

### Database Optimization

**Vacuum database** (after large ingestion):
```bash
sqlite3 ~/.agent-knowledge/data.db "VACUUM;"
```

**Check database size**:
```bash
du -h ~/.agent-knowledge/data.db
```

---

## 🔍 Querying Ingested Data

### PRs with JIRA Issues

```python
from database import KnowledgeDatabase

db = KnowledgeDatabase()
prs = db.get_prs_with_jira(limit=10)

for pr in prs:
    print(f"PR #{pr['number']}: {pr['title']}")
    print(f"  JIRA: {pr['jira_keys']}")
    print(f"  Repo: {pr['repo_id']}")
```

### JIRA Issues with GitHub PRs

```python
issues = db.get_jira_issues_with_github(project_key='OCPCLOUD')

for issue in issues:
    print(f"{issue['key']}: {issue['summary']}")
    print(f"  PRs: {issue['pr_numbers']} ({issue['pr_count']} total)")
```

### Custom SQL Queries

```python
with db.get_connection() as conn:
    cursor = conn.cursor()
    
    # Most active repositories
    cursor.execute("""
        SELECT r.full_name, COUNT(p.pr_id) as pr_count
        FROM github_repositories r
        LEFT JOIN github_pull_requests p ON p.repo_id = r.repo_id
        GROUP BY r.repo_id
        ORDER BY pr_count DESC
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        print(f"{row[0]}: {row[1]} PRs")
```

---

## 🛠️ Troubleshooting

### "Rate limit exceeded"

**Symptom**: `Rate limit exceeded` error

**Solution**:
```bash
# Reduce workers
python batch_ingest.py openshift_repos.json --workers 3

# Or set GITHUB_TOKEN for higher limit
export GITHUB_TOKEN=ghp_your_token_here
```

### "Database locked"

**Symptom**: `database is locked` error

**Solution**:
```bash
# Reduce parallel workers (SQLite has lock contention)
python batch_ingest.py openshift_repos.json --workers 3

# Or use WAL mode (better concurrency)
sqlite3 ~/.agent-knowledge/data.db "PRAGMA journal_mode=WAL;"
```

### Resume After Failure

**Symptom**: Ingestion interrupted or failed

**Solution**:
```bash
# Just run again - it resumes from checkpoint
python batch_ingest.py openshift_repos.json --workers 5 --jira OCPCLOUD

# Check checkpoint status
cat .ingestion_checkpoint.json | jq '.[] | select(.status == "failed")'

# Force re-ingest failed repos
python batch_ingest.py openshift_repos.json --no-skip-completed
```

### "gh: command not found"

**Symptom**: GitHub CLI not installed

**Solution**:
```bash
# Install GitHub CLI
# macOS
brew install gh

# Linux
# See: https://cli.github.com/manual/installation
```

### JIRA Issues Not Found

**Symptom**: Many JIRA issues return 404

**Reasons**:
1. Issue is private
2. Project key incorrect
3. JIRA instance URL wrong

**Solution**:
```bash
# Check JIRA URL (default is Red Hat public JIRA)
# For custom JIRA, set environment:
export JIRA_URL=https://your-jira.com

# Skip private issues (they're already filtered)
# Check logs for which issues failed
```

---

## 📋 Production Checklist

### Initial Setup

- [ ] Install prerequisites (`gh` CLI, Python 3.9+)
- [ ] Set GITHUB_TOKEN for higher rate limits
- [ ] Configure database path (default: ~/.agent-knowledge/data.db)
- [ ] Enable WAL mode for better concurrency
  ```bash
  sqlite3 ~/.agent-knowledge/data.db "PRAGMA journal_mode=WAL;"
  ```

### Initial Ingestion

- [ ] Run repository discovery
  ```bash
  python discover_openshift_repos.py
  ```
- [ ] Review manifest (openshift_repos.json)
- [ ] Run batch ingestion with appropriate limits
  ```bash
  python batch_ingest.py openshift_repos.json --workers 5 --jira OCPCLOUD OCPBUGS
  ```
- [ ] Monitor progress (check logs, checkpoint file)
- [ ] Verify database statistics
- [ ] Backup database
  ```bash
  cp ~/.agent-knowledge/data.db ~/.agent-knowledge/data.db.backup
  ```

### Daily Maintenance

- [ ] Run incremental updates (via cron)
  ```bash
  0 2 * * * cd /path/to/integrations/storage && python incremental_update.py all
  ```
- [ ] Monitor database size
- [ ] Vacuum database weekly
  ```bash
  sqlite3 ~/.agent-knowledge/data.db "VACUUM;"
  ```
- [ ] Check for failed updates
- [ ] Backup database (incremental or full)

### Weekly/Monthly

- [ ] Review checkpoint file for failures
- [ ] Re-ingest failed repositories
- [ ] Update JIRA projects (new issues)
- [ ] Check database integrity
  ```bash
  sqlite3 ~/.agent-knowledge/data.db "PRAGMA integrity_check;"
  ```
- [ ] Archive old database backups

---

## 📈 Scaling Considerations

### Current Limits

**GitHub API**:
- Unauthenticated: 60 requests/hour
- Authenticated: 5,000 requests/hour
- **Solution**: Use GITHUB_TOKEN

**SQLite**:
- Max database size: ~140TB (theoretical)
- Practical limit: ~1TB with good performance
- **Current usage**: <1GB for all OpenShift
- **Not a bottleneck**

**Disk Space**:
- Database: ~500MB - 1GB
- Checkpoints: ~100KB
- Logs: varies
- **Total**: <2GB

### Future Scaling

**If data grows 10x**:
- SQLite still fine (10GB is nothing)
- May need to increase incremental update frequency
- Consider archiving old data (>1 year)

**If data grows 100x**:
- Consider PostgreSQL migration (100GB+)
- Implement partitioning by date
- Archive historical data to separate DB

**For now**: SQLite is perfect for OpenShift scale

---

## 🎯 Best Practices

### 1. Start Small, Scale Up

```bash
# Test with one repo first
python ingest.py openshift/installer --prs 10

# Then small batch
python batch_ingest.py small_manifest.json --workers 2

# Then full ingestion
python batch_ingest.py openshift_repos.json --workers 5
```

### 2. Use Checkpoints

Always rely on checkpoints - they're reliable:
```bash
# If interrupted, just run again
python batch_ingest.py openshift_repos.json --workers 5
```

### 3. Monitor Rate Limits

```bash
# Check current rate limit
gh api rate_limit

# Output shows remaining requests
```

### 4. Incremental > Full

Prefer incremental updates:
```bash
# Daily incremental (fast)
python incremental_update.py all

# Only full re-ingest when needed
python batch_ingest.py openshift_repos.json --no-skip-completed
```

### 5. Backup Regularly

```bash
# Before major operations
cp ~/.agent-knowledge/data.db ~/.agent-knowledge/data.db.$(date +%Y%m%d)

# Or use SQLite backup command
sqlite3 ~/.agent-knowledge/data.db ".backup '/path/to/backup.db'"
```

---

## 📊 Example: Full OpenShift Ingestion

### End-to-End Workflow

```bash
# 1. Discovery (5 minutes)
cd integrations/storage
python discover_openshift_repos.py

# Review manifest
cat openshift_repos.json | jq '.total_repos'
# Output: 142

# 2. Batch ingestion (3 hours)
python batch_ingest.py openshift_repos.json \
  --workers 5 \
  --prs 500 \
  --issues 200 \
  --commits 500 \
  --jira OCPCLOUD OCPBUGS OCPPLAN SPLAT

# Output:
# 📊 BATCH INGESTION COMPLETE
# ✅ Success: 140/142
# ❌ Failed: 2/142
# ⏱️  Time: 3.21 hours
#
# 📊 Database Statistics:
#    Repositories: 142
#    Pull Requests: 54,231
#    Issues: 103,421
#    Commits: 523,112
#    JIRA Issues: 9,876
#    Correlations: 52,341

# 3. Setup daily updates
(crontab -l 2>/dev/null; echo "0 2 * * * cd $(pwd) && python incremental_update.py all") | crontab -

# 4. Done! Data is now available for agents
```

---

## 🔗 Integration with Agent System

### Extractor Agent Usage

```python
from integrations.storage.database import KnowledgeDatabase

# In extractor agent
db = KnowledgeDatabase()

# Get all PRs for a repository
prs = db.get_prs_with_jira(repo_id=123, limit=100)

# Extract features from JIRA
features = db.get_jira_issues_with_github(project_key='OCPCLOUD')

# Use in component documentation
for feature in features:
    if feature['pr_count'] > 0:
        # This feature has implementing PRs
        component_doc += f"- {feature['summary']}\n"
        component_doc += f"  PRs: {feature['pr_numbers']}\n"
```

### Synthesizer Agent Usage

```python
# Generate ADRs from PR patterns
with db.get_connection() as conn:
    cursor = conn.cursor()
    
    # Find architectural PRs
    cursor.execute("""
        SELECT pr.*, GROUP_CONCAT(ref.jira_issue_key) as jira_keys
        FROM github_pull_requests pr
        LEFT JOIN github_jira_references ref ON ref.github_pr_id = pr.pr_id
        WHERE pr.labels LIKE '%architecture%' OR pr.title LIKE '%design%'
        GROUP BY pr.pr_id
        ORDER BY pr.created_at DESC
        LIMIT 50
    """)
    
    architectural_prs = cursor.fetchall()

# Generate ADR from each PR
for pr in architectural_prs:
    adr = synthesize_adr(pr)
    # Write to agentic/design-docs/decisions/
```

---

## 🎉 Summary

**Most Efficient Approach**:

1. ✅ **One-time**: Discover → Batch ingest (3 hours)
2. ✅ **Daily**: Incremental updates (10 minutes)
3. ✅ **Always**: Checkpoint/resume capability
4. ✅ **Smart**: Parallel processing with rate limit coordination
5. ✅ **Complete**: GitHub + JIRA with automatic correlation

**Expected Results**:
- 142 repositories ingested
- 54K+ PRs, 103K+ issues, 523K+ commits
- 10K+ JIRA issues
- 52K+ correlations
- Ready for agent system in 3 hours

**This is the most efficient way to ingest all OpenShift data.**
