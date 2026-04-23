#!/usr/bin/env python3
"""
Parallel batch ingestion for multiple repositories.
Handles rate limits, checkpointing, and JIRA deduplication.
"""

import json
import sys
import time
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database import KnowledgeDatabase
from ingest_github import GitHubIngester
from ingest_jira import JiraIngester


class RateLimitCoordinator:
    """Coordinate rate limits across parallel workers."""

    def __init__(self, requests_per_hour: int = 4500):
        """
        Initialize rate limiter.

        Args:
            requests_per_hour: Max API requests per hour (留了500的缓冲)
        """
        self.requests_per_hour = requests_per_hour
        self.request_times = []
        self.lock = __import__('threading').Lock()

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        with self.lock:
            now = time.time()

            # Remove requests older than 1 hour
            cutoff = now - 3600
            self.request_times = [t for t in self.request_times if t > cutoff]

            # Check if we're at limit
            if len(self.request_times) >= self.requests_per_hour:
                # Wait until oldest request is >1hr old
                wait_time = 3600 - (now - self.request_times[0]) + 1
                print(f"⏸️  Rate limit reached, waiting {wait_time:.0f}s...")
                time.sleep(wait_time)

                # Refresh times
                now = time.time()
                cutoff = now - 3600
                self.request_times = [t for t in self.request_times if t > cutoff]

            # Record this request
            self.request_times.append(now)


class CheckpointManager:
    """Manage ingestion checkpoints for resume capability."""

    def __init__(self, checkpoint_file: str = '.ingestion_checkpoint.json'):
        """Initialize checkpoint manager."""
        self.checkpoint_file = checkpoint_file
        self.checkpoints = self._load()

    def _load(self) -> Dict:
        """Load checkpoints from file."""
        if Path(self.checkpoint_file).exists():
            with open(self.checkpoint_file) as f:
                return json.load(f)
        return {}

    def save(self):
        """Save checkpoints to file."""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoints, f, indent=2)

    def mark_completed(self, repo_full_name: str, stats: Dict):
        """Mark a repository as completed."""
        self.checkpoints[repo_full_name] = {
            'status': 'completed',
            'completed_at': datetime.now().isoformat(),
            'stats': stats,
        }
        self.save()

    def mark_failed(self, repo_full_name: str, error: str):
        """Mark a repository as failed."""
        self.checkpoints[repo_full_name] = {
            'status': 'failed',
            'failed_at': datetime.now().isoformat(),
            'error': str(error),
        }
        self.save()

    def is_completed(self, repo_full_name: str) -> bool:
        """Check if repository already ingested."""
        return (
            repo_full_name in self.checkpoints and
            self.checkpoints[repo_full_name].get('status') == 'completed'
        )

    def get_stats(self) -> Dict:
        """Get checkpoint statistics."""
        completed = sum(
            1 for cp in self.checkpoints.values()
            if cp.get('status') == 'completed'
        )
        failed = sum(
            1 for cp in self.checkpoints.values()
            if cp.get('status') == 'failed'
        )

        return {
            'total_processed': len(self.checkpoints),
            'completed': completed,
            'failed': failed,
        }


class BatchIngester:
    """Parallel batch ingestion for multiple repositories."""

    def __init__(
        self,
        db_path: str = None,
        num_workers: int = 5,
        pr_limit: int = 500,
        issue_limit: int = 200,
        commit_limit: int = 500,
    ):
        """
        Initialize batch ingester.

        Args:
            db_path: Database path
            num_workers: Number of parallel workers
            pr_limit: Max PRs per repo
            issue_limit: Max issues per repo
            commit_limit: Max commits per repo
        """
        self.db_path = db_path
        self.num_workers = num_workers
        self.pr_limit = pr_limit
        self.issue_limit = issue_limit
        self.commit_limit = commit_limit

        self.rate_limiter = RateLimitCoordinator()
        self.checkpoint_mgr = CheckpointManager()

    def ingest_repository(self, repo: Dict) -> Dict:
        """
        Ingest a single repository.

        Args:
            repo: Repository metadata from manifest

        Returns:
            Ingestion statistics
        """
        full_name = repo['full_name']
        owner, name = full_name.split('/')

        print(f"\n{'=' * 60}")
        print(f"📦 Ingesting: {full_name}")
        print(f"   Priority Score: {repo.get('priority_score', 0)}")
        print(f"{'=' * 60}")

        try:
            # Wait for rate limit
            self.rate_limiter.wait_if_needed()

            # Initialize database and ingesters
            db = KnowledgeDatabase(self.db_path)
            github_ingester = GitHubIngester(db)

            # Ingest GitHub data
            stats = github_ingester.ingest_full_repository(
                owner, name,
                pr_limit=self.pr_limit,
                issue_limit=self.issue_limit,
                commit_limit=self.commit_limit
            )

            # Mark as completed
            self.checkpoint_mgr.mark_completed(full_name, stats)

            return {
                'repo': full_name,
                'status': 'success',
                'stats': stats,
            }

        except Exception as e:
            print(f"❌ Error ingesting {full_name}: {e}")
            self.checkpoint_mgr.mark_failed(full_name, str(e))

            return {
                'repo': full_name,
                'status': 'failed',
                'error': str(e),
            }

    def ingest_jira_batch(self, jira_projects: List[str]):
        """
        Ingest JIRA issues after GitHub ingestion.

        Args:
            jira_projects: List of JIRA project keys (e.g., ['OCPCLOUD', 'OCPBUGS'])
        """
        print("\n" + "=" * 60)
        print("📊 JIRA BATCH INGESTION")
        print("=" * 60)

        db = KnowledgeDatabase(self.db_path)
        jira_ingester = JiraIngester(db)

        # Step 1: Ingest all referenced JIRA issues
        print("\nStep 1: Ingesting referenced JIRA issues...")
        ref_stats = jira_ingester.ingest_referenced_issues()

        # Step 2: Optionally ingest full JIRA projects
        project_stats = {}
        for project in jira_projects:
            print(f"\nStep 2: Ingesting JIRA project: {project}...")
            stats = jira_ingester.ingest_features_and_bugs(
                project,
                max_results=1000  # Higher limit for batch
            )
            project_stats[project] = stats

        return {
            'referenced': ref_stats,
            'projects': project_stats,
        }

    def ingest_from_manifest(
        self,
        manifest_file: str,
        skip_completed: bool = True,
        jira_projects: List[str] = None,
    ) -> Dict:
        """
        Ingest all repositories from manifest file.

        Args:
            manifest_file: Path to manifest JSON
            skip_completed: Skip already completed repos
            jira_projects: JIRA projects to ingest

        Returns:
            Overall statistics
        """
        # Load manifest
        with open(manifest_file) as f:
            manifest = json.load(f)

        repos = manifest['repositories']

        # Filter out completed
        if skip_completed:
            repos_to_process = [
                r for r in repos
                if not self.checkpoint_mgr.is_completed(r['full_name'])
            ]
            skipped = len(repos) - len(repos_to_process)
            if skipped > 0:
                print(f"⏭️  Skipping {skipped} already completed repositories")
        else:
            repos_to_process = repos

        print(f"\n📊 Batch Ingestion Plan:")
        print(f"   Total repositories: {len(repos)}")
        print(f"   To process: {len(repos_to_process)}")
        print(f"   Parallel workers: {self.num_workers}")
        print(f"   Limits: PRs={self.pr_limit}, Issues={self.issue_limit}, "
              f"Commits={self.commit_limit}")

        if not repos_to_process:
            print("\n✅ All repositories already ingested!")
            return {'skipped': len(repos)}

        # Process in parallel
        start_time = time.time()
        results = []

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = {
                executor.submit(self.ingest_repository, repo): repo
                for repo in repos_to_process
            }

            for future in as_completed(futures):
                result = future.result()
                results.append(result)

                # Progress update
                completed = len(results)
                total = len(repos_to_process)
                pct = (completed / total) * 100
                print(f"\n📊 Progress: {completed}/{total} ({pct:.1f}%)")

        # GitHub ingestion complete, now ingest JIRA
        jira_stats = None
        if jira_projects:
            jira_stats = self.ingest_jira_batch(jira_projects)

        # Calculate statistics
        elapsed = time.time() - start_time
        success_count = sum(1 for r in results if r['status'] == 'success')
        failed_count = sum(1 for r in results if r['status'] == 'failed')

        overall_stats = {
            'total_repos': len(repos),
            'processed': len(repos_to_process),
            'success': success_count,
            'failed': failed_count,
            'skipped': len(repos) - len(repos_to_process),
            'elapsed_seconds': elapsed,
            'elapsed_hours': elapsed / 3600,
            'jira_stats': jira_stats,
        }

        # Print summary
        print("\n" + "=" * 60)
        print("📊 BATCH INGESTION COMPLETE")
        print("=" * 60)
        print(f"\n✅ Success: {success_count}/{len(repos_to_process)}")
        print(f"❌ Failed: {failed_count}/{len(repos_to_process)}")
        print(f"⏭️  Skipped: {overall_stats['skipped']}")
        print(f"⏱️  Time: {elapsed/3600:.2f} hours")

        if failed_count > 0:
            print(f"\n❌ Failed repositories:")
            for result in results:
                if result['status'] == 'failed':
                    print(f"   - {result['repo']}: {result['error']}")

        # Database statistics
        db = KnowledgeDatabase(self.db_path)
        db_stats = db.get_statistics()
        print(f"\n📊 Database Statistics:")
        print(f"   Repositories: {db_stats['github_repos']}")
        print(f"   Pull Requests: {db_stats['github_prs']}")
        print(f"   Issues: {db_stats['github_issues']}")
        print(f"   Commits: {db_stats['github_commits']}")
        print(f"   JIRA Issues: {db_stats['jira_issues']}")
        print(f"   Correlations: {db_stats['correlations']}")

        return overall_stats


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Parallel batch ingestion for multiple repositories'
    )
    parser.add_argument(
        'manifest',
        help='Manifest file from discover_openshift_repos.py'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=5,
        help='Number of parallel workers (default: 5)'
    )
    parser.add_argument(
        '--prs',
        type=int,
        default=500,
        help='Max PRs per repo (default: 500)'
    )
    parser.add_argument(
        '--issues',
        type=int,
        default=200,
        help='Max issues per repo (default: 200)'
    )
    parser.add_argument(
        '--commits',
        type=int,
        default=500,
        help='Max commits per repo (default: 500)'
    )
    parser.add_argument(
        '--jira',
        nargs='+',
        help='JIRA projects to ingest (e.g., OCPCLOUD OCPBUGS)'
    )
    parser.add_argument(
        '--db',
        help='Database path (default: ~/.agent-knowledge/data.db)'
    )
    parser.add_argument(
        '--no-skip-completed',
        action='store_true',
        help='Re-ingest completed repositories'
    )

    args = parser.parse_args()

    ingester = BatchIngester(
        db_path=args.db,
        num_workers=args.workers,
        pr_limit=args.prs,
        issue_limit=args.issues,
        commit_limit=args.commits,
    )

    try:
        stats = ingester.ingest_from_manifest(
            args.manifest,
            skip_completed=not args.no_skip_completed,
            jira_projects=args.jira,
        )

        # Write stats to file
        with open('ingestion_stats.json', 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"\n📊 Statistics saved to: ingestion_stats.json")

    except KeyboardInterrupt:
        print("\n\n⚠️  Ingestion interrupted")
        print("💾 Progress saved to checkpoint file")
        print("🔄 Run again to resume")
        sys.exit(130)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
