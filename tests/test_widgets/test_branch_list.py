"""Tests for BranchListView widget."""

import pytest

from twig.models import Branch, SyncStatus
from twig.widgets import BranchListView


@pytest.mark.asyncio
async def test_branch_list_set_branches():
    """Test setting branches on the list."""
    widget = BranchListView()

    branches = [
        Branch(name="main", is_current=True, sync_status=SyncStatus.SYNCED),
        Branch(name="feature/auth", is_current=False, sync_status=SyncStatus.AHEAD),
    ]

    widget.set_branches(branches)
    assert widget.option_count == 2


@pytest.mark.asyncio
async def test_branch_list_filter():
    """Test branch filtering."""
    widget = BranchListView()

    branches = [
        Branch(name="main", is_current=True),
        Branch(name="feature/auth", is_current=False),
        Branch(name="feature/ui", is_current=False),
        Branch(name="bugfix/login", is_current=False),
    ]

    widget.set_branches(branches)
    assert widget.option_count == 4

    # Filter to feature branches
    widget.set_filter("feature")
    assert widget.option_count == 2

    # Clear filter
    widget.set_filter("")
    assert widget.option_count == 4


@pytest.mark.asyncio
async def test_branch_list_get_selected():
    """Test getting selected branch."""
    widget = BranchListView()

    branches = [
        Branch(name="main", is_current=True),
        Branch(name="feature/auth", is_current=False),
    ]

    widget.set_branches(branches)

    # Initially highlighted should be first item
    widget.highlighted = 0
    selected = widget.get_selected_branch()
    assert selected is not None
    assert selected.name == "main"
