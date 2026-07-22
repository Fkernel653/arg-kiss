# arg-kiss — Keep It Stupidly Simple CLI builder on top of argparse

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![PyPI](https://img.shields.io/pypi/v/arg-kiss.svg)](https://pypi.org/project/arg-kiss/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey)]()
[![Ruff](https://img.shields.io/badge/code%20style-ruff-261230?logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)

Write type-annotated Python functions, get a CLI with argparse's native `--help` — no magic, no bloat.

## 🚀 Quick Start
```bash
pip install arg-kiss                    # Python 3.10+
```
```python
from arg_kiss import Argkiss

cli = Argkiss(name="todo", description="Task manager", color=True)

@cli.command()
def add(task: str, priority: int = 1, done: bool = False):
    """Add a task."""
    status = "✓" if done else "○"
    print(f"[{status}] {task} (priority: {priority})")

@cli.command()
def list_all():
    """Show all tasks."""
    print("Nothing yet!")

cli()
```

```bash
$ python todo.py add "Buy milk" --priority 2
[○] Buy milk (priority: 2)

$ python todo.py list-all
Nothing yet!

$ python todo.py --help
usage: todo [-h] {add,list-all} ...

Task manager

positional arguments:
  {add,list-all}
    add           Add a task.
    list-all      Show all tasks.

options:
  -h, --help      show this help message and exit
```

## 📋 Commands & Features

### `@cli.command()` — Define commands from functions
```python
@cli.command()
def fetch(url: str, retries: int = 3):
    """Download from URL with retries"""
    print(f"Fetched {url} (retries: {retries})")
```

### `@cli.argument()` — Customize argument flags

Use `@cli.argument()` above `@cli.command()` to customize flags, help text, and behavior for individual parameters.

```python
@cli.argument("-u", "--user", help="Username")
@cli.argument("-p", "--port", type=int, default=8080, help="Port number")
@cli.argument("--ssl", action="store_true", help="Enable SSL")
@cli.command()
def connect(user: str, port: int = 8080, ssl: bool = False):
    """Connect to server"""
    print(f"Connecting as {user} on port {port} (SSL: {ssl})")
```

### Type → CLI mapping

| Function signature | CLI argument |
|--------------------|---------------|
| `name: str` | Positional `name` |
| `count: int = 1` | `--count 1` |
| `verbose: bool = False` | `--verbose` / `--no-verbose` |
| `mode: str \| None = None` | `--mode MODE` |

### Boolean flags — Two modes

By default, boolean parameters get `--flag/--no-flag` pairs:

```python
cli = Argkiss(name="app", boolean_optional=True)  # default

@cli.command()
def run(verbose: bool = False):
    """Run with --verbose or --no-verbose"""
```

To disable and use simple `--flag` with `store_true`/`store_false`:

```python
cli = Argkiss(name="app", boolean_optional=False)

@cli.command()
def run(verbose: bool = False):
    """Run with --verbose to enable"""
```

### Command groups
```python
remote = cli.group("remote", "Manage remotes")

@remote.command()
def add(name: str, url: str):
    print(f"Added remote {name} -> {url}")

@remote.command()
def remove(name: str):
    print(f"Removed remote {name}")
```

Usage:
```bash
$ python app.py remote add origin https://github.com/user/repo
Added remote origin -> https://github.com/user/repo

$ python app.py remote remove origin
Removed remote origin
```

### Global arguments (apply to all commands)
```python
cli.add_global_argument("--verbose", "-v", action="store_true", help="Verbose output")
cli.add_global_argument("--config", "-c", type=str, help="Config file path")

@cli.command()
def deploy(environment: str):
    """Deploy to environment."""
    # Global arguments available in parsed namespace
    pass
```

### Async support
```python
@cli.command()
async def fetch(url: str, retries: int = 3):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        print(f"Status: {r.status_code}")
```

## 🎨 CLI Configuration

```python
cli = Argkiss(
    name="myapp",                      # Program name (default: None)
    description="Does amazing things", # Description in help (default: None)
    version="2.0.0",                   # Adds --version flag (default: None)
    color=True,                        # ANSI colours (default: True)
    boolean_optional=True,             # --flag/--no-flag for bools (default: True)
)
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | `str \| None` | `None` | Program name in help |
| `description` | `str \| None` | `None` | Description in help |
| `version` | `str \| None` | `None` | Adds `--version` flag |
| `color` | `bool` | `True` | Enable/disable coloured output |
| `boolean_optional` | `bool` | `True` | Use `--flag/--no-flag` for bool params |

### Disable colours via environment
```bash
NO_COLOR=1 python myapp.py --help
```

## 📄 License & Acknowledgments

MIT License — Built with Python standard library:

| Module | Purpose |
|--------|---------|
| `argparse` | CLI parsing engine |
| `asyncio` | Async command execution |
| `inspect` | Signature introspection |

**Author:** [Fkernel653](https://github.com/Fkernel653)
**Project:** [GitHub](https://github.com/Fkernel653/arg-kiss) • [PyPI](https://pypi.org/project/arg-kiss/)
