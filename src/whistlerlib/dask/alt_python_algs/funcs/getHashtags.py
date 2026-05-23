

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
    # value_counts() returns a Series whose values are the counts and whose
    # index holds the unique items; rename the axis and the value column so
    # the resulting DataFrame has exactly the ['tag', 'freq'] columns the
    # downstream histogram code expects, regardless of pandas version.
    histogram_df = (
        getHashtags(x=x)
        .rename_axis('tag')
        .reset_index(name='freq')
    )
    histogram_df['tag'] = histogram_df['tag'].str.strip()

    return histogram_df
