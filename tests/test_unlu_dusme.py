"""Ünlü düşmesi (drops_vowel) kapsam genişletme runner.

Düşen sözcükler (ünlü-başlı ekte düşer, ünsüz-başlıda düşmez) + disharmonik front
+ DÜŞMEYEN kontrol grubu (false-drop yakalar). SPEC: 2026-07-19-unlu-dusme-kapsam.
"""
import pytest
from turkgram.morphology_noun import decline
from turkgram.analysis import analyze
from tests.golden_unlu_dusme import (
    UNLU_DUSME_CASES, UNLU_DUSME_NEGATIVE,
)


def _decline(lemma, key):
    if key == "poss3sg":
        return decline(lemma, possessive="3sg")
    return decline(lemma, case=key)


@pytest.mark.parametrize("case", UNLU_DUSME_CASES, ids=[c["lemma"] for c in UNLU_DUSME_CASES])
def test_unlu_dusme_generation(case):
    for key, exp in case.items():
        if key == "lemma":
            continue
        got = _decline(case["lemma"], key)
        assert got == exp, f"{case['lemma']} {key}: {got!r} != {exp!r}"


@pytest.mark.parametrize("case", UNLU_DUSME_NEGATIVE, ids=[c["lemma"] for c in UNLU_DUSME_NEGATIVE])
def test_unlu_dusme_negative(case):
    """DÜŞMEYEN kontrol grubu — false-drop regresyon."""
    for key, exp in case.items():
        if key == "lemma":
            continue
        got = _decline(case["lemma"], key)
        assert got == exp, f"{case['lemma']} {key} (DÜŞMEMELİ): {got!r} != {exp!r}"


@pytest.mark.parametrize("lemma,surface", [
    # harmonik düşme
    ("omuz", "omzuna"), ("zihin", "zihni"), ("nabız", "nabzı"),
    ("ilim", "ilmi"), ("beniz", "benzi"), ("şahıs", "şahsı"),
    # DİSHARMONİK düşme (2026-07-19: _root_candidates 4-ünlü ekleme ile ÇÖZÜLDÜ)
    ("nakil", "nakli"), ("haciz", "haczi"), ("kavim", "kavmi"), ("kavis", "kavsi"),
])
def test_unlu_dusme_analiz_roundtrip(lemma, surface):
    """Düşme analiz roundtrip (oracle + `_root_candidates` ünlü-restore). Disharmonik
    alıntılar (nakil→nakli) dahil: `_root_candidates` artık tüm yüksek ünlüleri (ı/i/u/ü)
    dener → ön 'nakil' restore edilir; precision roots+oracle garantili."""
    res = analyze(surface, roots={lemma})
    assert any(a.lemma == lemma and not a.hypothetical for a in res), \
        f"{surface} → {lemma} analizi bulunamadı"
