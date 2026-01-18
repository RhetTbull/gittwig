"""Pytest configuration and fixtures."""

import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        # Create initial commit
        readme = repo_path / "README.md"
        readme.write_text("# Test Repo\n")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        yield repo_path


@pytest.fixture
def temp_git_repo_with_branches(temp_git_repo):
    """Create a temporary git repository with multiple branches."""
    repo_path = temp_git_repo

    # Create feature branch
    subprocess.run(
        ["git", "checkout", "-b", "feature/auth"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Add a file on feature branch
    auth_file = repo_path / "auth.py"
    auth_file.write_text("# Auth module\ndef login():\n    pass\n")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add auth module"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create another branch from main
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "checkout", "-b", "feature/ui"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Add a file on UI branch
    ui_file = repo_path / "ui.py"
    ui_file.write_text("# UI module\ndef render():\n    pass\n")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add UI module"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Go back to main
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    yield repo_path
