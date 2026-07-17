"""test_reduplication.py — Faz 9d ikileme üretim testleri."""
import pytest
from turkgram.reduplication import full_reduplicate, converb_reduplicate, m_reduplicate
from tests.golden_reduplication import GOLDEN_FULL, GOLDEN_CONVERB, GOLDEN_M, GOLDEN_M_ERROR


@pytest.mark.parametrize("word,expected", GOLDEN_FULL)
def test_full_reduplicate(word: str, expected: str) -> None:
    assert full_reduplicate(word) == expected


@pytest.mark.parametrize("lemma,expected", GOLDEN_CONVERB)
def test_converb_reduplicate(lemma: str, expected: str) -> None:
    assert converb_reduplicate(lemma) == expected


@pytest.mark.parametrize("word,expected", GOLDEN_M)
def test_m_reduplicate(word: str, expected: str) -> None:
    assert m_reduplicate(word) == expected


@pytest.mark.parametrize("word", GOLDEN_M_ERROR)
def test_m_reduplicate_m_initial_error(word: str) -> None:
    with pytest.raises(ValueError):
        m_reduplicate(word)


def test_empty_string_raises() -> None:
    with pytest.raises(ValueError):
        full_reduplicate("")
    with pytest.raises(ValueError):
        converb_reduplicate("")
    with pytest.raises(ValueError):
        m_reduplicate("")
