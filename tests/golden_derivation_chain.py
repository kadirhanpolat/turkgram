# tests/golden_derivation_chain.py
# Bağımsız golden — motor-körü, elle doğrulanmış (SPEC + Korkmaz §134)
# Her eleman: (yüzey, beklenen_kök, zincir_uzunluğu, ara_lemmalar, roots_modu)
# roots_modu: "precision" (roots=lexicon) | "hypothetical" (roots=None)

CHAIN_CASES: list[tuple] = [
    # (yüzey, en_derin_kök, zincir_uzunluğu, [ara_lemmalar], roots_modu)

    # 2-katman precision
    ("yakınlık",        "yak",    2, ["yakın"],                "precision"),
    ("güzelleşme",      "güzel",  2, ["güzelleş"],             "precision"),
    ("toplumsal",       "toplum", 1, [],                       "precision"),   # -sAl tek katman

    # 3-katman precision
    ("gözlükçülük",     "göz",    3, ["gözlük", "gözlükçü"],  "precision"),
    ("gözlemlemek",     "göz",    3, ["gözle", "gözlem"],      "precision"),

    # 3-katman precision (ek örnek)
    # doğalcılık: doğa(-lI)→doğal(-CI)→doğalcı(-lIk)→doğalcılık
    ("doğalcılık",      "doğa",   3, ["doğal", "doğalcı"],       "precision"),

    # Çatı sınırı örnekleri (precision)
    # biçimsizleşme: biç→biçim→biçimsiz→biçimsizleş- (çatı: -tIr- dur)
    ("biçimsizleşme",   "biç",    3, ["biçim", "biçimsiz"],   "precision"),

    # Hypothetical (roots=None): kut leksikonda olmayabilir
    ("kutsallaşmak",    "kut",    2, ["kutsal"],               "hypothetical"),

    # Regresyon: max_depth=1 → chain boş (tek katman mevcut davranış)
    ("gözlük",          "göz",    1, [],                       "precision"),   # tek katman
]

# Segmentasyon doğrulama: (yüzey, beklenen_segments ilk 2 eleman)
SEGMENTS_CASES: list[tuple] = [
    ("gözlükçülük", [("göz", "kök"), ("lük", "-lIk")]),
    ("doğalcılık", [("doğa", "kök"), ("l", "-lI")]),
]
