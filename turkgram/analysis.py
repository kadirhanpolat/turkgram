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
from .nonfinite import converb, participle
from .analysis_candidates import (
    _VOICE_CHAINS,
    _root_candidates,
    _enumerate_conjugate, _enumerate_decline, _enumerate_copula,
    _enumerate_converb, _enumerate_participle,
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


# ---------------------------------------------------------------------------
# Sabitler (orchestration katmanı)
# ---------------------------------------------------------------------------
_POS = ("verb", "noun")
_KINDS = ("conjugate", "decline", "copula", "converb", "participle")

# _KIND_FUNCS özel sabit (SPEC §Adım 3)
_KIND_FUNCS: dict[str, Any] = {
    "conjugate": conjugate,
    "decline": decline,
    "copula": copula,
    "converb": converb,
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

    # Çok-token: yalnız tanınan kalıplar (soru grubu + birleşik çok-token fiil, SPEC §8/§8.2)
    if len(tokens) > 1:
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


_ENUMERATE_FN: dict[str, Any] = {
    "conjugate": lambda surface, stem, lemma: _enumerate_conjugate(surface, stem, lemma),
    "converb":   lambda surface, stem, lemma: _enumerate_converb(surface, stem),
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
    for kind in ("conjugate", "converb", "participle"):
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
