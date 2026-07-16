"""test_derivation_chain.py — zincirli türetme analizi runner."""
import pytest
from turkgram import analyze
from turkgram.lexicon import load as _load_lex

from .golden_derivation_chain import CHAIN_CASES, SEGMENTS_CASES

_ROOTS = _load_lex()


def _get_chain_result(surface: str, roots_modu: str) -> list:
    """max_depth=5 ile zincirli analiz; kind=derivation, chain dolu sonuçları döndür."""
    roots = _ROOTS if roots_modu == "precision" else None
    results = analyze(surface, roots=roots, max_derivation_depth=5)
    return [r for r in results if r.kind == "derivation" and r.chain]


@pytest.mark.parametrize(
    "surface,expected_root,chain_len,intermediate,roots_modu",
    CHAIN_CASES,
)
def test_chain_root(surface, expected_root, chain_len, intermediate, roots_modu):
    """En derin kök ve zincir uzunluğunu doğrula."""
    if chain_len == 1:
        pytest.skip("Tek katman — chain testi değil, _sal testi ayrıca kontrol eder")
    results = _get_chain_result(surface, roots_modu)
    assert results, f"{surface!r} için zincirli analiz bulunamadı"
    # En derin köke ulaşan sonucu bul
    found = [r for r in results if r.chain and r.chain[0].lemma == expected_root]
    assert found, (
        f"{surface!r} için kök={expected_root!r} bulunamadı. "
        f"Bulunan kökler: {[r.chain[0].lemma for r in results if r.chain]}"
    )
    best = found[0]
    assert len(best.chain) == chain_len, (
        f"Zincir uzunluğu: beklenen {chain_len}, bulunan {len(best.chain)}"
    )
    for lemma in intermediate:
        chain_lemmas = [a.lemma for a in best.chain]
        assert lemma in chain_lemmas, (
            f"Ara lemma {lemma!r} zincirde yok: {chain_lemmas}"
        )


def test_regression_max_depth_1():
    """max_depth=1 → chain boş (mevcut davranış korunur)."""
    results = analyze("gözlükçülük", roots=_ROOTS, max_derivation_depth=1)
    chain_results = [r for r in results if r.kind == "derivation" and r.chain]
    assert chain_results == [], "max_depth=1'de chain dolu olmamalı"


@pytest.mark.parametrize("surface,expected_root,expected_first_two", SEGMENTS_CASES)
def test_segments_flat(surface, expected_root, expected_first_two):
    """En derin kökün segments'inin ilk iki elemanını doğrula."""
    results = _get_chain_result(surface, "precision")
    assert results, f"{surface!r} için sonuç yok"
    # Beklenen köke göre filtrele (en derin zincirin segmentleri)
    found = [r for r in results if r.chain and r.chain[0].lemma == expected_root]
    if not found:
        found = results  # fallback: herhangi bir sonuç
    segs = list(found[0].segments)
    for i, (text, label) in enumerate(expected_first_two):
        assert segs[i].surface == text and segs[i].label == label, (
            f"segments[{i}]: beklenen ({text!r},{label!r}), "
            f"bulunan ({segs[i].surface!r},{segs[i].label!r})"
        )


def test_sal_single_layer():
    """-sAl eki tek katman analizi çalışıyor."""
    results = analyze("toplumsal", roots=_ROOTS)
    deriv = [r for r in results if r.kind == "derivation"]
    assert any(r.lemma == "toplum" for r in deriv), "toplumsal → toplum bulunamadı"
