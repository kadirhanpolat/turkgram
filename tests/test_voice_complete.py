"""Voice (çatı) analizi TAM — çok-katmanlı çatı × tüm kompozisyonlar (regresyon kilidi).

Voice analizi kapsamı (2026-07-19): çatı+çekim + çatı+türetme + çatı+fiilimsi, tek VE
çok-katmanlı (caus+caus, caus+pass, recip+caus). `_VOICE_CHAINS` çok-katmanı kapsar;
kompozisyonlar `_voiced_stem_root`→conjugate voice_chain'i miras alır. Yeni kod gerekmedi.
"""
import pytest
from turkgram.analysis import analyze

_ROOTS = {"yazmak", "okumak", "görmek", "sevmek", "gülmek"}


def _va(surface, kind=None):
    return [a for a in analyze(surface, roots=_ROOTS)
            if not a.hypothetical and a.kwargs.get("voice_chain")
            and (kind is None or a.kind == kind)]


@pytest.mark.parametrize("surface,lemma,vc,kind", [
    # çok-katmanlı çatı + çekim
    ("yazdırttı", "yazmak", ("caus", "caus"), "conjugate"),
    ("yazdırıldı", "yazmak", ("caus", "pass"), "conjugate"),
    ("seviştirdi", "sevmek", ("recip", "caus"), "conjugate"),
    ("yazdırttıracak", "yazmak", ("caus", "caus", "caus"), "conjugate"),
    # çok-katmanlı çatı + türetme
    ("yazdırttırıcı", "yazmak", ("caus", "caus", "caus"), "derivation"),
    # çok-katmanlı çatı + fiilimsi
    ("yazdırttırmak", "yazmak", ("caus", "caus", "caus"), "participle"),
])
def test_multilayer_voice(surface, lemma, vc, kind):
    hits = _va(surface, kind)
    assert any(a.lemma == lemma and a.kwargs.get("voice_chain") == vc for a in hits), \
        f"{surface}: {lemma}+{vc}+{kind} bulunamadı. Alınan: {[(a.lemma, a.kind, a.kwargs.get('voice_chain')) for a in hits]}"


@pytest.mark.parametrize("surface,kind", [
    ("yazdırdı", "conjugate"),   # çatı+çekim
    ("yazdırıcı", "derivation"), # çatı+türetme
    ("yazdırma", "participle"),  # çatı+fiilimsi
])
def test_single_voice_all_compositions(surface, kind):
    assert any(a.lemma == "yazmak" and a.kind == kind for a in _va(surface)), surface
