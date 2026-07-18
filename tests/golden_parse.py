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
    # --- İkileme adverbial (Faz E-devamı) ---
    {   # tam ikileme → AdvP, VP içinde
        "text": "yavaş yavaş yürüdü",
        "roots": {"yavaş", "yürümek"},
        "expected": {
            "tag": "S",
            "children": [
                {"tag": "VP", "children": [
                    {"tag": "AdvP", "surface": "yavaş yavaş"},
                    {"tag": "VERB", "token": "yürüdü"},
                ]},
            ],
        },
    },
    {   # ulaç ikilemesi → AdvP (VERB çifti), başıboş VERB kalmaz
        "text": "koşa koşa geldi",
        "roots": {"koşmak", "gelmek"},
        "expected": {
            "tag": "S",
            "children": [
                {"tag": "VP", "children": [
                    {"tag": "AdvP", "surface": "koşa koşa"},
                    {"tag": "VERB", "token": "geldi"},
                ]},
            ],
        },
    },
    {   # adnominal guard: uzun uzun yollar → NP, AdvP YOK
        "text": "uzun uzun yollar",
        "roots": {"uzun", "yol"},
        "expected": {"tag": "NP", "surface": "uzun uzun yollar"},
    },
    {   # derece-çift: çok çok güzel → AdvP (sonraki NOUN değil). Kök S (güzel ADJ kalır → S'ye sarılır).
        "text": "çok çok güzel",
        "roots": {"güzel"},
        "expected": {
            "tag": "S",
            "children": [
                {"tag": "AdvP", "surface": "çok çok"},
                {"tag": "ADJ", "token": "güzel"},
            ],
        },
    },
    {   # derece-çift + NOUN: guard skip → NP (adnominal)
        "text": "çok çok kitap",
        "roots": {"kitap"},
        "expected": {"tag": "NP", "surface": "çok çok kitap"},
    },
    # --- m-İkileme nominal (Faz E-devamı) ---
    {   # NOUN m-ikileme → NP; yalın nom → özne konumu (kitap aldı emsali)
        "text": "kitap mitap aldı",
        "roots": {"kitap", "almak"},
        "expected": {
            "tag": "S",
            "children": [
                {"tag": "NP", "surface": "kitap mitap"},
                {"tag": "VP", "children": [
                    {"tag": "VERB", "token": "aldı"},
                ]},
            ],
        },
    },
    {   # ünlü-başlı m-form (araba → maraba)
        "text": "araba maraba aldı",
        "roots": {"araba", "almak"},
        "expected": {
            "tag": "S",
            "children": [
                {"tag": "NP", "surface": "araba maraba"},
                {"tag": "VP", "children": [
                    {"tag": "VERB", "token": "aldı"},
                ]},
            ],
        },
    },
    {   # yüklemsiz m-ikileme → NP kök (X başıboş kalmaz)
        "text": "kitap mitap",
        "roots": {"kitap"},
        "expected": {"tag": "NP", "surface": "kitap mitap"},
    },
    {   # REGRESYON: m-değil bitişik NOUN çifti → m-NP KURULMAZ (mevcut davranış)
        "text": "kitap kalem",
        "roots": {"kitap", "kalem"},
        "expected": {
            "tag": "S",
            "children": [
                {"tag": "NP", "surface": "kitap"},
                {"tag": "NP", "surface": "kalem"},
            ],
        },
    },
]
