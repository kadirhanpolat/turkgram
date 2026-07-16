# tests/golden_normalization.py
# Motor-körü bağımsız golden — normalization.py

NUMBER_WORDS = [
    # (n, beklenen)
    (0,            "sıfır"),
    (1,            "bir"),
    (10,           "on"),
    (11,           "on bir"),
    (19,           "on dokuz"),
    (100,          "yüz"),
    (101,          "yüz bir"),
    (200,          "iki yüz"),
    (1000,         "bin"),          # "bir bin" DEĞİL
    (1001,         "bin bir"),
    (2000,         "iki bin"),
    (10000,        "on bin"),
    (100000,       "yüz bin"),
    (1000000,      "bir milyon"),
    (1000001,      "bir milyon bir"),
    (-42,          "eksi kırk iki"),
    (42,           "kırk iki"),
    (2026,         "iki bin yirmi altı"),
    (999999999999, "dokuz yüz doksan dokuz milyar dokuz yüz doksan dokuz milyon dokuz yüz doksan dokuz bin dokuz yüz doksan dokuz"),
]

FLOAT_WORDS = [
    (3.14,  "üç virgül bir dört"),
    (-3.14, "eksi üç virgül bir dört"),
    (0.5,   "sıfır virgül beş"),
    (-0.5,  "eksi sıfır virgül beş"),
]

DATE_WORDS = [
    ((15, "Temmuz", 2026), "on beş Temmuz iki bin yirmi altı"),
    ((1,  "Ocak",   2000), "bir Ocak iki bin"),
    ((1,  1,        2025), "bir Ocak iki bin yirmi beş"),
]

TIME_WORDS = [
    ((14, 30), "on dört otuz"),
    ((9,   5), "dokuz beş"),
    ((9,   0), "dokuz"),
    ((0,   5), "sıfır beş"),
    ((0,   0), "sıfır"),
]

ABBREV = [
    ("TL",   "türk lirası"),
    ("km",   "kilometre"),
    ("%",    "yüzde"),
    ("@",    "et"),
    ("vb",   "ve benzeri"),
    ("xyz",  "xyz"),
]

NORMALIZE = [
    ("42 km yol",   "kırk iki kilometre yol"),
    ("TL 100",      "türk lirası yüz"),
    ("merhaba",     "merhaba"),
]
