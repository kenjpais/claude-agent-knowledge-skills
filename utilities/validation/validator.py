"""
Validation utilities for agentic documentation quality checks.
Implements navigation depth checking, link validation, and quality scoring.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import yaml


@dataclass
class ValidationResult:
    """Result of a validation check."""
    passed: bool
    score: float
    violations: List[str]
    warnings: List[str]
    metadata: Dict


class NavigationDepthChecker:
    """Check that all documentation is reachable within N hops from AGENTS.md."""

    def __init__(self, root_file: Path, max_depth: int = 3):
        """
        Initialize depth checker.

        Args:
            root_file: Entry point file (usually AGENTS.md)
            max_depth: Maximum allowed navigation depth
        """
        self.root_file = root_file
        self.max_depth = max_depth
        self.visited: Set[Path] = set()
        self.depths: Dict[Path, int] = {}

    def check(self, agentic_dir: Path) -> ValidationResult:
        """
        Check navigation depth constraint.

        Args:
            agentic_dir: Path to agentic/ directory

        Returns:
            ValidationResult with depth violations
        """
        # Build navigation graph starting from root
        self._traverse(self.root_file, 0)

        # Find all markdown files in agentic directory
        all_docs = set(agentic_dir.rglob("*.md"))

        # Identify unreachable files (orphans)
        reachable = set(self.depths.keys())
        orphaned = all_docs - reachable

        # Identify files beyond max depth
        beyond_depth = {
            path: depth for path, depth in self.depths.items()
            if depth > self.max_depth
        }

        violations = []
        for path in orphaned:
            violations.append(f"Orphaned file (unreachable): {path}")

        for path, depth in beyond_depth.items():
            violations.append(
                f"File exceeds max depth {self.max_depth}: {path} (depth: {depth})"
            )

        passed = len(violations) == 0

        # Calculate distribution
        distribution = {
            f"depth_{i}": sum(1 for d in self.depths.values() if d == i)
            for i in range(self.max_depth + 2)
        }
        distribution["unreachable"] = len(orphaned)

        return ValidationResult(
            passed=passed,
            score=10.0 if passed else 0.0,
            violations=violations,
            warnings=[],
            metadata={
                "total_files": len(all_docs),
                "reachable_files": len(reachable),
                "orphaned_files": len(orphaned),
                "max_depth_found": max(self.depths.values()) if self.depths else 0,
                "distribution": distribution
            }
        )

    def _traverse(self, file_path: Path, depth: int) -> None:
        """Recursively traverse documentation links."""
        if file_path in self.visited:
            return

        self.visited.add(file_path)
        self.depths[file_path] = depth

        if depth >= self.max_depth + 1:  # Allow one extra to detect violations
            return

        # Extract markdown links from file
        links = self._extract_links(file_path)

        for link in links:
            linked_file = self._resolve_link(file_path, link)
            if linked_file and linked_file.exists():
                self._traverse(linked_file, depth + 1)

    def _extract_links(self, file_path: Path) -> List[str]:
        """Extract markdown links from file."""
        if not file_path.exists():
            return []

        content = file_path.read_text()
        # Match [text](link) and [text](link#anchor)
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(pattern, content)
        return [link for _, link in matches]

    def _resolve_link(self, source: Path, link: str) -> Optional[Path]:
        """Resolve relative link to absolute path."""
        # Remove anchor
        link = link.split('#')[0]

        # Skip external links
        if link.startswith('http://') or link.startswith('https://'):
            return None

        # Resolve relative path
        resolved = (source.parent / link).resolve()
        return resolved if resolved.suffix == '.md' else None


class LinkValidator:
    """Validate all markdown links in documentation."""

    def check(self, docs_dir: Path) -> ValidationResult:
        """
        Validate all links in markdown files.

        Args:
            docs_dir: Directory containing documentation

        Returns:
            ValidationResult with broken links
        """
        broken_links = []
        total_links = 0

        for md_file in docs_dir.rglob("*.md"):
            links = self._extract_all_links(md_file)
            total_links += len(links)

            for link, anchor in links:
                if not self._validate_link(md_file, link, anchor):
                    broken_links.append(f"{md_file} -> {link}#{anchor if anchor else ''}")

        passed = len(broken_links) == 0
        score = max(0, 10 - len(broken_links))

        return ValidationResult(
            passed=passed,
            score=float(score),
            violations=broken_links,
            warnings=[],
            metadata={
                "total_links": total_links,
                "broken_links": len(broken_links)
            }
        )

    def _extract_all_links(self, file_path: Path) -> List[Tuple[str, Optional[str]]]:
        """Extract all links with anchors."""
        if not file_path.exists():
            return []

        content = file_path.read_text()
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(pattern, content)

        links = []
        for _, link in matches:
            # Split link and anchor
            parts = link.split('#', 1)
            link_path = parts[0]
            anchor = parts[1] if len(parts) > 1 else None
            links.append((link_path, anchor))

        return links

    def _validate_link(self, source: Path, link: str, anchor: Optional[str]) -> bool:
        """Validate that link target exists."""
        # Skip external links
        if link.startswith('http://') or link.startswith('https://'):
            return True

        # Resolve file path
        if not link:  # Empty link means same file
            target = source
        else:
            target = (source.parent / link).resolve()

        # Check file exists
        if not target.exists():
            return False

        # If anchor specified, check it exists in file
        if anchor:
            return self._check_anchor(target, anchor)

        return True

    def _check_anchor(self, file_path: Path, anchor: str) -> bool:
        """Check if anchor exists in markdown file."""
        if not file_path.exists():
            return False

        content = file_path.read_text()
        # Generate anchor from heading
        # Markdown anchors are lowercase, spaces->hyphens
        headings = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)

        for heading in headings:
            heading_anchor = heading.lower().replace(' ', '-')
            heading_anchor = re.sub(r'[^\w\-]', '', heading_anchor)
            if heading_anchor == anchor:
                return True

        return False


class QualityScoreCalculator:
    """Calculate overall documentation quality score."""

    def __init__(self, repo_path: Path, agentic_dir: Path):
        """
        Initialize quality calculator.

        Args:
            repo_path: Path to repository root
            agentic_dir: Path to agentic/ directory
        """
        self.repo_path = repo_path
        self.agentic_dir = agentic_dir

    def calculate(self) -> Dict:
        """
        Calculate comprehensive quality metrics.

        Returns:
            Dictionary with quality score and metrics
        """
        # Check required files
        completeness = self._check_completeness()

        # Check navigation depth
        nav_checker = NavigationDepthChecker(self.repo_path / "AGENTS.md")
        navigation = nav_checker.check(self.agentic_dir)

        # Check links
        link_validator = LinkValidator()
        linkage = link_validator.check(self.agentic_dir)

        # Calculate total score
        total_score = (
            completeness["score"] +
            navigation.score +
            linkage.score
        )

        return {
            "overall_score": int(total_score),
            "passed": total_score >= 70,
            "completeness": completeness,
            "navigation": {
                "passed": navigation.passed,
                "score": navigation.score,
                "max_depth": navigation.metadata.get("max_depth_found", 0),
                "violations": navigation.violations
            },
            "linkage": {
                "total_links": linkage.metadata["total_links"],
                "broken_links": linkage.metadata["broken_links"],
                "score": linkage.score
            }
        }

    def _check_completeness(self) -> Dict:
        """Check required files exist."""
        required_files = [
            self.repo_path / "AGENTS.md",
            self.agentic_dir / "DESIGN.md",
            self.agentic_dir / "DEVELOPMENT.md",
            self.agentic_dir / "TESTING.md",
            self.agentic_dir / "RELIABILITY.md",
            self.agentic_dir / "SECURITY.md",
            self.agentic_dir / "QUALITY_SCORE.md"
        ]

        missing = [f for f in required_files if not f.exists()]
        present = len(required_files) - len(missing)

        score = (present / len(required_files)) * 20

        return {
            "score": score,
            "required_files_present": present,
            "total_required": len(required_files),
            "missing_files": [str(f) for f in missing]
        }
