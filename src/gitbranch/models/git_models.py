from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SyncStatus(Enum):
    """Branch sync status with remote."""

    SYNCED = "="  # Up to date with remote
    AHEAD = "↑"  # Local commits not pushed
    BEHIND = "↓"  # Remote commits not pulled
    DIVERGED = "↕"  # Both ahead and behind
    NO_REMOTE = ""  # No upstream configured


@dataclass
class Branch:
    """Represents a git branch."""

    name: str
    is_current: bool = False
    upstream: str | None = None
    commit_hash: str = ""
    sync_status: SyncStatus = SyncStatus.NO_REMOTE
    ahead_count: int = 0
    behind_count: int = 0

    @property
    def display_name(self) -> str:
        """Format branch name for display."""
        prefix = "* " if self.is_current else "  "
        status = f" [{self.sync_status.value}]" if self.sync_status.value else ""
        return f"{prefix}{self.name}{status}"

    @property
    def is_remote(self) -> bool:
        """Check if this is a remote branch."""
        return self.name.startswith("remotes/") or self.name.startswith("origin/")


@dataclass
class Commit:
    """Represents a git commit."""

    hash: str
    short_hash: str
    subject: str
    author: str
    date: datetime | None = None

    @property
    def display_line(self) -> str:
        """Format commit for single-line display."""
        return f"{self.short_hash} {self.subject}"


class FileChangeType(Enum):
    """Type of file change."""

    MODIFIED = "M"
    ADDED = "A"
    DELETED = "D"
    RENAMED = "R"
    COPIED = "C"
    UNTRACKED = "?"


@dataclass
class FileChange:
    """Represents a changed file."""

    path: str
    change_type: FileChangeType
    additions: int = 0
    deletions: int = 0
    old_path: str | None = None  # For renames

    @property
    def display_line(self) -> str:
        """Format file change for display."""
        stats = ""
        if self.additions or self.deletions:
            stats = f" +{self.additions}-{self.deletions}"
        return f"{self.change_type.value} {self.path}{stats}"

    @classmethod
    def from_status_line(cls, line: str) -> "FileChange":
        """Parse a git status line like 'M  src/file.py'."""
        if not line or len(line) < 2:
            return cls(path="", change_type=FileChangeType.MODIFIED)

        status_char = line[0]
        path = line[2:].strip() if len(line) > 2 else ""

        change_type_map = {
            "M": FileChangeType.MODIFIED,
            "A": FileChangeType.ADDED,
            "D": FileChangeType.DELETED,
            "R": FileChangeType.RENAMED,
            "C": FileChangeType.COPIED,
            "?": FileChangeType.UNTRACKED,
        }
        change_type = change_type_map.get(status_char, FileChangeType.MODIFIED)

        return cls(path=path, change_type=change_type)
