# arg-kiss — Keep It Stupidly Simple CLI builder on top of argparse

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![PyPI](https://img.shields.io/pypi/v/arg-kiss.svg)](https://pypi.org/project/arg-kiss/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey)]()

Write type-annotated Python functions, get a CLI with argparse's native `--help` — no magic, no bloat.

## ✨ Features

- **Zero Dependencies** — Pure stdlib: `argparse`, `asyncio`, `inspect`
- **Type-Driven** — Automatic arguments from function signatures and type hints
- **Async-Native** — `async def` handlers with automatic event loop management
- **Bool Flags** — Automatic `--name`/`--no-name` mutually exclusive group
- **Command Groups** — Nested subcommands via `cli.group()`
- **Standard --help** — Clean argparse output, nothing custom
- **Colour Output** — Optional coloured error messages and help text

## 🚀 Quick Start

### Installation
```bash
pip install arg-kiss
```

### Usage
```python
from arg_kiss import CLI

cli = CLI(name="todo", description="Task manager", color=True)

@cli.command()
def add(task: str, priority: int = 1, done: bool = False):
    """Add a task."""
    status = "✓" if done else "○"
    print(f"[{status}] {task} (priority: {priority})")

cli.run()
```

```bash
$ python todo.py --help
usage: todo [-h] {add} ...

Task manager

options:
  -h, --help  show this help message and exit

Commands:
  {add}
    add        Add a task.

$ python todo.py add --help
usage: todo add [-h] [--priority PRIORITY] [--done | --no-done] task

Add a task.

positional arguments:
  task

options:
  -h, --help           show this help message and exit
  --priority PRIORITY  (default: 1)
  --done               Enable done
  --no-done            Disable done
```

## 📋 API Reference

### `CLI` class
```python
CLI(name="myapp", description="Description", color=True)
```
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | `None` | Program name |
| `description` | `str` | `None` | Program description |
| `version` | `str` | `None` | Adds `--version` flag |
| `color` | `bool` | `True` | Enable/disable coloured output (help text) |

### Methods

#### `add_global_argument(*flags, **kwargs)`
Add a global argument that applies to **all commands**. These arguments can be placed anywhere in the command line (before or after the command).

```python
cli = CLI(name="myapp")

# Add global flags
cli.add_global_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
cli.add_global_argument("--config", "-c", type=str, help="Config file path")
cli.add_global_argument("--quiet", "-q", action="store_true", help="Suppress output")

@cli.command()
def deploy(environment: str):
    """Deploy to environment."""
    # Global arguments are available in the parsed namespace
    # They're not auto-injected into functions — access via your own logic
    pass
```

**Usage in command line:**
```bash
# Global arguments work with any command
myapp --verbose deploy production
myapp --config settings.json deploy staging
myapp deploy production --verbose  # Order doesn't matter
myapp --quiet backup
```

**Important:** Global arguments are parsed but **not automatically passed** to command functions. Access them via `argparse.Namespace` or implement your own context mechanism.

#### `group(name, description=None, **kwargs)`
Create a command group for nested subcommands.

#### `command(name=None, description=None, arguments=None, **kwargs)`
Decorator for registering a CLI command.

### Type → CLI Mapping
| Function Signature | CLI Argument |
|--------------------|--------------|
| `name: str` | Positional `name` |
| `count: int = 1` | `--count 1` |
| `verbose: bool = False` | `--verbose` / `--no-verbose` |
| `mode: str \| None = None` | `--mode MODE` |

---

### Или, если хотите добавить пример использования глобальных аргументов:

```python
### Global Arguments

Use `add_global_argument()` for flags that apply to all commands:

```python
from arg_kiss import CLI
import sys

cli = CLI(name="myapp")

# Global verbose flag
cli.add_global_argument("--verbose", "-v", action="store_true", help="Verbose output")

@cli.command()
def process(data: str):
    """Process some data."""
    # Access global arguments from sys.argv manually
    # Or better: extend the framework to pass them
    if "--verbose" in sys.argv or "-v" in sys.argv:
        print(f"Processing: {data}")
    return f"Result: {data.upper()}"

@cli.command()
def status():
    """Show status."""
    print("Status OK")

cli.run()
```

**Note:** Global arguments are added to the root parser, making them available for all subcommands. They're not automatically injected into command functions to keep the API simple and explicit.

## 🎨 Colour Support

The `color` parameter controls coloured output:

- **Error messages** — Displayed in red with helpful hints
- **Help text** — Syntax highlighting for usage, options, and commands
- **Respects NO_COLOR** — Automatically disabled when `NO_COLOR` env var is set

```python
# Disable colours globally
cli = CLI(name="myapp", color=False)

# Or via environment variable
export NO_COLOR=1
```

## 📖 Examples

### Multiple Commands
```python
from arg_kiss import CLI

cli = CLI(name="db", description="Simple database", color=True)

db = {}

@cli.command()
def set(key: str, value: str):
    """Store a value."""
    db[key] = value
    print(f"OK: {key} = {value}")

@cli.command()
def get(key: str):
    """Retrieve a value."""
    print(db.get(key, "Not found"))

@cli.command()
def delete(key: str, force: bool = False):
    """Delete a key."""
    if force or key in db:
        db.pop(key, None)
        print(f"Deleted: {key}")
    else:
        print(f"Not found (use --force)")

cli.run()
```

```bash
$ python db.py --help
usage: db [-h] {set,get,delete} ...

Simple database

options:
  -h, --help       show this help message and exit

Commands:
  {set,get,delete}
    set            Store a value.
    get            Retrieve a value.
    delete         Delete a key.

$ python db.py set hello world
OK: hello = world

$ python db.py get hello
world
```

### Command Groups
```python
cli = CLI(name="git", description="Version control")

remote = cli.group("remote", "Manage remotes")
stash = cli.group("stash", "Stash changes")

@remote.command()
def add(name: str, url: str):
    """Add a remote."""
    print(f"Added remote {name} -> {url}")

@stash.command()
def push(message: str = ""):
    """Stash changes."""
    print(f"Stashed: {message or 'WIP'}")

cli.run()
```

```bash
$ python git.py --help
usage: git [-h] {remote,stash} ...

Version control

options:
  -h, --help       show this help message and exit

Commands:
  {remote,stash}
    remote         Manage remotes
    stash          Stash changes

$ python git.py remote --help
usage: git remote [-h] {add} ...

options:
  -h, --help  show this help message and exit

Subcommands:
  {add}
    add        Add a remote.

$ python git.py remote add origin https://github.com/user/repo
Added remote origin -> https://github.com/user/repo
```

### Async Commands
```python
@cli.command()
async def fetch(url: str, retries: int = 3):
    """Fetch a URL."""
    import httpx
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        print(f"Status: {r.status_code}")
```

## ❓ FAQ

### Bool flags?
Automatic `--name`/`--no-name` mutually exclusive group with `store_true`/`store_false`.

### Async?
`async def` handlers auto-run with `asyncio.run()`.

### Colours?
Set `color=False` to disable, or use `NO_COLOR` environment variable.

## 📄 License

MIT — see [LICENSE](LICENSE) file.

---

**Author:** [Fkernel653](https://github.com/Fkernel653)  
**Repository:** [github.com/Fkernel653/arg-kiss](https://github.com/Fkernel653/arg-kiss)  
**PyPI:** [pypi.org/project/arg-kiss](https://pypi.org/project/arg-kiss/)
