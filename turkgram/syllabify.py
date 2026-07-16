# turkgram/syllabify.py
"""Türkçe hecelemleme ve vurgu."""

__all__ = ["syllabify", "stress", "stress_mark"]

_VOWELS = frozenset("aeıioöuüâîû")

_SYLLABLE_SEP = "·"  # U+00B7 MIDDLE DOT

# str.upper() kullanılmaz: i→I (hatalı). _tr_upper i→İ, ı→I yapar.
_TR_UPPER_MAP = str.maketrans(
    "aeıioöuübcçdfgğhjklmnprsştvyz",
    "AEIİOÖUÜBCÇDFGĞHJKLMNPRSŞTVYZ",
)


def _tr_upper(s: str) -> str:
    return s.translate(_TR_UPPER_MAP)


def _tr_lower(s: str) -> str:
    return s.replace("İ", "i").replace("I", "i").lower()


# Anahtar: _tr_lower() normalize edilmiş; Değer: 0-tabanlı vurgulu hece (baştan)
# Kaynak: elle küratörlenmiş, üçüncü taraf kaynak yok.
_STRESS_EXCEPTIONS: dict[str, int] = {
    # Yer adları
    "ankara": 0,
    "istanbul": 1,
    "izmir": 0,
    "bursa": 0,
    "adana": 1,
    "konya": 0,
    "erzurum": 0,
    "trabzon": 0,
    "samsun": 0,
    "malatya": 1,
    "eskişehir": 0,
    "kayseri": 0,
    "diyarbakır": 0,
    "gaziantep": 2,
    "mersin": 0,
    "kocaeli": 2,
    "antalya": 1,
    "denizli": 2,
    "sivas": 0,
    "van": 0,
    "muş": 0,
    "batman": 0,
    "rize": 0,
    "artvin": 0,
    # Alıntı sözcükler (kapalı küme — yalnız kesin olanlar)
    "stres": 0,
    "tren": 0,
    "spor": 0,
    "klima": 1,
    "bisiklet": 1,
    "otobüs": 1,
    "trafik": 0,
}


def syllabify(word: str) -> list[str]:
    """Sözcüğü hecelerine böl.

    syllabify("geldiğimiz")  # → ["gel", "di", "ği", "miz"]
    syllabify("Türkçe")      # → ["Türk", "çe"]
    syllabify("ait")         # → ["a", "it"]   (VV → V·V)
    syllabify("")            # → []
    syllabify("krt")         # → ["krt"]        (ünlüsüz pasif geçiş)
    """
    if not word:
        return []

    vowel_positions = [i for i, c in enumerate(word) if c in _VOWELS]

    if not vowel_positions:
        return [word]

    syllables: list[str] = []
    start = 0

    for idx, vpos in enumerate(vowel_positions[:-1]):
        next_vpos = vowel_positions[idx + 1]
        consonants_start = vpos + 1
        n_consonants = next_vpos - consonants_start

        if n_consonants == 0:
            # VV: ikinci ünlü yeni hece başlatır
            cut = next_vpos
        elif n_consonants == 1:
            # V·CV: ünsüz sağa
            cut = consonants_start
        elif n_consonants == 2:
            # VC·CV: ortadan
            cut = consonants_start + 1
        else:
            # VCC·CV (ve daha uzun kümeler): maksimal onset — son ünsüz sağa kalır
            cut = consonants_start + (n_consonants - 1)

        syllables.append(word[start:cut])
        start = cut

    syllables.append(word[start:])
    return syllables


def stress(word: str) -> int | None:
    """Vurgulu heceye 0-tabanlı indeks (baştan). Boş string için None.

    stress("geldi")    # → 1  (son hece)
    stress("ankara")   # → 0  (istisna)
    stress("istanbul") # → 1  (istisna: is·TAN·bul)
    stress("")         # → None
    stress("krt")      # → 0  (ünlüsüz: tek "hece"; anlamlı vurgu yok,
                       #        yalnız indeks tutarlılığı)
    """
    if not word:
        return None
    syllables = syllabify(word)
    if not syllables:
        return None
    key = _tr_lower(word)
    if key in _STRESS_EXCEPTIONS:
        return _STRESS_EXCEPTIONS[key]
    return len(syllables) - 1


def stress_mark(word: str) -> str:
    """Vurgulu heceyi büyük harfle + U+00B7 ayracıyla göster.

    Girdi _tr_lower ile normalize edilir; her iki iç çağrı (syllabify + stress)
    normalize edilmiş string üzerinden yapılır.

    stress_mark("geldi")    # → "gel·Dİ"
    stress_mark("istanbul") # → "is·TAN·bul"
    stress_mark("ankara")   # → "AN·ka·ra"
    stress_mark("")         # → ""
    stress_mark("krt")      # → "KRT"
    """
    if not word:
        return ""
    normalized = _tr_lower(word)          # tek normalize noktası
    syllables = syllabify(normalized)     # normalize üzerinden
    if not syllables:
        return ""
    idx = stress(normalized)              # normalize üzerinden (istisna tablosu aynı key)
    if idx is None:
        return ""
    marked = [
        _tr_upper(s) if i == idx else s
        for i, s in enumerate(syllables)
    ]
    return _SYLLABLE_SEP.join(marked)
