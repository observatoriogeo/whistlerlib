---
name: docs-deploy
description: Update and deploy the Whistlerlib docs site at https://whistlerlib.observatoriogeo.mx via the GitHub Pages workflow (.github/workflows/docs-deploy.yml). Use whenever the user wants to deploy, redeploy, ship, push, publish, or update the docs site to production / Pages / live, AND whenever the user wants to check whether the deploy is in sync ("is everything synced?", "did my docs changes ship?", "is local in sync with the published site?", "is the docs site up to date with main?"). Triggers on deploy phrases like "deploy the docs", "redeploy", "publish the website", "ship the docs", "update the live site", any mention of whistlerlib.observatoriogeo.mx; AND on sync-check phrases like "is everything synced", "verify the deploy", "did my changes ship".
---

# Docs deploy workflow (Whistlerlib)

End-to-end loop for publishing the Whistlerlib documentation site to GitHub Pages on the vanity domain `https://whistlerlib.observatoriogeo.mx`. The deploy is a single GitHub Actions workflow; there is no SSH, no Jinja2 templating, no reverse-proxy chain. Pushes to `main` that touch `website/**` (or the workflow file itself) build and publish; nothing else triggers a deploy.

## Fixed parameters for this project

These do not change across deploys. If the user asks to deploy somewhere else, stop and ask, do not silently swap a value.

| Param | Value | Where |
|---|---|---|
| Repo (SSH) | `git@github.com:observatoriogeo/whistlerlib.git` | |
| Default branch | `main` | |
| Workflow | `.github/workflows/docs-deploy.yml` (jobs: `build`, `deploy`) | |
| Build path | `website/` | |
| Build cmd | `cd website && npm ci && npm run build` | |
| Lock file (must be tracked) | `website/package-lock.json` | requires `!website/package-lock.json` negation in repo-root `.gitignore` |
| Node version | 20 (pinned by `actions/setup-node@v4`) | workflow |
| Custom domain | `whistlerlib.observatoriogeo.mx` | `website/static/CNAME` |
| DNS record | `CNAME whistlerlib.observatoriogeo.mx. -> observatoriogeo.github.io.` | observatoriogeo.mx zone (out of repo scope) |
| Pages config | `build_type: workflow`, `cname: whistlerlib.observatoriogeo.mx`, `https_enforced: true` | repo Settings → Pages |
| Workflow trigger paths | `website/**`, `.github/workflows/docs-deploy.yml` | workflow `on.push.paths` |

## Architecture (so you can debug when something does not deploy)

```
git push main
     │  (only if paths under website/** or the workflow file changed)
     ▼
.github/workflows/docs-deploy.yml
     ├─ build:  actions/checkout → setup-node@20 (cache: website/package-lock.json)
     │          → npm ci (in website/) → npm run build → upload-pages-artifact
     └─ deploy: actions/deploy-pages → Pages serves at whistlerlib.observatoriogeo.mx
```

Total time end-to-end is around one minute (typical: ~55 s build, ~8 s deploy). The two jobs run sequentially; the deploy job depends on the build artifact. No SSH layer, no proxy chain, no manual steps after push.

## The content-sync chain (subtle, read carefully)

Most-confusing failure mode. The website does NOT read from `docs/`; it reads from `website/docs/`. The chain is:

1. **Canonical tutorial source:** `examples/<slug>/README.md` (the runnable example's own README).
2. **`scripts/sync_tutorials.py`** regenerates `docs/tutorials/<slug>.md` from each example README (writes HTML banner comments `<!-- ... -->`).
3. **The website docs tree at `website/docs/tutorials/<slug>.md`** is a manual mirror of the sync script's output, with the HTML banner comment swapped to MDX form `{/* ... */}` (MDX 3 in strict mode chokes on HTML comments in `.md` files).

The deploy's path filter is `website/**`. Concrete consequences:

- Editing only `examples/<slug>/README.md`: no deploy.
- Editing only `docs/tutorials/<slug>.md`: no deploy.
- Running `python scripts/sync_tutorials.py` without also mirroring into `website/docs/tutorials/`: no deploy.
- Editing `website/docs/tutorials/<slug>.md` directly: triggers a deploy but creates drift with the canonical source; the next sync-script run will overwrite the drift.

Correct workflow for tutorial edits:

1. Edit `examples/<slug>/README.md`.
2. `python scripts/sync_tutorials.py`, this regenerates `docs/tutorials/<slug>.md`.
3. Mirror into `website/docs/tutorials/<slug>.md`, swapping `<!-- -->` to `{/* */}`.
4. Commit all three paths together, push.

If step 3 is skipped, the live site stays stale even though `git status` looks clean for the rest of the tree.

## Phases (the deploy loop)

Four phases for an active deploy. Phase 5 is a standalone sync check (no deploy in progress).

### 1. Local build verification

```bash
cd website && npm run build
```

`onBrokenLinks: 'throw'` catches link rot at build time. If the build fails locally, do not push, the workflow will reproduce the same failure.

Common build-breakers:

- Em-dashes (U+2014) anywhere in `.md` / `.mdx` / `.ts` / `.tsx` / `.css` / `.json` content under `website/`: the project's separate `docs` CI job will fail even if Docusaurus accepts the build. Pre-push scan: `grep -rP "\x{2014}" website/ examples/`.
- HTML comments `<!-- -->` in `.md` files under `website/docs/`: MDX 3 strict parsing fails. Swap to `{/* ... */}`.
- Trailing-slash drift on directory-index doc links (e.g. `/docs/api/` vs `/docs/api`). See `LINK_CONVENTIONS.md` at the repo root for the rule.

### 2. Commit and push

```bash
git add <paths>
git status
git commit -m "<one-line summary>"
git push origin main
```

Before committing, sanity-check the content-sync chain (see above) and that `website/package-lock.json` is in the diff if `package.json` changed. Pushing is visible to others and triggers the live deploy, so confirm with the user unless they have already said "deploy".

If the changes touch only `examples/`, `docs/`, or `scripts/`, the push will NOT trigger a deploy. Either also mirror to `website/`, or trigger a manual run with `gh workflow run docs-deploy.yml --ref main`.

### 3. Watch the workflow

```bash
RUN_ID=$(gh run list --workflow=docs-deploy.yml --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch "$RUN_ID" --exit-status
```

Typical timing: ~55 s build, ~8 s deploy. If the build step fails, view the logs with `gh run view "$RUN_ID" --log-failed`.

### 4. Verify live

Three-line smoke test against the public URL:

```bash
# Root
curl -sS -o /dev/null -w 'root:    %{http_code}\n' \
  https://whistlerlib.observatoriogeo.mx/

# Deep doc page (catches baseUrl misconfig and broken sidebars)
curl -sS -o /dev/null -w 'deep:    %{http_code}\n' \
  https://whistlerlib.observatoriogeo.mx/docs/api/

# Static asset (catches Docusaurus build-with-wrong-baseUrl)
curl -sS -o /dev/null -w 'asset:   %{http_code}\n' \
  https://whistlerlib.observatoriogeo.mx/img/whistlerlib-logo.png
```

All three should return 200 (occasional 301 on the root is fine for the trailing-slash redirect). If any return 404 or SSL errors, jump to "Debugging unreachable deploys" below.

### 5. Verify sync (standalone)

This phase is also a **standalone entry point**: when the user asks "is everything synced?" / "did my changes ship?" / "is local in sync with the published site?", jump straight here, skip phases 1 through 4.

Four state stores must agree:

1. Local working tree (no uncommitted edits in `website/`).
2. Local `HEAD`.
3. `origin/main` on GitHub.
4. The SHA of the latest successful workflow run.

```bash
git status --short website/             # expect: empty output
git fetch origin
LOCAL=$(git rev-parse HEAD)
ORIGIN=$(git rev-parse origin/main)
LATEST_RUN=$(gh run list --workflow=docs-deploy.yml --status=success --limit 1 \
              --json headSha --jq '.[0].headSha')

echo "local:    $LOCAL"
echo "origin:   $ORIGIN"
echo "deployed: $LATEST_RUN"
```

**Pass:** all three hashes match AND `git status --short website/` is empty. Report the matched short hash.

**Fail:** read the gap from the mismatch table:

| Symptom | Means | Fix |
|---|---|---|
| `git status --short website/` non-empty | Local website edits never committed | Run phase 2 |
| `local != origin` | Committed, never pushed | `git push origin main` |
| `origin != deployed` AND there is a more-recent run that failed | Build broke; the deployed version is stale | View failure with `gh run view <id> --log-failed`, fix, re-push |
| `origin != deployed` AND no recent run exists | Path filter missed: the push touched only non-`website/**` paths | Trigger `gh workflow run docs-deploy.yml --ref main`, or mirror into `website/` |

## Failure modes worth knowing about

Eight patterns that have actually bitten this project.

### 1. Lock file untracked

**Symptom:** `actions/setup-node@v4` fails with `Some specified paths were not resolved, unable to cache dependencies`. Deploy job is skipped.

**Cause:** the repo-root `.gitignore` excludes `package-lock.json` project-wide (legacy rule from the Python project). The `!website/package-lock.json` negation in `.gitignore` is load-bearing.

**Fix:**

```bash
# Confirm the lock file is tracked
git ls-files website/package-lock.json

# If empty, restore the negation rule and re-add
grep -n "!website/package-lock.json" .gitignore
git add .gitignore website/package-lock.json
```

### 2. CNAME drift

**Symptom:** `gh api repos/observatoriogeo/whistlerlib/pages --jq .cname` returns null or a wrong host. HTTPS cert provisioning fails or the custom domain stops resolving.

**Cause:** `website/static/CNAME` is missing, contains a different host, or has stray whitespace.

**Fix:**

```bash
printf 'whistlerlib.observatoriogeo.mx\n' > website/static/CNAME
git add website/static/CNAME && git commit -m "Restore Pages CNAME"
# After deploy:
gh api -X PUT repos/observatoriogeo/whistlerlib/pages \
  --field cname=whistlerlib.observatoriogeo.mx \
  --field https_enforced=true
```

### 3. Em-dashes in committed prose

**Symptom:** the workflow build succeeds (Docusaurus accepts em-dashes), but a separate `docs` CI job fails on the same commit and blocks the merge.

**Cause:** project-wide rule against U+2014 in `.py` / `.md` / `.mdx` / `.yml` / `.yaml` / `.toml` / `Dockerfile*` / `.R` content.

**Fix:** scan and substitute before push.

```bash
grep -rnP "\x{2014}" website/ examples/ docs/   # should be empty
# If hits found, replace each with comma, colon, period, or parens.
```

### 4. HTML comments in website MDX tutorials

**Symptom:** local `npm run build` fails with an MDX acorn parse error around a `<!--` token in `website/docs/tutorials/<slug>.md`.

**Cause:** `scripts/sync_tutorials.py` writes HTML banner comments (`<!-- ... -->`); the website's strict-mode MDX 3 parser refuses them in `.md` files.

**Fix:** swap to `{/* ... */}` when mirroring from `docs/tutorials/` into `website/docs/tutorials/`. This is the canonical website mirror, not a workaround.

### 5. Trailing-slash convention drift

**Symptom:** clicking a navbar link to `/docs/api/` or `/docs/tutorials/` lands on a 404; or local build fails with a `Docs version "current" has no doc named "..."` error.

**Cause:** missing trailing slash on a navbar / footer / homepage `to:` prop that targets a directory-index doc (one with an `index.mdx`). React Router then resolves relative MDX links against the no-slash form and drops the directory segment.

**Fix:** see `LINK_CONVENTIONS.md` for the full rule. Add the trailing slash to the offending `to:` prop. Do NOT set `trailingSlash: true` globally in `docusaurus.config.ts`, that breaks relative links across the whole site.

### 6. Path-filter miss

**Symptom:** `gh run list --workflow=docs-deploy.yml --limit 1` shows no new run after a push to `main`.

**Cause:** the push touched only files outside `website/**` and outside `.github/workflows/docs-deploy.yml`. The path filter intentionally excludes pure-Python and top-level docs edits.

**Fix:** if the change is content-relevant, also mirror into `website/`. If it is a one-off cosmetic redeploy, trigger manually:

```bash
gh workflow run docs-deploy.yml --ref main
```

### 7. Pages source drift

**Symptom:** the workflow's `deploy` job fails with a permissions or "Pages not configured" error.

**Cause:** someone toggled repo Settings → Pages → Source from "GitHub Actions" to "Deploy from a branch", or disabled Pages entirely.

**Fix:** check the API.

```bash
gh api repos/observatoriogeo/whistlerlib/pages --jq .build_type
# expect: "workflow"
```

If different, set it manually in repo Settings → Pages → "Build and deployment / Source: GitHub Actions" (the Source field is not settable via the public API).

### 8. `https_enforced` got flipped off

**Symptom:** `http://whistlerlib.observatoriogeo.mx/` returns 200 instead of a redirect to HTTPS; the Pages API shows `https_enforced: false`.

**Cause:** explicitly toggled off in repo Settings, or auto-reset after a CNAME change via the API.

**Fix:**

```bash
gh api -X PUT repos/observatoriogeo/whistlerlib/pages \
  --field https_enforced=true
```

## Debugging unreachable deploys

When live curl returns 4xx / 5xx, walk the chain from outside in.

```bash
# 1. Is the workflow even running?
gh run list --workflow=docs-deploy.yml --limit 3

# 2. Did the latest run succeed?
gh run view <run_id> --json status,conclusion,jobs

# 3. Pages config state
gh api repos/observatoriogeo/whistlerlib/pages | python3 -m json.tool

# 4. DNS still resolves correctly?
dig +short whistlerlib.observatoriogeo.mx
# Expected:
#   observatoriogeo.github.io.
#   185.199.108.153
#   185.199.109.153
#   185.199.110.153
#   185.199.111.153

# 5. HTTPS cert state
gh api repos/observatoriogeo/whistlerlib/pages --jq .https_certificate
# Expect: {"state": "approved", ...}

# 6. Direct curl with -v if the SSL handshake is failing
curl -vsS -o /dev/null https://whistlerlib.observatoriogeo.mx/ 2>&1 | head -30
```

Stop and report at the first mismatch; do not redeploy blindly.

## Out of scope for this skill

- **Initial GH Pages enablement.** One-time setup, already done. If somehow disabled, restore via repo Settings → Pages → Source: GitHub Actions.
- **DNS record provisioning.** Already done at the `observatoriogeo.mx` domain registrar; not changeable from this repo.
- **Cert revocation / renewal.** GitHub auto-manages Let's Encrypt for the custom domain; no manual cert work is needed.
- **Snapshotting a new versioned docs release** (e.g., freezing `docs/` as `versioned_docs/version-0.2.0/` before starting 0.3.0 work). Distinct workflow; deserves its own skill (TBD).
- **Migrating from Albatross.** Whistlerlib was Pages from day 1; no migration story exists.
- **PyPI / Docker Hub publishes.** Covered by separate skills (e.g. `publish-docker`); this skill is docs-only.
