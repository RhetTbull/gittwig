# CLAUDE.md

## Project Overview

Gittwig (`twig`) is a terminal UI application for managing Git branches, built with Python and Textual. It provides interactive branch browsing, diff viewing, commit history, and common git operations (checkout, create, delete, fetch, push, pull).

## Build & Run

```bash
# Install dependencies
uv sync --group dev

# Run the app
python -m gittwig          # current directory
python -m gittwig /path    # specific repo

# Install as tool
uv tool install gittwig
twig
```

## Testing & Quality

```bash
pytest                # run all tests
ruff check .          # lint (line length 100, rules: E/F/W/I)
ruff format .         # format
mypy src              # type check (strict mode, Python 3.12)
```

Tests use pytest-asyncio (auto mode). Fixtures in `tests/conftest.py` create temporary git repos.

## Architecture

Layered design under `src/gittwig/`:

- **models/** - Dataclasses: `Branch`, `Commit`, `FileChange`, `SyncStatus` enum
- **services/** - `GitService`: async git operations via subprocess
- **widgets/** - Textual widgets: `BranchListView`, `FileListView`, `CommitListView`, `DiffViewer`, `PaneHeader`. Each emits custom `Message` types.
- **screens/** - Modals: `CreateBranchModal`, `ConfirmDeleteModal`, `HelpScreen`
- **app.py** - `TwigApp`: main app orchestrating state, events, and pane layout
- **styles.tcss** - Textual CSS styling

## Code Conventions

- Python 3.12+, strict mypy typing throughout
- snake_case for modules/functions, CamelCase for classes
- Leading underscore for private attributes (`_branches`, `_filter_text`)
- Kebab-case for widget IDs (`"branch-list"`, `"diff-viewer"`)
- Async/await for all git operations
- Custom `Message` subclasses for widget-to-app communication
- 100-character line length

## Versioning

Semantic versioning managed by bump2version (`.bumpversion.cfg`). Version tracked in `src/gittwig/__init__.py` and `pyproject.toml`.
