"""Rules for validating Source engine config files.

The validator applies a small set of deterministic checks and returns a
structured result that the CLI and the test suite can consume.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from configcheck.parser import (
    UnbalancedQuotesError,
    is_blank,
    parse_bind,
    strip_comment,
    tokenize,
)

COMMAND_NAME_RE = re.compile(r"^[A-Za-z0-9_@+./\-]+$")


@dataclass(frozen=True)
class Issue:
    """A single validation finding for one config line."""

    path: str
    line: int
    kind: str
    message: str


@dataclass
class ValidationResult:
    """The outcome of validating a single config file."""

    issues: list[Issue] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        """Return the total number of recorded issues."""
        return len(self.issues)

    @property
    def ok(self) -> bool:
        """Return True when the file raised no issues."""
        return not self.issues


def _quote_issue(path: str, line_no: int, raw: str) -> list[Issue]:
    try:
        tokenize(raw)
    except UnbalancedQuotesError as exc:
        return [Issue(path, line_no, "quotes", str(exc))]
    return []


def _command_issue(path: str, line_no: int, raw: str) -> list[Issue]:
    stripped = strip_comment(raw).strip()
    if is_blank(stripped):
        return []
    try:
        tokens = tokenize(stripped)
    except UnbalancedQuotesError:
        return []
    if not tokens:
        return []
    if not COMMAND_NAME_RE.match(tokens[0]):
        return [
            Issue(
                path,
                line_no,
                "command",
                f"invalid command name: {tokens[0]!r}",
            )
        ]
    return []


def _bind_issue(
    path: str,
    line_no: int,
    raw: str,
    seen_binds: dict[str, int],
) -> list[Issue]:
    stripped = strip_comment(raw).strip()
    if is_blank(stripped):
        return []
    try:
        tokens = tokenize(stripped)
    except UnbalancedQuotesError:
        return []
    bound = parse_bind(tokens)
    if bound is None:
        return []
    key, _command = bound
    if key in seen_binds:
        return [
            Issue(
                path,
                line_no,
                "duplicate_bind",
                f"key {key!r} already bound on line {seen_binds[key]}",
            )
        ]
    seen_binds[key] = line_no
    return []


def validate_file(path: Path) -> ValidationResult:
    """Validate every line of a config file, collecting all issues found."""
    result = ValidationResult()
    seen_binds: dict[str, int] = {}
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        result.issues.extend(_quote_issue(str(path), line_no, raw))
        result.issues.extend(_command_issue(str(path), line_no, raw))
        result.issues.extend(_bind_issue(str(path), line_no, raw, seen_binds))
    return result
