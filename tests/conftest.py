import pytest
import advertools as adv
from whistlerlib import Context
import os

DASK_SCHEDULER_IP = os.getenv('WHISTLERLIB_DASK_SCHEDULER_IP')
DASK_SCHEDULER_PORT = os.getenv('WHISTLERLIB_DASK_SCHEDULER_PORT')  # 8786
# '/var/datasets/metroTestU.csv'
TESTS_DATASET_FILEN = os.getenv('WHISTLERLIB_TESTS_DATASET_FILEN')
TESTS_DATASET_ENCODING = os.getenv(
    'WHISTLERLIB_TESTS_DATASET_ENCODING')  # latin1
TESTS_DATASET_TEXT_COL = os.getenv(
    'WHISTLERLIB_TESTS_DATASET_TEXT_COL')  # text
TESTS_DATASET_DATE_COL = os.getenv(
    'WHISTLERLIB_TESTS_DATASET_DATE_COL')  # Date
R_SCRIPTS_PATH = os.getenv('WHISTLERLIB_R_SCRIPTS_PATH')
R_PATH = os.getenv('WHISTLERLIB_R_PATH')

assert DASK_SCHEDULER_IP, "Missing environment variable WHISTLERLIB_DASK_SCHEDULER_IP. Please set it."
assert DASK_SCHEDULER_PORT, "Missing environment variable WHISTLERLIB_DASK_SCHEDULER_PORT. Please set it."
assert TESTS_DATASET_FILEN, "Missing environment variable WHISTLERLIB_TESTS_DATASET_FILEN. Please set it."
assert TESTS_DATASET_ENCODING, "Missing environment variable WHISTLERLIB_TESTS_DATASET_ENCODING. Please set it."
assert TESTS_DATASET_TEXT_COL, "Missing environment variable WHISTLERLIB_TESTS_DATASET_TEXT_COL. Please set it."
assert TESTS_DATASET_DATE_COL, "Missing environment variable WHISTLERLIB_TESTS_DATASET_DATE_COL. Please set it."
assert R_SCRIPTS_PATH, "Missing environment variable WHISTLERLIB_R_SCRIPTS_PATH. Please set it."
assert R_PATH, "Missing environment variable WHISTLERLIB_R_PATH. Please set it."

DASK_SCHEDULER_PORT = int(DASK_SCHEDULER_PORT)


N = [1, 2, 3]
#P = [1, 2, 4]
P = [2, 4]
K = [10, 20, 30]
#K0 = [0, 10, 20, 30]
K0 = [0]
R = range(2)
W = ['word']  # TODO: finish
SENTIMENT_R_LANGUAGES = ['english', 'spanish']
NGRAM_ALT_PYTHON_LANGUAGES = ['english', 'spanish']
SENTIMENT_R_METHODS = ['nrc']  # TODO: finish
SENTIMENT_SPANISH_ALT_PYTHON_INTERVALS = [(0.0, 0.5), (0.5, 1.0), (0.9, 1.0)]
DISTRIBUTED_SORTING = [False, True]

combs_p_ds = [(p, ds)
              for p in P
              for ds in DISTRIBUTED_SORTING]

combs_no_k_ngram_alt_python = [(n, lan, w, p, ds)
                               for n in N
                               for lan in NGRAM_ALT_PYTHON_LANGUAGES
                               for w in W
                               for p in P
                               for ds in DISTRIBUTED_SORTING]

combs_k0_ngram_alt_python = [(k, n, lan, w, p, ds)
                             for k in K0
                             for n in N
                             for lan in NGRAM_ALT_PYTHON_LANGUAGES
                             for w in W
                             for p in P
                             for ds in DISTRIBUTED_SORTING]

combs_klt0_ngram_alt_python = [(k, n, lan, w, p, ds)
                               for k in K
                               for n in N
                               for lan in NGRAM_ALT_PYTHON_LANGUAGES
                               for w in W
                               for p in P
                               for ds in DISTRIBUTED_SORTING]

combs_k0_ngram_alt_python_no_ds = [(k, n, lan, w, p)
                                   for k in K
                                   for n in N
                                   for lan in NGRAM_ALT_PYTHON_LANGUAGES
                                   for w in W
                                   for p in P]

combs_k0_ngram_alt_python_rep = [(k, n, lan, w, p, r, ds)
                                 for k in K0
                                 for n in N
                                 for lan in NGRAM_ALT_PYTHON_LANGUAGES
                                 for w in W
                                 for p in P
                                 for r in R
                                 for ds in DISTRIBUTED_SORTING]

combs_sentiment_spanish_alt_python = [(interval, p)
                                      for interval in SENTIMENT_SPANISH_ALT_PYTHON_INTERVALS
                                      for p in P]

combs_sentiment_spanish_alt_python_rep = [(interval, p, r)
                                          for interval in SENTIMENT_SPANISH_ALT_PYTHON_INTERVALS
                                          for p in P
                                          for r in R]

combs_sentiment_r = [(language, method, p)
                     for language in SENTIMENT_R_LANGUAGES
                     for method in SENTIMENT_R_METHODS
                     for p in P]

combs_sentiment_r_rep = [(language, method, p, r)
                         for language in SENTIMENT_R_LANGUAGES
                         for method in SENTIMENT_R_METHODS
                         for p in P
                         for r in R]

combs_p_r = [(p, r)
             for p in P
             for r in R]

combs_k_p_ds = [(k, p, ds)
                for k in K
                for p in P
                for ds in DISTRIBUTED_SORTING]

combs_k0_p = [(k, p)
              for k in K0
              for p in P]

combs_k0_p_ds = [(k, p, ds)
                 for k in K0
                 for p in P
                 for ds in DISTRIBUTED_SORTING]


combs_k0_p_r_ds = [(k, p, r, ds)
                   for k in K0
                   for p in P
                   for r in R
                   for ds in DISTRIBUTED_SORTING]

combs_k_n_p_ds = [(k, n, p, ds)
                  for k in K
                  for n in N
                  for p in P
                  for ds in DISTRIBUTED_SORTING]

combs_n_p_ds = [(n, p, ds)
                for n in N
                for p in P
                for ds in DISTRIBUTED_SORTING]

combs_k0_n_p = [(k, n, p)
                for k in K0
                for n in N
                for p in P]

combs_k0_n_p_r_ds = [(k, n, p, r, ds)
                     for k in K0
                     for n in N
                     for p in P
                     for r in R
                     for ds in DISTRIBUTED_SORTING]

combs_k0_n_p_ds = [(k, n, p, ds)
                   for k in K0
                   for n in N
                   for p in P
                   for ds in DISTRIBUTED_SORTING]


def pytest_generate_tests(metafunc):
    os.environ['WHISTLERLIB_R_SCRIPTS_PATH'] = R_SCRIPTS_PATH
    os.environ['WHISTLERLIB_R_PATH'] = R_PATH


@pytest.fixture(scope='module')
def whistlerlib_context():
    return Context('processes', DASK_SCHEDULER_IP, DASK_SCHEDULER_PORT)


@pytest.fixture(scope='function')
def tweet_dataset(whistlerlib_context):
    dataset = \
        whistlerlib_context.load_csv(filen=TESTS_DATASET_FILEN,
                                     meta={
                                         'column_mapping': {
                                             'date_column': TESTS_DATASET_DATE_COL,
                                             'text_column': TESTS_DATASET_TEXT_COL
                                         },
                                         'file_encoding': TESTS_DATASET_ENCODING
                                     },
                                     num_partitions=1)
    assert dataset.tweet_count() == 1000
    return dataset


@pytest.fixture(scope='function')
def tweet_dataset_p1(whistlerlib_context):
    dataset = \
        whistlerlib_context.load_csv(filen=TESTS_DATASET_FILEN,
                                     meta={
                                         'column_mapping': {
                                             'date_column': TESTS_DATASET_DATE_COL,
                                             'text_column': TESTS_DATASET_TEXT_COL
                                         },
                                         'file_encoding': TESTS_DATASET_ENCODING
                                     },
                                     num_partitions=1)
    assert dataset.tweet_count() == 1000
    return dataset


def validate_hashtag(hashtag):
    hashtags = adv.extract_hashtags(hashtag)
    # there should be only 1 extracted hashtag from 1 tweet (coming from the hashtag variable)
    assert len(hashtags['hashtags']) == 1
    assert len(hashtags['hashtags'][0]) == 1
    # advertools converts to lowercase extracted hashtags
    assert hashtags['hashtags'][0][0] == hashtag.lower()


def validate_mention(mention):
    mentions = adv.extract_mentions(mention)
    # there should be only 1 extracted mention from 1 tweet (coming from the mention variable)
    assert len(mentions['mentions']) == 1
    assert len(mentions['mentions'][0]) == 1
    # advertools converts to lowercase extracted mentions
    assert mentions['mentions'][0][0] == mention.lower()


def validate_ngram(ngram, n):
    assert len(ngram.split(' ')) == n


def validate_graph(graph_df, graph):
    tokens = list(graph_df['source']) + list(graph_df['target'])
    num_tokens = len(set(tokens))

    assert not graph.is_directed()
    assert graph.ecount() == len(graph_df.index)
    assert graph.vcount() == num_tokens
