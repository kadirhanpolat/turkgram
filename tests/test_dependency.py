"""E5+E6 dependency graph + CoNLL-U runner."""
import pytest
from tests.golden_dependency import DEP_CASES
from tests.golden_conllu import CONLLU_CASES
from turkgram import tokenize, parse_text
from turkgram.parse import parse_phrase
from turkgram.dependency import DepToken, constituency_to_dep, to_conllu


@pytest.mark.parametrize("case", DEP_CASES, ids=[c["text"] for c in DEP_CASES])
def test_constituency_to_dep(case):
    tokens = tokenize(case["text"])
    analyses = parse_text(case["text"], case.get("roots"))
    tree = parse_phrase(tokens, analyses)
    dep = constituency_to_dep(tree)
    assert len(dep) == len(case["expected"])
    for got, exp in zip(dep, case["expected"]):
        assert got.id     == exp["id"],     f"id: {got.id} != {exp['id']}"
        assert got.form   == exp["form"],   f"form: {got.form!r} != {exp['form']!r}"
        assert got.upos   == exp["upos"],   f"upos: {got.upos} != {exp['upos']}"
        assert got.head   == exp["head"],   f"head: {got.head} != {exp['head']}"
        assert got.deprel == exp["deprel"], f"deprel: {got.deprel} != {exp['deprel']}"
        if "lemma" in exp:
            assert got.lemma == exp["lemma"], f"lemma: {got.lemma!r} != {exp['lemma']!r}"


@pytest.mark.parametrize("case", CONLLU_CASES, ids=[c["text"] for c in CONLLU_CASES])
def test_to_conllu(case):
    tokens = tokenize(case["text"])
    analyses = parse_text(case["text"], case.get("roots"))
    tree = parse_phrase(tokens, analyses)
    dep = constituency_to_dep(tree)
    result = to_conllu(dep, sent_id=case["sent_id"], text=case["text"])
    assert result == case["expected"], (
        f"\nBeklenen:\n{case['expected']!r}\nAlınan:\n{result!r}"
    )
