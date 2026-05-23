from .cleanText import cleanText
import pandas as pd


def getNgrams(x, n, w, stopwords):
    """Get the n-grams and its frequencies

    Parameters
    x: Series of text
    n: Number of ngrams    
    w: level of analysis, this case "word" or "character"
    stopwords: stop words from NLTK

    """

    from sklearn.feature_extraction.text import CountVectorizer

    # Define ngrams
    word_vectorizer = CountVectorizer(ngram_range=(n, n), analyzer=w)
    # Get the clean text
    text = x.apply(cleanText, stopwords=stopwords)
    # Generate the matrix
    sparse_matrix = word_vectorizer.fit_transform(text)
    # Get the frequencies
    frequencies = sum(sparse_matrix).toarray()[0]
    # Set the ngrams and its frequencies in a dataframe
    ngramsF = pd.DataFrame(frequencies,
                           index=word_vectorizer.get_feature_names(),
                           columns=['Frequency'])
    return ngramsF


def get_ngrams_wrapper(df, text_column, n, w, stopwords):

    x = df[text_column]
    histogram = getNgrams(x=x, n=n, w=w, stopwords=stopwords)

    histogram_df = pd.DataFrame(histogram)
    histogram_df = histogram_df.reset_index(level=0)
    histogram_df = histogram_df.rename(
        columns={'index': 'N_Tokens', 'Frequency': 'Freq'})

    return histogram_df
