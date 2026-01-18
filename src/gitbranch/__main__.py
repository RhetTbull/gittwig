"""Entry point for gitbranch CLI."""

import sys
from pathlib import Path

from .app import GitBranchApp


def main() -> int:
    """Run the GitBranch TUI application."""
    # Accept optional path argument
    repo_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None

    app = GitBranchApp(repo_path)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
