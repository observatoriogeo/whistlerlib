from .funcs.mfhashtags import getMFHashtags
from .funcs.ngrams import getNgrams
from .funcs.sentiments import getSentiments
from .funcs.getmentions import getMentions
from ..base_algs import compute_vector_histogram, compute_matrix_nz_histogram_and_sum


SENTIMENT_META = {
    'text': 'object',
    'polarity': 'int64',
    'emotions.anger': 'int64',
    'emotions.anticipation': 'int64',
    'emotions.disgust': 'int64',
    'emotions.fear': 'int64',
    'emotions.joy': 'int64',
    'emotions.sadness': 'int64',
    'emotions.surprise': 'int64',
    'emotions.trust': 'int64',
    'emotions.negative': 'int64',
    'emotions.positive': 'int64'
}

SENTIMENT_COL_NAMES = {'emotions.anger': 'Anger', 'emotions.anticipation': 'Anticipation', 'emotions.disgust': 'Disgust', 'emotions.fear': 'Fear',  'emotions.joy': 'Joy',
                       'emotions.sadness': 'Sadness', 'emotions.surprise': 'Surprise', 'emotions.trust': 'Trust', 'emotions.negative': 'Negative',  'emotions.positive': 'Positive'}


def compute_hashtag_histogram(df, k, text_column, distributed_sorting, num_partitions):
    '''
    Distributed getMFHashtags (R): compute for each DF partition in the workers.
    df: A Dask DataFrame that has been already partitioned.
    '''
    return compute_vector_histogram(df=df,
                                    k=k,
                                    text_column=text_column,
                                    token_col='tag',
                                    freq_col='freq',
                                    distributed_sorting=distributed_sorting,
                                    num_partitions=num_partitions,
                                    # func
                                    func=getMFHashtags)


def compute_ngram_histogram(df, n, k, text_column, distributed_sorting, num_partitions):
    '''
    Distributed getNgrams (R): compute for each DF partition in the workers.
    df: A Dask DataFrame that has been already partitioned.
    '''
    return compute_vector_histogram(df=df,
                                    k=k,
                                    text_column=text_column,
                                    token_col='N_Tokens',
                                    freq_col='Freq',
                                    distributed_sorting=distributed_sorting,
                                    num_partitions=num_partitions,
                                    # func
                                    func=getNgrams,
                                    # func args
                                    n=n)


def compute_mention_histogram(df, k, text_column, distributed_sorting, num_partitions):
    '''
    Distributed getMentions (R): compute for each DF partition in the workers.
    df: A Dask DataFrame that has been already partitioned.
    '''
    return compute_vector_histogram(df=df,
                                    k=k,
                                    text_column=text_column,
                                    token_col='mentions',
                                    freq_col='Freq',
                                    distributed_sorting=distributed_sorting,
                                    num_partitions=num_partitions,
                                    # func
                                    func=getMentions)


def compute_sentiment_histogram_and_sum(df, text_column, language, method, num_partitions):
    return compute_matrix_nz_histogram_and_sum(df=df,
                                               text_column=text_column,
                                               meta=SENTIMENT_META,
                                               col_names=SENTIMENT_COL_NAMES,
                                               num_partitions=num_partitions,
                                               # func
                                               func=getSentiments,
                                               # func args
                                               language=language,
                                               method=method)
