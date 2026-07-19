"""Stacked -ki + çekim çözümlemesi (evdekileri = evde+ki+ler+i).

with_ki gövdesi (evdeki) durum/iyelik/çoğul alır. İki golden'lı özelliğin (with_ki +
decline) kompozisyonu — yeni morfoloji kuralı YOK. Dış çekim birincil (case/number/
possessive), -ki'nin ekseni ki_case/ki_possessive (case-çakışması önlenir).
"""
import pytest
from turkgram.analysis import analyze


def _ki(surface, roots):
    return [a for a in analyze(surface, roots=roots)
            if not a.hypothetical and a.kind == "with_ki"]


@pytest.mark.parametrize("surface,root,expect", [
    ("evdekiler",  "ev",   {"number": "pl", "ki_case": "loc"}),
    ("masadakini", "masa", {"possessive": "2sg", "case": "acc", "ki_case": "loc"}),
    ("içindekini", "iç",   {"possessive": "2sg", "case": "acc",
                            "ki_case": "loc", "ki_possessive": "3sg"}),
])
def test_ki_inflected(surface, root, expect):
    """Stacked -ki: beklenen eksen kümesi analizler arasında olmalı."""
    hits = _ki(surface, {root})
    assert any(dict(a.kwargs) == expect and a.lemma == root for a in hits), \
        f"{surface}: {expect} bulunamadı. Alınan: {[dict(a.kwargs) for a in hits]}"


def test_ki_inflected_ambiguity():
    """evdekileri belirsiz (poss3pl / pl+acc / pl+poss3sg) — hepsi ki_case:loc."""
    hits = _ki("evdekileri", {"ev"})
    kws = [dict(a.kwargs) for a in hits]
    assert all(k.get("ki_case") == "loc" for k in kws)
    assert len(kws) >= 2  # gerçek belirsizlik


def test_ki_bare_regression():
    """Çekimsiz saf with_ki DEĞİŞMEZ (evdeki→{case:loc}, ki_case anahtarı YOK)."""
    hits = _ki("evdeki", {"ev"})
    assert any(dict(a.kwargs) == {"case": "loc"} for a in hits)
