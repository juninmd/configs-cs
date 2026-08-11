# Contributing

Thanks for contributing to configs-cs! This document covers the CI/CD
workflow every change must go through.

## Getting Started

```bash
git clone https://github.com/juninmd/configs-cs
cd configs-cs
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Development Workflow

1. Create a feature branch from `develop`.
2. Make your changes.
3. Run every quality gate locally:

   ```bash
   ruff check .              # linting
   ruff format --check .     # formatting
   mypy configcheck          # type checking
   bandit -r configcheck -q  # security scan
   python -m configcheck .   # config syntax validation
   pytest --cov=configcheck --cov-fail-under=80   # tests + coverage
   ```

4. Open a pull request against `main`. CI runs the same gates automatically.

## Branch Strategy

| Branch   | Purpose                              |
| -------- | ------------------------------------ |
| `main`   | Production; deploy triggers on push  |
| `develop`| Integration; CI runs on every push   |
| feature  | Work-in-progress branches            |

## CI/CD Guidelines

- **No scheduled/cron triggers.** Every workflow must be event-driven
  (`push`, `pull_request`, `workflow_dispatch`).
- **Pinned dependencies.** Add new tools to `requirements-dev.txt` with an
  exact `==` version so CI is reproducible.
- **Coverage gate.** New logic must keep total coverage at or above 80%.
- **Config edits.** Run `python -m configcheck .` before committing any `.cfg`
  change. Malformed quotes or duplicate binds will fail CI.
- **Notifications.** Pipeline failures post to `SLACK_WEBHOOK` when the secret
  is configured; keep its value out of the repository.

## Environment Variables

| Variable        | Required | Description                              |
| --------------- | -------- | ---------------------------------------- |
| `SLACK_WEBHOOK` | No       | Slack URL for pipeline failure alerts    |
| `CODECOV_TOKEN` | No       | Codecov upload token (public repos)      |

Secrets are configured in the repository **Settings → Secrets and
variables → Actions** and referenced as `${{ secrets.* }}` in workflows.
Never commit secrets or real values (including test credentials) to the
repository.
