"""test_interjection.py — ünlem + yansıma tanıma runner (SPEC §6).

Additive recognition → want ⊆ got. Homograf drift-lock: disambiguation tepe POS'u
ünlem/yansıma DEĞİL (öncelik 0; çekim/isim tepede).
"""
import pytest

from turkgram import analyze
from turkgram.interjection import INTERJECTIONS
from turkgram.onomatopoeia import ONOMATOPOEIA
from tests.golden_interjection import (
    GOLDEN_INTERJECTION, GOLDEN_ONOMATOPOEIA, GOLDEN_NORMALIZED,
    GOLDEN_AMBIGUOUS, GOLDEN_NEGATIVE,
)


def _has(surface, pos, kind, lemma):
    return any(
        a.pos == pos and a.kind == kind and a.lemma == lemma
        for a in analyze(surface)
    )


@pytest.mark.parametrize("surface,pos,kind,lemma", GOLDEN_INTERJECTION)
def test_interjection_recognized(surface, pos, kind, lemma):
    assert _has(surface, pos, kind, lemma)


@pytest.mark.parametrize("surface,pos,kind,lemma", GOLDEN_ONOMATOPOEIA)
def test_onomatopoeia_recognized(surface, pos, kind, lemma):
    assert _has(surface, pos, kind, lemma)


@pytest.mark.parametrize("surface,pos,kind,lemma", GOLDEN_NORMALIZED)
def test_normalized_recognized(surface, pos, kind, lemma):
    assert _has(surface, pos, kind, lemma)


@pytest.mark.parametrize("surface,kind", GOLDEN_AMBIGUOUS)
def test_ambiguous_additive(surface, kind):
    analyses = analyze(surface)
    # ünlem/yansıma okuması var
    assert any(a.kind == kind for a in analyses)
    # ama tek okuma değil (additive — başka okumalar da var)
    assert len(analyses) > 1


@pytest.mark.parametrize("surface", GOLDEN_NEGATIVE)
def test_negative_no_tag(surface):
    for a in analyze(surface):
        assert a.kind not in ("interjection", "onomatopoeia")


def test_sets_disjoint():
    """SPEC §4: iki kapalı küme ayrık kalmalı (bir yüzey tek sınıf)."""
    assert not (INTERJECTIONS & ONOMATOPOEIA)


@pytest.mark.parametrize("surface", ["of", "ay", "çat"])
def test_homograph_drift_lock(surface):
    """Homograf tepe okuması ünlem/yansıma DEĞİL (öncelik 0 → çekim/isim tepede)."""
    from turkgram import disambiguation
    ranked = disambiguation.rank(analyze(surface))
    top = ranked[0]
    assert top.kind not in ("interjection", "onomatopoeia")


def test_full_inventory_recognized():
    """Kümelerdeki HER üye kendi etiketiyle çözülür (kapsam güvencesi)."""
    for w in INTERJECTIONS:
        assert any(a.kind == "interjection" and a.lemma == w for a in analyze(w)), w
    for w in ONOMATOPOEIA:
        assert any(a.kind == "onomatopoeia" and a.lemma == w for a in analyze(w)), w
