#!/usr/bin/env python3
"""
Public JIRA Client - No Authentication Required
Access public JIRA instances (like issues.redhat.com) without API tokens.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from typing import Dict, List, Optional


class PublicJiraClient:
    """Client for accessing public JIRA instances without authentication."""

    def __init__(self, base_url: str = "https://issues.redhat.com"):
        """
        Initialize public JIRA client.

        Args:
            base_url: Base URL of JIRA instance (default: Red Hat JIRA)
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/rest/api/2"

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make HTTP request to JIRA API."""
        url = f"{self.api_base}/{endpoint}"

        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"

        try:
            with urllib.request.urlopen(url) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
            return {}
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return {}

    def search_issues(
        self,
        jql: str,
        fields: Optional[List[str]] = None,
        max_results: int = 50
    ) -> List[Dict]:
        """
        Search issues using JQL (JIRA Query Language).

        Args:
            jql: JIRA Query Language string
            fields: List of fields to return (default: all)
            max_results: Maximum number of results

        Returns:
            List of issue dictionaries
        """
        params = {
            'jql': jql,
            'maxResults': max_results
        }

        if fields:
            params['fields'] = ','.join(fields)

        result = self._make_request('search', params)
        return result.get('issues', [])

    def get_issue(self, issue_key: str) -> Dict:
        """
        Get issue by key (e.g., 'OCPCLOUD-1234').

        Args:
            issue_key: JIRA issue key

        Returns:
            Issue dictionary
        """
        return self._make_request(f'issue/{issue_key}')

    def get_issue_comments(self, issue_key: str) -> List[Dict]:
        """Get comments for an issue."""
        result = self._make_request(f'issue/{issue_key}/comment')
        return result.get('comments', [])

    def get_project(self, project_key: str) -> Dict:
        """Get project information."""
        return self._make_request(f'project/{project_key}')


def main():
    """Example usage."""
    # Initialize client (defaults to Red Hat public JIRA)
    client = PublicJiraClient()

    # Example: Search for OpenShift bugs
    print("Searching for recent OpenShift bugs...")
    issues = client.search_issues(
        jql='project = OCPCLOUD AND type = Bug AND created >= -30d',
        fields=['summary', 'status', 'priority', 'created'],
        max_results=10
    )

    print(f"\nFound {len(issues)} issues:\n")
    for issue in issues:
        key = issue['key']
        summary = issue['fields']['summary']
        status = issue['fields']['status']['name']
        priority = issue['fields']['priority']['name']

        print(f"{key}: {summary}")
        print(f"  Status: {status}, Priority: {priority}")
        print()


if __name__ == '__main__':
    main()
