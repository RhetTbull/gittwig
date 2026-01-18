"""Tests for GitService."""

import pytest

from gitbranch.services.git_service import GitError, GitService


@pytest.mark.asyncio
class TestGitService:
    """Tests for GitService class."""

    async def test_is_git_repo(self, temp_git_repo):
        """Test git repository detection."""
        service = GitService(temp_git_repo)
        assert await service.is_git_repo() is True

    async def test_is_not_git_repo(self, tmp_path):
        """Test non-git directory detection."""
        service = GitService(tmp_path)
        assert await service.is_git_repo() is False

    async def test_get_current_branch(self, temp_git_repo):
        """Test getting current branch name."""
        service = GitService(temp_git_repo)
        branch = await service.get_current_branch()
        assert branch == "main"

    async def test_get_branches(self, temp_git_repo_with_branches):
        """Test listing branches."""
        service = GitService(temp_git_repo_with_branches)
        branches = await service.get_branches()

        branch_names = [b.name for b in branches]
        assert "main" in branch_names
        assert "feature/auth" in branch_names
        assert "feature/ui" in branch_names

    async def test_get_branches_current_marked(self, temp_git_repo_with_branches):
        """Test that current branch is marked."""
        service = GitService(temp_git_repo_with_branches)
        branches = await service.get_branches()

        current_branches = [b for b in branches if b.is_current]
        assert len(current_branches) == 1
        assert current_branches[0].name == "main"

    async def test_create_branch(self, temp_git_repo):
        """Test creating a new branch."""
        service = GitService(temp_git_repo)
        branch = await service.create_branch("feature/new")

        assert branch.name == "feature/new"

        # Verify branch exists
        branches = await service.get_branches()
        branch_names = [b.name for b in branches]
        assert "feature/new" in branch_names

    async def test_create_branch_from_start_point(self, temp_git_repo_with_branches):
        """Test creating branch from specific start point."""
        service = GitService(temp_git_repo_with_branches)
        await service.create_branch("feature/from-auth", "feature/auth")

        branches = await service.get_branches()
        branch_names = [b.name for b in branches]
        assert "feature/from-auth" in branch_names

    async def test_delete_branch_unmerged_fails(self, temp_git_repo_with_branches):
        """Test deleting an unmerged branch fails without force."""
        service = GitService(temp_git_repo_with_branches)

        # Trying to delete unmerged feature/ui without force should fail
        with pytest.raises(GitError) as exc_info:
            await service.delete_branch("feature/ui")

        assert "not fully merged" in str(exc_info.value)

    async def test_delete_branch_force(self, temp_git_repo_with_branches):
        """Test force deleting an unmerged branch."""
        service = GitService(temp_git_repo_with_branches)

        # Force delete feature/auth (unmerged)
        await service.delete_branch("feature/auth", force=True)

        branches = await service.get_branches()
        branch_names = [b.name for b in branches]
        assert "feature/auth" not in branch_names

    async def test_checkout_branch(self, temp_git_repo_with_branches):
        """Test checking out a branch."""
        service = GitService(temp_git_repo_with_branches)

        await service.checkout_branch("feature/auth")

        current = await service.get_current_branch()
        assert current == "feature/auth"

    async def test_get_commits(self, temp_git_repo_with_branches):
        """Test getting commit history."""
        service = GitService(temp_git_repo_with_branches)
        commits = await service.get_commits("feature/auth")

        assert len(commits) >= 1
        # Should have at least "Add auth module" and "Initial commit"
        subjects = [c.subject for c in commits]
        assert "Add auth module" in subjects

    async def test_get_commits_limit(self, temp_git_repo):
        """Test commit limit."""
        service = GitService(temp_git_repo)
        commits = await service.get_commits("main", limit=1)

        assert len(commits) == 1

    async def test_get_changed_files(self, temp_git_repo_with_branches):
        """Test getting changed files between branches."""
        service = GitService(temp_git_repo_with_branches)
        files = await service.get_changed_files("feature/auth", "main")

        assert len(files) == 1
        assert files[0].path == "auth.py"

    async def test_get_file_diff(self, temp_git_repo_with_branches):
        """Test getting file diff."""
        service = GitService(temp_git_repo_with_branches)
        diff = await service.get_file_diff("auth.py", "feature/auth", "main")

        assert "auth.py" in diff
        assert "+# Auth module" in diff

    async def test_get_default_branch(self, temp_git_repo):
        """Test getting default branch."""
        service = GitService(temp_git_repo)
        default = await service.get_default_branch()

        # Should be main (our fixture creates main)
        assert default == "main"


@pytest.mark.asyncio
class TestGitServiceErrors:
    """Tests for GitService error handling."""

    async def test_checkout_nonexistent_branch(self, temp_git_repo):
        """Test error when checking out nonexistent branch."""
        service = GitService(temp_git_repo)

        with pytest.raises(GitError):
            await service.checkout_branch("nonexistent")

    async def test_delete_current_branch(self, temp_git_repo):
        """Test error when deleting current branch."""
        service = GitService(temp_git_repo)

        with pytest.raises(GitError):
            await service.delete_branch("main")

    async def test_create_duplicate_branch(self, temp_git_repo):
        """Test error when creating duplicate branch."""
        service = GitService(temp_git_repo)

        with pytest.raises(GitError):
            await service.create_branch("main")
