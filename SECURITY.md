# Security Policy

## Supported versions

Only the default branch (`main`/`master`) receives security fixes.

## Reporting a vulnerability

Do **not** open a public issue for a security problem. Instead, contact
the repository maintainer privately (GitHub security advisories or a
direct message) and include a description plus a minimal reproduction.

## Threat model

This is a configuration-only repository (Counter-Strike game configs and
CI definitions). There is no runtime application code, so the classic web
OWASP concerns (injection, SSRF, rate limiting, CORS, session handling)
do not apply here. The relevant risks are:

1. **Cryptographic Failures** — credentials committed in plain text.
2. **Security Misconfiguration** — overly permissive CI permissions or
   workflows that run on untrusted inputs.
3. **Vulnerable and Outdated Components** — stale CI actions and tools.
4. **Software and Data Integrity Failures** — third-party actions not
   pinned, or CI that can be tampered with.

## Secrets management

- Never commit passwords, tokens or keys. Game server passwords
  (`password`, `sv_password`) must be set **locally** only.
  `CSR.cfg` ships a commented placeholder instead of a real password.
- `*.key`, `*.pem`, `*.p12`, `.env*`, `secrets/` and `config/secrets.yml`
  are ignored via `.gitignore`.
- If a secret was ever committed, rotate it immediately and purge it from
  git history (e.g. `git filter-repo`), then notify affected users.

## CI/CD security

- Workflows use least-privilege `permissions: contents: read` by default;
  write permissions are scoped to the specific job that needs them.
- `security.yml` runs gitleaks on every push via the shared reusable
  action, and `.github/workflows/audit.yml` runs a local Python secret
  scanner plus its unit tests on every push and pull request.
- No workflow uses a scheduled (cron) trigger; all automation is
  event-driven (`push` / `pull_request` / `workflow_dispatch`).
- Secrets are only ever referenced as `${{ secrets.* }}`; they are never
  written into workflow files or configuration.

## Dependency management

- Dependabot is configured (`.github/dependabot.yml`) for `npm`, `pip`,
  `github-actions` and `docker` ecosystems. PRs bump dependencies
  automatically; review them like any other change.

## Development checklist

Before opening a pull request:

- Run `python -m security.secret_scanner .` (must print `OK`).
- Run `pytest` (all tests must pass).
- Do not introduce new secrets; add a regression test in
  `tests/test_secret_scanner.py` if you add new credential patterns.
