"""Koordine genitif tamlayan — dependency runner."""
import pytest
from tests.golden_koordine_genitif_dep import DEP_CASES
from turkgram import tokenize, parse_text
from turkgram.parse import parse_phrase
from turkgram.dependency import constituency_to_dep


@pytest.mark.parametrize("case", DEP_CASES, ids=[c["text"] for c in DEP_CASES])
def test_koordine_genitif_dep(case):
    tokens = tokenize(case["text"])
    analyses = parse_text(case["text"], case.get("roots"))
    tree = parse_phrase(tokens, analyses)
    dep = constituency_to_dep(tree)
    assert len(dep) == len(case["expected"])
    for got, exp in zip(dep, case["expected"]):
        assert got.id == exp["id"], f"id: {got.id} != {exp['id']}"
        assert got.form == exp["form"], f"form: {got.form!r} != {exp['form']!r}"
        assert got.upos == exp["upos"], f"upos: {got.upos} != {exp['upos']}"
        assert got.head == exp["head"], f"head: {got.head} != {exp['head']}"
        assert got.deprel == exp["deprel"], f"deprel: {got.deprel} != {exp['deprel']}"
        if "lemma" in exp:
            assert got.lemma == exp["lemma"], f"lemma: {got.lemma!r} != {exp['lemma']!r}"
