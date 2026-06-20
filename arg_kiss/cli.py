"""arg-kiss — Keep It Stupidly Simple CLI builder on top of argparse."""

from __future__ import annotations

import argparse
import inspect
import sys
from typing import Any, Callable, Dict, List, cast

from .utils import get_type_from_annotation, is_bool_type


class Argkiss:
    """
    Advanced wrapper over argparse for building command-line interfaces with decorator-based command registration.

    Features:
        - Decorator-based command registration via @cli.command()
        - Automatic argument inference from function signatures
        - Custom argument flags via @cli.argument() decorator or `arguments` parameter in @cli.command()
        - Support for boolean flags with --flag/--no-flag patterns
        - Async command support (asyncio)
        - Command grouping for nested subcommands
        - Global arguments shared across all commands
        - Colored output support (optional)
    """

    def __init__(
        self,
        name: str | None = None,
        description: str | None = None,
        version: str | None = None,
        color: bool = True,
    ):
        """
        Initialize the CLI application.

        Args:
            name: Program name shown in help output.
            description: Application description shown in help output.
            version: Version string that enables --version flag.
            color: Enable ANSI colored output (Python 3.14+ only).
        """
        self.name = name
        self.description = description
        self.version = version
        self._commands: Dict[str, dict] = {}
        self._parsers_setup = False

        if sys.version_info >= (3, 14):
            self.parser = argparse.ArgumentParser(
                prog=name, description=description, color=color
            )
        else:
            self.parser = argparse.ArgumentParser(prog=name, description=description)

        self.subparsers = self.parser.add_subparsers(dest="_command", title="Commands")

        if version:
            self.parser.add_argument("--version", action="version", version=version)

    def argument(self, *flags: str, **kwargs: Any) -> Callable:
        """
        Decorator to customize argument flags for a command function parameter.

        Use above @cli.command() to override default flag generation and add
        short flags, custom help text, or other argparse options.

        Args:
            *flags: Command-line flags (e.g., '-s', '--string')
            **kwargs: Additional options passed to argparse (help, type, required, choices, action, etc.)

        Returns:
            Decorator that attaches argument metadata to the function

        Example:
            >>> @cli.argument("-v", "--verbose", help="Enable verbose output")
            >>> @cli.argument("-r", "--retries", type=int, help="Number of retries")
            >>> @cli.command()
            >>> def fetch(url: str, verbose: bool = False, retries: int = 3):
            >>>     ...
        """

        def decorator(func):
            cli_args = getattr(func, "_cli_arguments", None)
            if cli_args is None:
                setattr(func, "_cli_arguments", [])
            func._cli_arguments.append({"flags": list(flags), **kwargs})
            return func

        return decorator

    def add_global_argument(self, *flags: str, **kwargs: Any) -> None:
        """
        Add a global argument that applies to all commands.

        Args:
            *flags: Command-line flags (e.g., '-v', '--verbose')
            **kwargs: Additional options passed to argparse (help, type, action, etc.)

        Example:
            >>> cli.add_global_argument('-v', '--verbose', action='store_true', help='Enable verbose mode')
        """
        self.parser.add_argument(*flags, **kwargs)

    def group(
        self, name: str, description: str | None = None, **kwargs: Any
    ) -> Argkiss:
        """
        Create a command group for organizing related subcommands.

        Args:
            name: The name of the command group (e.g., "remote", "container").
            description: Optional description shown in help output.
            **kwargs: Additional arguments passed to argparse's add_parser().

        Returns:
            A new Argkiss instance representing the group.

        Example:
            >>> remote = cli.group("remote", "Manage remotes")
            >>> @remote.command()
            >>> def add(name: str, url: str):
            >>>     ...
        """
        group_parser = self.subparsers.add_parser(
            name, help=description or f"{name} commands", **kwargs
        )
        group_sub = group_parser.add_subparsers(
            dest=f"_group_{name}", title="Subcommands"
        )

        sub_cli = Argkiss.__new__(Argkiss)
        sub_cli.name = name
        sub_cli.description = description
        sub_cli.version = None
        sub_cli._commands = self._commands
        sub_cli._parsers_setup = True
        sub_cli.parser = group_parser
        sub_cli.subparsers = group_sub
        return sub_cli

    def command(
        self,
        name: str | None = None,
        description: str | None = None,
        arguments: List[List] | None = None,
        **parser_kwargs: Any,
    ) -> Callable:
        """
        Decorator for creating a CLI command from a function.

        The decorated function's parameters are automatically converted to
        CLI arguments. Boolean parameters become --flag/--no-flag pairs.

        Can be combined with @cli.argument() or the `arguments` parameter to customize
        individual parameter flags.

        Args:
            name: Custom command name (defaults to function name with underscores replaced by dashes).
            description: Command description (defaults to function docstring).
            arguments: List of argument definitions in [flags..., {kwargs}] format.
                      Each item is a list where the last element is a dict of argparse options.
            **parser_kwargs: Additional arguments passed to argparse's add_parser().

        Returns:
            Decorator function that registers the command.

        Example:
            >>> @cli.command()
            >>> def greet(name: str, uppercase: bool = False):
            >>>     \"\"\"Greet a person.\"\"\"
            >>>     msg = f"Hello, {name}!"
            >>>     return msg.upper() if uppercase else msg

        Example with @cli.argument():
            >>> @cli.argument("-u", "--uppercase", help="Convert to uppercase")
            >>> @cli.command()
            >>> def greet(name: str, uppercase: bool = False):
            >>>     msg = f"Hello, {name}!"
            >>>     return msg.upper() if uppercase else msg

        Example with arguments parameter:
            >>> @cli.command(arguments=[
            >>>     ["-n", "--name", {"help": "Your name"}],
            >>>     ["-u", "--uppercase", {"action": "store_true", "help": "Convert to uppercase"}]
            >>> ])
            >>> def greet(name: str, uppercase: bool = False):
            >>>     msg = f"Hello, {name}!"
            >>>     return msg.upper() if uppercase else msg
        """

        def decorator(func: Callable) -> Callable:
            cmd_name = name or func.__name__.replace("_", "-")
            cmd_description = description or (func.__doc__ or "").strip()
            is_async = inspect.iscoroutinefunction(func)

            parser = self.subparsers.add_parser(
                cmd_name,
                help=cmd_description.split("\n")[0] if cmd_description else None,
                description=cmd_description,
                **parser_kwargs,
            )

            if arguments:
                for arg_def in arguments:
                    flags = []
                    kwargs = {}
                    for item in arg_def:
                        if isinstance(item, str):
                            flags.append(item)
                        elif isinstance(item, dict):
                            kwargs.update(item)
                    if flags:
                        cli_args = getattr(func, "_cli_arguments", None)
                        if cli_args is None:
                            setattr(func, "_cli_arguments", [])
                        cast(Any, func)._cli_arguments.append(
                            {"flags": flags, **kwargs}
                        )

            self._commands[cmd_name] = {
                "func": func,
                "parser": parser,
                "is_async": is_async,
            }
            return func

        return decorator

    def _setup_parsers(self):
        for cmd_info in self._commands.values():
            func = cmd_info["func"]
            parser = cmd_info["parser"]

            cli_args = getattr(func, "_cli_arguments", None)
            explicit_dests = set()

            if cli_args:
                for arg_config in cli_args:
                    flags = arg_config["flags"]
                    kwargs = {k: v for k, v in arg_config.items() if k != "flags"}

                    param_name = None
                    for flag in flags:
                        if flag.startswith("--"):
                            param_name = flag.lstrip("-").replace("-", "_")
                            break
                        elif not flag.startswith("-"):
                            param_name = flag
                            break

                    if not param_name:
                        param_name = flags[-1].lstrip("-").replace("-", "_")

                    param = inspect.signature(func).parameters.get(param_name)

                    arg_kwargs = {}

                    is_bool_action = False
                    if "action" in kwargs:
                        action = kwargs["action"]
                        if action in ("store_true", "store_false"):
                            arg_kwargs["action"] = action
                            is_bool_action = True
                            if "default" not in kwargs:
                                arg_kwargs["default"] = (
                                    False if action == "store_true" else True
                                )
                        elif action == "version":
                            arg_kwargs["action"] = "version"
                        elif action == "boolean_optional_action":
                            arg_kwargs["action"] = argparse.BooleanOptionalAction
                        else:
                            arg_kwargs["action"] = action
                    elif param and is_bool_type(param):
                        arg_kwargs["action"] = argparse.BooleanOptionalAction

                    if not is_bool_action and "action" not in kwargs:
                        if "type" in kwargs:
                            arg_kwargs["type"] = kwargs["type"]
                        elif param:
                            arg_kwargs["type"] = get_type_from_annotation(
                                param.annotation,
                                param.default
                                if param.default is not inspect.Parameter.empty
                                else None,
                            )

                    if "default" in kwargs:
                        arg_kwargs["default"] = kwargs["default"]
                    elif param and param.default is not inspect.Parameter.empty:
                        arg_kwargs["default"] = param.default

                    if "required" in kwargs:
                        arg_kwargs["required"] = kwargs["required"]
                    elif (
                        param
                        and param.default is inspect.Parameter.empty
                        and not is_bool_type(param)
                        and not is_bool_action
                    ):
                        arg_kwargs["required"] = True

                    if "help" in kwargs:
                        arg_kwargs["help"] = kwargs["help"]

                    if "choices" in kwargs:
                        arg_kwargs["choices"] = kwargs["choices"]

                    if "dest" in kwargs:
                        arg_kwargs["dest"] = kwargs["dest"]
                    else:
                        arg_kwargs["dest"] = param_name

                    parser.add_argument(*flags, **arg_kwargs)
                    explicit_dests.add(arg_kwargs.get("dest", param_name))

            for param_name, param in inspect.signature(func).parameters.items():
                if param_name in explicit_dests:
                    continue
                has_default = param.default is not inspect.Parameter.empty

                if is_bool_type(param):
                    base_flag = param_name.replace("_", "-")

                    if has_default:
                        default_val = param.default
                        parser.add_argument(
                            f"--{base_flag}",
                            action=argparse.BooleanOptionalAction,
                            default=default_val,
                            dest=param_name,
                            help=f"{param_name} (default: {default_val})",
                        )
                    else:
                        parser.add_argument(
                            f"--{base_flag}",
                            action=argparse.BooleanOptionalAction,
                            required=True,
                            dest=param_name,
                            help=f"{param_name} (required)",
                        )
                elif not has_default:
                    parser.add_argument(
                        param_name,
                        type=get_type_from_annotation(param.annotation, param.default),
                        help=param_name,
                    )
                else:
                    parser.add_argument(
                        f"--{param_name.replace('_', '-')}",
                        type=get_type_from_annotation(param.annotation, param.default),
                        default=param.default,
                        help=f"{param_name} (default: {param.default})",
                    )

    def run(self, args: List[str] | None = None) -> None:
        """
        Parse command-line arguments and execute the appropriate command.

        Args:
            args: Command-line arguments (defaults to sys.argv[1:]).
        """
        args = sys.argv[1:] if args is None else args

        if not self._parsers_setup:
            self._setup_parsers()
            self._parsers_setup = True

        namespace = self.parser.parse_args(args)
        namespace_dict = vars(namespace)

        if namespace._command is None:
            self.parser.print_help()
            return

        command_parts = [namespace._command]
        command_parts.extend(
            v for k, v in namespace_dict.items() if k.startswith("_group_") and v
        )
        full_command = ":".join(command_parts)
        command_info = self._commands.get(full_command)

        if command_info is None:
            self.parser.print_help()
            return

        func_kwargs = {k: v for k, v in namespace_dict.items() if not k.startswith("_")}

        result = (
            command_info["func"](**func_kwargs)
            if not command_info["is_async"]
            else __import__("asyncio").run(command_info["func"](**func_kwargs))
        )

        if result is not None:
            sys.stdout.write(str(result) + "\n")

    def __call__(self, args: List[str] | None = None) -> None:
        """
        Make the CLI instance callable, delegating to run().

        Args:
            args: Command-line arguments (defaults to sys.argv[1:]).

        Example:
            >>> cli = Argkiss()
            >>> cli()  # Equivalent to cli.run()
        """
        return self.run(args)
