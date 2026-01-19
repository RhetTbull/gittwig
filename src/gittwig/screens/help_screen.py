from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Static

HELP_TEXT = """\
[bold]Navigation[/bold]
  j / k         Move cursor down / up
  h / l         Focus left / right pane
  g g           Go to top of list
  G             Go to bottom of list
  Ctrl+d / u    Page down / up
  Enter         Select item / checkout branch

[bold]Branch Operations[/bold]
  n             Create new branch
  d             Delete branch (with confirmation)
  r             Refresh data
  f             Fetch from remotes
  p             Push current branch
  P             Pull current branch

[bold]Other[/bold]
  /             Search/filter branches
  ?             Show this help
  q             Quit
  Escape        Close modal / cancel

[bold]Branch Status Symbols[/bold]
  *             Current branch (checked out)
  [=]           Synced with remote
  [↑]           Ahead of remote (unpushed commits)
  [↓]           Behind remote (unpulled commits)
  [↕]           Diverged (both ahead and behind)
  [remote]      Remote-only (not checked out locally)
"""


class HelpScreen(ModalScreen[None]):
    """Modal screen showing keyboard shortcuts."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("q", "dismiss", "Close"),
        Binding("?", "dismiss", "Close"),
    ]

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }

    HelpScreen > Container {
        width: 60;
        height: auto;
        max-height: 80%;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }

    HelpScreen #help-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    HelpScreen #help-content {
        height: auto;
    }

    HelpScreen #help-footer {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Container():
            yield Static("Keyboard Shortcuts", id="help-title")
            yield Static(HELP_TEXT, id="help-content")
            yield Static("Press Escape or ? to close", id="help-footer")
