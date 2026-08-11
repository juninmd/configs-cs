"""Tests for the repository secret scanner (security/secret_scanner.py).

Covers benign inputs, credential payloads, tokens, private keys and the
end-to-end repo scan to prove the guard rails work.
"""

from pathlib import Path

import pytest

from security.secret_scanner import SecretFinding, scan_path, scan_text

REPO_ROOT = Path(__file__).resolve().parents[1]

BENIGN_CFG = """\
unbindall
bind "1" "slot1"
name "CSR7*"
sensitivity "2.5"
volume "0.05"
rate "786432"
"""


def test_benign_config_has_no_findings():
    assert scan_text(BENIGN_CFG) == []


def test_ci_secret_reference_is_not_a_finding():
    line = '        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}'
    assert scan_text(line) == []


def test_plain_password_is_flagged():
    findings = scan_text('password "GC8923"\n')
    assert len(findings) == 1
    assert findings[0].rule == "Credential assignment"
    assert findings[0].line == 1


def test_server_password_cvar_is_flagged():
    assert scan_text('sv_password "sup3r-s3cret"\n')


def test_empty_password_is_allowed():
    assert scan_text('password ""\n') == []


def test_commented_out_secret_is_not_flagged_as_assignment():
    assert scan_text('//password "GC8923"\n') == []


def test_api_key_assignment_is_flagged():
    findings = scan_text('api_key = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\n')
    assert len(findings) == 1
    assert findings[0].rule == "Credential assignment"


def test_aws_access_key_is_flagged():
    findings = scan_text('key "AKIAIOSFODNN7EXAMPLE"\n')
    assert len(findings) == 1
    assert findings[0].rule == "AWS access key ID"


def test_aws_secret_key_is_flagged():
    line = 'aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
    findings = scan_text(line + "\n")
    assert findings and any(f.rule == "AWS secret access key" for f in findings)


def test_github_token_is_flagged():
    findings = scan_text("ghp_0123456789abcdefghijklmnopqrstuvwxyzABCDEFG\n")
    assert len(findings) == 1
    assert findings[0].rule == "GitHub token"


def test_private_key_block_is_flagged():
    block = (
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEpAIBAAKCAQEA7eFcPHnYgWsqMu\n"
        "-----END RSA PRIVATE KEY-----\n"
    )
    findings = scan_text(block)
    assert len(findings) == 1
    assert findings[0].rule == "Private key"


def test_line_numbers_and_source_are_reported():
    text = "name 'x'\npassword 'hunter2'\n"
    findings = scan_text(text, source="user.cfg")
    assert findings == [SecretFinding("user.cfg", 2, "Credential assignment", "password 'hunter2'")]


def test_injection_style_values_are_still_flagged():
    payloads = [
        'password "GC8923; exec exploit"\n',
        'password "x"; DROP TABLE users; --\n',
        'password "x" && whoami\n',
    ]
    for payload in payloads:
        assert scan_text(payload), f"expected finding for {payload!r}"


def test_scan_path_finds_secret_in_file(tmp_path):
    target = tmp_path / "secrets.cfg"
    target.write_text('password "hunter2"\n', encoding="utf-8")
    findings = scan_path(target)
    assert len(findings) == 1
    assert findings[0].source == str(target)


def test_scan_path_skips_binary_and_non_target_files(tmp_path):
    (tmp_path / "notes.txt").write_text('password "hunter2"\n', encoding="utf-8")
    assert scan_path(tmp_path) == []


def test_repo_scan_is_clean():
    """Regression guard: the whole repository must not contain secrets."""
    findings = scan_path(REPO_ROOT)
    assert findings == []


def test_cli_exits_nonzero_when_secrets_found(tmp_path):
    from security.secret_scanner import main

    target = tmp_path / "leak.cfg"
    target.write_text('password "hunter2"\n', encoding="utf-8")
    assert main([str(target)]) == 1


def test_cli_exits_zero_on_clean_input():
    from security.secret_scanner import main

    assert main([str(REPO_ROOT)]) == 0


@pytest.mark.parametrize(
    "name",
    ["password", "passwd", "pwd", "sv_password", "secret", "api_key", "auth_token"],
)
def test_all_generic_credential_names_are_flagged(name):
    assert scan_text(f'{name} "somevalue"\n'), f"expected finding for {name}"
