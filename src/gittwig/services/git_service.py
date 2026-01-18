import asyncio
import subprocess
from datetime import datetime
from pathlib import Path

from ..models.git_models import Branch, Commit, FileChange, FileChangeType, SyncStatus


class GitError(Exception):
    """Raised when a git command fails."""

    pass


class GitService:
    """Service for interacting with git repositories."""

    def __init__(self, repo_path: Path | str | None = None):
        """Initialize git service.

        Args:
            repo_path: Path to the git repository. Defaults to current directory.
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()

    async def _run_git(self, *args: str, check: bool = True) -> str:
        """Run a git command asynchronously.

        Args:
            *args: Git command arguments (without 'git' prefix).
            check: If True, raise GitError on non-zero exit.

        Returns:
            Command stdout as string.

        Raises:
            GitError: If command fails and check is True.
        """
        cmd = ["git", "-C", str(self.repo_path)] + list(args)
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if check and proc.returncode != 0:
            error_msg = (
                stderr.decode().strip() or f"Git command failed: {' '.join(args)}"
            )
            raise GitError(error_msg)

        return stdout.decode().strip()

    def _run_git_sync(self, *args: str, check: bool = True) -> str:
        """Run a git command synchronously.

        Args:
            *args: Git command arguments (without 'git' prefix).
            check: If True, raise GitError on non-zero exit.

        Returns:
            Command stdout as string.
        """
        cmd = ["git", "-C", str(self.repo_path)] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)

        if check and result.returncode != 0:
            error_msg = result.stderr.strip() or f"Git command failed: {' '.join(args)}"
            raise GitError(error_msg)

        return result.stdout.strip()

    async def is_git_repo(self) -> bool:
        """Check if the current path is a git repository."""
        try:
            await self._run_git("rev-parse", "--git-dir")
            return True
        except GitError:
            return False

    async def get_current_branch(self) -> str:
        """Get the name of the current branch."""
        return await self._run_git("branch", "--show-current")

    async def get_default_branch(self) -> str:
        """Get the default branch name (main/master)."""
        try:
            ref = await self._run_git("symbolic-ref", "refs/remotes/origin/HEAD")
            return ref.split("/")[-1]
        except GitError:
            # Fallback: check if main or master exists
            branches = await self._run_git("branch", "--list", "main", "master")
            if "main" in branches:
                return "main"
            elif "master" in branches:
                return "master"
            return "main"  # Default fallback

    async def get_branches(self, include_remote: bool = False) -> list[Branch]:
        """Get list of branches.

        Args:
            include_remote: Include remote-tracking branches.

        Returns:
            List of Branch objects.
        """
        format_str = "%(refname:short)|%(upstream:short)|%(objectname:short)"
        args = ["branch", f"--format={format_str}"]
        if include_remote:
            args.append("-a")

        output = await self._run_git(*args)
        current = await self.get_current_branch()

        branches = []
        for line in output.splitlines():
            if not line.strip():
                continue

            parts = line.split("|")
            name = parts[0]
            upstream = parts[1] if len(parts) > 1 and parts[1] else None
            commit_hash = parts[2] if len(parts) > 2 else ""

            # Skip HEAD pointer
            if name == "origin/HEAD":
                continue

            branch = Branch(
                name=name,
                is_current=(name == current),
                upstream=upstream,
                commit_hash=commit_hash,
            )

            # Get sync status if upstream exists
            if upstream and not name.startswith("remotes/"):
                sync_status, ahead, behind = await self._get_sync_status(name, upstream)
                branch.sync_status = sync_status
                branch.ahead_count = ahead
                branch.behind_count = behind

            branches.append(branch)

        return branches

    async def _get_sync_status(
        self, branch: str, upstream: str
    ) -> tuple[SyncStatus, int, int]:
        """Get sync status between local branch and upstream.

        Returns:
            Tuple of (SyncStatus, ahead_count, behind_count).
        """
        try:
            output = await self._run_git(
                "rev-list", "--left-right", "--count", f"{branch}...{upstream}"
            )
            parts = output.split()
            if len(parts) >= 2:
                ahead = int(parts[0])
                behind = int(parts[1])

                if ahead == 0 and behind == 0:
                    return SyncStatus.SYNCED, 0, 0
                elif ahead > 0 and behind == 0:
                    return SyncStatus.AHEAD, ahead, 0
                elif ahead == 0 and behind > 0:
                    return SyncStatus.BEHIND, 0, behind
                else:
                    return SyncStatus.DIVERGED, ahead, behind
        except GitError:
            pass

        return SyncStatus.NO_REMOTE, 0, 0

    async def get_commits(
        self, branch: str, base: str | None = None, limit: int = 50
    ) -> list[Commit]:
        """Get commit history for a branch.

        Args:
            branch: Branch name.
            base: Base branch. If provided, only shows commits in branch but not in base.
            limit: Maximum number of commits to return.

        Returns:
            List of Commit objects.
        """
        format_str = "%H|%h|%s|%an|%aI"
        try:
            if base:
                # Show only commits in branch that are not in base
                ref_spec = f"{base}..{branch}"
            else:
                ref_spec = branch
            output = await self._run_git(
                "log", ref_spec, f"--format={format_str}", f"-n{limit}"
            )
        except GitError:
            return []

        commits = []
        for line in output.splitlines():
            if not line.strip():
                continue

            parts = line.split("|", 4)
            if len(parts) >= 4:
                date = None
                if len(parts) >= 5 and parts[4]:
                    try:
                        date = datetime.fromisoformat(parts[4])
                    except ValueError:
                        pass

                commits.append(
                    Commit(
                        hash=parts[0],
                        short_hash=parts[1],
                        subject=parts[2],
                        author=parts[3],
                        date=date,
                    )
                )

        return commits

    async def get_changed_files(
        self, branch: str, base: str | None = None
    ) -> list[FileChange]:
        """Get files changed in a branch compared to base.

        Args:
            branch: Branch to compare.
            base: Base branch. Defaults to default branch.

        Returns:
            List of FileChange objects.
        """
        if base is None:
            base = await self.get_default_branch()

        try:
            # Get file list with status
            output = await self._run_git("diff", "--name-status", f"{base}...{branch}")
        except GitError:
            return []

        files = []
        for line in output.splitlines():
            if not line.strip():
                continue

            parts = line.split("\t")
            if len(parts) >= 2:
                status_char = parts[0][0]  # First char of status
                path = parts[-1]  # Last part is path (handles renames)
                old_path = parts[1] if len(parts) > 2 else None

                change_type_map = {
                    "M": FileChangeType.MODIFIED,
                    "A": FileChangeType.ADDED,
                    "D": FileChangeType.DELETED,
                    "R": FileChangeType.RENAMED,
                    "C": FileChangeType.COPIED,
                }
                change_type = change_type_map.get(status_char, FileChangeType.MODIFIED)

                files.append(
                    FileChange(
                        path=path,
                        change_type=change_type,
                        old_path=old_path,
                    )
                )

        # Get stats for additions/deletions
        try:
            stat_output = await self._run_git("diff", "--numstat", f"{base}...{branch}")
            stat_map = {}
            for line in stat_output.splitlines():
                parts = line.split("\t")
                if len(parts) >= 3:
                    adds = int(parts[0]) if parts[0] != "-" else 0
                    dels = int(parts[1]) if parts[1] != "-" else 0
                    path = parts[2]
                    stat_map[path] = (adds, dels)

            for f in files:
                if f.path in stat_map:
                    f.additions, f.deletions = stat_map[f.path]
        except GitError:
            pass

        return files

    async def get_file_diff(
        self, file_path: str, branch: str, base: str | None = None
    ) -> str:
        """Get diff for a specific file.

        Args:
            file_path: Path to the file.
            branch: Branch to compare.
            base: Base branch. Defaults to default branch.

        Returns:
            Diff output as string.
        """
        if base is None:
            base = await self.get_default_branch()

        try:
            return await self._run_git("diff", f"{base}...{branch}", "--", file_path)
        except GitError:
            return ""

    async def checkout_branch(self, branch: str) -> None:
        """Checkout a branch.

        Args:
            branch: Branch name to checkout.

        Raises:
            GitError: If checkout fails.
        """
        await self._run_git("checkout", branch)

    async def create_branch(self, name: str, start_point: str | None = None) -> Branch:
        """Create a new branch.

        Args:
            name: Name for the new branch.
            start_point: Starting commit/branch. Defaults to HEAD.

        Returns:
            The newly created Branch.

        Raises:
            GitError: If branch creation fails.
        """
        args = ["branch", name]
        if start_point:
            args.append(start_point)

        await self._run_git(*args)

        return Branch(name=name, is_current=False)

    async def delete_branch(self, name: str, force: bool = False) -> None:
        """Delete a branch.

        Args:
            name: Branch name to delete.
            force: Force delete even if not merged.

        Raises:
            GitError: If deletion fails.
        """
        flag = "-D" if force else "-d"
        await self._run_git("branch", flag, name)

    async def fetch(self, remote: str = "origin", prune: bool = True) -> str:
        """Fetch from remote.

        Args:
            remote: Remote name.
            prune: Remove stale remote-tracking branches.

        Returns:
            Fetch output.
        """
        args = ["fetch", remote]
        if prune:
            args.append("--prune")
        return await self._run_git(*args, check=False)

    async def push(self, branch: str | None = None, set_upstream: bool = True) -> str:
        """Push branch to remote.

        Args:
            branch: Branch to push. Defaults to current branch.
            set_upstream: Set upstream tracking.

        Returns:
            Push output.
        """
        if branch is None:
            branch = await self.get_current_branch()

        args = ["push"]
        if set_upstream:
            args.extend(["-u", "origin", branch])
        else:
            args.extend(["origin", branch])

        return await self._run_git(*args)

    async def pull(self, branch: str | None = None) -> str:
        """Pull changes for branch.

        Args:
            branch: Branch to pull. Defaults to current branch.

        Returns:
            Pull output.
        """
        if branch is None:
            branch = await self.get_current_branch()

        return await self._run_git("pull", "origin", branch)

    async def get_uncommitted_changes(self) -> list[FileChange]:
        """Get uncommitted changes (both staged and unstaged).

        Returns:
            List of FileChange objects for modified working directory files.
        """
        files_map: dict[str, FileChange] = {}

        change_type_map = {
            "M": FileChangeType.MODIFIED,
            "A": FileChangeType.ADDED,
            "D": FileChangeType.DELETED,
            "R": FileChangeType.RENAMED,
            "C": FileChangeType.COPIED,
        }

        # Get unstaged changes
        try:
            unstaged_output = await self._run_git("diff", "--name-status")
            for line in unstaged_output.splitlines():
                if not line.strip():
                    continue
                parts = line.split("\t")
                if len(parts) >= 2:
                    status_char = parts[0][0]
                    path = parts[-1]
                    old_path = parts[1] if len(parts) > 2 else None
                    change_type = change_type_map.get(
                        status_char, FileChangeType.MODIFIED
                    )
                    files_map[path] = FileChange(
                        path=path,
                        change_type=change_type,
                        old_path=old_path,
                    )
        except GitError:
            pass

        # Get staged changes (these take precedence for status)
        try:
            staged_output = await self._run_git("diff", "--name-status", "--cached")
            for line in staged_output.splitlines():
                if not line.strip():
                    continue
                parts = line.split("\t")
                if len(parts) >= 2:
                    status_char = parts[0][0]
                    path = parts[-1]
                    old_path = parts[1] if len(parts) > 2 else None
                    change_type = change_type_map.get(
                        status_char, FileChangeType.MODIFIED
                    )
                    files_map[path] = FileChange(
                        path=path,
                        change_type=change_type,
                        old_path=old_path,
                    )
        except GitError:
            pass

        files = list(files_map.values())

        # Get stats for additions/deletions (combined staged + unstaged)
        try:
            stat_output = await self._run_git("diff", "--numstat", "HEAD")
            stat_map = {}
            for line in stat_output.splitlines():
                parts = line.split("\t")
                if len(parts) >= 3:
                    adds = int(parts[0]) if parts[0] != "-" else 0
                    dels = int(parts[1]) if parts[1] != "-" else 0
                    path = parts[2]
                    stat_map[path] = (adds, dels)

            for f in files:
                if f.path in stat_map:
                    f.additions, f.deletions = stat_map[f.path]
        except GitError:
            pass

        return files

    async def get_uncommitted_file_diff(self, file_path: str) -> str:
        """Get diff for an uncommitted file (staged + unstaged changes).

        Args:
            file_path: Path to the file.

        Returns:
            Diff output as string.
        """
        try:
            return await self._run_git("diff", "HEAD", "--", file_path)
        except GitError:
            return ""
