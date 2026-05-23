"""Pytest configuration for the Whistlerlib integration test suite.

Sets up:
- A session-scoped Dask `LocalCluster` so tests don't need an external scheduler.
- A session-scoped synthetic 1000-row CSV (real X-platform CSVs cannot be
  redistributed; see `.plans/REVIVAL-PLAN.md` §2).
- NLTK stopword pre-caching so test runs don't depend on network.
- `r_required` skip marker for tests that need an R install.
- All the parametrization combinators and `validate_*` helpers used by the
  test modules.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

# Point NLTK at the test-bundled stopwords corpus BEFORE pytest collects
# anything that might transitively import nltk. Keeps the suite offline.
_NLTK_DATA_PATH = (Path(__file__).parent / 'fixtures' / 'nltk_data').resolve()
os.environ['NLTK_DATA'] = str(_NLTK_DATA_PATH)

import pytest

# --------------------------------------------------------------------------- #
# R-bridge skip marker
# --------------------------------------------------------------------------- #

R_SCRIPTS_PATH = os.getenv('WHISTLERLIB_R_SCRIPTS_PATH')
R_PATH = os.getenv('WHISTLERLIB_R_PATH')


def _has_r() -> bool:
    """True when both R bridge env vars are set and `Rscript` is on PATH."""
    if not R_SCRIPTS_PATH or not R_PATH:
        return False
    return shutil.which('Rscript') is not None


r_required = pytest.mark.skipif(
    not _has_r(),
    reason=(
        "R bridge unavailable: set WHISTLERLIB_R_PATH and "
        "WHISTLERLIB_R_SCRIPTS_PATH and install R + Rscript to run these tests."
    ),
)


def pytest_generate_tests(metafunc):
    # Propagate R env vars to subprocesses (Dask workers) when they ARE set.
    # Skipped silently when the R bridge isn't configured.
    if R_SCRIPTS_PATH:
        os.environ['WHISTLERLIB_R_SCRIPTS_PATH'] = R_SCRIPTS_PATH
    if R_PATH:
        os.environ['WHISTLERLIB_R_PATH'] = R_PATH


# --------------------------------------------------------------------------- #
# Dask LocalCluster (session-scoped, in-process workers)
# --------------------------------------------------------------------------- #

@pytest.fixture(scope='session')
def dask_cluster():
    from dask.distributed import LocalCluster
    # processes=True (the LocalCluster default) → workers as subprocesses,
    # scheduler exposes a tcp://host:port URL that Context can parse.
    # NLTK_DATA env var (set at module-load) is inherited by the subprocess
    # workers so the algorithms find the bundled stopwords corpus.
    cluster = LocalCluster(
        n_workers=2,
        threads_per_worker=1,
        dashboard_address=None,
    )
    yield cluster
    cluster.close()


@pytest.fixture(scope='session')
def dask_address(dask_cluster):
    # scheduler_address looks like "tcp://127.0.0.1:36465"
    _, hostport = dask_cluster.scheduler_address.split('://')
    host, port = hostport.split(':')
    return host, int(port)


# --------------------------------------------------------------------------- #
# Synthetic 10-row tweet CSV
#
# Deliberately tiny — Phase 2's goal is "does the code path work end-to-end",
# not realistic profiling. The 10 rows are hand-crafted (not random) to
# satisfy every assertion the inherited test suite makes:
#
#   * `tweet_count() == TESTS_DATASET_SIZE` (= 10)
#   * histogram tests with k=10 need 10 distinct hashtags/mentions/ngrams
#     → each row carries a UNIQUE hashtag and a UNIQUE mention
#   * `sentiment_range_spanish_alt_python(left=0.9, right=1.0)` returns >0 rows
#     → 5 rows use strongly positive Spanish phrases
#   * n-gram histogram tests (n=1..3, k=10) need ≥10 distinct n-grams
#     → text has plenty of varied multi-word content
# --------------------------------------------------------------------------- #

TESTS_DATASET_SIZE = 10


# 30 distinct hashtags and 30 distinct mentions, 3 per row across 10 rows.
# Row i carries hashtags 3i..3i+2 and mentions 3i..3i+2 — none repeat across rows.
# This gives:
#   * 30 unique hashtags / mentions → k=10, k=20, k=30 histogram tests all succeed
#   * 30 distinct co-occurrence pairs (C(3,2)=3 per row × 10) → coonet tests non-empty
# Content texts are 6 unique Spanish content words per row (60 unique total) so
# unigram / bigram / trigram histogram tests find ≥30 distinct n-grams across n=1..3.
# Rows 0–2 prefix a strongly-positive phrase so the slow sentiment (0.9, 1.0)
# test has matching rows when explicitly run.
_HASHTAGS = [
    '#política', '#méxico', '#cdmx', '#noticias', '#ciencia',
    '#datos', '#código', '#salud', '#economía', '#cultura',
    '#educación', '#deporte', '#turismo', '#arte', '#música',
    '#cine', '#libro', '#tecnología', '#ambiente', '#clima',
    '#agua', '#energía', '#empleo', '#industria', '#vivienda',
    '#movilidad', '#seguridad', '#justicia', '#derecho', '#democracia',
]
_MENTIONS = [
    '@centrogeo', '@unam', '@conahcyt', '@uam', '@ipn',
    '@gob', '@senado', '@scjn', '@inegi', '@sct',
    '@sep', '@profeco', '@imss', '@issste', '@bansefi',
    '@semarnat', '@sener', '@economia', '@hacienda', '@salud',
    '@cultura', '@turismo', '@deporte', '@trabajo', '@bienestar',
    '@adip', '@metro', '@semovi', '@sicultura', '@sectur',
]
_TEXTS = [
    # Rows 0–2: positive sentiment prefix + 6 distinct content words.
    'excelente maravilloso fantástico ciudad metro urbano social política cultura',
    'magnífico bueno encantador datos análisis investigación estudio método tecnología',
    'extraordinario perfecto increíble ciencia salud economía educación progreso desarrollo',
    # Rows 3–9: neutral with distinct vocabulary so trigrams stay distinct across rows.
    'ambiente clima ecología naturaleza sostenibilidad reciclaje',
    'trabajo empleo industria comercio negocio finanza',
    'arte música literatura cine teatro danza',
    'historia memoria patrimonio tradición herencia identidad',
    'ley justicia derecho seguridad libertad democracia',
    'agua tierra fuego viento luz energía',
    'familia comunidad sociedad vecino amistad solidaridad',
]


def _build_rows() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    n = len(_TEXTS)
    assert len(_HASHTAGS) >= 3 * n and len(_MENTIONS) >= 3 * n
    for i in range(n):
        hs = ' '.join(_HASHTAGS[3 * i: 3 * i + 3])
        ms = ' '.join(_MENTIONS[3 * i: 3 * i + 3])
        text = f'{_TEXTS[i]} {hs} {ms}'
        rows.append((f'2022-01-01T{i:02d}:00:00', text))
    return rows


_ROWS = _build_rows()


@pytest.fixture(scope='session')
def synthetic_tweets_csv(tmp_path_factory):
    import pandas as pd
    df = pd.DataFrame(_ROWS, columns=['Date', 'text'])
    path = tmp_path_factory.mktemp('whistlerlib_data') / 'synthetic_tweets.csv'
    df.to_csv(path, index=False, encoding='utf-8')
    return str(path)


# --------------------------------------------------------------------------- #
# Whistlerlib fixtures
#
# Architecture: the CSV is loaded into a Dask DataFrame ONCE per session and
# persisted. Each test gets a fresh `TweetDataset` wrapper over the same base
# DataFrame — wrappers can repartition independently because `dd.repartition`
# returns a new object rather than mutating the source. Per-test cost is
# therefore tens of milliseconds rather than seconds.
# --------------------------------------------------------------------------- #

_DS_META = {
    'column_mapping': {'date_column': 'Date', 'text_column': 'text'},
    'file_encoding': 'utf-8',
}


@pytest.fixture(scope='session')
def whistlerlib_context(dask_address):
    from whistlerlib import Context
    host, port = dask_address
    return Context('processes', host, port)


@pytest.fixture(scope='session')
def _base_dask_df(whistlerlib_context, synthetic_tweets_csv):
    df = whistlerlib_context.dataset_repository_client.load_csv(
        synthetic_tweets_csv, _DS_META,
    )
    df = df.repartition(npartitions=1).persist()
    return df


@pytest.fixture(scope='session')
def _base_dataset_size_check(_base_dask_df):
    # Run the `tweet_count() == TESTS_DATASET_SIZE` assertion ONCE per session
    # instead of per test (it was the biggest fixed cost in the old fixture).
    from whistlerlib.dataset import TweetDataset
    ds = TweetDataset(ds_metadata=_DS_META, dask_df=_base_dask_df, num_partitions=1)
    assert ds.tweet_count() == TESTS_DATASET_SIZE


def _wrap(base_df):
    from whistlerlib.dataset import TweetDataset
    return TweetDataset(ds_metadata=_DS_META, dask_df=base_df, num_partitions=1)


@pytest.fixture(scope='function')
def tweet_dataset(_base_dask_df, _base_dataset_size_check):
    return _wrap(_base_dask_df)


@pytest.fixture(scope='function')
def tweet_dataset_p1(_base_dask_df, _base_dataset_size_check):
    # Independent wrapper kept at num_partitions=1 for partition-comparison
    # tests against `tweet_dataset` after repartitioning.
    return _wrap(_base_dask_df)


# --------------------------------------------------------------------------- #
# Validators (used by individual test files)
# --------------------------------------------------------------------------- #

def validate_hashtag(hashtag):
    import advertools as adv
    hashtags = adv.extract_hashtags(hashtag)
    assert len(hashtags['hashtags']) == 1
    assert len(hashtags['hashtags'][0]) == 1
    # advertools converts to lowercase extracted hashtags
    assert hashtags['hashtags'][0][0] == hashtag.lower()


def validate_mention(mention):
    import advertools as adv
    mentions = adv.extract_mentions(mention)
    assert len(mentions['mentions']) == 1
    assert len(mentions['mentions'][0]) == 1
    assert mentions['mentions'][0][0] == mention.lower()


def validate_ngram(ngram, n):
    assert len(ngram.split(' ')) == n


def validate_graph(graph_df, graph):
    tokens = list(graph_df['source']) + list(graph_df['target'])
    num_tokens = len(set(tokens))
    assert not graph.is_directed()
    assert graph.ecount() == len(graph_df.index)
    assert graph.vcount() == num_tokens


# --------------------------------------------------------------------------- #
# Parametrization combinator constants (consumed by individual test modules)
# --------------------------------------------------------------------------- #

N = [1, 2, 3]
P = [2, 4]
K = [10, 20, 30]
K0 = [0]
R = range(2)
W = ['word']
SENTIMENT_R_LANGUAGES = ['english', 'spanish']
NGRAM_ALT_PYTHON_LANGUAGES = ['english', 'spanish']
SENTIMENT_R_METHODS = ['nrc']
SENTIMENT_SPANISH_ALT_PYTHON_INTERVALS = [(0.0, 0.5), (0.5, 1.0), (0.9, 1.0)]
DISTRIBUTED_SORTING = [False, True]


combs_p_ds = [(p, ds) for p in P for ds in DISTRIBUTED_SORTING]

combs_no_k_ngram_alt_python = [
    (n, lan, w, p, ds)
    for n in N for lan in NGRAM_ALT_PYTHON_LANGUAGES for w in W
    for p in P for ds in DISTRIBUTED_SORTING
]

combs_k0_ngram_alt_python = [
    (k, n, lan, w, p, ds)
    for k in K0 for n in N for lan in NGRAM_ALT_PYTHON_LANGUAGES for w in W
    for p in P for ds in DISTRIBUTED_SORTING
]

combs_klt0_ngram_alt_python = [
    (k, n, lan, w, p, ds)
    for k in K for n in N for lan in NGRAM_ALT_PYTHON_LANGUAGES for w in W
    for p in P for ds in DISTRIBUTED_SORTING
]

combs_k0_ngram_alt_python_no_ds = [
    (k, n, lan, w, p)
    for k in K for n in N for lan in NGRAM_ALT_PYTHON_LANGUAGES for w in W
    for p in P
]

combs_k0_ngram_alt_python_rep = [
    (k, n, lan, w, p, r, ds)
    for k in K0 for n in N for lan in NGRAM_ALT_PYTHON_LANGUAGES for w in W
    for p in P for r in R for ds in DISTRIBUTED_SORTING
]

combs_sentiment_spanish_alt_python = [
    (interval, p)
    for interval in SENTIMENT_SPANISH_ALT_PYTHON_INTERVALS for p in P
]

combs_sentiment_spanish_alt_python_rep = [
    (interval, p, r)
    for interval in SENTIMENT_SPANISH_ALT_PYTHON_INTERVALS
    for p in P for r in R
]

combs_sentiment_r = [
    (language, method, p)
    for language in SENTIMENT_R_LANGUAGES for method in SENTIMENT_R_METHODS
    for p in P
]

combs_sentiment_r_rep = [
    (language, method, p, r)
    for language in SENTIMENT_R_LANGUAGES for method in SENTIMENT_R_METHODS
    for p in P for r in R
]

combs_p_r = [(p, r) for p in P for r in R]

combs_k_p_ds = [
    (k, p, ds) for k in K for p in P for ds in DISTRIBUTED_SORTING
]

combs_k0_p = [(k, p) for k in K0 for p in P]

combs_k0_p_ds = [
    (k, p, ds) for k in K0 for p in P for ds in DISTRIBUTED_SORTING
]

combs_k0_p_r_ds = [
    (k, p, r, ds) for k in K0 for p in P for r in R for ds in DISTRIBUTED_SORTING
]

combs_k_n_p_ds = [
    (k, n, p, ds) for k in K for n in N for p in P for ds in DISTRIBUTED_SORTING
]

combs_n_p_ds = [
    (n, p, ds) for n in N for p in P for ds in DISTRIBUTED_SORTING
]

combs_k0_n_p = [(k, n, p) for k in K0 for n in N for p in P]

combs_k0_n_p_r_ds = [
    (k, n, p, r, ds)
    for k in K0 for n in N for p in P for r in R for ds in DISTRIBUTED_SORTING
]

combs_k0_n_p_ds = [
    (k, n, p, ds) for k in K0 for n in N for p in P for ds in DISTRIBUTED_SORTING
]
