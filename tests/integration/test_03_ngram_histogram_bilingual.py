"""Integration test for example 03."""

import pytest

EXAMPLE_SLUG = '03-ngram-histogram-bilingual'

pytestmark = pytest.mark.docker


def test_ngram_histogram_bilingual(whistlerlib_swarm, example_module):
    host, port = whistlerlib_swarm
    spa, eng = example_module.run(host, port)

    assert list(spa.columns) == ['N_Tokens', 'Freq']
    assert list(eng.columns) == ['N_Tokens', 'Freq']
    assert len(spa) == 3
    assert len(eng) == 3

    # Each row must be a 2-token bigram.
    for bigram in list(spa['N_Tokens']) + list(eng['N_Tokens']):
        assert len(bigram.split()) == 2

    # Spanish stopwords should not leak into Spanish bigrams.
    spa_stopwords = {'el', 'la', 'de', 'que', 'en', 'y', 'a', 'los',
                     'del', 'se', 'las', 'por', 'un', 'para', 'con'}
    for bigram in spa['N_Tokens']:
        for token in bigram.split():
            assert token not in spa_stopwords, f'spanish stopword {token!r} in {bigram!r}'

    # English stopwords likewise.
    eng_stopwords = {'the', 'a', 'an', 'is', 'are', 'of', 'in', 'to',
                     'and', 'or', 'for', 'on', 'at', 'by'}
    for bigram in eng['N_Tokens']:
        for token in bigram.split():
            assert token not in eng_stopwords, f'english stopword {token!r} in {bigram!r}'
