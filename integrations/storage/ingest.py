#!/usr/bin/env python3
"""
Unified ingestion script for GitHub and JIRA data.
Coordinates ingestion and correlation.
"""

import sys
import argparse
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database import KnowledgeDatabase
from ingest_github import GitHubIngester
from ingest_jira import JiraIngester


def ingest_repository_full(
    owner: str,
    repo: str,
    jira_project: str = None,
    pr_limit: int = 100,
    issue_limit: int = 100,
    commit_limit: int = 100,
    db_path: str = None
):
    """
    Full ingestion workflow: GitHub → JIRA correlation → JIRA ingestion.

    Args:
        owner: GitHub repository owner
        repo: GitHub repository name
        jira_project: JIRA project key (e.g., 'OCPCLOUD')
        pr_limit: Max PRs to fetch
        issue_limit: Max GitHub issues to fetch
        commit_limit: Max commits to fetch
        db_path: Database path (optional)
    """
    print("=" * 60)
    print(f"🚀 FULL INGESTION: {owner}/{repo}")
    print("=" * 60)
    print()

    # Initialize database
    db = KnowledgeDatabase(db_path)
    print(f"📊 Database: {db.db_path}\n")

    # Step 1: Ingest GitHub data
    print("STEP 1: GitHub Ingestion")
    print("-" * 60)

    github_ingester = GitHubIngester(db)
    github_stats = github_ingester.ingest_full_repository(
        owner, repo,
        pr_limit=pr_limit,
        issue_limit=issue_limit,
        commit_limit=commit_limit
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
            max_results=100
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
    print(f"   Commits: {overall_stats['github_commits']}")

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
        description='Unified GitHub and JIRA data ingestion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest OpenShift installer repository
  python ingest.py openshift/installer --jira OCPCLOUD

  # Ingest with custom limits
  python ingest.py openshift/machine-api-operator --prs 200 --commits 200

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
        '--prs',
        type=int,
        default=100,
        help='Max PRs to fetch (default: 100)'
    )
    parser.add_argument(
        '--issues',
        type=int,
        default=100,
        help='Max GitHub issues to fetch (default: 100)'
    )
    parser.add_argument(
        '--commits',
        type=int,
        default=100,
        help='Max commits to fetch (default: 100)'
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

    # Run ingestion
    try:
        ingest_repository_full(
            owner, repo,
            jira_project=args.jira,
            pr_limit=args.prs,
            issue_limit=args.issues,
            commit_limit=args.commits,
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
