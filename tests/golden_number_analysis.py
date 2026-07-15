"""golden_number_analysis.py — sayı çözümlemesi bağımsız golden (motor-körü).

Elle-doğrulanmış: ordinal (-IncI) + distributif (-şAr/-Ar) yüzey → (lemma, kind).
Sayı çözümlemesi eksen içermez → axes={}.
"""

GOLDEN = [
    # --- Ordinal: 1-10 ---
    {"surface": "birinci", "lemma": "bir", "kind": "ordinal", "axes": {}},
    {"surface": "ikinci", "lemma": "iki", "kind": "ordinal", "axes": {}},
    {"surface": "üçüncü", "lemma": "üç", "kind": "ordinal", "axes": {}},
    {"surface": "dördüncü", "lemma": "dört", "kind": "ordinal", "axes": {}},
    {"surface": "beşinci", "lemma": "beş", "kind": "ordinal", "axes": {}},
    {"surface": "altıncı", "lemma": "altı", "kind": "ordinal", "axes": {}},
    {"surface": "yedinci", "lemma": "yedi", "kind": "ordinal", "axes": {}},
    {"surface": "sekizinci", "lemma": "sekiz", "kind": "ordinal", "axes": {}},
    {"surface": "dokuzuncu", "lemma": "dokuz", "kind": "ordinal", "axes": {}},
    {"surface": "onuncu", "lemma": "on", "kind": "ordinal", "axes": {}},

    # --- Ordinal: bileşik (son sözcük ek alır) ---
    {"surface": "yirmi birinci", "lemma": "yirmi bir", "kind": "ordinal", "axes": {}},
    {"surface": "kırk beşinci", "lemma": "kırk beş", "kind": "ordinal", "axes": {}},

    # --- Distributif: 1-10 ---
    {"surface": "birer", "lemma": "bir", "kind": "distributive", "axes": {}},
    {"surface": "ikişer", "lemma": "iki", "kind": "distributive", "axes": {}},
    {"surface": "üçer", "lemma": "üç", "kind": "distributive", "axes": {}},
    {"surface": "dörder", "lemma": "dört", "kind": "distributive", "axes": {}},
    {"surface": "beşer", "lemma": "beş", "kind": "distributive", "axes": {}},
    {"surface": "altışar", "lemma": "altı", "kind": "distributive", "axes": {}},
    {"surface": "yedişer", "lemma": "yedi", "kind": "distributive", "axes": {}},
    {"surface": "sekizer", "lemma": "sekiz", "kind": "distributive", "axes": {}},
    {"surface": "dokuzar", "lemma": "dokuz", "kind": "distributive", "axes": {}},
    {"surface": "onar", "lemma": "on", "kind": "distributive", "axes": {}},

    # --- Distributif: bileşik (son sözcük ek alır) ---
    {"surface": "yirmi birer", "lemma": "yirmi bir", "kind": "distributive", "axes": {}},
    {"surface": "kırk ikişer", "lemma": "kırk iki", "kind": "distributive", "axes": {}},
]
