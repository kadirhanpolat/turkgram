"""test_adjective.py — Sıfat morfolojisi testleri (SPEC adjective-spec.md).

Golden: tests/golden_adjective.py (motordan bağımsız, elle-doğrulanmış).
"""
from __future__ import annotations
import pytest
import turkgram as tg
from . import golden_adjective as G


# ---------------------------------------------------------------------------
# §1.2 — Pekiştirme: ünlü-başlı (algoritmik kural)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("adj,expected", G.INTENSIFY_VOWEL)
def test_intensify_vowel(adj, expected):
    got = tg.intensify(adj)
    assert got == expected, f"intensify({adj!r}) -> {got!r}, beklenen {expected!r}"


# ---------------------------------------------------------------------------
# §1.3 — Pekiştirme: ünsüz-başlı (kapalı tablo)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("adj,expected", G.INTENSIFY_CONSONANT)
def test_intensify_consonant(adj, expected):
    got = tg.intensify(adj)
    assert got == expected, f"intensify({adj!r}) -> {got!r}, beklenen {expected!r}"


# ---------------------------------------------------------------------------
# §1.4 — Tire varyantı
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("adj,expected", G.INTENSIFY_HYPHEN)
def test_intensify_hyphen(adj, expected):
    got = tg.intensify(adj)
    assert got == expected, f"intensify({adj!r}) -> {got!r}, beklenen {expected!r}"


# ---------------------------------------------------------------------------
# Bilinmeyen → None
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("adj", G.INTENSIFY_UNKNOWN)
def test_intensify_unknown(adj):
    got = tg.intensify(adj)
    assert got is None, f"intensify({adj!r}) -> {got!r}, beklenen None"


# ---------------------------------------------------------------------------
# §2.1 — Küçültme: -CIk
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("adj,expected", G.DIMINUTIVE_CIK_SAFE)
def test_diminutive_cik(adj, expected):
    got = tg.diminutive(adj, "-CIk")
    assert got == expected, f"diminutive({adj!r}, '-CIk') -> {got!r}, beklenen {expected!r}"


# ---------------------------------------------------------------------------
# §2.2 — Küçültme: -ImsI
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("adj,expected", G.DIMINUTIVE_IMSI)
def test_diminutive_imsi(adj, expected):
    got = tg.diminutive(adj, "-ImsI")
    assert got == expected, f"diminutive({adj!r}, '-ImsI') -> {got!r}, beklenen {expected!r}"


# ---------------------------------------------------------------------------
# §2.3 — Küçültme: -ImtIrak
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("adj,expected", G.DIMINUTIVE_IMTIRAK)
def test_diminutive_imtirak(adj, expected):
    got = tg.diminutive(adj, "-ImtIrak")
    assert got == expected, f"diminutive({adj!r}, '-ImtIrak') -> {got!r}, beklenen {expected!r}"


# ---------------------------------------------------------------------------
# Geçersiz ek → ValueError
# ---------------------------------------------------------------------------
def test_diminutive_invalid_suffix():
    with pytest.raises(ValueError):
        tg.diminutive("büyük", "-XYZ")
