"""Integration test for example 07 (R-bridge hashtag histogram).

R + the R libraries live only inside the worker container, no `r_required`
marker needed here because the `docker` fixture brings up the worker image
which has all of them. On a clean dev box without Docker, the conftest's
`_docker_available()` check skips the whole test instead.
"""

import pytest

pytestmark = pytest.mark.docker


def test_r_bridge_hashtag_histogram(whistlerlib_swarm, example_module):
    host, port = whistlerlib_swarm
    histogram = example_module.run(host, port)
    assert list(histogram.columns) == ['tag', 'freq']
    assert len(histogram) == 5
    freqs = histogram['freq'].tolist()
    assert freqs == sorted(freqs, reverse=True)
