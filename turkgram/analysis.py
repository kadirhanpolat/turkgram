"""Çözümleyici (analysis): yüzey → kök+eksenler — Faz 2a.

Mimari (docs/faz2a-cozumleyici-tasarim.md): önek-tabanlı kök adayları + ses-filtreli
grid enumerasyonu + üreteç oracle. Üreteç tek doğruluk kaynağı → form-precision yapısal.

Genel akış:
  Adım 0: giriş doğrulama + _tr_lower normalizasyon
  Adım 1: _root_candidates → (kök_str, kind_hint) aday kümesi
  Adım 2: _enumerate → ses-filtreli + ünlü-yuvası güvenli hipotez listesi
  Adım 3: dedup → oracle doğrulama (_verify) → sıralama → segmentasyon

parse_verb ↔ analyze ayrımı: parse_verb kökü ve morfofonolojik sınıfı tanımlar
(fiil-odaklı, çekim ÜRETMEZ); analyze yüzeyi parse eder → tüm olası kök+eksen
kombinasyonlarını döndürür (çözümleme).
"""
from __future__ import annotations

import functools
import re
from dataclasses import dataclass
from typing import Any, Collection, Mapping

from .morphology import conjugate, TENSES as _MORPH_TENSES
from .morphology_noun import decline, copula
from .nonfinite import converb, participle, CONVERBS, PARTICIPLES

# ---------------------------------------------------------------------------
# _tr_lower — YEREL kopya (tr.py'den import ETME: döngü tuzağı)
# ---------------------------------------------------------------------------
def _tr_lower(s: str) -> str:
    return s.replace("İ", "i").replace("I", "ı").lower()


# ---------------------------------------------------------------------------
# Veri tipleri (frozen)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Segment:
    """Bir morfemin yüzey dilimi + kanonik etiketi + yüzey içi ofseti."""
    surface: str
    label: str
    span: tuple[int, int]


@dataclass(frozen=True)
class Analysis:
    """Tek çözümleme: kanonik kwargs, segmentasyon, hypothetical bayrağı."""
    lemma: str
    pos: str        # "verb" | "noun"
    kind: str       # "conjugate"|"decline"|"copula"|"converb"|"participle"
    kwargs: Mapping[str, Any]
    segments: tuple[Segment, ...]
    hypothetical: bool


# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------
_POS = ("verb", "noun")
_KINDS = ("conjugate", "decline", "copula", "converb", "participle")

# 9 finite tense (conv_arak / part_dik ÇIKARILIR — SPEC §1)
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

# _KIND_FUNCS özel sabit (SPEC §Adım 3)
_KIND_FUNCS: dict[str, Any] = {
    "conjugate": conjugate,
    "decline": decline,
    "copula": copula,
    "converb": converb,
    "participle": participle,
}

# Ünlüler (Türkçe) — 8 temel + uzun varyantlar; ö DAHIL
_VOWELS = "aeıioöuüâîû"


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
    ("participle_is",):  re.compile(r"ş"),
}


def _cell_allowed(surface: str, axis: str, value: Any) -> bool:
    """Filtre geçerse True (enumerate devam), aksi halde atla."""
    key = (axis, value)
    pat = _FILTERS.get(key)
    if pat is None:
        return True
    return bool(pat.search(surface))


# ---------------------------------------------------------------------------
# Ünlü sayısı yardımcıları
# ---------------------------------------------------------------------------
def _count_vowels(s: str) -> int:
    return sum(1 for ch in s if ch in _VOWELS)


# ---------------------------------------------------------------------------
# Kanonik kwargs (SPEC §6) — default eksenler kwargs'ta YER ALMAZ
# voice_chain TUPLE olarak saklanır (hashable).
# ---------------------------------------------------------------------------
_CONJUGATE_DEFAULTS: dict[str, Any] = {
    "negative": False,
    "ability": False,
    "question": False,
    "aux": None,
    "aspect": None,
}
# voice_chain=() → her zaman atılır


def _canon_conjugate(kwargs: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for k, v in kwargs.items():
        if k == "voice_chain":
            vc = tuple(v) if v else ()
            if vc:
                out[k] = vc  # tuple — hashable
            # else atla (boş zincir)
        elif k in _CONJUGATE_DEFAULTS and v == _CONJUGATE_DEFAULTS[k]:
            pass  # default, atla
        else:
            out[k] = v
    return out


def _canon_decline(kwargs: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for k, v in kwargs.items():
        if k == "number" and v == "sg":
            pass
        elif k == "possessive" and v is None:
            pass
        elif k == "case" and v == "nom":
            pass
        else:
            out[k] = v
    return out


def _canon_copula(kwargs: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for k, v in kwargs.items():
        if k == "aux" and v is None:
            pass
        elif k == "case" and v in (None, "nom"):
            pass  # nom = default (same as None for copula)
        elif k == "possessive" and v is None:
            pass
        elif k == "number" and v == "sg":
            pass
        elif k == "question" and v is False:
            pass
        else:
            out[k] = v
    return out


def _canon_participle(kwargs: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for k, v in kwargs.items():
        if k == "possessive" and v is None:
            pass
        elif k == "case" and v in (None, "nom"):
            pass  # nom = default (same as None for participle)
        else:
            out[k] = v
    return out


def _canonicalize(kind: str, kwargs: dict[str, Any]) -> dict[str, Any]:
    if kind == "conjugate":
        return _canon_conjugate(kwargs)
    if kind == "decline":
        return _canon_decline(kwargs)
    if kind == "copula":
        return _canon_copula(kwargs)
    if kind == "converb":
        return dict(kwargs)  # kind zorunlu, değiştirme
    if kind == "participle":
        return _canon_participle(kwargs)
    return dict(kwargs)


# ---------------------------------------------------------------------------
# Ters-mutasyon envanteri (SPEC §4) — kök adayları
# ---------------------------------------------------------------------------
def _reverse_mutations(prefix: str) -> list[str]:
    """Verilen öneke ters-mutasyon uygula → ek aday kök listesi."""
    candidates = []
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
# Grid enumerasyon — her kind için hipotez kümesi
# ---------------------------------------------------------------------------
def _vowel_budget(surface_token: str, prefix_len: int) -> int:
    """Suffix bölgesindeki ünlü sayısı (kanonik guard sınırı)."""
    return _count_vowels(surface_token[prefix_len:])


def _enumerate_conjugate(surface: str, stem: str, lemma: str) -> list[dict]:
    """Conjugate hipotezleri; ses filtreleri + ünlü-yuvası guard."""
    budget = _count_vowels(surface) - _count_vowels(stem)
    if budget < 0:
        budget = 0
    hyps = []

    for tense in _FINITE_TENSES:
        if not _cell_allowed(surface, "tense", tense):
            continue
        for person in _PERSONS:
            for neg in (False, True):
                if neg and not _cell_allowed(surface, "negative", True):
                    continue
                for abil in (False, True):
                    if abil and not _cell_allowed(surface, "ability", True):
                        continue
                    for quest in (False, True):
                        if quest and not _cell_allowed(surface, "question", True):
                            continue
                        # Soru multi-token gerektiriyor — yalnız multi-token surface'de dene
                        if quest and " " not in surface:
                            continue
                        for aux in _CONJ_AUX:
                            if aux and not _cell_allowed(surface, "aux", aux):
                                continue
                            for asp in _ASPECTS:
                                if asp and not _cell_allowed(surface, "aspect", asp):
                                    continue
                                # Ünlü-yuvası bütçe tahmini (kaba — oracle kesin)
                                n_morphs = 1  # tense
                                if neg:
                                    n_morphs += 1
                                if abil:
                                    n_morphs += 1
                                if aux:
                                    n_morphs += 1
                                if asp:
                                    n_morphs += 2  # aspect aux = 2+ ünlü
                                if n_morphs > budget + 2:  # +2 tolerans (kişi eki vs.)
                                    continue
                                for vc in _VOICE_CHAINS:
                                    if len(vc) > 0:
                                        # Çatı ekleri de ünlü tüketir
                                        if n_morphs + len(vc) > budget + 3:
                                            continue
                                    # voice_chain: tuple (hashable) veya None
                                    raw_kwargs: dict[str, Any] = {
                                        "tense": tense,
                                        "person": person,
                                        "negative": neg,
                                        "ability": abil,
                                        "question": quest,
                                        "aux": aux,
                                        "aspect": asp,
                                        "voice_chain": vc if vc else None,
                                    }
                                    hyps.append(raw_kwargs)
    return hyps


def _enumerate_decline(surface: str, stem: str) -> list[dict]:
    budget = _count_vowels(surface) - _count_vowels(stem)
    hyps = []
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


def _enumerate_copula(surface: str, stem: str) -> list[dict]:
    budget = _count_vowels(surface) - _count_vowels(stem)
    hyps = []
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


def _enumerate_converb(surface: str, stem: str) -> list[dict]:
    hyps = []
    for kind in CONVERBS:
        if kind == "dikce" and not _cell_allowed(surface, "converb_kind", "dikce"):
            continue
        hyps.append({"kind": kind})
    return hyps


def _enumerate_participle(surface: str, stem: str) -> list[dict]:
    budget = _count_vowels(surface) - _count_vowels(stem)
    hyps = []
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


# ---------------------------------------------------------------------------
# Oracle doğrulama — lru_cache ile sarıl; çağrı sayacı
# ---------------------------------------------------------------------------
_call_count_state = [0]


def reset_call_count() -> None:
    """Test bütçesi için sayaç sıfırla (lru_cache de temizlenir)."""
    _call_count_state[0] = 0
    _call_generator.cache_clear()


def call_count() -> int:
    """Son reset'ten bu yana oracle çağrı sayısı."""
    return _call_count_state[0]


def _make_frozen(kwargs: dict[str, Any]) -> tuple:
    """kwargs → hashable tuple. voice_chain list/tuple → list (conjugate için), frozen olarak tuple."""
    items = []
    for k, v in sorted(kwargs.items(), key=lambda x: str(x)):
        # voice_chain liste ya da tuple → tuple (hashable)
        if k == "voice_chain" and isinstance(v, (list, tuple)):
            items.append((k, tuple(v)))
        else:
            items.append((k, v))
    return tuple(items)


@functools.lru_cache(maxsize=65536)
def _call_generator(kind: str, lemma: str, frozen_kwargs: tuple) -> str | None:
    """Üreteç oracle — cache'li. frozen_kwargs = tuple(sorted(kwargs.items())) — tüm değerler hashable."""
    _call_count_state[0] += 1
    # Reconstruct kwargs; voice_chain tuple → list (üreteç list bekler)
    kwargs = {}
    for k, v in frozen_kwargs:
        if k == "voice_chain" and isinstance(v, tuple):
            kwargs[k] = list(v)
        else:
            kwargs[k] = v
    fn = _KIND_FUNCS[kind]
    try:
        if kind == "conjugate":
            tense = kwargs.pop("tense")
            person = kwargs.pop("person", None)
            return fn(lemma, tense, person, **kwargs)
        elif kind == "decline":
            return fn(lemma, **kwargs)
        elif kind == "copula":
            aux = kwargs.pop("aux", None)
            person = kwargs.pop("person", "3sg")
            return fn(lemma, aux, person, **kwargs)
        elif kind == "converb":
            return fn(lemma, kwargs["kind"])
        elif kind == "participle":
            ptype = kwargs.pop("ptype")
            return fn(lemma, ptype, **kwargs)
        else:
            return None
    except (ValueError, KeyError, TypeError):
        return None


def _verify(kind: str, lemma: str, raw_kwargs: dict[str, Any], surface: str) -> bool:
    """Üreteç çağır; çıktı == surface ise True."""
    frozen = _make_frozen(raw_kwargs)
    result = _call_generator(kind, lemma, frozen)
    return result is not None and result == surface


# ---------------------------------------------------------------------------
# Segmentasyon (SPEC §7) — incremental generation
# ---------------------------------------------------------------------------

# Eksen etiketleri (modül seviyesi)
_AXIS_LABELS: dict[str, str] = {
    # tense
    "tense:pres": "Iyor", "tense:past": "DI", "tense:fut": "AcAk",
    "tense:aorist": "Ir", "tense:evid": "mIş", "tense:cond": "sA",
    "tense:necess": "mAlI", "tense:opt": "A", "tense:imp": "imp",
    # person
    "person:1sg": "1sg", "person:2sg": "2sg", "person:3sg": "3sg",
    "person:1pl": "1pl", "person:2pl": "2pl", "person:3pl": "3pl",
    # negative / ability
    "negative:True": "mA", "ability:True": "Abil",
    # aux (ekfiil)
    "aux:hikaye": "hikaye", "aux:rivayet": "rivayet", "aux:sart": "sart",
    # aspect
    "aspect:iver": "iver", "aspect:adur": "adur", "aspect:agel": "agel",
    "aspect:akal": "akal", "aspect:ayaz": "ayaz",
    # question
    "question:True": "mI",
    # decline
    "number:pl": "lAr",
    "case:acc": "acc", "case:dat": "dat", "case:loc": "loc",
    "case:abl": "abl", "case:gen": "gen", "case:ins": "ins",
    "possessive:1sg": "1sg", "possessive:2sg": "2sg", "possessive:3sg": "3sg",
    "possessive:1pl": "1pl", "possessive:2pl": "2pl", "possessive:3pl": "3pl",
    # converb
    "kind:arak": "arak", "kind:ip": "ip", "kind:inca": "inca",
    "kind:madan": "madan", "kind:dikce": "dikce", "kind:meksizin": "meksizin",
    "kind:eli": "eli", "kind:esiye": "esiye",
    # participle
    "ptype:dik": "DIk", "ptype:acak": "acak", "ptype:ma": "mA",
    "ptype:mak": "mAk", "ptype:is": "is",
}


def _get_label(axis: str, value: Any) -> str:
    key = f"{axis}:{value}"
    return _AXIS_LABELS.get(key, f"{axis}:{value}")


def _gen_with_raw(kind: str, lemma: str, kw: dict[str, Any]) -> str | None:
    """Raw kwargs → oracle çağrısı."""
    frozen = _make_frozen(kw)
    return _call_generator(kind, lemma, frozen)


def _raw_from_canon(kind: str, canon: dict[str, Any]) -> dict[str, Any]:
    """Canon kwargs'ı üreteç ham çağrı formatına dönüştür (atılan defaults geri ekle)."""
    raw = dict(canon)
    if kind == "conjugate":
        raw.setdefault("negative", False)
        raw.setdefault("ability", False)
        raw.setdefault("question", False)
        raw.setdefault("aux", None)
        raw.setdefault("aspect", None)
        if "voice_chain" not in raw:
            raw["voice_chain"] = None
        elif isinstance(raw["voice_chain"], (list, tuple)) and len(raw["voice_chain"]) == 0:
            raw["voice_chain"] = None
    elif kind == "decline":
        raw.setdefault("number", "sg")
        raw.setdefault("possessive", None)
        raw.setdefault("case", "nom")
    elif kind == "copula":
        raw.setdefault("aux", None)
        raw.setdefault("case", None)
        raw.setdefault("possessive", None)
        raw.setdefault("number", "sg")
        raw.setdefault("question", False)
    elif kind == "participle":
        raw.setdefault("possessive", None)
        raw.setdefault("case", None)
    return raw


def _imp2sg(lemma: str, **kw: Any) -> str | None:
    """conjugate(lemma, 'imp', '2sg', **kw) → stem proxy; returns None on error."""
    frozen = _make_frozen({"tense": "imp", "person": "2sg",
                           "negative": False, "ability": False,
                           "question": False, "aux": None, "aspect": None,
                           "voice_chain": None, **kw})
    return _call_generator("conjugate", lemma, frozen)


def _segs_to_tuple(segs_in_order: list[tuple[str, str]]) -> tuple[Segment, ...]:
    """(surface, label) listesini span'lı Segment demetine dönüştür."""
    result: list[Segment] = []
    cursor = 0
    for surf, lbl in segs_in_order:
        result.append(Segment(surface=surf, label=lbl, span=(cursor, cursor + len(surf))))
        cursor += len(surf)
    return tuple(result)


def _segment_conjugate(lemma: str, canon: dict[str, Any],
                       surface: str) -> tuple[Segment, ...]:
    """
    Fiil çekimi segmentasyonu — imp-2sg stem proxy yöntemi.

    Katmanlar (içten dışa):
      KÖK | ses_zinciri | abil/neg | tense | aux | person
    """
    tense = canon["tense"]
    person = canon.get("person", "3sg")
    negative = canon.get("negative", False)
    ability = canon.get("ability", False)
    aux = canon.get("aux", None)
    aspect = canon.get("aspect", None)
    voice_chain = canon.get("voice_chain", None)
    vc: tuple = tuple(voice_chain) if voice_chain else ()

    # aspect kw eklemek için yardımcı
    asp_kw: dict[str, Any] = {}
    if aspect:
        asp_kw["aspect"] = aspect

    # 1. Bare stem (tüm zincirler olmadan)
    bare = _imp2sg(lemma, **asp_kw)
    if bare is None:
        bare = surface
    stem_len = len(bare)

    # 2. Ses zinciri: her adım için imp-2sg ile progressif uzunluk
    vc_segs: list[tuple[str, str]] = []
    prev_len = stem_len
    for i, voice_elem in enumerate(vc):
        voiced = _imp2sg(lemma, voice_chain=list(vc[:i + 1]), **asp_kw)
        if voiced is None:
            break
        seg_surf = surface[prev_len:len(voiced)]
        vc_segs.append((seg_surf, voice_elem))
        prev_len = len(voiced)
    voiced_end = prev_len  # imp-2sg + full voice chain uzunluğu

    # 3. Ability / negative / combined (AmA)
    mod_segs: list[tuple[str, str]] = []
    mod_end = voiced_end
    if ability and negative:
        # AmA = ability+negative combined; ama_form (hem negative hem ability) uzunluğu pivot
        vc_kw = {"voice_chain": list(vc)} if vc else {}
        ama_form = _imp2sg(lemma, negative=True, ability=True, **vc_kw, **asp_kw)
        if ama_form is not None:
            ama_surf = surface[voiced_end:len(ama_form)]
            mod_segs.append((ama_surf, "AmA"))
            mod_end = len(ama_form)
    elif ability:
        vc_kw = {"voice_chain": list(vc)} if vc else {}
        abil_form = _imp2sg(lemma, ability=True, **vc_kw, **asp_kw)
        if abil_form is not None:
            abil_surf = surface[voiced_end:len(abil_form)]
            mod_segs.append((abil_surf, "Abil"))
            mod_end = len(abil_form)
    elif negative:
        vc_kw = {"voice_chain": list(vc)} if vc else {}
        neg_form = _imp2sg(lemma, negative=True, **vc_kw, **asp_kw)
        if neg_form is not None:
            neg_surf = surface[voiced_end:len(neg_form)]
            mod_segs.append((neg_surf, "mA"))
            mod_end = len(neg_form)

    # 4. Tense: conjugate(tense, None, mod_flags, no_aux)
    vc_kw2 = {"voice_chain": list(vc)} if vc else {}
    mod_kw: dict[str, Any] = {}
    if negative:
        mod_kw["negative"] = True
    if ability:
        mod_kw["ability"] = True
    t3sg_no_aux = _gen_with_raw("conjugate", lemma, {
        "tense": tense, "person": None,
        "negative": mod_kw.get("negative", False),
        "ability": mod_kw.get("ability", False),
        "question": False, "aux": None,
        "aspect": aspect, "voice_chain": list(vc) if vc else None,
    })
    if t3sg_no_aux is None:
        t3sg_no_aux = surface  # fallback

    tense_surf = surface[mod_end:len(t3sg_no_aux)]
    tense_segs: list[tuple[str, str]] = []
    if tense_surf:
        tense_segs.append((tense_surf, _get_label("tense", tense)))

    # 5. Aux (hikaye/rivayet/sart): 3sg + aux
    aux_segs: list[tuple[str, str]] = []
    aux_end = len(t3sg_no_aux)
    if aux:
        t3sg_with_aux = _gen_with_raw("conjugate", lemma, {
            "tense": tense, "person": None,
            "negative": mod_kw.get("negative", False),
            "ability": mod_kw.get("ability", False),
            "question": False, "aux": aux,
            "aspect": aspect, "voice_chain": list(vc) if vc else None,
        })
        if t3sg_with_aux is not None:
            aux_surf = surface[aux_end:len(t3sg_with_aux)]
            if aux_surf:
                aux_segs.append((aux_surf, _get_label("aux", aux)))
            aux_end = len(t3sg_with_aux)

    # 6. Person suffix
    person_surf = surface[aux_end:]
    person_segs: list[tuple[str, str]] = []
    if person_surf and person and person != "3sg":
        person_segs.append((person_surf, _get_label("person", person)))

    # Birleştir: KÖK | voice | mod | tense | aux | person
    root_surf = surface[:stem_len]
    all_segs = ([(root_surf, "KÖK")] + vc_segs + mod_segs
                + tense_segs + aux_segs + person_segs)
    return _segs_to_tuple(all_segs)


def _segment_decline(lemma: str, canon: dict[str, Any],
                     surface: str) -> tuple[Segment, ...]:
    """İsim çekimi segmentasyonu — ters-sıralı eksen kaldırma."""
    axes_order = ["case", "possessive", "number"]
    working = dict(canon)
    current_surface = _gen_with_raw("decline", lemma,
                                    _raw_from_canon("decline", working)) or surface
    segs_rev: list[tuple[str, str]] = []

    for axis in axes_order:
        if axis not in working:
            continue
        val = working[axis]
        kw_without = {k: v for k, v in working.items() if k != axis}
        new_surface = _gen_with_raw("decline", lemma,
                                    _raw_from_canon("decline", kw_without))
        if new_surface is None:
            continue
        suffix = current_surface[len(new_surface):]
        if suffix:
            segs_rev.append((suffix, _get_label(axis, val)))
        working = kw_without
        current_surface = new_surface

    # KÖK: current_surface uzunluğu kadar surface'ten al (mutasyon: kitab≠kitap)
    root_surf = surface[:len(current_surface)]
    segs_rev.append((root_surf, "KÖK"))
    return _segs_to_tuple(list(reversed(segs_rev)))


def _segment_copula(lemma: str, canon: dict[str, Any],
                    surface: str) -> tuple[Segment, ...]:
    """Ek-fiil segmentasyonu — lemma KÖK; aux + person oracle'la türetilir."""
    aux = canon.get("aux", None)
    person = canon.get("person", "3sg")

    # KÖK = lemma (tüm uzunluğuyla)
    root_surf = surface[:len(lemma)]

    segs: list[tuple[str, str]] = [(root_surf, "KÖK")]
    pos = len(lemma)

    # aux suffix: copula(lemma, aux, '3sg') - len(lemma)
    if aux:
        t3sg = _gen_with_raw("copula", lemma, {
            "aux": aux, "person": "3sg", "number": "sg",
            "possessive": None, "case": None, "question": False,
        })
        if t3sg is not None:
            aux_surf = surface[pos:len(t3sg)]
            if aux_surf:
                segs.append((aux_surf, _get_label("aux", aux)))
            pos = len(t3sg)

    # person suffix
    person_surf = surface[pos:]
    if person_surf and person and person != "3sg":
        segs.append((person_surf, _get_label("person", person)))

    return _segs_to_tuple(segs)


def _segment_converb(lemma: str, canon: dict[str, Any],
                     surface: str) -> tuple[Segment, ...]:
    """Zarf-fiil (ulaç) segmentasyonu — imp-2sg stem + kind suffix."""
    kind = canon["kind"]
    bare = _imp2sg(lemma)
    stem_len = len(bare) if bare else len(lemma) - 3
    root_surf = surface[:stem_len]
    suffix_surf = surface[stem_len:]
    segs = [(root_surf, "KÖK")]
    if suffix_surf:
        segs.append((suffix_surf, _get_label("kind", kind)))
    return _segs_to_tuple(segs)


def _segment_participle(lemma: str, canon: dict[str, Any],
                        surface: str) -> tuple[Segment, ...]:
    """
    Fiilimsi segmentasyonu — imp-2sg stem + ptype suffix + poss/case.
    Sıra: KÖK | ptype | possessive | case
    """
    ptype = canon["ptype"]
    possessive = canon.get("possessive", None)
    case = canon.get("case", None)

    bare = _imp2sg(lemma)
    stem_len = len(bare) if bare else len(lemma) - 3
    root_surf = surface[:stem_len]

    # ptype suffix: participle(lemma, ptype, possessive=None) = 3sg poss form
    # Its length - stem_len = ptype morpheme length
    ptype_form = _gen_with_raw("participle", lemma,
                               {"ptype": ptype, "possessive": None, "case": None})
    ptype_end = len(ptype_form) if ptype_form else stem_len
    ptype_surf = surface[stem_len:ptype_end]

    segs: list[tuple[str, str]] = [(root_surf, "KÖK")]
    if ptype_surf:
        segs.append((ptype_surf, _get_label("ptype", ptype)))

    # possessive suffix
    if possessive:
        # participle(lemma, ptype, possessive=possessive, case=None)
        poss_form = _gen_with_raw("participle", lemma,
                                  {"ptype": ptype, "possessive": possessive, "case": None})
        if poss_form is not None:
            poss_surf = surface[ptype_end:len(poss_form)]
            if poss_surf:
                segs.append((poss_surf, _get_label("possessive", possessive)))
            ptype_end = len(poss_form)

    # case suffix
    if case and case != "nom":
        case_surf = surface[ptype_end:]
        if case_surf:
            segs.append((case_surf, _get_label("case", case)))

    return _segs_to_tuple(segs)


def _segment(kind: str, lemma: str, canon_kwargs: dict[str, Any],
             surface_token: str) -> tuple[Segment, ...]:
    """Kind'a göre özel segmentasyon fonksiyonuna yönlendir."""
    if kind == "conjugate":
        return _segment_conjugate(lemma, canon_kwargs, surface_token)
    if kind == "decline":
        return _segment_decline(lemma, canon_kwargs, surface_token)
    if kind == "copula":
        return _segment_copula(lemma, canon_kwargs, surface_token)
    if kind == "converb":
        return _segment_converb(lemma, canon_kwargs, surface_token)
    if kind == "participle":
        return _segment_participle(lemma, canon_kwargs, surface_token)
    # Fallback: tüm yüzey = KÖK
    return _segs_to_tuple([(surface_token, "KÖK")])


# ---------------------------------------------------------------------------
# Sıralama anahtarı (SPEC §8)
# ---------------------------------------------------------------------------
def _sort_key(a: Analysis) -> tuple:
    """(segment sayısı↑, çatısız<çatılı, kind sırası, lemma, repr(sorted kwargs))."""
    n_segs = len(a.segments)
    has_voice = 1 if a.kwargs.get("voice_chain") else 0
    kind_idx = _KINDS.index(a.kind) if a.kind in _KINDS else 99
    return (n_segs, has_voice, kind_idx, a.lemma, repr(sorted(a.kwargs.items())))


# ---------------------------------------------------------------------------
# Dedup — frozenset-safe (voice_chain tuple)
# ---------------------------------------------------------------------------
def _kwargs_key(kw: dict[str, Any]) -> frozenset:
    """kwargs → hashable frozenset. voice_chain tuple garantili."""
    items = []
    for k, v in kw.items():
        if k == "voice_chain" and isinstance(v, (list, tuple)):
            items.append((k, tuple(v)))
        else:
            items.append((k, v))
    return frozenset(items)


def set_dedup(items: list[Analysis]) -> list[Analysis]:
    """Aynı (lemma, pos, kind, kwargs) anahtarlı duplikeleri kaldır."""
    seen: set[tuple] = set()
    result = []
    for a in items:
        key = (a.lemma, a.pos, a.kind, _kwargs_key(a.kwargs))
        if key not in seen:
            seen.add(key)
            result.append(a)
    return result


# ---------------------------------------------------------------------------
# Çok-token analizi
# ---------------------------------------------------------------------------
def _analyze_multi_token(tokens: list[str], roots: Collection[str] | None) -> list[Analysis]:
    """
    İki geçerli çok-token kalıbı (SPEC §8):
    1. Soru grubu: son token m[ıiuü]… ile başlıyor
    2. Birleşik önek: ilk token(lar) + son token → birleşik lemma
    """
    results: list[Analysis] = []

    # 1. Soru grubu
    last_tok = tokens[-1]
    if re.match(r"m[ıiuü]", last_tok):
        surface_full = " ".join(tokens)
        body = " ".join(tokens[:-1])
        body_cands = _root_candidates(body)
        for lemma, kind_hints in body_cands.items():
            if "verb" not in kind_hints:
                continue
            if roots is not None and lemma not in roots:
                continue
            hyp = roots is None
            stem = lemma[:-3] if lemma.endswith(("mak", "mek")) else lemma
            for raw_kwargs in _enumerate_conjugate(surface_full, stem, lemma):
                if not raw_kwargs.get("question"):
                    continue
                canon = _canonicalize("conjugate", raw_kwargs)
                raw = _raw_from_canon("conjugate", canon)
                if _verify("conjugate", lemma, raw, surface_full):
                    segs = _segment("conjugate", lemma, canon, surface_full)
                    results.append(Analysis(
                        lemma=lemma, pos="verb", kind="conjugate",
                        kwargs=canon, segments=segs, hypothetical=hyp,
                    ))

    # 2. Birleşik önek (e.g. "aday oldu" → lemma "aday olmak")
    if len(tokens) == 2:
        prefix_tok = tokens[0]
        body_tok = tokens[1]
        surface_full = " ".join(tokens)
        body_cands = _root_candidates(body_tok)
        for body_lemma, kind_hints in body_cands.items():
            if "verb" not in kind_hints:
                continue
            compound_lemma = prefix_tok + " " + body_lemma
            if roots is not None and compound_lemma not in roots:
                continue
            hyp = roots is None
            stem = body_tok[:-3] if body_tok.endswith(("mak", "mek")) else body_tok
            for raw_kwargs in _enumerate_conjugate(surface_full, stem, compound_lemma):
                if raw_kwargs.get("question"):
                    continue
                canon = _canonicalize("conjugate", raw_kwargs)
                raw = _raw_from_canon("conjugate", canon)
                if _verify("conjugate", compound_lemma, raw, surface_full):
                    segs = _segment("conjugate", compound_lemma, canon, surface_full)
                    results.append(Analysis(
                        lemma=compound_lemma, pos="verb", kind="conjugate",
                        kwargs=canon, segments=segs, hypothetical=hyp,
                    ))

    return results


# ---------------------------------------------------------------------------
# Ana giriş noktası
# ---------------------------------------------------------------------------
def analyze(surface: str, pos: str | None = None,
            *, roots: Collection[str] | None = None) -> list[Analysis]:
    """
    Yüzey biçimi → olası Analysis listesi.

    Args:
        surface: Çözümlenecek yüzey biçim (tek ya da çok-token).
        pos: "verb" | "noun" | None (ikisi de).
        roots: Lemma kümesi. Verilmişse lemma∉roots elenir (hypothetical=False);
               verilmemişse hepsi hypothetical=True.

    Returns:
        Deterministik sıralı Analysis listesi. Çözümsüz → [].

    Raises:
        ValueError: Boş/tip-hatalı surface veya bilinmeyen pos.
    """
    # Adım 0: doğrulama
    if not isinstance(surface, str) or not surface.strip():
        raise ValueError(f"geçersiz yüzey: {surface!r}")
    if pos is not None and pos not in _POS:
        raise ValueError(
            f"pos: bilinmeyen değer {pos!r}. Geçerli: {', '.join(_POS)}"
        )
    surface = _tr_lower(surface.strip())

    tokens = surface.split()

    # Çok-token: yalnız tanınan kalıplar
    if len(tokens) > 1:
        if len(tokens) > 2:
            return []  # 3+ token gürültü
        results = _analyze_multi_token(tokens, roots)
        results = sorted(set_dedup(results), key=_sort_key)
        return results

    surface_token = tokens[0]

    # Adım 1: kök adayları
    candidates = _root_candidates(surface_token)

    # Pos filtresi
    pos_filter = set()
    if pos == "verb" or pos is None:
        pos_filter.add("verb")
    if pos == "noun" or pos is None:
        pos_filter.add("noun")

    # Adım 2 + 3: enumerate, dedup, oracle
    seen: set[tuple] = set()
    analyses: list[Analysis] = []

    for lemma, kind_hints in candidates.items():
        if "verb" in kind_hints and lemma.endswith(("mak", "mek")):
            stem = lemma[:-3]
            if "verb" in pos_filter:
                _try_verb(surface_token, lemma, stem, analyses, seen, roots)
        if "noun" in kind_hints:
            stem = lemma  # isim lemma = kök
            if "noun" in pos_filter:
                _try_noun(surface_token, lemma, stem, analyses, seen, roots)

    # Sırala
    analyses.sort(key=_sort_key)
    return analyses


def _try_verb(surface: str, lemma: str, stem: str,
              analyses: list[Analysis], seen: set[tuple],
              roots: Collection[str] | None) -> None:
    """Fiil hipotezlerini üret, doğrula, ekle."""
    # roots verilmişse yalnız roots'taki lemmaları işle
    if roots is not None and lemma not in roots:
        return
    hyp = roots is None  # roots=None → hepsi hypothetical; roots verilmiş → lemma roots'ta → False

    hyp_list = _enumerate_conjugate(surface, stem, lemma)
    for raw_kwargs in hyp_list:
        canon = _canonicalize("conjugate", raw_kwargs)
        key = ("conjugate", lemma, _kwargs_key(canon))
        if key in seen:
            continue
        seen.add(key)
        raw = _raw_from_canon("conjugate", canon)
        if _verify("conjugate", lemma, raw, surface):
            segs = _segment("conjugate", lemma, canon, surface)
            analyses.append(Analysis(
                lemma=lemma, pos="verb", kind="conjugate",
                kwargs=canon, segments=segs, hypothetical=hyp,
            ))

    # converb (fiil → zarf-fiil)
    for raw_kwargs in _enumerate_converb(surface, stem):
        canon = _canonicalize("converb", raw_kwargs)
        key = ("converb", lemma, _kwargs_key(canon))
        if key in seen:
            continue
        seen.add(key)
        raw = dict(canon)
        if _verify("converb", lemma, raw, surface):
            segs = _segment("converb", lemma, canon, surface)
            analyses.append(Analysis(
                lemma=lemma, pos="verb", kind="converb",
                kwargs=canon, segments=segs, hypothetical=hyp,
            ))

    # participle (fiil → fiilimsi)
    for raw_kwargs in _enumerate_participle(surface, stem):
        canon = _canonicalize("participle", raw_kwargs)
        key = ("participle", lemma, _kwargs_key(canon))
        if key in seen:
            continue
        seen.add(key)
        raw = _raw_from_canon("participle", canon)
        if _verify("participle", lemma, raw, surface):
            segs = _segment("participle", lemma, canon, surface)
            analyses.append(Analysis(
                lemma=lemma, pos="verb", kind="participle",
                kwargs=canon, segments=segs, hypothetical=hyp,
            ))


def _try_noun(surface: str, lemma: str, stem: str,
              analyses: list[Analysis], seen: set[tuple],
              roots: Collection[str] | None) -> None:
    """İsim hipotezlerini üret, doğrula, ekle."""
    # roots verilmişse yalnız roots'taki lemmaları işle
    if roots is not None and lemma not in roots:
        return
    hyp = roots is None

    # decline
    for raw_kwargs in _enumerate_decline(surface, stem):
        canon = _canonicalize("decline", raw_kwargs)
        key = ("decline", lemma, _kwargs_key(canon))
        if key in seen:
            continue
        seen.add(key)
        raw = _raw_from_canon("decline", canon)
        if _verify("decline", lemma, raw, surface):
            segs = _segment("decline", lemma, canon, surface)
            analyses.append(Analysis(
                lemma=lemma, pos="noun", kind="decline",
                kwargs=canon, segments=segs, hypothetical=hyp,
            ))

    # copula
    for raw_kwargs in _enumerate_copula(surface, stem):
        canon = _canonicalize("copula", raw_kwargs)
        key = ("copula", lemma, _kwargs_key(canon))
        if key in seen:
            continue
        seen.add(key)
        raw = _raw_from_canon("copula", canon)
        if _verify("copula", lemma, raw, surface):
            segs = _segment("copula", lemma, canon, surface)
            analyses.append(Analysis(
                lemma=lemma, pos="noun", kind="copula",
                kwargs=canon, segments=segs, hypothetical=hyp,
            ))
