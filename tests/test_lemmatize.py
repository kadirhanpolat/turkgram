"""Faz 9c — lemmatizer runner."""
import pytest
from tests.golden_lemmatize import LEMMATIZE_CASES, CORRECTED_CASES, TEXT_CASES


@pytest.mark.parametrize("surface,expected", LEMMATIZE_CASES)
def test_lemmatize(surface, expected):
    from turkgram.lemmatize import lemmatize
    assert lemmatize(surface) == expected


@pytest.mark.parametrize("surface,expected_lemma", CORRECTED_CASES)
def test_lemmatize_corrected_flag(surface, expected_lemma):
    from turkgram.lemmatize import lemmatize_detail
    result = lemmatize_detail(surface)
    assert result is not None
    assert result.lemma == expected_lemma
    assert result.corrected is True


@pytest.mark.parametrize("text,expected", TEXT_CASES)
def test_lemmatize_text(text, expected):
    from turkgram.lemmatize import lemmatize_text
    assert lemmatize_text(text) == expected


def test_lemma_result_frozen():
    from turkgram.lemmatize import LemmaResult
    r = LemmaResult(lemma="ev", pos="noun", confidence=0.9, corrected=False)
    with pytest.raises(Exception):
        r.lemma = "araba"  # type: ignore


def test_lemma_result_confidence_is_float():
    from turkgram.lemmatize import lemmatize_detail
    result = lemmatize_detail("geliyorum")
    assert result is not None
    assert isinstance(result.confidence, float)


def test_lemmatize_empty_raises():
    from turkgram.lemmatize import lemmatize
    with pytest.raises(ValueError):
        lemmatize("")


def test_lemmatize_text_empty_raises():
    from turkgram.lemmatize import lemmatize_text
    with pytest.raises(ValueError):
        lemmatize_text("")


def test_lemmatize_detail_empty_raises():
    from turkgram.lemmatize import lemmatize_detail
    with pytest.raises(ValueError):
        lemmatize_detail("")


def test_lemmatize_text_detail_empty_raises():
    from turkgram.lemmatize import lemmatize_text_detail
    with pytest.raises(ValueError):
        lemmatize_text_detail("")


def test_tr_api_equivalence():
    import turkgram.tr as tr
    from turkgram.lemmatize import lemmatize
    for word in ["geliyorum", "evlerde", "bana"]:
        assert tr.temel_biçim(word) == lemmatize(word)


def test_tr_api_metin_equivalence():
    import turkgram.tr as tr
    from turkgram.lemmatize import lemmatize_text
    text = "Ali eve geldi"
    assert tr.temel_biçim_metin(text) == lemmatize_text(text)
