# -*- coding: utf-8 -*-

def getMentions(x):
    import advertools as adv
    import pandas as pd

    """Extract mentions @ of a text.
    
    Parameters
     x: Dataframe of text #TODO: x is a string: confirm with Angelina
    df_mentions: a list of mentions
     
    """

    # Get all data about mentions
    mention_summary = adv.extract_mentions(x)
    # Asigning to a variable
    # TODO: replace with 'mentions' in order to get all mentions?
    mention_list = mention_summary['top_mentions']
    # Convert into a dataframe
    df_mentions = pd.DataFrame(mention_list, columns=['Mentions', 'Frequency'])
    # Return a value
    return df_mentions


def get_mentions_wrapper(df, text_column):

    x = df[text_column]
    histogram_df = getMentions(x=x)

    return histogram_df
