# configs-cs

[![CI/CD Pipeline](https://github.com/juninmd/configs-cs/actions/workflows/ci.yml/badge.svg)](https://github.com/juninmd/configs-cs/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/juninmd/configs-cs/branch/main/graph/badge.svg)](https://codecov.io/gh/juninmd/configs-cs)

Counter-Strike configuration files used by juninmd.

## Contents

- `CSR.cfg` — model training parameters
- `fallen.cfg` — fall detection algorithm configuration
- `treino.cfg` — training parameters (epochs, batch size, practice server setup)
- `user.cfg` — user-specific settings

## Validation Tooling

Every `.cfg` file is validated by `configcheck`, a small Python package that
parses Source engine syntax and reports unbalanced quotes, malformed command
names and duplicate key bindings.

```bash
python -m configcheck .   # validate every *.cfg in the repository
```

## Build

The CI pipeline packages a versioned, gzipped bundle of all configs:

```bash
mkdir -p dist
version="1.0.${GITHUB_RUN_NUMBER:-0}"
tar -czf "dist/configs-cs-${version}.tar.gz" *.cfg
printf 'version=%s\n' "$version" > dist/manifest.txt
```

## Tests

Requires Python 3.10+.

```bash
pip install -r requirements-dev.txt
pytest --cov=configcheck --cov-fail-under=80
```

The suite covers parser units, validator rules, the CLI and an integration
check that every config shipped in this repository is valid. Coverage must
stay above 80%.

## CI/CD Pipeline

`.github/workflows/ci.yml` runs four stages on every push to `main`/`develop`
and on pull requests targeting `main`:

1. **lint** — `ruff`, `ruff format`, `mypy`, `bandit` and config validation
2. **test** — `pytest` with coverage, `pip-audit`, reports uploaded to Codecov
3. **build** — versioned config bundle uploaded as a workflow artifact
4. **deploy** — publish a prerelease bundle to GitHub Releases (main only)

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) and
[CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Environment Variables

| Variable        | Required | Description                                |
| --------------- | -------- | ------------------------------------------ |
| `SLACK_WEBHOOK` | No       | Receives pipeline failure notifications    |
| `CODECOV_TOKEN` | No       | Uploads coverage to Codecov (public repos) |

`GITHUB_TOKEN` is provided automatically by GitHub Actions.
