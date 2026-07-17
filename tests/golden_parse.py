"""E2 constituency parser — bağımsız golden (motor-körü, elle doğrulanmış).

Her giriş:
    text:     giriş cümlesi
    roots:    analyze() roots kümesi (precision için)
    expected: beklenen ağaç {tag, surface, children: [{tag, surface, token?}]}

Basit cümleler: özne + yüklem veya yalnız öbek.
"""

PARSE_CASES = [
    {
        "text": "öğrenci okudu",
        "roots": {"öğrenci", "okumak"},
        "expected": {
            "tag": "S",
            "surface": "öğrenci okudu",
            "children": [
                {"tag": "NP", "surface": "öğrenci",
                 "children": [{"tag": "NOUN", "token": "öğrenci"}]},
                {"tag": "VP", "surface": "okudu",
                 "children": [{"tag": "VERB", "token": "okudu"}]},
            ],
        },
    },
    {
        "text": "büyük ev",
        "roots": {"büyük", "ev"},
        "expected": {
            "tag": "NP",
            "surface": "büyük ev",
            "children": [
                {"tag": "ADJ",  "token": "büyük"},
                {"tag": "NOUN", "token": "ev"},
            ],
        },
    },
    {
        "text": "eve göre",
        "roots": {"ev"},
        "expected": {
            "tag": "PP",
            "surface": "eve göre",
            "children": [
                {"tag": "NP",  "surface": "eve",  "children": [{"tag": "NOUN", "token": "eve"}]},
                {"tag": "ADP", "token": "göre"},
            ],
        },
    },
    {
        "text": "kitap ve defter",
        "roots": {"kitap", "defter"},
        "expected": {
            "tag": "CoordP",
            "surface": "kitap ve defter",
            "children": [
                {"tag": "NP", "surface": "kitap",  "children": [{"tag": "NOUN", "token": "kitap"}]},
                {"tag": "CCONJ", "token": "ve"},
                {"tag": "NP", "surface": "defter", "children": [{"tag": "NOUN", "token": "defter"}]},
            ],
        },
    },
    {
        # AdjP+NOUN: derece+sıfat → AdjP; AdjP+NOUN → NP (R3 önce R1'den)
        "text": "çok büyük ev",
        "roots": {"büyük", "ev"},
        "expected": {
            "tag": "NP",
            "surface": "çok büyük ev",
            "children": [
                {"tag": "AdjP", "surface": "çok büyük",
                 "children": [
                     {"tag": "ADJ", "token": "çok"},
                     {"tag": "ADJ", "token": "büyük"},
                 ]},
                {"tag": "NOUN", "token": "ev"},
            ],
        },
    },
    {
        "text": "öğrenci kitabı okudu",
        "roots": {"öğrenci", "kitap", "okumak"},
        "expected": {
            "tag": "S",
            "surface": "öğrenci kitabı okudu",
            "children": [
                {"tag": "NP", "surface": "öğrenci",
                 "children": [{"tag": "NOUN", "token": "öğrenci"}]},
                {"tag": "VP", "surface": "kitabı okudu",
                 "children": [
                     {"tag": "NP", "surface": "kitabı",
                      "children": [{"tag": "NOUN", "token": "kitabı"}]},
                     {"tag": "VERB", "token": "okudu"},
                 ]},
            ],
        },
    },
]
