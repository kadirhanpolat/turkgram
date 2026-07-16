"""test_conjunction.py — Faz 5 D4 bağlaç runner."""
import pytest
from tests.golden_conjunction import (
    GOLDEN_CONJOIN, GOLDEN_COORDINATE, GOLDEN_ANALYZE, GOLDEN_ANALYZE_NEGATIVE
)
from turkgram.conjunction import conjoin, coordinate
from turkgram import analyze


@pytest.mark.parametrize("word,conj,expected", GOLDEN_CONJOIN)
def test_conjoin(word, conj, expected):
    assert conjoin(word, conj) == expected


@pytest.mark.parametrize("items,conj,expected", GOLDEN_COORDINATE)
def test_coordinate(items, conj, expected):
    assert coordinate(items, conj) == expected


def test_coordinate_empty_raises():
    with pytest.raises(ValueError):
        coordinate([], "ve")


def test_coordinate_unknown_conj_raises():
    with pytest.raises(ValueError):
        coordinate(["a", "b"], "xyz_bilinmeyen")


def test_conjoin_empty_raises():
    with pytest.raises(ValueError):
        conjoin("", "ve")


def test_conjoin_unknown_conj_raises():
    with pytest.raises(ValueError):
        conjoin("ev", "xyz_bilinmeyen")


def test_coordinate_correlative_three_raises():
    with pytest.raises(ValueError):
        coordinate(["a", "b", "c"], "hem_hem")


@pytest.mark.parametrize("surface,want_subset", GOLDEN_ANALYZE)
def test_analyze_conjunction(surface, want_subset):
    """want_subset ⊆ got (bilinçli belirsizlik: de = bağlaç + demek)."""
    results = analyze(surface)
    kinds = {a.kind for a in results}
    lemmas = {a.lemma for a in results}
    for item in want_subset:
        if "kind" in item:
            assert item["kind"] in kinds, f"{surface!r}: kind={item['kind']!r} bulunamadı. Bulunanlar: {kinds}"
        if "lemma" in item:
            assert item["lemma"] in lemmas, f"{surface!r}: lemma={item['lemma']!r} bulunamadı. Bulunanlar: {lemmas}"


@pytest.mark.parametrize("surface,banned_kind", GOLDEN_ANALYZE_NEGATIVE)
def test_analyze_no_conjunction(surface, banned_kind):
    """Tam-token guard: 'de'/'da' içeren kelimeler conjunction analizini DÖNDÜRMEZ."""
    results = analyze(surface)
    kinds = {a.kind for a in results}
    assert banned_kind not in kinds, f"{surface!r} yanlışlıkla {banned_kind!r} döndürdü"
