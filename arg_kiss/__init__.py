"""arg-kiss — Keep It Stupidly Simple CLI builder on top of argparse."""

from ._types import TypeResolver
from .argument import Argument, ArgumentBuilder
from .cli import Argkiss
from .command import Command, CommandRegistry
from .parsers import ParserFactory

__all__ = [
    "Argkiss",
    "Argument",
    "ArgumentBuilder",
    "Command",
    "CommandRegistry",
    "TypeResolver",
    "ParserFactory",
]
