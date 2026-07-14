"""test_adjective_analysis.py — Sıfat çözümleme testleri.

Golden: tests/golden_adjective_analysis.py (motordan bağımsız).
"""
from __future__ import annotations
import pytest
import turkgram as tg
from . import golden_adjective_analysis as G


# ---------------------------------------------------------------------------
# Pekiştirme round-trip
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("surface,roots,kind,lemma", G.INTENSIFY_ROUNDTRIP)
def test_intensify_analysis(surface, roots, kind, lemma):
    analyses = tg.analyze(surface, roots=roots)
    matching = [a for a in analyses if a.kind == kind and a.lemma == lemma]
    assert matching, (
        f"analyze({surface!r}, roots={set(roots)!r}): "
        f"kind={kind!r}, lemma={lemma!r} bulunamadı. "
        f"Adaylar: {[(a.kind, a.lemma) for a in analyses]}"
    )


# ---------------------------------------------------------------------------
# Küçültme round-trip
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("surface,roots,kind,lemma,suffix", G.DIMINUTIVE_ROUNDTRIP)
def test_diminutive_analysis(surface, roots, kind, lemma, suffix):
    analyses = tg.analyze(surface, roots=roots)
    matching = [
        a for a in analyses
        if a.kind == kind and a.lemma == lemma
        and a.kwargs.get("suffix") == suffix
    ]
    assert matching, (
        f"analyze({surface!r}, roots={set(roots)!r}): "
        f"kind={kind!r}, lemma={lemma!r}, suffix={suffix!r} bulunamadı. "
        f"Adaylar: {[(a.kind, a.lemma, a.kwargs) for a in analyses]}"
    )


# ---------------------------------------------------------------------------
# Precision: yanlış kök → intensify kind döndürmemeli
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("surface,roots", G.INTENSIFY_NO_RESULT)
def test_intensify_precision(surface, roots):
    analyses = tg.analyze(surface, roots=roots)
    intensify_hits = [a for a in analyses if a.kind == "intensify"]
    assert not intensify_hits, (
        f"analyze({surface!r}, roots={set(roots)!r}): "
        f"Yanlış kökle intensify bulundu: {intensify_hits}"
    )
