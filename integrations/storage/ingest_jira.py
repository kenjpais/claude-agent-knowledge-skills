#!/usr/bin/env python3
"""
JIRA data ingestion using JIRA MCP server or public API.
Fetches issues referenced by GitHub items and enriches correlation.
"""

import os
import sys
import json
from typing import List, Dict, Set, Optional
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'jira'))
sys.path.insert(0, str(Path(__file__).parent))

from public_jira_client import PublicJiraClient
from database import KnowledgeDatabase


class JiraIngester:
    """Ingest JIRA data into knowledge database."""

    def __init__(self, db: KnowledgeDatabase = None, jira_url: str = None):
        """
        Initialize ingester.

        Args:
            db: Knowledge database instance
            jira_url: JIRA base URL (default: Red Hat public JIRA)
        """
        self.db = db or KnowledgeDatabase()
        self.jira_client = PublicJiraClient(jira_url or "https://issues.redhat.com")

    def ingest_issue(self, issue_key: str) -> Optional[int]:
        """
        Ingest a single JIRA issue.

        Args:
            issue_key: JIRA issue key (e.g., 'OCPCLOUD-123')

        Returns:
            Issue ID if successful, None otherwise
        """
        try:
            issue_data = self.jira_client.get_issue(issue_key)

            if not issue_data or 'key' not in issue_data:
                print(f"   ⚠️  Issue not found: {issue_key}")
                return None

            issue_id = self.db.store_jira_issue(issue_data)
            return issue_id

        except Exception as e:
            print(f"   ❌ Error ingesting {issue_key}: {e}")
            return None

    def ingest_issues_by_keys(self, issue_keys: List[str]) -> Dict:
        """
        Ingest multiple JIRA issues by their keys.

        Args:
            issue_keys: List of JIRA issue keys

        Returns:
            Statistics dictionary
        """
        print(f"📥 Ingesting {len(issue_keys)} JIRA issues...")

        stats = {
            'total': len(issue_keys),
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

        for i, key in enumerate(issue_keys, 1):
            # Check if already ingested
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT issue_id FROM jira_issues WHERE key = ?", (key,))
                if cursor.fetchone():
                    stats['skipped'] += 1
                    continue

            # Ingest issue
            issue_id = self.ingest_issue(key)

            if issue_id:
                stats['success'] += 1
                if stats['success'] % 10 == 0:
                    print(f"   📝 Processed {stats['success']} issues...")
            else:
                stats['failed'] += 1

        print(f"   ✅ Ingested {stats['success']} new issues")
        print(f"   ⏭️  Skipped {stats['skipped']} existing issues")
        if stats['failed'] > 0:
            print(f"   ❌ Failed {stats['failed']} issues")

        return stats

    def ingest_referenced_issues(self, update_correlations: bool = True) -> Dict:
        """
        Ingest all JIRA issues referenced in GitHub data.

        Args:
            update_correlations: Update correlation table with JIRA IDs

        Returns:
            Statistics dictionary
        """
        print("🔗 Ingesting JIRA issues referenced by GitHub...")

        # Get all referenced JIRA keys
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT DISTINCT jira_issue_key
                   FROM github_jira_references
                   WHERE jira_issue_id IS NULL"""
            )
            issue_keys = [row[0] for row in cursor.fetchall()]

        if not issue_keys:
            print("   ℹ️  No unreferenced JIRA issues found")
            return {'total': 0, 'success': 0}

        # Ingest issues
        stats = self.ingest_issues_by_keys(issue_keys)

        # Update correlations
        if update_correlations and stats['success'] > 0:
            self._update_correlations()

        return stats

    def _update_correlations(self):
        """Update github_jira_references with JIRA issue IDs."""
        print("🔄 Updating correlations with JIRA issue IDs...")

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """UPDATE github_jira_references
                   SET jira_issue_id = (
                       SELECT issue_id FROM jira_issues
                       WHERE jira_issues.key = github_jira_references.jira_issue_key
                   )
                   WHERE jira_issue_id IS NULL"""
            )

            updated = cursor.rowcount
            conn.commit()

            print(f"   ✅ Updated {updated} correlations")

    def ingest_project_issues(
        self,
        project_key: str,
        jql_filter: str = None,
        max_results: int = 100
    ) -> Dict:
        """
        Ingest issues from a JIRA project.

        Args:
            project_key: JIRA project key (e.g., 'OCPCLOUD')
            jql_filter: Additional JQL filter
            max_results: Maximum issues to fetch

        Returns:
            Statistics dictionary
        """
        print(f"📦 Ingesting JIRA project: {project_key}")

        # Build JQL query
        jql = f'project = {project_key}'
        if jql_filter:
            jql += f' AND ({jql_filter})'

        # Fetch issues
        issues = self.jira_client.search_issues(
            jql=jql,
            fields=['summary', 'description', 'status', 'priority', 'issuetype',
                    'project', 'assignee', 'reporter', 'labels', 'components',
                    'created', 'updated', 'resolutiondate', 'resolution'],
            max_results=max_results
        )

        if not issues:
            print(f"   ⚠️  No issues found for project: {project_key}")
            return {'total': 0, 'success': 0}

        print(f"   📥 Found {len(issues)} issues")

        stats = {
            'total': len(issues),
            'success': 0,
            'failed': 0
        }

        for issue in issues:
            try:
                self.db.store_jira_issue(issue)
                stats['success'] += 1

                if stats['success'] % 10 == 0:
                    print(f"   📝 Processed {stats['success']} issues...")

            except Exception as e:
                print(f"   ❌ Error ingesting {issue.get('key', 'unknown')}: {e}")
                stats['failed'] += 1

        print(f"   ✅ Ingested {stats['success']} issues")
        if stats['failed'] > 0:
            print(f"   ❌ Failed {stats['failed']} issues")

        return stats

    def ingest_recent_issues(
        self,
        project_key: str,
        days: int = 90,
        max_results: int = 100
    ) -> Dict:
        """
        Ingest recent issues from a project.

        Args:
            project_key: JIRA project key
            days: Number of days to look back
            max_results: Maximum issues to fetch

        Returns:
            Statistics dictionary
        """
        jql_filter = f'created >= -{days}d'
        return self.ingest_project_issues(project_key, jql_filter, max_results)

    def ingest_features_and_bugs(
        self,
        project_key: str,
        component: str = None,
        max_results: int = 100
    ) -> Dict:
        """
        Ingest features and bugs for documentation generation.

        Args:
            project_key: JIRA project key
            component: Optional component filter
            max_results: Maximum issues to fetch

        Returns:
            Statistics dictionary
        """
        print(f"🎯 Ingesting features and bugs for documentation...")

        # Build JQL filter
        jql_filter = 'type IN (Feature, Bug, Epic)'
        if component:
            jql_filter += f' AND component = "{component}"'

        return self.ingest_project_issues(project_key, jql_filter, max_results)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Ingest JIRA data into knowledge database'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Ingest by keys
    keys_parser = subparsers.add_parser('keys', help='Ingest specific JIRA issues')
    keys_parser.add_argument('keys', nargs='+', help='JIRA issue keys')

    # Ingest referenced issues
    ref_parser = subparsers.add_parser(
        'referenced',
        help='Ingest issues referenced in GitHub data'
    )

    # Ingest project
    project_parser = subparsers.add_parser('project', help='Ingest JIRA project')
    project_parser.add_argument('project_key', help='JIRA project key')
    project_parser.add_argument('--filter', help='Additional JQL filter')
    project_parser.add_argument('--limit', type=int, default=100, help='Max issues')

    # Ingest recent
    recent_parser = subparsers.add_parser('recent', help='Ingest recent issues')
    recent_parser.add_argument('project_key', help='JIRA project key')
    recent_parser.add_argument('--days', type=int, default=90, help='Days to look back')
    recent_parser.add_argument('--limit', type=int, default=100, help='Max issues')

    # Common arguments
    parser.add_argument('--jira-url', help='JIRA base URL (default: Red Hat JIRA)')
    parser.add_argument('--db', help='Database path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize database
    db = KnowledgeDatabase(args.db) if args.db else KnowledgeDatabase()

    # Initialize ingester
    ingester = JiraIngester(db, args.jira_url)

    # Run command
    try:
        if args.command == 'keys':
            stats = ingester.ingest_issues_by_keys(args.keys)

        elif args.command == 'referenced':
            stats = ingester.ingest_referenced_issues()

        elif args.command == 'project':
            stats = ingester.ingest_project_issues(
                args.project_key,
                args.filter,
                args.limit
            )

        elif args.command == 'recent':
            stats = ingester.ingest_recent_issues(
                args.project_key,
                args.days,
                args.limit
            )

        print(f"\n📊 Final statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
