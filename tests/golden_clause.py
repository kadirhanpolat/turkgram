'''golden_clause.py — yargı bölme (clause segmentation) bağımsız golden.

Motor-körü, elle doğrulanmış (Opus); Türkçe DİLBİLGİSİNDEN (okul grameri +
Korkmaz *Şekil Bilgisi* cümle bilgisi) kuruldu — motora BAKILMADAN.
SPEC: docs/superpowers/specs/2026-07-20-clause-segmentation-design.md.

Her eleman:
{
  "text": <cümle, noktalamasız düz>,
  "clauses": [
    {"role": 'temel'|'yan'|'bağımsız',
     "elements": [ (label, tokens, head_id, aliases), ... ],
     "predicate_id": <yüklemin GLOBAL 1-tabanlı token id>,
     "connector": <koordinat bağlaç yüzeyi 've'/'ama'… | None>},
    ...
  ],
}

- head_id ve predicate_id: cümledeki GLOBAL 1-tabanlı token id (yüzey sırası).
- Koordinat bağlaç (ve/ama/fakat) yargı ögesi DEĞİL → sonraki yargının connector'ı.
- dolaylı tümleç aliases=("yer tamlayıcısı",); diğer ögelerde aliases=().
- Rol (SPEC §3): yüklem fiilimsi/şart → 'yan'; yan-olmayan yüklem ≥2 → her biri
  'bağımsız'; aksi (basit tek yargı / birleşiğin ana yargısı) → 'temel'.
'''

GOLDEN_CLAUSES = [
    # ── Basit cümleler: tek yargı, role='temel' ────────────────────────────
    # 1. özne + dolaylı tümleç + yüklem
    {
        "text": "Ben eve gidiyorum",
        "clauses": [
            {"role": "temel", "elements": [
                ("özne", ("Ben",), 1, ()),
                ("dolaylı tümleç", ("eve",), 2, ("yer tamlayıcısı",)),
                ("yüklem", ("gidiyorum",), 3, ()),
            ], "predicate_id": 3, "connector": None},
        ],
    },
    # 2. özne + belirtisiz nesne (yalın) + yüklem
    {
        "text": "Annem yemek yaptı",
        "clauses": [
            {"role": "temel", "elements": [
                ("özne", ("Annem",), 1, ()),
                ("belirtisiz nesne", ("yemek",), 2, ()),
                ("yüklem", ("yaptı",), 3, ()),
            ], "predicate_id": 3, "connector": None},
        ],
    },
    # 3. isim cümlesi (nominal yüklem): özne + yüklem
    {
        "text": "Hava güzel",
        "clauses": [
            {"role": "temel", "elements": [
                ("özne", ("Hava",), 1, ()),
                ("yüklem", ("güzel",), 2, ()),
            ], "predicate_id": 2, "connector": None},
        ],
    },
    # 3b. copula-yüklem koordinasyonu (ek-fiilli isim cümlesi bağlı) → 2 bağımsız
    {
        "text": "Hava güzeldi ve deniz sıcaktı",
        "clauses": [
            {"role": "bağımsız", "elements": [
                ("özne", ("Hava",), 1, ()),
                ("yüklem", ("güzeldi",), 2, ()),
            ], "predicate_id": 2, "connector": None},
            {"role": "bağımsız", "elements": [
                ("özne", ("deniz",), 4, ()),
                ("yüklem", ("sıcaktı",), 5, ()),
            ], "predicate_id": 5, "connector": "ve"},
        ],
    },

    # ── Bağlı cümleler (ve/ama/fakat): iki bağımsız yargı ──────────────────
    # 4. Geldi ve gitti — özneler pro-drop; ilk yargı yüklemsiz-gövdesiz
    {
        "text": "Geldi ve gitti",
        "clauses": [
            {"role": "bağımsız", "elements": [
                ("yüklem", ("Geldi",), 1, ()),
            ], "predicate_id": 1, "connector": None},
            {"role": "bağımsız", "elements": [
                ("yüklem", ("gitti",), 3, ()),
            ], "predicate_id": 3, "connector": "ve"},
        ],
    },
    # 5. Ali geldi ve Veli gitti — iki özneli bağlı
    {
        "text": "Ali geldi ve Veli gitti",
        "clauses": [
            {"role": "bağımsız", "elements": [
                ("özne", ("Ali",), 1, ()),
                ("yüklem", ("geldi",), 2, ()),
            ], "predicate_id": 2, "connector": None},
            {"role": "bağımsız", "elements": [
                ("özne", ("Veli",), 4, ()),
                ("yüklem", ("gitti",), 5, ()),
            ], "predicate_id": 5, "connector": "ve"},
        ],
    },
    # 14. Çok çalıştı ve başardı — zarf tümleçli ilk bağımsız yargı
    # NOT: "Çok" derece/miktar zarfı → zarf tümleci (fiili niteler). İkinci yargı
    #       yüklem-yalnız (pro-drop özne, ortak özne paylaştırılmaz — SPEC §6).
    {
        "text": "Çok çalıştı ve başardı",
        "clauses": [
            {"role": "bağımsız", "elements": [
                ("zarf tümleci", ("Çok",), 1, ()),
                ("yüklem", ("çalıştı",), 2, ()),
            ], "predicate_id": 2, "connector": None},
            {"role": "bağımsız", "elements": [
                ("yüklem", ("başardı",), 4, ()),
            ], "predicate_id": 4, "connector": "ve"},
        ],
    },

    # ── Sıralı cümleler (bağlaçsız seri finit fiil): iki bağımsız yargı ─────
    # 6. Geldi gitti
    {
        "text": "Geldi gitti",
        "clauses": [
            {"role": "bağımsız", "elements": [
                ("yüklem", ("Geldi",), 1, ()),
            ], "predicate_id": 1, "connector": None},
            {"role": "bağımsız", "elements": [
                ("yüklem", ("gitti",), 2, ()),
            ], "predicate_id": 2, "connector": None},
        ],
    },
    # 7. Ben geldim sen gittin — iki özneli sıralı
    {
        "text": "Ben geldim sen gittin",
        "clauses": [
            {"role": "bağımsız", "elements": [
                ("özne", ("Ben",), 1, ()),
                ("yüklem", ("geldim",), 2, ()),
            ], "predicate_id": 2, "connector": None},
            {"role": "bağımsız", "elements": [
                ("özne", ("sen",), 3, ()),
                ("yüklem", ("gittin",), 4, ()),
            ], "predicate_id": 4, "connector": None},
        ],
    },

    # ── Birleşik cümleler (fiilimsi/şart yan yargı + temel yargı) ──────────
    # 8. Eve gelince yattım — yan yargı kendi sol tümlecini AYRI öge yapar
    {
        "text": "Eve gelince yattım",
        "clauses": [
            {"role": "yan", "elements": [
                ("dolaylı tümleç", ("Eve",), 1, ("yer tamlayıcısı",)),
                ("yüklem", ("gelince",), 2, ()),
            ], "predicate_id": 2, "connector": None},
            {"role": "temel", "elements": [
                ("yüklem", ("yattım",), 3, ()),
            ], "predicate_id": 3, "connector": None},
        ],
    },
    # 9. Yağmur yağınca eve gittik — yan yargının kendi öznesi + temel dolaylı tümleç
    {
        "text": "Yağmur yağınca eve gittik",
        "clauses": [
            {"role": "yan", "elements": [
                ("özne", ("Yağmur",), 1, ()),
                ("yüklem", ("yağınca",), 2, ()),
            ], "predicate_id": 2, "connector": None},
            {"role": "temel", "elements": [
                ("dolaylı tümleç", ("eve",), 3, ("yer tamlayıcısı",)),
                ("yüklem", ("gittik",), 4, ()),
            ], "predicate_id": 4, "connector": None},
        ],
    },
    # 10. Gelirse gideriz — şart yan yargı (-se) + temel
    {
        "text": "Gelirse gideriz",
        "clauses": [
            {"role": "yan", "elements": [
                ("yüklem", ("Gelirse",), 1, ()),
            ], "predicate_id": 1, "connector": None},
            {"role": "temel", "elements": [
                ("yüklem", ("gideriz",), 2, ()),
            ], "predicate_id": 2, "connector": None},
        ],
    },
    # 11. Koşarak geldi — -arak zarf-fiili (bare fiilimsi) yan + temel
    {
        "text": "Koşarak geldi",
        "clauses": [
            {"role": "yan", "elements": [
                ("yüklem", ("Koşarak",), 1, ()),
            ], "predicate_id": 1, "connector": None},
            {"role": "temel", "elements": [
                ("yüklem", ("geldi",), 2, ()),
            ], "predicate_id": 2, "connector": None},
        ],
    },
    # 12. Gülerek konuştu — -erek zarf-fiili yan + temel
    {
        "text": "Gülerek konuştu",
        "clauses": [
            {"role": "yan", "elements": [
                ("yüklem", ("Gülerek",), 1, ()),
            ], "predicate_id": 1, "connector": None},
            {"role": "temel", "elements": [
                ("yüklem", ("konuştu",), 2, ()),
            ], "predicate_id": 2, "connector": None},
        ],
    },
    # 13. Görünce sevindi — -ünce zarf-fiili (bare fiilimsi) yan + temel
    # NOT: özgün taslak "Yorulunca dinlendi" idi; `yorulmak` edilgen/dönüşlü türev
    # olduğundan leksikonda lemma değil → converb üretilemiyor (pre-existing analyzer
    # açığı, segmentasyona özgü DEĞİL). Basit-lemma converb (gör+ünce) ile aynı yapı.
    {
        "text": "Görünce sevindi",
        "clauses": [
            {"role": "yan", "elements": [
                ("yüklem", ("Görünce",), 1, ()),
            ], "predicate_id": 1, "connector": None},
            {"role": "temel", "elements": [
                ("yüklem", ("sevindi",), 2, ()),
            ], "predicate_id": 2, "connector": None},
        ],
    },
]
