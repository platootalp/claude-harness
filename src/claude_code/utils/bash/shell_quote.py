"""Shell quoting utilities - re-exported for bash submodule."""
from __future__ import annotations

from claude_code.utils.shell_quote import (
    parse as shell_parse,
    quote as shell_quote,
    try_parse_shell_command,
    try_quote_shell_args,
    ParseEntry,
    ShellParseResult,
    ShellQuoteResult,
)

__all__ = [
    "shell_parse",
    "shell_quote",
    "try_parse_shell_command",
    "try_quote_shell_args",
    "ShellParseResult",
    "ShellQuoteResult",
    "ParseEntry",
]
