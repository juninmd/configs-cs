"""Unit tests for the config file validator."""

from pathlib import Path

import pytest

from configcheck.validator import validate_file

FIXTURES = Path(__file__).parent / "fixtures"


def kinds(result) -> set[str]:
    return {issue.kind for issue in result.issues}


class TestValidateFile:
    def test_valid_fixture_passes(self):
        result = validate_file(FIXTURES / "valid.cfg")
        assert result.ok
        assert result.error_count == 0

    def test_invalid_fixture_reports_all_issue_kinds(self):
        result = validate_file(FIXTURES / "invalid.cfg")
        assert not result.ok
        assert kinds(result) == {"quotes", "duplicate_bind", "command"}

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            validate_file(FIXTURES / "does-not-exist.cfg")


class TestIssueReporting:
    def test_quotes_issue_has_line_and_kind(self):
        result = validate_file(FIXTURES / "invalid.cfg")
        quote_issues = [i for i in result.issues if i.kind == "quotes"]
        assert len(quote_issues) == 2
        assert all(issue.line > 0 for issue in quote_issues)

    def test_duplicate_bind_points_at_second_occurrence(self):
        result = validate_file(FIXTURES / "invalid.cfg")
        dup_issues = [i for i in result.issues if i.kind == "duplicate_bind"]
        assert len(dup_issues) == 1
        assert "already bound" in dup_issues[0].message

    def test_each_issue_carries_a_path(self):
        result = validate_file(FIXTURES / "invalid.cfg")
        assert all(issue.path.endswith("invalid.cfg") for issue in result.issues)
