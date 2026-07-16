"""golden_conjunction.py — Faz 5 D4 bağımsız golden (motor-körü, elle doğrulanmış)."""

# GOLDEN_CONJOIN: list of (word, conj, expected_output)
GOLDEN_CONJOIN = [
    # de/da — ön ünlü → "de"
    ("eve", "de", "eve de"),       # e → ön
    ("elde", "de", "elde de"),     # e → ön
    ("ilde", "de", "ilde de"),     # i → ön
    ("göze", "de", "göze de"),     # ö → ön
    ("güle", "de", "güle de"),     # ü → ön
    ("köye", "de", "köye de"),     # ö → ön
    ("sine", "de", "sine de"),     # i → ön
    ("öze", "de", "öze de"),       # ö → ön
    # de/da — art ünlü → "da"
    ("okula", "da", "okula da"),   # a → art
    ("yolda", "da", "yolda da"),   # a → art (yolda zaten da, ama kelime olarak)
    ("kapıya", "da", "kapıya da"), # a → art
    ("oda", "da", "oda da"),       # a → art
    ("kola", "da", "kola da"),     # o → art
    ("duma", "da", "duma da"),     # u → art
    ("ışıkta", "da", "ışıkta da"), # ı → art
    ("durağa", "da", "durağa da"), # a → art
    # de/da — "de" verilse de "da" verilse de ses uyumu kendi sonucunu verir
    ("eve", "da", "eve de"),       # ön ünlü → "de" (da verilse bile)
    ("okula", "de", "okula da"),   # art ünlü → "da" (de verilse bile)
    # fallback: ünlü yok → "de"
    ("NATO", "de", "NATO de"),
    ("3", "da", "3 de"),
    ("AB", "de", "AB de"),
    ("TDK", "da", "TDK de"),
    # ise — ayrı, değişmez
    ("elma", "ise", "elma ise"),
    ("araba", "ise", "araba ise"),
    ("güzel", "ise", "güzel ise"),
    ("o", "ise", "o ise"),
    # diğer koordinatifler
    ("elma", "ve", "elma ve"),
    ("hızlı", "ama", "hızlı ama"),
    ("büyük", "fakat", "büyük fakat"),
    ("geldi", "lakin", "geldi lakin"),
    ("koştu", "ancak", "koştu ancak"),
    ("yağmur", "çünkü", "yağmur çünkü"),
    ("bitti", "oysa", "bitti oysa"),
    ("söyledi", "halbuki", "söyledi halbuki"),
    ("ya da", "ve", "ya da ve"),  # ya da bağlaç kelimesi olarak
    ("veya", "yoksa", "veya yoksa"),
]

# GOLDEN_COORDINATE: list of (items, conj, expected_output)
GOLDEN_COORDINATE = [
    # İkili koordinatif
    (["elma", "armut"], "ve", "elma ve armut"),
    (["hızlı", "güçlü"], "ama", "hızlı ama güçlü"),
    (["geldi", "gitti"], "fakat", "geldi fakat gitti"),
    (["büyük", "küçük"], "ya da", "büyük ya da küçük"),
    (["ev", "araba"], "veya", "ev veya araba"),
    (["yedi", "içti"], "bile", "yedi bile içti"),    # bile koordinatif
    # Üçlü koordinatif
    (["elma", "armut", "kiraz"], "ve", "elma, armut ve kiraz"),
    (["kırmızı", "mavi", "yeşil"], "ya da", "kırmızı, mavi ya da yeşil"),
    (["koştu", "atladı", "düştü"], "ve", "koştu, atladı ve düştü"),
    # Dörtlü koordinatif
    (["a", "b", "c", "d"], "ve", "a, b, c ve d"),
    # Tek öğe
    (["elma"], "ve", "elma"),
    (["hızlı"], "hem_hem", "hızlı"),
    # Korelatifler — hem_hem
    (["hızlı", "güçlü"], "hem_hem", "hem hızlı hem güçlü"),
    (["elma", "armut"], "hem_hem", "hem elma hem armut"),
    # Korelatifler — ya_ya
    (["gelir", "gelmez"], "ya_ya", "ya gelir ya gelmez"),
    (["siyah", "beyaz"], "ya_ya", "ya siyah ya beyaz"),
    # Korelatifler — ne_ne
    (["zengin", "fakir"], "ne_ne", "ne zengin ne fakir"),
    (["güzel", "çirkin"], "ne_ne", "ne güzel ne çirkin"),
    # Korelatifler — ister_ister
    (["büyük", "küçük"], "ister_ister", "ister büyük ister küçük"),
    (["gelsin", "gelmesin"], "ister_ister", "ister gelsin ister gelmesin"),
    # Korelatifler — gerek_gerek
    (["okul", "ev"], "gerek_gerek", "gerek okul gerek ev"),
    (["sabah", "akşam"], "gerek_gerek", "gerek sabah gerek akşam"),
    # Korelatifler — hem_hem_de
    (["akıllı", "güçlü"], "hem_hem_de", "hem akıllı hem de güçlü"),
    (["hızlı", "dayanıklı"], "hem_hem_de", "hem hızlı hem de dayanıklı"),
]

# GOLDEN_ANALYZE: list of (surface, want_subset)
# want_subset: list of dicts; her dict için o alan analizde bulunmalı (want <= got)
GOLDEN_ANALYZE = [
    # "de" — bilinçli belirsizlik: hem bağlaç hem demek imp-2sg
    ("de", [{"kind": "conjunction", "lemma": "de"}, {"kind": "conjugate"}]),
    # "da" — yalnız bağlaç (da için fiil analizi yok)
    ("da", [{"kind": "conjunction", "lemma": "de"}]),
    # "evde" — conjunction DÖNDÜRMEZ (tam-token guard)
    # Bu negatif test: kind="conjunction" kesinlikle OLMAMALI
]

# Negatif analyze testi ayrı tutuldu (pozitif want_subset'ten farklı mantık):
GOLDEN_ANALYZE_NEGATIVE = [
    # surface, banned_kind
    ("evde", "conjunction"),
    ("sende", "conjunction"),
    ("yerde", "conjunction"),
]
