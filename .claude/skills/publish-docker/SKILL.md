---
name: publish-docker
description: Publish or update the `albertogarob/whistlerlib` Docker image on Docker Hub via the project's CI workflow. Use this when releasing a new version, republishing an existing tag, building a manual dev image, or just inspecting what's already on Docker Hub.
argument-hint: "[release|rerun|dev|verify] [version]"
allowed-tools: Bash Read Edit
---

# publish-docker

End-to-end skill for the Docker Hub side of a Whistlerlib release. Delegates the actual buildx + push to the existing CI pipeline at [`.github/workflows/docker-publish.yml`](../../../.github/workflows/docker-publish.yml); this skill orchestrates the pipeline (auth checks, trigger, monitor, verify) without duplicating it.

## Image

- **Docker Hub**: `albertogarob/whistlerlib:<tag>`
- **GitHub repo**: `github.com/observatoriogeo/whistlerlib` (separate namespace; the Docker Hub account is the maintainer's personal one)
- **Tagging policy** (set in `docker-publish.yml`, do not change ad-hoc):
  - `vX.Y.Z` git tag pushed → image tagged `X.Y.Z`, `X.Y`, and `latest`
  - `workflow_dispatch` with `push=true` → image tagged `dev-<7char-sha>`
  - `workflow_dispatch` with `push=false` → build-only, no Docker Hub push

## Modes

Pick by argument (see "Dispatching" below). If you can't tell from `$ARGUMENTS` which mode the user meant, ASK them; never guess for a destructive action like "release."

### `release <version>`: cut a new versioned release

Tag the current `main` HEAD as `vX.Y.Z`, push the tag, let CI auto-publish.

**Steps**:

1. Run preflight checks (see "Preflight" below). Abort with a clear error if any fail.
2. Validate `<version>`: must match `^[0-9]+\.[0-9]+\.[0-9]+$` (semver, no `v` prefix in the argument; the script adds it). Example accepted: `0.3.0`. Rejected: `v0.3.0`, `0.3`, `0.3.0-beta`.
3. Confirm `main` is checked out and up to date with `origin/main`. Refuse to tag a detached HEAD or a branch ahead of origin without a `git push origin main` first.
4. Refuse to overwrite an existing tag without explicit confirmation. If `git tag -l v$VERSION` returns the tag, ask the user whether to delete the existing tag (locally + remote) and the matching GH release first.
5. Refuse to tag a non-empty CHANGELOG `[Unreleased]` section silently; if it exists with content, ask the user to finalize it (rename to `[$VERSION] - $(date +%Y-%m-%d)`) before proceeding.
6. Create the annotated tag, then push it:
   ```bash
   git tag -a "v$VERSION" main -m "v$VERSION release"
   git push origin "v$VERSION"
   ```
7. The tag push triggers `.github/workflows/docker-publish.yml`. Find the new run id with `gh run list --workflow=docker-publish.yml --limit 1 --json databaseId,status` and store it.
8. Monitor the run (see "Monitoring" below). On success, run the "Verify" steps and report. On failure, surface the failed step's log and stop without retrying.

### `rerun`: re-run the most recent docker-publish workflow

For when the workflow failed transiently (network, Docker Hub rate-limit, etc.) and you want to retry without making any source changes.

**Steps**:

1. Run preflight checks.
2. `gh run list --workflow=docker-publish.yml --limit 1 --json databaseId,status,conclusion,headBranch` to find the most recent run.
3. If `conclusion == "success"`, ask the user whether they really want to re-run (it'll just publish the same image again, which is harmless but wasteful). If they confirm, proceed; otherwise stop.
4. `gh run rerun <id>` to re-run.
5. Monitor + verify + report.

### `dev`: publish a dev image from the current HEAD

For testing image changes outside of a tagged release.

**Steps**:

1. Run preflight checks.
2. Confirm with the user before pushing a dev tag (Docker Hub will accumulate `dev-<sha>` tags; cleanup is manual).
3. Trigger the workflow with `push=true`:
   ```bash
   gh workflow run docker-publish.yml --ref main --field push=true
   ```
4. Wait ~5 s and find the new run id; monitor + verify (the verify check needs the short SHA, which CI computes as `${GITHUB_SHA:0:7}` of `main`'s tip).

### `verify`: just check what's currently on Docker Hub

No publish. Useful to confirm what users would `docker pull`.

**Steps**:

1. `curl -s "https://hub.docker.com/v2/repositories/albertogarob/whistlerlib/tags/?page_size=20"` and pretty-print the result.
2. Report the available tags, their last-pushed dates, and the manifest digest for `:latest`.
3. If the user passed a specific version (`/publish-docker verify 0.2.0`), also report whether that exact tag exists.

## Preflight (every mode)

Before any state-changing action, verify:

1. **gh CLI is authenticated**: `gh auth status` returns non-error.
2. **gh active account has push access** to `observatoriogeo/whistlerlib`. Check with `gh api repos/observatoriogeo/whistlerlib --jq '.permissions.push'` (must be `true`).
3. **Docker Hub secrets exist** on the repo: both `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` must be listed by `gh secret list --repo observatoriogeo/whistlerlib`. If missing, STOP and tell the user to set them (see "Secret setup" below).
4. **Working tree is clean** (`git status --porcelain` empty). If not, stop and ask whether they want to stash, commit, or abort.

If any check fails, give the user the exact command to fix it; don't auto-apply destructive corrections.

## Monitoring (release / rerun / dev modes)

After triggering, poll with:

```bash
RUN_ID=<id>
gh run watch "$RUN_ID" --exit-status
```

`gh run watch` blocks until completion and exits non-zero on failure. For long runs (multi-arch buildx of a 2.5 GB image takes 12-20 min), prefer launching it in the background and polling state every 60 s via the Monitor tool, mirroring the pattern used in earlier session work.

On completion:
- Success → "Verify" section.
- Failure → `gh run view "$RUN_ID" --log-failed | tail -200` to surface the failed step, then stop. Don't auto-rerun on failure: the user should look at the log first.

## Verify (after successful publish)

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
3. As a final smoke test (only on the local dev box, optional, asks user first):
   ```bash
   docker pull albertogarob/whistlerlib:<tag>
   docker run --rm albertogarob/whistlerlib:<tag> python /app/smoke.py --self-test
   ```
   Skip the smoke step if it would take more than ~2 min to pull on the user's connection.

Report back: the published tags, the multi-arch confirmation, and the Docker Hub URL `https://hub.docker.com/r/albertogarob/whistlerlib/tags`.

## Secret setup (only if preflight detects missing secrets)

Tell the user (don't run, they need to do it themselves):

```bash
# Generate a token at https://app.docker.com/settings/personal-access-tokens
# Permissions: Read & Write.  Description: "whistlerlib CI"

echo -n "albertogarob" | gh secret set DOCKERHUB_USERNAME --repo observatoriogeo/whistlerlib
gh secret set DOCKERHUB_TOKEN --repo observatoriogeo/whistlerlib
# Paste the token when prompted, press Enter.
```

`DOCKERHUB_USERNAME` is the **maintainer's personal Docker Hub login** (`albertogarob`), not the org name. The token authenticates that user, who has push access to `albertogarob/whistlerlib` because it's their own namespace.

## Failure-mode cheatsheet

| Symptom | Likely cause | Fix |
|---|---|---|
| `gh run rerun` reports "no permission" | gh CLI not authed as a user with write access to `observatoriogeo/whistlerlib` | `gh auth switch -u <user-with-write>` |
| Workflow's "Log in to Docker Hub" step fails with `unauthorized` | `DOCKERHUB_TOKEN` invalid / expired / wrong permissions | Regenerate the token, re-`gh secret set` it |
| Workflow's push step fails with `requested access to the resource is denied` | `DOCKERHUB_USERNAME` doesn't have push rights on `albertogarob/whistlerlib` | Verify the username; for an org you'd need to be added as a member with Read/Write permission |
| Workflow's buildx step OOMs or stalls | GitHub Actions free runner ran out of memory on the arm64 cross-compile | Re-run; if it recurs, drop arm64 from `platforms:` in `docker-publish.yml` temporarily |
| Manifest exists but pulls of `:latest` return an old digest on user machines | Docker layer cache | Tell user to `docker pull --no-cache` or refer them to the version-pinned tag |

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
