"""Pytest fixtures for the Phase 4 example tests.

Brings up a local Docker cluster (master + workers, all using the same
locally-built `whistlerlib/worker:dev` image) and yields the scheduler
endpoint to each test. The cluster lifecycle is session-scoped: one
bring-up per pytest run.

Deployment choice for this fixture: **Docker Compose**, not Docker Swarm.
The production deployment story is Swarm (see `docker/stack.yml`), but
single-node Swarm is fiddly with the `node.role==worker` placement
constraint, so for local example tests we use `docker/docker-compose.yml`
which validates exactly the same image and network story. CI runs these
tests too.

Tests opt in via `@pytest.mark.docker` (or `pytestmark = pytest.mark.docker`)
and are deselected from the default `pytest` run via
`addopts = "-m 'not slow and not docker'"` in `pyproject.toml`.

Run only the docker-backed examples:

    pytest -m docker examples/

Pre-requisites: Docker daemon running, `whistlerlib/worker:dev` image
present locally (the fixture builds it on demand the first time;
this costs 5–10 minutes for the R + radvertools install). NLTK corpora
(`stopwords`, `punkt`, `punkt_tab`) are auto-downloaded to `~/nltk_data`
on first run because examples 03 (n-grams) and 04 (sentiment) call
`nltk.corpus.stopwords` on the client side.
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPOSE_FILE = REPO_ROOT / 'docker' / 'docker-compose.yml'
WORKER_IMAGE = 'whistlerlib/worker:dev'
PROJECT_NAME = 'whistlerlib-examples'
SCHEDULER_HOST = 'localhost'
SCHEDULER_PORT = 8786
SCHEDULER_READY_TIMEOUT_S = 120

# Corpora that `compute_ngram_histogram` / `compute_sentiment_range_spanish`
# load on the client. Mapped to their `nltk.data.find` lookup paths so we
# can skip the download when the corpus is already cached on the host.
NLTK_CORPORA = {
    'stopwords': 'corpora/stopwords',
    'punkt': 'tokenizers/punkt',
    'punkt_tab': 'tokenizers/punkt_tab',
}


def _docker_available() -> bool:
    """Docker CLI present and daemon responding."""
    if not shutil.which('docker'):
        return False
    try:
        subprocess.run(['docker', 'info'], capture_output=True,
                       check=True, timeout=10)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
            FileNotFoundError):
        return False


def _compose_cmd() -> list[str]:
    """Return the right compose binary for the installed Docker (v2 plugin
    `docker compose` preferred, falling back to v1 `docker-compose`)."""
    try:
        subprocess.run(['docker', 'compose', 'version'],
                       capture_output=True, check=True, timeout=5)
        return ['docker', 'compose']
    except (subprocess.CalledProcessError, FileNotFoundError,
            subprocess.TimeoutExpired):
        pass
    if shutil.which('docker-compose'):
        return ['docker-compose']
    raise RuntimeError('Neither `docker compose` nor `docker-compose` is available')


def _worker_image_present() -> bool:
    r = subprocess.run(['docker', 'images', '-q', WORKER_IMAGE],
                       capture_output=True, text=True, check=True)
    return bool(r.stdout.strip())


def _build_worker_image() -> None:
    env = os.environ.copy()
    env['DOCKER_BUILDKIT'] = '1'
    print(f'\n[examples-fixture] Building {WORKER_IMAGE} '
          '(one-time; ~5–10 min for R + radvertools)...')
    subprocess.run(
        ['docker', 'build',
         '-f', str(REPO_ROOT / 'docker' / 'Dockerfile.worker'),
         '-t', WORKER_IMAGE, str(REPO_ROOT)],
        env=env, check=True,
    )


def _ensure_nltk_corpora() -> None:
    """Pre-download NLTK corpora the example tests need on the host.

    The bridges in `dask/alt_python_algs/algs.py` call `nltk.download()`
    lazily on the client. On hosts where IPv6 routing is broken (common
    in residential / corporate networks) the default `getaddrinfo`
    returns the IPv6 record first and the download stalls in `SYN-SENT`
    for the full TCP retry budget, multiple minutes per corpus, which
    looks identical to a hung test. Force IPv4 for the download window.
    """
    import nltk

    missing = [name for name, path in NLTK_CORPORA.items()
               if _nltk_missing(nltk, path)]
    if not missing:
        return

    orig_getaddrinfo = socket.getaddrinfo

    def _ipv4_only(host, port, family=0, *args, **kwargs):
        return orig_getaddrinfo(host, port, socket.AF_INET, *args, **kwargs)

    socket.getaddrinfo = _ipv4_only
    try:
        for name in missing:
            print(f'[examples-fixture] downloading NLTK corpus: {name}')
            if not nltk.download(name, quiet=True):
                raise RuntimeError(
                    f'failed to download NLTK corpus {name!r}; '
                    'check network connectivity to raw.githubusercontent.com'
                )
    finally:
        socket.getaddrinfo = orig_getaddrinfo


def _nltk_missing(nltk_module, lookup_path: str) -> bool:
    try:
        nltk_module.data.find(lookup_path)
        return False
    except LookupError:
        return True


def _wait_for_scheduler(host: str = SCHEDULER_HOST,
                        port: int = SCHEDULER_PORT,
                        timeout: int = SCHEDULER_READY_TIMEOUT_S) -> None:
    from dask.distributed import Client
    deadline = time.time() + timeout
    last_exc: Exception | None = None
    while time.time() < deadline:
        try:
            client = Client(f'tcp://{host}:{port}', timeout=2)
            client.close()
            return
        except Exception as exc:
            last_exc = exc
            time.sleep(2)
    raise RuntimeError(
        f'scheduler at {host}:{port} did not become ready within {timeout}s; '
        f'last error: {last_exc}'
    )


@pytest.fixture(scope='session')
def whistlerlib_swarm():
    """Session-scoped local cluster bring-up.

    Yields `(scheduler_host, scheduler_port)`. The name is `whistlerlib_swarm`
    even though the implementation uses Compose so it stays stable if/when
    we promote to actual Swarm in CI.
    """
    if not _docker_available():
        pytest.skip('Docker not available, install Docker daemon to run '
                    'example tests')

    compose = _compose_cmd()

    if not _worker_image_present():
        try:
            _build_worker_image()
        except subprocess.CalledProcessError as exc:
            pytest.fail(f'failed to build {WORKER_IMAGE}: {exc}')

    _ensure_nltk_corpora()

    up = compose + ['-f', str(COMPOSE_FILE),
                    '-p', PROJECT_NAME,
                    'up', '-d', '--no-build']
    # Use a high host port for the dashboard so we don't fight whatever else
    # the dev box has on 8787 (it's a common dev port, Jupyter, RStudio,
    # other Dask clusters, etc.).
    env = os.environ.copy()
    env.setdefault('DASK_DASHBOARD_HOST_PORT', '18787')
    print(f'\n[examples-fixture] Bringing up cluster ({" ".join(up)})...')
    subprocess.run(up, check=True, env=env)

    try:
        _wait_for_scheduler()
        print(f'[examples-fixture] Scheduler ready at '
              f'{SCHEDULER_HOST}:{SCHEDULER_PORT}')
        yield (SCHEDULER_HOST, SCHEDULER_PORT)
    finally:
        down = compose + ['-f', str(COMPOSE_FILE),
                          '-p', PROJECT_NAME,
                          'down', '-v', '--remove-orphans']
        print('\n[examples-fixture] Tearing down cluster...')
        subprocess.run(down, capture_output=True)


@pytest.fixture
def whistlerlib_context(whistlerlib_swarm):
    """Convenience: a `whistlerlib.Context` bound to the local cluster."""
    from whistlerlib import Context
    host, port = whistlerlib_swarm
    return Context('processes', host, port)


def pytest_collection_modifyitems(config, items):
    """Bump the per-test timeout for `docker`-marked tests.

    The repo-wide pytest-timeout is 30s (good default for fast unit tests),
    but docker-backed example tests legitimately need more, first-run
    `docker compose up` can take 30-60s on its own pulling daskdev/dask,
    and an end-to-end run inside the cluster adds another 10-60s. Without
    this hook, every docker test would fail in the fixture setup phase.
    """
    for item in items:
        if any(m.name == 'docker' for m in item.iter_markers()):
            item.add_marker(pytest.mark.timeout(600))  # 10 min ceiling


@pytest.fixture
def example_module(request):
    """Load the sibling `example.py` of the requesting test by file path.

    Avoids the Python-module-name collision that would happen if we let each
    `test_example.py` do `from example import run`, there are 7 `example.py`
    files in 7 sibling directories whose names (`01-quickstart-...`) aren't
    valid Python identifiers, so the standard package-style imports don't
    work. `importlib.util.spec_from_file_location` loads each one by path.
    """
    import importlib.util
    example_path = request.path.parent / 'example.py'
    spec = importlib.util.spec_from_file_location('example', example_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
