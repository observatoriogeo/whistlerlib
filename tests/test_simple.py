import pytest

##############################
# alt python methods
##############################


@pytest.mark.usefixtures('tweet_dataset')
def test_hashtag_histogram_alt_python(tweet_dataset):
    histogram = tweet_dataset.hashtag_histogram_alt_python(k=10)
    print(f'\n{histogram}')
    assert len(histogram.index) == 10


@pytest.mark.usefixtures('tweet_dataset')
def test_mention_histogram_alt_python(tweet_dataset):
    histogram = tweet_dataset.mention_histogram_alt_python(k=10)
    print(f'\n{histogram}')
    assert len(histogram.index) == 10


@pytest.mark.usefixtures('tweet_dataset')
def test_ngram_histogram_alt_python(tweet_dataset):
    histogram = tweet_dataset.ngram_histogram_alt_python(n=2,
                                                         k=10,
                                                         lan='spanish',
                                                         w='word')
    print(f'\n{histogram}')
    assert len(histogram.index) == 10


@pytest.mark.usefixtures('tweet_dataset')
def test_sentiment_range_spanish_alt_python(tweet_dataset):
    df = tweet_dataset.sentiment_range_spanish_alt_python(left_end=0.9,
                                                          right_end=1.0)
    print(f'\n{df}')
    assert len(df.index) > 0

##############################
# R methods
##############################


@pytest.mark.usefixtures('tweet_dataset')
def test_hashtag_histogram_r(tweet_dataset):
    histogram = tweet_dataset.hashtag_histogram_r(k=10)
    print(f'\n{histogram}')
    assert len(histogram.index) == 10


@pytest.mark.usefixtures('tweet_dataset')
def test_mention_histogram_r(tweet_dataset):
    histogram = tweet_dataset.mention_histogram_r(k=10)
    print(f'\n{histogram}')
    assert len(histogram.index) == 10


@pytest.mark.usefixtures('tweet_dataset')
def test_ngram_histogram_r(tweet_dataset):
    histogram = tweet_dataset.ngram_histogram_r(k=10, n=2)
    print(f'\n{histogram}')
    assert len(histogram.index) == 10


@pytest.mark.usefixtures('tweet_dataset')
def test_sentiment_histogram_and_sum_r(tweet_dataset):
    histogram = tweet_dataset.sentiment_histogram_and_sum_r(language='spanish',
                                                            method='nrc')
    print(f'\n{histogram}')
    assert len(histogram.index) > 0


##############################
# Coonet methods
##############################

@pytest.mark.usefixtures('tweet_dataset')
def test_hashtag_weighted_coonet(tweet_dataset):
    df, graph = tweet_dataset.hashtag_weighted_coonet()
    print(f'\n{df}')
    print(graph.summary())
    assert len(df.index) > 0
    assert graph.vcount() > 0


@pytest.mark.usefixtures('tweet_dataset')
def test_mention_weighted_coonet(tweet_dataset):
    df, graph = tweet_dataset.mention_weighted_coonet()
    print(f'\n{df}')
    print(graph.summary())
    assert len(df.index) > 0
    assert graph.vcount() > 0
