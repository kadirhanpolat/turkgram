# tests/golden_tokenize.py
# Bağımsız golden — tokenize() motoruna BAKMADAN elle doğrulanmış.
# SAF VERİ — pytest toplamaz (test_ öneki yok, sınıf yok).

GOLDEN_TOKENIZE = [
    # (girdi, beklenen çıktı)

    # Temel boşluk bölme
    ("Ali geldi", ["Ali", "geldi"]),
    ("", []),
    ("  ", []),

    # Son noktalama
    ("Ali geldi.", ["Ali", "geldi", "."]),
    ("Nereye gidiyorsun?", ["Nereye", "gidiyorsun", "?"]),
    ("Dur!", ["Dur", "!"]),

    # İç noktalama (virgül)
    ("geldi, gitti", ["geldi", ",", "gitti"]),
    ("bir, iki, üç", ["bir", ",", "iki", ",", "üç"]),

    # Parantez
    ("(eve) gitti", ["(", "eve", ")", "gitti"]),
    ("Ali (öğretmen) geldi", ["Ali", "(", "öğretmen", ")", "geldi"]),

    # Apostrof bölme — apostrof sağ parçada kalır
    ("Ankara'nın", ["Ankara", "'nın"]),
    ("Türkiye'de", ["Türkiye", "'de"]),
    ("İstanbul'dan", ["İstanbul", "'dan"]),

    # Apostrof + cümle noktalama
    ("Ankara'nın sınırı.", ["Ankara", "'nın", "sınırı", "."]),

    # Saf noktalama metin
    ("...", [".", ".", "."]),
    ("!?", ["!", "?"]),

    # Karma cümle
    ("Ali geldi, Ayşe gitti.", ["Ali", "geldi", ",", "Ayşe", "gitti", "."]),

    # İki nokta / noktalı virgül
    ("şöyle:", ["şöyle", ":"]),
    ("birinci; ikinci", ["birinci", ";", "ikinci"]),

    # Tırnak
    ('"merhaba"', ['"', "merhaba", '"']),

    # Apostrof olmayan kelime ortasında özel karakter yok
    ("okul", ["okul"]),
    ("gidiyorum", ["gidiyorum"]),

    # Çoklu boşluk
    ("ali   geldi", ["ali", "geldi"]),

    # Sayı + noktalama
    ("3.", ["3", "."]),
    ("2026'da", ["2026", "'da"]),

    # Kıvrık apostrof (U+2019) bölünmez — tek token olarak kalır (bilinen sınır)
    ("Türkiye’de", ["Türkiye’de"]),
]
