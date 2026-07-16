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
    return s.replace("İ", "i").replace("I", "ı").lower()


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
