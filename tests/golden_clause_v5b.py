'''golden_clause_v5b.py — aktarma best-effort sınırları (V5.1) bağımsız golden.

Elle doğrulanmış (Türkçe dilbilgisi: iç cümle/gömülü tümce, koordinasyon vs gömme).
SPEC: docs/superpowers/specs/2026-07-20-aktarma-robustlik-design.md.

Üç sınır kapatıldı:
  1. KOORDİNE-İÇİ GÖMME: reporting fiilinden HEMEN önce fiil → TÜM önceki yargı(lar) gömülü
     yan (koordine dahil). Reporting yargısı koordinat-bağlıysa → koordinasyon, gömme DEĞİL.
  2. HOMOGRAF-FİNİT: geleceğim (gelecek+iyelik AD ranklanır ama gel+ecek fiil okuması var) →
     reporting öncesi nom + net-fiil zamanı → fiil (gömülü yüklem).
  3. TIRNAK: "Gel" dedi → çift tırnak sıyrılır (index yeniden), aktarma gömer.

Her eleman: {"text", "clauses":[{"role","elements":[(label,tokens,head_id,aliases)],
             "predicate_id","connector"}]}. Tırnak tokenları sıyrıldığı için index içerik-token.
'''

GOLDEN_CLAUSES_V5B = [
    # ── 1. Koordine-içi gömme (Ali koştu ve Veli geldi = gömülü koordine tümce) ─
    {
        "text": "Ali koştu ve Veli geldi dedi",
        "clauses": [
            {"role": "yan", "elements": [
                ("özne", ("Ali",), 1, ()),
                ("yüklem", ("koştu",), 2, ()),
            ], "predicate_id": 2, "connector": None},
            {"role": "yan", "elements": [
                ("özne", ("Veli",), 4, ()),
                ("yüklem", ("geldi",), 5, ()),
            ], "predicate_id": 5, "connector": "ve"},
            {"role": "temel", "elements": [
                ("yüklem", ("dedi",), 6, ()),
            ], "predicate_id": 6, "connector": None},
        ],
    },
    # ── 1b. Koordinasyon (reporting yargısı koordinat-bağlı → gömme DEĞİL) ──────
    {
        "text": "Ali geldi ve Veli dedi",
        "clauses": [
            {"role": "bağımsız", "elements": [
                ("özne", ("Ali",), 1, ()),
                ("yüklem", ("geldi",), 2, ()),
            ], "predicate_id": 2, "connector": None},
            {"role": "bağımsız", "elements": [
                ("özne", ("Veli",), 4, ()),
                ("yüklem", ("dedi",), 5, ()),
            ], "predicate_id": 5, "connector": "ve"},
        ],
    },
    # ── 2. Homograf-finit (geleceğim = gel+ecek fiil → gömülü yüklem) ──────────
    {
        "text": "Yarın geleceğim dedi",
        "clauses": [
            {"role": "yan", "elements": [
                ("zarf tümleci", ("Yarın",), 1, ()),
                ("yüklem", ("geleceğim",), 2, ()),
            ], "predicate_id": 2, "connector": None},
            {"role": "temel", "elements": [
                ("yüklem", ("dedi",), 3, ()),
            ], "predicate_id": 3, "connector": None},
        ],
    },
    # ── 3. Tırnak aktarma ("Eve gel" = gömülü tümce; tırnak sıyrılır) ──────────
    {
        "text": '"Eve gel" dedi',
        "clauses": [
            {"role": "yan", "elements": [
                ("dolaylı tümleç", ("Eve",), 1, ("yer tamlayıcısı",)),
                ("yüklem", ("gel",), 2, ()),
            ], "predicate_id": 2, "connector": None},
            {"role": "temel", "elements": [
                ("yüklem", ("dedi",), 3, ()),
            ], "predicate_id": 3, "connector": None},
        ],
    },
    # ── Guard: dat oblique arg (Sana) reporting öncesi → gömme DEĞİL, dolaylı tümleç ─
    {
        "text": "Sana söyledim",
        "clauses": [
            {"role": "temel", "elements": [
                ("dolaylı tümleç", ("Sana",), 1, ("yer tamlayıcısı",)),
                ("yüklem", ("söyledim",), 2, ()),
            ], "predicate_id": 2, "connector": None},
        ],
    },
    # ── Guard: acc nesne (Yolu) reporting öncesi → gömme DEĞİL, belirtili nesne ─
    {
        "text": "Yolu sordu",
        "clauses": [
            {"role": "temel", "elements": [
                ("belirtili nesne", ("Yolu",), 1, ()),
                ("yüklem", ("sordu",), 2, ()),
            ], "predicate_id": 2, "connector": None},
        ],
    },
]
