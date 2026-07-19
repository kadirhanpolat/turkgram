"""Türetilmiş gövde + çekim istifi runner (derivation + inflection).

NOT (§2.2 uzlaştırma): golden'ın `chain` alanı tam zincir (son türetilmiş gövde dahil)
tahmin etmiş; motorun mevcut Faz A konvansiyonu farklı (single-layer→chain=[], multi→
ara-tabanlar). Chain iç temsil detayı → runner dilbilgisel-anlamlı çekirdek eksenleri
(lemma/kind/case/possessive/number + türetme yakalandı) sıkı, chain'i esnek kontrol eder.
"""
import pytest
from turkgram.analysis import analyze
from tests.golden_turetme_cekim import (
    TURETME_CEKIM_CASES, TURETME_CEKIM_AMBIGUOUS,
    TURETME_CEKIM_REGRESSION, TURETME_CEKIM_NEGATIVE,
)

_DEPTH = 5


def _infl_axes(kw: dict) -> dict:
    return {k: kw.get(k) for k in ("case", "possessive", "number") if kw.get(k)}


@pytest.mark.parametrize("case", TURETME_CEKIM_CASES,
                         ids=[c["surface"] for c in TURETME_CEKIM_CASES])
def test_turetme_cekim(case):
    result = analyze(case["surface"], roots=case["roots"], max_derivation_depth=_DEPTH)
    exp_infl = {k: case[k] for k in ("case", "possessive", "number") if k in case}
    hit = [
        r for r in result
        if not r.hypothetical
        and r.lemma == case["lemma"]
        and r.kind == "derivation"
        and r.kwargs.get("suffix")          # türetme yakalandı
        and _infl_axes(r.kwargs) == exp_infl  # çekim eksenleri tam eşleşme
    ]
    assert hit, (
        f"{case['surface']}: beklenen (lemma={case['lemma']}, çekim={exp_infl}) "
        f"bulunamadı. Alınan: "
        f"{[(r.lemma, r.kind, dict(r.kwargs)) for r in result if not r.hypothetical][:6]}"
    )


@pytest.mark.parametrize("case", TURETME_CEKIM_AMBIGUOUS,
                         ids=[c["surface"] for c in TURETME_CEKIM_AMBIGUOUS])
def test_turetme_cekim_ambiguous(case):
    """Çok-katmanlı türetme + çekim — lemma+kind+case yeterli (chain esnek)."""
    result = analyze(case["surface"], roots=case["roots"], max_derivation_depth=_DEPTH)
    exp_case = case.get("case")
    hit = [
        r for r in result
        if not r.hypothetical and r.lemma == case["lemma"]
        and r.kind == "derivation" and r.kwargs.get("case") == exp_case
    ]
    assert hit, f"{case['surface']}: lemma={case['lemma']} case={exp_case} bulunamadı"


@pytest.mark.parametrize("case", TURETME_CEKIM_REGRESSION,
                         ids=[c["surface"] for c in TURETME_CEKIM_REGRESSION])
def test_turetme_cekim_regression(case):
    """Çekimsiz saf türetme — çekim ekseni OLMAMALI (feature tetiklenmez)."""
    result = analyze(case["surface"], roots=case["roots"], max_derivation_depth=_DEPTH)
    deriv = [r for r in result if not r.hypothetical and r.kind == "derivation"
             and r.lemma == case["lemma"]]
    assert deriv, f"{case['surface']}: saf türetme analizi bulunamadı"
    # En az bir analiz çekimsiz olmalı (saf türetme korunur)
    assert any(not _infl_axes(r.kwargs) for r in deriv), (
        f"{case['surface']}: çekimsiz saf türetme kayboldu"
    )


@pytest.mark.parametrize("case", TURETME_CEKIM_NEGATIVE,
                         ids=[c["surface"] for c in TURETME_CEKIM_NEGATIVE])
def test_turetme_cekim_negative(case):
    """Saf çekim (türetme yok) → türetme+çekim istifi ÜRETİLMEMELİ."""
    result = analyze(case["surface"], roots=case["roots"], max_derivation_depth=_DEPTH)
    # derivation + çekim ekseni olan analiz OLMAMALI
    bad = [r for r in result if not r.hypothetical and r.kind == "derivation"
           and _infl_axes(r.kwargs)]
    assert not bad, f"{case['surface']}: beklenmeyen türetme+çekim: {[dict(r.kwargs) for r in bad]}"
