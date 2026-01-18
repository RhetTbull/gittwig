from textual.binding import Binding
from textual.message import Message
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from ..models import FileChange


class FileListView(OptionList):
    """Widget for displaying changed files."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("g,g", "go_to_top", "Top", show=False),
        Binding("G", "go_to_bottom", "Bottom", show=False),
    ]

    class FileSelected(Message):
        """Emitted when a file is selected."""

        def __init__(self, file_change: FileChange) -> None:
            self.file_change = file_change
            super().__init__()

    class FileHighlighted(Message):
        """Emitted when a file is highlighted."""

        def __init__(self, file_change: FileChange) -> None:
            self.file_change = file_change
            super().__init__()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._files: list[FileChange] = []

    def set_files(self, files: list[FileChange]) -> None:
        """Update the file list."""
        self._files = files
        self._update_display()

    def _update_display(self) -> None:
        """Update the option list display."""
        self.clear_options()
        for f in self._files:
            # Format: "M src/app.py +5-2"
            label = f.display_line
            self.add_option(Option(label, id=f.path))

    def get_selected_file(self) -> FileChange | None:
        """Get the currently selected file."""
        if self.highlighted is not None and self._files:
            idx = self.highlighted
            if 0 <= idx < len(self._files):
                return self._files[idx]
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
        file_change = self.get_selected_file()
        if file_change:
            self.post_message(self.FileSelected(file_change))

    def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        """Handle option highlighting."""
        file_change = self.get_selected_file()
        if file_change:
            self.post_message(self.FileHighlighted(file_change))
