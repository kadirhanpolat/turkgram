"""turkgram.compound — Bileşik (birleşik) zaman çekimi (Faz 2b / motor-dışı biçim 3).

Basit zaman finit tabanı + ek-fiil (hikaye -DI / rivayet -mIş / şart -sA) + kişi.
Taban motorun `conjugate` çıktısından AYNEN alınır; ek-fiil mevcut `_copula_suffix`
desenine delege edilir (sıfır yeni morfofonoloji). SPEC: spec/compound-tense-spec.md.

KRİTİK DEĞİŞMEZ (3pl yerleşimi): çoğul -lAr TABANA biner, ek-fiil 3sg olur →
`geliyorlardı` (geliyordular DEĞİL), `gelirlermiş`, `geleceklerdi`.

    >>> compound("gelmek", "pres", "hikaye", "3sg")   # geliyordu
    >>> compound("gelmek", "pres", "hikaye", "3pl")   # geliyorlardı
    >>> compound("gelmek", "aorist", "rivayet", "3pl")  # gelirlermiş
"""
from __future__ import annotations

from .morphology import PERSONS, conjugate
from .morphology_noun import _copula_suffix

# Ek-fiil binen basit tabanlar (basit -DI geçmişi hariç: ağızsal).
COMPOUND_BASES = ("pres", "aorist", "fut", "evid")
# Ek-fiiller (birleşik çekim kipleri).
COMPOUND_COPULAS = ("hikaye", "rivayet", "sart")


def compound(lemma: str, base: str, copula: str, person: str = "3sg", *,
             negative: bool = False) -> str:
    """Bileşik zaman: basit taban + ek-fiil + kişi. base ∈ COMPOUND_BASES,
    copula ∈ COMPOUND_COPULAS, person ∈ PERSONS."""
    if base not in COMPOUND_BASES:
        raise ValueError(
            f"bilinmeyen bileşik taban: {base!r}. Geçerli: {', '.join(COMPOUND_BASES)}"
        )
    if copula not in COMPOUND_COPULAS:
        raise ValueError(
            f"bilinmeyen ek-fiil: {copula!r}. Geçerli: {', '.join(COMPOUND_COPULAS)}"
        )
    if person not in PERSONS:
        raise ValueError(f"bilinmeyen person: {person!r}")

    if person == "3pl":
        # 3pl: çoğul tabana biner (geliyorlar), ek-fiil 3sg → geliyorlardı
        stem = conjugate(lemma, base, "3pl", negative=negative)
        return _copula_suffix(stem, copula, "3sg")
    # diğer kişiler: 3sg taban (geliyor), ek-fiil o kişiyle
    stem = conjugate(lemma, base, "3sg", negative=negative)
    return _copula_suffix(stem, copula, person)
