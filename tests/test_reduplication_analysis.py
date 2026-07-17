"""test_reduplication_analysis.py — Faz 9d ikileme analiz testleri.

Golden: tests/golden_reduplication_analysis.py (motordan bağımsız).
"""
from __future__ import annotations

import pytest
import turkgram as tg
from turkgram import lexicon

from . import golden_reduplication_analysis as G

# Leksikonu bir kez yükle (ulaç testleri için)
ROOTS = lexicon.load()


# ---------------------------------------------------------------------------
# 1. Tam ikileme analizi (roots={lemma})
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("entry", G.GOLDEN_FULL_ANALYSIS)
def test_full_reduplication_analysis(entry):
    surface = entry["surface"]
    roots = {entry["lemma"]}
    results = tg.analyze(surface, roots=roots)
    matched = [
        r for r in results
        if r.kind == "reduplication_full" and r.lemma == entry["lemma"]
    ]
    assert matched, (
        f"analyze({surface!r}, roots={roots!r}): "
        f"reduplication_full + lemma={entry['lemma']!r} bulunamadı. "
        f"Adaylar: {[(r.kind, r.lemma) for r in results]}"
    )
    if entry["pos"] is not None:
        assert matched[0].pos == entry["pos"], (
            f"Beklenen pos={entry['pos']!r}, gerçek pos={matched[0].pos!r} "
            f"({surface!r})"
        )


# ---------------------------------------------------------------------------
# 2. Ulaç ikilemesi analizi (roots=ROOTS — leksikon ile)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("entry", G.GOLDEN_CONVERB_ANALYSIS)
def test_converb_reduplication_analysis(entry):
    surface = entry["surface"]
    results = tg.analyze(surface, roots=ROOTS)
    matched = [
        r for r in results
        if r.kind == "reduplication_converb" and r.lemma == entry["lemma"]
    ]
    assert matched, (
        f"analyze({surface!r}, roots=ROOTS): "
        f"reduplication_converb + lemma={entry['lemma']!r} bulunamadı. "
        f"Adaylar: {[(r.kind, r.lemma) for r in results]}"
    )
    assert matched[0].pos == "verb", (
        f"Beklenen pos='verb', gerçek pos={matched[0].pos!r} ({surface!r})"
    )


# ---------------------------------------------------------------------------
# 3. M-ikilemesi analizi (roots={lemma})
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("entry", G.GOLDEN_M_ANALYSIS)
def test_m_reduplication_analysis(entry):
    surface = entry["surface"]
    roots = {entry["lemma"]}
    results = tg.analyze(surface, roots=roots)
    matched = [
        r for r in results
        if r.kind == "reduplication_m" and r.lemma == entry["lemma"]
    ]
    assert matched, (
        f"analyze({surface!r}, roots={roots!r}): "
        f"reduplication_m + lemma={entry['lemma']!r} bulunamadı. "
        f"Adaylar: {[(r.kind, r.lemma) for r in results]}"
    )
    if entry["pos"] is not None:
        assert matched[0].pos == entry["pos"], (
            f"Beklenen pos={entry['pos']!r}, gerçek pos={matched[0].pos!r} "
            f"({surface!r})"
        )


# ---------------------------------------------------------------------------
# 4. roots=None → converb analizi OLMAMALI
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("surface", G.GOLDEN_ROOTS_NONE)
def test_converb_skipped_without_roots(surface):
    results = tg.analyze(surface, roots=None)
    converb_results = [r for r in results if r.kind == "reduplication_converb"]
    assert not converb_results, (
        f"analyze({surface!r}, roots=None): "
        f"Beklenmedik reduplication_converb bulundu: {converb_results}"
    )


# ---------------------------------------------------------------------------
# 5. TR API denklik testleri
# ---------------------------------------------------------------------------
def test_tr_api_tam_ikile():
    from turkgram.tr import tam_ikile
    from turkgram.reduplication import full_reduplicate

    assert tam_ikile("yavaş") == full_reduplicate("yavaş")
    # _tr_lower: büyük harf normalleştirmesi
    assert tam_ikile("GÜZEL") == full_reduplicate("güzel")


def test_tr_api_ulac_ikile():
    from turkgram.tr import ulaç_ikile
    from turkgram.reduplication import converb_reduplicate

    assert ulaç_ikile("koşmak") == converb_reduplicate("koşmak")


def test_tr_api_m_ikile():
    from turkgram.tr import m_ikile
    from turkgram.reduplication import m_reduplicate

    assert m_ikile("kitap") == m_reduplicate("kitap")
