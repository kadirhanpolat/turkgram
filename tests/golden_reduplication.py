"""golden_reduplication.py — Faz 9d ikileme üretimi, bağımsız golden (motor-körü).

Elle-doğrulanmış biçimler; motora bakılmadan dilbilgisi kurallarından türetildi.
"""

# Tam tekrar: sözcük iki kez, aralarında boşluk. Her POS'tan örnekler.
GOLDEN_FULL: list[tuple[str, str]] = [
    # (sözcük, beklenen_çıktı)
    ("yavaş", "yavaş yavaş"),        # zarf/sıfat
    ("çok", "çok çok"),              # zarf
    ("güzel", "güzel güzel"),        # sıfat
    ("büyük", "büyük büyük"),        # sıfat
    ("küçük", "küçük küçük"),        # sıfat
    ("koşa", "koşa koşa"),           # ulaç (biçim)
    ("ev", "ev ev"),                 # isim
    ("kapı", "kapı kapı"),           # isim
    ("sıra", "sıra sıra"),           # isim
    ("damla", "damla damla"),        # isim
    ("kim", "kim kim"),              # zamir
    ("ne", "ne ne"),                 # zamir
    ("hızlı", "hızlı hızlı"),        # sıfat/zarf
    ("ağır", "ağır ağır"),           # zarf
    ("teker", "teker teker"),        # isim
    ("uzun", "uzun uzun"),           # sıfat
]

# Ulaç ikilemesi: mastar → -A ulaç biçimi, ikiz yazılır.
# Ses uyumu: son ünlü a/ı/o/u → a; e/i/ö/ü → e.
# Ünlü-final gövde → glide y; ye_de yumuşama ünlü-başlı ekte tetiklenir.
GOLDEN_CONVERB: list[tuple[str, str]] = [
    # (mastar, beklenen_ikileme)
    ("koşmak", "koşa koşa"),         # koş (o→a)
    ("gülmek", "güle güle"),         # gül (ü→e)
    ("gitmek", "gide gide"),         # git→gid (ye_de), (i→e)
    ("gelmek", "gele gele"),         # gel (e→e)
    ("yemek", "yiye yiye"),          # ye→yi (yumuşama) + glide
    ("okumak", "okuya okuya"),       # oku (u→a) + glide
    ("ağlamak", "ağlaya ağlaya"),    # ağla (a→a) + glide
    ("bakmak", "baka baka"),         # bak (a→a)
    ("anlamak", "anlaya anlaya"),    # anla (a→a) + glide
    ("söylemek", "söyleye söyleye"), # söyle (e→e) + glide
    ("içmek", "içe içe"),            # iç (i→e)
    ("vermek", "vere vere"),         # ver (e→e)
    ("almak", "ala ala"),            # al (a→a)
    ("yazmak", "yaza yaza"),         # yaz (a→a)
    ("çalışmak", "çalışa çalışa"),   # çalış (ı→a)
    ("oynamak", "oynaya oynaya"),    # oyna (a→a) + glide
    ("düşünmek", "düşüne düşüne"),   # düşün (ü→e)
    ("bilmek", "bile bile"),         # bil (i→e)
    ("görmek", "göre göre"),         # gör (ö→e)
    ("istemek", "isteye isteye"),    # iste (e→e) + glide
]

# m-ikilemesi: ünsüz-başlı → ilk ünsüz m'ye çevrilir;
# ünlü-başlı → başa m eklenir. Sonuç: orijinal + " " + m_biçimi.
GOLDEN_M: list[tuple[str, str]] = [
    # (sözcük, beklenen_çıktı)
    ("kitap", "kitap mitap"),        # k→m
    ("çiçek", "çiçek miçek"),        # ç→m
    ("telefon", "telefon melefon"),  # t→m
    ("kalem", "kalem malem"),        # k→m
    ("bardak", "bardak mardak"),     # b→m
    ("dost", "dost most"),           # d→m
    ("para", "para mara"),           # p→m
    ("araba", "araba maraba"),       # ünlü-başlı → m eklenir
    ("ev", "ev mev"),                # ünlü-başlı
    ("insan", "insan minsan"),       # ünlü-başlı
    ("okul", "okul mokul"),          # ünlü-başlı
    ("bahçe", "bahçe mahçe"),        # b→m
    ("fırın", "fırın mırın"),        # f→m
    ("yemek", "yemek memek"),        # y→m
    ("tablo", "tablo mablo"),        # t→m
    ("duman", "duman muman"),        # d→m
    ("şeker", "şeker meker"),        # ş→m
    ("büyük", "büyük müyük"),        # b→m
    ("küçük", "küçük müçük"),        # k→m
    ("güzel", "güzel müzel"),        # g→m
]

# m-başlı sözcükler: m-ikilemesi anlamsız → ValueError beklenir.
GOLDEN_M_ERROR: list[str] = [
    "masa",
    "makine",
    "mavi",
    "mektup",
]
