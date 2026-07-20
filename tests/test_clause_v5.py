"""test_clause_v5.py — gerçek gömme (aktarma + adlaşmış) yargı bölme runner.

SPEC docs/superpowers/specs/2026-07-20-clause-segmentation-design.md §5c.
Bağımsız golden (tests/golden_clause_v5.py, Opus motor-körü).
"""
import pytest

from turkgram import lexicon
from turkgram.sentence import analyze_sentence
from tests.golden_clause_v5 import GOLDEN_CLAUSES_V5

_ROOTS = lexicon.load()
_IDS = [g["text"] for g in GOLDEN_CLAUSES_V5]


def _clause_tuple(c):
    return (
        c.role,
        tuple((e.label, e.tokens, e.head_id, e.aliases) for e in c.elements),
        c.predicate_id,
        c.connector,
    )


@pytest.mark.parametrize("g", GOLDEN_CLAUSES_V5, ids=_IDS)
def test_clauses_v5(g):
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
