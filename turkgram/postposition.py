"""postposition.py — Türkçe edat/ilgeç yönetimi (Faz 5 D2)."""
from __future__ import annotations

from .morphology_noun import decline

# için özel durum: kişi zamirleri + n-gövde zamirleri genitif (benim için),
# düz isimler yalın (ev için). onlar→nom (onlar için, onların için değil).
_ICIN_GEN_PRONOUNS: frozenset[str] = frozenset({
    "ben", "sen", "o", "biz", "siz", "bu", "şu",
    "hepsi", "kendi", "kendisi", "hiçbiri", "birisi", "biri",
    "öteki", "öbürü", "hangisi", "bazısı", "çoğu", "azı",
})

_POSTPOSITION_CASE: dict[str, str] = {
    "için":     "nom",   # isimler yalın; zamir → _ICIN_GEN_PRONOUNS (gen)
    "ile":      "nom",   # ayrı; bitişik=True ise ins
    "göre":     "dat",
    "kadar":    "dat",
    "karşı":    "dat",
    "rağmen":   "dat",
    "doğru":    "dat",
    "dek":      "dat",
    "değin":    "dat",
    "üzere":    "nom",   # bu şart üzere; fiil-mastar tümleci sözdizimsel, kapsam dışı
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
        'ev için'
        >>> postposition('ben', 'için')
        'benim için'
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
    # için: kişi/n-gövde zamirleri genitif, düz isimler yalın
    if edat == "için":
        case = "gen" if lemma.lower() in _ICIN_GEN_PRONOUNS else "nom"
    else:
        case = _POSTPOSITION_CASE[edat]
    declined = decline(lemma, case=case)
    return declined + " " + edat
