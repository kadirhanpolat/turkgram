"""Gömülü kök leksikonu yükleyici testleri (Faz 2b, turkgram/lexicon.py).

Bu katman VERİ + PLUMBING sınar (gramer değil): yükleme, POS filtresi, değişmezlik,
veri bütünlüğü ve `analyze(roots=...)` entegrasyonu (gürültü azaltma). Biçim doğruluğu
çekirdek golden'larda; burada leksikonun çözümleyiciyi doğru beslediğini doğrularız.
"""
import pytest

from turkgram import lexicon as lx
from turkgram import analysis as an


# ---------------------------------------------------------------------------
# Yükleme + içerik
# ---------------------------------------------------------------------------

def test_load_bos_degil_ve_frozenset():
    roots = lx.load()
    assert isinstance(roots, frozenset)
    assert len(roots) > 20000  # Zemberek master-dictionary ~26k


@pytest.mark.parametrize("lemma,pos", [
    ("ev", "noun"), ("kitap", "noun"), ("gelmek", "verb"),
    ("okumak", "verb"), ("güzel", "adj"),
])
def test_bilinen_lemmalar(lemma, pos):
    assert lemma in lx.load()
    assert lx.pos_map()[lemma] == pos


def test_size_tum_pos():
    # size() tüm POS'u sayar; load() varsayılan çekilebilir alt-kümedir → size ≥ load
    assert lx.size() >= len(lx.load())
    assert lx.size() == len(lx.pos_map())


# ---------------------------------------------------------------------------
# POS filtresi
# ---------------------------------------------------------------------------

def test_pos_filtresi_verb_hepsi_mastar():
    verbs = lx.load("verb")
    assert verbs
    assert all(v.endswith(("mak", "mek")) for v in verbs)


def test_pos_filtresi_noun_fiil_icermez():
    nouns = lx.load("noun")
    assert "ev" in nouns
    assert "gelmek" not in nouns


def test_pos_filtresi_birlesim():
    v = lx.load("verb")
    n = lx.load("noun")
    both = lx.load({"verb", "noun"})
    assert both == (v | n)


def test_pos_varsayilan_cekilebilir_altkume():
    # interj/dup/conj/postp/det/ques varsayılan load()'a girmez
    default = lx.load()
    all_pos = lx.load(lx.POS_TAGS)
    assert default <= all_pos
    assert len(all_pos) > len(default)


def test_pos_bilinmeyen_hata():
    with pytest.raises(ValueError, match="bilinmeyen kategori"):
        lx.load("fiil")


# ---------------------------------------------------------------------------
# Veri bütünlüğü
# ---------------------------------------------------------------------------

def test_veri_butunlugu():
    pm = lx.pos_map()
    assert all(pm.values()), "boş POS olmamalı"
    assert set(pm.values()) <= lx.POS_TAGS, "bilinmeyen POS etiketi"
    assert all(lemma and lemma == lemma for lemma in pm), "boş lemma olmamalı"
    # Türkçe küçük harf normalize (İ→i, I→ı) — büyük Latin harf kalmamalı
    assert not any(c.isupper() for lemma in pm for c in lemma if c.isascii())


def test_cache_deterministik():
    # _load_raw lru_cache'li (aynı tuple nesnesi); load() eşit küme döndürür
    assert lx._load_raw() is lx._load_raw()
    assert lx.load() == lx.load()


# ---------------------------------------------------------------------------
# analyze(roots=leksikon) entegrasyonu — gürültü azaltma
# ---------------------------------------------------------------------------

def test_entegrasyon_gurultu_azaltma():
    roots = lx.load()
    # "evler" leksikonsuz gürültü (çıplak-önek); leksikonla yalnız gerçek 'ev' çoğul
    got = an.analyze("evler", roots=roots)
    assert got
    assert all(a.lemma == "ev" and not a.hypothetical for a in got)
    assert any(a.kind == "decline" and a.kwargs.get("number") == "pl" for a in got)


def test_entegrasyon_gercek_fiil():
    roots = lx.load()
    got = an.analyze("geldim", roots=roots)
    assert any(a.lemma == "gelmek" and a.kwargs.get("tense") == "past"
               and a.kwargs.get("person") == "1sg" for a in got)


def test_entegrasyon_sozde_kelime_elenir():
    # Leksikonda olmayan uydurma yüzey → gerçek okuma yok (hepsi elenir)
    roots = lx.load()
    assert an.analyze("qwxzptr", roots=roots) == []
