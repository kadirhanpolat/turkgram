"""Nominal ek-fiil (kopula) — golden koşucusu (Faz 1 / A4).

Golden `tests/golden_copula.py` motordan BAĞIMSIZ kuruldu; bu koşucu her anahtarı
parse edip `copula()` çağırır ve karşılaştırır (spec/copula-spec.md anahtar sözleşmesi).
"""
import pytest
from turkgram import morphology_noun as mn
from tests.golden_copula import GOLDEN_COPULA


def _call(word: str, key: str) -> str:
    parts = key.split(".")
    question = False
    if parts[0] == "soru":
        question = True
        parts = parts[1:]
    case = None
    if parts[0] == "loc":
        case = "loc"
        parts = parts[1:]
    tense, person = parts[0], parts[1]
    aux = None if tense == "pres" else tense
    return mn.copula(word, aux, person, case=case, question=question)


_CASES = [(w, k, v) for w, cells in GOLDEN_COPULA.items() for k, v in cells.items()]


@pytest.mark.parametrize("word,key,expected", _CASES,
                         ids=[f"{w}:{k}" for w, k, _ in _CASES])
def test_golden_copula(word, key, expected):
    assert _call(word, key) == expected
