"""Command registry and definition."""

from __future__ import annotations

import argparse
from typing import Callable, Dict, Optional


class Command:
    """Represents a registered CLI command."""

    def __init__(
        self,
        name: str,
        func: Callable,
        parser: argparse.ArgumentParser,
        is_async: bool = False,
    ):
        self.name = name
        self.func = func
        self.parser = parser
        self.is_async = is_async


class CommandRegistry:
    """Registry for managing commands."""

    def __init__(self):
        self._commands: Dict[str, Command] = {}

    def register(self, command: Command) -> None:
        """Register a command."""
        self._commands[command.name] = command

    def get(self, name: str) -> Optional[Command]:
        """Get a command by name."""
        return self._commands.get(name)

    def get_all(self) -> list[Command]:
        """Get all registered commands."""
        return list(self._commands.values())

    def clear(self) -> None:
        """Clear all registered commands."""
        self._commands.clear()
