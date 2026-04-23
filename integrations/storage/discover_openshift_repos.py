#!/usr/bin/env python3
"""
Discover all OpenShift repositories and prioritize for ingestion.
Outputs a ranked list of repositories to ingest.
"""

import json
import subprocess
import sys
from typing import List, Dict
from datetime import datetime, timedelta


class OpenShiftRepoDiscoverer:
    """Discover and prioritize OpenShift repositories."""

    # Core OpenShift organizations
    ORGS = [
        'openshift',
        'openshift-kni',
        'openshift-metal3',
        'openshift-online',
        'openshift-priv',
    ]

    # High-priority repos (ingest first)
    HIGH_PRIORITY = [
        'openshift/installer',
        'openshift/machine-api-operator',
        'openshift/cluster-api-provider-aws',
        'openshift/cluster-api-provider-azure',
        'openshift/cluster-api-provider-gcp',
        'openshift/cluster-api-provider-openstack',
        'openshift/origin',
        'openshift/kubernetes',
        'openshift/api',
    ]

    def __init__(self, min_stars: int = 10, min_activity_days: int = 180):
        """
        Initialize discoverer.

        Args:
            min_stars: Minimum stars for a repo to be included
            min_activity_days: Include repos active in last N days
        """
        self.min_stars = min_stars
        self.min_activity_days = min_activity_days

    def _gh_api(self, endpoint: str) -> Dict:
        """Call GitHub API using gh CLI."""
        try:
            result = subprocess.run(
                ['gh', 'api', endpoint, '--paginate'],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error calling GitHub API: {e.stderr}", file=sys.stderr)
            return []
        except json.JSONDecodeError:
            return []

    def discover_org_repos(self, org: str) -> List[Dict]:
        """
        Discover all repositories in an organization.

        Args:
            org: GitHub organization name

        Returns:
            List of repository metadata
        """
        print(f"🔍 Discovering repositories in {org}...")

        repos = self._gh_api(f'orgs/{org}/repos?per_page=100&type=public')

        if not isinstance(repos, list):
            return []

        # Filter and enrich
        filtered = []
        cutoff_date = datetime.now() - timedelta(days=self.min_activity_days)

        for repo in repos:
            # Basic filters
            if repo.get('archived', False):
                continue

            if repo.get('stargazers_count', 0) < self.min_stars:
                continue

            # Activity filter
            pushed_at = datetime.fromisoformat(
                repo['pushed_at'].replace('Z', '+00:00')
            )
            if pushed_at < cutoff_date:
                continue

            filtered.append({
                'owner': repo['owner']['login'],
                'name': repo['name'],
                'full_name': repo['full_name'],
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'open_issues': repo.get('open_issues_count', 0),
                'language': repo.get('language', 'Unknown'),
                'pushed_at': repo['pushed_at'],
                'description': repo.get('description', ''),
            })

        print(f"   ✅ Found {len(filtered)} active repositories")
        return filtered

    def discover_all(self) -> List[Dict]:
        """Discover all OpenShift repositories across organizations."""
        all_repos = []

        for org in self.ORGS:
            repos = self.discover_org_repos(org)
            all_repos.extend(repos)

        return all_repos

    def prioritize(self, repos: List[Dict]) -> List[Dict]:
        """
        Prioritize repositories for ingestion.

        Priority factors:
        1. High-priority list (installer, machine-api, etc.)
        2. Stars + forks (popularity)
        3. Open issues (activity)
        4. Recent commits (freshness)

        Returns:
            Sorted list of repositories (highest priority first)
        """
        def priority_score(repo: Dict) -> int:
            score = 0

            # High-priority repos get +10000
            if repo['full_name'] in self.HIGH_PRIORITY:
                score += 10000

            # Stars contribute 1:1
            score += repo.get('stars', 0)

            # Forks contribute 2:1 (more valuable)
            score += repo.get('forks', 0) * 2

            # Open issues contribute 0.5:1
            score += repo.get('open_issues', 0) * 0.5

            return int(score)

        # Add priority score
        for repo in repos:
            repo['priority_score'] = priority_score(repo)

        # Sort by priority
        return sorted(repos, key=lambda r: r['priority_score'], reverse=True)

    def generate_manifest(self, output_file: str = 'openshift_repos.json'):
        """
        Generate a manifest of all OpenShift repositories.

        Creates JSON file with prioritized repo list for ingestion.
        """
        print("=" * 60)
        print("🔍 OPENSHIFT REPOSITORY DISCOVERY")
        print("=" * 60)
        print()

        # Discover
        repos = self.discover_all()

        if not repos:
            print("❌ No repositories found")
            sys.exit(1)

        # Prioritize
        prioritized = self.prioritize(repos)

        # Generate manifest
        manifest = {
            'generated_at': datetime.now().isoformat(),
            'total_repos': len(prioritized),
            'organizations': self.ORGS,
            'filters': {
                'min_stars': self.min_stars,
                'min_activity_days': self.min_activity_days,
            },
            'repositories': prioritized,
        }

        # Write to file
        with open(output_file, 'w') as f:
            json.dump(manifest, f, indent=2)

        print(f"\n✅ Manifest generated: {output_file}")
        print(f"   Total repositories: {len(prioritized)}")
        print(f"\n📊 Top 10 Repositories:")
        print(f"   {'Rank':<6} {'Repository':<50} {'Score':<8} {'Stars':<8}")
        print("   " + "-" * 80)

        for i, repo in enumerate(prioritized[:10], 1):
            print(
                f"   {i:<6} {repo['full_name']:<50} "
                f"{repo['priority_score']:<8} {repo['stars']:<8}"
            )

        return manifest


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Discover OpenShift repositories for ingestion'
    )
    parser.add_argument(
        '--min-stars',
        type=int,
        default=10,
        help='Minimum stars (default: 10)'
    )
    parser.add_argument(
        '--min-activity-days',
        type=int,
        default=180,
        help='Minimum activity days (default: 180)'
    )
    parser.add_argument(
        '--output',
        default='openshift_repos.json',
        help='Output manifest file (default: openshift_repos.json)'
    )

    args = parser.parse_args()

    discoverer = OpenShiftRepoDiscoverer(
        min_stars=args.min_stars,
        min_activity_days=args.min_activity_days
    )

    try:
        discoverer.generate_manifest(args.output)

    except KeyboardInterrupt:
        print("\n⚠️  Discovery interrupted")
        sys.exit(130)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
