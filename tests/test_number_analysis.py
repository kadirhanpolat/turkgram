"""test_number_analysis.py — Sayı çözümleme testleri (Faz 5 D3).

Golden: tests/golden_number_analysis.py (motordan bağımsız, elle-doğrulanmış).
"""
from __future__ import annotations
import pytest
import turkgram as tg
from . import golden_number_analysis as G


@pytest.mark.parametrize(
    "case",
    G.GOLDEN,
    ids=[g["surface"] for g in G.GOLDEN],
)
def test_number_analysis(case):
    """Ordinal + distributif yüzey → doğru lemma + kind bulunmalı."""
    results = tg.analyze(case["surface"])
    found = [
        r for r in results
        if r.lemma == case["lemma"] and r.kind == case["kind"]
    ]
    assert found, (
        f"analyze({case['surface']!r}): "
        f"lemma={case['lemma']!r}, kind={case['kind']!r} bulunamadı. "
        f"Sonuçlar: {[(r.lemma, r.kind) for r in results]}"
    )
