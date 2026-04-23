#!/usr/bin/env python3
"""
Unified ingestion script for single GitHub repository and JIRA data.
Coordinates ingestion and correlation within a specified date range.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database import KnowledgeDatabase
from ingest_github import GitHubGraphQLIngester
from ingest_jira import JiraIngester


def ingest_repository_full(
    owner: str,
    repo: str,
    jira_project: str = None,
    since_date: datetime = None,
    until_date: datetime = None,
    pr_limit: int = 1000,
    issue_limit: int = 1000,
    db_path: str = None
):
    """
    Full ingestion workflow: GitHub → JIRA correlation → JIRA ingestion.

    Args:
        owner: GitHub repository owner
        repo: GitHub repository name
        jira_project: JIRA project key (e.g., 'OCPCLOUD')
        since_date: Start date for ingestion (default: 1 year ago)
        until_date: End date for ingestion (default: today)
        pr_limit: Max PRs to fetch
        issue_limit: Max GitHub issues to fetch
        db_path: Database path (optional)
    """
    # Default to past year
    if since_date is None:
        since_date = datetime.now() - timedelta(days=365)
    if until_date is None:
        until_date = datetime.now()

    # Validate date range
    if since_date > until_date:
        raise ValueError(f"since_date ({since_date.date()}) must be before until_date ({until_date.date()})")

    print("=" * 60)
    print(f"🚀 FULL INGESTION: {owner}/{repo}")
    print("=" * 60)
    print(f"📅 Date Range: {since_date.date()} to {until_date.date()}")
    print()

    # Initialize database
    db = KnowledgeDatabase(db_path)
    print(f"📊 Database: {db.db_path}\n")

    # Step 1: Ingest GitHub data
    print("STEP 1: GitHub Ingestion")
    print("-" * 60)

    github_ingester = GitHubGraphQLIngester(db)
    github_stats = github_ingester.ingest_repository_full(
        owner, repo,
        since_date=since_date,
        until_date=until_date,
        pr_limit=pr_limit,
        issue_limit=issue_limit,
    )

    # Step 2: Ingest referenced JIRA issues
    print("\nSTEP 2: JIRA Ingestion (Referenced Issues)")
    print("-" * 60)

    jira_ingester = JiraIngester(db)
    jira_stats = jira_ingester.ingest_referenced_issues()

    # Step 3: Optional - Ingest full JIRA project
    if jira_project:
        print(f"\nSTEP 3: JIRA Ingestion (Project: {jira_project})")
        print("-" * 60)

        project_stats = jira_ingester.ingest_features_and_bugs(
            jira_project,
            max_results=1000
        )

    # Final statistics
    print("\n" + "=" * 60)
    print("📊 FINAL STATISTICS")
    print("=" * 60)

    overall_stats = db.get_statistics()

    print(f"\n📁 GitHub:")
    print(f"   Repositories: {overall_stats['github_repos']}")
    print(f"   Pull Requests: {overall_stats['github_prs']}")
    print(f"   Issues: {overall_stats['github_issues']}")

    print(f"\n📊 JIRA:")
    print(f"   Projects: {overall_stats['jira_projects']}")
    print(f"   Issues: {overall_stats['jira_issues']}")

    print(f"\n🔗 Correlations:")
    print(f"   Total references: {overall_stats['correlations']}")
    print(f"   Unique JIRA issues: {overall_stats['jira_issues_referenced']}")

    print("\n" + "=" * 60)
    print("✅ INGESTION COMPLETE")
    print("=" * 60)

    return overall_stats


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Unified GitHub and JIRA data ingestion for a single repository',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest last year of data (default)
  python ingest.py openshift/installer --jira OCPCLOUD

  # Ingest specific date range
  python ingest.py openshift/installer \\
    --since 2024-01-01 \\
    --until 2024-12-31 \\
    --jira OCPCLOUD

  # Ingest last 90 days
  python ingest.py openshift/machine-api-operator \\
    --since 90-days-ago \\
    --jira OCPCLOUD

  # Ingest without JIRA project (only referenced issues)
  python ingest.py kubernetes/kubernetes
        """
    )

    parser.add_argument(
        'repository',
        help='GitHub repository in format owner/repo'
    )
    parser.add_argument(
        '--jira',
        help='JIRA project key to ingest (e.g., OCPCLOUD)'
    )
    parser.add_argument(
        '--since',
        help='Start date (YYYY-MM-DD or "N-days-ago", default: 365-days-ago)'
    )
    parser.add_argument(
        '--until',
        help='End date (YYYY-MM-DD, default: today)'
    )
    parser.add_argument(
        '--prs',
        type=int,
        default=1000,
        help='Max PRs to fetch (default: 1000)'
    )
    parser.add_argument(
        '--issues',
        type=int,
        default=1000,
        help='Max GitHub issues to fetch (default: 1000)'
    )
    parser.add_argument(
        '--db',
        help='Database path (default: ~/.agent-knowledge/data.db)'
    )

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
        # Support "N-days-ago" format
        if args.since.endswith('-days-ago'):
            try:
                days = int(args.since.replace('-days-ago', ''))
                since_date = datetime.now() - timedelta(days=days)
            except ValueError:
                print("Error: --since in 'N-days-ago' format must have valid number")
                sys.exit(1)
        else:
            # Parse as date
            try:
                since_date = datetime.strptime(args.since, '%Y-%m-%d')
            except ValueError:
                print("Error: --since must be YYYY-MM-DD or 'N-days-ago'")
                sys.exit(1)

    if args.until:
        try:
            until_date = datetime.strptime(args.until, '%Y-%m-%d')
        except ValueError:
            print("Error: --until must be in format YYYY-MM-DD")
            sys.exit(1)

    # Run ingestion
    try:
        ingest_repository_full(
            owner, repo,
            jira_project=args.jira,
            since_date=since_date,
            until_date=until_date,
            pr_limit=args.prs,
            issue_limit=args.issues,
            db_path=args.db
        )

    except KeyboardInterrupt:
        print("\n\n⚠️  Ingestion interrupted by user")
        sys.exit(130)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
