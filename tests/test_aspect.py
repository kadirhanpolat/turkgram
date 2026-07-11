"""Tasvir fiilleri (aktionsart) — golden koşucusu (Faz 1 / A2).

Golden `tests/golden_aspect.py` motordan BAĞIMSIZ kuruldu. Anahtar:
`<aspect>.<tense>.<person>` veya `<aspect>.<tense>.neg.<person>`.
"""
import pytest
from turkgram import morphology as m
from tests.golden_aspect import GOLDEN_ASPECT

_CASES = [(v, k, form) for v, cells in GOLDEN_ASPECT.items() for k, form in cells.items()]


def _call(verb: str, key: str) -> str:
    parts = key.split(".")
    aspect = parts[0]
    negative = "neg" in parts
    parts = [p for p in parts[1:] if p != "neg"]
    tense, person = parts[0], parts[1]
    return m.conjugate(verb, tense, person, aspect=aspect, negative=negative)


@pytest.mark.parametrize("verb,key,expected", _CASES,
                         ids=[f"{v}:{k}" for v, k, _ in _CASES])
def test_golden_aspect(verb, key, expected):
    assert _call(verb, key) == expected


def test_bilinmeyen_aspect():
    with pytest.raises(ValueError, match="aspect"):
        m.conjugate("gelmek", "pres", "3sg", aspect="olmayan")
