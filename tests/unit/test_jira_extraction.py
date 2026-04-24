"""Unit tests for JIRA key extraction."""

import sys
from pathlib import Path

# Add integrations to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "integrations" / "storage"))

from ingest_github import JiraKeyExtractor


class TestJiraKeyExtractor:
    """Test JIRA key extraction from text."""

    def test_extract_valid_keys(self):
        """Test extraction of valid JIRA keys."""
        text = "This PR fixes OCPCLOUD-123 and resolves OCPBUGS-456"
        keys = JiraKeyExtractor.extract(text)

        assert "OCPCLOUD-123" in keys
        assert "OCPBUGS-456" in keys
        assert len(keys) == 2

    def test_filter_false_positives(self):
        """Test that common false positives are filtered out."""
        text = "HTTP-404 and API-123 should be filtered"
        keys = JiraKeyExtractor.extract(text)

        assert "HTTP-404" not in keys
        assert "API-123" not in keys
        assert len(keys) == 0

    def test_known_limitation_cve_patterns(self):
        """Test documenting known limitation: CVE patterns not filtered yet."""
        # NOTE: This is a known limitation documented in TEST_RESULTS.md
        # CVE-*, RHSA-*, etc. are not currently filtered but should be
        text = "CVE-2024-1234 is a security vulnerability"
        keys = JiraKeyExtractor.extract(text)

        # Currently this matches (known issue)
        assert "CVE-2024" in keys

        # TODO: Implement enhanced filter to exclude CVE-*, RHSA-*, etc.
        # Expected after fix: assert "CVE-2024" not in keys

    def test_extract_with_context(self):
        """Test extraction with surrounding context."""
        text = "This change fixes OCPCLOUD-123 which was causing issues"
        results = JiraKeyExtractor.extract_with_context(text, context_chars=20)

        assert len(results) == 1
        assert results[0]["key"] == "OCPCLOUD-123"
        assert "fixes" in results[0]["context"]

    def test_empty_text(self):
        """Test extraction from empty text."""
        keys = JiraKeyExtractor.extract("")
        assert len(keys) == 0

        results = JiraKeyExtractor.extract_with_context("")
        assert len(results) == 0

    def test_multiple_same_key(self):
        """Test that duplicate keys are deduplicated."""
        text = "OCPCLOUD-123 is mentioned twice: OCPCLOUD-123"
        keys = JiraKeyExtractor.extract(text)

        assert len(keys) == 1
        assert "OCPCLOUD-123" in keys
