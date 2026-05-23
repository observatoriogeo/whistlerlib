import pandas as pd


def getHashtags(x):
    """Get the hashtags and its frequencies

    Parameters
     x: Series of text

    """
    hashtags = x.str.split(expand=True).stack()
    # Counting hashtags
    hashtagsF = hashtags[lambda x: x.str.startswith('#')].value_counts()
    # Return hashtags and it's frequency
    return hashtagsF


def get_hashtags_wrapper(df, text_column):

    x = df[text_column]
    histogram = getHashtags(x=x)

    histogram_df = pd.DataFrame(histogram)
    histogram_df = histogram_df.reset_index(level=0)
    histogram_df = histogram_df.rename(columns={'index': 'tag', 0: 'freq'})
    histogram_df['tag'] = histogram_df['tag'].str.strip()

    return histogram_df
