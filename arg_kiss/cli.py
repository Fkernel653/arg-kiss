"""arg-kiss — Keep It Stupidly Simple CLI builder on top of argparse."""

from __future__ import annotations

import argparse
import inspect
import sys
from typing import Any, Callable, Dict, List, Optional

from ._types import TypeResolver
from .argument import Argument, ArgumentBuilder
from .command import Command, CommandRegistry


class Argkiss:
    """
    Main CLI application class with decorator-based command registration.

    Example:
        >>> cli = Argkiss(name="myapp", description="My awesome CLI")
        >>>
        >>> @cli.command()
        >>> def greet(name: str, uppercase: bool = False):
        >>>     return f"Hello, {name}!" if not uppercase else f"HELLO, {name.upper()}!"
        >>>
        >>> cli()
    """

    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        version: Optional[str] = None,
        color: bool = True,
        boolean_optional: bool = True,
    ):
        self._name = name
        self._description = description
        self._version = version
        self._color = color
        self._boolean_optional = boolean_optional

        self._registry = CommandRegistry()
        self._global_args: List[Argument] = []
        self._parsers_initialized = False

        self._root_parser = self._create_root_parser()
        self._subparsers = self._root_parser.add_subparsers(
            dest="_command", title="Commands"
        )

    def _create_root_parser(self) -> argparse.ArgumentParser:
        """Create the root argument parser with proper configuration."""
        parser_kwargs: Dict[str, Any] = {
            "prog": self._name,
            "description": self._description,
        }

        if sys.version_info >= (3, 14):
            parser_kwargs["color"] = self._color

        parser = argparse.ArgumentParser(**parser_kwargs)

        if self._version:
            parser.add_argument("--version", action="version", version=self._version)

        return parser

    def add_global_argument(self, *flags: str, **kwargs) -> None:
        """
        Add a global argument available to all commands.

        Example:
            >>> cli.add_global_argument("-v", "--verbose", action="store_true")
        """
        argument = ArgumentBuilder().with_flags(*flags).with_options(**kwargs).build()

        self._global_args.append(argument)
        self._root_parser.add_argument(*flags, **kwargs)

    def argument(self, *flags: str, **kwargs):
        """
        Decorator to customize argument flags for a command.

        Example:
            >>> @cli.argument("-u", "--uppercase", help="Convert to uppercase")
            >>> @cli.command()
            >>> def greet(name: str, uppercase: bool = False):
            >>>     ...
        """
        argument = ArgumentBuilder().with_flags(*flags).with_options(**kwargs).build()

        def decorator(func: Callable) -> Callable:
            if not hasattr(func, "_cli_arguments"):
                setattr(func, "_cli_arguments", [])
            func._cli_arguments.append(argument)  # type: ignore
            return func

        return decorator

    def group(self, name: str, description: Optional[str] = None, **kwargs):
        """
        Create a command group for organizing related commands.

        Example:
            >>> remote = cli.group("remote", "Manage remote repositories")
            >>> @remote.command()
            >>> def add(name: str, url: str):
            >>>     ...
        """
        group_parser = self._subparsers.add_parser(
            name, help=description or f"{name} commands", **kwargs
        )
        group_subparsers = group_parser.add_subparsers(
            dest=f"_group_{name}", title="Subcommands"
        )

        sub_cli = Argkiss.__new__(Argkiss)
        sub_cli.__dict__.update(
            {
                "_name": name,
                "_description": description,
                "_version": None,
                "_color": self._color,
                "_boolean_optional": self._boolean_optional,
                "_registry": self._registry,
                "_global_args": self._global_args,
                "_parsers_initialized": True,
                "_root_parser": group_parser,
                "_subparsers": group_subparsers,
            }
        )
        return sub_cli

    def command(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **parser_kwargs,
    ):
        """
        Decorator to register a function as a CLI command.

        Example:
            >>> @cli.command()
            >>> def greet(name: str, uppercase: bool = False):
            >>>     ...
        """

        def decorator(func: Callable) -> Callable:
            cmd_name = name or func.__name__.replace("_", "-")
            cmd_desc = description or (func.__doc__ or "").strip()

            parser = self._subparsers.add_parser(
                cmd_name,
                help=cmd_desc.split("\n")[0] if cmd_desc else None,
                description=cmd_desc,
                **parser_kwargs,
            )

            if hasattr(func, "_cli_arguments"):
                for arg in func._cli_arguments:  # type: ignore
                    self._add_argument_to_parser(parser, arg)

            command = Command(
                name=cmd_name,
                func=func,
                parser=parser,
                is_async=inspect.iscoroutinefunction(func),
            )
            self._registry.register(command)
            return func

        return decorator

    def _add_argument_to_parser(
        self, parser: argparse.ArgumentParser, argument: Argument
    ) -> None:
        """Add an argument to a parser with proper configuration."""
        resolver = TypeResolver(
            argument=argument, boolean_optional=self._boolean_optional
        )

        resolved_options = resolver.resolve()

        parser.add_argument(*argument.flags, **resolved_options)

    def _initialize_parsers(self) -> None:
        """Initialize all command parsers with their arguments."""
        if self._parsers_initialized:
            return

        for command in self._registry.get_all():
            self._add_function_arguments(command)

        self._parsers_initialized = True

    def _add_function_arguments(self, command: Command) -> None:
        """Automatically add arguments from function parameters."""
        func = command.func
        parser = command.parser
        signature = inspect.signature(func)

        handled_params: set[str] = set()

        if hasattr(func, "_cli_arguments"):
            for arg in func._cli_arguments:  # type: ignore
                param_name = arg.get_dest_name()
                if param_name:
                    handled_params.add(param_name)

        for param_name, param in signature.parameters.items():
            if param_name in handled_params:
                continue

            is_global = False
            for arg in self._global_args:
                if arg.get_dest_name() == param_name:
                    is_global = True
                    break

            if is_global:
                continue

            builder = ArgumentBuilder().from_parameter(param_name, param)

            if self._is_boolean_parameter(param):
                builder.with_boolean_optional(self._boolean_optional)

            argument = builder.build()
            self._add_argument_to_parser(parser, argument)

    def _is_boolean_parameter(self, param: inspect.Parameter) -> bool:
        """Check if a parameter is boolean."""
        annotation = param.annotation

        if annotation is bool:
            return True

        if annotation is inspect.Parameter.empty:
            return isinstance(param.default, bool)

        return False

    def run(self, args: Optional[List[str]] = None) -> None:
        """
        Parse arguments and execute the appropriate command.

        Args:
            args: Command-line arguments (defaults to sys.argv[1:])
        """
        args = sys.argv[1:] if args is None else args

        self._initialize_parsers()

        namespace = self._root_parser.parse_args(args)
        ns_dict = vars(namespace)

        if namespace._command is None:
            self._root_parser.print_help()
            return

        cmd_parts = [namespace._command]
        cmd_parts.extend(v for k, v in ns_dict.items() if k.startswith("_group_") and v)
        full_cmd = ":".join(cmd_parts)

        command = self._registry.get(full_cmd)
        if not command:
            self._root_parser.print_help()
            return

        kwargs = {k: v for k, v in ns_dict.items() if not k.startswith("_")}

        result = (
            __import__("asyncio").run(command.func(**kwargs))
            if command.is_async
            else command.func(**kwargs)
        )

        if result is not None:
            sys.stdout.write(str(result) + "\n")

    def __call__(self, args: Optional[List[str]] = None) -> None:
        """Make the CLI instance callable."""
        self.run(args)
