"""Argument definition and builder pattern."""

from __future__ import annotations

import inspect
from typing import Any, Dict, List, Optional


class Argument:
    """Represents a command-line argument definition."""

    def __init__(
        self,
        flags: List[str],
        options: Dict[str, Any],
        param_name: Optional[str] = None,
    ):
        self.flags = flags
        self.options = options
        self._param_name = param_name

    def get_dest_name(self) -> Optional[str]:
        """Get the destination parameter name for this argument."""
        if self._param_name:
            return self._param_name

        if "dest" in self.options:
            return self.options["dest"]

        for flag in self.flags:
            if flag.startswith("--"):
                return flag.lstrip("-").replace("-", "_")

        if self.flags:
            return self.flags[-1].lstrip("-").replace("-", "_")

        return None


class ArgumentBuilder:
    """Builder pattern for creating Argument objects."""

    def __init__(self):
        self._flags: List[str] = []
        self._options: Dict[str, Any] = {}
        self._param_name: Optional[str] = None

    def with_flags(self, *flags: str) -> ArgumentBuilder:
        """Set the command-line flags for this argument."""
        self._flags = list(flags)
        return self

    def with_options(self, **options) -> ArgumentBuilder:
        """Set additional options for this argument."""
        self._options.update(options)
        return self

    def with_param_name(self, name: str) -> ArgumentBuilder:
        """Set the parameter name this argument maps to."""
        self._param_name = name
        return self

    def from_parameter(self, name: str, param: inspect.Parameter) -> ArgumentBuilder:
        """Build an argument from a function parameter."""
        self._param_name = name

        if param.default is inspect.Parameter.empty:
            self._flags = [name]
        else:
            flag = f"--{name.replace('_', '-')}"
            self._flags = [flag]
            self._options["default"] = param.default

        return self

    def with_boolean_optional(self, enabled: bool) -> ArgumentBuilder:
        """Configure boolean argument handling."""
        if not self._param_name:
            return self

        if not self._is_boolean():
            return self

        if enabled:
            self._options["action"] = "boolean_optional_action"
        else:
            default = self._options.get("default", False)
            self._options["action"] = "store_false" if default else "store_true"

        return self

    def _is_boolean(self) -> bool:
        """Check if this argument represents a boolean type."""
        return False

    def build(self) -> Argument:
        """Build the Argument object."""
        return Argument(
            flags=self._flags, options=self._options, param_name=self._param_name
        )
