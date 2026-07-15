"""postposition.py — Türkçe edat/ilgeç yönetimi (Faz 5 D2)."""
from __future__ import annotations

from .morphology_noun import decline

_POSTPOSITION_CASE: dict[str, str] = {
    "için":     "gen",
    "ile":      "nom",   # ayrı; bitişik=True ise ins
    "göre":     "dat",
    "kadar":    "dat",
    "karşı":    "dat",
    "rağmen":   "dat",
    "doğru":    "dat",
    "dek":      "dat",
    "değin":    "dat",
    "üzere":    "dat",
    "önce":     "abl",
    "sonra":    "abl",
    "beri":     "abl",
    "itibaren": "abl",
    "başka":    "abl",
    "dolayı":   "abl",
    "ötürü":    "abl",
    "gibi":     "nom",   # yalın; bitişik yolu yok
    "aşkın":    "acc",
}


def postposition(lemma: str, edat: str, bitişik: bool = False) -> str:
    """İsim lemması + edat → tam edat öbeği.

    Args:
        lemma:   İsim lemması (yalın biçim).
        edat:    Edat (ör. 'için', 'ile', 'göre').
        bitişik: True yalnız 'ile' için: decline(lemma, case='ins') döndürür.

    Returns:
        Tam edat öbeği dizesi.

    Raises:
        ValueError: Boş lemma, bilinmeyen edat veya bitişik=True iken edat != 'ile'.

    Examples:
        >>> postposition('ev', 'için')
        'evin için'
        >>> postposition('ev', 'ile')
        'ev ile'
        >>> postposition('ev', 'ile', bitişik=True)
        'evle'
        >>> postposition('araba', 'göre')
        'arabaya göre'
    """
    if not lemma or not lemma.strip():
        raise ValueError("lemma boş olamaz.")
    if edat not in _POSTPOSITION_CASE:
        raise ValueError(
            f"Bilinmeyen edat: {edat!r}. Geçerliler: {sorted(_POSTPOSITION_CASE)}"
        )
    if bitişik and edat != "ile":
        raise ValueError(
            f"bitişik=True yalnız 'ile' için geçerlidir, {edat!r} değil."
        )
    if bitişik:
        return decline(lemma, case="ins")
    case = _POSTPOSITION_CASE[edat]
    declined = decline(lemma, case=case)
    return declined + " " + edat
