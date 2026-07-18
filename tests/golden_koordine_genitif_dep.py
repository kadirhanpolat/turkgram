"""Koordine genitif tamlayan — dependency bağımsız golden (motor-körü, elle doğrulanmış).

Format golden_dependency.py emsali: cümle metni + beklenen DepToken listesi
(id, form, lemma?, upos, head, deprel). UD ilişkileri.

SPEC §4: koordine gen-CoordP → NP-child ilk konjunkt başı `nmod:poss` (possessed
head'e); CoordP içi `cc`(ve) + `conj`(ikinci+ konjunkt, ilk konjunkta bağlı);
possessed head = NP başı = root. `Ali'nin` birleşik yaprak (id tek token) → form
apostroflu birleşik, lemma özel-ad VERBATIM ("Ali"). Head homograf poss/acc feats
kapsam dışı (SPEC §4.3) → upos + deprel + head yapısı doğrulanır.

KİLİT KARAR — koordinasyonda cc/conj konjunktlar arası (ilk konjunkta bağlanır),
nmod:poss ilk konjunkttan possessed head'e (mevcut koord dependency konvansiyonu:
golden_dependency.py `kırmızı ve mavi araba` — cc/conj ilk konjunkta, amod ilk
konjunkttan başa; burada nmod:poss muadili).
"""

DEP_CASES = [
    {   # Ali'nin ve Veli'nin evi
        # Ali'nin --nmod:poss--> evi ; ve --cc--> Ali'nin ; Veli'nin --conj--> Ali'nin
        "text": "Ali'nin ve Veli'nin evi",
        "roots": {"ev", "ali", "veli"},
        "expected": [
            {"id": 1, "form": "Ali'nin",  "lemma": "Ali",  "upos": "NOUN",
             "head": 4, "deprel": "nmod:poss"},
            {"id": 2, "form": "ve",                          "upos": "CCONJ",
             "head": 1, "deprel": "cc"},
            {"id": 3, "form": "Veli'nin", "lemma": "Veli", "upos": "NOUN",
             "head": 1, "deprel": "conj"},
            {"id": 4, "form": "evi",      "lemma": "ev",   "upos": "NOUN",
             "head": 0, "deprel": "root"},
        ],
    },
    {   # evin ve kapının rengi (common-noun)
        "text": "evin ve kapının rengi",
        "roots": {"ev", "kapı", "renk"},
        "expected": [
            {"id": 1, "form": "evin",    "lemma": "ev",   "upos": "NOUN",
             "head": 4, "deprel": "nmod:poss"},
            {"id": 2, "form": "ve",                        "upos": "CCONJ",
             "head": 1, "deprel": "cc"},
            {"id": 3, "form": "kapının", "lemma": "kapı", "upos": "NOUN",
             "head": 1, "deprel": "conj"},
            {"id": 4, "form": "rengi",   "lemma": "renk", "upos": "NOUN",
             "head": 0, "deprel": "root"},
        ],
    },
]
