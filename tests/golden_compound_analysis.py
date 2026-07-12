# Bileşik ZAMAN çözümleme golden (Faz 2b / motor-dışı biçim 3 — REGRESYON KİLİDİ).
# Bileşik zaman ANALİZİ yeni motor gerektirmez: compound(l,base,cop,person,neg) üreteci
# conjugate(l,base,person,aux=cop,neg) ile BİREBİR aynı (216.000 çağrı 0 fark, şart-2pl fix
# sonrası). Çözümleyici bu yüzeyleri kind="conjugate" + aux kwargs olarak çözer (compound kind'ı
# analizde KULLANILMAZ — tek kanonik okuma). Bu golden ileride aux çözüm yolu kırılırsa yakalar.
# NOT: golden_analysis.py'deki GOLDEN_COMPOUND çok-token birleşik FİİL'dir (göz ardı etti); bu
# ayrı — bileşik ZAMAN (geliyordu). Değer: (lemma,pos,kind,kanonik kwargs).

# (surface) -> [ {lemma, pos, kind, kwargs} ]  — hepsi conjugate + aux
GOLDEN_COMPOUND_TENSE = {
    # hikaye (-DI)
    "geliyordu":    [{"lemma": "gelmek", "pos": "verb", "kind": "conjugate", "kwargs": {"tense": "pres",   "person": "3sg", "aux": "hikaye"}}],
    "geliyordum":   [{"lemma": "gelmek", "pos": "verb", "kind": "conjugate", "kwargs": {"tense": "pres",   "person": "1sg", "aux": "hikaye"}}],
    "geliyorlardı": [{"lemma": "gelmek", "pos": "verb", "kind": "conjugate", "kwargs": {"tense": "pres",   "person": "3pl", "aux": "hikaye"}}],  # 3pl: taban+lAr, ek-fiil 3sg
    "gelirdi":      [{"lemma": "gelmek", "pos": "verb", "kind": "conjugate", "kwargs": {"tense": "aorist", "person": "3sg", "aux": "hikaye"}}],
    "gelirlerdi":   [{"lemma": "gelmek", "pos": "verb", "kind": "conjugate", "kwargs": {"tense": "aorist", "person": "3pl", "aux": "hikaye"}}],
    "gelmişti":     [{"lemma": "gelmek", "pos": "verb", "kind": "conjugate", "kwargs": {"tense": "evid",   "person": "3sg", "aux": "hikaye"}}],
    "gelecekti":    [{"lemma": "gelmek", "pos": "verb", "kind": "conjugate", "kwargs": {"tense": "fut",    "person": "3sg", "aux": "hikaye"}}],
    "yapıyordu":    [{"lemma": "yapmak", "pos": "verb", "kind": "conjugate", "kwargs": {"tense": "pres",   "person": "3sg", "aux": "hikaye"}}],
    # rivayet (-mIş)
    "gelirmiş":     [{"lemma": "gelmek", "pos": "verb", "kind": "conjugate", "kwargs": {"tense": "aorist", "person": "3sg", "aux": "rivayet"}}],
    "geliyormuş":   [{"lemma": "gelmek", "pos": "verb", "kind": "conjugate", "kwargs": {"tense": "pres",   "person": "3sg", "aux": "rivayet"}}],
    # sart (-sA)
    "gelirse":      [{"lemma": "gelmek", "pos": "verb", "kind": "conjugate", "kwargs": {"tense": "aorist", "person": "3sg", "aux": "sart"}}],
    # olumsuz
    "gelmiyordu":   [{"lemma": "gelmek", "pos": "verb", "kind": "conjugate", "kwargs": {"tense": "pres",   "person": "3sg", "aux": "hikaye", "negative": True}}],
    "gelmezdi":     [{"lemma": "gelmek", "pos": "verb", "kind": "conjugate", "kwargs": {"tense": "aorist", "person": "3sg", "aux": "hikaye", "negative": True}}],
}

COMPOUND_TENSE_LEXICON = frozenset(
    g["lemma"] for entries in GOLDEN_COMPOUND_TENSE.values() for g in entries
)
