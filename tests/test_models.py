"""Tests for data models."""

from datetime import datetime

from gittwig.models.git_models import (
    Branch,
    Commit,
    FileChange,
    FileChangeType,
    SyncStatus,
)


class TestBranch:
    """Tests for Branch model."""

    def test_branch_creation(self):
        """Test basic branch creation."""
        branch = Branch(name="main", is_current=True)
        assert branch.name == "main"
        assert branch.is_current is True
        assert branch.upstream is None
        assert branch.sync_status == SyncStatus.NO_REMOTE

    def test_branch_with_upstream(self):
        """Test branch with upstream tracking."""
        branch = Branch(
            name="feature/auth",
            is_current=False,
            upstream="origin/feature/auth",
            sync_status=SyncStatus.AHEAD,
            ahead_count=2,
        )
        assert branch.upstream == "origin/feature/auth"
        assert branch.sync_status == SyncStatus.AHEAD
        assert branch.ahead_count == 2

    def test_display_name_current(self):
        """Test display name for current branch."""
        branch = Branch(name="main", is_current=True, sync_status=SyncStatus.SYNCED)
        assert branch.display_name == "* main [=]"

    def test_display_name_not_current(self):
        """Test display name for non-current branch."""
        branch = Branch(name="feature/auth", is_current=False, sync_status=SyncStatus.AHEAD)
        assert branch.display_name == "  feature/auth [↑]"

    def test_display_name_no_remote(self):
        """Test display name with no remote."""
        branch = Branch(name="local-only", is_current=False)
        assert branch.display_name == "  local-only"

    def test_is_remote(self):
        """Test remote branch detection."""
        local = Branch(name="main")
        remote = Branch(name="origin/main")
        remotes = Branch(name="remotes/origin/main")

        assert local.is_remote is False
        assert remote.is_remote is True
        assert remotes.is_remote is True


class TestCommit:
    """Tests for Commit model."""

    def test_commit_creation(self):
        """Test basic commit creation."""
        commit = Commit(
            hash="abc123def456",
            short_hash="abc123d",
            subject="Fix authentication bug",
            author="John Doe",
        )
        assert commit.hash == "abc123def456"
        assert commit.short_hash == "abc123d"
        assert commit.subject == "Fix authentication bug"
        assert commit.author == "John Doe"
        assert commit.date is None

    def test_commit_with_date(self):
        """Test commit with date."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        commit = Commit(
            hash="abc123",
            short_hash="abc",
            subject="Test",
            author="Test User",
            date=dt,
        )
        assert commit.date == dt

    def test_display_line(self):
        """Test commit display line formatting."""
        commit = Commit(
            hash="abc123def456",
            short_hash="abc123d",
            subject="Fix authentication bug",
            author="John Doe",
        )
        assert commit.display_line == "abc123d Fix authentication bug"


class TestFileChange:
    """Tests for FileChange model."""

    def test_file_change_creation(self):
        """Test basic file change creation."""
        change = FileChange(
            path="src/app.py",
            change_type=FileChangeType.MODIFIED,
            additions=10,
            deletions=5,
        )
        assert change.path == "src/app.py"
        assert change.change_type == FileChangeType.MODIFIED
        assert change.additions == 10
        assert change.deletions == 5

    def test_display_line_with_stats(self):
        """Test display line with stats."""
        change = FileChange(
            path="src/app.py",
            change_type=FileChangeType.MODIFIED,
            additions=10,
            deletions=5,
        )
        assert change.display_line == "M src/app.py +10-5"

    def test_display_line_no_stats(self):
        """Test display line without stats."""
        change = FileChange(
            path="new_file.py",
            change_type=FileChangeType.ADDED,
        )
        assert change.display_line == "A new_file.py"

    def test_from_status_line_modified(self):
        """Test parsing modified file status."""
        change = FileChange.from_status_line("M  src/file.py")
        assert change.change_type == FileChangeType.MODIFIED
        assert change.path == "src/file.py"

    def test_from_status_line_added(self):
        """Test parsing added file status."""
        change = FileChange.from_status_line("A  new_file.py")
        assert change.change_type == FileChangeType.ADDED

    def test_from_status_line_deleted(self):
        """Test parsing deleted file status."""
        change = FileChange.from_status_line("D  old_file.py")
        assert change.change_type == FileChangeType.DELETED


class TestSyncStatus:
    """Tests for SyncStatus enum."""

    def test_sync_status_values(self):
        """Test sync status display values."""
        assert SyncStatus.SYNCED.value == "="
        assert SyncStatus.AHEAD.value == "↑"
        assert SyncStatus.BEHIND.value == "↓"
        assert SyncStatus.DIVERGED.value == "↕"
        assert SyncStatus.NO_REMOTE.value == ""
