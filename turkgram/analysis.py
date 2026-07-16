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

from .morphology import conjugate
from .morphology_noun import decline, copula
from .nonfinite import converb, participle, converb_casina, converb_ken
from .adjective import intensify, diminutive, _VALID_SUFFIXES as _ADJ_SUFFIXES
from .number import ordinal as _ordinal, distributive as _distributive
from .analysis_candidates import (
    _VOICE_CHAINS,
    _root_candidates,
    _enumerate_conjugate, _enumerate_decline, _enumerate_copula,
    _enumerate_converb, _enumerate_participle, _enumerate_casina, _enumerate_ken,
)

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
    chain: tuple = ()   # tuple["Analysis", ...] — pedagoji zinciri; boş = tek katman


# ---------------------------------------------------------------------------
# Sabitler (orchestration katmanı)
# ---------------------------------------------------------------------------
_POS = ("verb", "noun", "adj", "num", "conj")
_KINDS = ("conjugate", "decline", "copula", "converb",
          "converb_casina", "converb_ken", "participle",
          "intensify", "diminutive", "ordinal", "distributive",
          "conjunction", "derivation")

# _KIND_FUNCS özel sabit (SPEC §Adım 3)
_KIND_FUNCS: dict[str, Any] = {
    "conjugate": conjugate,
    "decline": decline,
    "copula": copula,
    "converb": converb,
    "converb_casina": converb_casina,
    "converb_ken": converb_ken,
    "participle": participle,
}


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
    is_ken = kwargs.get("aux") == "ken"
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
        elif is_ken and k in ("person", "question"):
            pass  # -ken KİŞİSİZ + soru YOK → eksenleri at
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


def _canon_casina(kwargs: dict[str, Any]) -> dict[str, Any]:
    """base daima; negative yalnız True iken (converb kind emsali + conjugate negative)."""
    out: dict[str, Any] = {"base": kwargs["base"]}
    if kwargs.get("negative"):
        out["negative"] = True
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
    if kind == "converb_casina":
        return _canon_casina(kwargs)
    if kind == "converb_ken":
        return _canon_casina(kwargs)  # aynı şema: base daima, negative yalnız True
    if kind == "participle":
        return _canon_participle(kwargs)
    return dict(kwargs)


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
        elif kind == "converb_casina":
            return fn(lemma, base=kwargs["base"], negative=kwargs.get("negative", False))
        elif kind == "converb_ken":
            return fn(lemma, base=kwargs["base"], negative=kwargs.get("negative", False))
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
    "aux:ken": "ken",
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
    elif kind in ("converb_casina", "converb_ken"):
        raw.setdefault("negative", False)  # base canon'da daima var
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


def _seg_voice(
    lemma: str, surface: str, vc: tuple[str, ...],
    stem_len: int, asp_kw: dict[str, Any],
) -> tuple[list[tuple[str, str]], int]:
    """Ses zinciri segmentleri + voiced_end döndür."""
    vc_segs: list[tuple[str, str]] = []
    prev_len = stem_len
    for i, voice_elem in enumerate(vc):
        voiced = _imp2sg(lemma, voice_chain=list(vc[:i + 1]), **asp_kw)
        if voiced is None:
            break
        seg_surf = surface[prev_len:len(voiced)]
        vc_segs.append((seg_surf, voice_elem))
        prev_len = len(voiced)
    return vc_segs, prev_len


def _seg_mod(
    lemma: str, surface: str, vc: tuple[str, ...],
    voiced_end: int, negative: bool, ability: bool, asp_kw: dict[str, Any],
) -> tuple[list[tuple[str, str]], int]:
    """Abil/neg/AmA segmentleri + mod_end döndür."""
    mod_segs: list[tuple[str, str]] = []
    mod_end = voiced_end
    vc_kw: dict[str, Any] = {"voice_chain": list(vc)} if vc else {}
    if ability and negative:
        ama_form = _imp2sg(lemma, negative=True, ability=True, **vc_kw, **asp_kw)
        if ama_form is not None:
            mod_segs.append((surface[voiced_end:len(ama_form)], "AmA"))
            mod_end = len(ama_form)
    elif ability:
        abil_form = _imp2sg(lemma, ability=True, **vc_kw, **asp_kw)
        if abil_form is not None:
            mod_segs.append((surface[voiced_end:len(abil_form)], "Abil"))
            mod_end = len(abil_form)
    elif negative:
        neg_form = _imp2sg(lemma, negative=True, **vc_kw, **asp_kw)
        if neg_form is not None:
            mod_segs.append((surface[voiced_end:len(neg_form)], "mA"))
            mod_end = len(neg_form)
    return mod_segs, mod_end


def _seg_tense_aux(
    lemma: str, surface: str, tense: str, aux: Any,
    vc: tuple[str, ...], mod_end: int,
    negative: bool, ability: bool, aspect: Any,
) -> tuple[list[tuple[str, str]], list[tuple[str, str]], int]:
    """Tense + aux segmentleri + aux_end döndür."""
    vc_list = list(vc) if vc else None
    t3sg_no_aux = _gen_with_raw("conjugate", lemma, {
        "tense": tense, "person": None,
        "negative": negative, "ability": ability,
        "question": False, "aux": None,
        "aspect": aspect, "voice_chain": vc_list,
    }) or surface

    tense_segs: list[tuple[str, str]] = []
    tense_surf = surface[mod_end:len(t3sg_no_aux)]
    if tense_surf:
        tense_segs.append((tense_surf, _get_label("tense", tense)))

    aux_segs: list[tuple[str, str]] = []
    aux_end = len(t3sg_no_aux)
    if aux:
        t3sg_with_aux = _gen_with_raw("conjugate", lemma, {
            "tense": tense, "person": None,
            "negative": negative, "ability": ability,
            "question": False, "aux": aux,
            "aspect": aspect, "voice_chain": vc_list,
        })
        if t3sg_with_aux is not None:
            aux_surf = surface[aux_end:len(t3sg_with_aux)]
            if aux_surf:
                aux_segs.append((aux_surf, _get_label("aux", aux)))
            aux_end = len(t3sg_with_aux)

    return tense_segs, aux_segs, aux_end


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
    vc: tuple[str, ...] = tuple(voice_chain) if voice_chain else ()
    asp_kw: dict[str, Any] = {"aspect": aspect} if aspect else {}

    # 1. Bare stem
    bare = _imp2sg(lemma, **asp_kw)
    stem_len = len(bare) if bare is not None else len(surface)

    # 2. Ses zinciri
    vc_segs, voiced_end = _seg_voice(lemma, surface, vc, stem_len, asp_kw)

    # 3. Ability / negative modifiers
    mod_segs, mod_end = _seg_mod(lemma, surface, vc, voiced_end, negative, ability, asp_kw)

    # 4+5. Tense + aux
    tense_segs, aux_segs, aux_end = _seg_tense_aux(
        lemma, surface, tense, aux, vc, mod_end, negative, ability, aspect,
    )

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
    """
    Ek-fiil segmentasyonu — build-up peeling; eksenler yüzey sırasıyla eklenir.

    Yüzey morfem sırası: KÖK | case | mI(soru) | aux | person
    (evde miydim = ev + de + mi + ydi + m). Her sınır oracle'la ölçülür:
    bir sonraki ekseni açıp uzunluk farkını al.
    """
    aux = canon.get("aux", None)
    person = canon.get("person", "3sg")
    case = canon.get("case", None)
    question = canon.get("question", False)
    possessive = canon.get("possessive", None)
    number = canon.get("number", "sg")

    def _cop(*, aux_: Any = None, question_: bool = False,
             person_: str = "3sg") -> str | None:
        return _gen_with_raw("copula", lemma, {
            "aux": aux_, "person": person_, "number": number,
            "possessive": possessive, "case": case, "question": question_,
        })

    # KÖK = lemma (bare present -dir tabanını KULLANMA: copula(None,3sg)→"evdir").
    segs: list[tuple[str, str]] = [(surface[:len(lemma)], "KÖK")]
    pos = len(lemma)

    # 1. case — copula case-çekimli isim üstüne kurulur; sınırı decline ölçer
    if case and case != "nom":
        cf = _gen_with_raw("decline", lemma, {
            "number": number, "possessive": possessive, "case": case,
        })
        if cf is not None:
            seg = surface[pos:len(cf)]
            if seg:
                segs.append((seg, _get_label("case", case)))
            pos = len(cf)

    # 2. soru (mI) — aux'tan ÖNCE gelir (evde mi + ydi)
    if question:
        qf = _cop(question_=True)
        if qf is not None:
            seg = surface[pos:len(qf)]
            if seg:
                segs.append((seg, _get_label("question", True)))
            pos = len(qf)

    # 3. aux (ekfiil zaman/kip)
    if aux:
        af = _cop(aux_=aux, question_=question)
        if af is not None:
            seg = surface[pos:len(af)]
            if seg:
                segs.append((seg, _get_label("aux", aux)))
            pos = len(af)

    # 4. person (3sg eksiz)
    if person and person != "3sg":
        person_surf = surface[pos:]
        if person_surf:
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


def _segment_converb_casina(lemma: str, canon: dict[str, Any],
                            surface: str) -> tuple[Segment, ...]:
    """-cAsInA segmentasyonu — DELEGASYON (A3 emsali): finit tabanı conjugate
    segmentasyonuna ver, sonra tek cAsInA dilimini ekle. Taban = conjugate(base,3sg,neg)."""
    base = canon["base"]
    negative = canon.get("negative", False)
    base_form = _gen_with_raw("conjugate", lemma, {
        "tense": base, "person": None, "negative": negative,
        "ability": False, "question": False, "aux": None,
        "aspect": None, "voice_chain": None,
    })
    if base_form is None or not surface.startswith(base_form):
        return _segs_to_tuple([(surface, "KÖK")])  # güvenli geri-düşüş
    base_canon: dict[str, Any] = {"tense": base, "person": "3sg"}
    if negative:
        base_canon["negative"] = True
    base_segs = _segment_conjugate(lemma, base_canon, base_form)
    pairs = [(s.surface, s.label) for s in base_segs]
    suffix = surface[len(base_form):]
    if suffix:
        pairs.append((suffix, "cAsInA"))
    return _segs_to_tuple(pairs)


def _segment_converb_ken(lemma: str, canon: dict[str, Any],
                         surface: str) -> tuple[Segment, ...]:
    """Fiil -ken segmentasyonu — DELEGASYON (casina emsali): finit tabanı conjugate
    segmentasyonuna ver + tek 'ken' dilimi. Glide YOK (finit taban ünsüz-final)."""
    base = canon["base"]
    negative = canon.get("negative", False)
    base_form = _gen_with_raw("conjugate", lemma, {
        "tense": base, "person": None, "negative": negative,
        "ability": False, "question": False, "aux": None,
        "aspect": None, "voice_chain": None,
    })
    if base_form is None or not surface.startswith(base_form):
        return _segs_to_tuple([(surface, "KÖK")])
    base_canon: dict[str, Any] = {"tense": base, "person": "3sg"}
    if negative:
        base_canon["negative"] = True
    base_segs = _segment_conjugate(lemma, base_canon, base_form)
    pairs = [(s.surface, s.label) for s in base_segs]
    suffix = surface[len(base_form):]
    if suffix:
        pairs.append((suffix, "ken"))
    return _segs_to_tuple(pairs)


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
    if kind == "converb_casina":
        return _segment_converb_casina(lemma, canon_kwargs, surface_token)
    if kind == "converb_ken":
        return _segment_converb_ken(lemma, canon_kwargs, surface_token)
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
            hyp = roots is None
            in_roots = roots is None or lemma in roots
            if not in_roots:
                continue

            # 1a. Fiil gövdesi → conjugate(question=True)
            if "verb" in kind_hints:
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

            # 1b. İsim gövdesi → copula(question=True)  [nominal ekfiil soru grubu]
            if "noun" in kind_hints:
                for raw_kwargs in _enumerate_copula(surface_full, lemma):
                    if not raw_kwargs.get("question"):
                        continue
                    canon = _canonicalize("copula", raw_kwargs)
                    raw = _raw_from_canon("copula", canon)
                    if _verify("copula", lemma, raw, surface_full):
                        segs = _segment("copula", lemma, canon, surface_full)
                        results.append(Analysis(
                            lemma=lemma, pos="noun", kind="copula",
                            kwargs=canon, segments=segs, hypothetical=hyp,
                        ))

    # 2. Birleşik çok-token fiil (SPEC §8.2): değişmez nominal önek (çok-kelimeli
    #    olabilir) + son token çekimli yardımcı/leksik fiil. "aday oldu" → "aday olmak";
    #    "göz ardı etti" → "göz ardı etmek". Precision roots-garantili (§8.1).
    if len(tokens) >= 2:
        prefix_tok = " ".join(tokens[:-1])
        body_tok = tokens[-1]
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
            *, roots: Collection[str] | None = None,
            max_derivation_depth: int = 1) -> list[Analysis]:
    """
    Yüzey biçimi → olası Analysis listesi.

    Args:
        surface: Çözümlenecek yüzey biçim (tek ya da çok-token).
        pos: "verb" | "noun" | "adj" | "num" | None (tümü).
        roots: Lemma kümesi. Verilmişse lemma∉roots elenir (hypothetical=False);
               verilmemişse hepsi hypothetical=True.
        max_derivation_depth: Zincirli türetme derinliği. 1=tek katman (varsayılan,
            mevcut davranış). 2+ → _try_derivation_chain devreye girer. Araştırma
            modu için 10+ verilebilir.

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

    # Çok-token: yalnız tanınan kalıplar (soru grubu + birleşik çok-token fiil, SPEC §8/§8.2)
    if len(tokens) > 1:
        results = _analyze_multi_token(tokens, roots)
        # Bileşik sayı formları (yirmi birinci, kırk ikişer)
        num_analyses: list[Analysis] = []
        num_seen: set[tuple] = set()
        _try_number_all(surface, num_analyses, num_seen, roots)
        results = sorted(set_dedup(results + num_analyses), key=_sort_key)
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

    # Adım 4: Sıfat çözümlemesi (intensify + diminutive) — roots sağlandıysa
    # Roots'taki her kök için oracle çağrısı; precision roots-garantili.
    if roots is not None and pos in (None, "adj"):
        _try_adj_all(surface_token, roots, analyses, seen)

    # Adım 5: Bağlaç çözümlemesi (kapalı liste, oracle dışı)
    if pos in (None, "conj"):
        _try_conjunction_all(surface_token, analyses, seen)

    # Adım 6: Sayı çözümlemesi (ordinal + distributive)
    if pos in (None, "num"):
        _try_number_all(surface_token, analyses, seen, roots)

    # Adım 7: Yapım eki çözümlemesi (tek katman, fiilimsi + çatı dışlı)
    if pos in (None, "noun", "verb", "adj"):
        _try_derivation_all(surface_token, analyses, seen, roots=roots)
        if max_derivation_depth >= 2:
            _try_derivation_chain(
                surface_token, analyses, seen,
                roots=roots, max_depth=max_derivation_depth,
            )

    return analyses


_ENUMERATE_FN: dict[str, Any] = {
    "conjugate": lambda surface, stem, lemma: _enumerate_conjugate(surface, stem, lemma),
    "converb":   lambda surface, stem, lemma: _enumerate_converb(surface, stem),
    "converb_casina": lambda surface, stem, lemma: _enumerate_casina(surface, stem),
    "converb_ken": lambda surface, stem, lemma: _enumerate_ken(surface, stem),
    "participle": lambda surface, stem, lemma: _enumerate_participle(surface, stem),
    "decline":   lambda surface, stem, lemma: _enumerate_decline(surface, stem),
    "copula":    lambda surface, stem, lemma: _enumerate_copula(surface, stem),
}


def _process_kind(
    kind: str, pos: str, surface: str, lemma: str, stem: str,
    analyses: list[Analysis], seen: set[tuple], hyp: bool,
) -> None:
    """Tek kind için: enumerate → canon → dedup → verify → segment → Analysis ekle."""
    enum_fn = _ENUMERATE_FN[kind]
    for raw_kwargs in enum_fn(surface, stem, lemma):
        canon = _canonicalize(kind, raw_kwargs)
        key = (kind, lemma, _kwargs_key(canon))
        if key in seen:
            continue
        seen.add(key)
        raw = _raw_from_canon(kind, canon) if kind != "converb" else dict(canon)
        if _verify(kind, lemma, raw, surface):
            segs = _segment(kind, lemma, canon, surface)
            analyses.append(Analysis(
                lemma=lemma, pos=pos, kind=kind,
                kwargs=canon, segments=segs, hypothetical=hyp,
            ))


def _try_verb(surface: str, lemma: str, stem: str,
              analyses: list[Analysis], seen: set[tuple],
              roots: Collection[str] | None) -> None:
    """Fiil hipotezlerini üret, doğrula, ekle."""
    if roots is not None and lemma not in roots:
        return
    hyp = roots is None
    for kind in ("conjugate", "converb", "converb_casina", "converb_ken", "participle"):
        _process_kind(kind, "verb", surface, lemma, stem, analyses, seen, hyp)


def _try_noun(surface: str, lemma: str, stem: str,
              analyses: list[Analysis], seen: set[tuple],
              roots: Collection[str] | None) -> None:
    """İsim hipotezlerini üret, doğrula, ekle."""
    if roots is not None and lemma not in roots:
        return
    hyp = roots is None
    for kind in ("decline", "copula"):
        _process_kind(kind, "noun", surface, lemma, stem, analyses, seen, hyp)


# ---------------------------------------------------------------------------
# Sayı çözümlemesi (Faz 5 D3) — kapalı-küme kök + oracle
# ---------------------------------------------------------------------------
_NUMBER_SIMPLE_ROOTS: frozenset[str] = frozenset({
    "sıfır", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz",
    "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan",
    "yüz", "bin", "milyon", "milyar",
})

_NUM_UNVOICE: dict[str, str] = {"d": "t", "c": "ç", "b": "p", "ğ": "k"}


def _num_unvoice(s: str) -> str:
    """Gövde-sonu sesini sertleştir (distributif/ordinal ters-mutasyonu için)."""
    if not s:
        return s
    return s[:-1] + _NUM_UNVOICE.get(s[-1], s[-1])


def _ordinal_root_candidates(last_word: str) -> list[str]:
    """Son sözcük için olası ordinal kök adayları (sesletim önce/sonra)."""
    cands = []
    if re.search(r"nc[ıiuü]$", last_word):           # ünlü-final: ikinci, altıncı
        cands.append(last_word[:-3])
    if re.search(r"[ıiuü]nc[ıiuü]$", last_word):     # ünsüz-final: birinci, dördüncü
        raw = last_word[:-4]
        cands.extend([raw, _num_unvoice(raw)])
    return cands


def _distributive_root_candidates(last_word: str) -> list[str]:
    """Son sözcük için olası distributif kök adayları."""
    cands = []
    if re.search(r"[şs][ae]r$", last_word):           # ünlü-final: ikişer, altışar
        cands.append(last_word[:-3])
    if re.search(r"[ae]r$", last_word):               # ünsüz-final: birer, dörder, onar
        raw = last_word[:-2]
        cands.extend([raw, _num_unvoice(raw)])
    return cands


def _template_to_allomorphs(template: str) -> list[str]:
    """Arşifonem template → tüm olası realize biçimler.

    Birden fazla arşifonem içeren template'ler için kartezyen çarpım:
    I→[ı,i,u,ü], A→[a,e], C→[c,ç], D→[d,t], G→[g,k].
    Küçük küme (max ~32 varyant / suffix) — performans sorunu yok.
    """
    import itertools
    _ARCH: dict[str, list[str]] = {
        "I": ["ı", "i", "u", "ü"],
        "A": ["a", "e"],
        "C": ["c", "ç"],
        "D": ["d", "t"],
        "G": ["g", "k"],
    }
    positions: list[list[str]] = []
    for ch in template:
        positions.append(_ARCH.get(ch, [ch]))
    return ["".join(combo) for combo in itertools.product(*positions)]


def _strip_derivation(
    surface: str,
    label: str,
    src_pos: str,
) -> list[str]:
    """Yüzeyden derivasyon suffix'ini soy → olası kök adayları listesi.

    Ters harmoni: suffix'in her ünlü alloformunu dener.
    Fiil çıktılı suffix (is_verb_output=True, isim→fiil): mastar -mAk soyulur → gövde.
    Ünlü-başlı suffix + kaynaştırma -y-: son -y de atılır.
    Başarısız soyma → boş liste (oracle zaten false döner → precision güvenli).
    """
    from .derivation import _NOUN_TO_NOUN, _NOUN_TO_VERB, _VERB_TO_NOUN

    # Suffix tablolarından template + meta bul (label ile eşleştir)
    all_specs = _NOUN_TO_NOUN + _NOUN_TO_VERB + _VERB_TO_NOUN
    template: str | None = None
    vowel_initial: bool = False
    is_verb_output: bool = False
    for (cat, lbl, tmpl, vinit, pv) in all_specs:
        if lbl == label:
            template = tmpl
            vowel_initial = vinit
            is_verb_output = pv
            break
    if template is None:
        return []

    # isim→fiil suffix (is_verb_output=True): surface mastar biçiminde (-mAk)
    work = surface
    if is_verb_output:
        for ending in ("mak", "mek"):
            if work.endswith(ending):
                work = work[: -len(ending)]
                break
        else:
            return []  # -mAk yoksa bu surface fiil türevi olamaz

    suffixes: list[str] = _template_to_allomorphs(template)

    candidates: list[str] = []
    for suf in suffixes:
        if not work.endswith(suf):
            continue
        root = work[: -len(suf)]
        if not root:
            continue
        # Kaynaştırma -y- geri al (ünlü-başlı suffix + ünlü-final kök)
        if vowel_initial and root.endswith("y"):
            candidates.append(root[:-1])  # y'siz kök
        candidates.append(root)
    return candidates


def _strip_one_layer(
    surface: str,
) -> list[tuple[str, str, str, str]]:
    """Verilen yüzeyden tek katman leksik suffix soy.

    Returns:
        List of (stem, label, suffix_surface, src_pos).
        Boş liste = hiç eşleşme yok.
    """
    from .derivation import _LEXICAL_SUFFIXES

    results: list[tuple[str, str, str, str]] = []
    for (cat, label, src_pos) in _LEXICAL_SUFFIXES:
        for stem in _strip_derivation(surface, label, src_pos):
            if not stem:
                continue
            suffix_surface = surface[len(stem):]
            results.append((stem, label, suffix_surface, src_pos))
    return results


def _try_derivation_all(
    surface: str,
    analyses: list,
    seen: set,
    roots: "set[str] | None" = None,
) -> None:
    """Tek-katman yapım eki analizi — oracle analysis-by-generation.

    _LEXICAL_SUFFIXES üzerinden döner (fiilimsi + çatı DIŞLI).
    Kök adayı → oracle doğrular (derivations() çıktısı == surface) → Analysis ekler.
    Fiil-kaynaklı isim (src_pos=verb): gövde → mastar yeniden kurulur (seç → seçmek).
    Kök filtresi §8.1: roots is not None → lemma ∉ roots → atla.
    Zincirli türetme kapsam dışı (tek katman).
    """
    from .derivation import (
        derivations as _derivations,
        _DERIVED_POS,
    )
    from .morphology import low_vowel

    for (stem, label, suffix_surface, src_pos) in _strip_one_layer(surface):
        # Fiil-kaynaklı → mastar yeniden kur (seç → seçmek)
        if src_pos == "verb":
            try:
                lemma = stem + "m" + low_vowel(stem) + "k"
            except (ValueError, IndexError):
                continue
        else:
            lemma = stem
        # §8.1 precision filtresi
        if roots is not None and lemma not in roots:
            continue
        # Oracle: derivations() ile doğrula
        try:
            derived = _derivations(lemma, src_pos)
        except Exception:
            continue
        if not derived:
            continue
        for r in derived:
            if r["form"] != surface or r["suffix"] != label:
                continue
            key = ("derivation", lemma, label)
            if key in seen:
                continue
            seen.add(key)
            derived_pos = _DERIVED_POS.get(label, "noun")
            segs = _segs_to_tuple([(stem, "kök"), (suffix_surface, label)])
            analyses.append(
                Analysis(
                    kind="derivation",
                    lemma=lemma,
                    pos=derived_pos,
                    kwargs={"suffix": label, "src_pos": src_pos},
                    segments=segs,
                    hypothetical=(roots is None),
                )
            )


def _build_chain_analysis(
    surface: str,
    chain: list,   # list[Analysis], chain[0] = en derin kök (ilk soyulan), chain[-1] = yüzeye en yakın
    top_label: str,
    top_suffix_surface: str,
    top_src_pos: str,
    top_pos: str,
    top_lemma: str,
    hypothetical: bool,
) -> "Analysis":
    """BFS zincirinden Analysis üret.

    segments: tüm katmanların segmentleri art arda düzleştirilir.
    chain: düz Analysis listesi (chain[0] = en derin kök).
    """
    from .derivation import _DERIVED_POS  # noqa: F401

    stem_surface = surface[: len(surface) - len(top_suffix_surface)]
    flat_segs: list[tuple[str, str]] = []
    if chain:
        for a in chain:
            flat_segs.extend((seg.surface, seg.label) for seg in a.segments)
        flat_segs.append((stem_surface, top_label))
        flat_segs.append((top_suffix_surface, top_label))
    else:
        flat_segs = [(stem_surface, "kök"), (top_suffix_surface, top_label)]

    return Analysis(
        kind="derivation",
        lemma=top_lemma,
        pos=top_pos,
        kwargs={"suffix": top_label, "src_pos": top_src_pos},
        segments=_segs_to_tuple(flat_segs),
        hypothetical=hypothetical,
        chain=tuple(chain),
    )


def _try_derivation_chain(
    surface: str,
    analyses: list,
    seen: set,
    roots: "set[str] | None" = None,
    max_depth: int = 5,
) -> None:
    """Zincirli leksik türetme analizi — BFS, max_depth katmana kadar.

    Tek katman (_try_derivation_all) sonuçlarını tekrar üretmez (min 2 katman).
    seen anahtarı: ("derivation_chain", surface, chain_key) — mevcut seen ile çakışmaz.
    ZİNCİR YÖN: chain[0] = en derin kök (ilk soyulan), chain[-1] = yüzeye en yakın.
    Çatı ekleri _LEXICAL_SUFFIXES dışında olduğundan otomatik dışlanır.
    """
    from collections import deque
    from .derivation import _DERIVED_POS
    from .morphology import low_vowel

    if max_depth < 2:
        return

    queue: deque = deque([(surface, [], max_depth)])

    while queue:
        current, chain_so_far, depth = queue.popleft()

        if depth == 0:
            continue

        for (stem, label, suffix_surface, src_pos) in _strip_one_layer(current):
            # Fiil-kaynaklı → mastar yeniden kur
            if src_pos == "verb":
                try:
                    lemma = stem + "m" + low_vowel(stem) + "k"
                except (ValueError, IndexError):
                    continue
            else:
                lemma = stem

            # Döngü tespiti: stem + lemma her ikisi de kontrol
            chain_lemmas = {a.lemma for a in chain_so_far}
            chain_stems = set()
            for a in chain_so_far:
                chain_stems.add(a.lemma)
                if a.kwargs.get("src_pos") == "verb" and a.lemma.endswith(("mak", "mek")):
                    chain_stems.add(a.lemma[:-3])
            if stem in chain_lemmas or lemma in chain_lemmas or stem in chain_stems:
                continue

            # Precision kontrolü
            is_hypothetical = (roots is not None and lemma not in roots)

            # Oracle doğrulama
            from .derivation import derivations as _derivations
            try:
                derived = _derivations(lemma, src_pos)
            except Exception:
                continue
            oracle_ok = any(
                r["form"] == current and r["suffix"] == label
                for r in (derived or [])
            )
            if not oracle_ok:
                continue

            # Yeni chain: bu katman + önceki zincir
            derived_pos = _DERIVED_POS.get(label, "noun")
            leaf = Analysis(
                kind="derivation",
                lemma=lemma,
                pos=derived_pos,
                kwargs={"suffix": label, "src_pos": src_pos},
                segments=_segs_to_tuple([(stem, "kök"), (suffix_surface, label)]),
                hypothetical=is_hypothetical,
            )
            new_chain = [leaf] + chain_so_far  # chain[0] = en derin (ilk soyulan)

            # Zincir en az 2 katmansa → tam analiz üret
            if len(new_chain) >= 2:
                chain_key = tuple(a.lemma for a in new_chain)
                seen_key = ("derivation_chain", surface, chain_key)
                if seen_key not in seen:
                    seen.add(seen_key)
                    top = _build_chain_analysis(
                        surface=surface,
                        chain=new_chain,
                        top_label=label,
                        top_suffix_surface=suffix_surface,
                        top_src_pos=src_pos,
                        top_pos=derived_pos,
                        top_lemma=lemma,
                        hypothetical=is_hypothetical or (roots is None),
                    )
                    analyses.append(top)

            # Daha derin araştır
            queue.append((stem, new_chain, depth - 1))


def _try_number_all(
    surface: str,
    analyses: list[Analysis],
    seen: set[tuple],
    roots: Collection[str] | None = None,
) -> None:
    """Ordinal + distributif çözümleme — kapalı küme + oracle.

    Hem tek-token (birinci) hem bileşik (yirmi birinci) çalışır.
    Bileşik: prefix boşlukla ayrılmış (yirmi), son sözcük ek alır (birinci).
    Precision: _NUMBER_SIMPLE_ROOTS kapalı-kümesi + oracle ile filtrelenir.
    roots verilirse compound_root∉roots olan analizler elenir (sıfat analizi sözleşmesiyle tutarlı).
    """
    tokens = surface.split()
    last_word = tokens[-1]
    prefix = " ".join(tokens[:-1])   # "" for single-token

    for kind, cand_fn, oracle_fn in [
        ("ordinal", _ordinal_root_candidates, _ordinal),
        ("distributive", _distributive_root_candidates, _distributive),
    ]:
        for cand in cand_fn(last_word):
            if cand not in _NUMBER_SIMPLE_ROOTS:
                continue
            compound_root = (prefix + " " + cand).strip() if prefix else cand
            if roots is not None and compound_root not in roots:
                continue
            try:
                form = oracle_fn(compound_root)
            except Exception:
                continue
            if form != surface:
                continue
            key = (kind, compound_root, frozenset())
            if key in seen:
                continue
            seen.add(key)
            # Segmentasyon: kök (voiced surface form) + ek
            root_surf = (prefix + " " + last_word[:len(cand)]).strip() if prefix else last_word[:len(cand)]
            suffix_surf = last_word[len(cand):]
            segs = _segs_to_tuple([(root_surf, "kök"), (suffix_surf, kind)])
            analyses.append(Analysis(
                lemma=compound_root,
                pos="num",
                kind=kind,
                kwargs={},
                segments=segs,
                hypothetical=False,
            ))


def _try_conjunction_all(surface: str, analyses: list[Analysis], seen: set[tuple]) -> None:
    """Bağlaç çözümlemesi — oracle dışı, kapalı-liste.

    Yalnız 'de' ve 'da' tam-token eşleşmesinde tetiklenir.
    Bilinçli belirsizlik: 'de' = bağlaç VE demek imp-2sg.
    """
    if surface not in ("de", "da"):
        return
    key = ("conjunction", "de", frozenset())
    if key in seen:
        return
    seen.add(key)
    analyses.append(Analysis(
        lemma="de",
        pos="conj",
        kind="conjunction",
        kwargs={},
        segments=_segs_to_tuple([(surface, "conj")]),
        hypothetical=False,
    ))


def _try_adj_all(
    surface: str, roots: Collection[str],
    analyses: list[Analysis], seen: set[tuple],
) -> None:
    """§Sifat çözümleme (Faz 3 C2) — analysis-by-generation.

    roots'taki her lemma için:
    - intensify(lemma) == surface → Analysis(kind='intensify')
    - diminutive(lemma, suffix) == surface → Analysis(kind='diminutive', suffix=suffix)

    Precision: roots-garantili (roots None ise çağrılmaz).
    """
    for lemma in roots:
        # intensify
        try:
            form = intensify(lemma)
        except Exception:
            form = None
        if form is not None and form == surface:
            key = ("intensify", lemma, ())
            if key not in seen:
                seen.add(key)
                segs = _segs_to_tuple([
                    (form[:len(form) - len(lemma)], "pekıştirme"),
                    (lemma, "kök"),
                ])
                analyses.append(Analysis(
                    lemma=lemma, pos="adj", kind="intensify",
                    kwargs={}, segments=segs, hypothetical=False,
                ))

        # diminutive: 3 ek
        for suffix in _ADJ_SUFFIXES:
            try:
                form = diminutive(lemma, suffix)
            except Exception:
                form = None
            if form is not None and form == surface:
                kwargs = {"suffix": suffix}
                key = ("diminutive", lemma, (("suffix", suffix),))
                if key not in seen:
                    seen.add(key)
                    # Segmentasyon: kök + ek
                    root_part = lemma
                    if lemma.endswith("k") and suffix == "-CIk":
                        root_part = lemma[:-1]  # k düştc
                    suffix_surf = form[len(root_part):]
                    segs = _segs_to_tuple([
                        (root_part, "kök"),
                        (suffix_surf, suffix),
                    ])
                    analyses.append(Analysis(
                        lemma=lemma, pos="adj", kind="diminutive",
                        kwargs=kwargs, segments=segs, hypothetical=False,
                    ))
