"""Fiil-türevli çekim çözümlemesi (güzelleşti = güzel+-lAş+di).

isim→fiil türetilmiş fiil (leksikonda yok) çekilir. Çatı+fiilimsi emsali: türetilmiş
mastar conjugate oracle'a lemma verilir, KÖK + türetme etiketi raporlanır.
"""
import pytest
from turkgram.analysis import analyze

_ROOTS = {"güzel", "kör", "yeşil", "sarı", "temiz"}


def _dv(surface):
    return [a for a in analyze(surface, roots=_ROOTS)
            if not a.hypothetical and a.kind == "conjugate" and a.kwargs.get("derivation")]


@pytest.mark.parametrize("surface,lemma,tense", [
    ("güzelleşti", "güzel", "past"),
    ("körleşti", "kör", "past"),
    ("yeşilleşti", "yeşil", "past"),
    ("güzelleşiyor", "güzel", "pres"),
    ("güzelleşmiş", "güzel", "evid"),
])
def test_derived_verb_inflected(surface, lemma, tense):
    hits = _dv(surface)
    assert any(a.lemma == lemma and a.kwargs.get("tense") == tense
               and a.kwargs.get("derivation") == "-lAş-" for a in hits), \
        f"{surface}: {lemma}+-lAş+{tense} bulunamadı. Alınan: {[(a.lemma, dict(a.kwargs)) for a in hits]}"


def test_derived_verb_no_spurious():
    """Leksik fiil/isim türevli-çekim üretmemeli."""
    for s in ["geldi", "okudu", "kitabı"]:
        assert not [a for a in analyze(s, roots={"gelmek", "okumak", "kitap"})
                    if not a.hypothetical and a.kind == "conjugate" and a.kwargs.get("derivation")], s
