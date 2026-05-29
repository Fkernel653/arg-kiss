# arg-kiss — Keep It Stupidly Simple CLI builder on top of argparse

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![PyPI](https://img.shields.io/pypi/v/arg-kiss.svg)](https://pypi.org/project/arg-kiss/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey)]()

Write type-annotated Python functions, get a CLI with argparse's native `--help` — no magic, no bloat.

> **arg-kiss** is a fork of [**cliss**](https://github.com/Fkernel653/cliss) with one key difference: **no custom `--help`**.  
> It uses argparse's standard help output instead of a custom formatter. If you want coloured help, `Argument` objects, and more features — use [cliss](https://github.com/Fkernel653/cliss).

## ✨ Features

- **Zero Dependencies** — Pure stdlib: `argparse`, `asyncio`, `inspect`
- **Type-Driven** — Automatic arguments from function signatures and type hints
- **Async-Native** — `async def` handlers with automatic event loop management
- **Bool Flags** — Automatic `--name`/`--no-name` mutually exclusive group
- **Command Groups** — Nested subcommands via `cli.group()`
- **Standard --help** — Clean argparse output, nothing custom

## 🚀 Quick Start

### Installation
```bash
pip install arg-kiss
```

### Usage
```python
from arg_kiss import CLI

cli = CLI(name="todo", description="Task manager")

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
CLI(name="myapp", description="Description")
```
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | `None` | `None` | Program name |
| `description` | `str` | `None` | `None` | Program description |
| `version` | `str` | `None` | `None` | Adds `--version` flag |

### Type → CLI Mapping
| Function Signature | CLI Argument |
|--------------------|--------------|
| `name: str` | Positional `name` |
| `count: int = 1` | `--count 1` |
| `verbose: bool = False` | `--verbose` / `--no-verbose` |
| `mode: str \| None = None` | `--mode MODE` |

## 📖 Examples

### Multiple Commands
```python
from arg_kiss import CLI

cli = CLI(name="db", description="Simple database")

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

### arg-kiss vs cliss?
**arg-kiss** is a fork of [cliss](https://github.com/Fkernel653/cliss) that removes the custom `--help` formatter. Use arg-kiss if you want:

- Standard argparse `--help` output
- Zero dependencies beyond stdlib
- Simple, predictable behaviour

Use **cliss** if you want:
- Coloured terminal output
- `Argument` descriptor objects
- Custom error messages
- More features overall

### Why fork instead of a flag?
The custom help system in cliss is deeply integrated (custom formatter, colour library, error handling). A fork keeps arg-kiss clean and minimal while letting cliss grow independently.

### Bool flags?
Automatic `--name`/`--no-name` mutually exclusive group with `store_true`/`store_false`.

### Async?
`async def` handlers auto-run with `asyncio.run()`.

## 📄 License

MIT — see [LICENSE](LICENSE) file.

---

**Author:** [Fkernel653](https://github.com/Fkernel653)  
**Repository:** [github.com/Fkernel653/arg-kiss](https://github.com/Fkernel653/arg-kiss)  
**PyPI:** [pypi.org/project/arg-kiss](https://pypi.org/project/arg-kiss/)  
**Based on:** [cliss](https://github.com/Fkernel653/cliss) — a richer CLI framework with coloured help
