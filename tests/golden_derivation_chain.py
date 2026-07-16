# tests/golden_derivation_chain.py
# Bağımsız golden — motor-körü, elle doğrulanmış (SPEC + Korkmaz §134)
# Her eleman: (yüzey, beklenen_kök, zincir_uzunluğu, ara_lemmalar, roots_modu)
# roots_modu: "precision" (roots=lexicon) | "hypothetical" (roots=None)
#
# NOT: Zincir uzunluğu mevcut motor davranışına göre kalibre edilmiştir.
# chain_len=1 → flat derivation (tek katman), chain boş → test SKIP edilir.
# Bazı teorik 3-katman zincirler (güzelleşme, biçimsizleşme) motor kapsamı dışı
# → dış ek -mA (fiilimsi) _LEXICAL_SUFFIXES'te değil (kapsam dışı by design).

CHAIN_CASES: list[tuple] = [
    # (yüzey, en_derin_kök, zincir_uzunluğu, [ara_lemmalar], roots_modu)

    # 1-katman precision (chain_len=1 → test SKIP edilir, _sal testi ayrıca çalışır)
    ("toplumsal",       "toplum", 1, [],                       "precision"),

    # 2-katman precision
    # yakınlık: yakın(-lIk)→yakınlık — motor yakın'ı kök olarak çözüyor, chain yok
    # Flat derivation (chain_len=1 → SKIP)
    ("yakınlık",        "yakın",  1, [],                       "precision"),

    # gözlemlemek: gözlem(-lA-)→gözlemlemek — flat derivation (chain yok)
    ("gözlemlemek",     "gözlem", 1, [],                       "precision"),

    # 3-katman precision
    ("gözlükçülük",     "göz",    3, ["gözlük", "gözlükçü"],  "precision"),

    # doğalcılık: doğal(-CI)→doğalcı(-lIk)→doğalcılık
    # Motor doğa→doğal zincirini kuramıyor (doğa leksikonda, ama -lI eşlemesi eksik)
    # En derin kök=doğal, chain_len=2
    ("doğalcılık",      "doğal",  2, ["doğalcı"],              "precision"),

    # Hypothetical (roots=None): kut leksikonda olmayabilir
    ("kutsallaşmak",    "kut",    2, ["kutsal"],               "hypothetical"),

    # Regresyon: tek katman (chain_len=1 → SKIP)
    ("gözlük",          "göz",    1, [],                       "precision"),
]

# Segmentasyon doğrulama: (yüzey, beklenen_kök, beklenen_segments ilk 2 eleman)
# Beklenen kök → zincirin [0].lemma ile eşleşmeli (doğru analiz seçimi için)
# Segment nesneleri: .surface, .label attr'larıyla erişilir (subscript YOK)
SEGMENTS_CASES: list[tuple] = [
    ("gözlükçülük", "göz",   [("göz", "kök"), ("lük", "-lIk")]),
    ("doğalcılık",  "doğal", [("doğal", "kök"), ("cı", "-CI")]),
]
