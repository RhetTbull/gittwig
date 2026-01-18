"""Integration tests for Twig app."""

import pytest

from twig.app import TwigApp


@pytest.mark.asyncio
async def test_app_starts(temp_git_repo):
    """Test that the app starts successfully."""
    app = TwigApp(temp_git_repo)

    async with app.run_test() as _:
        # App should be running
        assert app.is_running

        # Branch list should exist
        branch_list = app.query_one("#branch-list")
        assert branch_list is not None


@pytest.mark.asyncio
async def test_app_loads_branches(temp_git_repo_with_branches):
    """Test that branches are loaded on startup."""
    app = TwigApp(temp_git_repo_with_branches)

    async with app.run_test() as pilot:
        # Wait for data to load
        await pilot.pause()

        branch_list = app.query_one("#branch-list")
        assert branch_list.option_count >= 3  # main, feature/auth, feature/ui


@pytest.mark.asyncio
async def test_navigation_keys(temp_git_repo_with_branches):
    """Test vim navigation keys."""
    app = TwigApp(temp_git_repo_with_branches)

    async with app.run_test() as pilot:
        await pilot.pause()

        # j should move down
        await pilot.press("j")
        await pilot.pause()

        # k should move up
        await pilot.press("k")
        await pilot.pause()


@pytest.mark.asyncio
async def test_help_screen(temp_git_repo):
    """Test help screen opens and closes."""
    app = TwigApp(temp_git_repo)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Open help
        await pilot.press("?")
        await pilot.pause()

        # Help screen should be visible
        assert len(app.screen_stack) > 1

        # Close help
        await pilot.press("escape")
        await pilot.pause()

        # Should be back to main screen
        assert len(app.screen_stack) == 1


@pytest.mark.asyncio
async def test_create_branch_modal(temp_git_repo):
    """Test create branch modal opens."""
    app = TwigApp(temp_git_repo)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Open create branch modal
        await pilot.press("n")
        await pilot.pause()

        # Modal should be visible
        assert len(app.screen_stack) > 1

        # Cancel
        await pilot.press("escape")
        await pilot.pause()


@pytest.mark.asyncio
async def test_filter_branches(temp_git_repo_with_branches):
    """Test branch filtering with / key."""
    app = TwigApp(temp_git_repo_with_branches)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Start filter
        await pilot.press("slash")
        await pilot.pause()

        # Type filter text
        await pilot.press("f", "e", "a", "t", "u", "r", "e")
        await pilot.pause()

        # Submit filter
        await pilot.press("enter")
        await pilot.pause()


@pytest.mark.asyncio
async def test_quit_app(temp_git_repo):
    """Test quitting the app."""
    app = TwigApp(temp_git_repo)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Quit
        await pilot.press("q")
        await pilot.pause()

        # App should no longer be running
        assert not app.is_running
