"""Zarf-fiil (ulaç) — golden koşucusu (Faz 1 / A5).

Golden `tests/golden_nonfinite.py` motordan BAĞIMSIZ kuruldu; bu koşucu her
(fiil, kind) için `converb()` çağırır ve karşılaştırır.
"""
import pytest
from turkgram import nonfinite as nf
from tests.golden_nonfinite import GOLDEN_CONVERB

_CASES = [(v, k, form) for v, cells in GOLDEN_CONVERB.items() for k, form in cells.items()]


@pytest.mark.parametrize("verb,kind,expected", _CASES,
                         ids=[f"{v}:{k}" for v, k, _ in _CASES])
def test_golden_converb(verb, kind, expected):
    assert nf.converb(verb, kind) == expected


def test_bilinmeyen_ulac():
    with pytest.raises(ValueError):
        nf.converb("gelmek", "olmayan")
