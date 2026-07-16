"""Metin normalleştirme: sayı→sözel, tarih/saat, kısaltma, IPA-öncesi pipeline."""
from __future__ import annotations
import math
import re

_ONES = ["", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
_TENS = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]
_MONTHS = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
    7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık",
}
_MONTH_ABBR = {v.lower(): k for k, v in _MONTHS.items()}

_ABBREV_TABLE: dict[str, str] = {
    "TL": "türk lirası", "USD": "dolar", "EUR": "euro",
    "km": "kilometre", "cm": "santimetre", "m": "metre",
    "kg": "kilogram", "gr": "gram", "g": "gram",
    "m²": "metrekare", "m³": "metreküp",
    "%": "yüzde", "@": "et",
    "No": "numara", "no": "numara",
    "Dr": "doktor", "Prof": "profesör", "Öğr": "öğrenci",
    "vb": "ve benzeri", "vd": "ve diğerleri",
    "TDK": "Türk Dil Kurumu",
    "TBMM": "Türkiye Büyük Millet Meclisi",
    "TC": "Türkiye Cumhuriyeti",
    "MEB": "Millî Eğitim Bakanlığı",
    "TRT": "Türkiye Radyo ve Televizyon Kurumu",
    "BM": "Birleşmiş Milletler",
    "AB": "Avrupa Birliği",
    "NATO": "NATO",
    "TV": "televizyon",
    "PC": "bilgisayar",
    "vb.": "ve benzeri", "vd.": "ve diğerleri",
    "vs": "ve saire", "vs.": "ve saire",
    "sn": "sayın", "Sn": "sayın",
}


def _chunk_to_words(n: int) -> str:
    """0-999 arasını sözel çevirir."""
    if n == 0:
        return ""
    parts = []
    hundreds = n // 100
    remainder = n % 100
    tens = remainder // 10
    ones = remainder % 10
    if hundreds == 1:
        parts.append("yüz")
    elif hundreds > 1:
        parts.append(_ONES[hundreds] + " yüz")
    if tens:
        parts.append(_TENS[tens])
    if ones:
        parts.append(_ONES[ones])
    return " ".join(parts)


def number_to_words(n: int) -> str:
    """Tam sayıyı Türkçe sözel gösterimine çevirir."""
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError(f"int beklendi, {type(n).__name__} geldi")
    if n == 0:
        return "sıfır"
    if n < 0:
        return "eksi " + number_to_words(-n)
    parts = []
    trilyon = n // 1_000_000_000_000
    n %= 1_000_000_000_000
    milyar = n // 1_000_000_000
    n %= 1_000_000_000
    milyon = n // 1_000_000
    n %= 1_000_000
    bin_ = n // 1_000
    remainder = n % 1_000
    if trilyon:
        parts.append(_chunk_to_words(trilyon) + " trilyon")
    if milyar:
        parts.append(_chunk_to_words(milyar) + " milyar")
    if milyon:
        parts.append(_chunk_to_words(milyon) + " milyon")
    if bin_ == 1:
        parts.append("bin")
    elif bin_ > 1:
        parts.append(_chunk_to_words(bin_) + " bin")
    if remainder:
        parts.append(_chunk_to_words(remainder))
    return " ".join(parts)


def float_to_words(n: float) -> str:
    """Ondalık sayıyı Türkçe sözel gösterimine çevirir."""
    if math.copysign(1.0, n) < 0:
        return "eksi " + float_to_words(-n)
    s = str(n)
    if "." in s:
        int_part, dec_part = s.split(".", 1)
    else:
        int_part, dec_part = s, ""
    result = number_to_words(int(int_part))
    if dec_part:
        digits = " ".join(number_to_words(int(d)) for d in dec_part)
        result += " virgül " + digits
    return result


def date_to_words(gün: int, ay: "str | int", yıl: int) -> str:
    """Tarih bileşenlerini Türkçe sözel biçime çevirir."""
    if isinstance(ay, int):
        if not 1 <= ay <= 12:
            raise ValueError(f"Geçersiz ay: {ay}. 1-12 arasında olmalı.")
        ay_adı = _MONTHS[ay]
    else:
        ay_lower = ay.lower()
        if ay_lower in _MONTH_ABBR:
            ay_adı = _MONTHS[_MONTH_ABBR[ay_lower]]
        else:
            ay_adı = ay
    return f"{number_to_words(gün)} {ay_adı} {number_to_words(yıl)}"


def time_to_words(saat: int, dakika: int) -> str:
    """Saat ve dakikayı Türkçe sözel biçime çevirir."""
    if not (0 <= saat <= 23 and 0 <= dakika <= 59):
        raise ValueError(f"Geçersiz saat/dakika: {saat}:{dakika}. 0-23 / 0-59 arasında olmalı.")
    if dakika == 0:
        return number_to_words(saat)
    if saat == 0:
        return f"sıfır {number_to_words(dakika)}"
    return f"{number_to_words(saat)} {number_to_words(dakika)}"


def expand_abbreviation(token: str) -> str:
    """Kapalı tabloda kısaltmayı genişletir; bilinmeyen → aynen döner."""
    return _ABBREV_TABLE.get(token, _ABBREV_TABLE.get(token.upper(), token))


def normalize(text: str) -> str:
    """Token bazlı pipeline: sayı + kısaltma + sembol genişletme."""
    tokens = text.split()
    result = []
    for token in tokens:
        if re.fullmatch(r"-?\d+", token):
            result.append(number_to_words(int(token)))
        else:
            result.append(expand_abbreviation(token))
    return " ".join(result)
