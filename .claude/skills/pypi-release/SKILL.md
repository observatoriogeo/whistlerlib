---
name: pypi-release
description: Publish a new Whistlerlib version to PyPI end-to-end (pre-flight audit, build, twine check, TestPyPI dry-run, fresh-venv install verification, real PyPI upload, post-publish smoke test, git tag). Use whenever the user wants to release, publish, ship, or cut a new version to PyPI / pypi.org, and whenever the user wants to do a TestPyPI dry-run, verify the latest PyPI release, or test that a freshly built wheel installs cleanly. Triggers on release phrases like "release 0.X.Y to PyPI", "publish to pypi", "ship the next version", "cut a release", "do a PyPI dry-run", "TestPyPI dry-run", "verify the PyPI install", any mention of pypi.org/project/whistlerlib.
---

# PyPI release workflow (Whistlerlib)

End-to-end loop for publishing a new Whistlerlib version to PyPI. The workflow is intentionally two-phase: a TestPyPI dry-run validates that the artifacts and the install flow work, then the real PyPI upload runs unattended. PyPI version numbers are permanently burned, so do not skip the dry-run on a first-time release of any version.

## Fixed parameters for this project

These do not change across releases. If the user asks to publish under a different package name or to a different index, stop and ask, do not silently swap a value.

| Param | Value | Where |
|---|---|---|
| Package name | `whistlerlib` | `pyproject.toml` `[project] name` |
| Build backend | hatchling | `pyproject.toml` `[build-system]` |
| Build cmd | `uv build` | produces `dist/whistlerlib-<ver>-py3-none-any.whl` and `dist/whistlerlib-<ver>.tar.gz` |
| Validate cmd | `uvx twine check dist/*` | catches metadata / README rendering issues |
| Upload cmd | `uvx twine upload --config-file .pypirc --repository <name> dist/*` | `<name>` is `testpypi` or `pypi` |
| Credentials | `.pypirc` at the repo root (gitignored) | INI with `[testpypi]` + `[pypi]` sections, `username = __token__`, `password = pypi-...` |
| PyPI project page | `https://pypi.org/project/whistlerlib/<ver>/` | |
| TestPyPI project page | `https://test.pypi.org/project/whistlerlib/<ver>/` | |
| Sdist include list | `src/`, `tests/`, `README.md`, `LICENSE`, `CHANGELOG.md`, `pyproject.toml` | `[tool.hatch.build.targets.sdist]` |
| Project URLs (must be correct on the PyPI page) | Homepage + Documentation = `https://whistlerlib.observatoriogeo.mx`, Repository / Issues / Changelog = `github.com/observatoriogeo/whistlerlib`, Paper = `https://doi.org/10.1007/s11042-024-19827-z` | `pyproject.toml` `[project.urls]` |
| Git tag scheme | `v<ver>` (e.g. `v0.2.0`) | annotated tag, push to origin |

The `v*` tag push triggers `.github/workflows/docker-publish.yml`, which rebuilds and republishes `albertogarob/whistlerlib:<ver>` to Docker Hub. Idempotent if the source has not changed; benign but takes ~5 to 10 min of CI time.

## Architecture (so you can debug when something fails)

```
bump pyproject.toml `version` + CHANGELOG.md  (manual, before invoking this skill)
        │
        ▼
uv build                    → dist/<name>-<ver>-py3-none-any.whl + .tar.gz
        │
        ▼
uvx twine check dist/*      → metadata + README validation (PASSED gate)
        │
        ▼
uvx twine upload --repository testpypi dist/*
        │
        ▼
uv venv --seed + pip install (deps from PyPI, whistlerlib --no-deps from TestPyPI)
        │  (smoke import passes)
        ▼
uvx twine upload --repository pypi dist/*       ← IRREVERSIBLE
        │
        ▼
fresh venv + pip install whistlerlib==<ver>    ← real-PyPI verification
        │
        ▼
git tag -a v<ver> -m "Whistlerlib <ver>" + git push origin v<ver>
        │  (docker-publish.yml workflow auto-fires on v* tag)
        ▼
shields.io PyPI badge auto-flips to <ver> on the README within minutes
```

## Phases

Eight phases for a release. Stop at the first failure; do not proceed to phase N+1 if phase N errored.

### 1. Pre-flight audit

Read `pyproject.toml` and confirm:

- `name = "whistlerlib"` (must match PyPI).
- `version` is the new version (bumped from the last release; PyPI rejects duplicates).
- `description` is concise (one line, no marketing fluff).
- `readme = "README.md"` (hatchling auto-detects `text/markdown` content type).
- `requires-python` matches what is tested in CI (`>=3.11` currently).
- `license = "GPL-3.0-or-later"` + `license-files = ["LICENSE"]` (PEP 639).
- `authors` has at least name + email.
- `keywords` and `classifiers` are reasonable for discoverability.
- `dependencies` floors are accurate (no missing runtime dep that the code imports).
- `[project.urls]` points at the live docs site (Homepage / Documentation) and the real GitHub repo (Repository / Issues / Changelog) and the DOI (Paper). Watch for stale `CentroGeo/whistlerlib` placeholders, the real repo is `observatoriogeo/whistlerlib`.

Also confirm the README hero image uses an absolute URL (`https://whistlerlib.observatoriogeo.mx/img/whistlerlib-logo.png`), since PyPI does not follow relative paths.

If anything looks wrong, surface it and ask the user before changing.

### 2. Build

```bash
rm -rf dist
uv build
```

Produces:
- `dist/whistlerlib-<ver>-py3-none-any.whl` (typically ~45 kB)
- `dist/whistlerlib-<ver>.tar.gz` (typically ~4.5 MB, includes `tests/fixtures/nltk_data/`)

Sanity-check the wheel actually contains the R scripts:

```bash
uvx --from wheel python -m wheel unpack --dest /tmp/wheel-unpack dist/whistlerlib-<ver>-py3-none-any.whl
find /tmp/wheel-unpack -name '*.R' | wc -l   # expect 7
```

The R scripts under `src/whistlerlib/dask/r_algs/funcs/*/*.R` are load-bearing for the R-bridge analytics; if the count is anything other than 7, hatchling missed them and the wheel is broken.

### 3. Validate

```bash
uvx twine check dist/*
```

Both files must report `PASSED`. The check covers:
- README parses as valid markdown.
- Metadata is RFC-compliant.
- File names and content match each other.

### 4. TestPyPI upload

```bash
uvx twine upload --config-file .pypirc --repository testpypi dist/*
```

Watch for the trailing `View at: https://test.pypi.org/project/whistlerlib/<ver>/`. Confirm 200 with:

```bash
curl -sS -o /dev/null -w '%{http_code}\n' https://test.pypi.org/project/whistlerlib/<ver>/
```

### 5. Test install + smoke import from TestPyPI

This is the most failure-prone step because TestPyPI hosts dependency-confusion sentinel packages (notably `jmespath==99.99.99`) that poison naive installs. The canonical safe pattern is to install all deps from real PyPI in step 5a, then `whistlerlib --no-deps` from TestPyPI in step 5b.

```bash
# Clean venv with pip seeded
rm -rf /tmp/test-install-venv
uv venv --seed --python 3.11 /tmp/test-install-venv

# 5a: install all deps from REAL PyPI only (no TestPyPI in the picture)
/tmp/test-install-venv/bin/python -m pip install --quiet \
  "dask[distributed]>=2024.1" "pandas>=2.2" "numpy>=1.26,<3" "pyarrow>=15" \
  "fsspec>=2024.1" "cloudpickle>=3" "msgpack>=1.0" "scikit-learn>=1.4" \
  "nltk>=3.8" "igraph>=0.11" "advertools>=0.16" \
  "sentiment-analysis-spanish>=0.0.25" "emoji>=2"

# 5b: install whistlerlib WITH --no-deps from TestPyPI only
/tmp/test-install-venv/bin/python -m pip install \
  --index-url https://test.pypi.org/simple/ --no-deps \
  whistlerlib==<ver>

# Smoke import
/tmp/test-install-venv/bin/python -c "
from whistlerlib import Context
from whistlerlib.dataset import TweetDataset
from whistlerlib.dask import alt_python_algs, r_algs, coonet_algs, base_algs
import importlib.metadata as md
print('whistlerlib version:', md.version('whistlerlib'))
"
```

The dep install is heavy (TensorFlow is ~500 MB via `sentiment-analysis-spanish`). Allow 5 to 15 min on a typical connection. Use `run_in_background: true` if the call exceeds the foreground timeout, then poll for completion.

### 6. Publish to real PyPI (irreversible)

```bash
uvx twine upload --config-file .pypirc --repository pypi dist/*
```

This is the point of no return: PyPI versions cannot be overwritten or deleted (only yanked, which keeps the version reserved). Do not invoke this phase unless the user has explicitly authorized publishing to pypi.org.

Confirm with:

```bash
curl -sS -o /dev/null -w '%{http_code}\n' https://pypi.org/project/whistlerlib/<ver>/
```

### 7. Verify the real-PyPI install

Fresh venv, no extra-index dance (TestPyPI is now out of the picture):

```bash
rm -rf /tmp/pypi-verify-venv
uv venv --seed --python 3.11 /tmp/pypi-verify-venv
/tmp/pypi-verify-venv/bin/python -m pip install --quiet whistlerlib==<ver>
/tmp/pypi-verify-venv/bin/python -c "
from whistlerlib import Context
import importlib.metadata as md
print('whistlerlib version:', md.version('whistlerlib'))
"
```

### 8. Git tag and push (if not already present)

```bash
git tag -l v<ver>                          # check local
git ls-remote --tags origin v<ver>         # check origin

# If not present:
git tag -a v<ver> -m "Whistlerlib <ver>"
git push origin v<ver>
```

The tag push triggers `.github/workflows/docker-publish.yml`, which rebuilds and republishes the Docker image. Idempotent if the source has not changed.

## Failure modes worth knowing about

Eight patterns that have actually bitten this project on the first release.

### 1. TestPyPI dependency-confusion sentinel

**Symptom:** pip install fails with `Failed to resolve 'cx-demo-test.website'` or `Failed building wheel for jmespath`, hint mentions `jmespath==99.99.99`.

**Cause:** TestPyPI hosts version-99.99.99 fake packages for common transitive deps (jmespath via advertools → scrapy → parsel → jmespath, etc.) to catch installers that consider all indices equally. pip + uv default version resolvers pick the higher version, get the sentinel, and the install fails (the sentinel is intentionally unbuildable).

**Fix:** never put TestPyPI and real PyPI in the same index set for transitive dep resolution. Install deps from real PyPI alone in one step, then `whistlerlib --no-deps` from TestPyPI in a second step. The two-step pattern in phase 5 is the canonical answer.

### 2. `uv pip install --index-strategy unsafe-best-match`

**Symptom:** Same TestPyPI sentinel hits even with pypi.org primary and TestPyPI extra.

**Cause:** `--index-strategy unsafe-best-match` makes uv consider all versions across all indices, regardless of order. This is exactly what the dependency-confusion attack relies on.

**Fix:** never use that flag for TestPyPI installs. Use plain pip (default first-index strategy) or split the install into the two phases above.

### 3. `uv venv` without pip

**Symptom:** `No module named pip` after `uv venv /tmp/foo`.

**Cause:** `uv venv` does not seed pip / setuptools / wheel by default.

**Fix:** `uv venv --seed` for any venv you intend to drive with `python -m pip`.

### 4. `.pypirc` is a bare token, not INI

**Symptom:** Twine prompts for username / password despite `--config-file .pypirc` being set, OR uploads to the wrong repository.

**Cause:** the file contains only the raw token instead of a proper INI structure.

**Fix:** the file must contain section headers and key = value lines. Confirm with `configparser` (never `cat` the file directly):

```bash
.venv/bin/python -c "
import configparser
cp = configparser.ConfigParser()
cp.read('.pypirc')
print('sections:', cp.sections())   # expect ['distutils', 'testpypi', 'pypi']
for s in cp.sections():
    for k in cp[s]:
        v = cp[s][k]
        if k.lower() in ('username', 'repository'):
            print(f'  [{s}] {k} = {v}')
        else:
            print(f'  [{s}] {k} = <set, {len(v)} chars>' if v else f'  [{s}] {k} = <EMPTY>')
"
```

A correct file shape:

```ini
[distutils]
  index-servers =
    testpypi
    pypi

[testpypi]
  repository = https://test.pypi.org/legacy/
  username = __token__
  password = pypi-XXXX...

[pypi]
  username = __token__
  password = pypi-XXXX...
```

### 5. `.pypirc` not gitignored

**Symptom:** `git status` shows `.pypirc` (or `.env.pypirc`, or whatever filename you use) as untracked. The token is one `git add .` away from being public.

**Cause:** the file was created at the repo root without first updating `.gitignore`.

**Fix:** add the filename to `.gitignore` BEFORE writing any credential into the file. Confirm with `git check-ignore -v .pypirc`.

### 6. Token leak via shell output

**Symptom:** the user's PyPI / TestPyPI token shows up in a conversation transcript, terminal scrollback, or log file.

**Cause:** code printed the file's contents (or a "redacted" wrapper that did not handle bare tokens, for example an `awk -F= '{print $1}'` redactor will print the whole line when the line contains no `=`).

**Fix:** never read or print a credential file with `cat`, `head`, `grep -A`, or naive awk. Use the `configparser` snippet above (only structurally-safe values are printed). If a token does leak, immediately tell the user to revoke at `https://[test.]pypi.org/manage/account/token/` and issue a fresh one.

### 7. Project URL placeholders shipped to PyPI

**Symptom:** the PyPI project page shows broken "Source" / "Issues" / "Homepage" links (404 on click).

**Cause:** `pyproject.toml` `[project.urls]` was left with placeholder values, e.g. `github.com/CentroGeo/whistlerlib` (a non-existent repo) instead of `github.com/observatoriogeo/whistlerlib`.

**Fix:** fix before phase 2 (rebuild). PyPI metadata cannot be edited after upload; you would have to publish a new patch version with corrected URLs.

### 8. Version not bumped before re-upload

**Symptom:** `twine upload` rejects with `HTTPError: 400 ... File already exists`. PyPI does not allow overwriting a published version.

**Cause:** `pyproject.toml` `version` was not bumped between releases. Also affects TestPyPI (same constraint).

**Fix:** bump `version` in `pyproject.toml`, add a CHANGELOG entry, then start the workflow from phase 2 (rebuild).

## Debugging unreachable releases

When the project page returns 404 or pip cannot find the version, walk these in order:

```bash
# 1. Did the upload actually succeed?
ls dist/                          # expect both .whl and .tar.gz at the new version

# 2. Is the project page live on PyPI?
curl -sS -o /dev/null -w '%{http_code}\n' https://pypi.org/project/whistlerlib/<ver>/
# Wait ~30 s on first publish if 404 (CDN propagation).

# 3. Can pip even see the version?
pip index versions whistlerlib    # lists all available

# 4. If installing from TestPyPI for a dry-run, check the version is there too
curl -sS -o /dev/null -w '%{http_code}\n' https://test.pypi.org/project/whistlerlib/<ver>/

# 5. If install errors but the version exists, get verbose pip output
pip install whistlerlib==<ver> --verbose 2>&1 | tail -40
```

## Out of scope for this skill

- **Yanking a release.** Done via the PyPI web UI (`https://pypi.org/manage/project/whistlerlib/release/<ver>/`); the yanked version stays reserved (cannot be reissued) but is hidden from default resolvers. The skill does not automate yanking.
- **Trusted publishing via GitHub Actions** (OIDC-based, no token). Planned future enhancement; until then we use API tokens.
- **Pre-release versioning** (`0.3.0a1`, `0.3.0rc1`). The workflow above works for these too; PyPI honors PEP 440. No special handling needed beyond bumping `version` to the appropriate string.
- **Bumping the version itself.** That is a maintainer decision based on semver impact (added APIs, breaking changes, bug fixes). The skill assumes `version` is already bumped to the target release before invocation.
- **CHANGELOG generation.** Maintainer-curated; the skill assumes the CHANGELOG entry for the new version is already in place.
- **PyPI account / token provisioning.** One-time setup per maintainer; the skill assumes `.pypirc` is already configured with valid `[testpypi]` and `[pypi]` sections.
