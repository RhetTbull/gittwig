from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Input, Static

from .models import Branch, FileChange
from .screens import ConfirmDeleteModal, CreateBranchModal, HelpScreen
from .services import GitService
from .widgets import (
    BranchListView,
    CommitListView,
    DiffViewer,
    FileListView,
    PaneHeader,
)


class TwigApp(App[None]):
    """Twig - Git Branch Manager TUI Application."""

    TITLE = "Twig - Branch Manager"
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("?", "show_help", "Help"),
        Binding("n", "new_branch", "New"),
        Binding("d", "delete_branch", "Delete"),
        Binding("r", "refresh", "Refresh"),
        Binding("f", "fetch", "Fetch"),
        Binding("p", "push", "Push"),
        Binding("P", "pull", "Pull"),
        Binding("h", "focus_left", "Left", show=False),
        Binding("l", "focus_right", "Right", show=False),
        Binding("slash", "start_filter", "Search", key_display="/"),
        Binding("escape", "cancel_filter", "Cancel", show=False),
        Binding("enter", "select_item", "Select", show=False),
    ]

    def __init__(self, repo_path: Path | None = None):
        super().__init__()
        self.git = GitService(repo_path or Path.cwd())
        self._current_branch: Branch | None = None
        self._selected_file: FileChange | None = None
        self._default_branch: str = "main"
        self._panes: list[str] = ["branch-list", "file-list", "diff-viewer"]
        self._current_pane_index: int = 0
        self._filter_active: bool = False

    def compose(self) -> ComposeResult:
        yield Static("Twig - Branch Manager", id="app-title")

        with Horizontal(id="main-container"):
            # Left pane: Branch list
            with Vertical(id="left-pane"):
                yield PaneHeader("Branches", classes="pane-header")
                yield BranchListView(id="branch-list")

            # Middle pane: Files and Commits
            with Vertical(id="middle-pane"):
                with Vertical(id="middle-top"):
                    yield PaneHeader("Changed Files", classes="pane-header")
                    yield FileListView(id="file-list")
                with Vertical(id="middle-bottom"):
                    yield PaneHeader("Commit History", classes="pane-header")
                    yield CommitListView(id="commit-list")

            # Right pane: Diff viewer
            with Vertical(id="right-pane"):
                yield PaneHeader("Diff View", classes="pane-header")
                yield DiffViewer(id="diff-viewer")

        with Container(id="filter-container"):
            yield Input(placeholder="Filter branches...", id="filter-input")

        yield Static(
            r"\[n]ew \[d]elete \[enter]checkout \[r]efresh \[f]etch \[?]help \[q]uit",
            id="status-bar",
        )

    async def on_mount(self) -> None:
        """Initialize the app when mounted."""
        # Check if we're in a git repo
        if not await self.git.is_git_repo():
            self.notify("Not a git repository!", severity="error")
            return

        # Get default branch for comparisons
        self._default_branch = await self.git.get_default_branch()

        # Load initial data
        await self._refresh_branches()

        # Focus the branch list
        self.query_one("#branch-list").focus()

    async def _refresh_branches(self) -> None:
        """Refresh the branch list."""
        try:
            branches = await self.git.get_branches()
            branch_list = self.query_one("#branch-list", BranchListView)
            branch_list.set_branches(branches)

            # Find and select current branch
            for branch in branches:
                if branch.is_current:
                    self._current_branch = branch
                    break
        except Exception as e:
            self.notify(f"Error loading branches: {e}", severity="error")

    async def _load_branch_details(self, branch: Branch) -> None:
        """Load files and commits for a branch."""
        try:
            # Load changed files (compared to default branch)
            files = await self.git.get_changed_files(branch.name, self._default_branch)
            file_list = self.query_one("#file-list", FileListView)
            file_list.set_files(files)

            # Load commits unique to this branch (not in default branch)
            # If viewing the default branch itself, show recent commits without filter
            if branch.name == self._default_branch:
                commits = await self.git.get_commits(branch.name, base=None, limit=30)
            else:
                commits = await self.git.get_commits(
                    branch.name, base=self._default_branch, limit=30
                )
            commit_list = self.query_one("#commit-list", CommitListView)
            commit_list.set_commits(commits)

            # Clear diff
            diff_viewer = self.query_one("#diff-viewer", DiffViewer)
            diff_viewer.clear_diff()
        except Exception as e:
            self.notify(f"Error loading branch details: {e}", severity="error")

    async def _load_file_diff(self, file_change: FileChange, branch: Branch) -> None:
        """Load diff for a specific file."""
        try:
            diff = await self.git.get_file_diff(file_change.path, branch.name)
            diff_viewer = self.query_one("#diff-viewer", DiffViewer)
            diff_viewer.set_diff(diff)
        except Exception as e:
            self.notify(f"Error loading diff: {e}", severity="error")

    # Event handlers for widgets
    async def on_branch_list_view_branch_highlighted(
        self, event: BranchListView.BranchHighlighted
    ) -> None:
        """Handle branch highlight."""
        self._current_branch = event.branch
        await self._load_branch_details(event.branch)

    async def on_branch_list_view_branch_selected(
        self, event: BranchListView.BranchSelected
    ) -> None:
        """Handle branch selection (checkout)."""
        await self._checkout_branch(event.branch)

    async def on_file_list_view_file_highlighted(
        self, event: FileListView.FileHighlighted
    ) -> None:
        """Handle file highlight."""
        self._selected_file = event.file_change
        if self._current_branch:
            await self._load_file_diff(event.file_change, self._current_branch)

    async def on_file_list_view_file_selected(
        self, event: FileListView.FileSelected
    ) -> None:
        """Handle file selection."""
        self._selected_file = event.file_change
        if self._current_branch:
            await self._load_file_diff(event.file_change, self._current_branch)

    # Actions
    def action_show_help(self) -> None:
        """Show help screen."""
        self.push_screen(HelpScreen())

    async def action_new_branch(self) -> None:
        """Show create branch modal."""
        branch_list = self.query_one("#branch-list", BranchListView)
        start_point = branch_list.get_selected_branch()
        start_name = start_point.name if start_point else None

        async def handle_result(name: str | None) -> None:
            if name:
                try:
                    await self.git.create_branch(name, start_name)
                    self.notify(f"Created branch '{name}'", severity="information")
                    await self._refresh_branches()
                except Exception as e:
                    self.notify(f"Error creating branch: {e}", severity="error")

        self.push_screen(CreateBranchModal(start_name), handle_result)

    async def action_delete_branch(self) -> None:
        """Show delete branch confirmation."""
        branch_list = self.query_one("#branch-list", BranchListView)
        branch = branch_list.get_selected_branch()

        if not branch:
            self.notify("No branch selected", severity="warning")
            return

        if branch.is_current:
            self.notify("Cannot delete current branch", severity="error")
            return

        async def handle_result(confirmed: bool | None) -> None:
            if confirmed:
                try:
                    # Try normal delete first, then force if modal indicated
                    await self.git.delete_branch(branch.name, force=False)
                    self.notify(f"Deleted branch '{branch.name}'", severity="information")
                    await self._refresh_branches()
                except Exception as e:
                    if "not fully merged" in str(e).lower():
                        # Show modal again with unmerged warning
                        self.push_screen(
                            ConfirmDeleteModal(branch.name, is_unmerged=True),
                            handle_force_delete,
                        )
                    else:
                        self.notify(f"Error deleting branch: {e}", severity="error")

        async def handle_force_delete(confirmed: bool | None) -> None:
            if confirmed:
                try:
                    await self.git.delete_branch(branch.name, force=True)
                    self.notify(f"Force deleted branch '{branch.name}'", severity="information")
                    await self._refresh_branches()
                except Exception as e:
                    self.notify(f"Error deleting branch: {e}", severity="error")

        self.push_screen(ConfirmDeleteModal(branch.name), handle_result)

    async def action_refresh(self) -> None:
        """Refresh all data."""
        self.notify("Refreshing...")
        await self._refresh_branches()
        if self._current_branch:
            await self._load_branch_details(self._current_branch)
        self.notify("Refreshed", severity="information")

    async def action_fetch(self) -> None:
        """Fetch from remotes."""
        self.notify("Fetching...")
        try:
            await self.git.fetch()
            await self._refresh_branches()
            self.notify("Fetch complete", severity="information")
        except Exception as e:
            self.notify(f"Fetch failed: {e}", severity="error")

    async def action_push(self) -> None:
        """Push current branch."""
        current = await self.git.get_current_branch()
        if not current:
            self.notify("No branch to push", severity="warning")
            return

        self.notify(f"Pushing {current}...")
        try:
            await self.git.push(current)
            await self._refresh_branches()
            self.notify(f"Pushed {current}", severity="information")
        except Exception as e:
            self.notify(f"Push failed: {e}", severity="error")

    async def action_pull(self) -> None:
        """Pull current branch."""
        current = await self.git.get_current_branch()
        if not current:
            self.notify("No branch to pull", severity="warning")
            return

        self.notify(f"Pulling {current}...")
        try:
            await self.git.pull(current)
            await self._refresh_branches()
            self.notify(f"Pulled {current}", severity="information")
        except Exception as e:
            self.notify(f"Pull failed: {e}", severity="error")

    async def _checkout_branch(self, branch: Branch) -> None:
        """Checkout a branch."""
        if branch.is_current:
            self.notify("Already on this branch", severity="warning")
            return

        try:
            await self.git.checkout_branch(branch.name)
            self.notify(f"Switched to '{branch.name}'", severity="information")
            await self._refresh_branches()
        except Exception as e:
            self.notify(f"Checkout failed: {e}", severity="error")

    def action_focus_left(self) -> None:
        """Focus the pane to the left."""
        if self._current_pane_index > 0:
            self._current_pane_index -= 1
            self._focus_current_pane()

    def action_focus_right(self) -> None:
        """Focus the pane to the right."""
        if self._current_pane_index < len(self._panes) - 1:
            self._current_pane_index += 1
            self._focus_current_pane()

    def _focus_current_pane(self) -> None:
        """Focus the current pane."""
        pane_id = self._panes[self._current_pane_index]
        try:
            self.query_one(f"#{pane_id}").focus()
        except Exception:
            pass

    def action_start_filter(self) -> None:
        """Start filtering branches."""
        self._filter_active = True
        filter_container = self.query_one("#filter-container")
        filter_container.add_class("visible")
        filter_input = self.query_one("#filter-input", Input)
        filter_input.value = ""
        filter_input.focus()

    def action_cancel_filter(self) -> None:
        """Cancel filtering."""
        if self._filter_active:
            self._filter_active = False
            filter_container = self.query_one("#filter-container")
            filter_container.remove_class("visible")
            branch_list = self.query_one("#branch-list", BranchListView)
            branch_list.set_filter("")
            branch_list.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle filter input changes."""
        if event.input.id == "filter-input":
            branch_list = self.query_one("#branch-list", BranchListView)
            branch_list.set_filter(event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle filter input submission."""
        if event.input.id == "filter-input":
            self._filter_active = False
            filter_container = self.query_one("#filter-container")
            filter_container.remove_class("visible")
            self.query_one("#branch-list").focus()

    async def action_select_item(self) -> None:
        """Select the current item (checkout branch)."""
        focused = self.focused
        if isinstance(focused, BranchListView):
            branch = focused.get_selected_branch()
            if branch:
                await self._checkout_branch(branch)
