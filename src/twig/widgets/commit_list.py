from typing import Any

from textual.binding import Binding
from textual.message import Message
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from ..models import Commit


class CommitListView(OptionList):
    """Widget for displaying commit history."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("g,g", "go_to_top", "Top", show=False),
        Binding("G", "go_to_bottom", "Bottom", show=False),
    ]

    class CommitSelected(Message):
        """Emitted when a commit is selected."""

        def __init__(self, commit: Commit) -> None:
            self.commit = commit
            super().__init__()

    class CommitHighlighted(Message):
        """Emitted when a commit is highlighted."""

        def __init__(self, commit: Commit) -> None:
            self.commit = commit
            super().__init__()

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._commits: list[Commit] = []

    def set_commits(self, commits: list[Commit]) -> None:
        """Update the commit list."""
        self._commits = commits
        self._update_display()

    def _update_display(self) -> None:
        """Update the option list display."""
        self.clear_options()
        for commit in self._commits:
            # Format: "abc123 Fix auth bug"
            label = commit.display_line
            self.add_option(Option(label, id=commit.hash))

    def get_selected_commit(self) -> Commit | None:
        """Get the currently selected commit."""
        if self.highlighted is not None and self._commits:
            idx = self.highlighted
            if 0 <= idx < len(self._commits):
                return self._commits[idx]
        return None

    def action_go_to_top(self) -> None:
        """Move cursor to top of list."""
        if self.option_count > 0:
            self.highlighted = 0

    def action_go_to_bottom(self) -> None:
        """Move cursor to bottom of list."""
        if self.option_count > 0:
            self.highlighted = self.option_count - 1

    def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        """Handle option selection."""
        commit = self.get_selected_commit()
        if commit:
            self.post_message(self.CommitSelected(commit))

    def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        """Handle option highlighting."""
        commit = self.get_selected_commit()
        if commit:
            self.post_message(self.CommitHighlighted(commit))
