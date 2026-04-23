#!/usr/bin/env python3
"""
GitHub data ingestion using GitHub MCP server.
Fetches PRs, issues, commits and extracts JIRA references.
"""

import re
import os
import sys
import json
import subprocess
from typing import List, Dict, Set
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from database import KnowledgeDatabase


class JiraKeyExtractor:
    """Extract JIRA keys from text."""

    # Common JIRA project prefixes for OpenShift
    COMMON_PREFIXES = [
        'OCPCLOUD', 'OCPBUGS', 'OCPPLAN', 'SPLAT',
        'CNV', 'MULTIARCH', 'ROSA', 'HIVE',
        'OSDE2E', 'SDthe', 'API', 'MON',
    ]

    # Pattern: PROJECT-1234 or PROJECT-1234
    JIRA_PATTERN = re.compile(
        r'\b([A-Z]{2,10})-(\d+)\b'
    )

    @classmethod
    def extract(cls, text: str) -> Set[str]:
        """
        Extract JIRA issue keys from text.

        Args:
            text: Text to search

        Returns:
            Set of JIRA keys found (e.g., {'OCPCLOUD-123', 'API-456'})
        """
        if not text:
            return set()

        keys = set()
        for match in cls.JIRA_PATTERN.finditer(text):
            prefix = match.group(1)
            number = match.group(2)
            key = f"{prefix}-{number}"

            # Filter out common false positives
            if prefix not in ['PR', 'GO', 'HTTP', 'HTTPS', 'SHA', 'API', 'AWS', 'GCP']:
                keys.add(key)

        return keys

    @classmethod
    def extract_with_context(cls, text: str, context_chars: int = 50) -> List[Dict]:
        """
        Extract JIRA keys with surrounding context.

        Returns:
            List of {key, context} dictionaries
        """
        if not text:
            return []

        results = []
        for match in cls.JIRA_PATTERN.finditer(text):
            key = f"{match.group(1)}-{match.group(2)}"

            # Extract context around the match
            start = max(0, match.start() - context_chars)
            end = min(len(text), match.end() + context_chars)
            context = text[start:end].strip()

            results.append({
                'key': key,
                'context': context
            })

        return results


class GitHubIngester:
    """Ingest GitHub data using GitHub MCP server."""

    def __init__(self, db: KnowledgeDatabase = None):
        """Initialize ingester."""
        self.db = db or KnowledgeDatabase()
        self.jira_extractor = JiraKeyExtractor()

    def _call_gh_api(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Call GitHub API using gh CLI (through MCP server or directly).

        Args:
            endpoint: API endpoint (e.g., 'repos/owner/repo')
            params: Query parameters

        Returns:
            API response as dictionary
        """
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
        except subprocess.CalledProcessError as e:
            print(f"GitHub API error: {e.stderr}", file=sys.stderr)
            return {}
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}", file=sys.stderr)
            return {}

    def ingest_repository(self, owner: str, repo: str) -> int:
        """
        Ingest repository metadata.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Repository ID
        """
        print(f"📦 Ingesting repository: {owner}/{repo}")

        repo_data = self._call_gh_api(f'repos/{owner}/{repo}')

        if not repo_data:
            raise ValueError(f"Failed to fetch repository: {owner}/{repo}")

        repo_id = self.db.store_github_repository(repo_data)
        print(f"   ✅ Stored repository (ID: {repo_id})")

        return repo_id

    def ingest_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = 'all',
        limit: int = 100
    ) -> int:
        """
        Ingest pull requests and extract JIRA references.

        Args:
            owner: Repository owner
            repo: Repository name
            state: PR state (open, closed, all)
            limit: Maximum PRs to fetch

        Returns:
            Number of PRs ingested
        """
        print(f"🔍 Ingesting pull requests: {owner}/{repo} (state={state}, limit={limit})")

        # Ensure repository exists
        repo_id = self.ingest_repository(owner, repo)

        # Fetch PRs
        prs = self._call_gh_api(
            f'repos/{owner}/{repo}/pulls',
            {'state': state, 'per_page': str(min(limit, 100))}
        )

        if not isinstance(prs, list):
            print(f"   ⚠️  No PRs returned or API error")
            return 0

        count = 0
        for pr in prs[:limit]:
            # Store PR
            pr_id = self.db.store_github_pull_request(pr, repo_id)
            count += 1

            # Extract JIRA references from PR
            self._extract_pr_jira_references(pr, pr_id)

            if count % 10 == 0:
                print(f"   📝 Processed {count} PRs...")

        print(f"   ✅ Ingested {count} pull requests")
        return count

    def _extract_pr_jira_references(self, pr: Dict, pr_id: int):
        """Extract and store JIRA references from a PR."""
        # Extract from title
        title_keys = self.jira_extractor.extract(pr.get('title', ''))
        for key in title_keys:
            self.db.store_github_jira_reference(
                jira_key=key,
                reference_type='pr_title',
                reference_context=pr['title'][:200],
                github_pr_id=pr_id
            )

        # Extract from body
        body_refs = self.jira_extractor.extract_with_context(pr.get('body', ''))
        for ref in body_refs:
            self.db.store_github_jira_reference(
                jira_key=ref['key'],
                reference_type='pr_body',
                reference_context=ref['context'],
                github_pr_id=pr_id
            )

    def ingest_issues(
        self,
        owner: str,
        repo: str,
        state: str = 'all',
        limit: int = 100
    ) -> int:
        """
        Ingest GitHub issues and extract JIRA references.

        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (open, closed, all)
            limit: Maximum issues to fetch

        Returns:
            Number of issues ingested
        """
        print(f"🐛 Ingesting issues: {owner}/{repo} (state={state}, limit={limit})")

        # Ensure repository exists
        repo_id = self.ingest_repository(owner, repo)

        # Fetch issues
        issues = self._call_gh_api(
            f'repos/{owner}/{repo}/issues',
            {'state': state, 'per_page': str(min(limit, 100))}
        )

        if not isinstance(issues, list):
            print(f"   ⚠️  No issues returned or API error")
            return 0

        count = 0
        for issue in issues[:limit]:
            # Skip pull requests (they also appear in issues API)
            if 'pull_request' in issue:
                continue

            # Store issue
            issue_id = self.db.store_github_issue(issue, repo_id)
            count += 1

            # Extract JIRA references
            self._extract_issue_jira_references(issue, issue_id)

            if count % 10 == 0:
                print(f"   📝 Processed {count} issues...")

        print(f"   ✅ Ingested {count} issues")
        return count

    def _extract_issue_jira_references(self, issue: Dict, issue_id: int):
        """Extract and store JIRA references from an issue."""
        # Extract from title
        title_keys = self.jira_extractor.extract(issue.get('title', ''))
        for key in title_keys:
            self.db.store_github_jira_reference(
                jira_key=key,
                reference_type='issue_title',
                reference_context=issue['title'][:200],
                github_issue_id=issue_id
            )

        # Extract from body
        body_refs = self.jira_extractor.extract_with_context(issue.get('body', ''))
        for ref in body_refs:
            self.db.store_github_jira_reference(
                jira_key=ref['key'],
                reference_type='issue_body',
                reference_context=ref['context'],
                github_issue_id=issue_id
            )

    def ingest_commits(
        self,
        owner: str,
        repo: str,
        branch: str = 'main',
        limit: int = 100
    ) -> int:
        """
        Ingest recent commits and extract JIRA references.

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            limit: Maximum commits to fetch

        Returns:
            Number of commits ingested
        """
        print(f"📝 Ingesting commits: {owner}/{repo} (branch={branch}, limit={limit})")

        # Ensure repository exists
        repo_id = self.ingest_repository(owner, repo)

        # Fetch commits
        commits = self._call_gh_api(
            f'repos/{owner}/{repo}/commits',
            {'sha': branch, 'per_page': str(min(limit, 100))}
        )

        if not isinstance(commits, list):
            print(f"   ⚠️  No commits returned or API error")
            return 0

        count = 0
        for commit in commits[:limit]:
            # Store commit
            self.db.store_github_commit(commit, repo_id)
            count += 1

            # Extract JIRA references from commit message
            self._extract_commit_jira_references(commit)

            if count % 10 == 0:
                print(f"   📝 Processed {count} commits...")

        print(f"   ✅ Ingested {count} commits")
        return count

    def _extract_commit_jira_references(self, commit: Dict):
        """Extract and store JIRA references from commit message."""
        message = commit['commit']['message']
        refs = self.jira_extractor.extract_with_context(message)

        for ref in refs:
            self.db.store_github_jira_reference(
                jira_key=ref['key'],
                reference_type='commit_message',
                reference_context=ref['context'],
                github_commit_sha=commit['sha']
            )

    def ingest_full_repository(
        self,
        owner: str,
        repo: str,
        pr_limit: int = 100,
        issue_limit: int = 100,
        commit_limit: int = 100
    ) -> Dict:
        """
        Ingest all data for a repository.

        Returns:
            Statistics dictionary
        """
        print(f"\n🚀 Full ingestion: {owner}/{repo}\n")

        stats = {}

        try:
            # Repository metadata
            stats['repo_id'] = self.ingest_repository(owner, repo)

            # Pull requests
            stats['prs'] = self.ingest_pull_requests(owner, repo, limit=pr_limit)

            # Issues
            stats['issues'] = self.ingest_issues(owner, repo, limit=issue_limit)

            # Commits
            stats['commits'] = self.ingest_commits(owner, repo, limit=commit_limit)

            # Get correlation stats
            db_stats = self.db.get_statistics()
            stats['correlations'] = db_stats['correlations']

            print(f"\n✅ Ingestion complete!")
            print(f"   PRs: {stats['prs']}")
            print(f"   Issues: {stats['issues']}")
            print(f"   Commits: {stats['commits']}")
            print(f"   JIRA correlations: {stats['correlations']}")

            return stats

        except Exception as e:
            print(f"\n❌ Ingestion failed: {e}")
            raise


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Ingest GitHub data into knowledge database'
    )
    parser.add_argument('repository', help='Repository in format owner/repo')
    parser.add_argument('--prs', type=int, default=100, help='Max PRs to fetch')
    parser.add_argument('--issues', type=int, default=100, help='Max issues to fetch')
    parser.add_argument('--commits', type=int, default=100, help='Max commits to fetch')
    parser.add_argument('--db', help='Database path (default: ~/.agent-knowledge/data.db)')

    args = parser.parse_args()

    # Parse repository
    if '/' not in args.repository:
        print("Error: Repository must be in format 'owner/repo'")
        sys.exit(1)

    owner, repo = args.repository.split('/', 1)

    # Initialize database
    db = KnowledgeDatabase(args.db) if args.db else KnowledgeDatabase()

    # Initialize ingester
    ingester = GitHubIngester(db)

    # Run ingestion
    try:
        stats = ingester.ingest_full_repository(
            owner, repo,
            pr_limit=args.prs,
            issue_limit=args.issues,
            commit_limit=args.commits
        )

        print(f"\n📊 Final statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
