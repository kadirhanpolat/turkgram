"""Olasılıksal disambiguation testleri (Faz 2b, turkgram/disambiguation.py).

SPEC: `spec/disambiguation-spec.md`. Golden = SIRA (order) testi, güven DEĞERİ değil
(float; SPEC §3). Yalnız dilbilimsel olarak KESİN çağrılabilen belirsiz yüzeylerde top-1
beklenir; yakın çağrılar (aynı-lemma iyelik/belirtme berabere) deterministik tiebreak'e
bırakılır. Motor imzası/sırası değişmediğinden (opt-in), analiz golden'larına dokunulmaz.
"""
import pytest

from turkgram import analysis as an, disambiguation as dis, lexicon as lx


@pytest.fixture(scope="module")
def pm():
    return lx.pos_map()


@pytest.fixture(scope="module")
def roots():
    return lx.load()


# ---------------------------------------------------------------------------
# Dilbilimsel öncelik (freq yok) — KESİN çağrılabilen top-1 (SPEC §1, §3)
# ---------------------------------------------------------------------------

# (surface, beklenen top-1: (lemma, kind, kwargs-alt-kümesi))
CONFIDENT_TOP1 = [
    # ekonomik yalın isim, çok-morfemli fiil okumalarına baskın
    ("gelin", "gelin", "decline", {}),
    # sonlu geçmiş, -dik sıfat-fiiline baskın (kind_prior + ekonomi)
    ("geldik", "gelmek", "conjugate", {"tense": "past", "person": "1pl"}),
    # sonlu geniş-olumsuz, -ma ad-fiiline baskın
    ("gelmem", "gelmek", "conjugate", {"tense": "aorist", "person": "1sg", "negative": True}),
]


@pytest.mark.parametrize("surface,lemma,kind,kw", CONFIDENT_TOP1)
def test_dilbilimsel_top1(surface, lemma, kind, kw, roots, pm):
    top = dis.rank(an.analyze(surface, roots=roots), pos=pm)[0]
    assert top.lemma == lemma
    assert top.kind == kind
    assert kw.items() <= top.kwargs.items()


# ---------------------------------------------------------------------------
# Sıklık kancası (SPEC §1.1) — enjekte edilen freq top-1'i çevirir
# ---------------------------------------------------------------------------

def test_freq_override_topu_cevirir(roots, pm):
    cands = an.analyze("gelin", roots=roots)
    # freq yok → yalın isim tepede
    assert dis.rank(cands, pos=pm)[0].lemma == "gelin"
    # gelmek lehine güçlü freq → fiil okuması tepeye
    top = dis.rank(cands, freq={"gelmek": 1000.0}, pos=pm)[0]
    assert top.lemma == "gelmek" and top.kind == "conjugate"


def test_freq_none_dilbilimsel_belirleyici(roots, pm):
    # freq=None ile boş-freq {} aynı sırayı vermeli (sıklık terimi etkisiz)
    cands = an.analyze("geldik", roots=roots)
    assert dis.rank(cands, pos=pm) == dis.rank(cands, freq={}, pos=pm)


# ---------------------------------------------------------------------------
# POS-tutarlılık (SPEC §1.2)
# ---------------------------------------------------------------------------

def test_pos_consistency_isaretleri():
    # yapay Analysis'lerle _pos_consistency birim testi
    verb_read = an.Analysis("gelmek", "verb", "conjugate", {}, (), False)
    noun_read = an.Analysis("ev", "noun", "decline", {}, (), False)
    pos = {"gelmek": "verb", "ev": "noun"}
    assert dis._pos_consistency(verb_read, pos) == 1
    assert dis._pos_consistency(noun_read, pos) == 1
    # tutarsız: fiil-lemma nominal kind'da
    bad = an.Analysis("gelmek", "verb", "decline", {}, (), False)
    assert dis._pos_consistency(bad, pos) == -1
    # bilinmeyen lemma → 0
    assert dis._pos_consistency(verb_read, {}) == 0
    assert dis._pos_consistency(verb_read, None) == 0


# ---------------------------------------------------------------------------
# disambiguate — güven (olasılık) özellikleri (SPEC §2)
# ---------------------------------------------------------------------------

def test_guven_toplam_bir_ve_azalan(roots, pm):
    pairs = dis.disambiguate(an.analyze("gelin", roots=roots), pos=pm)
    assert pairs
    probs = [p for _, p in pairs]
    assert abs(sum(probs) - 1.0) < 1e-9
    assert probs == sorted(probs, reverse=True)  # best-first
    assert all(0.0 <= p <= 1.0 for p in probs)


def test_guven_tek_aday_bir(roots, pm):
    pairs = dis.disambiguate(an.analyze("evler", roots=roots), pos=pm)
    assert len(pairs) == 1
    assert pairs[0][1] == 1.0


def test_guven_bos_girdi():
    assert dis.disambiguate([]) == []
    assert dis.rank([]) == []


def test_freq_guveni_yukseltir(roots, pm):
    cands = an.analyze("gelin", roots=roots)
    base = dict((a.lemma, p) for a, p in dis.disambiguate(cands, pos=pm))
    boosted = dict((a.lemma, p) for a, p in
                   dis.disambiguate(cands, freq={"gelmek": 1000.0}, pos=pm))
    assert boosted["gelmek"] > base["gelmek"]


# ---------------------------------------------------------------------------
# Değişmezlik (immutability) — girdi listesi/nesneleri değişmez
# ---------------------------------------------------------------------------

def test_girdi_mutasyonu_yok(roots, pm):
    cands = an.analyze("gelin", roots=roots)
    snapshot = list(cands)
    dis.rank(cands, pos=pm)
    dis.disambiguate(cands, pos=pm)
    assert cands == snapshot  # sıra/içerik korunur
