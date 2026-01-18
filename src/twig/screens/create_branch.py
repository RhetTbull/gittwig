from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


class CreateBranchModal(ModalScreen[str | None]):
    """Modal for creating a new branch."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    DEFAULT_CSS = """
    CreateBranchModal {
        align: center middle;
    }

    CreateBranchModal > Container {
        width: 60;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }

    CreateBranchModal #title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    CreateBranchModal Label {
        margin: 1 0 0 0;
    }

    CreateBranchModal Input {
        margin: 0 0 1 0;
    }

    CreateBranchModal #error-label {
        color: $error;
        height: 1;
        margin: 0 0 1 0;
    }

    CreateBranchModal Horizontal {
        align: center middle;
        height: auto;
        margin-top: 1;
    }

    CreateBranchModal Button {
        margin: 0 1;
    }
    """

    def __init__(self, start_point: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._start_point = start_point

    def compose(self) -> ComposeResult:
        with Container():
            yield Static("Create New Branch", id="title")
            yield Label("Branch name:")
            yield Input(placeholder="feature/my-new-feature", id="branch-name")
            if self._start_point:
                yield Label(f"From: {self._start_point}")
            yield Static("", id="error-label")
            with Horizontal():
                yield Button("Create", variant="primary", id="create-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_mount(self) -> None:
        """Focus the input when mounted."""
        self.query_one("#branch-name", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "create-btn":
            self._submit()
        elif event.button.id == "cancel-btn":
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input."""
        self._submit()

    def _submit(self) -> None:
        """Validate and submit the branch name."""
        name_input = self.query_one("#branch-name", Input)
        name = name_input.value.strip()

        if not name:
            self._show_error("Branch name cannot be empty")
            return

        # Basic validation
        invalid_chars = [" ", "~", "^", ":", "\\", "?", "*", "["]
        for char in invalid_chars:
            if char in name:
                self._show_error(f"Branch name cannot contain '{char}'")
                return

        if name.startswith("-"):
            self._show_error("Branch name cannot start with '-'")
            return

        if name.endswith(".lock"):
            self._show_error("Branch name cannot end with '.lock'")
            return

        self.dismiss(name)

    def _show_error(self, message: str) -> None:
        """Display an error message."""
        error_label = self.query_one("#error-label", Static)
        error_label.update(message)

    def action_cancel(self) -> None:
        """Cancel and close modal."""
        self.dismiss(None)
