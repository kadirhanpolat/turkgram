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

# Tek doğruluk kaynağı — üretim + analiz + K2 (context._POSTP_GOV) buradan beslenir.
# yönet KÜMESİ elle yazılır (üret'ten TÜRETİLMEZ): zamir çok-case edatları korunur.
_POSTPOSITIONS: dict[str, dict] = {
    "için":     {"üret": "nom", "üret_zamir": "gen", "yönet": frozenset({"nom", "gen"}),        "üretilebilir": True},
    "ile":      {"üret": "nom",                       "yönet": frozenset({"nom", "gen"}),        "üretilebilir": True},
    "gibi":     {"üret": "nom",                       "yönet": frozenset({"nom", "gen"}),        "üretilebilir": True},
    "kadar":    {"üret": "dat",                       "yönet": frozenset({"nom", "gen", "dat"}), "üretilebilir": True},
    "göre":     {"üret": "dat",                       "yönet": frozenset({"dat"}),               "üretilebilir": True},
    "karşı":    {"üret": "dat",                       "yönet": frozenset({"dat"}),               "üretilebilir": True},
    "rağmen":   {"üret": "dat",                       "yönet": frozenset({"dat"}),               "üretilebilir": True},
    "doğru":    {"üret": "dat",                       "yönet": frozenset({"dat"}),               "üretilebilir": True},
    "dek":      {"üret": "dat",                       "yönet": frozenset({"dat"}),               "üretilebilir": True},
    "değin":    {"üret": "dat",                       "yönet": frozenset({"dat"}),               "üretilebilir": True},
    "üzere":    {"üret": "nom",                       "yönet": frozenset({"nom"}),               "üretilebilir": True},
    "önce":     {"üret": "abl",                       "yönet": frozenset({"abl"}),               "üretilebilir": True},
    "sonra":    {"üret": "abl",                       "yönet": frozenset({"abl"}),               "üretilebilir": True},
    "beri":     {"üret": "abl",                       "yönet": frozenset({"abl"}),               "üretilebilir": True},
    "itibaren": {"üret": "abl",                       "yönet": frozenset({"abl"}),               "üretilebilir": True},
    "başka":    {"üret": "abl",                       "yönet": frozenset({"abl"}),               "üretilebilir": True},
    "dolayı":   {"üret": "abl",                       "yönet": frozenset({"abl"}),               "üretilebilir": True},
    "ötürü":    {"üret": "abl",                       "yönet": frozenset({"abl"}),               "üretilebilir": True},
    "aşkın":    {"üret": "acc",                       "yönet": frozenset({"acc"}),               "üretilebilir": True},
    "dair":     {"yönet": frozenset({"dat"}), "üretilebilir": False},
    "ilişkin":  {"yönet": frozenset({"dat"}), "üretilebilir": False},
    "ait":      {"yönet": frozenset({"dat"}), "üretilebilir": False},
    "yana":     {"yönet": frozenset({"abl"}), "üretilebilir": False},
}

# Geriye uyum görünümü — eski _POSTPOSITION_CASE importları yalnız üretilebilir üret-case bekler.
_POSTPOSITION_CASE: dict[str, str] = {
    e: v["üret"] for e, v in _POSTPOSITIONS.items() if v["üretilebilir"]
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
    if edat not in _POSTPOSITIONS:
        producible = sorted(e for e, v in _POSTPOSITIONS.items() if v["üretilebilir"])
        raise ValueError(f"Bilinmeyen edat: {edat!r}. Geçerliler: {producible}")
    if not _POSTPOSITIONS[edat]["üretilebilir"]:
        raise ValueError(
            f"{edat!r} donmuş bir edat (donmuş kalıp), postposition() üretmez."
        )
    if bitişik and edat != "ile":
        raise ValueError(
            f"bitişik=True yalnız 'ile' için geçerlidir, {edat!r} değil."
        )
    if bitişik:
        return decline(lemma, case="ins")
    entry = _POSTPOSITIONS[edat]
    if edat == "için" and lemma.lower() in _ICIN_GEN_PRONOUNS:
        case = entry["üret_zamir"]
    else:
        case = entry["üret"]
    declined = decline(lemma, case=case)
    return declined + " " + edat
