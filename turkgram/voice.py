"""Çatı (voice) morfotaktik katmanı — voice-spec.md (Faz 1 / A1).

Delegasyon deseni (aspect/copula emsali, CLAUDE.md #6): çatı zincirini köke sırayla
uygular, türetilmiş gövdeyi `VerbStem`'e sarar; oluşan gövde NORMAL çekilir (k→ğ,
aorist -Ir, -Iyor ünlü düşmesi vs. `morphology._conjugate_core`'dan gelir — sıfır ek
çekim morfolojisi). Motor biçimi ÜRETİR, SAKLAMAZ (#5).

Çatılı gövde daima çok-heceli + ünsüz-final → aorist otomatik -Ir (hece sayımı),
softens/ye_de bayrakları düşer (yalnız zincirin İLK ekinde, orijinal köke devrede).
"""
from __future__ import annotations

from collections.abc import Sequence

from .morphology import (
    VerbStem,
    VOWELS,
    BACK,
    last_vowel,
    high_vowel,
    low_vowel,
    ends_in_vowel,
    hardens,
    _stem_before_suffix,
)

# Çekirdek çatı etiketleri (İngilizce); tr.py ettirgen/edilgen/dönüşlü/işteş → bunlar.
VOICES = ("caus", "pass", "refl", "recip")

# Ettirgen leksik istisnalar (SPEC §3.1) — YALNIZ orijinal köke (ilk ek). Fonolojiyle
# öngörülemez; değer allomorf sınıfı ('Ir'/'Ar'/'It'), harmoni köke göre çözülür.
CAUSATIVE_LEXICAL: dict[str, str] = {
    # -(I)r/-(U)r  (§498.3, tek-heceli ç/ş/t/… sonrası)
    "aş": "Ir", "düş": "Ir", "geç": "Ir", "göç": "Ir", "iç": "Ir",
    "kaç": "Ir", "piş": "Ir", "şiş": "Ir", "yat": "Ir", "uç": "Ir", "doy": "Ir",
    # -Ar/-Er  (§498, leksik)
    "çık": "Ar", "kop": "Ar", "on": "Ar",
    # -(I)t/-(U)t  (§498.1, seyrek tek-heceli k/p/ç/m sonrası)
    "kork": "It", "ürk": "It", "ak": "It", "kok": "It", "sark": "It", "sap": "It",
}


def _syllables(word: str) -> int:
    return sum(1 for ch in word if ch in VOWELS)


# ---------------------------------------------------------------------------
# Tekil çatı ekleri — `stem` = güncel gövde (str); `vs` YALNIZ ilk ekte (orijinal
# kök, softens/ye_de için), sonraki adımlarda None.
# ---------------------------------------------------------------------------
def _causative(stem: str, vs: VerbStem | None) -> str:
    """Ettirgen (SPEC §3). Allomorf: leksik -Ir/-Ar/-It, çok-heceli ünlü/-l/-r → -t,
    diğer → -DIr. Ettirgen ekleri ünsüz-başlı (-DIr/-t) ya da leksik non-softening
    köke gelir → yumuşama/ye_de tetiklenmez (vs kullanılmaz)."""
    if vs is not None and vs.root in CAUSATIVE_LEXICAL:
        typ = CAUSATIVE_LEXICAL[vs.root]
        if typ == "Ir":
            return stem + high_vowel(stem) + "r"     # piş→pişir, düş→düşür
        if typ == "Ar":
            return stem + low_vowel(stem) + "r"      # çık→çıkar, kop→kopar
        return stem + high_vowel(stem) + "t"         # kork→korkut, ak→akıt
    poly = _syllables(stem) >= 2
    if poly and (ends_in_vowel(stem) or stem[-1] in "lr"):
        return stem + "t"                            # oku→okut, otur→oturt, azal→azalt
    d = "t" if hardens(stem) else "d"                # -DIr (sertleşme + 4'lü)
    return stem + d + high_vowel(stem) + "r"         # yap→yaptır, gör→gördür, de→dedir


def _passive(stem: str, vs: VerbStem | None) -> str:
    """Edilgen (SPEC §4). Ünlü-final → -n (ünsüz-başlı: ye_de tetiklemez, de→den);
    -l final → -In; diğer → -Il (-Il/-In ünlü-başlı: yumuşama, git→gidil)."""
    raw = vs.root if vs is not None else stem
    if ends_in_vowel(raw):
        return raw + "n"                             # oku→okun, ara→aran, de→den
    base = _stem_before_suffix(vs, True) if vs is not None else stem
    if raw[-1] == "l":
        return base + high_vowel(base) + "n"         # bil→bilin, al→alın
    return base + high_vowel(base) + "l"             # yap→yapıl, gör→görül, git→gidil


def _reflexive(stem: str, vs: VerbStem | None) -> str:
    """Dönüşlü (SPEC §5). Ünlü-final → -n; ünsüz-final → -In (l-özel dalı YOK)."""
    raw = vs.root if vs is not None else stem
    if ends_in_vowel(raw):
        return raw + "n"                             # yıka→yıkan, tara→taran
    base = _stem_before_suffix(vs, True) if vs is not None else stem
    return base + high_vowel(base) + "n"             # giy→giyin, döv→dövün, sev→sevin


def _reciprocal(stem: str, vs: VerbStem | None) -> str:
    """İşteş (SPEC §6). Ünlü-final → -ş; ünsüz-final → -Iş."""
    raw = vs.root if vs is not None else stem
    if ends_in_vowel(raw):
        return raw + "ş"                             # ağla→ağlaş
    base = _stem_before_suffix(vs, True) if vs is not None else stem
    return base + high_vowel(base) + "ş"             # döv→dövüş, bak→bakış, gör→görüş


_APPLY = {
    "caus": _causative,
    "pass": _passive,
    "refl": _reflexive,
    "recip": _reciprocal,
}


def apply_voice(vs: VerbStem, chain: Sequence[str]) -> VerbStem:
    """Çatı zincirini `vs`'e sırayla uygula → çatılı `VerbStem` (root = çatılı gövde).

    `chain` boş/None → `vs` değişmeden döner. Her adım güncel gövdenin son sesine
    bakar (SPEC §7 yığılma). Bilinmeyen etiket → ValueError.
    """
    if not chain:
        return vs
    for v in chain:
        if v not in _APPLY:
            raise ValueError(
                f"bilinmeyen çatı (voice): {v!r}; geçerli: {', '.join(VOICES)}")
    stem = vs.root
    for idx, v in enumerate(chain):
        stem = _APPLY[v](stem, vs if idx == 0 else None)
    suffix = "mak" if last_vowel(stem) in BACK else "mek"  # arka-ünlü → -mak
    return VerbStem(
        lemma=stem + suffix, prefix=vs.prefix, root=stem,
        aorist_ir=False,        # çok-heceli → -Ir zaten hece sayımından gelir
        softens=False, special=None,
    )
