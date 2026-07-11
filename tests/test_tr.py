"""turkgram.tr — Türkçe API katmanı testleri.

Bu katman yalnız ÇEVİRİ doğruluğunu sınar: her Türkçe çağrının sonucu, eşdeğer
İngilizce çekirdek çağrısının sonucuyla AYNI olmalı (biçim doğruluğu çekirdek
golden'larında garanti). Ayrıca alias, _tr_lower ve bilinmeyen-değer hatası.
"""
import pytest
from turkgram import tr
from turkgram import morphology as m, morphology_noun as n, derivation as d
from turkgram import nonfinite as nf


# ── Çeviri denkliği (Türkçe == çekirdek) ─────────────────────────────────
def test_cekimle_denklik():
    assert tr.çekimle("gelmek", "şimdiki", "1tekil") == m.conjugate("gelmek", "pres", "1sg")
    assert tr.çekimle("gitmek", "görülen_geçmiş", "3tekil", olumsuz=True) == \
        m.conjugate("gitmek", "past", "3sg", negative=True)
    assert tr.çekimle("okumak", "geniş", "3tekil", yeterlik=True) == \
        m.conjugate("okumak", "aorist", "3sg", ability=True)
    assert tr.çekimle("gelmek", "şimdiki", "1tekil", soru=True) == \
        m.conjugate("gelmek", "pres", "1sg", question=True)
    assert tr.çekimle("gelmek", "şimdiki", "3tekil", birleşik="hikaye") == \
        m.conjugate("gelmek", "pres", "3sg", aux="hikaye")


def test_kip_tam_denklik():
    """Tüm kip + kişi kombinasyonları çekirdekle bire bir."""
    kip_map = {"şimdiki": "pres", "görülen_geçmiş": "past", "gelecek": "fut",
               "geniş": "aorist", "öğrenilen_geçmiş": "evid", "şart": "cond",
               "gereklilik": "necess", "istek": "opt"}
    kisi_map = {"1tekil": "1sg", "2tekil": "2sg", "3tekil": "3sg",
                "1çoğul": "1pl", "2çoğul": "2pl", "3çoğul": "3pl"}
    for tk, ek in kip_map.items():
        for tp, ep in kisi_map.items():
            assert tr.çekimle("yazmak", tk, tp) == m.conjugate("yazmak", ek, ep)


def test_ad_cekimle_denklik():
    assert tr.ad_çekimle("kitap", durum="yönelme") == n.decline("kitap", case="dat")
    assert tr.ad_çekimle("ev", iyelik="3tekil", durum="bulunma") == \
        n.decline("ev", possessive="3sg", case="loc")
    assert tr.ad_çekimle("göz", sayı="çoğul", durum="ayrılma") == \
        n.decline("göz", number="pl", case="abl")


def test_ekfiil_denklik():
    assert tr.ekfiil("öğrenci", "hikaye", "1tekil") == n.copula("öğrenci", "hikaye", "1sg")
    assert tr.ekfiil("ev", "rivayet", "3tekil", durum="bulunma") == \
        n.copula("ev", "rivayet", "3sg", case="loc")
    assert tr.ekfiil("genç", None, "1tekil") == n.copula("genç", None, "1sg")   # gencim
    assert tr.ekfiil("öğrenci", "hikaye", "1tekil", soru=True) == \
        n.copula("öğrenci", "hikaye", "1sg", question=True)


def test_yuklem_denklik():
    # yalın adda `not core` korunmalı (yumuşama): gencim
    assert tr.yüklem("genç", kişi="1tekil") == n.predicative("genç", person="1sg")
    assert tr.yüklem("ev") == n.predicative("ev")


def test_turet_denklik():
    assert tr.türet("göz", "isim") == d.derivations("göz", "noun")
    assert tr.türet("gelmek", "fiil") == d.derivations("gelmek", "verb")


def test_ulac_denklik():
    assert tr.ulaç("gitmek", "arak") == nf.converb("gitmek", "arak")   # giderek
    assert tr.ulaç("okumak", "ince") == nf.converb("okumak", "inca")   # okuyunca (alias ince→inca)
    assert tr.ulaç("yapmak", "meden") == nf.converb("yapmak", "madan") # yapmadan (alias)
    assert tr.ulaç("gitmek", "dikçe") == nf.converb("gitmek", "dikce") # gittikçe


def test_tablo_ve_coz_denklik():
    assert tr.çekim_tablosu("okumak") == m.paradigm("okumak")
    assert tr.ad_çekim_tablosu("kitap") == n.paradigm_noun("kitap")
    assert tr.fiil_çöz("gitmek") == m.parse_verb("gitmek")
    assert tr.ad_çöz("kitap") == n.parse_noun("kitap")


# ── Karma: alias eşdeğerliği ─────────────────────────────────────────────
def test_alias_esdeger():
    assert tr.çekimle("gitmek", "dili_geçmiş", "3tekil") == \
        tr.çekimle("gitmek", "görülen_geçmiş", "3tekil")
    assert tr.çekimle("gitmek", "duyulan", "3tekil") == \
        tr.çekimle("gitmek", "öğrenilen_geçmiş", "3tekil")
    assert tr.ad_çekimle("ev", durum="de") == tr.ad_çekimle("ev", durum="bulunma")
    assert tr.ad_çekimle("ev", durum="i") == tr.ad_çekimle("ev", durum="belirtme")
    # ASCII-fold
    assert tr.çekimle("gelmek", "genis", "3tekil") == tr.çekimle("gelmek", "geniş", "3tekil")


# ── _tr_lower: büyük-harf girdi ──────────────────────────────────────────
def test_buyuk_harf_normalize():
    assert tr.çekimle("gelmek", "GENİŞ", "3tekil") == tr.çekimle("gelmek", "geniş", "3tekil")
    assert tr.ad_çekimle("ev", durum="Yönelme") == tr.ad_çekimle("ev", durum="yönelme")


# ── Bilinmeyen değer → ValueError (seçenekleri sıralar) ──────────────────
def test_bilinmeyen_deger():
    with pytest.raises(ValueError, match="kip"):
        tr.çekimle("gelmek", "olmayan_kip", "1tekil")
    with pytest.raises(ValueError, match="durum"):
        tr.ad_çekimle("ev", durum="olmayan")
    with pytest.raises(ValueError, match="kişi"):
        tr.çekimle("gelmek", "şimdiki", "5tekil")
