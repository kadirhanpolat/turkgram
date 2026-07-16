import pytest
from turkgram.normalization import (
    number_to_words, float_to_words, date_to_words,
    time_to_words, expand_abbreviation, normalize,
)
from tests.golden_normalization import (
    NUMBER_WORDS, FLOAT_WORDS, DATE_WORDS, TIME_WORDS, ABBREV, NORMALIZE,
)


@pytest.mark.parametrize("n,expected", NUMBER_WORDS)
def test_number_to_words(n, expected):
    assert number_to_words(n) == expected


@pytest.mark.parametrize("n,expected", FLOAT_WORDS)
def test_float_to_words(n, expected):
    assert float_to_words(n) == expected


@pytest.mark.parametrize("args,expected", DATE_WORDS)
def test_date_to_words(args, expected):
    assert date_to_words(*args) == expected


@pytest.mark.parametrize("args,expected", TIME_WORDS)
def test_time_to_words(args, expected):
    assert time_to_words(*args) == expected


@pytest.mark.parametrize("token,expected", ABBREV)
def test_expand_abbreviation(token, expected):
    assert expand_abbreviation(token) == expected


@pytest.mark.parametrize("text,expected", NORMALIZE)
def test_normalize(text, expected):
    assert normalize(text) == expected


def test_number_to_words_type_error():
    with pytest.raises(TypeError):
        number_to_words(3.14)


# TR API denklik testleri
import turkgram.tr as tr


def test_tr_sayiya_cevir():
    assert tr.sayıya_çevir(42) == number_to_words(42)


def test_tr_normallesir():
    assert tr.normalleştir("42 km yol") == normalize("42 km yol")


def test_tr_ipa():
    from turkgram.phonology import to_ipa
    assert tr.ipa("merhaba") == to_ipa("merhaba")
