"""
Local shell-quote compatible module using bashlex.

This module provides a shell-quote compatible API (parse, quote) using bashlex
as the underlying parser. Since shell-quote npm package's Python port is not
available on PyPI, we implement the same API using bashlex.

TypeScript equivalent: shellQuote.ts (wrapping shell-quote npm package)
"""

from __future__ import annotations

from typing import cast

import bashlex
import bashlex.ast as ast

# =============================================================================
# Type Aliases
# =============================================================================

ParseEntry = str | dict[str, str]


# =============================================================================
# Parse
# =============================================================================


def parse(command: str, env: dict[str, str] | None = None) -> list[ParseEntry]:
    """Parse a shell command into tokens (shell-quote compatible API).

    Args:
        command: The shell command string to parse.
        env: Optional environment dict for variable expansion (not currently used).

    Returns:
        A list of tokens: strings for words/assignments, dicts for operators.
        Operator dicts have the form {"op": "|"} or {"op": ";"} etc.
    """
    if not command:
        return []

    def walk(node: ast.node) -> list[ParseEntry]:
        tokens: list[ParseEntry] = []

        if isinstance(node, ast.node):
            # Pipe nodes (|)
            if hasattr(node, "pipe"):
                tokens.append({"op": node.pipe})

            # Redirection nodes (>, <, >>, <<, etc.)
            elif hasattr(node, "redirect"):
                redir = getattr(node, "redirect", None)
                if redir is not None:
                    # Try to get the operator
                    op = getattr(node, "op", None)
                    if op is not None:
                        tokens.append({"op": op})

            # Operator nodes (;, &&, ||, etc.)
            elif hasattr(node, "op"):
                tokens.append({"op": node.op})

            # Word/assignment nodes
            elif hasattr(node, "word"):
                tokens.append(node.word)

            # Recurse into parts
            if hasattr(node, "parts"):
                for part in node.parts:
                    tokens.extend(walk(part))

        return tokens

    try:
        nodes = bashlex.parse(command)
    except bashlex.errors.ParseError:
        # Fall back to simple whitespace splitting for unparseable commands
        return cast(list[ParseEntry], command.split())

    tokens: list[ParseEntry] = []
    for node in nodes:
        tokens.extend(walk(node))
    return tokens


# =============================================================================
# Quote
# =============================================================================


_NEED_QUOTE_RE = None  # Lazily initialized


def _get_need_quote_re():
    global _NEED_QUOTE_RE
    if _NEED_QUOTE_RE is None:
        import re
        # Characters that require quoting
        _NEED_QUOTE_RE = re.compile(r"[ \t\n\r\'\"\\\$`;&|<>()#*?!\[\]{}~!]")
    return _NEED_QUOTE_RE


def quote(args: list[str]) -> str:
    """Quote arguments for shell (shell-quote compatible API).

    Args:
        args: List of string arguments to quote.

    Returns:
        A space-separated string of quoted arguments suitable for shell execution.
    """
    if not args:
        return ""

    result: list[str] = []
    for arg in args:
        if not arg:
            # Empty strings must be quoted
            result.append("''")
            continue

        # Check if quoting is needed
        if not _get_need_quote_re().search(arg):
            # No special characters - return as-is
            result.append(arg)
            continue

        # Use single quotes if no embedded single quotes
        if "'" not in arg:
            result.append("'" + arg + "'")
        else:
            # Has single quotes - use double quotes, escaping special chars
            # In double quotes: \", \\, \$, \` are recognized
            escaped = arg.replace("\\", "\\\\").replace('"', '\\"').replace(
                "$", "\\$"
            ).replace("`", "\\`")
            result.append('"' + escaped + '"')

    return " ".join(result)
