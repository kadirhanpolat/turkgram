"""turkgram.spellcheck — Türkçe yazım denetimi (Faz 9b).

is_valid() → analyze() + lexicon.load() ile morfolojik geçerlilik.
suggest()  → BK-tree + Türkçe-ağırlıklı Levenshtein (sonraki görevde).
check()    → SpellResult (is_valid + suggestions).

NOT: roots=None burada lexicon.load()'u otomatik yükler (analyze(roots=None)'den farklı).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .analysis import analyze as _analyze
from . import lexicon as _lexicon

_MAX_WORD_LEN = 200

# Türkçe karakter konfüzyon çiftleri: her çift 0.5 maliyet taşır.
_TR_CONFUSIONS: dict[str, str] = {
    "ı": "i", "i": "ı",
    "ö": "o", "o": "ö",
    "ü": "u", "u": "ü",
    "ş": "s", "s": "ş",
    "ç": "c", "c": "ç",
    "ğ": "g", "g": "ğ",
}


def _tr_lower(s: str) -> str:
    return s.replace("İ", "i").replace("I", "ı").lower()


def _roots(roots: frozenset[str] | None) -> frozenset[str]:
    """roots=None → leksikonu otomatik yükle (is_valid/suggest için zorunlu)."""
    return roots if roots is not None else _lexicon.load()


@dataclass(frozen=True)
class SpellResult:
    """Yazım denetimi sonucu.

    suggestions: is_valid=True ise her zaman boş tuple; immutable (frozen uyum).
    word: çağıranın orijinal girdisi (normalize edilmemiş olabilir).
    """
    word: str
    is_valid: bool
    suggestions: tuple[str, ...]


def is_valid(word: str, *, roots: frozenset[str] | None = None) -> bool:
    """Kelimenin morfolojik olarak geçerli Türkçe olup olmadığını döner."""
    word = _tr_lower(word.strip())
    if not word or len(word) > _MAX_WORD_LEN:
        return False
    r = _roots(roots)
    return any(not a.hypothetical for a in _analyze(word, roots=r))


# suggest() ve check() bir sonraki görevde eklenecek — placeholder yok.
