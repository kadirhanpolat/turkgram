'''golden_clause_v5.py — gerçek gömme (aktarma + adlaşmış) yargı bölme bağımsız golden (V5).

Motor-körü, elle doğrulanmış (Opus); Türkçe DİLBİLGİSİNDEN (okul grameri +
Korkmaz *Şekil Bilgisi* cümle bilgisi: iç cümle/gömülü tümce) kuruldu —
motora BAKILMADAN. SPEC: docs/superpowers/specs/2026-07-20-clause-segmentation-design.md §5c.

Kapsam (V5): gerçek gömme (gömülü tümce = ana yargının argümanı) — iki tür:
  * AKTARMA (reported/quote): gömülü FİNİT tümce + bildirme/biliş fiili
    (demek/sanmak/zannetmek/söylemek/düşünmek/ummak/sormak). Gömülü tümce = 'yan'
    (connector=None, yapısal — leksik bağlaç değil); bildirme fiili = 'temel'.
  * ADLAŞMIŞ (nominalized): -DIK/-mA + iyelik + durum (geldiğini/gelmesini/olduğunu
    = sıfat-fiil/isim-fiil, participle) gömülü yargının yüklemi → 'yan'; ana fiil = 'temel'.
  * GUARD: bildirme fiili + NESNE NP (finit tümce YOK) → gömme DEĞİL, tek 'temel'.

Her eleman:
{
  "text": <cümle, noktalamasız düz>,
  "clauses": [
    {"role": 'temel'|'yan'|'bağımsız',
     "elements": [ (label, tokens, head_id, aliases), ... ],
     "predicate_id": <yüklemin GLOBAL 1-tabanlı token id>,
     "connector": None},  # gömme yapısaldır → connector daima None
    ...
  ],
}

- head_id ve predicate_id: cümledeki GLOBAL 1-tabanlı token id (yüzey sırası).
- Gömülü (aktarma/adlaşmış) yan yargı KENDİ özne/tümleç/yüklemini taşır
  (Yağmur=özne, yağacak=yüklem; Ali=özne, geldiğini=yüklem).
- dolaylı tümleç aliases=("yer tamlayıcısı",); diğer ögelerde aliases=().
- Gömmede connector=None (SPEC §5c: gömme leksik değil, yapısaldır).
'''

GOLDEN_CLAUSES_V5 = [
    # ── AKTARMA (reported speech): gömülü finit tümce + bildirme fiili ──────
    # 1. Yağmur yağacak sandı — gömülü tümce (Yağmur=özne, yağacak=yüklem gelecek
    #    zaman) 'yan'; sandı (sanmak) = 'temel'. Bildirme fiili + öncesinde FİNİT
    #    tümce (yağacak) → aktarma tetiklenir.
    {
        "text": "Yağmur yağacak sandı",
        "clauses": [
            {"role": "yan", "elements": [
                ("özne", ("Yağmur",), 1, ()),
                ("yüklem", ("yağacak",), 2, ()),
            ], "predicate_id": 2, "connector": None},
            {"role": "temel", "elements": [
                ("yüklem", ("sandı",), 3, ()),
            ], "predicate_id": 3, "connector": None},
        ],
    },
    # 2. Gel dedi — gömülü emir tümcesi (Gel = emir yüklemi) 'yan'; dedi (demek)
    #    = 'temel'. Gel anlatı-dışı ama gömülü aktarma yüklemi (bildirme fiili
    #    öncesi finit) → yan sınır.
    {
        "text": "Gel dedi",
        "clauses": [
            {"role": "yan", "elements": [
                ("yüklem", ("Gel",), 1, ()),
            ], "predicate_id": 1, "connector": None},
            {"role": "temel", "elements": [
                ("yüklem", ("dedi",), 2, ()),
            ], "predicate_id": 2, "connector": None},
        ],
    },
    # 3. Hasta olduğunu söyledi — olduğunu (olmak -DIK+iyelik+acc) adlaşmış ORTAC
    #    → gömülü yargının yüklemi, 'yan'; söyledi = 'temel'.
    # NOT: "Hasta" gömülü tümcenin yüklem-içi ögesi. olmak koşaç fiilidir;
    #      "Hasta olduğunu" = "(onun) hasta olduğunu" → Hasta yüklem-adı/ad-tümleç.
    #      Ne özne ne nesne tam; nom öge → motor 'özne' varsayar (ad-tümleç/yüklem-adı
    #      etiketi V5 kapsamı dışı — belirsiz edge, motor nom→özne default kabul edildi).
    {
        "text": "Hasta olduğunu söyledi",
        "clauses": [
            {"role": "yan", "elements": [
                ("özne", ("Hasta",), 1, ()),  # NOT: belirsiz ad-tümleç; nom→özne default
                ("yüklem", ("olduğunu",), 2, ()),
            ], "predicate_id": 2, "connector": None},
            {"role": "temel", "elements": [
                ("yüklem", ("söyledi",), 3, ()),
            ], "predicate_id": 3, "connector": None},
        ],
    },
    # 4. Gelecek zannetti — Gelecek = FİİL (gelmek gelecek-zaman, 3sg) → gömülü
    #    yüklem 'yan'; zannetti (zannetmek) = 'temel'.
    # NOT: "Gelecek" isim (gelecek=future/istikbal) ile homograf; SPEC §5c gereği
    #      burada FİİL okunuşu (gelmek fut) → gömme tetiklenir. Homograf-finit
    #      disambiguation kök nedeni (isim rank edilirse gömme tetiklenmez).
    {
        "text": "Gelecek zannetti",
        "clauses": [
            {"role": "yan", "elements": [
                ("yüklem", ("Gelecek",), 1, ()),
            ], "predicate_id": 1, "connector": None},
            {"role": "temel", "elements": [
                ("yüklem", ("zannetti",), 2, ()),
            ], "predicate_id": 2, "connector": None},
        ],
    },

    # ── ADLAŞMIŞ (nominalized): -DIK/-mA+iyelik+durum yan yargı + ana fiil ──
    # 5. Gelmesini istedi — Gelmesini (gelmek -mA+iyelik+acc, isim-fiil) adlaşmış
    #    → gömülü yargının yüklemi, 'yan'; istedi (istemek) = 'temel'.
    {
        "text": "Gelmesini istedi",
        "clauses": [
            {"role": "yan", "elements": [
                ("yüklem", ("Gelmesini",), 1, ()),
            ], "predicate_id": 1, "connector": None},
            {"role": "temel", "elements": [
                ("yüklem", ("istedi",), 2, ()),
            ], "predicate_id": 2, "connector": None},
        ],
    },
    # 6. Ali geldiğini biliyorum — geldiğini (gelmek -DIK+iyelik+acc, sıfat-fiil)
    #    adlaşmış → gömülü yüklem 'yan'; Ali = gömülü tümcenin öznesi; biliyorum
    #    = 'temel'.
    {
        "text": "Ali geldiğini biliyorum",
        "clauses": [
            {"role": "yan", "elements": [
                ("özne", ("Ali",), 1, ()),
                ("yüklem", ("geldiğini",), 2, ()),
            ], "predicate_id": 2, "connector": None},
            {"role": "temel", "elements": [
                ("yüklem", ("biliyorum",), 3, ()),
            ], "predicate_id": 3, "connector": None},
        ],
    },
    # 7. Onun geldiğini gördüm — Onun (genitif zamir) gömülü tümcenin öznesi;
    #    geldiğini adlaşmış → gömülü yüklem 'yan'; gördüm = 'temel'.
    # NOT: "Onun" tamlayan-genitif özne (adlaşmış tümcenin faili). Türkçede
    #      adlaşmış yan cümlenin öznesi genitif alır (onun gelmesi/geldiği).
    {
        "text": "Onun geldiğini gördüm",
        "clauses": [
            {"role": "yan", "elements": [
                ("özne", ("Onun",), 1, ()),
                ("yüklem", ("geldiğini",), 2, ()),
            ], "predicate_id": 2, "connector": None},
            {"role": "temel", "elements": [
                ("yüklem", ("gördüm",), 3, ()),
            ], "predicate_id": 3, "connector": None},
        ],
    },

    # ── GUARD: bildirme fiili + NESNE NP (finit tümce YOK) → gömme DEĞİL ────
    # 8. Ali bir şey söyledi — söyledi bildirme fiili AMA öncesinde finit tümce
    #    YOK (bir şey = nesne NP) → aktarma tetiklenmez → TEK 'temel' yargı.
    # NOT: "bir şey" tek belirtisiz nesne ögesi (yalın; bir=belirsizlik sıfatı +
    #      şey=ad, birlikte NP). head_id = ad başı (şey@3).
    {
        "text": "Ali bir şey söyledi",
        "clauses": [
            {"role": "temel", "elements": [
                ("özne", ("Ali",), 1, ()),
                ("belirtisiz nesne", ("bir", "şey"), 3, ()),
                ("yüklem", ("söyledi",), 4, ()),
            ], "predicate_id": 4, "connector": None},
        ],
    },
]
