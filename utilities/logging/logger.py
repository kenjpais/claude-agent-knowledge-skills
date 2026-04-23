"""
Centralized logging utility for all agent operations.
Provides structured JSON logging with automatic enrichment.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class AgentLogger:
    """Structured logger for agent operations."""

    def __init__(self, agent_id: str, log_dir: str = "agents/logs"):
        """
        Initialize logger for specific agent.

        Args:
            agent_id: Unique identifier for the agent
            log_dir: Directory for log files
        """
        self.agent_id = agent_id
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.agent_log_file = self.log_dir / f"{agent_id}.jsonl"
        self.operations_log_file = self.log_dir / "operations.jsonl"

    def log(
        self,
        operation: str,
        resource: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None,
        level: str = "INFO"
    ) -> None:
        """
        Log an operation with structured metadata.

        Args:
            operation: Name of the operation (e.g., "extract-go-structs")
            resource: Resource being operated on (e.g., file path)
            status: Operation status (started|success|failure)
            metadata: Additional operation-specific metadata
            level: Log level (INFO|WARN|ERROR|DEBUG)
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        log_entry = {
            "timestamp": timestamp,
            "agent_id": self.agent_id,
            "operation": operation,
            "resource": resource,
            "status": status,
            "level": level,
            "metadata": metadata or {}
        }

        # Write to agent-specific log
        self._write_log(self.agent_log_file, log_entry)

        # Write to aggregated operations log
        self._write_log(self.operations_log_file, log_entry)

    def log_start(self, operation: str, resource: str, **metadata) -> None:
        """Log operation start."""
        self.log(operation, resource, "started", metadata, level="INFO")

    def log_success(
        self,
        operation: str,
        resource: str,
        duration_ms: Optional[int] = None,
        **metadata
    ) -> None:
        """Log operation success."""
        if duration_ms is not None:
            metadata["duration_ms"] = duration_ms
        self.log(operation, resource, "success", metadata, level="INFO")

    def log_failure(
        self,
        operation: str,
        resource: str,
        error: str,
        **metadata
    ) -> None:
        """Log operation failure."""
        metadata["error"] = error
        self.log(operation, resource, "failure", metadata, level="ERROR")

    def log_warning(
        self,
        operation: str,
        resource: str,
        warning: str,
        **metadata
    ) -> None:
        """Log operation warning."""
        metadata["warning"] = warning
        self.log(operation, resource, "warning", metadata, level="WARN")

    def _write_log(self, log_file: Path, log_entry: Dict[str, Any]) -> None:
        """Write log entry to file as JSON line."""
        with open(log_file, "a") as f:
            json.dump(log_entry, f)
            f.write("\n")

        # Rotate if file too large (>10MB)
        if log_file.stat().st_size > 10 * 1024 * 1024:
            self._rotate_log(log_file)

    def _rotate_log(self, log_file: Path) -> None:
        """Rotate log file if it exceeds size threshold."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        rotated_name = f"{log_file.stem}_{timestamp}.jsonl"
        rotated_path = log_file.parent / rotated_name

        log_file.rename(rotated_path)

    def query_logs(
        self,
        operation: Optional[str] = None,
        status: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> list[Dict[str, Any]]:
        """
        Query logs with filters.

        Args:
            operation: Filter by operation name
            status: Filter by status
            since: Filter by timestamp (entries after this time)
            limit: Maximum number of entries to return

        Returns:
            List of matching log entries
        """
        results = []

        if not self.agent_log_file.exists():
            return results

        with open(self.agent_log_file) as f:
            for line in f:
                if len(results) >= limit:
                    break

                entry = json.loads(line)

                # Apply filters
                if operation and entry.get("operation") != operation:
                    continue
                if status and entry.get("status") != status:
                    continue
                if since:
                    entry_time = datetime.fromisoformat(entry["timestamp"])
                    if entry_time < since:
                        continue

                results.append(entry)

        return results


class RetrievalLogger(AgentLogger):
    """Specialized logger for retrieval agent with query tracking."""

    def __init__(self, log_dir: str = "agents/logs"):
        super().__init__("retrieval", log_dir)
        self.queries_log_file = self.log_dir / "retrieval_queries.jsonl"

    def log_query(
        self,
        query_type: str,
        query_text: str,
        requester: str,
        session_id: str,
        documents_returned: list[str],
        response_time_ms: int,
        cache_hit: bool = False,
        excerpt_length: Optional[int] = None
    ) -> None:
        """
        Log retrieval query with detailed metadata.

        Args:
            query_type: Type of query (intent|component|concept|navigation|search)
            query_text: The actual query text
            requester: ID of the requesting agent
            session_id: Session identifier
            documents_returned: List of document paths returned
            response_time_ms: Response time in milliseconds
            cache_hit: Whether result was served from cache
            excerpt_length: Length of excerpt if not full document
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        query_entry = {
            "timestamp": timestamp,
            "agent_id": self.agent_id,
            "operation": "query",
            "query": {
                "type": query_type,
                "query_text": query_text,
                "requester": requester,
                "session_id": session_id
            },
            "response": {
                "documents_returned": documents_returned,
                "excerpt_length": excerpt_length,
                "full_document": excerpt_length is None
            },
            "metadata": {
                "response_time_ms": response_time_ms,
                "cache_hit": cache_hit
            }
        }

        self._write_log(self.queries_log_file, query_entry)
        self._write_log(self.operations_log_file, query_entry)


# Convenience functions
def get_logger(agent_id: str) -> AgentLogger:
    """Get logger instance for agent."""
    return AgentLogger(agent_id)


def get_retrieval_logger() -> RetrievalLogger:
    """Get specialized retrieval logger."""
    return RetrievalLogger()
