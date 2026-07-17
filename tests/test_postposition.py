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


def test_frozen_edat_raises_distinct_error():
    """dair/ilişkin/ait/yana donmuş — üretilemez, ayrı ValueError."""
    for edat in ("dair", "ilişkin", "ait", "yana"):
        with pytest.raises(ValueError, match="donmuş"):
            postposition("ev", edat)


def test_unknown_edat_lists_only_producible():
    """Bilinmeyen edat mesajındaki 'Geçerliler' donmuş edatları İÇERMEZ."""
    with pytest.raises(ValueError) as exc:
        postposition("ev", "zzz")
    msg = str(exc.value)
    assert "dair" not in msg and "ilişkin" not in msg
    assert "için" in msg


def test_new_edats_present_in_table():
    from turkgram.postposition import _POSTPOSITIONS
    assert set(_POSTPOSITIONS) >= {
        "dair", "ilişkin", "ait", "yana",
        "dek", "üzere", "başka", "aşkın",
    }
    assert _POSTPOSITIONS["dair"]["üretilebilir"] is False
    assert _POSTPOSITIONS["için"]["üretilebilir"] is True


def test_yonet_sets_preserve_pronoun_cases():
    """KRİTİK: ile/gibi/kadar zamir-genitifi korunur (üret'ten türetilmez)."""
    from turkgram.postposition import _POSTPOSITIONS
    assert _POSTPOSITIONS["ile"]["yönet"] == frozenset({"nom", "gen"})
    assert _POSTPOSITIONS["gibi"]["yönet"] == frozenset({"nom", "gen"})
    assert _POSTPOSITIONS["kadar"]["yönet"] == frozenset({"nom", "gen", "dat"})
