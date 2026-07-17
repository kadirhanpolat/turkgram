"""E6 CoNLL-U export — bağımsız golden (motor-körü, elle doğrulanmış).

CoNLL-U 10 sütun: ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC
DEPS = _ (sütun 9, enhanced deps yok), MISC = _ (sütun 10)
FEATS alfabetik sırada.
"""

CONLLU_CASES = [
    {
        "sent_id": "1",
        "text": "öğrenci okudu",
        "roots": {"öğrenci", "okumak"},
        # Feats:
        #   öğrenci: noun nom sg → Case=Nom|Number=Sing
        #   okudu: verb past 3sg → Number=Sing|Person=3|Tense=Past
        "expected": (
            "# sent_id = 1\n"
            "# text = öğrenci okudu\n"
            "1\töğrenci\töğrenci\tNOUN\tdecline\tCase=Nom|Number=Sing\t2\tnsubj\t_\t_\n"
            "2\tokudu\tokumak\tVERB\tconjugate\tNumber=Sing|Person=3|Tense=Past\t0\troot\t_\t_\n"
        ),
    },
]
