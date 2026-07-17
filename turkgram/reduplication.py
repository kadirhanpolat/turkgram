"""reduplication.py — Türkçe ikileme üretimi (Faz 9d).

Üç tür:
  full_reduplicate  : yavaş → yavaş yavaş
  converb_reduplicate: koşmak → koşa koşa   (-A ulacı × 2)
  m_reduplicate     : kitap → kitap mitap   (ilk C→m)
"""
from __future__ import annotations

from .morphology import _stem_before_suffix, ends_in_vowel, low_vowel, parse_verb

__all__ = ["full_reduplicate", "converb_reduplicate", "m_reduplicate"]

_VOWELS: frozenset[str] = frozenset("aeıioöuüâîû")


def full_reduplicate(word: str) -> str:
    """Sözcüğü kendisiyle tekrarla: yavaş → yavaş yavaş."""
    if not word:
        raise ValueError("Boş sözcük")
    return word + " " + word


def _a_converb(lemma: str) -> str:
    """-A zarf-fiil biçimini üret: koşmak→koşa, gülmek→güle, gitmek→gide."""
    vs = parse_verb(lemma)
    stem = _stem_before_suffix(vs, True)   # yumuşamalı (git→gid, ye→yi)
    y = "y" if ends_in_vowel(stem) else ""
    a = low_vowel(stem)
    return stem + y + a


def converb_reduplicate(lemma: str) -> str:
    """-A ulaç biçimini ikile: koşmak → koşa koşa.

    Parameters
    ----------
    lemma:
        Fiil mastarı (-mAk biçimi). Mastar olmayan girdi ValueError fırlatır.
    """
    if not lemma:
        raise ValueError("Boş sözcük")
    form = _a_converb(lemma)
    return form + " " + form


def m_reduplicate(word: str) -> str:
    """İlk ünsüzü m ile değiştir: kitap → kitap mitap.

    Ünlü-başlı sözcüklerde başa m eklenir: araba → araba maraba.
    m-başlı sözcükler için ValueError fırlatılır (p-ikileme kapsam dışı).
    """
    if not word:
        raise ValueError("Boş sözcük")
    if word[0] == "m":
        raise ValueError(
            f"m-başlı sözcüğe m-ikileme uygulanamaz: {word!r}"
        )
    if word[0] in _VOWELS:
        m_form = "m" + word
    else:
        m_form = "m" + word[1:]
    return word + " " + m_form
