"""Parser factory and utilities."""

from __future__ import annotations

import argparse
import sys
from typing import Any, Optional


class ParserFactory:
    """Factory for creating argument parsers."""

    @staticmethod
    def create_parser(
        name: Optional[str] = None,
        description: Optional[str] = None,
        color: bool = True,
        version: Optional[str] = None,
    ) -> argparse.ArgumentParser:
        """Create a new argument parser."""
        kwargs: dict[str, Any] = {
            "prog": name,
            "description": description,
        }

        if sys.version_info >= (3, 14):
            kwargs["color"] = color

        parser = argparse.ArgumentParser(**kwargs)

        if version:
            parser.add_argument("--version", action="version", version=version)

        return parser
