from .cleanText import cleanText


def getSentimentScore(x, stopwords, sentiment):
    """Get the sentiment score of text by rows.
     Parameters
     x: Series of text
     stopwords: stop words from NLTK          
    """
    x = x.apply(cleanText, stopwords=stopwords)
    y = x.apply(lambda i: sentiment.sentiment(i))
    x = x.to_frame()
    x['Score Sentiment'] = y
    return x


def get_sentiment_score_wrapper(df, text_column, stopwords, sentiment):

    x = df[text_column]
    scores_df = getSentimentScore(
        x=x, stopwords=stopwords, sentiment=sentiment)
    scores_df = scores_df.rename(
        columns={'text': 'text', 'Score Sentiment': 'score'})  # TODO: may skip this step

    return scores_df
