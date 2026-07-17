"""E5 dependency graph — bağımsız golden (motor-körü, elle doğrulanmış).

Her giriş: cümle metni + beklenen DepToken listesi (dict formatında).
UD bağımlılık ilişkileri (Universal Dependencies): nsubj, obj, root, nmod:poss vb.
"""

DEP_CASES = [
    {
        "text": "öğrenci okudu",
        "roots": {"öğrenci", "okumak"},
        "expected": [
            {"id": 1, "form": "öğrenci", "lemma": "öğrenci", "upos": "NOUN",
             "head": 2, "deprel": "nsubj"},
            {"id": 2, "form": "okudu",   "lemma": "okumak",  "upos": "VERB",
             "head": 0, "deprel": "root"},
        ],
    },
    {
        "text": "öğrenci kitabı okudu",
        "roots": {"öğrenci", "kitap", "okumak"},
        "expected": [
            {"id": 1, "form": "öğrenci", "lemma": "öğrenci", "upos": "NOUN",
             "head": 3, "deprel": "nsubj"},
            {"id": 2, "form": "kitabı",  "lemma": "kitap",   "upos": "NOUN",
             "head": 3, "deprel": "obj"},
            {"id": 3, "form": "okudu",   "lemma": "okumak",  "upos": "VERB",
             "head": 0, "deprel": "root"},
        ],
    },
    {
        "text": "evin kapısını gördüm",
        "roots": {"ev", "kapı", "görmek"},
        "expected": [
            {"id": 1, "form": "evin",     "lemma": "ev",     "upos": "NOUN",
             "head": 2, "deprel": "nmod:poss"},
            {"id": 2, "form": "kapısını", "lemma": "kapı",   "upos": "NOUN",
             "head": 3, "deprel": "obj"},
            {"id": 3, "form": "gördüm",   "lemma": "görmek", "upos": "VERB",
             "head": 0, "deprel": "root"},
        ],
    },
]
