"""Tests for the configcheck command line interface."""

from pathlib import Path

from configcheck.cli import EXIT_ERRORS, EXIT_OK, build_parser, discover_configs, main

FIXTURES = Path(__file__).parent / "fixtures"


class TestDiscoverConfigs:
    def test_finds_all_cfg_files(self, tmp_path):
        (tmp_path / "a.cfg").write_text("", encoding="utf-8")
        (tmp_path / "b.cfg").write_text("", encoding="utf-8")
        found = discover_configs(tmp_path)
        assert [p.name for p in found] == ["a.cfg", "b.cfg"]

    def test_returns_empty_list_for_empty_dir(self, tmp_path):
        assert discover_configs(tmp_path) == []

    def test_fixtures_directory_is_scanned(self):
        names = {p.name for p in discover_configs(FIXTURES)}
        assert {"valid.cfg", "invalid.cfg"} <= names


class TestBuildParser:
    def test_root_defaults_to_current_directory(self):
        args = build_parser().parse_args([])
        assert args.root == Path(".")

    def test_root_can_be_configured(self):
        args = build_parser().parse_args(["some/dir"])
        assert args.root == Path("some/dir")


class TestMain:
    def test_valid_directory_exits_ok(self, tmp_path):
        (tmp_path / "clean.cfg").write_text('bind "MOUSE1" "+attack"\n', encoding="utf-8")
        assert main([str(tmp_path)]) == EXIT_OK

    def test_directory_with_errors_exits_failure(self):
        assert main([str(FIXTURES)]) == EXIT_ERRORS

    def test_no_arguments_uses_current_directory(self, monkeypatch, tmp_path):
        monkeypatch.chdir(tmp_path)
        assert main([]) == EXIT_OK
