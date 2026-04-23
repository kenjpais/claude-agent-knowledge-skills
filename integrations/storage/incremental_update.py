#!/usr/bin/env python3
"""
Incremental updates for repositories.
Only fetches new data since last update.
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database import KnowledgeDatabase
from ingest_github import GitHubIngester
from ingest_jira import JiraIngester


class IncrementalUpdater:
    """Incremental updates for existing repositories."""

    def __init__(self, db_path: str = None):
        """Initialize updater."""
        self.db = KnowledgeDatabase(db_path)
        self.github_ingester = GitHubIngester(self.db)
        self.jira_ingester = JiraIngester(self.db)

    def _gh_api(self, endpoint: str, params: Dict = None) -> Dict:
        """Call GitHub API."""
        cmd = ['gh', 'api', endpoint]

        if params:
            for key, value in params.items():
                cmd.extend(['-f', f'{key}={value}'])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return {}

    def get_last_update_time(self, owner: str, repo: str) -> Optional[datetime]:
        """
        Get the last update time for a repository.

        Returns:
            Last PR/issue/commit timestamp or None
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Get repo_id
            cursor.execute(
                "SELECT repo_id FROM github_repositories WHERE owner = ? AND name = ?",
                (owner, repo)
            )
            result = cursor.fetchone()

            if not result:
                return None

            repo_id = result[0]

            # Get most recent timestamp across PRs, issues, commits
            cursor.execute(
                """
                SELECT MAX(timestamp) FROM (
                    SELECT MAX(created_at) as timestamp FROM github_pull_requests WHERE repo_id = ?
                    UNION
                    SELECT MAX(created_at) as timestamp FROM github_issues WHERE repo_id = ?
                    UNION
                    SELECT MAX(author_date) as timestamp FROM github_commits WHERE repo_id = ?
                )
                """,
                (repo_id, repo_id, repo_id)
            )

            result = cursor.fetchone()
            if result and result[0]:
                return datetime.fromisoformat(result[0].replace('Z', '+00:00'))

            return None

    def update_repository(
        self,
        owner: str,
        repo: str,
        force_full: bool = False
    ) -> Dict:
        """
        Update a repository incrementally.

        Args:
            owner: Repository owner
            repo: Repository name
            force_full: Force full re-ingestion

        Returns:
            Update statistics
        """
        print(f"\n{'=' * 60}")
        print(f"🔄 Updating: {owner}/{repo}")
        print(f"{'=' * 60}")

        last_update = self.get_last_update_time(owner, repo)

        if not last_update or force_full:
            print("   ℹ️  No previous data, running full ingestion...")
            stats = self.github_ingester.ingest_full_repository(
                owner, repo,
                pr_limit=500,
                issue_limit=200,
                commit_limit=500
            )
            return {
                'type': 'full',
                'stats': stats,
            }

        # Incremental update
        print(f"   ℹ️  Last update: {last_update.isoformat()}")
        since = last_update.isoformat()

        stats = {
            'new_prs': 0,
            'new_issues': 0,
            'new_commits': 0,
            'new_jira_refs': 0,
        }

        # Fetch new PRs
        print(f"   🔍 Fetching PRs since {since}...")
        prs = self._gh_api(
            f'repos/{owner}/{repo}/pulls',
            {'state': 'all', 'sort': 'created', 'direction': 'desc', 'per_page': '100'}
        )

        if isinstance(prs, list):
            repo_id = self.github_ingester.ingest_repository(owner, repo)

            for pr in prs:
                pr_created = datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00'))
                if pr_created <= last_update:
                    break

                self.db.store_github_pull_request(pr, repo_id)
                self.github_ingester._extract_pr_jira_references(pr, pr['id'])
                stats['new_prs'] += 1

        # Fetch new issues
        print(f"   🔍 Fetching issues since {since}...")
        issues = self._gh_api(
            f'repos/{owner}/{repo}/issues',
            {'state': 'all', 'sort': 'created', 'direction': 'desc', 'per_page': '100'}
        )

        if isinstance(issues, list):
            repo_id = self.github_ingester.ingest_repository(owner, repo)

            for issue in issues:
                if 'pull_request' in issue:
                    continue

                issue_created = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
                if issue_created <= last_update:
                    break

                issue_id = self.db.store_github_issue(issue, repo_id)
                self.github_ingester._extract_issue_jira_references(issue, issue_id)
                stats['new_issues'] += 1

        # Fetch new commits
        print(f"   🔍 Fetching commits since {since}...")
        commits = self._gh_api(
            f'repos/{owner}/{repo}/commits',
            {'since': since, 'per_page': '100'}
        )

        if isinstance(commits, list):
            repo_id = self.github_ingester.ingest_repository(owner, repo)

            for commit in commits:
                self.db.store_github_commit(commit, repo_id)
                self.github_ingester._extract_commit_jira_references(commit)
                stats['new_commits'] += 1

        print(f"\n   ✅ Incremental update complete:")
        print(f"      New PRs: {stats['new_prs']}")
        print(f"      New Issues: {stats['new_issues']}")
        print(f"      New Commits: {stats['new_commits']}")

        return {
            'type': 'incremental',
            'since': since,
            'stats': stats,
        }

    def update_jira_references(self) -> Dict:
        """
        Update JIRA issues for new references.

        Returns:
            Update statistics
        """
        print("\n" + "=" * 60)
        print("🔄 Updating JIRA References")
        print("=" * 60)

        stats = self.jira_ingester.ingest_referenced_issues()
        return stats

    def update_all_repositories(self, force_full: bool = False) -> Dict:
        """
        Update all repositories in database.

        Args:
            force_full: Force full re-ingestion

        Returns:
            Overall statistics
        """
        # Get all repositories
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT owner, name FROM github_repositories")
            repos = cursor.fetchall()

        if not repos:
            print("ℹ️  No repositories found in database")
            return {}

        print(f"\n📊 Updating {len(repos)} repositories...")

        results = []
        for owner, name in repos:
            try:
                result = self.update_repository(owner, name, force_full)
                results.append({
                    'repo': f'{owner}/{name}',
                    'status': 'success',
                    'result': result,
                })
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append({
                    'repo': f'{owner}/{name}',
                    'status': 'failed',
                    'error': str(e),
                })

        # Update JIRA references
        jira_stats = self.update_jira_references()

        # Calculate overall stats
        success_count = sum(1 for r in results if r['status'] == 'success')
        failed_count = sum(1 for r in results if r['status'] == 'failed')

        overall_stats = {
            'total_repos': len(repos),
            'success': success_count,
            'failed': failed_count,
            'jira_stats': jira_stats,
            'results': results,
        }

        print("\n" + "=" * 60)
        print("📊 UPDATE COMPLETE")
        print("=" * 60)
        print(f"   Success: {success_count}/{len(repos)}")
        print(f"   Failed: {failed_count}/{len(repos)}")
        print(f"   New JIRA issues: {jira_stats.get('success', 0)}")

        return overall_stats


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Incremental updates for repositories'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Update single repo
    repo_parser = subparsers.add_parser('repo', help='Update single repository')
    repo_parser.add_argument('repository', help='Repository (owner/repo)')
    repo_parser.add_argument('--force-full', action='store_true',
                            help='Force full re-ingestion')

    # Update all repos
    all_parser = subparsers.add_parser('all', help='Update all repositories')
    all_parser.add_argument('--force-full', action='store_true',
                           help='Force full re-ingestion')

    # Update JIRA only
    jira_parser = subparsers.add_parser('jira', help='Update JIRA references only')

    # Common arguments
    parser.add_argument('--db', help='Database path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    updater = IncrementalUpdater(args.db)

    try:
        if args.command == 'repo':
            if '/' not in args.repository:
                print("Error: Repository must be in format 'owner/repo'")
                sys.exit(1)

            owner, repo = args.repository.split('/', 1)
            stats = updater.update_repository(owner, repo, args.force_full)

            print(f"\n📊 Statistics:")
            print(json.dumps(stats, indent=2))

        elif args.command == 'all':
            stats = updater.update_all_repositories(args.force_full)

            with open('update_stats.json', 'w') as f:
                json.dump(stats, f, indent=2)

            print(f"\n📊 Statistics saved to: update_stats.json")

        elif args.command == 'jira':
            stats = updater.update_jira_references()

            print(f"\n📊 Statistics:")
            print(json.dumps(stats, indent=2))

    except KeyboardInterrupt:
        print("\n\n⚠️  Update interrupted")
        sys.exit(130)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
