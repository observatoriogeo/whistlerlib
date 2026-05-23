import pytest
import pandas as pd
from .conftest import combs_k_n_p_ds, combs_n_p_ds, combs_k0_n_p, combs_k0_n_p_r_ds, combs_k0_n_p_ds, validate_ngram


@pytest.mark.parametrize('k,n,p,ds', combs_k_n_p_ds)
@pytest.mark.usefixtures('tweet_dataset')
def test_k_lt_0(k, n, p, ds, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with k > 0 and a given n, p, and ds
    * Check that the number of rows in the output is equals to k
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    histogram = tweet_dataset.ngram_histogram_r(k=k,
                                                n=n,
                                                distributed_sorting=ds,
                                                return_time_profile=False)
    assert len(histogram.index) == k


@pytest.mark.parametrize('n,p,ds', combs_n_p_ds)
@pytest.mark.usefixtures('tweet_dataset')
def test_k_eq_0(n, p, ds, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with k = 0 and a given n, p, and ds
    * Check that the number of rows in the output is larger than 0
    '''

    if p > 1:
        tweet_dataset.repartition(p)
        assert tweet_dataset.get_num_partitions() == p

    histogram = tweet_dataset.ngram_histogram_r(k=0,
                                                n=n,
                                                distributed_sorting=ds,
                                                return_time_profile=False)
    assert len(histogram.index) > 0


@pytest.mark.parametrize('k,n,p', combs_k0_n_p)
@pytest.mark.usefixtures('tweet_dataset', 'tweet_dataset_p1')
def test_p1_eq_plt1(k, n, p, tweet_dataset, tweet_dataset_p1):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Check that the dataset with p = 1 has indeed only one partition
    * Run the whistlerlib method with p = 1 and a given k and n
    * Run the whistlerlib method with p > 1 and a given k and n
    * Check that the results of the two runs are identical
    * Note: ds=True is not tested because with distributed sorting enabled 
            there are no guarantees on the order of the resulting rows 
            for different values of p
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p
    assert tweet_dataset_p1.get_num_partitions() == 1

    histogram_plt1 = tweet_dataset.ngram_histogram_r(k=k,
                                                     n=n,
                                                     distributed_sorting=False,
                                                     return_time_profile=False)

    histogram_p1 = tweet_dataset_p1.ngram_histogram_r(k=k,
                                                      n=n,
                                                      distributed_sorting=False,
                                                      return_time_profile=False)

    # compare dataframes
    identical = histogram_plt1.equals(histogram_p1)

    # compute diff df in case of an assert failure for debugging
    histogram_p1["p"] = 1
    histogram_plt1["p"] = p
    diff_df = pd.concat([histogram_p1, histogram_plt1])
    diff_df = diff_df.drop_duplicates(
        subset=["N_Tokens", "Freq"], keep=False, ignore_index=True)

    assert identical, f'\nP=1\n{histogram_p1}\nP={p}\n{histogram_plt1}\nDiff=\n{diff_df}'


@pytest.mark.parametrize('k,n,p,r,ds', combs_k0_n_p_r_ds)
@pytest.mark.usefixtures('tweet_dataset')
def test_reps(k, n, p, r, ds, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with a given k, n, p, and ds
    * Run again the whistlerlib method with the same k, n, p and ds
    * Check that the outputs of the runs are identical
    Note: r is just the number of test repetition and not actually used inside the test
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    histogram = tweet_dataset.ngram_histogram_r(k=k,
                                                n=n,
                                                distributed_sorting=ds,
                                                return_time_profile=False)

    histogram_rep = tweet_dataset.ngram_histogram_r(k=k,
                                                    n=n,
                                                    distributed_sorting=ds,
                                                    return_time_profile=False)
    assert histogram_rep.equals(histogram)
 

@pytest.mark.parametrize('k,n,p,ds', combs_k0_n_p_ds)
@pytest.mark.usefixtures('tweet_dataset')
def test_validate_ngrams(k, n, p, ds, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with a given k, n, p, and ds    
    * Validate the n-grams    
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    histogram = tweet_dataset.ngram_histogram_r(k=k,
                                                n=n,
                                                distributed_sorting=ds,
                                                return_time_profile=False)

    for _, row in histogram.iterrows():
        ngram = row['N_Tokens']
        validate_ngram(ngram, n)
