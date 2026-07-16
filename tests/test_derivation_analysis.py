"""Yapım eki analizi runner — golden_derivation_analysis.py karşı doğrular.

Bilinen motor sınırı (xfail):
  meslektaş: Türkçede lexikalize düzensiz biçim. Gerçek sözcük 'meslektaş' iken
  motoru düzenli 4'lü uyumla 'meslekteş' üretir (meslek son ünlü e → ön → -teş).
  Bu bir motor açığıdır (leksik istisna); golden doğrudur, motor düzensizi kapsamaz.
"""

import pytest
from turkgram.analysis import analyze
from turkgram.lexicon import load

from tests.golden_derivation_analysis import GOLDEN_ANALYSIS

# Motor tarafından üretilemeyen bilinen düzensiz/leksikalize biçimler
_KNOWN_ENGINE_GAPS: set[str] = {
    "meslektaş",  # Düzenli harmoni: meslekteş (e→ön); gerçek sözcük: meslektaş (leksik istisna)
}


@pytest.fixture(scope="module")
def roots():
    return load()


@pytest.mark.parametrize(
    "surface,expected_lemma,expected_pos,expected_suffix,expected_src_pos",
    GOLDEN_ANALYSIS,
    ids=[entry[0] for entry in GOLDEN_ANALYSIS],
)
def test_derivation_golden(
    roots,
    surface: str,
    expected_lemma: str,
    expected_pos: str,
    expected_suffix: str,
    expected_src_pos: str,
) -> None:
    """Her golden girişi için türetme analizinin sonuçlar listesinde olduğunu doğrular."""
    if surface in _KNOWN_ENGINE_GAPS:
        pytest.xfail(f"{surface!r}: bilinen motor açığı (leksik düzensiz biçim, golden doğru)")

    # Lemma leksikonda yoksa genişletilmiş root kümesi kullan
    extended_roots = roots | {expected_lemma}

    results = analyze(surface, roots=extended_roots)

    derivation_hits = [
        a
        for a in results
        if a.kind == "derivation"
        and a.lemma == expected_lemma
        and a.pos == expected_pos
        and a.kwargs.get("suffix") == expected_suffix
        and a.kwargs.get("src_pos") == expected_src_pos
    ]

    assert derivation_hits, (
        f"analyze({surface!r}) içinde beklenen türetme analizi bulunamadı:\n"
        f"  lemma={expected_lemma!r}, pos={expected_pos!r}, "
        f"suffix={expected_suffix!r}, src_pos={expected_src_pos!r}\n"
        f"  Mevcut sonuçlar: {results}"
    )


def test_derivation_pos_filter(roots: set) -> None:
    """pos='conj' filtresiyle türetme adımı hiç çalışmaz; derivation sonucu gelmemeli.

    analyze() pos='conj' olduğunda _try_derivation_all çağrılmaz (koşul:
    pos in (None, 'noun', 'verb', 'adj')).
    """
    results = analyze("gözlük", pos="conj", roots=roots)
    derivation_hits = [a for a in results if a.kind == "derivation"]
    assert not derivation_hits, (
        f"pos='conj' filtresiyle türetme analizi beklenmiyordu: {derivation_hits}"
    )


def test_derivation_hypothetical_false(roots: set) -> None:
    """roots ile hypothetical=False analizi beklenir (gözlük güvenilir leksikonda)."""
    extended_roots = roots | {"göz"}
    results = analyze("gözlük", roots=extended_roots)
    derivation_hits = [a for a in results if a.kind == "derivation"]
    assert derivation_hits, "roots ile 'gözlük' için türetme analizi beklendi"
    # roots sağlandığında hypothetical=False olmalı
    assert all(not a.hypothetical for a in derivation_hits), (
        f"roots sağlandığında hypothetical=True beklenmiyordu: {derivation_hits}"
    )


def test_derivation_hypothetical_true() -> None:
    """roots=None (hypothetical mod) ile türetme analizi hypothetical=True olmalı."""
    results = analyze("gözlük", roots=None)
    derivation_hits = [a for a in results if a.kind == "derivation"]
    if derivation_hits:
        assert all(a.hypothetical for a in derivation_hits), (
            f"roots=None ile hypothetical=True beklendi: {derivation_hits}"
        )
