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


def test_tasvir_denklik():
    assert tr.çekimle("yapmak", "görülen_geçmiş", "3tekil", tasvir="tezlik") == \
        m.conjugate("yapmak", "past", "3sg", aspect="iver")          # yapıverdi
    assert tr.çekimle("bakmak", "geniş", "3tekil", tasvir="akal") == \
        m.conjugate("bakmak", "aorist", "3sg", aspect="akal")        # bakakalır
    assert tr.çekimle("gitmek", "şimdiki", "3tekil", tasvir="sürerlik") == \
        m.conjugate("gitmek", "pres", "3sg", aspect="adur")          # gideduruyor


def test_cati_denklik():
    # tekil çatı
    assert tr.çekimle("yapmak", "görülen_geçmiş", "3tekil", çatı="ettirgen") == \
        m.conjugate("yapmak", "past", "3sg", voice_chain=["caus"])       # yaptırdı
    assert tr.çekimle("okumak", "geçmiş", "3tekil", çatı="edilgen") == \
        m.conjugate("okumak", "past", "3sg", voice_chain=["pass"])       # okundu
    # yığılma (liste → zincir)
    assert tr.çekimle("dövmek", "geçmiş", "3tekil",
                      çatı=["işteş", "ettirgen", "edilgen"]) == \
        m.conjugate("dövmek", "past", "3sg",
                    voice_chain=["recip", "caus", "pass"])               # dövüştürüldü
    # alias eşdeğerliği (pasif≡edilgen, karşılıklı≡işteş)
    assert tr.çekimle("yapmak", "geçmiş", "3tekil", çatı="pasif") == \
        tr.çekimle("yapmak", "geçmiş", "3tekil", çatı="edilgen")
    assert tr.çekimle("bakmak", "geçmiş", "3tekil", çatı="karşılıklı") == \
        tr.çekimle("bakmak", "geçmiş", "3tekil", çatı="işteş")


def test_bilinmeyen_cati():
    with pytest.raises(ValueError, match="çatı"):
        tr.çekimle("yapmak", "geçmiş", "3tekil", çatı="olmayan")


def test_ulac_denklik():
    assert tr.ulaç("gitmek", "arak") == nf.converb("gitmek", "arak")   # giderek
    assert tr.ulaç("okumak", "ince") == nf.converb("okumak", "inca")   # okuyunca (alias ince→inca)
    assert tr.ulaç("yapmak", "meden") == nf.converb("yapmak", "madan") # yapmadan (alias)
    assert tr.ulaç("gitmek", "dikçe") == nf.converb("gitmek", "dikce") # gittikçe


def test_fiilimsi_denklik():
    assert tr.fiilimsi("okumak", "dik", iyelik="1tekil") == \
        nf.participle("okumak", "dik", possessive="1sg")            # okuduğum
    assert tr.fiilimsi("gitmek", "ma", iyelik="3tekil", durum="belirtme") == \
        nf.participle("gitmek", "ma", possessive="3sg", case="acc") # gitmesini
    assert tr.fiilimsi("gelmek", "ecek", iyelik="3tekil", durum="belirtme") == \
        nf.participle("gelmek", "acak", possessive="3sg", case="acc")  # geleceğini (ecek→acak alias)


def test_tablo_ve_coz_denklik():
    # çekim_tablosu/ad_çekim_tablosu: anahtar Türkçeleşir, değerler AYNI kalır.
    çv = tr.çekim_tablosu("okumak")
    çekirdek_v = m.paradigm("okumak")
    assert len(çv) == len(çekirdek_v)
    assert list(çv.values()) == list(çekirdek_v.values())         # sıra + değer korunur
    assert çv["şimdiki.3tekil"] == çekirdek_v["pres.3sg"]         # okuyor
    assert çv["olumsuz.görülen_geçmiş.1tekil"] == çekirdek_v["neg.past.1sg"]
    assert çv["ulaç"] == çekirdek_v["conv_arak"]                  # kişisiz (segment tek)

    çn = tr.ad_çekim_tablosu("kitap")
    çekirdek_n = n.paradigm_noun("kitap")
    assert list(çn.values()) == list(çekirdek_n.values())
    assert çn["belirtme"] == çekirdek_n["acc"]
    assert çn["çoğul.bulunma"] == çekirdek_n["pl.loc"]
    assert çn["iyelik.1tekil.yönelme"] == çekirdek_n["poss.1sg.dat"]

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


# ── çözümle — Türkçe çözümleme yüzü ─────────────────────────────────────
def test_cozumle_denklik():
    # conjugate round-trip: okuyor → şimdiki / 3tekil
    a = next(x for x in tr.çözümle("okuyor", tür="fiil")
             if x.kwargs.get("kip") == "şimdiki" and x.kwargs.get("kişi") == "3tekil")
    assert tr.çekimle(a.lemma, **a.kwargs) == "okuyor"

    # decline round-trip: evlerde → çoğul + bulunma
    b = [x for x in tr.çözümle("evlerde", tür="isim") if x.kwargs.get("durum") == "bulunma"][0]
    assert tr.ad_çekimle(b.lemma, **b.kwargs) == "evlerde"

    # voice çatı yığılması
    c = next(x for x in tr.çözümle("dövüştürüldü", tür="fiil")
             if x.kwargs.get("çatı") == ["işteş", "ettirgen", "edilgen"])
    assert tr.çekimle(c.lemma, **c.kwargs) == "dövüştürüldü"

    # converb / ulaç round-trip
    d = next(x for x in tr.çözümle("giderek", tür="fiil") if x.kind == "converb")
    assert tr.ulaç(d.lemma, d.kwargs["tür"]) == "giderek"


def test_cozumle_bilinmeyen_tur():
    with pytest.raises(ValueError, match="tür"):
        tr.çözümle("okuyor", tür="olmayan")


def test_cozumle_segment_turkce():
    a = tr.çözümle("okuduğum", tür="fiil", kökler={"okumak"})[0]
    labels = [s.label for s in a.segments]
    assert "ortaç" in labels  # DIk → ortaç
