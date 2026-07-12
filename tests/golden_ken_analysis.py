# -ken çözümleme golden (Faz 2b / motor-dışı biçim 2 — analiz).
# BAĞIMSIZ: motor-körü Opus ajanı yalnız spec/ken-spec.md + Türkçe dilbilgisiyle kurdu
# (turkgram/ görülmeden). İki bağlanma: fiil (kind=converb_ken) + nominal (kind=copula,
# aux=ken kişisiz). `ken` DEĞİŞMEZ (harmoni yok). Belirsizlik: bazı yüzeyler hem fiil hem
# isim (gelirken=gelmek|gelir; giderken=gitmek|gider; yazarken=yazmak|yazar).

# (surface) -> [ {lemma, pos, kind, kwargs} ]
GOLDEN_KEN = {
    # --- fiil aorist ---
    "okurken":  [{"lemma": "okumak", "pos": "verb", "kind": "converb_ken", "kwargs": {"base": "aorist"}}],
    "bakarken": [{"lemma": "bakmak", "pos": "verb", "kind": "converb_ken", "kwargs": {"base": "aorist"}}],
    "gülerken": [{"lemma": "gülmek", "pos": "verb", "kind": "converb_ken", "kwargs": {"base": "aorist"}}],
    "olurken":  [{"lemma": "olmak",  "pos": "verb", "kind": "converb_ken", "kwargs": {"base": "aorist"}}],
    "yaparken": [{"lemma": "yapmak", "pos": "verb", "kind": "converb_ken", "kwargs": {"base": "aorist"}}],
    "koşarken": [{"lemma": "koşmak", "pos": "verb", "kind": "converb_ken", "kwargs": {"base": "aorist"}}],
    # --- fiil diğer tabanlar ---
    "geliyorken": [{"lemma": "gelmek", "pos": "verb", "kind": "converb_ken", "kwargs": {"base": "pres"}}],
    "okuyorken":  [{"lemma": "okumak", "pos": "verb", "kind": "converb_ken", "kwargs": {"base": "pres"}}],   # -Iyor
    "gelmişken":  [{"lemma": "gelmek", "pos": "verb", "kind": "converb_ken", "kwargs": {"base": "evid"}}],
    "gelecekken": [{"lemma": "gelmek", "pos": "verb", "kind": "converb_ken", "kwargs": {"base": "fut"}}],    # çift-k korunur
    "gidecekken": [{"lemma": "gitmek", "pos": "verb", "kind": "converb_ken", "kwargs": {"base": "fut"}}],    # t→d yumuşama
    # --- fiil olumsuz ---
    "gelmezken":     [{"lemma": "gelmek", "pos": "verb", "kind": "converb_ken", "kwargs": {"base": "aorist", "negative": True}}],
    "gelmiyorken":   [{"lemma": "gelmek", "pos": "verb", "kind": "converb_ken", "kwargs": {"base": "pres",   "negative": True}}],
    "gelmeyecekken": [{"lemma": "gelmek", "pos": "verb", "kind": "converb_ken", "kwargs": {"base": "fut",    "negative": True}}],
    # --- nominal (copula aux=ken) ---
    "çocukken":    [{"lemma": "çocuk",    "pos": "noun", "kind": "copula", "kwargs": {"aux": "ken"}}],            # ünsüz-final → glide yok
    "öğretmenken": [{"lemma": "öğretmen", "pos": "noun", "kind": "copula", "kwargs": {"aux": "ken"}}],
    "gençken":     [{"lemma": "genç",     "pos": "noun", "kind": "copula", "kwargs": {"aux": "ken"}}],
    "hastayken":   [{"lemma": "hasta",    "pos": "noun", "kind": "copula", "kwargs": {"aux": "ken"}}],           # ünlü-final → glide y
    "evdeyken":    [{"lemma": "ev",       "pos": "noun", "kind": "copula", "kwargs": {"aux": "ken", "case": "loc"}}],
    "okuldayken":  [{"lemma": "okul",     "pos": "noun", "kind": "copula", "kwargs": {"aux": "ken", "case": "loc"}}],
    "kapıdayken":  [{"lemma": "kapı",     "pos": "noun", "kind": "copula", "kwargs": {"aux": "ken", "case": "loc"}}],
    # --- BELİRSİZ: hem fiil hem gerçek isim ---
    "gelirken": [
        {"lemma": "gelmek", "pos": "verb", "kind": "converb_ken", "kwargs": {"base": "aorist"}},
        {"lemma": "gelir",  "pos": "noun", "kind": "copula",      "kwargs": {"aux": "ken"}},   # gelir = income
    ],
    "giderken": [
        {"lemma": "gitmek", "pos": "verb", "kind": "converb_ken", "kwargs": {"base": "aorist"}},
        {"lemma": "gider",  "pos": "noun", "kind": "copula",      "kwargs": {"aux": "ken"}},   # gider = expense
    ],
    "yazarken": [
        {"lemma": "yazmak", "pos": "verb", "kind": "converb_ken", "kwargs": {"base": "aorist"}},
        {"lemma": "yazar",  "pos": "noun", "kind": "copula",      "kwargs": {"aux": "ken"}},   # yazar = author
    ],
}

# (surface) -> {"lemma": ..., "segments": [(dilim, etiket), ...]} — tek-çözümlü sade yüzeyler.
GOLDEN_KEN_SEGMENTS = {
    # fiil
    "okurken":    {"lemma": "okumak", "segments": [("oku", "KÖK"), ("r", "Ir"), ("ken", "ken")]},
    "bakarken":   {"lemma": "bakmak", "segments": [("bak", "KÖK"), ("ar", "Ir"), ("ken", "ken")]},
    "gülerken":   {"lemma": "gülmek", "segments": [("gül", "KÖK"), ("er", "Ir"), ("ken", "ken")]},
    "geliyorken": {"lemma": "gelmek", "segments": [("gel", "KÖK"), ("iyor", "Iyor"), ("ken", "ken")]},
    "gelmişken":  {"lemma": "gelmek", "segments": [("gel", "KÖK"), ("miş", "mIş"), ("ken", "ken")]},
    "gelecekken": {"lemma": "gelmek", "segments": [("gel", "KÖK"), ("ecek", "AcAk"), ("ken", "ken")]},
    # nominal
    "çocukken":   {"lemma": "çocuk", "segments": [("çocuk", "KÖK"), ("ken", "ken")]},
    "gençken":    {"lemma": "genç",  "segments": [("genç", "KÖK"), ("ken", "ken")]},
    "hastayken":  {"lemma": "hasta", "segments": [("hasta", "KÖK"), ("yken", "ken")]},
    "evdeyken":   {"lemma": "ev",    "segments": [("ev", "KÖK"), ("de", "loc"), ("yken", "ken")]},
    "kapıdayken": {"lemma": "kapı",  "segments": [("kapı", "KÖK"), ("da", "loc"), ("yken", "ken")]},
}

# Precision testi için lemma kümesi (roots): golden'daki tüm lemma'lar.
KEN_LEXICON = frozenset(
    g["lemma"] for entries in GOLDEN_KEN.values() for g in entries
)
