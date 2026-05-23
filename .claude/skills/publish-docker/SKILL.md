---
name: publish-docker
description: Thin wrapper around the project's GitHub Actions workflow (`.github/workflows/docker-publish.yml`) that builds and publishes the `albertogarob/whistlerlib` Docker image. The skill itself never builds or pushes images, it only triggers the workflow, monitors the run, and verifies the result on Docker Hub. Use this when releasing a new version, republishing an existing tag, building a manual dev image, or inspecting what's already on Docker Hub.
argument-hint: "[release|rerun|dev|verify] [version]"
allowed-tools: Bash Read Edit
---

# publish-docker

**This skill does not build Docker images.** Every `docker buildx` + `docker push` operation happens inside GitHub Actions on the project's CI runners (multi-arch `linux/amd64` + `linux/arm64` via QEMU). The skill is a thin orchestrator: it triggers the workflow, watches the run, and reads the result back from Docker Hub.

The single source of truth for image creation is [`.github/workflows/docker-publish.yml`](../../../.github/workflows/docker-publish.yml). If a build setting needs to change (platforms, tags, cache strategy, base image, …), edit that workflow, not this skill.

## Image

- **Docker Hub**: `albertogarob/whistlerlib:<tag>`
- **GitHub repo**: `observatoriogeo/whistlerlib` (the GitHub owner is a user account, separate from the Docker Hub namespace which is the maintainer's personal `albertogarob`)
- **Tagging policy** (defined in `docker-publish.yml`, do not duplicate or override here):
  - `vX.Y.Z` git tag pushed → workflow tags the image `X.Y.Z`, `X.Y`, and `latest`
  - `workflow_dispatch` with `push=true` → workflow tags the image `dev-<7char-sha>`
  - `workflow_dispatch` with `push=false` → workflow builds only, no push

## How the workflow gets triggered

Every mode below ultimately fires `docker-publish.yml` through one of two GH-Actions-native trigger paths:

| Trigger path | How the skill invokes it | GHA event |
|---|---|---|
| Tag push (`v*`) | `gh release create vX.Y.Z` (creates the tag remotely, GHA picks up the push) | `push` event with `refs/tags/v*` |
| Manual dispatch | `gh workflow run docker-publish.yml --field push=<bool>` | `workflow_dispatch` event |
| Rerun previous run | `gh run rerun <id>` | re-runs the same event that triggered the original |

Nothing in this skill touches Docker locally for state-changing work. The optional smoke-test at the end of `verify` is a *read-only* `docker pull` from a user's perspective, not part of publication.

## Modes

Pick by argument (see "Dispatching" below). If you can't tell from `$ARGUMENTS` which mode the user meant, ASK them; never guess for a state-changing action like `release`.

### `release <version>`: cut a new versioned release

Tag the current `main` HEAD as `vX.Y.Z` *via `gh release create`* (which creates the tag on GitHub, fires the workflow, and creates the GitHub release in one step).

**Steps**:

1. Run preflight checks (see "Preflight" below). Abort with a clear error if any fail.
2. Validate `<version>`: must match `^[0-9]+\.[0-9]+\.[0-9]+$` (semver, no `v` prefix in the argument; the script adds it). Example accepted: `0.3.0`. Rejected: `v0.3.0`, `0.3`, `0.3.0-beta`.
3. Confirm `main` is checked out and up to date with `origin/main`. Refuse to release from a detached HEAD or a branch ahead of origin without a `git push origin main` first.
4. Refuse to overwrite an existing tag/release without explicit confirmation. If `gh release view "v$VERSION"` succeeds, ask the user whether to delete the existing release + tag first.
5. Refuse to release while CHANGELOG `[Unreleased]` has content; if it exists, ask the user to finalize it (rename to `[$VERSION] - $(date +%Y-%m-%d)`) before proceeding.
6. Create the GitHub release (which creates and pushes the tag, triggering the workflow):
   ```bash
   gh release create "v$VERSION" \
       --target main \
       --title "v$VERSION" \
       --generate-notes
   ```
7. The tag push fires `docker-publish.yml`. Find the new run id with `gh run list --workflow=docker-publish.yml --limit 1 --json databaseId,status` and store it.
8. Monitor the run (see "Monitoring" below). On success, run the "Verify" steps and report. On failure, surface the failed step's log and stop without retrying.

### `rerun`: re-run the most recent docker-publish workflow

For when the workflow failed transiently (network, Docker Hub rate-limit, etc.) and you want GHA to retry without making any source changes.

**Steps**:

1. Run preflight checks.
2. `gh run list --workflow=docker-publish.yml --limit 1 --json databaseId,status,conclusion,headBranch` to find the most recent run.
3. If `conclusion == "success"`, ask the user whether they really want to re-run (it'll just publish the same image again, which is harmless but wasteful). If they confirm, proceed; otherwise stop.
4. `gh run rerun <id>` to re-run the GHA workflow.
5. Monitor + verify + report.

### `dev`: publish a dev image from the current HEAD via manual dispatch

For testing image changes outside of a tagged release. Fires `workflow_dispatch` on `docker-publish.yml` with `push=true`.

**Steps**:

1. Run preflight checks.
2. Confirm with the user before pushing a dev tag (Docker Hub will accumulate `dev-<sha>` tags; cleanup is manual).
3. Trigger the workflow:
   ```bash
   gh workflow run docker-publish.yml --ref main --field push=true
   ```
4. Wait ~5 s and find the new run id; monitor + verify (the verify check needs the short SHA, which the workflow computes as `${GITHUB_SHA:0:7}` of `main`'s tip).

### `verify`: just check what's currently on Docker Hub

No publish. Useful to confirm what users would `docker pull`. Does not invoke any workflow.

**Steps**:

1. `curl -s "https://hub.docker.com/v2/repositories/albertogarob/whistlerlib/tags/?page_size=20"` and pretty-print the result.
2. Report the available tags, their last-pushed dates, and the manifest digest for `:latest`.
3. If the user passed a specific version (`/publish-docker verify 0.2.0`), also report whether that exact tag exists.

## Preflight (every state-changing mode)

Before any state-changing action (`release`, `rerun`, `dev`), verify:

1. **gh CLI is authenticated**: `gh auth status` returns non-error.
2. **gh active account has push access** to `observatoriogeo/whistlerlib`. Check with `gh api repos/observatoriogeo/whistlerlib --jq '.permissions.push'` (must be `true`).
3. **Docker Hub secrets exist** on the repo: both `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` must be listed by `gh secret list --repo observatoriogeo/whistlerlib`. If missing, STOP and tell the user to set them (see "Secret setup" below). These are the credentials the GHA workflow uses for `docker/login-action`; the skill itself never reads them.
4. **Working tree is clean** (`git status --porcelain` empty). If not, stop and ask whether they want to stash, commit, or abort.

If any check fails, give the user the exact command to fix it; don't auto-apply destructive corrections.

## Monitoring (release / rerun / dev modes)

After triggering, watch the GHA run with:

```bash
RUN_ID=<id>
gh run watch "$RUN_ID" --exit-status
```

`gh run watch` blocks until completion and exits non-zero on failure. For long runs (multi-arch buildx of the ~2.5 GB image takes 12 to 60 min on the free GH Actions runners with QEMU), prefer launching it in the background and polling state every 60 s via the Monitor tool.

On completion:
- Success → "Verify" section below.
- Failure → `gh run view "$RUN_ID" --log-failed | tail -200` to surface the failed step, then stop. Don't auto-rerun on failure: the user should look at the log first.

## Verify (after a successful GHA run)

Verification reads from Docker Hub directly; the GHA workflow has already done the publish by this point.

1. Confirm the manifest exists on Docker Hub via the v2 API:
   ```bash
   curl -s "https://hub.docker.com/v2/repositories/albertogarob/whistlerlib/tags/<tag>/" | python3 -m json.tool
   ```
   For a release publish, check `<tag>` = the version (e.g. `0.2.0`), `<major>.<minor>`, and `latest`.
2. Pull the manifest list and confirm it has both `linux/amd64` and `linux/arm64`:
   ```bash
   docker manifest inspect "albertogarob/whistlerlib:<tag>" | jq '.manifests[].platform'
   ```
   (You may need `docker manifest` enabled via `~/.docker/config.json`.)
3. As a final local smoke test (read-only, asks the user first, skipped if the pull would take more than ~2 min on their connection):
   ```bash
   docker pull albertogarob/whistlerlib:<tag>
   docker run --rm albertogarob/whistlerlib:<tag> python /app/smoke.py --self-test
   ```
   This is a user-perspective sanity check, not part of publication. The publication itself is whatever the GHA workflow did.

Report back: the published tags, the multi-arch confirmation, and the Docker Hub URL `https://hub.docker.com/r/albertogarob/whistlerlib/tags`.

## Secret setup (only if preflight detects missing secrets)

These secrets are read by the GHA workflow's `docker/login-action` step. The skill never sees them. Tell the user (don't run; they need to do it themselves):

```bash
# Generate a token at https://app.docker.com/settings/personal-access-tokens
# Permissions: Read & Write.  Description: "whistlerlib CI"

echo -n "albertogarob" | gh secret set DOCKERHUB_USERNAME --repo observatoriogeo/whistlerlib
gh secret set DOCKERHUB_TOKEN --repo observatoriogeo/whistlerlib
# Paste the token when prompted, press Enter.
```

`DOCKERHUB_USERNAME` is the **maintainer's personal Docker Hub login** (`albertogarob`), not the GitHub owner. The token authenticates that user, who has push access to `albertogarob/whistlerlib` because it's their own namespace.

## Failure-mode cheatsheet

All symptoms below are failures *of the GHA workflow*, not of this skill. Fixes target the workflow's environment (secrets, runner, workflow file), not local Docker.

| Symptom | Likely cause | Fix |
|---|---|---|
| `gh run rerun` reports "no permission" | gh CLI not authed as a user with write access to `observatoriogeo/whistlerlib` | `gh auth switch -u <user-with-write>` |
| Workflow's "Log in to Docker Hub" step fails with `unauthorized` | `DOCKERHUB_TOKEN` invalid / expired / wrong permissions | Regenerate the token at hub.docker.com, then re-`gh secret set` it |
| Workflow's push step fails with `requested access to the resource is denied` | `DOCKERHUB_USERNAME` doesn't have push rights on `albertogarob/whistlerlib` | Verify the username matches the Docker Hub namespace owner |
| Workflow's buildx step OOMs or stalls on arm64 | GHA free runner ran out of memory on the QEMU-emulated arm64 build | `gh run rerun`; if it recurs, edit `docker-publish.yml` to drop arm64 from `platforms:` temporarily, or split into per-arch jobs on native arm64 runners (`ubuntu-24.04-arm`) |
| Manifest exists but `docker pull :latest` returns an old digest on user machines | Local layer cache on the user's host | Tell user to `docker pull` again (Docker Hub returns the current manifest); or refer them to the version-pinned tag |

## Dispatching

```bash
case "$1" in
  release)  shift; release_flow "$@" ;;
  rerun)    rerun_flow ;;
  dev)      dev_flow ;;
  verify)   shift; verify_flow "$@" ;;
  "")       # no args: ask the user what they want, don't guess
            echo "Modes: release <version> | rerun | dev | verify [tag]"
            ;;
  *)        echo "Unknown mode: $1. Modes: release | rerun | dev | verify" ;;
esac
```

When invoked with no arguments, ask the user which mode (release / rerun / dev / verify) before doing anything.
