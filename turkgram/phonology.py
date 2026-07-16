"""IPA transkripsiyon — karakter düzeyinde, kapsam: harf eşleme + ğ/k/l bağlam."""
from __future__ import annotations

_FRONT_VOWELS = set("eiöü")
_BACK_VOWELS  = set("aıou")
_ALL_VOWELS   = _FRONT_VOWELS | _BACK_VOWELS

_BASE: dict[str, str] = {
    "a": "a",  "b": "b",  "c": "dʒ", "ç": "tʃ",
    "d": "d",  "e": "e",  "f": "f",  "g": "ɡ",
    "h": "h",  "ı": "ɯ",  "i": "i",  "j": "ʒ",
    "k": "k",  "l": "l",  "m": "m",  "n": "n",
    "o": "o",  "ö": "ø",  "p": "p",  "r": "ɾ",
    "s": "s",  "ş": "ʃ",  "t": "t",  "u": "u",
    "ü": "y",  "v": "v",  "y": "j",  "z": "z",
}


def ipa_table() -> dict[str, str]:
    """Türkçe harf → IPA sembol tablosu (bağlam-bağımsız temel eşleme)."""
    return dict(_BASE)


def _neighbor_vowel(chars: list[str], idx: int) -> "str | None":
    """Sol-komşu ünlü, yoksa sağ-komşu ünlü, yoksa None."""
    for i in range(idx - 1, -1, -1):
        if chars[i] in _ALL_VOWELS:
            return chars[i]
    for i in range(idx + 1, len(chars)):
        if chars[i] in _ALL_VOWELS:
            return chars[i]
    return None


def to_ipa(text: str) -> str:
    """Türkçe metin → IPA transkripsiyon dizesi."""
    chars = list(text.lower())
    result: list[str] = []
    i = 0
    while i < len(chars):
        ch = chars[i]

        # ğ: kelime-ortası (sonraki char var ve boşluk değil) → önceki ünlüyü uzat
        # kelime-sonu veya söylem-sonu: sessiz atlanır
        if ch == "ğ":
            prev_vowel = i > 0 and chars[i - 1] in _ALL_VOWELS
            not_word_final = i < len(chars) - 1 and chars[i + 1] not in (" ", "\t", "\n")
            if prev_vowel and not_word_final:
                result.append("ː")
            i += 1
            continue

        # k: bağlam-duyarlı (ön-ünlü → /c/, art-ünlü veya bağımsız → /k/)
        if ch == "k":
            neighbor = _neighbor_vowel(chars, i)
            result.append("c" if neighbor in _FRONT_VOWELS else "k")
            i += 1
            continue

        # l: bağlam-duyarlı (art-ünlü → /ɫ/, ön-ünlü veya bağımsız → /l/)
        if ch == "l":
            neighbor = _neighbor_vowel(chars, i)
            result.append("ɫ" if neighbor in _BACK_VOWELS else "l")
            i += 1
            continue

        if ch in _BASE:
            result.append(_BASE[ch])
        else:
            result.append(ch)  # bilinmeyen (boşluk, noktalama) aynen
        i += 1

    return "".join(result)
