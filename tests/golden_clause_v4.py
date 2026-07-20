'''golden_clause_v4.py — ki/diye yan cümle bölme (clause segmentation V4) bağımsız golden.

Motor-körü, elle doğrulanmış (Opus); Türkçe DİLBİLGİSİNDEN (okul grameri +
Korkmaz *Şekil Bilgisi* cümle bilgisi — birleşik cümle, ki'li/diye'li bağlanma)
kuruldu — motora BAKILMADAN.
SPEC: docs/superpowers/specs/2026-07-20-clause-segmentation-design.md §5b.

Her eleman:
{
  "text": <cümle, noktalamasız düz>,
  "clauses": [
    {"role": 'temel'|'yan'|'bağımsız',
     "elements": [ (label, tokens, head_id, aliases), ... ],
     "predicate_id": <yüklemin GLOBAL 1-tabanlı token id>,
     "connector": <bağlayıcı yüzeyi 've'/'ki'/'diye' | None>},
    ...
  ],
}

- head_id ve predicate_id: cümledeki GLOBAL 1-tabanlı token id (yüzey sırası).
- ki/diye tokenları öge DEĞİL (connector'a gider) ama GLOBAL id sayımında
  token'dır → sonraki tokenların id'lerini kaydırır.
- dolaylı tümleç aliases=("yer tamlayıcısı",); diğer ögelerde aliases=().

ki/diye kuralları (SPEC §5b):
- ki (İLERİ subordinatör): `temel ki yan`. ki ÖNCESİ = temel; ki SONRASI
  yargı(lar) = yan, connector='ki' (ilk yan-yargıda). ki-domain: ki'den sonra
  her yargı yan.
- diye (GERİ subordinatör): `yan diye temel`. diye ÖNCESİ yargı = yan,
  connector='diye'; diye SONRASI = temel.
- Rol: fiilimsi/şart yüklem VEYA ki/diye-marker → yan; yan-olmayan ≥2 →
  bağımsız; aksi → temel.
'''

GOLDEN_CLAUSES_V4 = [
    # ── ki: İLERİ subordinatör (temel + yan) ───────────────────────────────
    # 1. Biliyorum ki gelecek
    #    Biliyorum@1 (temel yüklem, bilmek geniş 1sg) | ki@2 (connector, öge değil)
    #    gelecek@3 (yan yüklem, gelmek gelecek-zaman — İSİM 'gelecek' DEĞİL).
    {
        "text": "Biliyorum ki gelecek",
        "clauses": [
            {"role": "temel", "elements": [
                ("yüklem", ("Biliyorum",), 1, ()),
            ], "predicate_id": 1, "connector": None},
            {"role": "yan", "elements": [
                ("yüklem", ("gelecek",), 3, ()),
            ], "predicate_id": 3, "connector": "ki"},
        ],
    },
    # 2. Söyledim ki duysun
    #    Söyledim@1 (temel, söylemek past 1sg) | ki@2 | duysun@3 (yan, duymak
    #    emir/istek 3sg). ki-domain → sonrası yan.
    {
        "text": "Söyledim ki duysun",
        "clauses": [
            {"role": "temel", "elements": [
                ("yüklem", ("Söyledim",), 1, ()),
            ], "predicate_id": 1, "connector": None},
            {"role": "yan", "elements": [
                ("yüklem", ("duysun",), 3, ()),
            ], "predicate_id": 3, "connector": "ki"},
        ],
    },
    # 3. Öyle yoruldum ki uyudum
    #    Öyle@1 (derece/tarz sözcüğü → zarf tümleci, fiili niteler) | yoruldum@2
    #    (temel yüklem, yorulmak past 1sg) | ki@3 | uyudum@4 (yan, uyumak past 1sg).
    #    ki ÖNCESİ (Öyle yoruldum) = temel; SONRASI = yan.
    {
        "text": "Öyle yoruldum ki uyudum",
        "clauses": [
            {"role": "temel", "elements": [
                ("zarf tümleci", ("Öyle",), 1, ()),
                ("yüklem", ("yoruldum",), 2, ()),
            ], "predicate_id": 2, "connector": None},
            {"role": "yan", "elements": [
                ("yüklem", ("uyudum",), 4, ()),
            ], "predicate_id": 4, "connector": "ki"},
        ],
    },

    # ── diye: GERİ subordinatör (yan + temel) ──────────────────────────────
    # 4. Gelsin diye bekledim
    #    Gelsin@1 (yan yüklem, gelmek emir/istek 3sg) | diye@2 (connector, öge değil)
    #    bekledim@3 (temel yüklem, beklemek past 1sg). diye ÖNCESİ = yan.
    {
        "text": "Gelsin diye bekledim",
        "clauses": [
            {"role": "yan", "elements": [
                ("yüklem", ("Gelsin",), 1, ()),
            ], "predicate_id": 1, "connector": "diye"},
            {"role": "temel", "elements": [
                ("yüklem", ("bekledim",), 3, ()),
            ], "predicate_id": 3, "connector": None},
        ],
    },
    # 5. Duysun diye bağırdım
    #    Duysun@1 (yan yüklem, duymak emir/istek 3sg) | diye@2 | bağırdım@3
    #    (temel, bağırmak past 1sg).
    {
        "text": "Duysun diye bağırdım",
        "clauses": [
            {"role": "yan", "elements": [
                ("yüklem", ("Duysun",), 1, ()),
            ], "predicate_id": 1, "connector": "diye"},
            {"role": "temel", "elements": [
                ("yüklem", ("bağırdım",), 3, ()),
            ], "predicate_id": 3, "connector": None},
        ],
    },
    # 6. Yağmur yağıyor diye gelmedim
    #    Yağmur@1 (özne) | yağıyor@2 (yan yüklem, yağmak şimdiki 3sg) | diye@3
    #    gelmedim@4 (temel yüklem, gelmek OLUMSUZ past 1sg). diye ÖNCESİ yargı
    #    (Yağmur yağıyor) = yan; kendi özne+yüklemini taşır.
    {
        "text": "Yağmur yağıyor diye gelmedim",
        "clauses": [
            {"role": "yan", "elements": [
                ("özne", ("Yağmur",), 1, ()),
                ("yüklem", ("yağıyor",), 2, ()),
            ], "predicate_id": 2, "connector": "diye"},
            {"role": "temel", "elements": [
                ("yüklem", ("gelmedim",), 4, ()),
            ], "predicate_id": 4, "connector": None},
        ],
    },

    # ── ki: çok-öge yan yargı ──────────────────────────────────────────────
    # 7. Biliyorum ki yarın gelecek
    #    Biliyorum@1 (temel) | ki@2 | yarın@3 (zaman zarfı → zarf tümleci)
    #    gelecek@4 (yan yüklem, gelmek gelecek-zaman). ki SONRASI yargı kendi
    #    zarf tümleci + yüklemini taşır.
    {
        "text": "Biliyorum ki yarın gelecek",
        "clauses": [
            {"role": "temel", "elements": [
                ("yüklem", ("Biliyorum",), 1, ()),
            ], "predicate_id": 1, "connector": None},
            {"role": "yan", "elements": [
                ("zarf tümleci", ("yarın",), 3, ()),
                ("yüklem", ("gelecek",), 4, ()),
            ], "predicate_id": 4, "connector": "ki"},
        ],
    },
]
