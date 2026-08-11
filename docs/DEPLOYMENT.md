# Deployment

The `deploy` job in `.github/workflows/ci.yml` publishes a versioned config
bundle whenever code lands on `main`. There is no remote service to update —
the "deployment" is the release artifact itself.

## Pipeline

| Stage    | Trigger              | Artifact                          |
| -------- | -------------------- | --------------------------------- |
| `build`  | Every push / PR      | `dist/configs-cs-<version>-<sha>.tar.gz` (workflow artifact) |
| `deploy` | Push to `main` only  | GitHub Release (prerelease) with the bundle + manifest |

Versions follow `1.0.<run_number>`, which increases monotonically across
workflow runs.

## Production Approval

The `deploy` job targets the `production` GitHub environment. To require
manual approval:

1. Go to **Settings → Environments → production**.
2. Add **required reviewers** to the protection rules.
3. Deployments will now pause for approval before publishing a release.

Without protection rules the deploy proceeds automatically.

## Rollback

Every release is an immutable snapshot. To roll back:

1. Open the **Releases** tab on GitHub.
2. Pick an earlier `ci-build-v*` prerelease.
3. Download its bundle and restore the `.cfg` files.

## Health Checks

After publishing, the deploy job verifies the bundle:

- The tarball exists and passes an integrity read (`tar -tzf`).
- Every expected config (`CSR.cfg`, `fallen.cfg`, `treino.cfg`, `user.cfg`)
  is present.

## Notifications

On any failure, the `notify` job posts to `SLACK_WEBHOOK` if that secret is
configured. Email alerts can be enabled in GitHub by adding the repository to
a team with **email notification** settings enabled.
