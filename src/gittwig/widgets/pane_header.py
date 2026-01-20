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

    def __init__(self, title: str, number: int | None = None, **kwargs: Any) -> None:
        if number is not None:
            display = f"[{number}] {title}"
        else:
            display = title
        super().__init__(display, **kwargs)
