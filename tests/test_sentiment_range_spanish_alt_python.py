import pytest
from .conftest import combs_sentiment_spanish_alt_python, combs_sentiment_spanish_alt_python_rep, P


def check_monotonicity(a_list):
    for i in range(len(a_list) - 1):
        if a_list[i+1] < a_list[i]:
            return False
    return True


@pytest.mark.parametrize('interval,p', combs_sentiment_spanish_alt_python)
@pytest.mark.usefixtures('tweet_dataset')
def test_index_monotonicity(interval, p, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with a given interval and p >= 1
    * Check that the index of the resulting DataFrame is monotonically increasing
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    scores = tweet_dataset.sentiment_range_spanish_alt_python(left_end=interval[0],
                                                              right_end=interval[1],
                                                              return_time_profile=False)

    assert check_monotonicity(scores.index)


@pytest.mark.parametrize('interval,p', combs_sentiment_spanish_alt_python)
@pytest.mark.usefixtures('tweet_dataset')
def test_scores_minmax(interval, p, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with a given interval and p >= 1
    * Check that the resulting scores are within the given interval
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    scores = tweet_dataset.sentiment_range_spanish_alt_python(left_end=interval[0],
                                                              right_end=interval[1],
                                                              return_time_profile=False)

    assert (scores['score'].min() >= interval[0]) and \
        (scores['score'].max() <= interval[1])


@pytest.mark.parametrize('p', P)
@pytest.mark.usefixtures('tweet_dataset')
def test_interval_0to1(p, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with p >= 1, left_end = 0.0 and right_end = 1.0 (full range)
    * Check that the number of rows of the result is the number of rows of the dataset
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    scores = tweet_dataset.sentiment_range_spanish_alt_python(left_end=0.0,
                                                              right_end=1.0,
                                                              return_time_profile=False)

    assert len(scores.index) == tweet_dataset.tweet_count()


@pytest.mark.parametrize('interval,p', combs_sentiment_spanish_alt_python)
@pytest.mark.usefixtures('tweet_dataset', 'tweet_dataset_p1')
def test_p1_eq_plt1(interval, p, tweet_dataset, tweet_dataset_p1):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Check that the dataset with p = 1 has indeed only one partition
    * Run the whistlerlib method with a given interval and p = 1        
    * Run the whistlerlib method with a given interval and p > 1    
    * Check that the results of the two runs are identical
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p
    assert tweet_dataset_p1.get_num_partitions() == 1

    scores_plt1 = tweet_dataset.sentiment_range_spanish_alt_python(left_end=interval[0],
                                                                   right_end=interval[1],
                                                                   return_time_profile=False)

    scores_p1 = tweet_dataset_p1.sentiment_range_spanish_alt_python(left_end=interval[0],
                                                                    right_end=interval[1],
                                                                    return_time_profile=False)
    assert scores_plt1.equals(scores_p1)


@pytest.mark.parametrize('interval,p,r', combs_sentiment_spanish_alt_python_rep)
@pytest.mark.usefixtures('tweet_dataset')
def test_reps(interval, p, r, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with a given interval and p >= 1
    * Run again the whistlerlib method with the same interval and p
    * Check that the outputs of the runs are identical
    * Note: r is just the number of test repetition and not actually used inside the test
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    scores = tweet_dataset.sentiment_range_spanish_alt_python(left_end=interval[0],
                                                              right_end=interval[1],
                                                              return_time_profile=False)

    scores_rep = tweet_dataset.sentiment_range_spanish_alt_python(left_end=interval[0],
                                                                  right_end=interval[1],
                                                                  return_time_profile=False)

    assert scores_rep.equals(scores)
