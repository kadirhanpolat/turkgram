"""
Motor-körü bağımsız golden — syllabify + stress_mark
Kaynak: Türkçe hece kuralları (dilbilgisi); turkgram kaynak koduna BAKILMADI.

Hece kuralları:
  - Her hecede tam olarak BİR ünlü.
  - Ünlüler: a e ı i o ö u ü â î û
  - V+C+V  → V·CV   (tek ünsüz sağa)
  - V+CC+V → VC·CV  (birincisi solda, ikincisi sağda)
  - V+CCC+V→ VCC·CV (ilk ikisi solda, son sağda)
  - VV     → V·V    (iki ünlü yan yana → yeni hece)
  - Sözcük-sonu ünsüzler son hecede kalır.

Vurgu: varsayılan SON hece (0-tabanlı son indeks).
İstisnalar: yer adları ve alıntı sözcükler elle doğrulanmıştır.
"""

# ---------------------------------------------------------------------------
# SYLLABIFY_CASES
# (surface, expected_syllables, expected_stress_index)
# stress_index: 0-tabanlı, soldan sayılır
# ---------------------------------------------------------------------------
SYLLABIFY_CASES = [
    # --- Temel CV / CVC ---
    ("ara",      ["a", "ra"],        1),   # a·RA
    ("oku",      ["o", "ku"],        1),   # o·KU
    ("eve",      ["e", "ve"],        1),   # e·VE
    ("gel",      ["gel"],            0),   # GEL
    ("al",       ["al"],             0),   # AL
    ("ev",       ["ev"],             0),   # EV
    ("at",       ["at"],             0),   # AT
    ("ip",       ["ip"],             0),   # İP

    # --- V+CC+V: birinci ünsüz solda, ikinci sağda ---
    ("aldı",     ["al", "dı"],       1),   # al·DI
    ("erken",    ["er", "ken"],      1),   # er·KEN
    ("elbise",   ["el", "bi", "se"], 2),   # el·bi·SE
    ("kaldı",    ["kal", "dı"],      1),   # kal·DI
    ("ördek",    ["ör", "dek"],      1),   # ör·DEK

    # --- V+CCC+V: ilk iki ünsüz solda, son sağda ---
    ("türkçe",   ["türk", "çe"],     1),   # türk·ÇE
    ("kartlı",   ["kart", "lı"],     1),   # kart·LI

    # --- VV yan yana → yeni hece ---
    ("ait",      ["a", "it"],        1),   # a·İT
    ("saat",     ["sa", "at"],       1),   # sa·AT
    ("aile",     ["a", "i", "le"],   2),   # a·i·LE
    ("şair",     ["şa", "ir"],       1),   # şa·İR

    # --- Çok heceli genel ---
    ("geldi",    ["gel", "di"],      1),   # gel·Dİ
    ("geldiğimiz", ["gel", "di", "ği", "miz"], 3),  # gel·di·ği·MİZ
    ("okuyorum", ["o", "ku", "yo", "rum"],   3),    # o·ku·yo·RUM
    ("öğrenci",  ["öğ", "ren", "ci"],        2),    # öğ·ren·Cİ
    ("çalışıyor", ["ça", "lı", "şı", "yor"], 3),   # ça·lı·şı·YOR
    ("kitap",    ["ki", "tap"],              1),    # ki·TAP
    ("anlatıyordu", ["an", "la", "tı", "yor", "du"], 4),  # an·la·tı·yor·DU
    ("okul",     ["o", "kul"],               1),   # o·KUL
    ("araba",    ["a", "ra", "ba"],          2),   # a·ra·BA
    ("telefon",  ["te", "le", "fon"],        2),   # te·le·FON

    # --- İstisnalar: yer adları (elle doğrulanmış) ---
    ("ankara",     ["an", "ka", "ra"],              0),   # AN·ka·ra
    ("istanbul",   ["is", "tan", "bul"],            1),   # is·TAN·bul
    ("izmir",      ["iz", "mir"],                   0),   # İZ·mir
    ("bursa",      ["bur", "sa"],                   0),   # BUR·sa
    ("adana",      ["a", "da", "na"],               1),   # a·DA·na
    ("konya",      ["kon", "ya"],                   0),   # KON·ya
    ("erzurum",    ["er", "zu", "rum"],             0),   # ER·zu·rum
    ("trabzon",    ["trab", "zon"],                 0),   # TRAB·zon
    ("samsun",     ["sam", "sun"],                  0),   # SAM·sun
    ("malatya",    ["ma", "lat", "ya"],             1),   # ma·LAT·ya
    ("eskişehir",  ["es", "ki", "şe", "hir"],       0),   # ES·ki·şe·hir
    ("kayseri",    ["kay", "se", "ri"],             0),   # KAY·se·ri
    ("diyarbakır", ["di", "yar", "ba", "kır"],      0),   # Dİ·yar·ba·kır
    ("gaziantep",  ["ga", "zi", "an", "tep"],       2),   # ga·zi·AN·tep
    ("antalya",    ["an", "tal", "ya"],             1),   # an·TAL·ya
    ("denizli",    ["de", "niz", "li"],             2),   # de·niz·Lİ

    # --- İstisnalar: alıntı sözcükler ---
    ("stres",    ["stres"],          0),   # STRES
    ("tren",     ["tren"],           0),   # TREN
    ("spor",     ["spor"],           0),   # SPOR

    # --- Yabancı onset kümeleri (tr, kr vb.) — maksimal onset C1 düzeltmesi ---
    ("elektrik", ["e", "lek", "trik"],       2),   # e·lek·TRİK  (tr geçerli onset)
    ("kontrol",  ["kon", "trol"],            1),   # kon·TROL    (tr geçerli onset)
    ("endüstri", ["en", "düs", "tri"],       2),   # en·düs·TRİ  (tr geçerli onset)

    # --- Şapkalı (circumflex) ünlüler ---
    ("kâtip",    ["kâ", "tip"],      1),   # kâ·TİP
    ("rûh",      ["rûh"],            0),   # RÛH

    # --- Kenar durumlar ---
    ("",         [],                 None),   # boş
    ("a",        ["a"],              0),      # tek ünlü
    ("krt",      ["krt"],            0),      # ünlüsüz
]

# ---------------------------------------------------------------------------
# STRESS_MARK_CASES
# (surface, expected_mark)
# Ayraç: · (U+00B7 MIDDLE DOT)
# Vurgulu hece BÜYÜK HARF (Türkçe bilinçli: i→İ, ı→I)
# stress_mark() input'u _tr_lower ile normalizer → büyük harf girişi tolere edilir
# ---------------------------------------------------------------------------
STRESS_MARK_CASES = [
    # Temel çok heceli
    ("geldi",    "gel·Dİ"),
    ("aldı",     "al·DI"),
    ("araba",    "a·ra·BA"),
    ("elbise",   "el·bi·SE"),
    ("kitap",    "ki·TAP"),
    ("okul",     "o·KUL"),
    ("telefon",  "te·le·FON"),

    # VV yan yana
    ("ait",      "a·İT"),
    ("saat",     "sa·AT"),
    ("aile",     "a·i·LE"),
    ("şair",     "şa·İR"),

    # Çok heceli
    ("okuyorum", "o·ku·yo·RUM"),
    ("öğrenci",  "öğ·ren·Cİ"),
    ("çalışıyor","ça·lı·şı·YOR"),
    ("anlatıyordu","an·la·tı·yor·DU"),
    ("geldiğimiz","gel·di·ği·MİZ"),

    # İstisnalar: yer adları
    ("ankara",     "AN·ka·ra"),
    ("istanbul",   "is·TAN·bul"),
    ("izmir",      "İZ·mir"),
    ("bursa",      "BUR·sa"),
    ("adana",      "a·DA·na"),
    ("konya",      "KON·ya"),
    ("erzurum",    "ER·zu·rum"),
    ("trabzon",    "TRAB·zon"),
    ("samsun",     "SAM·sun"),
    ("malatya",    "ma·LAT·ya"),
    ("eskişehir",  "ES·ki·şe·hir"),
    ("kayseri",    "KAY·se·ri"),
    ("diyarbakır", "Dİ·yar·ba·kır"),
    ("gaziantep",  "ga·zi·AN·tep"),
    ("antalya",    "an·TAL·ya"),
    ("denizli",    "de·niz·Lİ"),

    # Alıntı sözcükler
    ("stres",    "STRES"),
    ("tren",     "TREN"),
    ("spor",     "SPOR"),

    # Şapkalı
    ("kâtip",    "kâ·TİP"),

    # Yabancı onset kümeleri — C1 düzeltmesi
    ("elektrik", "e·lek·TRİK"),

    # Büyük harf girişi (normaliser tolere eder)
    # ASCII "I" (U+0049) → _tr_lower → "ı" (undotted) → _tr_upper → "I" (undotted)
    # "GELDI" burada "I" undotted-I olduğundan çıktısı gel·DI (İ değil)
    ("GELDI",    "gel·DI"),
    ("ARABA",    "a·ra·BA"),

    # Kenar durumlar
    ("",    ""),
    ("a",   "A"),
    ("krt", "KRT"),
]
