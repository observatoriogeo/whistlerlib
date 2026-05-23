# Install with Docker

Whistlerlib ships **one custom Docker image** — `whistlerlib/worker` — that runs both worker and scheduler roles in a Dask cluster. R and every R library the R-bridge calls (`tm`, `syuzhet`, `radvertools`, `RWeka`, …) are baked in, so your host never installs R.

Two deployment shapes are supported out of the box:

| Use case | Tool | File |
|---|---|---|
| Local dev / smoke testing | Docker Compose | `docker/docker-compose.yml` |
| Production multi-node | Docker Swarm | `docker/stack.yml` |

The image is the same in both. The orchestration differs.

## Image roles

| Role | Image | Notes |
|---|---|---|
| Scheduler ("master") | `whistlerlib/worker:<version>` with the entrypoint overridden to `dask-scheduler` | The scheduler runs no whistlerlib algorithm code, but Dask requires consistent Python environments between client / scheduler / workers for task-graph serialization. We reuse the worker image rather than publish a second lean one. |
| Worker | `whistlerlib/worker:<version>` | Where every algorithm closure (alt-python and R-bridge) actually runs. |
| Client | Whatever Python env you have | `pip install whistlerlib` and connect via `Context(...)`. See [pip installation](pip.md). |

See [Architecture](../concepts/architecture.md) for the why behind this split.

## Image tags

| Tag | When | What |
|---|---|---|
| `latest` | each tagged release | most recent published version |
| `<major>.<minor>` | each tagged release | floating tag for that minor line |
| `<major>.<minor>.<patch>` | each tagged release | pinned version |
| `dev-<sha>` | manual `workflow_dispatch` runs in CI | development builds (never auto-tagged as `latest`) |

For reproducibility, pin to `<major>.<minor>.<patch>` in production.

## Quick start — local cluster with Docker Compose

```bash
# From the repo root (clone if you don't have it locally):
docker compose -f docker/docker-compose.yml up -d
```

You now have a scheduler on `tcp://localhost:8786`, a dashboard on `http://localhost:8787`, and two workers connected. Smoke-test it:

```bash
docker compose -f docker/docker-compose.yml \
    run --rm worker python /app/smoke.py master 8786
```

Then connect a client (on the host) and run something:

```python
from whistlerlib import Context

ctx = Context('processes', 'localhost', 8786)
# ... ds = ctx.load_csv(...) ...
```

Tear down when done:

```bash
docker compose -f docker/docker-compose.yml down
```

The compose file bind-mounts the host `/tmp` into each worker as read-only so a CSV written by the client (via `tempfile.NamedTemporaryFile`) is visible to workers under the same path. For non-trivial data, configure your own mount (NFS, a shared volume, etc.) — see `docker/stack.yml` for examples.

## Production — Docker Swarm

For multi-node production, use Swarm:

```bash
docker stack deploy -c docker/stack.yml whistlerlib
```

The stack file:

- Places the scheduler on a `node.role==manager` host (one scheduler, network-stable address).
- Replicates workers across `node.role==worker` hosts (scale with `docker service scale whistlerlib_worker=N`).
- Wires them on an overlay network so workers can find the scheduler by service name.

This matches the legacy Linode + Ansible production layout the library was designed for.

## Building locally

If you want to build the image yourself (e.g. you're hacking on `Dockerfile.worker`):

```bash
docker build -f docker/Dockerfile.worker -t whistlerlib/worker:dev .
```

The first build takes ~5–10 minutes (R + Posit binary R wheels + `radvertools` from GitHub + `uv sync`). Subsequent builds are cached layer-by-layer and finish in seconds unless you touched the R install or the lockfile.

## Next

- [Tutorial 01](../tutorials/01-quickstart-hashtag-histogram.md) — first end-to-end run against the local cluster.
- [Architecture](../concepts/architecture.md) — what the scheduler, workers, and R bridge actually do.
