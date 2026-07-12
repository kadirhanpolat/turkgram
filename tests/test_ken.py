# -*- coding: utf-8 -*-
"""-ken zarf-fiili: motor çıktısı bağımsız golden'a eşit mi (ken-spec.md)."""
import pytest

from turkgram.nonfinite import converb_ken
from turkgram.morphology_noun import copula
from tests.golden_ken import GOLDEN_KEN_VERB, GOLDEN_KEN_NOMINAL


@pytest.mark.parametrize("key,expected", sorted(GOLDEN_KEN_VERB.items()))
def test_ken_verb_golden(key, expected):
    lemma, base, negative = key
    assert converb_ken(lemma, base=base, negative=negative) == expected


@pytest.mark.parametrize("key,expected", sorted(GOLDEN_KEN_NOMINAL.items(),
                                                key=lambda t: (t[0][0], t[0][1] or "")))
def test_ken_nominal_golden(key, expected):
    headword, case = key
    kw = {"case": case} if case is not None else {}
    assert copula(headword, "ken", **kw) == expected


def test_ken_invariant_no_harmony():
    # ken hiçbir bağlamda kan/kun olmaz
    assert converb_ken("bakmak").endswith("ken")
    assert converb_ken("olmak").endswith("ken")


def test_ken_invalid_base():
    with pytest.raises(ValueError):
        converb_ken("gelmek", base="cond")
