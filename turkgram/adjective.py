"""adjective.py — Sıfat morfolojisi (SPEC spec/adjective-spec.md).

Saf Python, bağımlılıksız. Üretir, saklamaz.

API:
    intensify(adj)           → pekiştirme biçimi veya None
    diminutive(adj, suffix)  → küçültme biçimi veya None
"""
from __future__ import annotations

from .morphology import (
    VOWELS, BACK, ROUND, HARD_CONS,
    last_vowel, high_vowel, low_vowel, ends_in_vowel, hardens,
)

# ---------------------------------------------------------------------------
# §1.3 — Ünsüz-başlı sıfat pekiştirme ön-ek tablosu (leksik kapalı küme)
# Biçim: {sıfat: ön_ek}  — tire dahil saklanmaz, üretimde birleştirilir.
# ---------------------------------------------------------------------------
INTENSIFIER_PREFIX: dict[str, str] = {
    "beyaz":   "bem",    # bembeyaz
    "kara":    "kap",    # kapkara
    "sıcak":   "sım",    # sımsıcak
    "mavi":    "mas",    # masmavi
    "yeşil":   "yem",    # yemyeşil
    "kırmızı": "kıp",    # kıpkırmızı
    "sarı":    "sap",    # sapsarı
    "dolu":    "dop",    # dopdolu
    "temiz":   "ter",    # tertemiz
    "düz":     "düm",    # dümdüz
    "boş":     "bom",    # bomboş
    "yeni":    "yep",    # yepyeni
    "büyük":   "büs",    # büsbüyük
    "kuru":    "kup",    # kupkuru
    "sağlam":  "sap",    # sapsağlam
    "saf":     "sap",    # sapsaf
    "geniş":   "gep",    # gepgeniş
    "doğru":   "dos",    # dosdoğru
    "koca":    "kos",    # koskoca
    "yavaş":   "yap",    # yapyavaş
    "düzgün":  "düp",    # düpdüzgün
    "çıplak":  "çırıl",  # çırılçıplak (uzun önek — istisna)
    "mor":     "momp",   # ? — belirsiz; tabloya girmez
    "koyu":    "kon",    # konkoyu
}

# ---------------------------------------------------------------------------
# §1 — intensify: sıfat pekiştirmesi
# ---------------------------------------------------------------------------

def intensify(adj: str) -> str | None:
    """Sıfat pekiştirmesi (SPEC §1).

    - Ünlü-başlı sıfat → ilk_ünlü + 'p' + adj  (apaçık, upuzun, ipince)
    - Ünsüz-başlı sıfat → INTENSIFIER_PREFIX[adj] + adj  (bembeyaz, kapkara)
    - Tabloda yoksa → None

    Dönüş biçimi küçük harfli, tire yok (sımsıcak — tire varyantı kabul edilir ama
    canonical biçim tiresiz).
    """
    if not adj:
        return None
    adj = adj.strip().lower()

    # Ünlü-başlı: algoritmik kural
    if adj[0] in VOWELS:
        return adj[0] + "p" + adj

    # Ünsüz-başlı: kapalı tablo
    prefix = INTENSIFIER_PREFIX.get(adj)
    if prefix is None:
        return None
    return prefix + adj


# ---------------------------------------------------------------------------
# §2 — diminutive: küçültme ekleri
# ---------------------------------------------------------------------------

_VALID_SUFFIXES = frozenset({"-CIk", "-ImsI", "-ImtIrak"})


def diminutive(adj: str, suffix: str = "-CIk") -> str | None:
    """Küçültme eki uygula (SPEC §2).

    suffix: '-CIk' | '-ImsI' | '-ImtIrak'
    Dönüş: küçültülmüş biçim veya None (geçersiz ek).
    """
    if suffix not in _VALID_SUFFIXES:
        raise ValueError(f"Geçersiz küçültme eki: {suffix!r}. "
                         f"Seçenekler: {sorted(_VALID_SUFFIXES)}")
    if not adj:
        return None
    adj = adj.strip().lower()

    if suffix == "-CIk":
        return _diminutive_cik(adj)
    elif suffix == "-ImsI":
        return _diminutive_imsi(adj)
    else:  # -ImtIrak
        return _diminutive_imtirak(adj)


def _diminutive_cik(adj: str) -> str:
    """§2.1 — -CIk küçültme eki.

    Kural:
    - Ünlü-final kök: + cık/cuk/cik/cük (C sertleşme, I harmoni)
    - k-final kök: k düşer → + cık/cük vb.  (küçük→küçücük, ufak→ufacık)
    - Diğer ünsüz-final: direkt + çık/çuk/cık vb. (buffer ünlü YOK)
      (yavaş→yavaşçık, dar→daracık, uzun→uzuncuk, az→azıcık)

    TUZAK: 'az' ve 'dar' buffer alıyor gibi görünse de bu sadece harmoni yansıması
    değil; gerçek kural direkt ektir, 'a' ve 'ı' sıfatın son ünlüsünden geliyor.
    Düzeltme: buffer yoktur; son ünlüden harmoni hesaplanır → C+I+k direkt eklenir.
    """
    c = "ç" if hardens(adj) else "c"
    i = high_vowel(adj)

    if ends_in_vowel(adj):
        # ünlü-final: direkt CIk
        return adj + c + i + "k"
    elif adj.endswith("k"):
        # k-final: k düşer, CIk eklenir (küçük→küçücük, ufak→ufacık)
        stem = adj[:-1]
        # harmoni kalan gövdeden hesaplanır
        c2 = "ç" if hardens(stem) else "c"
        i2 = high_vowel(stem)
        return stem + c2 + i2 + "k"
    else:
        # diğer ünsüz-final: direkt CIk (buffer yok)
        return adj + c + i + "k"


def _diminutive_imsi(adj: str) -> str:
    """§2.2 — -ImsI küçültme eki ('-ish', benzerlik).

    - Ünsüz-final: + ImsI  (yeşil → yeşilimsi, beyaz → beyazımsı)
    - Ünlü-final:  + msI   (kara → karamsı, sarı → sarımsı, mavi → mavimsi)
      kaynaştırma: son ünlü kalır, m + harmoni-I
    """
    if ends_in_vowel(adj):
        # ünlü-final: son ünlüden harmoni, m + sI
        i = high_vowel(adj)
        return adj + "m" + "s" + i
    else:
        # ünsüz-final: I (buffer, harmoni) + msI
        i = high_vowel(adj)
        return adj + i + "ms" + i


def _diminutive_imtirak(adj: str) -> str:
    """§2.3 — -ImtIrak küçültme eki (daha güçlü benzerlik).

    'tırak' / 'tirak' kısmı: arka-ünlülü kök → tırak, ön-ünlülü kök → tirak.
    - Ünsüz-final: + ImtIrak  (yeşil → yeşilimtırak, beyaz → beyazımtırak)
    - Ünlü-final:  + mtIrak   (sarı → sarımtırak, kara → karamtırak)
    """
    lv = last_vowel(adj)
    # tIrak kısmı: ı (arka/düz) veya i (ön/düz)
    t_vowel = "ı" if lv in BACK else "i"

    if ends_in_vowel(adj):
        # ünlü-final: + mtIrak
        i = high_vowel(adj)  # Im kısmının I'sı (harmoni)
        return adj + "mt" + t_vowel + "rak"
    else:
        # ünsüz-final: + ImtIrak
        i = high_vowel(adj)
        return adj + i + "mt" + t_vowel + "rak"



# ---------------------------------------------------------------------------
# Public API özeti
# ---------------------------------------------------------------------------
__all__ = ["intensify", "diminutive", "INTENSIFIER_PREFIX"]
