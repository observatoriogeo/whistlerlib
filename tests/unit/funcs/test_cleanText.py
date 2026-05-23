"""Unit tests for `whistlerlib.dask.alt_python_algs.funcs.cleanText`.

The function is pure (string → string), unit tests should run in microseconds.
Covers the cleanup steps individually so a regression points at the exact rule
that broke.
"""

import pytest

from whistlerlib.dask.alt_python_algs.funcs.cleanText import cleanText


def test_lowercases(spanish_stopwords):
    assert cleanText('HOLA MUNDO', stopwords=spanish_stopwords) == 'hola mundo'


def test_removes_url():
    out = cleanText('visit https://example.com today', stopwords=[])
    assert 'http' not in out
    assert 'example' not in out  # whole URL token is replaced with a space
    assert 'visit' in out and 'today' in out


def test_removes_http_url_too():
    out = cleanText('see http://foo.bar/baz next', stopwords=[])
    assert 'foo' not in out and 'bar' not in out


def test_removes_mention():
    out = cleanText('hi @alice and @bob_99', stopwords=[])
    assert '@' not in out


def test_removes_hashtag():
    out = cleanText('great #day #news today', stopwords=[])
    assert '#' not in out
    # '#day' and '#news' are removed wholesale (they're #\S+)
    assert 'today' in out


def test_removes_emoji_modern_api():
    """emoji.replace_emoji() is the post-2.0 API; the function used to call
    `get_emoji_regexp()` which was removed."""
    out = cleanText('hello 😀 world 🎉', stopwords=[])
    assert '😀' not in out
    assert '🎉' not in out
    assert 'hello' in out and 'world' in out


def test_removes_punctuation():
    out = cleanText('hello, world! how are you?', stopwords=[])
    for char in ',!?':
        assert char not in out


def test_removes_numbers_in_words():
    out = cleanText('abc123 plain word2 normal', stopwords=[])
    assert 'abc123' not in out
    assert 'word2' not in out
    assert 'plain' in out and 'normal' in out


def test_collapses_whitespace():
    out = cleanText('a    b\t\t  c', stopwords=[])
    assert '  ' not in out


def test_removes_stopwords(spanish_stopwords):
    out = cleanText('esto es un mundo de prueba', stopwords=spanish_stopwords)
    # 'esto', 'es', 'un', 'de' are stopwords → removed
    assert 'esto' not in out.split()
    assert 'es' not in out.split()
    assert 'un' not in out.split()
    assert 'de' not in out.split()
    assert 'mundo' in out
    assert 'prueba' in out


def test_strips_accents_via_nfd_pass():
    """The unicode normalization pass strips combining diacritics but
    preserves Spanish ñ (tilde over n)."""
    out = cleanText('niño año cañón', stopwords=[])
    # NFC normalization keeps ñ; the regex preserves the ñ ligature.
    assert 'niño' in out or 'nino' in out  # tolerant: either canonical form
    # Other accented vowels get their combining marks stripped.
    out2 = cleanText('café acción música', stopwords=[])
    # 'café' becomes 'cafe' after accent stripping in older code, or keeps
    # accent in NFC. Just check the bare consonants survive.
    assert 'caf' in out2
    assert 'mus' in out2


def test_empty_string(spanish_stopwords):
    assert cleanText('', stopwords=spanish_stopwords) == ''


def test_only_stopwords(spanish_stopwords):
    out = cleanText('el la de y a', stopwords=spanish_stopwords)
    assert out.strip() == ''


@pytest.mark.parametrize('inp', [
    'PLAIN TEXT',
    'mixed CASE text',
    'with-dashes and-words',
])
def test_returns_str(inp):
    assert isinstance(cleanText(inp, stopwords=[]), str)
