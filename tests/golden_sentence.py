'''golden_sentence.py — cümle çözümleme bağımsız golden (motor-körü, elle doğrulanmış; Opus).
SPEC docs/superpowers/specs/2026-07-20-cumle-cozumleme-design.md.'''

# Her eleman:
# {
#   "text": <cümle, noktalamasız düz>,
#   "elements": [ (label, tokens, head_id, aliases), ... ],
#   "type": { yuklem_turu, yuklem_yeri, olumluluk, soru, kip, yapi, eksiltili },
# }
#
# head_id: 1-tabanlı token id (yüzey sırası).
# aliases: dolaylı tümleç için ("yer tamlayıcısı",); diğerlerinde ().

GOLDEN_SENTENCES = [
    # ── 1. Basit fiil cümlesi: özne + dolaylı tümleç + yüklem ──────────────
    {
        "text": "Ben eve gidiyorum",
        "elements": [
            ("özne", ("Ben",), 1, ()),
            ("dolaylı tümleç", ("eve",), 2, ("yer tamlayıcısı",)),
            ("yüklem", ("gidiyorum",), 3, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },
    # özne + belirtili nesne + yüklem
    {
        "text": "Ali kitabı okudu",
        "elements": [
            ("özne", ("Ali",), 1, ()),
            ("belirtili nesne", ("kitabı",), 2, ()),
            ("yüklem", ("okudu",), 3, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },
    # özne + belirtisiz nesne + yüklem
    {
        "text": "Annem yemek yaptı",
        "elements": [
            ("özne", ("Annem",), 1, ()),
            ("belirtisiz nesne", ("yemek",), 2, ()),
            ("yüklem", ("yaptı",), 3, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },
    # özne + belirtili nesne + dolaylı tümleç + yüklem
    {
        "text": "Çocuk topu bahçede oynadı",
        "elements": [
            ("özne", ("Çocuk",), 1, ()),
            ("belirtili nesne", ("topu",), 2, ()),
            ("dolaylı tümleç", ("bahçede",), 3, ("yer tamlayıcısı",)),
            ("yüklem", ("oynadı",), 4, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },

    # ── 2. İsim cümlesi (nominal yüklem) ───────────────────────────────────
    {
        "text": "Hava güzel",
        "elements": [
            ("özne", ("Hava",), 1, ()),
            ("yüklem", ("güzel",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "isim", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },
    {
        "text": "Ben öğretmenim",
        "elements": [
            ("özne", ("Ben",), 1, ()),
            ("yüklem", ("öğretmenim",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "isim", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },
    {
        "text": "Bu kitap benim",
        "elements": [
            ("özne", ("Bu", "kitap"), 2, ()),
            ("yüklem", ("benim",), 3, ()),
        ],
        "type": {
            "yuklem_turu": "isim", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },

    # ── 3. Olumsuz: fiil + isim ────────────────────────────────────────────
    {
        "text": "Okula gitmedim",
        "elements": [
            ("dolaylı tümleç", ("Okula",), 1, ("yer tamlayıcısı",)),
            ("yüklem", ("gitmedim",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumsuz",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },
    {
        "text": "Hava güzel değil",
        "elements": [
            ("özne", ("Hava",), 1, ()),
            ("yüklem", ("güzel", "değil"), 2, ()),
        ],
        "type": {
            "yuklem_turu": "isim", "yuklem_yeri": "kurallı", "olumluluk": "olumsuz",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },
    {
        "text": "Param yok",
        "elements": [
            ("özne", ("Param",), 1, ()),
            ("yüklem", ("yok",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "isim", "yuklem_yeri": "kurallı", "olumluluk": "olumsuz",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },

    # ── 4. Soru: ayrı mI + isim cümlesi soru ───────────────────────────────
    {
        "text": "Geldin mi",
        "elements": [
            ("yüklem", ("Geldin", "mi"), 1, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": True, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },
    {
        "text": "Kitabı okudun mu",
        "elements": [
            ("belirtili nesne", ("Kitabı",), 1, ()),
            ("yüklem", ("okudun", "mu"), 2, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": True, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },
    {
        "text": "Hasta mısın",
        "elements": [
            ("yüklem", ("Hasta", "mısın"), 1, ()),
        ],
        "type": {
            "yuklem_turu": "isim", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": True, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },

    # ── 5. Emir / istek / gereklilik / şart ────────────────────────────────
    {
        "text": "Eve git",
        "elements": [
            ("dolaylı tümleç", ("Eve",), 1, ("yer tamlayıcısı",)),
            ("yüklem", ("git",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "emir", "yapi": "basit", "eksiltili": False,
        },
    },
    {
        "text": "Buraya gel",
        "elements": [
            ("dolaylı tümleç", ("Buraya",), 1, ("yer tamlayıcısı",)),
            ("yüklem", ("gel",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "emir", "yapi": "basit", "eksiltili": False,
        },
    },
    {
        "text": "Gidelim",
        "elements": [
            ("yüklem", ("Gidelim",), 1, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "istek", "yapi": "basit", "eksiltili": False,
        },
    },
    {
        "text": "Gitmeliyim",
        "elements": [
            ("yüklem", ("Gitmeliyim",), 1, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "gereklilik", "yapi": "basit", "eksiltili": False,
        },
    },
    {
        "text": "Gelsen",
        "elements": [
            ("yüklem", ("Gelsen",), 1, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "şart", "yapi": "basit", "eksiltili": False,
        },
    },
    {
        "text": "Gelirse gideriz",
        "elements": [
            ("zarf tümleci", ("Gelirse",), 1, ()),
            ("yüklem", ("gideriz",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "birleşik", "eksiltili": False,
        },
    },

    # ── 6. Kurallı vs devrik ───────────────────────────────────────────────
    {
        "text": "Gittim okula",
        "elements": [
            ("yüklem", ("Gittim",), 1, ()),
            ("dolaylı tümleç", ("okula",), 2, ("yer tamlayıcısı",)),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "devrik", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },

    # ── 7. Zarf tümleci ────────────────────────────────────────────────────
    {
        "text": "Çok hızlı koştu",
        "elements": [
            ("zarf tümleci", ("Çok", "hızlı"), 2, ()),
            ("yüklem", ("koştu",), 3, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },
    {
        "text": "Dün geldi",
        "elements": [
            ("zarf tümleci", ("Dün",), 1, ()),
            ("yüklem", ("geldi",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },
    {
        "text": "Yavaşça yürüdü",
        "elements": [
            ("zarf tümleci", ("Yavaşça",), 1, ()),
            ("yüklem", ("yürüdü",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },

    # ── 8. Sıfat+isim öge (özne çok-token) ─────────────────────────────────
    {
        "text": "Kırmızı araba geldi",
        "elements": [
            ("özne", ("Kırmızı", "araba"), 2, ()),
            ("yüklem", ("geldi",), 3, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },
    {
        "text": "Küçük çocuk uyudu",
        "elements": [
            ("özne", ("Küçük", "çocuk"), 2, ()),
            ("yüklem", ("uyudu",), 3, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },

    # ── 9. Birleşik (fiilimsi / yan cümle) ─────────────────────────────────
    {
        "text": "Eve gelince yattım",
        "elements": [
            ("zarf tümleci", ("Eve", "gelince"), 2, ()),
            ("yüklem", ("yattım",), 3, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "birleşik", "eksiltili": False,
        },
    },
    {
        "text": "Koşarak geldi",
        "elements": [
            ("zarf tümleci", ("Koşarak",), 1, ()),
            ("yüklem", ("geldi",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "birleşik", "eksiltili": False,
        },
    },
    {
        "text": "Gülerek konuştu",
        "elements": [
            ("zarf tümleci", ("Gülerek",), 1, ()),
            ("yüklem", ("konuştu",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "birleşik", "eksiltili": False,
        },
    },

    # ── 10. Bağlı / sıralı ─────────────────────────────────────────────────
    {
        "text": "Geldi ve gitti",
        "elements": [
            ("yüklem", ("Geldi",), 1, ()),
            ("cümle dışı unsur", ("ve",), 2, ()),
            ("yüklem", ("gitti",), 3, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "bağlı", "eksiltili": False,
        },
    },
    {
        "text": "Geldi gitti",
        "elements": [
            ("yüklem", ("Geldi",), 1, ()),
            ("yüklem", ("gitti",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "sıralı", "eksiltili": False,
        },
    },

    # ── 11. Çok-öge zengin ─────────────────────────────────────────────────
    {
        "text": "Ali dün okulda kitabı arkadaşına verdi",
        "elements": [
            ("özne", ("Ali",), 1, ()),
            ("zarf tümleci", ("dün",), 2, ()),
            ("dolaylı tümleç", ("okulda",), 3, ("yer tamlayıcısı",)),
            ("belirtili nesne", ("kitabı",), 4, ()),
            ("dolaylı tümleç", ("arkadaşına",), 5, ("yer tamlayıcısı",)),
            ("yüklem", ("verdi",), 6, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },

    # ── Ek: edat tümleci ───────────────────────────────────────────────────
    {
        "text": "Senin için geldim",
        "elements": [
            ("edat tümleci", ("Senin", "için"), 2, ()),
            ("yüklem", ("geldim",), 3, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },
    {
        "text": "Okula doğru yürüdü",
        "elements": [
            ("edat tümleci", ("Okula", "doğru"), 2, ()),
            ("yüklem", ("yürüdü",), 3, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },

    # ── Ek: cümle dışı unsur (hitap / ünlem) ───────────────────────────────
    {
        "text": "Ahmet buraya gel",
        "elements": [
            ("cümle dışı unsur", ("Ahmet",), 1, ()),
            ("dolaylı tümleç", ("buraya",), 2, ("yer tamlayıcısı",)),
            ("yüklem", ("gel",), 3, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "emir", "yapi": "basit", "eksiltili": False,
        },
    },

    # ── Ek: olumsuz fiil + nesne ───────────────────────────────────────────
    {
        "text": "Ödevini yapmadın",
        "elements": [
            ("belirtili nesne", ("Ödevini",), 1, ()),
            ("yüklem", ("yapmadın",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumsuz",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },

    # ── Ek: çoğul/iyelik özne (leksikon adj-kuruntusu; çekimli adj → isim) ──
    {
        "text": "Çocuklar bahçede oynuyor",
        "elements": [
            ("özne", ("Çocuklar",), 1, ()),
            ("dolaylı tümleç", ("bahçede",), 2, ("yer tamlayıcısı",)),
            ("yüklem", ("oynuyor",), 3, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },
    {
        "text": "Öğretmenler geldi",
        "elements": [
            ("özne", ("Öğretmenler",), 1, ()),
            ("yüklem", ("geldi",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },

    # ── Ek: fiil-eşsesli ad özne (Kar/Yaz = ad + imperatif homografı) ──────
    {
        "text": "Kar yağdı",
        "elements": [
            ("özne", ("Kar",), 1, ()),
            ("yüklem", ("yağdı",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },
    {
        "text": "Yaz geldi",
        "elements": [
            ("özne", ("Yaz",), 1, ()),
            ("yüklem", ("geldi",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },

    # ── Ek: zaman adı + durum → zarf tümleci (V2 zaman-adı) ────────────────
    {
        "text": "Akşama gittik",
        "elements": [
            ("zarf tümleci", ("Akşama",), 1, ()),
            ("yüklem", ("gittik",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },

    # ── Ek: kişi zamiri eğik biçim (bana/sana fiil-homografı fix) ──────────
    {
        "text": "Sana söyledim",
        "elements": [
            ("dolaylı tümleç", ("Sana",), 1, ("yer tamlayıcısı",)),
            ("yüklem", ("söyledim",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },

    # ── Ek: demonstratif özne + eğik zamir (hakem HIGH: özne yutulmamalı) ──
    {
        "text": "O bana güldü",
        "elements": [
            ("özne", ("O",), 1, ()),
            ("dolaylı tümleç", ("bana",), 2, ("yer tamlayıcısı",)),
            ("yüklem", ("güldü",), 3, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },

    # ── Ek: cümle-başı pür ünlem → cümle dışı unsur (V2 sinerji) ───────────
    {
        "text": "Haydi gidelim",
        "elements": [
            ("cümle dışı unsur", ("Haydi",), 1, ()),
            ("yüklem", ("gidelim",), 2, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "istek", "yapi": "basit", "eksiltili": False,
        },
    },

    # ── Ek: bağlı cümle iki öznesli (V2 çok-cümle gate: Veli=özne) ─────────
    {
        "text": "Ali geldi ve Veli gitti",
        "elements": [
            ("özne", ("Ali",), 1, ()),
            ("yüklem", ("geldi",), 2, ()),
            ("cümle dışı unsur", ("ve",), 3, ()),
            ("özne", ("Veli",), 4, ()),
            ("yüklem", ("gitti",), 5, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "bağlı", "eksiltili": False,
        },
    },

    # ── Ek: gelecek zaman haber ────────────────────────────────────────────
    {
        "text": "Yarın sinemaya gideceğiz",
        "elements": [
            ("zarf tümleci", ("Yarın",), 1, ()),
            ("dolaylı tümleç", ("sinemaya",), 2, ("yer tamlayıcısı",)),
            ("yüklem", ("gideceğiz",), 3, ()),
        ],
        "type": {
            "yuklem_turu": "fiil", "yuklem_yeri": "kurallı", "olumluluk": "olumlu",
            "soru": False, "kip": "haber", "yapi": "basit", "eksiltili": False,
        },
    },
]
