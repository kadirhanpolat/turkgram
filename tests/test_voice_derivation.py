"""Çatı + türetme istifi çözümlemesi (yazdırıcı = yaz+CAUS+-IcI).

Voiced verb gövdesi (leksikonda lemma DEĞİL) fiil→isim leksik türetme alır. Voiced gövde
conjugate/imp/voice_chain ile çözülür + türetme oracle. lemma=KÖK fiil, kwargs.voice_chain.
NOT: çatı+fiilimsi (-mA nominalizasyon, yazdırma) AYRI alt-sistem → kapsam dışı.
"""
import pytest
from turkgram.analysis import analyze

_ROOTS = {"yazmak", "görmek", "gülmek", "sevmek", "okumak", "bakmak", "gezmek"}


def _vd(surface):
    return [a for a in analyze(surface, roots=_ROOTS)
            if not a.hypothetical and a.kind == "derivation" and a.kwargs.get("voice_chain")]


@pytest.mark.parametrize("surface,lemma,suffix,vc", [
    ("yazdırıcı", "yazmak", "-IcI", ("caus",)),
    ("güldürücü", "gülmek", "-IcI", ("caus",)),
    ("gördürücü", "görmek", "-IcI", ("caus",)),
])
def test_voice_derivation(surface, lemma, suffix, vc):
    hits = _vd(surface)
    assert any(a.lemma == lemma and a.kwargs.get("suffix") == suffix
               and a.kwargs.get("voice_chain") == vc for a in hits), \
        f"{surface}: {lemma}+{vc}+{suffix} bulunamadı. Alınan: {[(a.lemma, dict(a.kwargs)) for a in hits]}"


def test_no_spurious_on_plain_noun():
    """Düz isim/fiil çatı+türetme üretmemeli (false-positive)."""
    for s in ["kitabı", "evler", "geldi", "okudu"]:
        assert not _vd(s), f"{s}: beklenmeyen çatı+türetme"
