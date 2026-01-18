from rich.syntax import Syntax
from rich.text import Text
from textual.binding import Binding
from textual.widgets import RichLog


class DiffViewer(RichLog):
    """Widget for displaying file diffs with syntax highlighting."""

    BINDINGS = [
        Binding("j", "scroll_down", "Scroll Down", show=False),
        Binding("k", "scroll_up", "Scroll Up", show=False),
        Binding("g,g", "scroll_home", "Top", show=False),
        Binding("G", "scroll_end", "Bottom", show=False),
        Binding("ctrl+d", "page_down", "Page Down", show=False),
        Binding("ctrl+u", "page_up", "Page Up", show=False),
    ]

    DEFAULT_CSS = """
    DiffViewer {
        background: $surface;
        scrollbar-gutter: stable;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(highlight=False, markup=False, wrap=False, auto_scroll=False, **kwargs)
        self._diff_content: str = ""

    def set_diff(self, diff: str) -> None:
        """Set the diff content to display."""
        self._diff_content = diff
        self._render_diff()

    def _render_diff(self) -> None:
        """Render the diff with syntax highlighting."""
        self.clear()

        if not self._diff_content:
            self.write(Text("No diff to display", style="dim"))
            return

        # Use Rich's Syntax for diff highlighting
        syntax = Syntax(
            self._diff_content,
            "diff",
            theme="monokai",
            line_numbers=False,
            word_wrap=False,
        )
        self.write(syntax)

    def clear_diff(self) -> None:
        """Clear the diff display."""
        self._diff_content = ""
        self.clear()
        self.write(Text("Select a file to view diff", style="dim"))

    def action_scroll_down(self) -> None:
        """Scroll down one line."""
        self.scroll_relative(y=1)

    def action_scroll_up(self) -> None:
        """Scroll up one line."""
        self.scroll_relative(y=-1)

    def action_page_down(self) -> None:
        """Scroll down half page."""
        self.scroll_relative(y=self.size.height // 2)

    def action_page_up(self) -> None:
        """Scroll up half page."""
        self.scroll_relative(y=-self.size.height // 2)
