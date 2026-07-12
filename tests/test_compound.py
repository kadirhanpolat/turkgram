# -*- coding: utf-8 -*-
"""Bileşik zaman: motor çıktısı bağımsız golden'a eşit mi (compound-tense-spec.md)."""
import pytest

from turkgram.compound import compound
from tests.golden_compound import GOLDEN_COMPOUND


@pytest.mark.parametrize("key,expected", sorted(GOLDEN_COMPOUND.items()))
def test_compound_golden(key, expected):
    lemma, base, cop, person, negative = key
    assert compound(lemma, base, cop, person, negative=negative) == expected


def test_compound_3pl_placement():
    # En kritik değişmez: 3pl çoğul tabanda, ek-fiil 3sg
    assert compound("gelmek", "pres", "hikaye", "3pl") == "geliyorlardı"
    assert compound("gelmek", "aorist", "rivayet", "3pl") == "gelirlermiş"


def test_compound_invalid():
    with pytest.raises(ValueError):
        compound("gelmek", "past", "hikaye")   # basit geçmiş taban kapsam dışı
    with pytest.raises(ValueError):
        compound("gelmek", "pres", "bogus")
