"""golden_reduplication_analysis.py — Faz 9d ikileme analiz golden (motor-körü).

Motordan BAĞIMSIZ kurulmuş, elle-doğrulanmış ikileme analiz beklentileri.
Üç ikileme türü:
  - reduplication_full     : tam ikileme (yavaş yavaş, ev ev)
  - reduplication_converb  : ulaç ikilemesi (koşa koşa → koşmak, verb)
  - reduplication_m        : m-ikilemesi (kitap mitap → kitap)

Doğrulama şablonu:
    result = analyze(surface, roots=roots)
    assert any(
        r.lemma == expected["lemma"]
        and r.kind == expected["kind"]
        and r.pos == expected["pos"]
        for r in result
    )

NOT: pos=None girdileri test sırasında pos eşleşmesini gevşetir (atlanabilir).
"""

# --- Tam ikileme -----------------------------------------------------------
# kind = "reduplication_full", lemma = tekrarlanan sözcük (token1).
# pos: sözcüğün sözlük POS'u; fiil-türevli/belirsiz biçimler için None.
GOLDEN_FULL_ANALYSIS: list[dict] = [
    {"surface": "yavaş yavaş", "lemma": "yavaş", "kind": "reduplication_full", "pos": "adj"},
    {"surface": "güzel güzel", "lemma": "güzel", "kind": "reduplication_full", "pos": "adj"},
    {"surface": "büyük büyük", "lemma": "büyük", "kind": "reduplication_full", "pos": "adj"},
    {"surface": "yeni yeni", "lemma": "yeni", "kind": "reduplication_full", "pos": "adj"},
    {"surface": "sıcak sıcak", "lemma": "sıcak", "kind": "reduplication_full", "pos": "adj"},
    {"surface": "ev ev", "lemma": "ev", "kind": "reduplication_full", "pos": "noun"},
    {"surface": "kapı kapı", "lemma": "kapı", "kind": "reduplication_full", "pos": "noun"},
    {"surface": "adım adım", "lemma": "adım", "kind": "reduplication_full", "pos": "noun"},
    # Fiil-türevli ulaç biçimi aynı zamanda full olarak da çözülebilir (roots'ta
    # "koşa"/"güle" varsa). POS belirsiz → None.
    {"surface": "koşa koşa", "lemma": "koşa", "kind": "reduplication_full", "pos": None},
    {"surface": "güle güle", "lemma": "güle", "kind": "reduplication_full", "pos": None},
]

# --- Ulaç ikilemesi --------------------------------------------------------
# kind = "reduplication_converb", lemma = fiil mastarı, pos = "verb".
# SADECE roots sağlandığında döner (roots=None → converb analizi YOK).
GOLDEN_CONVERB_ANALYSIS: list[dict] = [
    {"surface": "koşa koşa", "lemma": "koşmak", "kind": "reduplication_converb", "pos": "verb"},
    {"surface": "güle güle", "lemma": "gülmek", "kind": "reduplication_converb", "pos": "verb"},
    {"surface": "gide gide", "lemma": "gitmek", "kind": "reduplication_converb", "pos": "verb"},
    {"surface": "gele gele", "lemma": "gelmek", "kind": "reduplication_converb", "pos": "verb"},
    {"surface": "yiye yiye", "lemma": "yemek", "kind": "reduplication_converb", "pos": "verb"},
    {"surface": "okuya okuya", "lemma": "okumak", "kind": "reduplication_converb", "pos": "verb"},
    {"surface": "ağlaya ağlaya", "lemma": "ağlamak", "kind": "reduplication_converb", "pos": "verb"},
    {"surface": "çalışa çalışa", "lemma": "çalışmak", "kind": "reduplication_converb", "pos": "verb"},
    {"surface": "düşüne düşüne", "lemma": "düşünmek", "kind": "reduplication_converb", "pos": "verb"},
    {"surface": "bile bile", "lemma": "bilmek", "kind": "reduplication_converb", "pos": "verb"},
]

# --- M-ikilemesi -----------------------------------------------------------
# kind = "reduplication_m", lemma = orijinal sözcük (token1).
# İkinci token m- ile başlar (ünlü-başlıda m+kök, ünsüz-başlıda ilk ünsüz→m).
GOLDEN_M_ANALYSIS: list[dict] = [
    {"surface": "kitap mitap", "lemma": "kitap", "kind": "reduplication_m", "pos": "noun"},
    {"surface": "çiçek miçek", "lemma": "çiçek", "kind": "reduplication_m", "pos": "noun"},
    {"surface": "araba maraba", "lemma": "araba", "kind": "reduplication_m", "pos": "noun"},
    {"surface": "ev mev", "lemma": "ev", "kind": "reduplication_m", "pos": "noun"},
    {"surface": "kalem malem", "lemma": "kalem", "kind": "reduplication_m", "pos": "noun"},
    {"surface": "para mara", "lemma": "para", "kind": "reduplication_m", "pos": "noun"},
    {"surface": "insan minsan", "lemma": "insan", "kind": "reduplication_m", "pos": "noun"},
    {"surface": "bardak mardak", "lemma": "bardak", "kind": "reduplication_m", "pos": "noun"},
    {"surface": "dost most", "lemma": "dost", "kind": "reduplication_m", "pos": "noun"},
    {"surface": "şeker meker", "lemma": "şeker", "kind": "reduplication_m", "pos": "noun"},
]

# --- roots=None durumu -----------------------------------------------------
# Bu yüzeyler için analyze(surface, roots=None) → reduplication_converb OLMAMALI.
# (converb ikilemesi ancak leksikon köküyle üretilebildiği için opt-in.)
GOLDEN_ROOTS_NONE: list[str] = [
    "koşa koşa",
    "güle güle",
    "gide gide",
]
