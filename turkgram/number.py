"""number.py — sayı morfolojisi: ordinal (-IncI) ve distributif (-şAr/-Ar)."""
from __future__ import annotations
from .morphology import ends_in_vowel, high_vowel, low_vowel


def _tr_lower(s: str) -> str:
    """Türkçe büyük harf duyarlı küçültme: İ→i, I→ı, ardından lower()."""
    return s.replace("İ", "i").replace("I", "ı").lower()

# Distributif/ordinal gövde-sonu sedalılaşma: YALNIZ sayı sözcükleri için bilinen
# sedalılaşmalar. Genel ses bilgisi ({ç:c, k:ğ, p:b}) sayı gövdelerine UYGULANMAZ
# (üç→üçer, kırk→kırkar; yalnız dört→dörd- gibi t→d değişimi gerçekleşir).
# hardens() KULLANILMAZ (ek-başı sertleşmesi ölçer, gövde-sonu değil).
_VOICE_MAP: dict[str, str] = {"t": "d"}


def _voice_final(s: str) -> str:
    """Son harfi sedalılaştır; haritada yoksa değişmez (üç→üç, kırk→kırk, beş→beş)."""
    if not s:
        raise ValueError("Boş gövde")
    return s[:-1] + _VOICE_MAP.get(s[-1], s[-1])


def _split_compound(kok: str) -> tuple[str, str]:
    """Bileşik sayı köküni önek ve son token'a böl.

    Döner: (prefix, son_token) — prefix boş string veya boşlukla biten ön-parça.
    """
    parts = kok.split()
    if not parts or not parts[-1]:
        raise ValueError("Boş kök")
    if len(parts) > 1:
        return " ".join(parts[:-1]) + " ", parts[-1]
    return "", kok


def ordinal(kok: str) -> str:
    """Sayı köküne ordinal eki ekle: bir→birinci, iki→ikinci, on→onuncu.

    Bileşik sayılarda (ör. 'yirmi bir') yalnız son sözcük ek alır;
    önceki sözcükler değişmeden kalır.
    """
    kok = _tr_lower(kok.strip())
    if not kok:
        raise ValueError("Boş kök")
    prefix, kok = _split_compound(kok)
    hv = high_vowel(kok)
    if ends_in_vowel(kok):
        return prefix + kok + "nc" + hv           # iki → ikinci, altı → altıncı
    else:
        stem = _voice_final(kok)                   # dört → dörd (t→d); diğerleri değişmez
        return prefix + stem + hv + "nc" + hv      # dördüncü, birinci, onuncu


def distributive(kok: str) -> str:
    """Sayı köküne distributif eki ekle: bir→birer, iki→ikişer, dört→dörder.

    Bileşik sayılarda (ör. 'yirmi bir') yalnız son sözcük ek alır;
    önceki sözcükler değişmeden kalır.
    """
    kok = _tr_lower(kok.strip())
    if not kok:
        raise ValueError("Boş kök")
    prefix, kok = _split_compound(kok)
    lv = low_vowel(kok)
    if ends_in_vowel(kok):
        return prefix + kok + "ş" + lv + "r"  # iki → ikişer, altı → altışar
    else:
        stem = _voice_final(kok)               # dört→dörd, beş→beş, bir→bir
        return prefix + stem + lv + "r"        # dörder, beşer, birer
