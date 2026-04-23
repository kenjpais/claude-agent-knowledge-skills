#!/usr/bin/env python3
"""
Database utilities for GitHub and JIRA data storage.
Uses SQLite for lightweight local storage.
"""

import os
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager


class KnowledgeDatabase:
    """SQLite database for GitHub and JIRA data with correlation."""

    def __init__(self, db_path: str = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file (default: ~/.agent-knowledge/data.db)
        """
        if db_path is None:
            db_dir = Path.home() / ".agent-knowledge"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "data.db")

        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize database schema."""
        schema_path = Path(__file__).parent / "schema.sql"

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Read and execute schema
            if schema_path.exists():
                schema_sql = schema_path.read_text()
                cursor.executescript(schema_sql)
                conn.commit()
            else:
                print(f"Warning: Schema file not found at {schema_path}")

            # Initialize issue types if empty
            cursor.execute("SELECT COUNT(*) FROM jira_issue_types")
            if cursor.fetchone()[0] == 0:
                self._init_issue_types(cursor)
                conn.commit()

    def _init_issue_types(self, cursor):
        """Initialize default JIRA issue types."""
        issue_types = [
            (1, 'Epic', 1, 'Large body of work'),
            (2, 'Story', 2, 'User story'),
            (3, 'Task', 3, 'Task to be completed'),
            (4, 'Bug', 3, 'Software defect'),
            (5, 'Feature', 2, 'New feature request'),
            (6, 'Improvement', 3, 'Enhancement to existing feature'),
            (7, 'Sub-task', 4, 'Breakdown of a task'),
        ]

        cursor.executemany(
            """INSERT OR IGNORE INTO jira_issue_types
               (issue_type_id, name, hierarchy_level, description)
               VALUES (?, ?, ?, ?)""",
            issue_types
        )

    @contextmanager
    def get_connection(self):
        """Get database connection (context manager)."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()

    # ============================================
    # GITHUB STORAGE
    # ============================================

    def store_github_repository(self, repo_data: Dict) -> int:
        """Store GitHub repository."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """INSERT OR REPLACE INTO github_repositories
                   (repo_id, owner, name, full_name, description,
                    default_branch, language, stars, forks, open_issues,
                    created_at, updated_at, pushed_at, github_url)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    repo_data['id'],
                    repo_data['owner']['login'],
                    repo_data['name'],
                    repo_data['full_name'],
                    repo_data.get('description'),
                    repo_data.get('default_branch'),
                    repo_data.get('language'),
                    repo_data.get('stargazers_count', 0),
                    repo_data.get('forks_count', 0),
                    repo_data.get('open_issues_count', 0),
                    repo_data.get('created_at'),
                    repo_data.get('updated_at'),
                    repo_data.get('pushed_at'),
                    repo_data.get('html_url'),
                )
            )
            conn.commit()
            return repo_data['id']

    def store_github_pull_request(self, pr_data: Dict, repo_id: int) -> int:
        """Store GitHub pull request."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """INSERT OR REPLACE INTO github_pull_requests
                   (pr_id, repo_id, number, title, body, state, draft,
                    author, assignees, reviewers, base_branch, head_branch,
                    labels, created_at, updated_at, closed_at, merged_at,
                    merge_commit_sha, additions, deletions, changed_files,
                    github_url, raw_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    pr_data['id'],
                    repo_id,
                    pr_data['number'],
                    pr_data['title'],
                    pr_data.get('body'),
                    pr_data['state'],
                    pr_data.get('draft', False),
                    pr_data['user']['login'],
                    json.dumps([a['login'] for a in pr_data.get('assignees', [])]),
                    json.dumps([r['login'] for r in pr_data.get('requested_reviewers', [])]),
                    pr_data['base']['ref'],
                    pr_data['head']['ref'],
                    json.dumps([l['name'] for l in pr_data.get('labels', [])]),
                    pr_data['created_at'],
                    pr_data['updated_at'],
                    pr_data.get('closed_at'),
                    pr_data.get('merged_at'),
                    pr_data.get('merge_commit_sha'),
                    pr_data.get('additions'),
                    pr_data.get('deletions'),
                    pr_data.get('changed_files'),
                    pr_data['html_url'],
                    json.dumps(pr_data),
                )
            )
            conn.commit()
            return pr_data['id']

    def store_github_issue(self, issue_data: Dict, repo_id: int) -> int:
        """Store GitHub issue."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """INSERT OR REPLACE INTO github_issues
                   (issue_id, repo_id, number, title, body, state,
                    author, assignees, labels, created_at, updated_at,
                    closed_at, github_url, raw_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    issue_data['id'],
                    repo_id,
                    issue_data['number'],
                    issue_data['title'],
                    issue_data.get('body'),
                    issue_data['state'],
                    issue_data['user']['login'],
                    json.dumps([a['login'] for a in issue_data.get('assignees', [])]),
                    json.dumps([l['name'] for l in issue_data.get('labels', [])]),
                    issue_data['created_at'],
                    issue_data['updated_at'],
                    issue_data.get('closed_at'),
                    issue_data['html_url'],
                    json.dumps(issue_data),
                )
            )
            conn.commit()
            return issue_data['id']

    def store_github_commit(self, commit_data: Dict, repo_id: int) -> int:
        """Store GitHub commit."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """INSERT OR IGNORE INTO github_commits
                   (repo_id, sha, message, author_name, author_email, author_date,
                    committer_name, committer_email, committer_date,
                    parents, additions, deletions, changed_files,
                    github_url, raw_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    repo_id,
                    commit_data['sha'],
                    commit_data['commit']['message'],
                    commit_data['commit']['author'].get('name'),
                    commit_data['commit']['author'].get('email'),
                    commit_data['commit']['author'].get('date'),
                    commit_data['commit']['committer'].get('name'),
                    commit_data['commit']['committer'].get('email'),
                    commit_data['commit']['committer'].get('date'),
                    json.dumps([p['sha'] for p in commit_data.get('parents', [])]),
                    commit_data['stats'].get('additions') if 'stats' in commit_data else None,
                    commit_data['stats'].get('deletions') if 'stats' in commit_data else None,
                    len(commit_data.get('files', [])),
                    commit_data.get('html_url'),
                    json.dumps(commit_data),
                )
            )
            conn.commit()
            return cursor.lastrowid

    # ============================================
    # JIRA STORAGE
    # ============================================

    def store_jira_project(self, project_data: Dict) -> int:
        """Store JIRA project."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """INSERT OR REPLACE INTO jira_projects
                   (project_id, project_key, name, description, jira_url)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    int(project_data['id']) if 'id' in project_data else hash(project_data['key']),
                    project_data['key'],
                    project_data['name'],
                    project_data.get('description'),
                    project_data.get('self'),
                )
            )
            conn.commit()
            return cursor.lastrowid

    def store_jira_issue(self, issue_data: Dict) -> int:
        """Store JIRA issue."""
        fields = issue_data['fields']

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get or create project
            project_key = issue_data['fields']['project']['key']
            cursor.execute(
                "SELECT project_id FROM jira_projects WHERE project_key = ?",
                (project_key,)
            )
            result = cursor.fetchone()
            if result:
                project_id = result[0]
            else:
                project_id = self.store_jira_project(fields['project'])

            # Get issue type ID
            issue_type_name = fields['issuetype']['name']
            cursor.execute(
                "SELECT issue_type_id FROM jira_issue_types WHERE name = ?",
                (issue_type_name,)
            )
            result = cursor.fetchone()
            issue_type_id = result[0] if result else 3  # Default to Task

            cursor.execute(
                """INSERT OR REPLACE INTO jira_issues
                   (project_id, issue_type_id, key, summary, description,
                    status, priority, resolution, assignee, reporter,
                    labels, components, created_at, updated_at,
                    resolved_at, due_date, jira_url, raw_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    project_id,
                    issue_type_id,
                    issue_data['key'],
                    fields['summary'],
                    fields.get('description'),
                    fields['status']['name'] if fields.get('status') else None,
                    fields['priority']['name'] if fields.get('priority') else None,
                    fields['resolution']['name'] if fields.get('resolution') else None,
                    fields['assignee']['displayName'] if fields.get('assignee') else None,
                    fields['reporter']['displayName'] if fields.get('reporter') else None,
                    json.dumps(fields.get('labels', [])),
                    json.dumps([c['name'] for c in fields.get('components', [])]),
                    fields.get('created'),
                    fields.get('updated'),
                    fields.get('resolutiondate'),
                    fields.get('duedate'),
                    issue_data.get('self'),
                    json.dumps(issue_data),
                )
            )
            conn.commit()

            # Get the issue_id
            cursor.execute("SELECT issue_id FROM jira_issues WHERE key = ?", (issue_data['key'],))
            return cursor.fetchone()[0]

    # ============================================
    # CORRELATION STORAGE
    # ============================================

    def store_github_jira_reference(
        self,
        jira_key: str,
        reference_type: str,
        reference_context: str = None,
        github_pr_id: int = None,
        github_issue_id: int = None,
        github_commit_sha: str = None,
    ) -> int:
        """Store a GitHub → JIRA reference."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Try to get JIRA issue_id if it exists
            cursor.execute(
                "SELECT issue_id FROM jira_issues WHERE key = ?",
                (jira_key,)
            )
            result = cursor.fetchone()
            jira_issue_id = result[0] if result else None

            cursor.execute(
                """INSERT OR IGNORE INTO github_jira_references
                   (github_pr_id, github_issue_id, github_commit_sha,
                    jira_issue_key, jira_issue_id, reference_type, reference_context)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    github_pr_id,
                    github_issue_id,
                    github_commit_sha,
                    jira_key,
                    jira_issue_id,
                    reference_type,
                    reference_context,
                )
            )
            conn.commit()
            return cursor.lastrowid

    # ============================================
    # RETRIEVAL METHODS
    # ============================================

    def get_prs_with_jira(self, repo_id: int = None, limit: int = 100) -> List[Dict]:
        """Get pull requests with linked JIRA issues."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT
                    pr.*,
                    GROUP_CONCAT(DISTINCT ref.jira_issue_key) as jira_keys
                FROM github_pull_requests pr
                LEFT JOIN github_jira_references ref ON ref.github_pr_id = pr.pr_id
                WHERE 1=1
            """

            params = []
            if repo_id:
                query += " AND pr.repo_id = ?"
                params.append(repo_id)

            query += " GROUP BY pr.pr_id ORDER BY pr.created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_jira_issues_with_github(
        self,
        project_key: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get JIRA issues with linked GitHub items."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT
                    ji.*,
                    GROUP_CONCAT(DISTINCT pr.number) as pr_numbers,
                    COUNT(DISTINCT ref.github_pr_id) as pr_count
                FROM jira_issues ji
                LEFT JOIN github_jira_references ref ON ref.jira_issue_key = ji.key
                LEFT JOIN github_pull_requests pr ON pr.pr_id = ref.github_pr_id
                WHERE 1=1
            """

            params = []
            if project_key:
                query += """
                    AND ji.project_id IN (
                        SELECT project_id FROM jira_projects WHERE project_key = ?
                    )
                """
                params.append(project_key)

            query += " GROUP BY ji.issue_id ORDER BY ji.created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict:
        """Get database statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # GitHub stats
            cursor.execute("SELECT COUNT(*) FROM github_repositories")
            stats['github_repos'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM github_pull_requests")
            stats['github_prs'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM github_issues")
            stats['github_issues'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM github_commits")
            stats['github_commits'] = cursor.fetchone()[0]

            # JIRA stats
            cursor.execute("SELECT COUNT(*) FROM jira_projects")
            stats['jira_projects'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM jira_issues")
            stats['jira_issues'] = cursor.fetchone()[0]

            # Correlation stats
            cursor.execute("SELECT COUNT(*) FROM github_jira_references")
            stats['correlations'] = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(DISTINCT jira_issue_key) FROM github_jira_references"
            )
            stats['jira_issues_referenced'] = cursor.fetchone()[0]

            return stats
