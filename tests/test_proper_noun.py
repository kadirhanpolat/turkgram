"""test_proper_noun.py — kural-tabanlı özel-ad etiketleme runner.

SPEC docs/superpowers/specs/2026-07-20-proper-noun-tagging-design.md §7.
"""
import pytest

from turkgram import lexicon
from turkgram import proper_noun as pn
from tests.golden_proper_noun import GOLDEN_PROPER

_ROOTS = lexicon.load()
_IDS = [g["text"] for g in GOLDEN_PROPER]


@pytest.mark.parametrize("g", GOLDEN_PROPER, ids=_IDS)
def test_tag(g):
    got = [(p.surface, p.type, p.index) for p in pn.tag(g["text"], roots=_ROOTS)]
    assert got == [tuple(t) for t in g["tags"]]


@pytest.mark.parametrize("surface,expected", [
    ("İstanbul", "LOC"), ("Ali", "PER"), ("TBMM", "ORG"),
    ("kitap", None), ("çocuk", None),
])
def test_proper_type_gazetteer(surface, expected):
    """Gazetteer konumdan bağımsız (cümle-başı olsa da)."""
    assert pn.proper_type(surface, sentence_initial=True) == expected


def test_proper_type_apostrophe():
    """Apostrof-ek → PROPER (cümle-başı OOV olsa da, kesin sinyal)."""
    assert pn.proper_type("Kadirhan'ın", sentence_initial=True) == "PROPER"


def test_proper_type_midsentence_caps():
    """Cümle-içi büyük harf → PROPER; cümle-başı OOV common→None / OOV→PROPER."""
    assert pn.proper_type("Kadirhan", sentence_initial=False) == "PROPER"
    assert pn.proper_type("Kadirhan", sentence_initial=True, is_common=True) is None
    assert pn.proper_type("Kadirhan", sentence_initial=True, is_common=False) == "PROPER"


def test_negative_lowercase():
    assert pn.proper_type("çocuk") is None
    assert pn.proper_type("kırmızı", sentence_initial=False) is None


def test_sentence_integration():
    """proper_noun gazetteer → sentence çıplak-tekil override (yer/kurum da özne)."""
    from turkgram.sentence import analyze_sentence
    for text, head in [("İstanbul güzeldi", "İstanbul"), ("Ankara başkenttir", "Ankara")]:
        sa = analyze_sentence(text, roots=_ROOTS)
        assert ("özne", (head,)) in [(e.label, e.tokens) for e in sa.elements]


def test_tr_api():
    from turkgram import tr
    a = tr.özel_adlar("Ali geldi", kökler=_ROOTS)
    b = pn.tag("Ali geldi", roots=_ROOTS)
    assert a == b


def test_roots_none_sentence_initial():
    """roots=None → cümle-başı OOV varsayılan PROPER (leksikon danışması yok)."""
    got = pn.tag("Kitap masada", roots=None)
    # roots yok → 'Kitap' ortak-ad bilinmiyor → PROPER (belgeli varsayılan)
    assert got and got[0].type == "PROPER"
