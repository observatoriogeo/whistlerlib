
# Whistlerlib

**Whistlerlib** is a Python library developed at the CentroGeo Metropolitan Observatory, designed for distributed processing of large social media datasets. Utilizing data exploratory techniques in social network analysis (SNA) and natural language processing (NLP), Whistlerlib enables complex analyses on multi-core clusters.

## Features

Whistlerlib offers a variety of functions for analyzing social media data, including:

- Hashtag histograms
- Mention histograms
- N-gram histograms
- Sentiment polarity analysis
- Emotion analysis (fear, anger, joy, etc.)
- Weighted co-occurrence networks of hashtags
- Weighted co-occurrence networks of mentions

These functionalities are supported by distributed algorithms that operate on the Dask framework, optimizing performance on multi-core systems and computing clusters.

Whistlerlib accelerates several third-party libraries, which include:

- advertools: For extracting mentions.
- Syuzhet: For generating emotion and polarity scores.
- sentiment-analysis-spanish: For computing sentiment scores on Spanish datasets.

## Basic Usage

Here's a quick example of how to use Whistlerlib to analyze a Twitter dataset:

```python

from whistlerlib import Context

# create the Whistlerlib context and pass the IP and port of the Dask server
wl_context = Context('processes', '127.0.0.1', 8786)

# load a CSV file with X posts, and make 8 distributed partitions
dataset = wl_context.load_csv(filen='x_dataset.csv',
                              meta={
                                  'column_mapping': {
                                      'date_column': 'Date',
                                      'text_column': 'text'
                                  },
                                  'file_encoding': 'latin-1'
                              },
                              num_partitions=8)

# get the number of posts in a distributed fashion
posts_count = dataset.tweet_count()
print(f'Posts count: {posts_count}')

# compute the posts with sentiment scores between 0.9 and 0.95 in a distributed fashion
posts_with_scores = dataset.sentiment_range_spanish_alt_python(0.9, 0.95)
print(posts_with_scores)
```

## Development Status

**Please note:** Whistlerlib is currently under active development. This project is considered a work in progress, and it may undergo significant changes or improvements. We encourage users to wait for the first official release before utilizing this library for critical applications.


### Upcoming Releases

Upon completion, Whistlerlib will be available as a PyPi package, allowing for easy installation via pip. This will simplify the integration of Whistlerlib into existing Python environments and projects.


### Docker Support

For enhanced usability and deployment, Docker images will be provided for both the Dask scheduler and Dask workers. These images will come pre-configured with all necessary dependencies, ensuring a seamless setup for distributed computing environments.

Stay tuned for updates on release dates and additional features!


## License

Whistlerlib is distributed under the GPL-3 license. See the `LICENSE` file for more details.


## Contact

If you have specific questions about the project, you can contact the developers via [GitHub Issues](link_to_your_github_issues) or directly by email at [agarcia@centrogeo.edu.mx](mailto:agarcia@centrogeo.edu.mx).

---

For more information and updates, follow our project on GitHub.

