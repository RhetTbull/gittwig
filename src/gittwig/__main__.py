"""Entry point for twig CLI."""

import sys
from pathlib import Path

from .app import TwigApp


def main() -> int:
    """Run the Twig TUI application."""
    # Accept optional path argument
    repo_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None

    app = TwigApp(repo_path)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
