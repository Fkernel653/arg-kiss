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
from arg_kiss import CLI

cli = CLI(name="todo", description="Task manager", color=True)

@cli.command()
def add(task: str, priority: int = 1, done: bool = False):
    """Add a task."""
    status = "✓" if done else "○"
    print(f"[{status}] {task} (priority: {priority})")

cli()
```

## 📋 Commands & Features

### `@cli.command()` — Define commands from functions
```python
@cli.command()
def fetch(url: str, retries: int = 3):
    """Download from URL with retries"""
    print(f"Fetched {url} (retries: {retries})")
```

### Type → CLI mapping

| Function signature | CLI argument |
|--------------------|---------------|
| `name: str` | Positional `name` |
| `count: int = 1` | `--count 1` |
| `verbose: bool = False` | `--verbose` / `--no-verbose` |
| `mode: str \| None = None` | `--mode MODE` |

### Command groups
```python
remote = cli.group("remote", "Manage remotes")

@remote.command()
def add(name: str, url: str):
    print(f"Added remote {name} -> {url}")
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
cli = CLI(
    name="myapp",                      # Program name (default: None)
    description="Does amazing things", # Description in help (default: None)
    version="2.0.0",                   # Adds --version flag (default: None)
    color=False,                       # Disable ANSI colours (default: True)
)
```

| Option | Description |
|--------|-------------|
| `name` | Program name in help (default: `None`) |
| `description` | Description in help (default: `None`) |
| `version` | Adds `--version` flag (default: `None`) |
| `color` | Enable/disable coloured output (default: `True`) |

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
