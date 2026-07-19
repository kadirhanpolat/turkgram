"""Fiilimsi + çatı istifi çözümlemesi (yazdırma = yaz+CAUS+-mA).

Voiced verb gövdesi + fiilimsi (mA/mAk/DIk/AcAk…). Çatı+türetme emsali: voiced mastar
participle oracle'ına lemma verilir, KÖK fiil + voice_chain raporlanır. _in_voice_pass
re-entrancy guard (sonsuz özyineleme önlenir).
"""
import pytest
from turkgram.analysis import analyze

_ROOTS = {"yazmak", "okumak", "görmek", "sevmek", "gülmek", "bakmak"}


def _vp(surface):
    return [a for a in analyze(surface, roots=_ROOTS)
            if not a.hypothetical and a.kind == "participle" and a.kwargs.get("voice_chain")]


@pytest.mark.parametrize("surface,lemma,ptype,vc", [
    ("okutmak", "okumak", "mak", ("caus",)),
    ("yazdırma", "yazmak", "ma", ("caus",)),
    ("yazdırdığı", "yazmak", "dik", ("caus",)),
    ("sevişmek", "sevmek", "mak", ("recip",)),
    ("görüşme", "görmek", "ma", ("recip",)),
])
def test_voice_participle(surface, lemma, ptype, vc):
    hits = _vp(surface)
    assert any(a.lemma == lemma and a.kwargs.get("ptype") == ptype
               and a.kwargs.get("voice_chain") == vc for a in hits), \
        f"{surface}: {lemma}+{vc}+{ptype} bulunamadı. Alınan: {[(a.lemma, dict(a.kwargs)) for a in hits]}"


def test_voice_participle_no_spurious():
    """Düz fiilimsi/isim çatılı-fiilimsi üretmemeli."""
    for s in ["okuma", "yazdığı", "gelmek", "kitabı"]:
        assert not _vp(s), f"{s}: beklenmeyen çatı+fiilimsi"


def test_normal_participle_regression():
    """Normal (çatısız) fiilimsi DEĞİŞMEZ."""
    res = [a for a in analyze("okuma", roots={"okumak"})
           if not a.hypothetical and a.kind == "participle"]
    assert any(a.lemma == "okumak" and a.kwargs.get("ptype") == "ma" for a in res)
