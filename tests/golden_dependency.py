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
    {   # ikileme: baş→fiil advmod, ikinci→baş compound:redup
        "text": "yavaş yavaş yürüdü",
        "roots": {"yavaş", "yürümek"},
        "expected": [
            {"id": 1, "form": "yavaş", "lemma": "yavaş",   "upos": "ADJ",
             "head": 3, "deprel": "advmod"},
            {"id": 2, "form": "yavaş", "lemma": "yavaş",   "upos": "ADJ",
             "head": 1, "deprel": "compound:redup"},
            {"id": 3, "form": "yürüdü","lemma": "yürümek", "upos": "VERB",
             "head": 0, "deprel": "root"},
        ],
    },
    {   # m-ikileme nominal: baş(kitap) nsubj, reduplikant(mitap) compound:redup upos=NOUN
        "text": "kitap mitap aldı",
        "roots": {"kitap", "almak"},
        "expected": [
            {"id": 1, "form": "kitap", "lemma": "kitap", "upos": "NOUN",
             "head": 3, "deprel": "nsubj"},
            {"id": 2, "form": "mitap",                   "upos": "NOUN",
             "head": 1, "deprel": "compound:redup"},
            {"id": 3, "form": "aldı",  "lemma": "almak", "upos": "VERB",
             "head": 0, "deprel": "root"},
        ],
    },
    {   # ADJ-taban m-ikileme: güzel amod→elbise; müzel MRED→ADJ compound:redup→güzel
        "text": "güzel müzel elbise",
        "roots": {"güzel", "elbise"},
        "expected": [
            {"id": 1, "form": "güzel",  "lemma": "güzel",  "upos": "ADJ",
             "head": 3, "deprel": "amod"},
            {"id": 2, "form": "müzel",                     "upos": "ADJ",
             "head": 1, "deprel": "compound:redup"},
            {"id": 3, "form": "elbise", "lemma": "elbise", "upos": "NOUN",
             "head": 0, "deprel": "root"},
        ],
    },
]
