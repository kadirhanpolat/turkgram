# tests/golden_subordinate.py
"""Faz E3/E4 yan cümle — bağımsız golden (motor-körü, elle doğrulanmış).

Her giriş: {"text", "roots" (opsiyonel), "expected": {tag, surface?, children?}}

Ağaç formatı (test_parse.py ile aynı):
  {"tag": "...", "surface": "...", "children": [...]}
  Yaprak: {"tag": "NOUN"|"VERB"|..., "token": "..."}
  Öbek: {"tag": "NP"|"CompP"|..., "children": [...]}

DiyeP testleri için: root.children[0].tag == "DiyeP" kontrolü zorunludur
(spec §6.1 notu: DiyeP S-düzeyinde olmalı, VP içinde DEĞİL).
"""

SUBORDINATE_CASES = [
    # ── E3: ki-cümleleri ──────────────────────────────────────────────────

    {
        # Case 1: CompP — sol VERB + ki + sağ-VERB
        "text": "biliyorum ki geldi",
        "roots": {"bilmek", "gelmek"},
        "expected": {
            "tag": "CompP",
            "surface": "biliyorum ki geldi",
            "children": [
                {"tag": "VERB", "token": "biliyorum"},
                {"tag": "CCONJ", "token": "ki"},
                {"tag": "VERB", "token": "geldi"},
            ],
        },
    },
    {
        # Case 2: RelP — sol NP + ki + sağ-VERB
        # Not: öyle+bir → AdjP (R3), AdjP+şey → NP (R1)
        "text": "öyle bir şey ki gördüm",
        "roots": {"öyle", "bir", "şey", "görmek"},
        "expected": {
            "tag": "RelP",
            "surface": "öyle bir şey ki gördüm",
            "children": [
                {
                    "tag": "NP",
                    "surface": "öyle bir şey",
                    "children": [
                        {
                            "tag": "AdjP",
                            "surface": "öyle bir",
                            "children": [
                                {"tag": "ADJ", "token": "öyle"},
                                {"tag": "ADJ", "token": "bir"},
                            ],
                        },
                        {"tag": "NOUN", "token": "şey"},
                    ],
                },
                {"tag": "CCONJ", "token": "ki"},
                {"tag": "VERB", "token": "gördüm"},
            ],
        },
    },
    {
        # Case 3: E3 geçiş — sol ADJ, R6 ateşlemez → S (ki CCONJ olarak kalır)
        "text": "iyi ki geldin",
        "roots": {"iyi", "gelmek"},
        "expected": {
            "tag": "S",
            "surface": "iyi ki geldin",
        },
    },
    {
        # Case 4: Cümle-başı ki — R6 sol komşu yok, atlar → S
        "text": "ki geldi",
        "roots": {"gelmek"},
        "expected": {
            "tag": "S",
            "surface": "ki geldi",
        },
    },
    {
        # Case 5: NP ki NP — R6 sol=NP → RelP (eski davranış CoordP'ydi)
        "text": "ev ki araba",
        "roots": {"ev", "araba"},
        "expected": {
            "tag": "RelP",
            "surface": "ev ki araba",
            "children": [
                {
                    "tag": "NP",
                    "surface": "ev",
                    "children": [{"tag": "NOUN", "token": "ev"}],
                },
                {"tag": "CCONJ", "token": "ki"},
                {
                    "tag": "NP",
                    "surface": "araba",
                    "children": [{"tag": "NOUN", "token": "araba"}],
                },
            ],
        },
    },

    # ── E4: diye-cümleleri ────────────────────────────────────────────────

    {
        # Case 6: DiyeP alıntı — DiyeP S-düzeyinde (VP içinde DEĞİL)
        # children[0].tag == "DiyeP" kontrolü zorunlu
        "text": "gelir diye bekledi",
        "roots": {"gelmek", "beklemek"},
        "expected": {
            "tag": "S",
            "surface": "gelir diye bekledi",
            "children": [
                {
                    "tag": "DiyeP",
                    "surface": "gelir diye",
                    "children": [
                        {"tag": "VERB", "token": "gelir"},
                        {"tag": "VERB", "token": "diye"},
                    ],
                },
                {
                    "tag": "VP",
                    "surface": "bekledi",
                    "children": [{"tag": "VERB", "token": "bekledi"}],
                },
            ],
        },
    },
    {
        # Case 7: DiyeP amaç — DiyeP S-düzeyinde; kitap yalın NP → R5 özne konumunda bırakır
        # Not: yalın NP VP-dışı (R5 özne sezgisi); kitap belirtisiz nesne ama R5 biçimsel sınır
        "text": "okusun diye kitap aldı",
        "roots": {"okumak", "kitap", "almak"},
        "expected": {
            "tag": "S",
            "surface": "okusun diye kitap aldı",
            "children": [
                {
                    "tag": "DiyeP",
                    "surface": "okusun diye",
                    "children": [
                        {"tag": "VERB", "token": "okusun"},
                        {"tag": "VERB", "token": "diye"},
                    ],
                },
                {
                    "tag": "NP",
                    "surface": "kitap",
                    "children": [{"tag": "NOUN", "token": "kitap"}],
                },
                {
                    "tag": "VP",
                    "surface": "aldı",
                    "children": [{"tag": "VERB", "token": "aldı"}],
                },
            ],
        },
    },
    {
        # Case 8: DiyeP varyant
        "text": "okudu diye sevindi",
        "roots": {"okumak", "sevinmek"},
        "expected": {
            "tag": "S",
            "surface": "okudu diye sevindi",
            "children": [
                {
                    "tag": "DiyeP",
                    "surface": "okudu diye",
                    "children": [
                        {"tag": "VERB", "token": "okudu"},
                        {"tag": "VERB", "token": "diye"},
                    ],
                },
                {
                    "tag": "VP",
                    "surface": "sevindi",
                    "children": [{"tag": "VERB", "token": "sevindi"}],
                },
            ],
        },
    },

    # ── Regresyon: mevcut davranış değişmemeli ────────────────────────────

    {
        # Case 9: Regresyon — ki/diye yok, CoordP
        "text": "kitap ve defter",
        "roots": {"kitap", "defter"},
        "expected": {
            "tag": "CoordP",
            "surface": "kitap ve defter",
            "children": [
                {
                    "tag": "NP",
                    "surface": "kitap",
                    "children": [{"tag": "NOUN", "token": "kitap"}],
                },
                {"tag": "CCONJ", "token": "ve"},
                {
                    "tag": "NP",
                    "surface": "defter",
                    "children": [{"tag": "NOUN", "token": "defter"}],
                },
            ],
        },
    },
    {
        # Case 10: Regresyon — fiilimsi NP (R1b), ki/diye yok
        "text": "okuduğunu biliyorum",
        "roots": {"okumak", "bilmek"},
        "expected": {
            "tag": "S",
            "surface": "okuduğunu biliyorum",
        },
    },
]
