"""E2 constituency parser runner."""
import pytest
from tests.golden_parse import PARSE_CASES
from turkgram import tokenize, parse_text
from turkgram.parse import LeafNode, PhraseNode, parse_phrase


def _node_matches(node: "PhraseNode | LeafNode", expected: dict) -> bool:
    """Ağaç düğümünü beklenen sözlükle karşılaştır."""
    if isinstance(node, LeafNode):
        return (
            node.tag == expected.get("tag")
            and node.token == expected.get("token")
        )
    if node.tag != expected.get("tag"):
        return False
    if "surface" in expected and node.surface != expected["surface"]:
        return False
    exp_children = expected.get("children", [])
    if len(node.children) != len(exp_children):
        return False
    return all(_node_matches(c, e) for c, e in zip(node.children, exp_children))


@pytest.mark.parametrize("case", PARSE_CASES, ids=[c["text"] for c in PARSE_CASES])
def test_parse_phrase(case):
    tokens = tokenize(case["text"])
    analyses = parse_text(case["text"], case.get("roots"))
    tree = parse_phrase(tokens, analyses)
    assert _node_matches(tree, case["expected"]), (
        f"\nBeklenen:\n{case['expected']}\nAlınan:\n{tree}"
    )
