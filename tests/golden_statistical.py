# İstatistiksel disambiguation golden (Faz 2b — madde A, Artım-1 + Artım-2).
# BAĞIMSIZ: motor-körü olarak yalnız spec/statistical-disambiguation-spec.md +
# Türkçe dilbilgisi + TrMor2018 formatıyla kuruldu (turkgram/statistical.py görülmeden).
# Runner: tests/test_statistical.py
#
# Üç aile:
#   1. MAPPING_CASES   — Oflazer etiket dizgesi → (lemma, major_pos) Artım-1 eşlemesi
#   2. COUNT_CASES     — mini-korpus elle sayımı (emisyon + geçiş beklentisi)
#   3. VITERBI_CASES   — belirsiz cümle → HMM Viterbi yolu (elle çözülmüş)
#
# SPEC §5 Artım-1: yalnız (kök, major POS) hizalanır; ince eksenler göz ardı.
# major_pos değerleri: "Noun", "Verb", "Adj", "Adverb", "Postp", "Num", "Det",
#                      "Pron", "Punc", "Conj", "Interj", "Prop"
# Bilinmeyen/eşlenemeyen etiket → major_pos = "unmapped"

# ─── AİLE 1: Eşleme golden'ı ───────────────────────────────────────────────
# Her girdi: (oflazer_analiz_dizgesi, beklenen_lemma, beklenen_major_pos)
# Oflazer format: lemma+Tag+Tag...  veya  lemma+Tag^DB+...  (^DB türetme sınırı)
# Kural: ^DB zincirinde SON inflectional group'un POS'u major_pos'tur (SPEC §5 Artım-1).
# Kural: kök = ilk group'un lemması (küçük-harf normalizasyonu uygulanmaz).

MAPPING_CASES = [
    # --- Basit isimler ---
    ("hazine+Noun+A3sg+Pnon+Nom",           "hazine",   "Noun"),
    ("kitap+Noun+A3pl+Pnon+Acc",            "kitap",    "Noun"),
    ("Hazine+Noun+Prop+A3sg+Pnon+Nom",      "Hazine",   "Noun"),   # özel isim — Prop Oflazer'de Noun sub-feature; Artım-1 → Noun
    ("merkez+Noun+A3sg+Pnon+Nom",           "merkez",   "Noun"),

    # --- Fiiller ---
    ("gel+Verb+Pos+Past+A3sg",              "gel",      "Verb"),
    ("rahatla+Verb+Pos+Past+A3sg",          "rahatla",  "Verb"),
    ("yap+Verb+Pos+Past+A3sg",              "yap",      "Verb"),
    ("gözle+Verb+Pass+Pos+Past+A3sg",       "gözle",    "Verb"),

    # --- Sıfatlar ---
    ("geçen+Adj",                           "geçen",    "Adj"),
    ("kısa+Adj",                            "kısa",     "Adj"),
    ("kırmızı+Adj",                         "kırmızı",  "Adj"),

    # --- Zarflar ---
    ("geri+Adverb",                         "geri",     "Adverb"),
    ("hemen+Adverb",                        "hemen",    "Adverb"),

    # --- Edatlar ---
    ("için+Postp+PCGen",                    "için",     "Postp"),
    ("kadar+Postp+PCNom",                   "kadar",    "Postp"),

    # --- Sayılar ---
    ("48.7+Num+Real",                       "48.7",     "Num"),
    ("trilyon+Num+Card",                    "trilyon",  "Num"),
    ("üç+Num+Card",                         "üç",       "Num"),

    # --- Zamir ---
    ("bu+Pron+Demons+A3sg+Pnon+Nom",        "bu",       "Pron"),
    ("ben+Pron+Pers+A1sg+Pnon+Nom",         "ben",      "Pron"),

    # --- Belirteç ---
    ("bu+Det",                              "bu",       "Det"),
    ("her+Det",                             "her",      "Det"),

    # --- Noktalama ---
    (",+Punct",                             ",",        "Punc"),
    (".+Punct",                             ".",        "Punc"),

    # --- ^DB zinciri: SON group'un POS'u alınır ---
    # rahatla+Verb^DB+Verb+Caus+Pos+Past+A3sg  → kök=rahatla, major_pos=Verb (son group Verb)
    ("rahatla+Verb^DB+Verb+Caus+Pos+Past+A3sg",  "rahatla",  "Verb"),
    # hazin+Adj^DB+Noun+Zero+A3sg+Pnon+Dat       → kök=hazin,  major_pos=Noun (son group Noun)
    ("hazin+Adj^DB+Noun+Zero+A3sg+Pnon+Dat",     "hazin",    "Noun"),
    # vade+Noun^DB+Adj+With                       → kök=vade,  major_pos=Adj
    ("vade+Noun+A3sg+Pnon+Nom^DB+Adj+With",      "vade",     "Adj"),
    # yap+Verb+Pos^DB+Adj+PresPart                → kök=yap,   major_pos=Adj (son group Adj)
    ("yap+Verb+Pos^DB+Adj+PresPart",              "yap",      "Adj"),
    # öde+Verb+Pos^DB+Noun+Inf2+A3sg+Pnon+Nom    → kök=öde,   major_pos=Noun
    ("öde+Verb+Pos^DB+Noun+Inf2+A3sg+Pnon+Nom",  "öde",      "Noun"),
    # kullan+Verb+Pos^DB+Verb+Able^DB+Adj+FutPart+P3sg → kök=kullan, son group=Adj
    ("kullan+Verb+Pos^DB+Verb+Able^DB+Adj+FutPart+P3sg", "kullan", "Adj"),

    # --- Bilinmeyen/eşlenemeyen → "unmapped" ---
    # Türkçe NLP'de nadir görülen etiketler; harness'te ayrı sınıf
    ("bilinmeyen+XYZ+Foo",                  "bilinmeyen", "unmapped"),
    ("test+Interj",                         "test",       "Interj"),  # Interj destekleniyor
]

# ─── AİLE 2: Sayım golden'ı ────────────────────────────────────────────────
# Mini-korpus (elle-tasarlanmış 4 cümle, ~16 token).
# Her cümle: [(yüzey, doğru_analiz_dizgesi), ...]
# Beklenen EMISYON sayımları: {(major_pos, yüzey): count}
# Beklenen GEÇİŞ sayımları (bigram, <S>→ilk, son→</S>): {(prev_pos, next_pos): count}
#
# Mini-korpus (Türkçe, basit, belirsiz token içermeyen):
#   S1: Hazine Merkez'i rahatlattı.
#       [(Hazine, Noun/Prop), (Merkez'i, Noun/Prop), (rahatlattı, Verb), (., Punc)]
#   S2: Geçen hafta kısa vadeli avans hesabına para yatırdı.
#       [(Geçen, Adj), (hafta, Noun), (kısa, Adj), (vadeli, Adj), (avans, Noun),
#        (hesabına, Noun), (para, Noun), (yatırdı, Verb), (., Punc)]
#   S3: Merkez Bankası kaynakları düzeltti.
#       [(Merkez, Noun), (Bankası, Noun), (kaynakları, Noun), (düzeltti, Verb), (., Punc)]
#   S4: Geri ödeme yapan Hazine rahatlattı.
#       [(Geri, Adverb), (ödeme, Noun), (yapan, Adj), (Hazine, Noun), (rahatlattı, Verb), (., Punc)]
#
# Elle sayım — emisyon (major_pos, lower(yüzey)): doğru analiz'in major_pos'u ile
# NOT: yüzey küçük harfe normalize edilir; birden fazla cümlede aynı (pos,yüzey) → toplam

MINI_CORPUS = [
    # S1
    [("Hazine",   "Hazine+Noun+Prop+A3sg+Pnon+Nom"),
     ("Merkezi",  "Merkez+Noun+Prop+A3sg+Pnon+Acc"),
     ("rahatlattı", "rahatla+Verb+Caus+Pos+Past+A3sg"),
     (".",         ".+Punct")],
    # S2
    [("Geçen",    "geçen+Adj"),
     ("hafta",    "hafta+Noun+A3sg+Pnon+Nom"),
     ("kısa",     "kısa+Adj"),
     ("vadeli",   "vade+Noun+A3sg+Pnon+Nom^DB+Adj+With"),
     ("avans",    "avans+Noun+A3sg+Pnon+Nom"),
     ("hesabına", "hesap+Noun+A3sg+P3sg+Dat"),
     ("para",     "para+Noun+A3sg+Pnon+Nom"),
     ("yatırdı",  "yatır+Verb+Pos+Past+A3sg"),
     (".",         ".+Punct")],
    # S3
    [("Merkez",     "Merkez+Noun+Prop+A3sg+Pnon+Nom"),
     ("Bankası",    "banka+Noun+A3sg+P3sg+Nom"),
     ("kaynakları", "kaynak+Noun+A3pl+P3sg+Acc"),
     ("düzeltti",   "düzel+Verb+Caus+Pos+Past+A3sg"),
     (".",           ".+Punct")],
    # S4
    [("Geri",       "geri+Adverb"),
     ("ödeme",      "öde+Verb+Pos^DB+Noun+Inf2+A3sg+Pnon+Nom"),
     ("yapan",      "yap+Verb+Pos^DB+Adj+PresPart"),
     ("Hazine",     "Hazine+Noun+Prop+A3sg+Pnon+Nom"),
     ("rahatlattı", "rahatla+Verb+Caus+Pos+Past+A3sg"),
     (".",           ".+Punct")],
]

# Elle-hesaplanan beklenen emisyon sayımları (major_pos, lower(surface)): count
# Artım-1: Prop, Oflazer'de Noun'ın sub-feature'ıdır (+Noun+Prop+) → major_pos = Noun
EXPECTED_EMISSION_COUNTS = {
    ("Noun",    "hazine"):      2,   # S1 + S4 (Hazine → Noun; Prop sub-feature)
    ("Noun",    "merkezi"):     1,   # S1
    ("Verb",    "rahatlattı"):  2,   # S1 + S4
    ("Punc",    "."):           4,   # dört cümle
    ("Adj",     "geçen"):       1,
    ("Noun",    "hafta"):       1,
    ("Adj",     "kısa"):        1,
    ("Adj",     "vadeli"):      1,   # ^DB zinciri → son POS = Adj
    ("Noun",    "avans"):       1,
    ("Noun",    "hesabına"):    1,
    ("Noun",    "para"):        1,
    ("Verb",    "yatırdı"):     1,
    ("Noun",    "merkez"):      1,   # S3 (Merkez+Noun+Prop → Noun)
    ("Noun",    "bankası"):     1,
    ("Noun",    "kaynakları"):  1,
    ("Verb",    "düzeltti"):    1,
    ("Adverb",  "geri"):        1,
    ("Noun",    "ödeme"):       1,   # ^DB zinciri → son POS = Noun
    ("Adj",     "yapan"):       1,   # ^DB zinciri → son POS = Adj
}

# Elle-hesaplanan beklenen geçiş sayımları (bigram)
# <S> = cümle başı, </S> = cümle sonu semboller
# Artım-1: Prop → Noun (Oflazer'de Noun sub-feature)
# S1: <S>→Noun, Noun→Noun, Noun→Verb, Verb→Punc, Punc→</S>
# S2: <S>→Adj, Adj→Noun, Noun→Adj, Adj→Adj, Adj→Noun, Noun→Noun, Noun→Noun, Noun→Verb, Verb→Punc, Punc→</S>
# S3: <S>→Noun, Noun→Noun, Noun→Noun, Noun→Verb, Verb→Punc, Punc→</S>
# S4: <S>→Adverb, Adverb→Noun, Noun→Adj, Adj→Noun, Noun→Verb, Verb→Punc, Punc→</S>
EXPECTED_TRANSITION_COUNTS = {
    ("<S>",    "Noun"):     2,   # S1, S3 (Prop → Noun)
    ("<S>",    "Adj"):      1,   # S2
    ("<S>",    "Adverb"):   1,   # S4
    ("Noun",   "Noun"):     5,   # S1: Hazine→Merkezi; S2: avans→hesabına, hesabına→para; S3: Merkez→Bankası, Bankası→kaynakları
    ("Noun",   "Verb"):     4,   # S1: Merkezi→rahatlattı; S2: para→yatırdı; S3: kaynakları→düzeltti; S4: Hazine→rahatlattı
    ("Verb",   "Punc"):     4,   # tüm cümleler
    ("Punc",   "</S>"):     4,
    ("Adj",    "Noun"):     3,   # S2: Geçen→hafta, vadeli→avans; S4: yapan→Hazine(Noun); toplam 3
    ("Noun",   "Adj"):      2,   # S2: hafta→kısa, S4: ödeme→yapan
    ("Adj",    "Adj"):      1,   # S2: kısa→vadeli
    ("Adverb", "Noun"):     1,   # S4: geri→ödeme
}
# S2 Adj→Noun: Geçen→hafta + vadeli→avans = 2.
# S4 yapan(Adj)→Hazine(Noun) = 1. Toplam = 3.
# NOT: önceki Prop ayrımı kaldırıldı; hepsi Noun.

# ─── AİLE 3: Viterbi golden'ı ──────────────────────────────────────────────
# Elle-tasarlanmış belirsiz cümleler; HMM Viterbi yolu elle çözüldü.
# Eğitim verisinde tahmin edilen geçiş olasılıkları ve "makul" emisyon
# varsayımlarıyla (gerçek model parametreleri değil; MANTIKSAL sıra).
#
# Format: (tokens, analyses_per_token, expected_pos_sequence)
# analyses_per_token: her token için aday (lemma, major_pos) listesi
# expected_pos_sequence: beklenen Viterbi tarafından seçilen major_pos dizisi
#
# Not: Bu golden, HMM'in "doğru" bağlamsal seçim yapmasını değil,
# MANTIKSAL dizi uyumu gözetmesini sınar.
# Seçim gerekçesi her girdi yanında yorumda açıklanır.

VITERBI_CASES = [
    # ──────────────────────────────────────────────────────────────────────
    # Case V1: "üç gelin"
    # Token 0 "üç": Num (sayı anlamında; tek aday)
    # Token 1 "gelin": [("gelin", "Noun"), ("gel", "Verb")]
    # Beklenti: Num→Noun (K1 ile örtüşür; istatistiksel geçiş Num→Noun >> Num→Verb)
    (
        ["üç", "gelin"],
        [
            [("üç", "Num")],
            [("gelin", "Noun"), ("gel", "Verb")],
        ],
        ["Num", "Noun"],
    ),

    # ──────────────────────────────────────────────────────────────────────
    # Case V2: "kırmızı gül"
    # Token 0 "kırmızı": Adj (tek aday)
    # Token 1 "gül": [("gül", "Noun"), ("gül", "Verb")]
    # Beklenti: Adj→Noun (niteleyici+ad; geçiş Adj→Noun > Adj→Verb)
    (
        ["kırmızı", "gül"],
        [
            [("kırmızı", "Adj")],
            [("gül", "Noun"), ("gül", "Verb")],
        ],
        ["Adj", "Noun"],
    ),

    # ──────────────────────────────────────────────────────────────────────
    # Case V3: "ben geldim"
    # Token 0 "ben": Pron (1sg özne; tek aday)
    # Token 1 "geldim": [("gel", "Verb")] (tek; kişi uyumu Verb zaten doğru)
    # Beklenti: Pron→Verb
    (
        ["ben", "geldim"],
        [
            [("ben", "Pron")],
            [("gel", "Verb")],
        ],
        ["Pron", "Verb"],
    ),

    # ──────────────────────────────────────────────────────────────────────
    # Case V4: "geldi mi"
    # Token 0 "geldi": [("gel", "Verb")] (tek; question=False olmadan fiil)
    # Token 1 "mi": [("mi", "Punc"), ("mi", "Det")]
    # Türkçe'de ayrı yazılan soru parçacığı dilbilimsel açıdan fiil sonrası gelir.
    # Geçiş Verb→Punc (noktalama geniş kategoride) > Verb→Det
    # Beklenti: Verb→Punc  (soru parçacığı Punc kategorisine düşer; makul modelde)
    (
        ["geldi", "mi"],
        [
            [("gel", "Verb")],
            [("mi", "Punc"), ("mi", "Det")],
        ],
        ["Verb", "Punc"],
    ),

    # ──────────────────────────────────────────────────────────────────────
    # Case V5: üç token — "her güzel kız"
    # Token 0 "her": Det (belirteç; tek aday)
    # Token 1 "güzel": Adj (tek aday)
    # Token 2 "kız": [("kız", "Noun"), ("kız", "Verb")]
    # Beklenti: Det→Adj→Noun (niteleyici zinciri; Det→Adj→Noun >> Det→Adj→Verb)
    (
        ["her", "güzel", "kız"],
        [
            [("her", "Det")],
            [("güzel", "Adj")],
            [("kız", "Noun"), ("kız", "Verb")],
        ],
        ["Det", "Adj", "Noun"],
    ),
]
