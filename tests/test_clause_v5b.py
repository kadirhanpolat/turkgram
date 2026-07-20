"""test_clause_v5b.py — aktarma best-effort sınırları (V5.1) runner.

SPEC docs/superpowers/specs/2026-07-20-aktarma-robustlik-design.md.
Golden tests/golden_clause_v5b.py (koordine-içi gömme + homograf-finit + tırnak + guard'lar).
"""
import pytest

from turkgram import lexicon
from turkgram.sentence import analyze_sentence
from tests.golden_clause_v5b import GOLDEN_CLAUSES_V5B

_ROOTS = lexicon.load()
_IDS = [g["text"] for g in GOLDEN_CLAUSES_V5B]


@pytest.mark.parametrize("g", GOLDEN_CLAUSES_V5B, ids=_IDS)
def test_clauses_v5b(g):
    sa = analyze_sentence(g["text"], roots=_ROOTS)
    got = [(c.role,
            tuple((e.label, e.tokens, e.head_id, e.aliases) for e in c.elements),
            c.predicate_id, c.connector)
           for c in sa.clauses]
    exp = [(cl["role"],
            tuple((l, t, h, a) for (l, t, h, a) in cl["elements"]),
            cl["predicate_id"], cl["connector"])
           for cl in g["clauses"]]
    assert got == exp
