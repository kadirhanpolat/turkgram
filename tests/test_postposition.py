"""tests/test_postposition.py — Edat/ilgeç motor testleri (Faz 5 D2)."""
import pytest
from tests.golden_postposition import GOLDEN
from turkgram import postposition
import turkgram.tr as tr


@pytest.mark.parametrize(
    "case",
    GOLDEN,
    ids=[
        f"{g['lemma']}+{g['edat']}{'(bit)' if g.get('bitisik') else ''}"
        for g in GOLDEN
    ],
)
def test_postposition(case):
    result = postposition(case["lemma"], case["edat"], case.get("bitisik", False))
    assert result == case["expected"], (
        f"postposition({case['lemma']!r}, {case['edat']!r}, "
        f"bitişik={case.get('bitisik', False)}) = {result!r}, "
        f"beklenen {case['expected']!r}"
    )


def test_unknown_edat_raises():
    with pytest.raises(ValueError, match="Bilinmeyen edat"):
        postposition("ev", "xyz")


def test_bitisik_nonile_raises():
    with pytest.raises(ValueError, match="bitişik=True yalnız 'ile'"):
        postposition("ev", "için", bitişik=True)


def test_empty_lemma_raises():
    with pytest.raises(ValueError, match="lemma boş olamaz"):
        postposition("", "için")


def test_tr_edat_obeği_denklik():
    assert tr.edat_obeği("ev", "için") == postposition("ev", "için")
    assert tr.edat_obeği("ev", "ile", bitişik=True) == postposition("ev", "ile", bitişik=True)
    assert tr.edat_obeği("ben", "göre") == postposition("ben", "göre")
