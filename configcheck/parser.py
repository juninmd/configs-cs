"""Low-level parsing utilities for Source engine config files.

Source engine (CS:GO / CS2) config files are line oriented.  Each line is
either a comment, a blank line, or a ``command`` / ``command value`` pair in
which values may be wrapped in double quotes.  This module provides the
building blocks used by the validator.
"""

from __future__ import annotations


class UnbalancedQuotesError(ValueError):
    """Raised when a line has an unclosed or dangling double quote."""

    def __init__(self, line: str) -> None:
        super().__init__(f"unbalanced double quotes in line: {line!r}")


def is_blank(line: str) -> bool:
    """Return True when a line is empty or only contains whitespace."""
    return not line.strip()


def strip_comment(line: str) -> str:
    """Remove a trailing ``//`` comment while keeping quotes inside values.

    A ``//`` appearing inside a double-quoted value is preserved, because
    commands such as ``say "http://example.com"`` are legal in configs.
    """
    in_quotes = False
    for index, char in enumerate(line):
        if char == '"':
            in_quotes = not in_quotes
        if char == "/" and not in_quotes and line[index + 1 : index + 2] == "/":
            return line[:index]
    return line


def tokenize(line: str) -> list[str]:
    """Split a line into whitespace-separated tokens honouring double quotes.

    Raises:
        UnbalancedQuotesError: when a quote never closes or a value is
            followed by an extra dangling quote.
    """
    tokens: list[str] = []
    current: list[str] = []
    in_quotes = False
    for char in line:
        if in_quotes:
            if char == '"':
                in_quotes = False
                tokens.append("".join(current))
                current = []
            else:
                current.append(char)
        elif char == '"':
            if current:
                tokens.append("".join(current))
                current = []
            in_quotes = True
        elif char.isspace():
            if current:
                tokens.append("".join(current))
                current = []
        else:
            current.append(char)
    if in_quotes:
        raise UnbalancedQuotesError(line)
    if current:
        tokens.append("".join(current))
    return tokens


def parse_bind(tokens: list[str]) -> tuple[str, str] | None:
    """Return ``(key, command)`` for a ``bind`` line, else None.

    A bare ``bind <key>`` without a command is valid Source syntax, so the
    command defaults to an empty string.
    """
    if len(tokens) < 2 or tokens[0] != "bind":
        return None
    return tokens[1], " ".join(tokens[2:])
