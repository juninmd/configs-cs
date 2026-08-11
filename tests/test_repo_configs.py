"""Integration tests running the validator against the real repository configs.

These tests give us end-to-end confidence that every ``.cfg`` shipped in the
repository parses cleanly, mirroring what the CI ``lint`` job executes.
"""

from pathlib import Path

from configcheck.cli import discover_configs
from configcheck.validator import validate_file

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_all_repo_configs_are_valid():
    configs = discover_configs(REPO_ROOT)
    assert configs, "expected at least one .cfg file at the repository root"
    for path in configs:
        result = validate_file(path)
        details = "; ".join(f"line {i.line} {i.kind}: {i.message}" for i in result.issues)
        assert result.ok, (
            f"{path.name} failed validation with {result.error_count} issue(s): {details}"
        )


def test_expected_configs_exist():
    names = {path.name for path in discover_configs(REPO_ROOT)}
    assert {"CSR.cfg", "fallen.cfg", "treino.cfg", "user.cfg"} <= names
