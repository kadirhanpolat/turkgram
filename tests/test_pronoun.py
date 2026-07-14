"""test_pronoun.py — Zamir çekim testleri (SPEC pronoun-spec.md).

Golden: tests/golden_pronoun.py (motordan bağımsız, elle-doğrulanmış).
"""
from __future__ import annotations
import pytest
import turkgram as tg
from . import golden_pronoun as G


# ---------------------------------------------------------------------------
# §P1-P2 — Suppletif çoğul
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("lemma,number,possessive,case,expected", G.SUPPLETIVE_PLURAL)
def test_suppletive_plural(lemma, number, possessive, case, expected):
    got = tg.decline(lemma, number=number, possessive=possessive, case=case)
    assert got == expected, f"decline({lemma!r}, number={number!r}, case={case!r}) -> {got!r}, beklenen {expected!r}"


# ---------------------------------------------------------------------------
# §P3 — hepsi (n-gövde)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("lemma,number,possessive,case,expected", G.HEPSI)
def test_hepsi(lemma, number, possessive, case, expected):
    got = tg.decline(lemma, number=number, possessive=possessive, case=case)
    assert got == expected, f"decline({lemma!r}, case={case!r}) -> {got!r}, beklenen {expected!r}"


# ---------------------------------------------------------------------------
# §P4 — kendi (dönüşlü, n-gövde)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("lemma,number,possessive,case,expected", G.KENDI)
def test_kendi(lemma, number, possessive, case, expected):
    got = tg.decline(lemma, number=number, possessive=possessive, case=case)
    assert got == expected, f"decline({lemma!r}, case={case!r}) -> {got!r}, beklenen {expected!r}"


# ---------------------------------------------------------------------------
# §P6-P8 — Diğer n-gövde zamirleri
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("lemma,number,possessive,case,expected", G.N_STEM_OTHERS)
def test_n_stem_others(lemma, number, possessive, case, expected):
    got = tg.decline(lemma, number=number, possessive=possessive, case=case)
    assert got == expected, f"decline({lemma!r}, case={case!r}) -> {got!r}, beklenen {expected!r}"


# ---------------------------------------------------------------------------
# §P5 — herkes (düzenli, doğrulama)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("lemma,number,possessive,case,expected", G.HERKES)
def test_herkes(lemma, number, possessive, case, expected):
    got = tg.decline(lemma, number=number, possessive=possessive, case=case)
    assert got == expected, f"decline({lemma!r}, case={case!r}) -> {got!r}, beklenen {expected!r}"


# ---------------------------------------------------------------------------
# Regresyon — mevcut doğru zamir çekimleri bozulmadı
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("lemma,number,possessive,case,expected", G.REGRESSION)
def test_regression(lemma, number, possessive, case, expected):
    got = tg.decline(lemma, number=number, possessive=possessive, case=case)
    assert got == expected, f"decline({lemma!r}, number={number!r}, case={case!r}) -> {got!r}, beklenen {expected!r}"


# ---------------------------------------------------------------------------
# Round-trip — analyze çözümlemesi
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("surface,roots,kind,kwargs_subset", G.ROUNDTRIP)
def test_roundtrip(surface, roots, kind, kwargs_subset):
    analyses = tg.analyze(surface, roots=roots)
    matching = [a for a in analyses if a.kind == kind
                and all(a.kwargs.get(k) == v for k, v in kwargs_subset.items())]
    assert matching, (
        f"analyze({surface!r}, roots={set(roots)!r}): "
        f"kind={kind!r}, kwargs⊇{kwargs_subset!r} bulunamadı. "
        f"Adaylar: {analyses}"
    )
