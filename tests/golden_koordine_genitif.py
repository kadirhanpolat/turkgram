"""Koordine genitif tamlayan + özel-isim apostrof-ek merge — bağımsız golden.

MOTOR-KÖRÜ: beklenen ağaçlar dilbilgisinden elle türetildi, motora BAKMADAN;
elle doğrulandı. Format golden_parse.py emsali ({tag, surface, children,
token?}). SPEC: docs/superpowers/specs/2026-07-19-koordine-genitif-tamlayan-design.md

KİLİT KARAR — CoordP konjunktları NP'ye sarılı (golden_parse.py `kitap ve defter`
emsali: her konjunkt `{"tag":"NP", ...}`). Birleşik apostroflu yaprak tek NOUN:
`{"tag":"NOUN","token":"Ali'nin"}`. B1 tek-durum (loc/dat) → tamlama DEĞİL, tek
NOUN yaprağı.
"""

PARSE_CASES = [
    # ------------------------------------------------------------------ #
    # B1 — özel-isim apostrof-ek merge (tek yaprak)
    # ------------------------------------------------------------------ #
    {   # gen possessor + head → NP tamlama; possessor tek birleşik NOUN yaprağı
        "text": "Ali'nin evi",
        "roots": {"ev", "ali"},
        "expected": {
            "tag": "NP",
            "surface": "Ali'nin evi",
            "children": [
                {"tag": "NOUN", "token": "Ali'nin"},
                {"tag": "NOUN", "token": "evi"},
            ],
        },
    },
    {   # loc — tamlama DEĞİL; tek isim NP'ye sarılır (motor konvansiyonu: evde→NP)
        "text": "İstanbul'da",
        "roots": {"istanbul"},
        "expected": {
            "tag": "NP",
            "surface": "İstanbul'da",
            "children": [{"tag": "NOUN", "token": "İstanbul'da"}],
        },
    },
    {   # dat — tek isim NP'ye sarılır
        "text": "Ankara'ya",
        "roots": {"ankara"},
        "expected": {
            "tag": "NP",
            "surface": "Ankara'ya",
            "children": [{"tag": "NOUN", "token": "Ankara'ya"}],
        },
    },
    # ------------------------------------------------------------------ #
    # B2 — koordine genitif tamlama
    # ------------------------------------------------------------------ #
    {   # NP( CoordP(Ali'nin ve Veli'nin), evi )
        "text": "Ali'nin ve Veli'nin evi",
        "roots": {"ev", "ali", "veli"},
        "expected": {
            "tag": "NP",
            "surface": "Ali'nin ve Veli'nin evi",
            "children": [
                {"tag": "CoordP", "surface": "Ali'nin ve Veli'nin",
                 "children": [
                     {"tag": "NP", "surface": "Ali'nin",
                      "children": [{"tag": "NOUN", "token": "Ali'nin"}]},
                     {"tag": "CCONJ", "token": "ve"},
                     {"tag": "NP", "surface": "Veli'nin",
                      "children": [{"tag": "NOUN", "token": "Veli'nin"}]},
                 ]},
                {"tag": "NOUN", "token": "evi"},
            ],
        },
    },
    {   # common-noun koordine tamlama: evin ve kapının rengi
        "text": "evin ve kapının rengi",
        "roots": {"ev", "kapı", "renk"},
        "expected": {
            "tag": "NP",
            "surface": "evin ve kapının rengi",
            "children": [
                {"tag": "CoordP", "surface": "evin ve kapının",
                 "children": [
                     {"tag": "NP", "surface": "evin",
                      "children": [{"tag": "NOUN", "token": "evin"}]},
                     {"tag": "CCONJ", "token": "ve"},
                     {"tag": "NP", "surface": "kapının",
                      "children": [{"tag": "NOUN", "token": "kapının"}]},
                 ]},
                {"tag": "NOUN", "token": "rengi"},
            ],
        },
    },
    {   # 3'lü koordine tamlayan → CoordP(3 konjunkt) + head
        "text": "Ali'nin ve Veli'nin ve Ayşe'nin evi",
        "roots": {"ev", "ali", "veli", "ayşe"},
        "expected": {
            "tag": "NP",
            "surface": "Ali'nin ve Veli'nin ve Ayşe'nin evi",
            "children": [
                {"tag": "CoordP", "surface": "Ali'nin ve Veli'nin ve Ayşe'nin",
                 "children": [
                     {"tag": "NP", "surface": "Ali'nin",
                      "children": [{"tag": "NOUN", "token": "Ali'nin"}]},
                     {"tag": "CCONJ", "token": "ve"},
                     {"tag": "NP", "surface": "Veli'nin",
                      "children": [{"tag": "NOUN", "token": "Veli'nin"}]},
                     {"tag": "CCONJ", "token": "ve"},
                     {"tag": "NP", "surface": "Ayşe'nin",
                      "children": [{"tag": "NOUN", "token": "Ayşe'nin"}]},
                 ]},
                {"tag": "NOUN", "token": "evi"},
            ],
        },
    },
    # ------------------------------------------------------------------ #
    # Basit tamlama regresyon (koordinasyon yok)
    # ------------------------------------------------------------------ #
    {   # poss net: evin kapısı → NP
        "text": "evin kapısı",
        "roots": {"ev", "kapı"},
        "expected": {
            "tag": "NP",
            "surface": "evin kapısı",
            "children": [
                {"tag": "NOUN", "token": "evin"},
                {"tag": "NOUN", "token": "kapısı"},
            ],
        },
    },
    {   # acc homograf head: adamın evi → yapısal NP (R0 gevşetme yan faydası)
        "text": "adamın evi",
        "roots": {"adam", "ev"},
        "expected": {
            "tag": "NP",
            "surface": "adamın evi",
            "children": [
                {"tag": "NOUN", "token": "adamın"},
                {"tag": "NOUN", "token": "evi"},
            ],
        },
    },
    # ------------------------------------------------------------------ #
    # Negatif — head yok → CoordP kalır (tamlama kurulmaz)
    # ------------------------------------------------------------------ #
    {   # Ali'nin ve Veli'nin (head yok) → CoordP kök
        "text": "Ali'nin ve Veli'nin",
        "roots": {"ali", "veli"},
        "expected": {
            "tag": "CoordP",
            "surface": "Ali'nin ve Veli'nin",
            "children": [
                {"tag": "NP", "surface": "Ali'nin",
                 "children": [{"tag": "NOUN", "token": "Ali'nin"}]},
                {"tag": "CCONJ", "token": "ve"},
                {"tag": "NP", "surface": "Veli'nin",
                 "children": [{"tag": "NOUN", "token": "Veli'nin"}]},
            ],
        },
    },
]
