def cleanText(x, stopwords):
    """Remove unnecesary elements of the text

    Parameters
     x: Series of text
     lan: language

    """

    import string
    import re
    # import nltk
    import emoji
    from unicodedata import normalize

    # Change to lower
    x = x.lower()
    # Remove emojis
    x = re.sub(emoji.get_emoji_regexp(), r"", x)
    # Extra u
    x = re.sub(r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+",
               r"\1", normalize("NFD", x), 0, re.I)
    # Data normalization(remove acents and unicode characters)
    x = normalize('NFC', x)
    # Remove URL
    x = re.sub(r'https*\S+', ' ', x)
    # Remove mentions
    x = re.sub(r'@\S+', ' ', x)
    # Remove Hashtags
    x = re.sub(r'#\S+', ' ', x)
    # Remove ticks and the next character
    x = re.sub(r'\'\w+', '', x)
    # Remove punctuations
    x = re.sub('[%s]' % re.escape(string.punctuation), ' ', x)
    # Remove numbers
    x = re.sub(r'\w*\d+\w*', '', x)
    # Replace the over spaces
    x = re.sub(r'\s{2,}', ' ', x)
    # Remove stopwords
    x = ' '.join([word for word in x.split(' ') if word not in stopwords])
    return x
