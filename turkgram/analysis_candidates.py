"""Öneri üretim katmanı (analysis_candidates): kök adayları + grid enumerasyonu.

Saf fonksiyonlar — üreteç/oracle ÇAĞIRMAZ. analysis.py tarafından import edilir.
Bağımlılık: yalnız morfofonoloji sabitleri + nonfinite sabitleri.
"""
from __future__ import annotations

import itertools
import re
from typing import Any

from .nonfinite import CONVERBS, PARTICIPLES

# ---------------------------------------------------------------------------
# Ünlüler
# ---------------------------------------------------------------------------
_VOWELS = "aeıioöuüâîû"


# ---------------------------------------------------------------------------
# Eksen sabitleri
# ---------------------------------------------------------------------------
_FINITE_TENSES = ("pres", "past", "fut", "aorist", "evid", "cond", "necess", "opt", "imp")
_PERSONS = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")
_CASES = ("nom", "acc", "dat", "loc", "abl", "gen", "ins")
_POSSESSIVES = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")
_COPULA_AUX = (None, "hikaye", "rivayet", "sart")
_CONJ_AUX = (None, "hikaye", "rivayet", "sart")
_ASPECTS = (None, "iver", "adur", "agel", "akal", "ayaz")

# 24 çatı zinciri (SPEC §5): (refl|recip ≤1) × (caus 0-3) × (pass 0-1)
_VOICE_CHAINS: list[tuple[str, ...]] = []
for _vc_base in ((), ("refl",), ("recip",)):
    for _vc_caus_n in range(4):
        for _vc_pass in ((), ("pass",)):
            _VOICE_CHAINS.append(_vc_base + ("caus",) * _vc_caus_n + _vc_pass)

assert len(_VOICE_CHAINS) == 24


# ---------------------------------------------------------------------------
# Ses filtreleri (SPEC §3) — her filtre: (eksen, değer) → zorunlu regex
# Filtre yalnız gereklilik → hiçbir zaman recall kırmaz.
# ---------------------------------------------------------------------------
_FILTERS: dict[tuple[str, Any], re.Pattern[str]] = {
    # conjugate tense
    ("tense", "pres"):   re.compile(r"yor"),
    ("tense", "fut"):    re.compile(r"c[ae]"),
    ("tense", "evid"):   re.compile(r"m[ıiuü]ş"),
    ("tense", "necess"): re.compile(r"m[ae]l[ıi]"),
    ("tense", "cond"):   re.compile(r"s[ae]"),
    ("tense", "past"):   re.compile(r"[dt][ıiuü]"),
    # kesişen eksenler
    ("question", True):  re.compile(r" m[ıiuü]"),
    ("aux", "hikaye"):   re.compile(r"[dt][ıiuü]"),
    ("aux", "rivayet"):  re.compile(r"m[ıiuü]ş"),
    ("aux", "sart"):     re.compile(r"s[ae]"),
    ("aspect", "iver"):  re.compile(r"ver"),
    ("aspect", "adur"):  re.compile(r"dur"),
    ("aspect", "agel"):  re.compile(r"gel"),
    ("aspect", "akal"):  re.compile(r"kal"),
    ("aspect", "ayaz"):  re.compile(r"yaz"),
    ("negative", True):  re.compile(r"m[ae]"),
    ("ability", True):   re.compile(r"[ae]bil|[ae]m[ae]"),
    # copula
    ("copula_aux", "rivayet"): re.compile(r"m[ıiuü]ş"),
    # converb
    ("converb_kind", "dikce"): re.compile(r"[kc][cç]"),
    # participle
    ("participle_is", None):  re.compile(r"ş"),
}


def _cell_allowed(surface: str, axis: str, value: Any) -> bool:
    """Filtre geçerse True (enumerate devam), aksi halde atla."""
    pat = _FILTERS.get((axis, value))
    if pat is None:
        return True
    return bool(pat.search(surface))


# ---------------------------------------------------------------------------
# Ünlü sayısı yardımcıları
# ---------------------------------------------------------------------------
def _count_vowels(s: str) -> int:
    return sum(1 for ch in s if ch in _VOWELS)


def _vowel_budget(surface_token: str, prefix_len: int) -> int:
    """Suffix bölgesindeki ünlü sayısı (kanonik guard sınırı)."""
    return _count_vowels(surface_token[prefix_len:])


# ---------------------------------------------------------------------------
# Ters-mutasyon envanteri (SPEC §4) — kök adayları
# ---------------------------------------------------------------------------
def _reverse_mutations(prefix: str) -> list[str]:
    """Verilen öneke ters-mutasyon uygula → ek aday kök listesi."""
    candidates: list[str] = []
    if not prefix:
        return candidates
    last = prefix[-1]
    init = prefix[:-1]

    # d → t (git→gid, isim t→d yumuşama)
    if last == "d":
        candidates.append(init + "t")
    # ğ → k (çok-heceli k→ğ)
    if last == "ğ":
        candidates.append(init + "k")
    # b → p (kitap→kitab)
    if last == "b":
        candidates.append(init + "p")
    # c → ç (amaç→amac)
    if last == "c":
        candidates.append(init + "ç")
    # g → k (nk→ng bağlamı: renk→reng)
    if last == "g" and len(init) >= 1 and init[-1] == "n":
        candidates.append(init + "k")
    # ye_de: i/ı → e (yi→ye, di→de — sadece ünlüyle biten, son ünlü i/ı)
    if last in "iı":
        candidates.append(init + "e")
    # Düşen ünlü: ikiz-ünsüz tekleştir (hakk→hak, redd→ret)
    if len(prefix) >= 2 and prefix[-1] == prefix[-2]:
        candidates.append(prefix[:-1])
    # Düşen ünlü geri-ekle: son hece ünsüz-ünsüz bitiyor, son ünlüden harmoni
    # (burn→burun, ağzı→ağız). Basit buluşsal: son 2 harf ünsüz mü?
    if len(prefix) >= 2 and prefix[-1] not in _VOWELS and prefix[-2] not in _VOWELS:
        # Son ünlüyü bul
        last_v_idx = max((i for i, c in enumerate(prefix) if c in _VOWELS), default=-1)
        if last_v_idx >= 0:
            last_v = prefix[last_v_idx]
            # Harmoni uyumlu yüksek ünlü
            if last_v in "aıou":
                insert = "ı" if last_v in "aı" else "u"
            else:
                insert = "i" if last_v in "ei" else "ü"
            candidates.append(prefix[:-1] + insert + prefix[-1])

    return candidates


def _root_candidates(surface_token: str) -> dict[str, list[str]]:
    """
    Yüzey token'ının öneklerinden kök adayları üret.
    Dönüş: {kök_str: [kind_hint, ...]} — kind_hint "verb"|"noun"|"any"
    Her önek için:
      - Fiil lemma = önek + "mak"/"mek" (harmoni)
      - İsim lemma = önek (direkt)
      - Ters-mutasyon çeşitleri
    """
    result: dict[str, list[str]] = {}

    def _add(cand: str, kind: str) -> None:
        if cand not in result:
            result[cand] = []
        if kind not in result[cand]:
            result[cand].append(kind)

    n = len(surface_token)
    # En az 1 harf önek (boş önek = yüzeyin kendisi fiilimsi kök değil)
    for end in range(1, n + 1):
        prefix = surface_token[:end]
        # Yalnız ünlü içeren önekler (SPEC §Adım 1)
        if not any(c in _VOWELS for c in prefix):
            continue

        # İsim kökü: doğrudan
        _add(prefix, "noun")

        # Fiil kökü: mastar eki (harmoni: son ünlüye göre)
        last_v = next((c for c in reversed(prefix) if c in _VOWELS), None)
        # Türkçe ünlü harmoni: ön-ünlü → mek, arka → mak
        if last_v in ("e", "i", "ü", "ö"):
            suffix = "mek"
        else:
            suffix = "mak"
        _add(prefix + suffix, "verb")

        # Ters-mutasyonlar
        for mutated in _reverse_mutations(prefix):
            if not any(c in _VOWELS for c in mutated):
                continue
            _add(mutated, "noun")
            last_mv = next((c for c in reversed(mutated) if c in _VOWELS), None)
            if last_mv in ("e", "i", "ü", "ö"):
                msuffix = "mek"
            else:
                msuffix = "mak"
            _add(mutated + msuffix, "verb")

    return result


# ---------------------------------------------------------------------------
# Filtre + bütçe yardımcıları (_enumerate_conjugate için)
# ---------------------------------------------------------------------------
def _passes_filters(surface: str, combo: tuple[Any, ...]) -> bool:
    """Tüm eksen filtrelerini kontrol et; herhangi biri başarısız → False."""
    tense, person, neg, abil, quest, aux, asp = combo
    if not _cell_allowed(surface, "tense", tense):
        return False
    if neg and not _cell_allowed(surface, "negative", True):
        return False
    if abil and not _cell_allowed(surface, "ability", True):
        return False
    if quest and not _cell_allowed(surface, "question", True):
        return False
    if aux and not _cell_allowed(surface, "aux", aux):
        return False
    if asp and not _cell_allowed(surface, "aspect", asp):
        return False
    return True


def _estimate_morphs(combo: tuple[Any, ...]) -> int:
    """Ünlü-yuvası bütçe tahmini (kaba — oracle kesin)."""
    _tense, _person, neg, abil, _quest, aux, asp = combo
    n = 1  # tense
    if neg:
        n += 1
    if abil:
        n += 1
    if aux:
        n += 1
    if asp:
        n += 2  # aspect aux = 2+ ünlü
    return n


# ---------------------------------------------------------------------------
# Grid enumerasyon — her kind için hipotez kümesi
# ---------------------------------------------------------------------------
def _enumerate_conjugate(surface: str, stem: str, lemma: str) -> list[dict[str, Any]]:
    """Conjugate hipotezleri; ses filtreleri + ünlü-yuvası guard."""
    budget = max(0, _count_vowels(surface) - _count_vowels(stem))
    multi = " " in surface
    hyps: list[dict[str, Any]] = []

    for combo in itertools.product(
        _FINITE_TENSES, _PERSONS,
        (False, True), (False, True), (False, True),
        _CONJ_AUX, _ASPECTS,
    ):
        tense, person, neg, abil, quest, aux, asp = combo
        # Soru multi-token gerektiriyor
        if quest and not multi:
            continue
        if not _passes_filters(surface, combo):
            continue
        n_morphs = _estimate_morphs(combo)
        if n_morphs > budget + 2:  # +2 tolerans (kişi eki vs.)
            continue
        for vc in _VOICE_CHAINS:
            if vc and n_morphs + len(vc) > budget + 3:
                continue
            hyps.append({
                "tense": tense, "person": person,
                "negative": neg, "ability": abil,
                "question": quest, "aux": aux,
                "aspect": asp,
                "voice_chain": vc if vc else None,
            })
    return hyps


def _enumerate_decline(surface: str, stem: str) -> list[dict[str, Any]]:
    budget = _count_vowels(surface) - _count_vowels(stem)
    hyps: list[dict[str, Any]] = []
    for number in ("sg", "pl"):
        if number == "pl" and budget < 1:
            continue
        for poss in (None,) + tuple(_POSSESSIVES):
            poss_cost = 0 if poss is None else 1
            for case in _CASES:
                case_cost = 0 if case == "nom" else 1
                total = (1 if number == "pl" else 0) + poss_cost + case_cost
                if total > budget + 1:
                    continue
                hyps.append({"number": number, "possessive": poss, "case": case})
    return hyps


def _enumerate_copula(surface: str, stem: str) -> list[dict[str, Any]]:
    budget = _count_vowels(surface) - _count_vowels(stem)
    hyps: list[dict[str, Any]] = []
    for aux in _COPULA_AUX:
        if aux and not _cell_allowed(surface, "copula_aux", aux):
            continue
        aux_cost = 1 if aux else 0
        for person in _PERSONS:
            for number in ("sg", "pl"):
                for poss in (None,) + tuple(_POSSESSIVES):
                    poss_cost = 0 if poss is None else 1
                    for case in (None,) + tuple(_CASES):
                        case_cost = 0 if case is None else 1
                        for question in (False, True):
                            if question and " " not in surface:
                                continue
                            total = aux_cost + poss_cost + case_cost
                            if total > budget + 2:
                                continue
                            hyps.append({
                                "aux": aux, "person": person,
                                "number": number, "possessive": poss,
                                "case": case, "question": question,
                            })
    return hyps


def _enumerate_converb(surface: str, stem: str) -> list[dict[str, Any]]:
    hyps: list[dict[str, Any]] = []
    for kind in CONVERBS:
        if kind == "dikce" and not _cell_allowed(surface, "converb_kind", "dikce"):
            continue
        hyps.append({"kind": kind})
    return hyps


def _enumerate_participle(surface: str, stem: str) -> list[dict[str, Any]]:
    budget = _count_vowels(surface) - _count_vowels(stem)
    hyps: list[dict[str, Any]] = []
    for ptype in PARTICIPLES:
        if ptype == "is" and not _cell_allowed(surface, "participle_is", None):
            continue
        for poss in (None,) + tuple(_POSSESSIVES):
            poss_cost = 0 if poss is None else 1
            for case in (None,) + tuple(_CASES):
                case_cost = 0 if case is None else 1
                if poss_cost + case_cost > budget + 1:
                    continue
                hyps.append({"ptype": ptype, "possessive": poss, "case": case})
    return hyps
