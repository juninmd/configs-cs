"""Unit tests for the config parsing primitives."""

import pytest

from configcheck.parser import (
    UnbalancedQuotesError,
    is_blank,
    parse_bind,
    strip_comment,
    tokenize,
)


class TestIsBlank:
    def test_empty_line(self):
        assert is_blank("")

    def test_whitespace_only_line(self):
        assert is_blank(" \t ")

    def test_content_line_is_not_blank(self):
        assert not is_blank("unbindall")


class TestStripComment:
    def test_removes_trailing_comment(self):
        assert strip_comment('cl_crosshaircolor "1" // color') == 'cl_crosshaircolor "1" '

    def test_removes_full_line_comment(self):
        assert strip_comment("  // only a comment").strip() == ""

    def test_keeps_url_inside_quotes(self):
        assert strip_comment('say "http://example.com/path"') == 'say "http://example.com/path"'


class TestTokenize:
    def test_simple_tokens(self):
        assert tokenize("unbindall") == ["unbindall"]

    def test_quoted_value(self):
        assert tokenize('bind "MOUSE1" "+attack"') == ["bind", "MOUSE1", "+attack"]

    def test_empty_quoted_value(self):
        assert tokenize('con_enable ""') == ["con_enable", ""]

    def test_unquoted_value(self):
        assert tokenize("sensitivity 2.5") == ["sensitivity", "2.5"]

    def test_value_with_semicolon(self):
        assert tokenize('bind "w" "+forward; +jump"') == ["bind", "w", "+forward; +jump"]

    def test_panorama_command_prefix(self):
        assert tokenize('@panorama_debug_overlay_opacity "0.8"') == [
            "@panorama_debug_overlay_opacity",
            "0.8",
        ]

    def test_leading_quoted_token_merges_with_surrounding_text(self):
        assert tokenize('pre"mid"post') == ["pre", "mid", "post"]

    def test_smart_quote_raises(self):
        with pytest.raises(UnbalancedQuotesError):
            tokenize('bind "9" "slot9\u201d')

    def test_dangling_quote_raises(self):
        with pytest.raises(UnbalancedQuotesError):
            tokenize('cl_teammate_colors_show 1"')

    def test_unclosed_quote_raises(self):
        with pytest.raises(UnbalancedQuotesError):
            tokenize('say "hello')


class TestParseBind:
    def test_full_bind(self):
        assert parse_bind(["bind", "MOUSE1", "+attack"]) == ("MOUSE1", "+attack")

    def test_bind_with_multi_word_command(self):
        assert parse_bind(["bind", "f", "+lookatweapon; r_cleardecals"]) == (
            "f",
            "+lookatweapon; r_cleardecals",
        )

    def test_bare_bind_has_empty_command(self):
        assert parse_bind(["bind", "KP_RIGHTARROW"]) == ("KP_RIGHTARROW", "")

    def test_non_bind_line_returns_none(self):
        assert parse_bind(["unbindall"]) is None
