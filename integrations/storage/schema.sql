-- Agent Knowledge System - Database Schema
-- Stores GitHub and JIRA data with correlation

-- ============================================
-- JIRA TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS jira_projects (
    project_id        INTEGER PRIMARY KEY,
    project_key       VARCHAR(20) UNIQUE NOT NULL,
    name              VARCHAR(255) NOT NULL,
    description       TEXT,
    jira_url          VARCHAR(500),
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jira_issue_types (
    issue_type_id     INTEGER PRIMARY KEY,
    name              VARCHAR(50) UNIQUE NOT NULL,  -- Epic, Story, Task, Bug, Feature
    hierarchy_level   INTEGER NOT NULL,             -- Epic=1, Story=2, Task=3
    description       TEXT
);

CREATE TABLE IF NOT EXISTS jira_issues (
    issue_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id        INTEGER NOT NULL,
    issue_type_id     INTEGER NOT NULL,
    parent_issue_id   INTEGER NULL,  -- self-reference for hierarchy

    key               VARCHAR(50) UNIQUE NOT NULL,  -- e.g., OCPCLOUD-123
    summary           VARCHAR(500) NOT NULL,
    description       TEXT,

    status            VARCHAR(50),
    priority          VARCHAR(50),
    resolution        VARCHAR(50),

    assignee          VARCHAR(255),
    reporter          VARCHAR(255),

    labels            TEXT,  -- JSON array
    components        TEXT,  -- JSON array

    created_at        TIMESTAMP NOT NULL,
    updated_at        TIMESTAMP,
    resolved_at       TIMESTAMP,
    due_date          TIMESTAMP,

    jira_url          VARCHAR(500),
    raw_data          TEXT,  -- Full JSON from JIRA API

    ingested_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES jira_projects(project_id),
    FOREIGN KEY (issue_type_id) REFERENCES jira_issue_types(issue_type_id),
    FOREIGN KEY (parent_issue_id) REFERENCES jira_issues(issue_id)
);

CREATE TABLE IF NOT EXISTS jira_issue_links (
    link_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    source_issue_id   INTEGER NOT NULL,
    target_issue_id   INTEGER NOT NULL,
    link_type         VARCHAR(50), -- blocks, relates_to, duplicates, implements

    FOREIGN KEY (source_issue_id) REFERENCES jira_issues(issue_id),
    FOREIGN KEY (target_issue_id) REFERENCES jira_issues(issue_id),

    UNIQUE(source_issue_id, target_issue_id, link_type)
);

CREATE TABLE IF NOT EXISTS jira_comments (
    comment_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id          INTEGER NOT NULL,
    author            VARCHAR(255),
    body              TEXT,
    created_at        TIMESTAMP NOT NULL,
    updated_at        TIMESTAMP,

    FOREIGN KEY (issue_id) REFERENCES jira_issues(issue_id)
);

-- ============================================
-- GITHUB TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS github_repositories (
    repo_id           INTEGER PRIMARY KEY,
    owner             VARCHAR(255) NOT NULL,
    name              VARCHAR(255) NOT NULL,
    full_name         VARCHAR(500) UNIQUE NOT NULL,  -- owner/name
    description       TEXT,

    default_branch    VARCHAR(100),
    language          VARCHAR(50),

    stars             INTEGER DEFAULT 0,
    forks             INTEGER DEFAULT 0,
    open_issues       INTEGER DEFAULT 0,

    created_at        TIMESTAMP,
    updated_at        TIMESTAMP,
    pushed_at         TIMESTAMP,

    github_url        VARCHAR(500),
    ingested_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS github_pull_requests (
    pr_id             INTEGER PRIMARY KEY,
    repo_id           INTEGER NOT NULL,

    number            INTEGER NOT NULL,
    title             VARCHAR(500) NOT NULL,
    body              TEXT,

    state             VARCHAR(50),  -- open, closed, merged
    draft             BOOLEAN DEFAULT 0,

    author            VARCHAR(255),
    assignees         TEXT,  -- JSON array
    reviewers         TEXT,  -- JSON array

    base_branch       VARCHAR(255),
    head_branch       VARCHAR(255),

    labels            TEXT,  -- JSON array

    created_at        TIMESTAMP NOT NULL,
    updated_at        TIMESTAMP,
    closed_at         TIMESTAMP,
    merged_at         TIMESTAMP,

    merge_commit_sha  VARCHAR(255),

    additions         INTEGER,
    deletions         INTEGER,
    changed_files     INTEGER,

    github_url        VARCHAR(500),
    raw_data          TEXT,  -- Full JSON from GitHub API

    ingested_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (repo_id) REFERENCES github_repositories(repo_id),
    UNIQUE(repo_id, number)
);

CREATE TABLE IF NOT EXISTS github_issues (
    issue_id          INTEGER PRIMARY KEY,
    repo_id           INTEGER NOT NULL,

    number            INTEGER NOT NULL,
    title             VARCHAR(500) NOT NULL,
    body              TEXT,

    state             VARCHAR(50),  -- open, closed

    author            VARCHAR(255),
    assignees         TEXT,  -- JSON array

    labels            TEXT,  -- JSON array

    created_at        TIMESTAMP NOT NULL,
    updated_at        TIMESTAMP,
    closed_at         TIMESTAMP,

    github_url        VARCHAR(500),
    raw_data          TEXT,  -- Full JSON from GitHub API

    ingested_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (repo_id) REFERENCES github_repositories(repo_id),
    UNIQUE(repo_id, number)
);

CREATE TABLE IF NOT EXISTS github_commits (
    commit_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_id           INTEGER NOT NULL,

    sha               VARCHAR(255) UNIQUE NOT NULL,
    message           TEXT NOT NULL,

    author_name       VARCHAR(255),
    author_email      VARCHAR(255),
    author_date       TIMESTAMP,

    committer_name    VARCHAR(255),
    committer_email   VARCHAR(255),
    committer_date    TIMESTAMP,

    parents           TEXT,  -- JSON array of parent SHAs

    additions         INTEGER,
    deletions         INTEGER,
    changed_files     INTEGER,

    github_url        VARCHAR(500),
    raw_data          TEXT,  -- Full JSON from GitHub API

    ingested_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (repo_id) REFERENCES github_repositories(repo_id)
);

CREATE TABLE IF NOT EXISTS github_pr_commits (
    pr_commit_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    pr_id             INTEGER NOT NULL,
    commit_sha        VARCHAR(255) NOT NULL,

    FOREIGN KEY (pr_id) REFERENCES github_pull_requests(pr_id),
    UNIQUE(pr_id, commit_sha)
);

CREATE TABLE IF NOT EXISTS github_pr_reviews (
    review_id         INTEGER PRIMARY KEY,
    pr_id             INTEGER NOT NULL,

    author            VARCHAR(255),
    state             VARCHAR(50),  -- APPROVED, CHANGES_REQUESTED, COMMENTED
    body              TEXT,

    submitted_at      TIMESTAMP,

    FOREIGN KEY (pr_id) REFERENCES github_pull_requests(pr_id)
);

CREATE TABLE IF NOT EXISTS github_comments (
    comment_id        INTEGER PRIMARY KEY,

    -- Can be on PR or issue
    pr_id             INTEGER NULL,
    issue_id          INTEGER NULL,

    author            VARCHAR(255),
    body              TEXT,

    created_at        TIMESTAMP NOT NULL,
    updated_at        TIMESTAMP,

    FOREIGN KEY (pr_id) REFERENCES github_pull_requests(pr_id),
    FOREIGN KEY (issue_id) REFERENCES github_issues(issue_id),

    CHECK ((pr_id IS NOT NULL AND issue_id IS NULL) OR (pr_id IS NULL AND issue_id IS NOT NULL))
);

-- ============================================
-- CORRELATION TABLES (GITHUB ↔ JIRA)
-- ============================================

CREATE TABLE IF NOT EXISTS github_jira_references (
    reference_id      INTEGER PRIMARY KEY AUTOINCREMENT,

    -- GitHub source (one of these)
    github_pr_id      INTEGER NULL,
    github_issue_id   INTEGER NULL,
    github_commit_sha VARCHAR(255) NULL,

    -- JIRA target
    jira_issue_key    VARCHAR(50) NOT NULL,
    jira_issue_id     INTEGER NULL,  -- Populated after JIRA ingestion

    -- Reference metadata
    reference_type    VARCHAR(50) NOT NULL,  -- title, body, commit_message, comment
    reference_context TEXT,  -- Surrounding text where reference was found

    extracted_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (github_pr_id) REFERENCES github_pull_requests(pr_id),
    FOREIGN KEY (github_issue_id) REFERENCES github_issues(issue_id),
    FOREIGN KEY (jira_issue_id) REFERENCES jira_issues(issue_id)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- JIRA indexes
CREATE INDEX IF NOT EXISTS idx_jira_issues_project ON jira_issues(project_id);
CREATE INDEX IF NOT EXISTS idx_jira_issues_type ON jira_issues(issue_type_id);
CREATE INDEX IF NOT EXISTS idx_jira_issues_key ON jira_issues(key);
CREATE INDEX IF NOT EXISTS idx_jira_issues_status ON jira_issues(status);
CREATE INDEX IF NOT EXISTS idx_jira_issues_created ON jira_issues(created_at);
CREATE INDEX IF NOT EXISTS idx_jira_comments_issue ON jira_comments(issue_id);

-- GitHub indexes
CREATE INDEX IF NOT EXISTS idx_github_prs_repo ON github_pull_requests(repo_id);
CREATE INDEX IF NOT EXISTS idx_github_prs_number ON github_pull_requests(number);
CREATE INDEX IF NOT EXISTS idx_github_prs_state ON github_pull_requests(state);
CREATE INDEX IF NOT EXISTS idx_github_prs_created ON github_pull_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_github_prs_author ON github_pull_requests(author);

CREATE INDEX IF NOT EXISTS idx_github_issues_repo ON github_issues(repo_id);
CREATE INDEX IF NOT EXISTS idx_github_issues_number ON github_issues(number);
CREATE INDEX IF NOT EXISTS idx_github_issues_state ON github_issues(state);

CREATE INDEX IF NOT EXISTS idx_github_commits_repo ON github_commits(repo_id);
CREATE INDEX IF NOT EXISTS idx_github_commits_sha ON github_commits(sha);
CREATE INDEX IF NOT EXISTS idx_github_commits_date ON github_commits(author_date);

CREATE INDEX IF NOT EXISTS idx_github_pr_commits_pr ON github_pr_commits(pr_id);
CREATE INDEX IF NOT EXISTS idx_github_pr_commits_sha ON github_pr_commits(commit_sha);

-- Correlation indexes
CREATE INDEX IF NOT EXISTS idx_github_jira_refs_pr ON github_jira_references(github_pr_id);
CREATE INDEX IF NOT EXISTS idx_github_jira_refs_issue ON github_jira_references(github_issue_id);
CREATE INDEX IF NOT EXISTS idx_github_jira_refs_commit ON github_jira_references(github_commit_sha);
CREATE INDEX IF NOT EXISTS idx_github_jira_refs_jira_key ON github_jira_references(jira_issue_key);
CREATE INDEX IF NOT EXISTS idx_github_jira_refs_jira_id ON github_jira_references(jira_issue_id);

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- View: PRs with linked JIRA issues
CREATE VIEW IF NOT EXISTS v_prs_with_jira AS
SELECT
    pr.pr_id,
    pr.number,
    pr.title,
    pr.state,
    pr.author,
    pr.created_at,
    pr.merged_at,
    GROUP_CONCAT(DISTINCT ref.jira_issue_key) as jira_keys,
    COUNT(DISTINCT ref.jira_issue_key) as jira_count
FROM github_pull_requests pr
LEFT JOIN github_jira_references ref ON ref.github_pr_id = pr.pr_id
GROUP BY pr.pr_id;

-- View: JIRA issues with linked GitHub PRs
CREATE VIEW IF NOT EXISTS v_jira_with_prs AS
SELECT
    ji.issue_id,
    ji.key,
    ji.summary,
    ji.status,
    ji.priority,
    GROUP_CONCAT(DISTINCT pr.number) as pr_numbers,
    COUNT(DISTINCT ref.github_pr_id) as pr_count
FROM jira_issues ji
LEFT JOIN github_jira_references ref ON ref.jira_issue_key = ji.key
LEFT JOIN github_pull_requests pr ON pr.pr_id = ref.github_pr_id
GROUP BY ji.issue_id;

-- View: Recent activity (GitHub + JIRA)
CREATE VIEW IF NOT EXISTS v_recent_activity AS
SELECT
    'github_pr' as source,
    pr.number as identifier,
    pr.title as title,
    pr.state as status,
    pr.author as author,
    pr.created_at as activity_date,
    pr.github_url as url
FROM github_pull_requests pr
UNION ALL
SELECT
    'jira_issue' as source,
    ji.key as identifier,
    ji.summary as title,
    ji.status as status,
    ji.reporter as author,
    ji.created_at as activity_date,
    ji.jira_url as url
FROM jira_issues ji
ORDER BY activity_date DESC;
