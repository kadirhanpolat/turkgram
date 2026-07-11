"""Çatı (voice) — golden koşucusu (Faz 1 / A1).

Golden `tests/golden_voice.py` motordan BAĞIMSIZ kuruldu (SPEC + iki bağımsız
elle-türetme, %100 uyum). Anahtar: `<chain>.<tense>.<person>` (chain '+' ile
birleşik) veya `.neg.` olumsuz için.
"""
import pytest
from turkgram import morphology as m
from tests.golden_voice import GOLDEN_VOICE

_CASES = [(v, k, form) for v, cells in GOLDEN_VOICE.items() for k, form in cells.items()]


def _call(verb: str, key: str) -> str:
    parts = key.split(".")
    chain = parts[0].split("+")
    negative = "neg" in parts
    rest = [p for p in parts[1:] if p != "neg"]
    tense, person = rest[0], rest[1]
    return m.conjugate(verb, tense, person, voice_chain=chain, negative=negative)


@pytest.mark.parametrize("verb,key,expected", _CASES,
                         ids=[f"{v}:{k}" for v, k, _ in _CASES])
def test_golden_voice(verb, key, expected):
    assert _call(verb, key) == expected


def test_bilinmeyen_voice():
    with pytest.raises(ValueError, match="voice|çatı"):
        m.conjugate("gelmek", "past", "3sg", voice_chain=["olmayan"])
