"""test_clause_v4.py — ki/diye yan cümle bölme (clause segmentation V4) runner.

SPEC docs/superpowers/specs/2026-07-20-clause-segmentation-design.md §5b.
Bağımsız golden (tests/golden_clause_v4.py, Opus motor-körü).
"""
import pytest

from turkgram import lexicon
from turkgram.sentence import analyze_sentence
from tests.golden_clause_v4 import GOLDEN_CLAUSES_V4

_ROOTS = lexicon.load()
_IDS = [g["text"] for g in GOLDEN_CLAUSES_V4]


def _clause_tuple(c):
    return (
        c.role,
        tuple((e.label, e.tokens, e.head_id, e.aliases) for e in c.elements),
        c.predicate_id,
        c.connector,
    )


@pytest.mark.parametrize("g", GOLDEN_CLAUSES_V4, ids=_IDS)
def test_clauses_v4(g):
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


def test_trailing_bare_subordinator_robust():
    """Hakem HIGH: bare/trailing subordinatör (malformed) → phantom yüklem YOK, ana yargı
    yanlış 'yan' etiketlenMEZ. Best-effort (§6), çökmesiz + marker öge/yüklem sızmaz."""
    # trailing diye = demek opt pred_i → phantom yüklem=('diye',) OLMAMALI (yapısal güvenlik).
    # Tek elliptik yargı (yan-kardeşsiz) → temel (§3); rol best-effort, asıl güvence phantom yok.
    c = analyze_sentence("Bekledim diye", roots=_ROOTS).clauses
    assert all(e.tokens != ("diye",) for cl in c for e in cl.elements)
    assert len(c) == 1 and any(e.tokens == ("Bekledim",) for e in c[0].elements)
    # trailing ki ana yüklemle aynı segmentte → ana yargı 'yan' OLMAMALI (temel kalmalı)
    c = analyze_sentence("Biliyorum ki", roots=_ROOTS).clauses
    assert [cl.role for cl in c] == ["temel"]
    assert all(e.tokens != ("ki",) for cl in c for e in cl.elements)
    # cümle-başı ki → çökme yok, marker sızmaz
    c = analyze_sentence("ki gelecek", roots=_ROOTS).clauses
    assert c and all(e.tokens != ("ki",) for cl in c for e in cl.elements)
