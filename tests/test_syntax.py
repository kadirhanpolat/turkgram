"""test_syntax.py — Sözdizimi öbek üretimi testleri (syntax.py).

Golden: tests/golden_syntax.py (motordan bağımsız, elle-doğrulanmış).
"""
from __future__ import annotations
import pytest
import turkgram as tg
from . import golden_syntax as G


# ---------------------------------------------------------------------------
# §1 — İsim tamlaması (belirtili)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("tamlayan,tamlanan,expected", G.ISIM_TAMLAMASI_BELIRTILI)
def test_isim_tamlamasi_belirtili(tamlayan, tamlanan, expected):
    got = tg.isim_tamlamasi(tamlayan, tamlanan, tur="belirtili")
    assert got == expected, (
        f"isim_tamlamasi({tamlayan!r}, {tamlanan!r}, tur='belirtili') "
        f"-> {got!r}, beklenen {expected!r}"
    )


# ---------------------------------------------------------------------------
# §1 — İsim tamlaması (belirtisiz)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("tamlayan,tamlanan,expected", G.ISIM_TAMLAMASI_BELIRTISIZ)
def test_isim_tamlamasi_belirtisiz(tamlayan, tamlanan, expected):
    got = tg.isim_tamlamasi(tamlayan, tamlanan, tur="belirtisiz")
    assert got == expected, (
        f"isim_tamlamasi({tamlayan!r}, {tamlanan!r}, tur='belirtisiz') "
        f"-> {got!r}, beklenen {expected!r}"
    )


# ---------------------------------------------------------------------------
# §2 — Sıfat tamlaması
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("sifat,isim,expected", G.SIFAT_TAMLAMASI)
def test_sifat_tamlamasi(sifat, isim, expected):
    got = tg.sifat_tamlamasi(sifat, isim)
    assert got == expected, (
        f"sifat_tamlamasi({sifat!r}, {isim!r}) -> {got!r}, beklenen {expected!r}"
    )


# ---------------------------------------------------------------------------
# §3 — Zarf türetme
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("adj,expected", G.ZARF_YAP)
def test_zarf_yap(adj, expected):
    got = tg.zarf_yap(adj)
    assert got == expected, (
        f"zarf_yap({adj!r}) -> {got!r}, beklenen {expected!r}"
    )


# ---------------------------------------------------------------------------
# §4 — Cümle üretimi
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("ozne,yuklem,kwargs,expected", G.CUMLE_URET)
def test_cumle_uret(ozne, yuklem, kwargs, expected):
    got = tg.cumle_uret(ozne, yuklem, **kwargs)
    assert got == expected, (
        f"cumle_uret({ozne!r}, {yuklem!r}, **{kwargs}) -> {got!r}, beklenen {expected!r}"
    )


# ---------------------------------------------------------------------------
# Hata: geçersiz tür
# ---------------------------------------------------------------------------
def test_isim_tamlamasi_invalid_tur():
    with pytest.raises(ValueError):
        tg.isim_tamlamasi("ev", "kapı", tur="geçersiz")
