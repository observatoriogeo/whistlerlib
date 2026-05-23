import pytest

from .conftest import (
    combs_k0_p,
    combs_k0_p_ds,
    combs_k0_p_r_ds,
    combs_k_p_ds,
    combs_p_ds,
    r_required,
    validate_mention,
)


@pytest.mark.parametrize('k,p,ds', combs_k_p_ds)
@pytest.mark.usefixtures('tweet_dataset')
def test_k_lt_0(k, p, ds, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with k > 0 and a given n, p, and ds
    * Check that the number of rows in the output is equals to k
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    histogram = tweet_dataset.mention_histogram_alt_python(k=k,
                                                           distributed_sorting=ds,
                                                           return_time_profile=False)
    assert len(histogram.index) == k


@pytest.mark.parametrize('p,ds', combs_p_ds)
@pytest.mark.usefixtures('tweet_dataset')
def test_k_eq_0(p, ds, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with k = 0 and a given n, p, and ds
    * Check that the number of rows in the output is larger than 0
    '''

    if p > 1:
        tweet_dataset.repartition(p)
        assert tweet_dataset.get_num_partitions() == p

    histogram = tweet_dataset.mention_histogram_alt_python(k=0,
                                                           distributed_sorting=ds,
                                                           return_time_profile=False)
    assert len(histogram.index) > 0


@pytest.mark.parametrize('k,p', combs_k0_p)
@pytest.mark.usefixtures('tweet_dataset', 'tweet_dataset_p1')
def test_p1_eq_plt1(k, p, tweet_dataset, tweet_dataset_p1):
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

    histogram_plt1 = tweet_dataset.mention_histogram_alt_python(k=k,
                                                                distributed_sorting=False,
                                                                return_time_profile=False)

    histogram_p1 = tweet_dataset_p1.mention_histogram_alt_python(k=k,
                                                                 distributed_sorting=False,
                                                                 return_time_profile=False)
    assert histogram_plt1.equals(histogram_p1)


@pytest.mark.parametrize('k,p,r,ds', combs_k0_p_r_ds)
@pytest.mark.usefixtures('tweet_dataset')
def test_reps(k, p, r, ds, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with a given k, n, p, and ds
    * Run again the whistlerlib method with the same k, n, p, and ds
    * Check that the outputs of the runs are identical
    * Note: r is just the number of test repetition and not actually used inside the test
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    histogram = tweet_dataset.mention_histogram_alt_python(k=k,
                                                           distributed_sorting=ds,
                                                           return_time_profile=False)

    histogram_rep = tweet_dataset.mention_histogram_alt_python(k=k,
                                                               distributed_sorting=ds,
                                                               return_time_profile=False)
    assert histogram_rep.equals(histogram)

#TODO: disabled


@r_required
@pytest.mark.parametrize('k,p,r,ds', combs_k0_p_r_ds)
@pytest.mark.usefixtures('tweet_dataset')
def test_python_vs_r(k, p, r, ds, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with a given k, n, p, and ds (python)
    * Run the whistlerlib method with a given k, n, p, and ds (r)
    * Check that the outputs of the runs are identical
    * Note: r is just the number of test repetition and not actually used inside the test
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    histogram_alt_python = tweet_dataset.mention_histogram_alt_python(k=k,
                                                                      distributed_sorting=ds,
                                                                      return_time_profile=False)

    histogram_r = tweet_dataset.mention_histogram_r(k=k,
                                                    distributed_sorting=ds,
                                                    return_time_profile=False)
    assert histogram_alt_python.equals(
        histogram_r), f'\nPython:\n{histogram_alt_python}\nR:\n{histogram_r}\n'


@pytest.mark.parametrize('k,p,r,ds', combs_k0_p_r_ds)
@pytest.mark.usefixtures('tweet_dataset')
def test_unique_tokens(k, p, r, ds, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with a given k, n, p, and ds (python)
    * Run the whistlerlib method with a given k, n, p, and ds (r)
    * Check that the token column has unique values 
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    histogram = tweet_dataset.mention_histogram_alt_python(k=k,
                                                           distributed_sorting=ds,
                                                           return_time_profile=False)

    # print(histogram['Mentions'])

    assert histogram['Mentions'].is_unique, f'\n{histogram}'


@pytest.mark.parametrize('k,p,ds', combs_k0_p_ds)
@pytest.mark.usefixtures('tweet_dataset')
def test_validate_mentions(k, p, ds, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with a given k, p, and ds    
    * Check that the mentions are valid    
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    histogram = tweet_dataset.mention_histogram_alt_python(k=k,
                                                           distributed_sorting=ds,
                                                           return_time_profile=False)
    for mention in histogram['Mentions']:
        validate_mention(mention)
