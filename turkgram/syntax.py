"""syntax.py — Sözdizimi katmanı: öbek üretimi (Faz 4).

Mevcut morfoloji üretici (decline/conjugate) üzerinde çalışır; içlerine dokunmaz.
Saf Python, bağımlılıksız.

API:
    isim_tamlamasi(tamlayan, tamlanan, tur)   → belirtili/belirtisiz isim tamlaması
    sifat_tamlamasi(sifat, isim)              → sıfat + isim (basit öbek)
    cumle_uret(ozne, yuklem_lemma, ...)       → özne-yüklem cümlesi

Referans: Korkmaz §200-230 (Tamlama); §265 (Sıfat tamlaması); §295 (Cümle).
"""
from __future__ import annotations

from .morphology_noun import decline

# ---------------------------------------------------------------------------
# §1 — İsim tamlaması
# ---------------------------------------------------------------------------

def isim_tamlamasi(
    tamlayan: str,
    tamlanan: str,
    *,
    tur: str = "belirtili",
) -> str:
    """İsim tamlaması üret (Korkmaz §200-210).

    Args:
        tamlayan: Tamlayan isim (lemma — sözlük biçimi).
        tamlanan: Tamlanan isim (lemma — sözlük biçimi).
        tur: 'belirtili' | 'belirtisiz'

    Belirtili (takısız belirtili tamlama):
        tamlayan → tamlayan + GEN (-ın/-in/-un/-ün/-nın/-nin/…)
        tamlanan → tamlanan + 3sg-POSS (-ı/-i/-u/-ü/-sı/-si/…)
        Örnek: isim_tamlamasi('ev', 'kapı') → 'evin kapısı'

    Belirtisiz (sıfat-benzeri, iyeliksiz tamlanan):
        tamlayan → bare (ek yok)
        tamlanan → tamlanan + 3sg-POSS
        Örnek: isim_tamlamasi('taş', 'köprü', tur='belirtisiz') → 'taş köprüsü'

        NOT: Türkçede gerçek belirtisiz tamlama 3sg-poss ALIR (taş köprüsü),
        ekten yoksun sıfat tamlaması DEĞİLDİR (demir kapı = sıfat tamlaması, bu farklı).

    Returns:
        str — tamlama biçimi (boşlukla ayrılmış iki token).

    Raises:
        ValueError: Bilinmeyen tür.
    """
    tur = tur.lower().strip()
    if tur not in ("belirtili", "belirtisiz"):
        raise ValueError(
            f"Bilinmeyen tamlama türü: {tur!r}. Geçerli: 'belirtili', 'belirtisiz'"
        )

    # Tamlanan: her iki türde de 3sg-iyelik alır
    tamlanan_form = decline(tamlanan, possessive="3sg")

    if tur == "belirtili":
        # Tamlayan: tamlayan durumu (gen = ilgi durumu)
        tamlayan_form = decline(tamlayan, case="gen")
    else:
        # Belirtisiz: tamlayan çekimsiz (yalın)
        tamlayan_form = tamlayan.lower().strip()

    return f"{tamlayan_form} {tamlanan_form}"


# ---------------------------------------------------------------------------
# §2 — Sıfat tamlaması
# ---------------------------------------------------------------------------

def sifat_tamlamasi(sifat: str, isim: str) -> str:
    """Sıfat tamlaması üret (Korkmaz §265).

    Türkçede sıfat tamlamasında sıfat çekimsiz, isim yalın:
        kırmızı + araba → 'kırmızı araba'
        büyük  + ev    → 'büyük ev'
        eski   + kitap → 'eski kitap'

    Kongruans (uyum) YOK — sıfat değişmez.

    Args:
        sifat: Sıfat (değişmez, sözlük biçimi).
        isim:  Başlıca isim (yalın, lemma).

    Returns:
        str — 'sıfat isim' (boşlukla).
    """
    return f"{sifat.lower().strip()} {isim.lower().strip()}"


# ---------------------------------------------------------------------------
# §3 — Cümle üretimi: özne + yüklem uyumu
# ---------------------------------------------------------------------------

def cumle_uret(
    ozne: str,
    yuklem_lemma: str,
    *,
    kip: str = "pres",
    olumsuz: bool = False,
    soru: bool = False,
    ozne_sayi: str = "sg",
    ozne_sahis: str | None = None,
) -> str:
    """Basit özne-yüklem cümlesi üret (Korkmaz §295-310).

    Türkçede yüklem kişiye göre çekilir; özne adılları genellikle düşer
    (pro-drop dil). Bu fonksiyon özne + yüklem üretir.

    Args:
        ozne:         Özne (lemma — isim veya kişi zamiri).
        yuklem_lemma: Yüklem fiil mastarı ('gitmek', 'okumak'…).
        kip:          Fiil kipi (conjugate API): 'pres'|'past'|'fut'|'aorist'|…
        olumsuz:      Olumsuz çekim (değil).
        soru:         Soru çekimi (mI).
        ozne_sayi:    'sg' | 'pl'.
        ozne_sahis:   '1'|'2'|'3' (belirtilmezse özne adına göre belirlenir).

    Returns:
        str — 'özne yüklem' (boşlukla); pro-drop mümkün ama burada özne yazılır.

    Örnek:
        cumle_uret('ben', 'gelmek') → 'ben geliyorum'
        cumle_uret('öğrenci', 'okumak', kip='past') → 'öğrenci okudu'
        cumle_uret('onlar', 'gitmek', kip='fut') → 'onlar gidecekler'
    """
    from .morphology import conjugate

    # Özne → kişi-sayı belirleme
    person = _ozne_to_person(ozne, ozne_sahis, ozne_sayi)

    yuklem_form = conjugate(
        yuklem_lemma, kip, person,
        negative=olumsuz,
        question=soru,
    )
    ozne_str = ozne.lower().strip()
    return f"{ozne_str} {yuklem_form}"


# ---------------------------------------------------------------------------
# Yardımcı: özne → kişi-sayı tahmini
# ---------------------------------------------------------------------------

# Kişi zamirleri tablosu
_SAHIS_MAP: dict[str, str] = {
    "ben":   "1sg",
    "sen":   "2sg",
    "o":     "3sg",
    "biz":   "1pl",
    "siz":   "2pl",
    "onlar": "3pl",
    # Soru zamiri — 3sg varsayılan
    "kim":   "3sg",
    "ne":    "3sg",
}


def _ozne_to_person(ozne: str, sahis: str | None, sayi: str) -> str:
    """Özne + sahis + sayi → kişi kodu ('1sg', '3pl', …).

    Önce _SAHIS_MAP'e bak; bulunamazsa sahis+sayi birleştir;
    sahis belirtilmemişse 3sg varsayılan (isim özneler 3. kişi).
    """
    ozne_lower = ozne.lower().strip()
    if ozne_lower in _SAHIS_MAP:
        return _SAHIS_MAP[ozne_lower]
    if sahis is not None:
        return f"{sahis}{sayi}"
    # İsim özne → 3. kişi
    return f"3{sayi}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
__all__ = [
    "isim_tamlamasi",
    "sifat_tamlamasi",
    "cumle_uret",
]
