"""Secret detection for the configs-cs repository.

Scans plain-text configuration files for accidentally committed
credentials (passwords, API keys, tokens, private keys). Used both by
the local CLI and by CI. Intended to complement, not replace, git-based
secret scanning tools such as gitleaks.
"""

import argparse
import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path

# High-confidence, format-specific patterns. These are flagged even when
# they appear inside comments, because they are unambiguous secret blobs.
HIGH_CONFIDENCE_PATTERNS = [
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key ID"),
    (
        re.compile(
            r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*[\"']?[A-Za-z0-9/+=]{40}"
        ),
        "AWS secret access key",
    ),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{36,}\b"), "GitHub token"),
    (
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY"),
        "Private key",
    ),
]

# Generic credential assignments such as `password "foo"`, `api_key = "bar"`
# or `sv_password x`. Full-line comments are skipped to avoid flagging
# documentation placeholders. A non-empty value followed by extra content
# on the same line (e.g. `password "x"; DROP TABLE users`) is flagged as a
# potential injection attempt.
GENERIC_SECRET_LINE = re.compile(
    r"^\s*(?P<name>password|passwd|pwd|sv_password|secret|api[_-]?key|"
    r"access[_-]?token|auth[_-]?token)\s*[:=]?\s*(?P<value>\"[^\"]+\"|\S+)"
    r"(?P<trailing>.*)$",
    re.IGNORECASE,
)
COMMENT_LINE = re.compile(r"^\s*(//|#|;)\s*")

DEFAULT_EXTENSIONS = {
    ".cfg",
    ".conf",
    ".env",
    ".ini",
    ".json",
    ".properties",
    ".toml",
    ".yaml",
    ".yml",
}


@dataclass
class SecretFinding:
    """A single potential secret located in a scanned file."""

    source: str
    line: int
    rule: str
    snippet: str

    def __str__(self):
        return f"{self.source}:{self.line}: [{self.rule}] {self.snippet}"


def scan_text(text, source="<memory>"):
    """Return a list of SecretFinding objects for a text buffer."""
    findings = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip("\n")
        for pattern, label in HIGH_CONFIDENCE_PATTERNS:
            for match in pattern.finditer(line):
                findings.append(SecretFinding(source, lineno, label, match.group(0)))
        if COMMENT_LINE.match(line):
            continue
        match = GENERIC_SECRET_LINE.match(line)
        if match and match.group("value") not in ('""', "'"):
            rule = (
                "Suspicious credential assignment"
                if match.group("trailing").strip()
                else "Credential assignment"
            )
            findings.append(
                SecretFinding(source, lineno, rule, line.strip())
            )
    return findings


def scan_path(path, extensions=DEFAULT_EXTENSIONS):
    """Scan a file or directory tree (recursively) for secrets."""
    path = Path(path)
    findings = []
    if path.is_file():
        return scan_text(path.read_text(encoding="utf-8", errors="replace"), str(path))
    if not path.is_dir():
        return findings
    for file in sorted(path.rglob("*")):
        if not file.is_file() or ".git" in file.parts:
            continue
        if file.suffix.lower() in extensions:
            findings.extend(
                scan_text(file.read_text(encoding="utf-8", errors="replace"), str(file))
            )
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description="Scan files for leaked secrets.")
    parser.add_argument("paths", nargs="+", help="Files or directories to scan")
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        help="Glob patterns (e.g. '*tests*') to exclude from the scan",
    )
    args = parser.parse_args(argv)

    findings = []
    for raw in args.paths:
        for finding in scan_path(raw):
            if not any(fnmatch.fnmatch(finding.source, pat) for pat in args.exclude):
                findings.append(finding)

    for finding in findings:
        print(finding)
    if findings:
        print(f"FAIL: {len(findings)} potential secret(s) found.")
        return 1
    print("OK: no secrets found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
