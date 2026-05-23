#TODO: check graph weights?

import pytest
from .conftest import P, combs_p_r, validate_mention, validate_graph


@pytest.mark.parametrize('p', P)
@pytest.mark.usefixtures('tweet_dataset')
def test_not_null_graph(p, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with a given p >= 1
    * Check that the number of nodes of the resulting graph is > 0
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    _, graph = tweet_dataset.mention_weighted_coonet()

    assert graph.vcount() > 0


@pytest.mark.parametrize('p', P)
@pytest.mark.usefixtures('tweet_dataset')
def test_not_empty_graph(p, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with a given p >= 1            
    * Check that the number of rows of the resulting DataFrame is > 0
    * Check that the number of edges of the resulting graph is > 0    
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    _, graph = tweet_dataset.mention_weighted_coonet()

    assert graph.ecount() > 0


@pytest.mark.parametrize('p', P)
@pytest.mark.usefixtures('tweet_dataset')
def test_not_empty_df(p, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with a given p >= 1            
    * Check that the number of rows of the resulting DataFrame is > 0
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    graph_df, _ = tweet_dataset.mention_weighted_coonet()

    assert len(graph_df.index) > 0


@pytest.mark.parametrize('p', P)
@pytest.mark.usefixtures('tweet_dataset', 'tweet_dataset_p1')
def test_p1_eq_plt1_graph(p, tweet_dataset, tweet_dataset_p1):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Check that the dataset with p = 1 has indeed only one partition
    * Run the whistlerlib method with p = 1        
    * Run the whistlerlib method with p > 1        
    * Check that the number of graph nodes of the two runs are identical
    * Check that the number of graph edges of the two runs are identical
    * Check that the degree lists of the two runs are identical
    Note: checking that the two graphs are isomorphic would be the ideal, but it is computationally hard
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p
    assert tweet_dataset_p1.get_num_partitions() == 1

    _, graph_plt1 = tweet_dataset.mention_weighted_coonet()
    _, graph_p1 = tweet_dataset_p1.mention_weighted_coonet()

    assert graph_plt1.vcount() == graph_p1.vcount()
    assert graph_plt1.ecount() == graph_p1.ecount()
    assert graph_plt1.degree() == graph_p1.degree()


@pytest.mark.parametrize('p', P)
@pytest.mark.usefixtures('tweet_dataset', 'tweet_dataset_p1')
def test_p1_eq_plt1_df(p, tweet_dataset, tweet_dataset_p1):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Check that the dataset with p = 1 has indeed only one partition
    * Run the whistlerlib method with p = 1        
    * Run the whistlerlib method with p > 1    
    * Check that the graph DFs of the two runs are identical 
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p
    assert tweet_dataset_p1.get_num_partitions() == 1

    graph_df_plt1, _ = tweet_dataset.mention_weighted_coonet()
    graph_df_p1, _ = tweet_dataset_p1.mention_weighted_coonet()

    assert graph_df_plt1.equals(graph_df_p1)


@pytest.mark.parametrize('p,r', combs_p_r)
@pytest.mark.usefixtures('tweet_dataset')
def test_reps_graph(p, r, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with p >= 1
    * Run again the whistlerlib method with the same p
    * Check that the number of graph nodes of the two runs are identical
    * Check that the number of graph edges of the two runs are identical
    * Check that the degree lists of the two runs are identical
    Note: checking that the two graphs are isomorphic would be the ideal, but it is computationally hard
    Note: r is just the number of test repetition and not actually used inside the test
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    _, graph = tweet_dataset.mention_weighted_coonet()
    _, graph_rep = tweet_dataset.mention_weighted_coonet()

    assert graph_rep.vcount() == graph.vcount()
    assert graph_rep.ecount() == graph.ecount()
    assert graph_rep.degree() == graph.degree()


@pytest.mark.parametrize('p,r', combs_p_r)
@pytest.mark.usefixtures('tweet_dataset')
def test_reps_df(p, r, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with p >= 1
    * Run again the whistlerlib method with the same p
    * Check that the graph DFs of the two runs are identical  
    Note: r is just the number of test repetition and not actually used inside the test
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    graph_df, _ = tweet_dataset.mention_weighted_coonet()
    graph_df_rep, _ = tweet_dataset.mention_weighted_coonet()

    assert graph_df_rep.equals(graph_df)


@pytest.mark.parametrize('p', P)
@pytest.mark.usefixtures('tweet_dataset')
def test_validate_mentions(p, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with a given p
    * Check that the mentions in the graph's nodes are valid
    * Check that the mentions in the DataFrame's source and target columns are valid    
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    graph_df, graph = tweet_dataset.mention_weighted_coonet(return_time_profile=False)
    
    for node in graph.vs:
        node_mention = node['name']
        validate_mention(node_mention)

    for _, row in graph_df.iterrows():
        source_mention = row['source']
        target_mention = row['target']
        validate_mention(source_mention)
        validate_mention(target_mention)
        

@pytest.mark.parametrize('p', P)
@pytest.mark.usefixtures('tweet_dataset')
def test_validate_weights(p, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with a given p
    * Check that the weights in the graph's edges are valid
    * Check that the weights in the DataFrame's are valid    
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    graph_df, graph = tweet_dataset.mention_weighted_coonet(return_time_profile=False)
    
    for edge in graph.es:
        assert edge['weight'] > 0

    for _, row in graph_df.iterrows():
        assert row['weight'] > 0


@pytest.mark.parametrize('p', P)
@pytest.mark.usefixtures('tweet_dataset')
def test_validate_graph(p, tweet_dataset):
    ''' Scenario:
    * Repartition the dataset if needed
    * Check that the partitioning was successful
    * Run the whistlerlib method with a given p
    * Validate the returned graph against the returned DataFrame    
    '''

    if p > 1:
        tweet_dataset.repartition(p)
    assert tweet_dataset.get_num_partitions() == p

    graph_df, graph = tweet_dataset.mention_weighted_coonet(return_time_profile=False)
    
    validate_graph(graph_df, graph)

