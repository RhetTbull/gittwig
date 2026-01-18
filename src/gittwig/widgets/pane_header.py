from typing import Any

from textual.widgets import Static


class PaneHeader(Static):
    """Styled header for panes."""

    DEFAULT_CSS = """
    PaneHeader {
        background: $primary;
        color: $text;
        text-align: center;
        height: 1;
        text-style: bold;
    }
    """

    def __init__(self, title: str, **kwargs: Any) -> None:
        super().__init__(title, **kwargs)
