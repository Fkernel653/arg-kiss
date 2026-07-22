"""Type resolution for command-line arguments."""

from __future__ import annotations

import argparse
import inspect
from typing import Any, Dict, get_args, get_origin

from .argument import Argument


class TypeResolver:
    """Resolve argument types and options for argparse."""

    def __init__(self, argument: Argument, boolean_optional: bool = True):
        self.argument = argument
        self.boolean_optional = boolean_optional
        self.param = None

    def resolve(self) -> Dict[str, Any]:
        """Resolve the full argument configuration for argparse."""
        result = dict(self.argument.options)

        if "action" in result:
            return result

        param_type = self._get_parameter_type()

        if self._is_bool_type(param_type):
            return self._resolve_bool_type(result)
        else:
            return self._resolve_other_type(result, param_type)

    def _get_parameter_type(self) -> Any:
        """Get the type annotation from the parameter."""
        if self.param is None:
            return None

        return self.param.annotation

    def _is_bool_type(self, param_type: Any) -> bool:
        """Check if a type is boolean."""
        if param_type is bool:
            return True

        if param_type is None:
            return False

        if param_type is inspect.Parameter.empty:
            return False

        if isinstance(param_type, str):
            return param_type in {"bool", "Optional[bool]", "Union[bool, None]"}

        origin = get_origin(param_type)
        if origin is not None:
            args = get_args(param_type)
            none_type = type(None)
            non_none = [a for a in args if a is not none_type]
            return len(non_none) == 1 and non_none[0] is bool

        return False

    def _resolve_bool_type(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve configuration for boolean arguments."""
        if "default" not in result:
            result["default"] = False

        if self.boolean_optional:
            result["action"] = argparse.BooleanOptionalAction
        else:
            default = result["default"]
            if default:
                result["action"] = "store_false"
            else:
                result["action"] = "store_true"

        return result

    def _resolve_other_type(
        self, result: Dict[str, Any], param_type: Any
    ) -> Dict[str, Any]:
        """Resolve configuration for non-boolean arguments."""
        if param_type and param_type is not inspect.Parameter.empty:
            if param_type is not str and isinstance(param_type, type):
                result["type"] = param_type

        return result
