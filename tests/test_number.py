"""test_number.py — Sayı morfolojisi testleri (Faz 5 D1, spec/number-spec.md).

Golden: tests/golden_number.py (motordan bağımsız, elle-doğrulanmış).
"""
from __future__ import annotations
import pytest
from turkgram.number import ordinal, distributive
from turkgram.morphology_noun import decline
from . import golden_number as G


# ---------------------------------------------------------------------------
# Ordinal -(I)ncI
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("kok,beklenen", G.ORDINAL_CASES)
def test_ordinal(kok, beklenen):
    got = ordinal(kok)
    assert got == beklenen, f"ordinal({kok!r}) -> {got!r}, beklenen {beklenen!r}"


# ---------------------------------------------------------------------------
# Distributif -(ş)Ar
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("kok,beklenen", G.DISTRIBUTIVE_CASES)
def test_distributive(kok, beklenen):
    got = distributive(kok)
    assert got == beklenen, f"distributive({kok!r}) -> {got!r}, beklenen {beklenen!r}"


# ---------------------------------------------------------------------------
# Decline round-trip: ordinal biçim → hâl çekimi
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("form,durum,beklenen", G.DECLINE_CASES)
def test_decline(form, durum, beklenen):
    got = decline(form, case=durum)
    assert got == beklenen, f"decline({form!r}, case={durum!r}) -> {got!r}, beklenen {beklenen!r}"


# ---------------------------------------------------------------------------
# TR sarmalayıcı denklik testleri
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("kok,beklenen", G.ORDINAL_CASES)
def test_tr_sırali_denklik(kok, beklenen):
    from turkgram.tr import sıralı
    assert sıralı(kok) == beklenen


@pytest.mark.parametrize("kok,beklenen", G.DISTRIBUTIVE_CASES)
def test_tr_dagitimli_denklik(kok, beklenen):
    from turkgram.tr import dağıtımlı
    assert dağıtımlı(kok) == beklenen
