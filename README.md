# gittwig

A terminal user interface (TUI) for viewing and switching git branches, built with Python and [Textual](https://textual.textualize.io/).

I built this because I wanted a quick way to view git branches and switch between them. Vibe-coded with Claude Code.

This provides a fast, easy way to browse branches, see the commit history for a given branch, identify files changed in a branch, and view file diffs with syntax highlighting. As an open source developer who works with many branches across multiple projects, this is very helpful for figuring out where I left off and juggling multiple branches.

![Screenshot](twig.svg)

## Features

- Browse local and remote branches in a navigable list
- View changed files compared to your default branch
- View commit history unique to each branch
- Syntax-highlighted diff viewer
- Checkout branches with Enter
- Create and delete branches
- Fetch, push, and pull operations
- Filter branches with `/` search
- Vim-style keyboard navigation

## Installation

Requires Python 3.12 or later.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and run:

```bash
uv tool install gittwig
```

To run with `uv` without installing:

```bash
uv tool run --from gittwig twig
```

## Usage

Run `twig` in any git repository:

```bash
twig
```

Or specify a repository path:

```bash
twig /path/to/repo
```

## Keyboard Shortcuts

### Navigation

| Key | Action |
|-----|--------|
| `j` / `k` | Move cursor down / up |
| `h` / `l` | Focus left / right pane |
| `g g` | Go to top of list |
| `G` | Go to bottom of list |
| `Ctrl+d` / `Ctrl+u` | Page down / up |
| `Enter` | Select item / checkout branch |

### Branch Operations

| Key | Action |
|-----|--------|
| `n` | Create new branch |
| `d` | Delete branch (with confirmation) |
| `r` | Refresh data |
| `f` | Fetch from remotes |
| `p` | Push current branch |
| `P` | Pull current branch |

### Other

| Key | Action |
|-----|--------|
| `/` | Search/filter branches |
| `?` | Show help |
| `q` | Quit |
| `Escape` | Close modal / cancel |

## Development

```bash
# Install development dependencies
uv sync --group dev

# Run tests
pytest

# Run linter
ruff check .

# Run type checker
mypy src
```

## License

MIT License - see [LICENSE](LICENSE) for details.
