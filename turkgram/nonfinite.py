"""turkgram.nonfinite — Fiilimsi üretimi (Faz 1 / A5: zarf-fiil / ulaç).

Kişisiz zarf-fiil (ulaç) biçimlerini ÜRETİR. Morfofonoloji motorun çekim üretimiyle
BİREBİR tutarlıdır: kök varyantı `morphology._stem_before_suffix` (yumuşama git→gid,
ye_de ye→yi yalnız ünlü-başlı ekte) + kaynaştırma -y-. SPEC: spec/nonfinite-spec.md.

A5 yalnız KÖK-EKLENEN ulaçları üretir. `-ken`/`-cAsInA` (çekimli gövde üstüne binen) ve
`-DIğIndA` (sıfat-fiil + durum) A5 DIŞI (A3/copula).

    >>> converb("gitmek", "arak")     # giderek  (yumuşama)
    >>> converb("gitmek", "madan")    # gitmeden (yumuşama YOK — ünsüz-başlı)
    >>> converb("yemek", "arak")      # yiyerek  (ye_de)
    >>> converb("okumak", "eli")      # okuyalı  (yüksek-düz)
"""
from __future__ import annotations

from .morphology import (
    parse_verb, _stem_before_suffix, conjugate,
    low_vowel, high_vowel, ends_in_vowel, hardens,
)
from .morphology_noun import decline

# Ünlü-başlı ulaçlar (yumuşama/ye_de tetikler); ünsüz-başlılar aşağıda.
_VOWEL_INITIAL = frozenset({"arak", "ip", "inca", "eli", "esiye"})
_CONSONANT_INITIAL = frozenset({"madan", "dikce", "meksizin"})
CONVERBS = _VOWEL_INITIAL | _CONSONANT_INITIAL

# Biçim-eklenen ulaçlar (finit taban üstüne biner; A5 kök-eklenenlerden ayrı).
_CASINA_BASES = frozenset({"aorist", "evid"})       # -cAsInA: geniş / -mIş tabanı
_KEN_BASES = frozenset({"aorist", "pres", "evid", "fut"})  # -ken: dört basit taban


def converb(lemma: str, kind: str) -> str:
    """Fiilden zarf-fiil (ulaç) üret. kind ∈ CONVERBS."""
    if kind not in CONVERBS:
        raise ValueError(
            f"bilinmeyen ulaç: {kind!r}. Geçerli: {', '.join(sorted(CONVERBS))}"
        )
    vs = parse_verb(lemma)

    if kind in _VOWEL_INITIAL:
        stem = _stem_before_suffix(vs, True)        # yumuşamalı (git→gid, ye→yi)
        y = "y" if ends_in_vowel(stem) else ""
        a = low_vowel(stem)
        if kind == "arak":                          # -ArAk
            return stem + y + a + "r" + a + "k"
        if kind == "ip":                            # -Ip (4'lü)
            return stem + y + high_vowel(stem) + "p"
        if kind == "inca":                          # -IncA (4'lü + A)
            return stem + y + high_vowel(stem) + "nc" + a
        # -AlI / -AsIyA: A'dan sonra YÜKSEK-DÜZ (yuvarlaklık kaybolur)
        iyi = "i" if a == "e" else "ı"
        if kind == "eli":                           # -AlI
            return stem + y + a + "l" + iyi
        return stem + y + a + "s" + iyi + "y" + a    # -AsIyA

    # ünsüz-başlı: çıplak kök (yumuşama/ye_de YOK)
    stem = _stem_before_suffix(vs, False)
    a = low_vowel(stem)
    if kind == "madan":                             # -mAdAn
        return stem + "m" + a + "d" + a + "n"
    if kind == "dikce":                             # -DIkçA (D sertleşme + 4'lü)
        d = "t" if hardens(stem) else "d"
        return stem + d + high_vowel(stem) + "kç" + a
    # -mAksIzIn: -mAk sonrası YÜKSEK-DÜZ
    iyi = "i" if a == "e" else "ı"
    return stem + "m" + a + "ks" + iyi + "z" + iyi + "n"


# ---------------------------------------------------------------------------
# Biçim-eklenen ulaçlar — finit taban üstüne biner (casina-spec.md, ken-spec.md).
# Taban motorun `conjugate` çıktısından AYNEN alınır (yumuşama/-Ir istisna/olumsuz
# orada çözülü); ek yalnız tabanın son sesine/ünlüsüne göre gerçeklenir.
# ---------------------------------------------------------------------------
def converb_casina(lemma: str, *, base: str = "aorist", negative: bool = False) -> str:
    """`-cAsInA` gibilik/benzerlik zarf-fiili (gülercesine, gelmişçesine). base ∈
    {aorist, evid}. Kişisiz. C(ç/c son-ses) + A(alçak) + s + Iyi(YÜKSEK-DÜZ) + n + A."""
    if base not in _CASINA_BASES:
        raise ValueError(
            f"bilinmeyen -cAsInA tabanı: {base!r}. Geçerli: {', '.join(sorted(_CASINA_BASES))}"
        )
    stem = conjugate(lemma, base, "3sg", negative=negative)
    a = low_vowel(stem)                              # a / e — son ünlüden
    iyi = "ı" if a == "a" else "i"                   # YÜKSEK-DÜZ (yuvarlaklık taşınmaz)
    c = "ç" if hardens(stem) else "c"                # son ses sert → ç
    return stem + c + a + "s" + iyi + "n" + a


def converb_ken(lemma: str, *, base: str = "aorist", negative: bool = False) -> str:
    """`-ken` zaman zarf-fiili (gelirken, geliyorken). base ∈ {aorist, pres, evid, fut}.
    `-ken` DONMUŞ ektir (ünlü uyumu YOK); finit taban ünsüz-final → glide YOK."""
    if base not in _KEN_BASES:
        raise ValueError(
            f"bilinmeyen -ken tabanı: {base!r}. Geçerli: {', '.join(sorted(_KEN_BASES))}"
        )
    stem = conjugate(lemma, base, "3sg", negative=negative)
    return stem + "ken"


# ---------------------------------------------------------------------------
# Fiilimsi (sıfat-fiil / ad-fiil) + iyelik/durum istifi — A3 (participle-spec.md)
# Bare fiilimsi gövde fiil primitifleriyle kurulur, sonra İSİM motoruna (decline)
# beslenir: iyelik/durum, k→ğ yumuşaması, pronominal -n- oradan gelir.
# ---------------------------------------------------------------------------
PARTICIPLES = frozenset({"dik", "acak", "ma", "mak", "is"})


def _participle_bare(vs, kind: str) -> str:
    """Bare fiilimsi gövdesi (iyelik/durum eklenmemiş)."""
    if kind in ("acak", "is"):                      # ünlü-başlı (yumuşama/ye_de)
        stem = _stem_before_suffix(vs, True)
        y = "y" if ends_in_vowel(stem) else ""
        if kind == "acak":                          # -AcAk
            a = low_vowel(stem)
            return stem + y + a + "c" + a + "k"
        return stem + y + high_vowel(stem) + "ş"     # -Iş (4'lü)
    # ünsüz-başlı: çıplak kök (yumuşama/ye_de YOK)
    stem = _stem_before_suffix(vs, False)
    a = low_vowel(stem)
    if kind == "dik":                               # -DIk (D sertleşme + 4'lü)
        d = "t" if hardens(stem) else "d"
        return stem + d + high_vowel(stem) + "k"
    if kind == "ma":                                # -mA
        return stem + "m" + a
    return stem + "m" + a + "k"                       # -mAk (mastar)


def participle(lemma: str, kind: str, *, possessive: str | None = None,
               case: str | None = None) -> str:
    """Fiilimsi (sıfat-fiil dik/acak, ad-fiil ma/mak/is) + iyelik/durum. İyelik/durum
    verilmezse bare fiilimsi döner. İstif İSİM motoruna (decline) delege edilir."""
    if kind not in PARTICIPLES:
        raise ValueError(
            f"bilinmeyen fiilimsi: {kind!r}. Geçerli: {', '.join(sorted(PARTICIPLES))}"
        )
    vs = parse_verb(lemma)
    bare = _participle_bare(vs, kind)
    if possessive is None and case is None:
        return vs.prefix + bare
    kw: dict = {}
    if possessive is not None:
        kw["possessive"] = possessive
    if case is not None:
        kw["case"] = case
    return vs.prefix + decline(bare, **kw)
