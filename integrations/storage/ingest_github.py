#!/usr/bin/env python3
"""
GitHub data ingestion using GitHub GraphQL API.
Fetches PRs, issues within a date range and extracts JIRA references.
"""

import re
import sys
import json
import os
import subprocess
from typing import List, Dict, Set, Optional
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (project root)
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from database import KnowledgeDatabase


class JiraKeyExtractor:
    """Extract JIRA keys from text."""

    # Common JIRA project prefixes for OpenShift
    COMMON_PREFIXES = [
        'OCPCLOUD', 'OCPBUGS', 'OCPPLAN', 'SPLAT',
        'CNV', 'MULTIARCH', 'ROSA', 'HIVE',
        'OSDE2E', 'SDE', 'API', 'MON',
    ]

    # Pattern: PROJECT-1234
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
            prefix = match.group(1)
            number = match.group(2)
            key = f"{prefix}-{number}"

            # Filter out common false positives (same as extract method)
            if prefix in ['PR', 'GO', 'HTTP', 'HTTPS', 'SHA', 'API', 'AWS', 'GCP']:
                continue

            # Extract context around the match
            start = max(0, match.start() - context_chars)
            end = min(len(text), match.end() + context_chars)
            context = text[start:end].strip()

            results.append({
                'key': key,
                'context': context
            })

        return results


class GitHubGraphQLIngester:
    """Ingest GitHub data using GitHub GraphQL API."""

    def __init__(self, db: KnowledgeDatabase = None):
        """Initialize ingester."""
        self.db = db or KnowledgeDatabase()
        self.jira_extractor = JiraKeyExtractor()

    def _call_graphql(self, query: str, variables: Dict = None) -> Dict:
        """
        Call GitHub GraphQL API using gh CLI.

        Args:
            query: GraphQL query string
            variables: Query variables

        Returns:
            API response as dictionary
        """
        cmd = ['gh', 'api', 'graphql', '-f', f'query={query}']

        if variables:
            for key, value in variables.items():
                # Convert Python values to JSON strings
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                elif isinstance(value, bool):
                    value = 'true' if value else 'false'
                else:
                    value = str(value)
                cmd.extend(['-f', f'{key}={value}'])

        # Prepare environment with GitHub token from .env file
        env = os.environ.copy()
        gh_token = os.getenv('GH_API_TOKEN')
        if gh_token:
            env['GITHUB_TOKEN'] = gh_token
            env['GH_TOKEN'] = gh_token  # gh CLI also checks GH_TOKEN

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                env=env
            )
            response = json.loads(result.stdout)

            # Check for GraphQL errors
            if 'errors' in response:
                print(f"GraphQL errors: {response['errors']}", file=sys.stderr)
                return {}

            return response.get('data', {})

        except subprocess.CalledProcessError as e:
            # Check if it's a retryable error (502, 503, 504)
            error_msg = e.stderr
            if 'HTTP 502' in error_msg or 'HTTP 503' in error_msg or 'HTTP 504' in error_msg:
                print(f"⚠️  GitHub API temporary error: {error_msg}", file=sys.stderr)
                print("   Retry in a few minutes or check https://www.githubstatus.com", file=sys.stderr)
            else:
                print(f"❌ GitHub GraphQL API error: {error_msg}", file=sys.stderr)
            return {}
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}", file=sys.stderr)
            return {}

    def ingest_repository(self, owner: str, repo: str) -> int:
        """
        Ingest repository metadata using GraphQL.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Repository ID
        """
        print(f"📦 Ingesting repository: {owner}/{repo}")

        query = """
        query($owner: String!, $repo: String!) {
          repository(owner: $owner, name: $repo) {
            id
            databaseId
            name
            nameWithOwner
            description
            defaultBranchRef {
              name
            }
            primaryLanguage {
              name
            }
            stargazerCount
            forkCount
            openIssues: issues(states: OPEN) {
              totalCount
            }
            createdAt
            updatedAt
            pushedAt
            url
          }
        }
        """

        data = self._call_graphql(query, {'owner': owner, 'repo': repo})

        if not data or 'repository' not in data:
            raise ValueError(f"Failed to fetch repository: {owner}/{repo}")

        repo_data = data['repository']

        # Convert GraphQL response to REST API format for compatibility
        rest_format = {
            'id': repo_data['databaseId'],
            'owner': {'login': owner},
            'name': repo_data['name'],
            'full_name': repo_data['nameWithOwner'],
            'description': repo_data.get('description'),
            'default_branch': repo_data['defaultBranchRef']['name'] if repo_data.get('defaultBranchRef') else None,
            'language': repo_data['primaryLanguage']['name'] if repo_data.get('primaryLanguage') else None,
            'stargazers_count': repo_data.get('stargazerCount', 0),
            'forks_count': repo_data.get('forkCount', 0),
            'open_issues_count': repo_data['openIssues']['totalCount'] if repo_data.get('openIssues') else 0,
            'created_at': repo_data.get('createdAt'),
            'updated_at': repo_data.get('updatedAt'),
            'pushed_at': repo_data.get('pushedAt'),
            'html_url': repo_data.get('url'),
        }

        repo_id = self.db.store_github_repository(rest_format)
        print(f"   ✅ Stored repository (ID: {repo_id})")

        return repo_id

    def ingest_pull_requests(
        self,
        owner: str,
        repo: str,
        since_date: Optional[datetime] = None,
        until_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> int:
        """
        Ingest pull requests within date range using GraphQL.

        Args:
            owner: Repository owner
            repo: Repository name
            since_date: Start date (default: 1 year ago)
            until_date: End date (default: now)
            limit: Maximum PRs to fetch

        Returns:
            Number of PRs ingested
        """
        # Default to past year
        if since_date is None:
            since_date = datetime.now(timezone.utc) - timedelta(days=365)
        if until_date is None:
            until_date = datetime.now(timezone.utc)

        # Ensure dates are timezone-aware (convert to UTC if naive)
        if since_date.tzinfo is None:
            since_date = since_date.replace(tzinfo=timezone.utc)
        if until_date.tzinfo is None:
            until_date = until_date.replace(tzinfo=timezone.utc)

        # Validate date range
        if since_date > until_date:
            raise ValueError(f"since_date ({since_date.date()}) must be before until_date ({until_date.date()})")

        print(f"🔍 Ingesting pull requests: {owner}/{repo}")
        print(f"   Date range: {since_date.date()} to {until_date.date()}")

        # Get repository ID (avoid re-ingesting if possible)
        # Check if repo already exists in DB
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT repo_id FROM github_repositories WHERE owner = ? AND name = ?",
                (owner, repo)
            )
            result = cursor.fetchone()
            repo_id = result[0] if result else self.ingest_repository(owner, repo)

        query = """
        query($owner: String!, $repo: String!, $cursor: String) {
          repository(owner: $owner, name: $repo) {
            pullRequests(first: 100, after: $cursor, orderBy: {field: CREATED_AT, direction: DESC}) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                id
                databaseId
                number
                title
                body
                state
                isDraft
                createdAt
                updatedAt
                closedAt
                mergedAt
                url
                author {
                  login
                }
                assignees(first: 10) {
                  nodes {
                    login
                  }
                }
                reviewRequests(first: 10) {
                  nodes {
                    requestedReviewer {
                      ... on User {
                        login
                      }
                    }
                  }
                }
                labels(first: 20) {
                  nodes {
                    name
                  }
                }
                baseRef {
                  name
                }
                headRef {
                  name
                }
                mergeCommit {
                  oid
                }
                additions
                deletions
                changedFiles
              }
            }
          }
        }
        """

        count = 0
        cursor = None
        has_next_page = True

        while has_next_page and count < limit:
            variables = {'owner': owner, 'repo': repo}
            if cursor:
                variables['cursor'] = cursor

            data = self._call_graphql(query, variables)

            if not data or 'repository' not in data:
                break

            pull_requests = data['repository']['pullRequests']

            for pr in pull_requests['nodes']:
                # Check date range
                created_at = datetime.fromisoformat(pr['createdAt'].replace('Z', '+00:00'))

                if created_at < since_date:
                    # Reached PRs before date range, stop
                    has_next_page = False
                    break

                if created_at > until_date:
                    # Skip PRs after date range
                    continue

                # Convert to REST format
                rest_pr = self._convert_pr_to_rest_format(pr)

                # Store PR
                pr_id = self.db.store_github_pull_request(rest_pr, repo_id)
                count += 1

                # Extract JIRA references
                self._extract_pr_jira_references(rest_pr, pr_id)

                if count % 10 == 0:
                    print(f"   📝 Processed {count} PRs...")

                if count >= limit:
                    break

            # Pagination
            page_info = pull_requests['pageInfo']
            has_next_page = has_next_page and page_info['hasNextPage']
            cursor = page_info['endCursor']

        print(f"   ✅ Ingested {count} pull requests")
        return count

    def ingest_issues(
        self,
        owner: str,
        repo: str,
        since_date: Optional[datetime] = None,
        until_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> int:
        """
        Ingest GitHub issues within date range using GraphQL.

        Args:
            owner: Repository owner
            repo: Repository name
            since_date: Start date (default: 1 year ago)
            until_date: End date (default: now)
            limit: Maximum issues to fetch

        Returns:
            Number of issues ingested
        """
        # Default to past year
        if since_date is None:
            since_date = datetime.now(timezone.utc) - timedelta(days=365)
        if until_date is None:
            until_date = datetime.now(timezone.utc)

        # Ensure dates are timezone-aware (convert to UTC if naive)
        if since_date.tzinfo is None:
            since_date = since_date.replace(tzinfo=timezone.utc)
        if until_date.tzinfo is None:
            until_date = until_date.replace(tzinfo=timezone.utc)

        # Validate date range
        if since_date > until_date:
            raise ValueError(f"since_date ({since_date.date()}) must be before until_date ({until_date.date()})")

        print(f"🐛 Ingesting issues: {owner}/{repo}")
        print(f"   Date range: {since_date.date()} to {until_date.date()}")

        # Get repository ID (avoid re-ingesting if possible)
        # Check if repo already exists in DB
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT repo_id FROM github_repositories WHERE owner = ? AND name = ?",
                (owner, repo)
            )
            result = cursor.fetchone()
            repo_id = result[0] if result else self.ingest_repository(owner, repo)

        query = """
        query($owner: String!, $repo: String!, $cursor: String) {
          repository(owner: $owner, name: $repo) {
            issues(first: 100, after: $cursor, orderBy: {field: CREATED_AT, direction: DESC}) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                id
                databaseId
                number
                title
                body
                state
                createdAt
                updatedAt
                closedAt
                url
                author {
                  login
                }
                assignees(first: 10) {
                  nodes {
                    login
                  }
                }
                labels(first: 20) {
                  nodes {
                    name
                  }
                }
              }
            }
          }
        }
        """

        count = 0
        cursor = None
        has_next_page = True

        while has_next_page and count < limit:
            variables = {'owner': owner, 'repo': repo}
            if cursor:
                variables['cursor'] = cursor

            data = self._call_graphql(query, variables)

            if not data or 'repository' not in data:
                break

            issues = data['repository']['issues']

            for issue in issues['nodes']:
                # Check date range
                created_at = datetime.fromisoformat(issue['createdAt'].replace('Z', '+00:00'))

                if created_at < since_date:
                    # Reached issues before date range, stop
                    has_next_page = False
                    break

                if created_at > until_date:
                    # Skip issues after date range
                    continue

                # Convert to REST format
                rest_issue = self._convert_issue_to_rest_format(issue)

                # Store issue
                issue_id = self.db.store_github_issue(rest_issue, repo_id)
                count += 1

                # Extract JIRA references
                self._extract_issue_jira_references(rest_issue, issue_id)

                if count % 10 == 0:
                    print(f"   📝 Processed {count} issues...")

                if count >= limit:
                    break

            # Pagination
            page_info = issues['pageInfo']
            has_next_page = has_next_page and page_info['hasNextPage']
            cursor = page_info['endCursor']

        print(f"   ✅ Ingested {count} issues")
        return count

    def _convert_pr_to_rest_format(self, pr: Dict) -> Dict:
        """Convert GraphQL PR format to REST API format."""
        return {
            'id': pr['databaseId'],
            'number': pr['number'],
            'title': pr['title'],
            'body': pr.get('body', ''),
            'state': pr['state'].lower(),
            'draft': pr.get('isDraft', False),
            'user': {'login': pr['author']['login'] if pr.get('author') else 'ghost'},
            'assignees': [{'login': a['login']} for a in pr.get('assignees', {}).get('nodes', [])],
            'requested_reviewers': [
                {'login': r['requestedReviewer']['login']}
                for r in pr.get('reviewRequests', {}).get('nodes', [])
                if r.get('requestedReviewer') and 'login' in r['requestedReviewer']
            ],
            'labels': [{'name': l['name']} for l in pr.get('labels', {}).get('nodes', [])],
            'base': {'ref': pr['baseRef']['name'] if pr.get('baseRef') else 'main'},
            'head': {'ref': pr['headRef']['name'] if pr.get('headRef') else 'unknown'},
            'created_at': pr['createdAt'],
            'updated_at': pr['updatedAt'],
            'closed_at': pr.get('closedAt'),
            'merged_at': pr.get('mergedAt'),
            'merge_commit_sha': pr['mergeCommit']['oid'] if pr.get('mergeCommit') else None,
            'additions': pr.get('additions'),
            'deletions': pr.get('deletions'),
            'changed_files': pr.get('changedFiles'),
            'html_url': pr['url'],
        }

    def _convert_issue_to_rest_format(self, issue: Dict) -> Dict:
        """Convert GraphQL issue format to REST API format."""
        return {
            'id': issue['databaseId'],
            'number': issue['number'],
            'title': issue['title'],
            'body': issue.get('body', ''),
            'state': issue['state'].lower(),
            'user': {'login': issue['author']['login'] if issue.get('author') else 'ghost'},
            'assignees': [{'login': a['login']} for a in issue.get('assignees', {}).get('nodes', [])],
            'labels': [{'name': l['name']} for l in issue.get('labels', {}).get('nodes', [])],
            'created_at': issue['createdAt'],
            'updated_at': issue['updatedAt'],
            'closed_at': issue.get('closedAt'),
            'html_url': issue['url'],
        }

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

    def ingest_repository_full(
        self,
        owner: str,
        repo: str,
        since_date: Optional[datetime] = None,
        until_date: Optional[datetime] = None,
        pr_limit: int = 1000,
        issue_limit: int = 1000,
    ) -> Dict:
        """
        Ingest all data for a repository within date range.

        Args:
            owner: Repository owner
            repo: Repository name
            since_date: Start date (default: 1 year ago)
            until_date: End date (default: now)
            pr_limit: Max PRs to fetch
            issue_limit: Max issues to fetch

        Returns:
            Statistics dictionary
        """
        print(f"\n🚀 Full ingestion: {owner}/{repo}\n")

        # Default to past year
        if since_date is None:
            since_date = datetime.now(timezone.utc) - timedelta(days=365)
        if until_date is None:
            until_date = datetime.now(timezone.utc)

        # Ensure dates are timezone-aware (convert to UTC if naive)
        if since_date.tzinfo is None:
            since_date = since_date.replace(tzinfo=timezone.utc)
        if until_date.tzinfo is None:
            until_date = until_date.replace(tzinfo=timezone.utc)

        # Validate date range
        if since_date > until_date:
            raise ValueError(f"since_date ({since_date.date()}) must be before until_date ({until_date.date()})")

        print(f"📅 Date range: {since_date.date()} to {until_date.date()}\n")

        stats = {}

        try:
            # Repository metadata (ingest once, will be reused)
            repo_id = self.ingest_repository(owner, repo)
            stats['repo_id'] = repo_id

            # Pull requests
            stats['prs'] = self.ingest_pull_requests(
                owner, repo,
                since_date=since_date,
                until_date=until_date,
                limit=pr_limit
            )

            # Issues
            stats['issues'] = self.ingest_issues(
                owner, repo,
                since_date=since_date,
                until_date=until_date,
                limit=issue_limit
            )

            # Get correlation stats
            db_stats = self.db.get_statistics()
            stats['correlations'] = db_stats['correlations']

            print(f"\n✅ Ingestion complete!")
            print(f"   PRs: {stats['prs']}")
            print(f"   Issues: {stats['issues']}")
            print(f"   JIRA correlations: {stats['correlations']}")

            return stats

        except Exception as e:
            print(f"\n❌ Ingestion failed: {e}")
            raise


# Maintain backward compatibility
GitHubIngester = GitHubGraphQLIngester


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Ingest GitHub data into knowledge database using GraphQL API'
    )
    parser.add_argument('repository', help='Repository in format owner/repo')
    parser.add_argument(
        '--since',
        help='Start date (YYYY-MM-DD, default: 1 year ago)'
    )
    parser.add_argument(
        '--until',
        help='End date (YYYY-MM-DD, default: today)'
    )
    parser.add_argument('--prs', type=int, default=1000, help='Max PRs to fetch')
    parser.add_argument('--issues', type=int, default=1000, help='Max issues to fetch')
    parser.add_argument('--db', help='Database path (default: ~/.agent-knowledge/data.db)')

    args = parser.parse_args()

    # Parse repository
    if '/' not in args.repository:
        print("Error: Repository must be in format 'owner/repo'")
        sys.exit(1)

    owner, repo = args.repository.split('/', 1)

    # Parse dates
    since_date = None
    until_date = None

    if args.since:
        try:
            since_date = datetime.strptime(args.since, '%Y-%m-%d')
        except ValueError:
            print("Error: --since must be in format YYYY-MM-DD")
            sys.exit(1)

    if args.until:
        try:
            until_date = datetime.strptime(args.until, '%Y-%m-%d')
        except ValueError:
            print("Error: --until must be in format YYYY-MM-DD")
            sys.exit(1)

    # Initialize database
    db = KnowledgeDatabase(args.db) if args.db else KnowledgeDatabase()

    # Initialize ingester
    ingester = GitHubGraphQLIngester(db)

    # Run ingestion
    try:
        stats = ingester.ingest_repository_full(
            owner, repo,
            since_date=since_date,
            until_date=until_date,
            pr_limit=args.prs,
            issue_limit=args.issues,
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
