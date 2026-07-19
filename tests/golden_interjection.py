"""golden_interjection.py — ünlem + yansıma tanıma bağımsız golden (motor-körü, elle
doğrulanmış; SPEC spec/interjection-onomatopoeia-spec.md).

Recognition additive → ``want ⊆ got``: her giriş için beklenen (pos, kind, lemma)
üçlüsünün analiz kümesinde BULUNMASI sınanır (diğer okumalar da olabilir).
"""

# Temsili ünlemler → (pos, kind, lemma) beklenir (SPEC §2.1 kümesinden elle seçildi)
GOLDEN_INTERJECTION = [
    ("ah", "ünlem", "interjection", "ah"),
    ("of", "ünlem", "interjection", "of"),
    ("eyvah", "ünlem", "interjection", "eyvah"),
    ("aman", "ünlem", "interjection", "aman"),
    ("hey", "ünlem", "interjection", "hey"),
    ("hişt", "ünlem", "interjection", "hişt"),
    ("işte", "ünlem", "interjection", "işte"),
    ("haydi", "ünlem", "interjection", "haydi"),
    ("hadi", "ünlem", "interjection", "hadi"),
    ("marş", "ünlem", "interjection", "marş"),
    ("bravo", "ünlem", "interjection", "bravo"),
    ("aferin", "ünlem", "interjection", "aferin"),
    ("vay", "ünlem", "interjection", "vay"),
    ("yazık", "ünlem", "interjection", "yazık"),
    ("çüş", "ünlem", "interjection", "çüş"),
]

# Temsili yansımalar → (pos, kind, lemma) (SPEC §3.1)
GOLDEN_ONOMATOPOEIA = [
    ("şır", "yansıma", "onomatopoeia", "şır"),
    ("güm", "yansıma", "onomatopoeia", "güm"),
    ("çat", "yansıma", "onomatopoeia", "çat"),
    ("pat", "yansıma", "onomatopoeia", "pat"),
    ("tık", "yansıma", "onomatopoeia", "tık"),
    ("miyav", "yansıma", "onomatopoeia", "miyav"),
    ("hav", "yansıma", "onomatopoeia", "hav"),
    ("gümbür", "yansıma", "onomatopoeia", "gümbür"),
    ("şırıl", "yansıma", "onomatopoeia", "şırıl"),
    ("vız", "yansıma", "onomatopoeia", "vız"),
]

# Büyük-harf normalizasyonu (İ→i, I→ı): analyze() _tr_lower uygular → yine tanınmalı
GOLDEN_NORMALIZED = [
    ("AH", "ünlem", "interjection", "ah"),
    ("Eyvah", "ünlem", "interjection", "eyvah"),
    ("ÇAT", "yansıma", "onomatopoeia", "çat"),
]

# Belirsizlik (additive): ünlem/yansıma okuması VAR ama TEK okuma DEĞİL.
# (yüzey, beklenen_kind) — kind analiz kümesinde bulunmalı, ama >1 analiz olmalı.
GOLDEN_AMBIGUOUS = [
    ("of", "interjection"),    # + ofmak imp + of isim
    ("ay", "interjection"),    # + ay isim (gökcisim)
    ("işte", "interjection"),  # + iş+loc
    ("çat", "onomatopoeia"),   # + çatmak imp
    ("güm", "onomatopoeia"),
]

# Negatif: küme dışı → ünlem/yansıma etiketi ÜRETİLMEMELİ
GOLDEN_NEGATIVE = [
    "masa", "gelmek", "kırmızı", "kitap", "ev", "güzel", "koşmak",
]
