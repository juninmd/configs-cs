"""Command line interface for validating Source engine config files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from configcheck.validator import validate_file

EXIT_OK = 0
EXIT_ERRORS = 1


def discover_configs(root: Path) -> list[Path]:
    """Return every ``*.cfg`` file below root, sorted for stable output."""
    return sorted(root.glob("*.cfg"))


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse CLI parser."""
    parser = argparse.ArgumentParser(
        prog="configcheck",
        description="Validate Source engine .cfg files.",
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        type=Path,
        help="directory to scan for .cfg files (default: current directory)",
    )
    return parser


def run(root: Path) -> int:
    """Validate all configs under root and print any issues found."""
    configs = discover_configs(root)
    failures = 0
    for path in configs:
        result = validate_file(path)
        for issue in result.issues:
            print(f"{issue.path}:{issue.line}: {issue.kind}: {issue.message}")
        failures += result.error_count
    if failures:
        print(f"configcheck: {failures} issue(s) found across {len(configs)} file(s)")
        return EXIT_ERRORS
    print(f"configcheck: {len(configs)} file(s) OK")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    """Entry point used by both ``configcheck`` and ``python -m configcheck``."""
    args = build_parser().parse_args(argv)
    return run(args.root)


if __name__ == "__main__":
    sys.exit(main())
