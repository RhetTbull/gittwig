from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Static


class ConfirmDeleteModal(ModalScreen[bool]):
    """Modal for confirming branch deletion."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("y", "confirm", "Yes"),
        Binding("n", "cancel", "No"),
    ]

    DEFAULT_CSS = """
    ConfirmDeleteModal {
        align: center middle;
    }

    ConfirmDeleteModal > Container {
        width: 50;
        height: auto;
        border: thick $error;
        background: $surface;
        padding: 1 2;
    }

    ConfirmDeleteModal #title {
        text-align: center;
        text-style: bold;
        color: $error;
        margin-bottom: 1;
    }

    ConfirmDeleteModal #message {
        text-align: center;
        margin-bottom: 1;
    }

    ConfirmDeleteModal #warning {
        text-align: center;
        color: $warning;
        margin-bottom: 1;
    }

    ConfirmDeleteModal Checkbox {
        margin: 1 0;
    }

    ConfirmDeleteModal Horizontal {
        align: center middle;
        height: auto;
        margin-top: 1;
    }

    ConfirmDeleteModal Button {
        margin: 0 1;
    }
    """

    def __init__(self, branch_name: str, is_unmerged: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._branch_name = branch_name
        self._is_unmerged = is_unmerged
        self._force_delete = False

    def compose(self) -> ComposeResult:
        with Container():
            yield Static("Delete Branch", id="title")
            yield Static(
                f"Are you sure you want to delete '[bold]{self._branch_name}[/bold]'?",
                id="message",
            )
            if self._is_unmerged:
                yield Static(
                    "Warning: This branch has unmerged changes!",
                    id="warning",
                )
                yield Checkbox("Force delete (lose unmerged changes)", id="force-checkbox")
            with Horizontal():
                yield Button("Delete", variant="error", id="delete-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "delete-btn":
            self._submit()
        elif event.button.id == "cancel-btn":
            self.dismiss(False)

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle force delete checkbox."""
        self._force_delete = event.value

    def _submit(self) -> None:
        """Submit deletion request."""
        if self._is_unmerged and not self._force_delete:
            # If unmerged and not force, show reminder to check the box
            self.app.notify(
                "Check the force delete box to delete unmerged branch",
                severity="warning",
            )
            return
        self.dismiss(True)

    def action_confirm(self) -> None:
        """Confirm deletion."""
        self._submit()

    def action_cancel(self) -> None:
        """Cancel deletion."""
        self.dismiss(False)

    @property
    def force_delete(self) -> bool:
        """Whether to force delete."""
        return self._force_delete
