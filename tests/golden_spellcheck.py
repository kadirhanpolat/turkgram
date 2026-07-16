"""Motor-körü bağımsız golden — spellcheck (Faz 9b).
Kaynak: Türkçe dilbilgisi; turkgram kaynak koduna BAKILMADI.

Bu dosya YALNIZ veri içerir (liste). Assert/pytest yoktur.

Kapsanan API:
- is_valid(word) -> bool
- suggest(word, max_distance=2) -> list[str]  (V1: KÖK/lemma döner, yüzey biçim değil)
- check(word) -> SpellResult(word, is_valid, suggestions: tuple[str, ...])

Türkçe karakter konfüzyonları (distance=0.5 her biri):
  ı↔i, ö↔o, ü↔u, ş↔s, ç↔c, ğ↔g
Birden çok konfüzyon toplanır (ör. gozluk: ö/o + ü/u = 1.0).
"""

# ---------------------------------------------------------------------------
# IS_VALID_CASES: (word, expected_bool)
#   True  -> morfolojik olarak geçerli Türkçe (kök veya agglütinatif çekim)
#   False -> bozuk / geçersiz / edge
# ---------------------------------------------------------------------------
IS_VALID_CASES = [
    # --- Basit kökler (True) ---
    ("ev", True),          # çıplak isim kökü
    ("gelmek", True),      # fiil mastarı
    ("güzel", True),       # sıfat kökü
    ("kitap", True),       # isim kökü
    ("araba", True),       # ünlü-final isim kökü

    # --- Çekimli formlar / agglütinasyon (True) ---
    ("evde", True),        # ev + bulunma (locative)
    ("evlerde", True),     # ev + çoğul + bulunma
    ("geliyorum", True),   # gel + şimdiki zaman + 1sg
    ("gidecekler", True),  # git->gid + gelecek + 3pl
    ("okudum", True),      # oku + görülen geçmiş + 1sg
    ("güzeldir", True),    # güzel + ekfiil bildirme -dir

    # --- Karmaşık çekim (True) ---
    ("öğrenciyim", True),  # öğrenci + ekfiil 1sg (kaynaştırma -y-)
    ("kitabımda", True),   # kitap + iyelik 1sg + bulunma (durum çekimi)

    # --- Bozuk / geçersiz (False) ---
    ("evdte", False),      # bozuk: fazla/yanlış ünsüz kümesi
    ("gelioyrm", False),   # bozuk: harf sırası bozuk (geliyorum)
    ("guzl", False),       # bozuk: ünlü eksik (güzel)
    ("ktap", False),       # bozuk: ünlü eksik (kitap)

    # --- Edge (False) ---
    ("", False),           # boş string
    ("a" * 201, False),    # aşırı uzun (201 karakter, 200+ eşiği)
]

# ---------------------------------------------------------------------------
# SUGGEST_CASES: (word, must_include_root, max_distance)
#   must_include_root: suggest() sonucunda ZORUNLU bulunması gereken KÖK lemma
#   (yüzey biçim değil; çıplak isim / mastar fiil / kök sıfat)
# ---------------------------------------------------------------------------
SUGGEST_CASES = [
    # --- Tek Türkçe karakter konfüzyonu (distance=0.5) ---
    ("seker", "şeker", 2),   # ş/s
    ("cok", "çok", 2),       # ç/c
    ("kapi", "kapı", 2),     # ı/i
    ("dag", "dağ", 2),       # ğ/g
    ("gul", "gül", 2),       # ü/u
    ("goz", "göz", 2),       # ö/o

    # --- İki karakter konfüzyonu tek kelimede (distance=1.0) ---
    ("uc", "üç", 2),         # ü/u + ç/c = 1.0
    ("gozluk", "gözlük", 2), # ö/o + ü/u = 1.0

    # --- Normal Levenshtein (distance=1.0) ---
    ("kiyap", "kitap", 2),   # y->t yerdeğişim/ikame
    ("evd", "ev", 2),        # fazla harf -> kök ev bulunmalı

    # --- max_distance eşik edge (0.5 tam sınır) ---
    ("seker", "şeker", 0.5), # yalnız ş/s konfüzyonu = 0.5, eşikte bulunmalı
]

# ---------------------------------------------------------------------------
# CHECK_CASES: (word, expected_is_valid, expected_roots_in_suggestions)
#   is_valid=True  -> suggestions=() (boş tuple), beklenen kök yok
#   is_valid=False -> expected_roots_in_suggestions içindeki köklerden
#                     EN AZ BİRİ suggestions tuple'ında olmalı.
#                     () verilirse öneri belirsiz -> herhangi (boş dahil) kabul.
# ---------------------------------------------------------------------------
CHECK_CASES = [
    # --- Geçerli: öneri yok ---
    ("ev", True, ()),         # çıplak isim kökü
    ("evde", True, ()),       # çekimli geçerli
    ("gelmek", True, ()),     # fiil mastarı geçerli
    ("okudum", True, ()),     # çekimli geçerli

    # --- Geçersiz: kök önerisi beklenir ---
    ("seker", False, ("şeker",)),   # ş/s
    ("cok", False, ("çok",)),       # ç/c
    ("kapi", False, ("kapı",)),     # ı/i ; kapı isim kökü (lemma)
    ("gozluk", False, ("gözlük",)), # ö/o + ü/u ; gözlük isim kökü

    # --- Geçersiz ama öneri belirsiz: boş tuple = herhangi kabul ---
    ("evdte", False, ()),     # bozuk, tek net kök yok
]
