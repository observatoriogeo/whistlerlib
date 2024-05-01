# pyright: reportMissingImports=false

import dask
from .funcs.getHashtags import get_hashtags_wrapper
from .funcs.getNgrams import get_ngrams_wrapper
from .funcs.getSentimentScore import get_sentiment_score_wrapper
from .funcs.getMentions import get_mentions_wrapper
from ..base_algs import compute_vector_histogram, compute_vector_range
from ...logger import logger


def compute_hashtag_histogram(df, k, text_column, distributed_sorting, num_partitions):
    '''
    Distributed getHashtags: compute for each DF partition in the workers.
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
                                    func=get_hashtags_wrapper)


def compute_ngram_histogram(df, n, k, lan, w, text_column, distributed_sorting, num_partitions):

    # locally download stopwords
    logger.debug(
        f"[whistler_dask.ngrams.alt_python.get_ngrams] downloading NLTK stop words ...")
    import nltk
    nltk.download('stopwords')
    stopwords = nltk.corpus.stopwords.words(lan)

    return compute_vector_histogram(df=df,
                                    k=k,
                                    text_column=text_column,
                                    token_col='N_Tokens',
                                    freq_col='Freq',
                                    distributed_sorting=distributed_sorting,
                                    num_partitions=num_partitions,
                                    # func
                                    func=get_ngrams_wrapper,
                                    # func args
                                    n=n,
                                    w=w,
                                    stopwords=stopwords)


def compute_sentiment_range_spanish(df, left_end, right_end, text_column, num_partitions):
    '''
    Distributed getSentimentScore: compute for each DF partition in the workers.
    df: A Dask DataFrame that has been already partitioned.
    '''

    # locally download stopwords
    logger.debug(
        f"[compute_sentiment_range_spanish] downloading NLTK stop words ...")
    import nltk
    nltk.download('stopwords')
    stopwords = nltk.corpus.stopwords.words('spanish')

    # locally load sentiment analysis model
    from sentiment_analysis_spanish import sentiment_analysis
    sentiment = sentiment_analysis.SentimentAnalysisSpanish()
    sentiment = dask.delayed(sentiment)

    return compute_vector_range(df,
                                left_end,
                                right_end,
                                text_column,
                                output_text_col='text',
                                output_score_col='score',
                                num_partitions=num_partitions,
                                # func
                                func=get_sentiment_score_wrapper,
                                # func args
                                stopwords=stopwords,
                                sentiment=sentiment)


def compute_mention_histogram(df, k, text_column, distributed_sorting, num_partitions):
    '''
    Distributed getMentions: compute for each DF partition in the workers.
    df: A Dask DataFrame that has been already partitioned.
    '''
    return compute_vector_histogram(df=df,
                                    k=k,
                                    text_column=text_column,
                                    token_col='Mentions',
                                    freq_col='Frequency',
                                    distributed_sorting=distributed_sorting,
                                    num_partitions=num_partitions,
                                    # func
                                    func=get_mentions_wrapper)
