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
    ("omuz", "omzuna"), ("zihin", "zihni"), ("nabız", "nabzı"),
    ("ilim", "ilmi"), ("beniz", "benzi"), ("şahıs", "şahsı"),
])
def test_unlu_dusme_analiz_roundtrip(lemma, surface):
    """HARMONİK düşme: üretim düzelince analiz (oracle + _root_candidates restore) da bulur.

    NOT: DİSHARMONİK düşmeli alıntılar (nakil/haciz/kavim/kavis) analizde kaçar —
    `_root_candidates` harmonik ünlü-ekleme yapar (nakl→nakıl/nakul, ön 'nakil' değil);
    pre-existing sınır (CLAUDE.md §6d). Üretim (decline) DOĞRU; yalnız ters-analiz sınırlı.
    """
    res = analyze(surface, roots={lemma})
    assert any(a.lemma == lemma and not a.hypothetical for a in res), \
        f"{surface} → {lemma} analizi bulunamadı"
