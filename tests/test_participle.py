"""Fiilimsi + iyelik/durum istifi — golden koşucusu (Faz 1 / A3).

Golden `tests/golden_participle.py` motordan BAĞIMSIZ kuruldu. Anahtar: kind = ilk
parça; sonraki parçalar iyelik {1sg..3pl} veya durum {acc,dat,loc,abl,gen,ins}
(küme üyeliğiyle ayrılır).
"""
import pytest
from turkgram import nonfinite as nf

from tests.golden_participle import GOLDEN_PARTICIPLE

_PERSONS = {"1sg", "2sg", "3sg", "1pl", "2pl", "3pl"}
_CASES = {"nom", "acc", "dat", "loc", "abl", "gen", "ins"}

_ALL = [(v, k, form) for v, cells in GOLDEN_PARTICIPLE.items() for k, form in cells.items()]


def _call(verb: str, key: str) -> str:
    parts = key.split(".")
    kind = parts[0]
    possessive = case = None
    for tok in parts[1:]:
        if tok in _PERSONS:
            possessive = tok
        elif tok in _CASES:
            case = tok
        else:
            raise AssertionError(f"anahtar çözülemedi: {key}")
    return nf.participle(verb, kind, possessive=possessive, case=case)


@pytest.mark.parametrize("verb,key,expected", _ALL,
                         ids=[f"{v}:{k}" for v, k, _ in _ALL])
def test_golden_participle(verb, key, expected):
    assert _call(verb, key) == expected


def test_bilinmeyen_fiilimsi():
    with pytest.raises(ValueError):
        nf.participle("gelmek", "olmayan")
