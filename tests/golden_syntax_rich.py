"""E1 zengin öbek üretimi — bağımsız golden (motor-körü, elle doğrulanmış).

Her giriş: (fonksiyon, kwargs, beklenen_çıktı)
"""

NP_URET_CASES = [
    # (head, kwargs, beklenen)
    ("kapı",  {"durum": "nom"},                              "kapı"),
    ("kapı",  {"tamlayan": "ev"},                            "evin kapısı"),
    ("kapı",  {"tamlayan": "ev", "durum": "acc"},            "evin kapısını"),
    ("kapı",  {"on_sifatlar": ("büyük",), "tamlayan": "ev", "durum": "acc"}, "büyük evin kapısını"),
    ("kitap", {"miktar": "üç", "durum": "dat"},              "üç kitaba"),
    ("araba", {"on_sifatlar": ("kırmızı", "büyük")},         "kırmızı büyük araba"),
    ("ev",    {"iyelik": "1sg"},                             "evim"),
    ("ev",    {"iyelik": "2sg", "durum": "dat"},             "evine"),
    ("öğrenci", {"tamlayan": "okul"},                        "okulun öğrencisi"),
]

PP_URET_CASES = [
    # (isim, edat, kwargs, beklenen)
    ("ev",    "göre",  {},                  "eve göre"),
    ("okul",  "için",  {},                  "okul için"),
    ("okul",  "ile",   {"bitişik": True},   "okulla"),
    ("araba", "kadar", {},                  "arabaya kadar"),
    ("ben",   "göre",  {},                  "bana göre"),
]

DEGMOD_URET_CASES = [
    # (baş, kwargs, beklenen)
    ("hızlı",   {},                    "hızlı"),
    ("hızlı",   {"derece": "çok"},     "çok hızlı"),
    ("güzel",   {"derece": "oldukça"}, "oldukça güzel"),
    ("iyi",     {"derece": "en"},      "en iyi"),
    ("büyük",   {"derece": "daha"},    "daha büyük"),
]

KOORDINE_NP_CASES = [
    # (ogeler, baglac, beklenen)
    (["kitap", "defter"],          "ve",   "kitap ve defter"),
    (["kitap", "defter"],          "veya", "kitap veya defter"),
    (["kitap", "defter", "kalem"], "ve",   "kitap, defter ve kalem"),
    (["ev", "araba"],              "ama",  "ev ama araba"),
]
