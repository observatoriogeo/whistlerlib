import pytest

from .conftest import combs_sentiment_r, combs_sentiment_r_rep, r_required

pytestmark = r_required


@pytest.mark.parametrize('language,method,p', combs_sentiment_r)
@pytest.mark.usefixtures('tweet_dataset', 'tweet_dataset_p1')
def test_p1_eq_plt1(language, method, p, tweet_dataset, tweet_dataset_p1):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Check that the dataset with p = 1 has indeed only one partition
    * Run the whistlerlib method with a given language, method and p = 1        
    * Run the whistlerlib method with a given language, method and p > 1    
    * Check that the results of the two runs are identical
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p
    assert tweet_dataset_p1.get_num_partitions() == 1

    histogram_plt1 = tweet_dataset.sentiment_histogram_and_sum_r(language=language,
                                                                 method=method,
                                                                 return_time_profile=False)

    histogram_p1 = tweet_dataset_p1.sentiment_histogram_and_sum_r(language=language,
                                                                  method=method,
                                                                  return_time_profile=False)

    assert histogram_plt1.equals(histogram_p1)


@pytest.mark.parametrize('language,method,p,r', combs_sentiment_r_rep)
@pytest.mark.usefixtures('tweet_dataset')
def test_reps(language, method, p, r, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with a given language, method and p >= 1
    * Run again the whistlerlib method with the language, method and p
    * Check that the outputs of the runs are identical
    * Note: r is just the number of test repetition and not actually used inside the test
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    histogram = tweet_dataset.sentiment_histogram_and_sum_r(language=language,
                                                            method=method,
                                                            return_time_profile=False)

    histogram_rep = tweet_dataset.sentiment_histogram_and_sum_r(language=language,
                                                                method=method,
                                                                return_time_profile=False)

    assert histogram_rep.equals(histogram)
