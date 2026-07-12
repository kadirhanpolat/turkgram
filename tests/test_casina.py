# -*- coding: utf-8 -*-
"""-cAsInA zarf-fiili: motor çıktısı bağımsız golden'a eşit mi (casina-spec.md)."""
import pytest

from turkgram.nonfinite import converb_casina
from tests.golden_casina import GOLDEN_CASINA


@pytest.mark.parametrize("key,expected", sorted(GOLDEN_CASINA.items()))
def test_casina_golden(key, expected):
    lemma, base, negative = key
    assert converb_casina(lemma, base=base, negative=negative) == expected


def test_casina_invalid_base():
    with pytest.raises(ValueError):
        converb_casina("gelmek", base="fut")
