import pytest

from .conftest import (
    combs_k0_ngram_alt_python,
    combs_k0_ngram_alt_python_no_ds,
    combs_k0_ngram_alt_python_rep,
    combs_klt0_ngram_alt_python,
    combs_no_k_ngram_alt_python,
    validate_ngram,
)


@pytest.mark.parametrize('k,n,lan,w,p,ds', combs_klt0_ngram_alt_python)
@pytest.mark.usefixtures('tweet_dataset', 'tweet_dataset_p1')
def test_k_lt_0(k, n, lan, w, p, ds, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with k > 0 and a given n, lan, w, p and ds
    * Check that the number of rows in the output is equals to k
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    histogram = tweet_dataset.ngram_histogram_alt_python(n=n,
                                                         k=k,
                                                         lan=lan,
                                                         w=w,
                                                         distributed_sorting=ds,
                                                         return_time_profile=False)
    assert len(histogram.index) == k


@pytest.mark.parametrize('n,lan,w,p,ds', combs_no_k_ngram_alt_python)
@pytest.mark.usefixtures('tweet_dataset', 'tweet_dataset_p1')
def test_k_eq_0(n, lan, w, p, ds, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with k = 0 and a given n, lan, w, p and ds
    * Check that the number of rows in the output is larger than 0
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    histogram = tweet_dataset.ngram_histogram_alt_python(n=n,
                                                         k=0,
                                                         lan=lan,
                                                         w=w,
                                                         distributed_sorting=ds,
                                                         return_time_profile=False)
    assert len(histogram.index) > 0


@pytest.mark.parametrize('k,n,lan,w,p', combs_k0_ngram_alt_python_no_ds)
@pytest.mark.usefixtures('tweet_dataset', 'tweet_dataset_p1')
def test_p1_eq_plt1(k, n, lan, w, p, tweet_dataset, tweet_dataset_p1):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Check that the dataset with p = 1 has indeed only one partition
    * Run the whistlerlib method with p = 1 and a given k, n, lan, and w
    * Run the whistlerlib method with p > 1 and a given k, n, lan, and w
    * Check that the results of the two runs are identical
    * Note: ds=True is not tested because with distributed sorting enabled 
            there are no guarantees on the order of the resulting rows 
            for different values of p
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p
    assert tweet_dataset_p1.get_num_partitions() == 1

    histogram_plt1 = tweet_dataset.ngram_histogram_alt_python(n=n,
                                                              k=k,
                                                              lan=lan,
                                                              w=w,
                                                              distributed_sorting=False,
                                                              return_time_profile=False)

    histogram_p1 = tweet_dataset_p1.ngram_histogram_alt_python(n=n,
                                                               k=k,
                                                               lan=lan,
                                                               w=w,
                                                               distributed_sorting=False,
                                                               return_time_profile=False)

    assert histogram_plt1.equals(histogram_p1)


@pytest.mark.parametrize('k,n,lan,w,p,r,ds', combs_k0_ngram_alt_python_rep)
@pytest.mark.usefixtures('tweet_dataset')
def test_reps(k, n, lan, w, p, r, ds, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with a given k, n, lan, w, p, and ds 
    * Run again the whistlerlib method with the same k, n, lan, w, p, r, and ds 
    * Check that the outputs of the runs are identical
    Note: r is just the number of test repetition and not actually used inside the test
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    histogram = tweet_dataset.ngram_histogram_alt_python(n=n,
                                                         k=k,
                                                         lan=lan,
                                                         w=w,
                                                         distributed_sorting=ds,
                                                         return_time_profile=False)

    histogram_rep = tweet_dataset.ngram_histogram_alt_python(n=n,
                                                             k=k,
                                                             lan=lan,
                                                             w=w,
                                                             distributed_sorting=ds,
                                                             return_time_profile=False)

    assert histogram_rep.equals(histogram)


@pytest.mark.parametrize('k,n,lan,w,p,ds', combs_k0_ngram_alt_python)
@pytest.mark.usefixtures('tweet_dataset')
def test_validate_ngrams(k, n, lan, w, p, ds, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with a given k, n, lan, w, p, and ds     
    * Validate the n-grams      
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    histogram = tweet_dataset.ngram_histogram_alt_python(n=n,
                                                         k=k,
                                                         lan=lan,
                                                         w=w,
                                                         distributed_sorting=ds,
                                                         return_time_profile=False)

    for _, row in histogram.iterrows():
        ngram = row['N_Tokens']
        validate_ngram(ngram, n)