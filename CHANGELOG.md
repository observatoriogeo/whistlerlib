# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

This entry tracks work toward the upcoming `0.2.0` revival release. See also
[`MIGRATION.md`](MIGRATION.md) for the upgrade story from the abandoned
pre-revival snapshot.

### Added
- PEP 621 `pyproject.toml` with hatchling build backend.
- `src/whistlerlib/` package layout.
- Python 3.11+ requirement declared via `requires-python` and `.python-version`.
- `CHANGELOG.md` and `MIGRATION.md`.
- Ported `getWordCloud.py` and `getWordCloud.R` from the unreleased working copy.
- Test suite (12 files) ported into `tests/`.

### Changed
- Package source relocated from `whistlerlib/` to `src/whistlerlib/` (via `git mv` to preserve history).

### Removed
- Pinned `requirements*.txt` files (replaced by `pyproject.toml` dependencies + extras).
