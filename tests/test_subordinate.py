# tests/test_subordinate.py
"""Faz E3/E4 yan cümle runner."""
import pytest
from tests.golden_subordinate import SUBORDINATE_CASES
from tests.test_parse import _node_matches          # mevcut yardımcı yeniden kullan
from turkgram import tokenize, parse_text
from turkgram.parse import LeafNode, PhraseNode, parse_phrase


@pytest.mark.parametrize(
    "case",
    SUBORDINATE_CASES,
    ids=[c["text"] for c in SUBORDINATE_CASES],
)
def test_subordinate_parse(case):
    tokens = tokenize(case["text"])
    analyses = parse_text(case["text"], case.get("roots"))
    tree = parse_phrase(tokens, analyses)
    assert _node_matches(tree, case["expected"]), (
        f"\nBeklenen:\n{case['expected']}\nAlınan:\n{tree}"
    )
