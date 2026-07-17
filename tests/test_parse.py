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
    if "children" not in expected:
        return True  # children kontrolü opsiyonel — sadece tag/surface yeterli
    exp_children = expected["children"]
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


def test_pp_carries_governs():
    """R2 PP düğümü yönetilen durum kümesini taşır."""
    from turkgram import tokenize, parse_text
    from turkgram.parse import parse_phrase

    # roots sağlanmazsa 'ev' X etiketlenir → R2 PP kuramaz; golden convention'ı izle
    tokens = tokenize("ev için")
    analyses = parse_text("ev için", {"ev"})
    tree = parse_phrase(tokens, analyses)

    def find_pp(node):
        if getattr(node, "tag", None) == "PP":
            return node
        for ch in getattr(node, "children", ()):
            r = find_pp(ch)
            if r:
                return r
        return None

    pp = find_pp(tree)
    assert pp is not None, "PP düğümü kurulmadı"
    assert pp.governs == frozenset({"nom", "gen"})


def test_frozen_edat_forms_pp():
    """Donmuş edat (dair) ADP kümesinde → R2 PP kurar."""
    from turkgram.parse import _leaf_tag
    assert _leaf_tag("dair", None) == "ADP"
