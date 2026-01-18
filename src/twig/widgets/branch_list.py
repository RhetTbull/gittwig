from typing import Any

from textual.binding import Binding
from textual.message import Message
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from ..models import Branch


class BranchListView(OptionList):
    """Widget for displaying and selecting branches."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("g,g", "go_to_top", "Top", show=False),
        Binding("G", "go_to_bottom", "Bottom", show=False),
        Binding("ctrl+d", "page_down", "Page Down", show=False),
        Binding("ctrl+u", "page_up", "Page Up", show=False),
    ]

    class BranchSelected(Message):
        """Emitted when a branch is selected."""

        def __init__(self, branch: Branch) -> None:
            self.branch = branch
            super().__init__()

    class BranchHighlighted(Message):
        """Emitted when a branch is highlighted (cursor moved)."""

        def __init__(self, branch: Branch) -> None:
            self.branch = branch
            super().__init__()

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._branches: list[Branch] = []
        self._filtered_branches: list[Branch] = []
        self._filter_text: str = ""

    def set_branches(self, branches: list[Branch]) -> None:
        """Update the branch list."""
        self._branches = branches
        self._apply_filter()

    def _apply_filter(self) -> None:
        """Apply current filter and update display."""
        if self._filter_text:
            self._filtered_branches = [
                b for b in self._branches
                if self._filter_text.lower() in b.name.lower()
            ]
        else:
            self._filtered_branches = self._branches.copy()

        self._update_display()

    def _update_display(self) -> None:
        """Update the option list display."""
        self.clear_options()
        for branch in self._filtered_branches:
            # Format: "* main [=]" or "  feature/auth [↑]"
            prefix = "* " if branch.is_current else "  "
            status = f" [{branch.sync_status.value}]" if branch.sync_status.value else ""
            label = f"{prefix}{branch.name}{status}"
            self.add_option(Option(label, id=branch.name))

    def set_filter(self, text: str) -> None:
        """Set filter text for branches."""
        self._filter_text = text
        self._apply_filter()

    def get_selected_branch(self) -> Branch | None:
        """Get the currently selected branch."""
        if self.highlighted is not None and self._filtered_branches:
            idx = self.highlighted
            if 0 <= idx < len(self._filtered_branches):
                return self._filtered_branches[idx]
        return None

    def get_highlighted_branch(self) -> Branch | None:
        """Get the currently highlighted branch."""
        return self.get_selected_branch()

    def action_go_to_top(self) -> None:
        """Move cursor to top of list."""
        if self.option_count > 0:
            self.highlighted = 0

    def action_go_to_bottom(self) -> None:
        """Move cursor to bottom of list."""
        if self.option_count > 0:
            self.highlighted = self.option_count - 1

    def action_page_down(self) -> None:
        """Move cursor down by half page."""
        if self.option_count > 0:
            # Move by ~10 items or to end
            new_idx = min(
                (self.highlighted or 0) + 10,
                self.option_count - 1
            )
            self.highlighted = new_idx

    def action_page_up(self) -> None:
        """Move cursor up by half page."""
        if self.option_count > 0:
            # Move by ~10 items or to start
            new_idx = max((self.highlighted or 0) - 10, 0)
            self.highlighted = new_idx

    def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        """Handle option selection."""
        branch = self.get_selected_branch()
        if branch:
            self.post_message(self.BranchSelected(branch))

    def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        """Handle option highlighting."""
        branch = self.get_highlighted_branch()
        if branch:
            self.post_message(self.BranchHighlighted(branch))
