"""test_clause.py — yargı bölme (clause segmentation) runner.

SPEC docs/superpowers/specs/2026-07-20-clause-segmentation-design.md §7.
Bağımsız golden (tests/golden_clause.py, Opus motor-körü) → clauses tam sınanır.
Ayrıca V1/V2 düz `elements` + `sentence_type` REGRESYONU (additive kanıtı).
"""
import pytest

from turkgram import lexicon
from turkgram.sentence import analyze_sentence
from tests.golden_clause import GOLDEN_CLAUSES

_ROOTS = lexicon.load()
_IDS = [g["text"] for g in GOLDEN_CLAUSES]


def _clause_tuple(c):
    return (
        c.role,
        tuple((e.label, e.tokens, e.head_id, e.aliases) for e in c.elements),
        c.predicate_id,
        c.connector,
    )


@pytest.mark.parametrize("g", GOLDEN_CLAUSES, ids=_IDS)
def test_clauses(g):
    """Yargı listesi (rol + öge + predicate_id + connector) TAM."""
    sa = analyze_sentence(g["text"], roots=_ROOTS)
    got = [_clause_tuple(c) for c in sa.clauses]
    exp = [
        (cl["role"],
         tuple((l, t, h, a) for (l, t, h, a) in cl["elements"]),
         cl["predicate_id"],
         cl["connector"])
        for cl in g["clauses"]
    ]
    assert got == exp


def test_flat_elements_unchanged():
    """Additive kanıtı: V1 düz `elements` + tür DEĞİŞMEZ (44 golden ayrıca test_sentence)."""
    from tests.golden_sentence import GOLDEN_SENTENCES
    _OGE_LIMITS = {"Ali kitabı okudu", "Çocuk topu bahçede oynadı"}
    for g in GOLDEN_SENTENCES:
        sa = analyze_sentence(g["text"], roots=_ROOTS)
        st = sa.sentence_type
        t = g["type"]
        assert (st.yuklem_turu, st.yuklem_yeri, st.olumluluk, st.soru,
                st.kip, st.yapi, st.eksiltili) == (
            t["yuklem_turu"], t["yuklem_yeri"], t["olumluluk"], t["soru"],
            t["kip"], t["yapi"], t["eksiltili"])
        if g["text"] in _OGE_LIMITS:
            continue
        got = [(e.label, e.tokens, e.head_id, e.aliases) for e in sa.elements]
        assert got == [(l, tt, h, a) for (l, tt, h, a) in g["elements"]]


def test_clause_consistency():
    """Her cümlede yüklemli yargı sayısı = elements'teki yüklem öge sayısı (temel+bağımsız
    +yan), en az bir yargı; predicate_id tokens içi tutarlı."""
    for g in GOLDEN_CLAUSES:
        sa = analyze_sentence(g["text"], roots=_ROOTS)
        assert sa.clauses, g["text"]
        # her yargının bir yüklem ögesi var (predicate_id>0)
        for c in sa.clauses:
            assert c.predicate_id > 0
            assert any(e.label == "yüklem" for e in c.elements)


def test_empty_no_clauses():
    """Boş metin → clauses=()."""
    assert analyze_sentence("", roots=_ROOTS).clauses == ()
