"""Olasılıksal disambiguation — aday sıralama + güven (Faz 2b, SPEC disambiguation-spec.md).

`analyze` bir yüzey için birden çok çözümleme döndürebilir. Bu modül adayları olabilirlik
sırasına koyar (dilbilimsel öncelik + opsiyonel sıklık) ve normalize güven (olasılık) verir.

DEĞİŞMEZ (SPEC §0): OPT-IN, geriye-uyumlu. `analyze` imzası/sırası DOKUNULMAZ; sıralamayı
isteyen bu modülü çağırır. Girdi mutasyonu YOK (yeni liste döndürülür). `freq=None` →
sıklık terimi etkisiz, sıralama tümüyle dilbilimsel önceliklere düşer.

Kullanım:
    from turkgram import analysis, disambiguation, lexicon
    cands = analysis.analyze("gelin", roots=lexicon.load())
    ranked = disambiguation.rank(cands, pos=lexicon.pos_map())
    for a, p in disambiguation.disambiguate(cands, pos=lexicon.pos_map()):
        print(a.lemma, a.kind, round(p, 3))
"""
from __future__ import annotations

import math
from typing import Any, Callable, Mapping, Sequence

from .analysis import Analysis, _sort_key

# Kind sınıfları (SPEC §1.2)
_VERB_KINDS: frozenset[str] = frozenset({"conjugate", "converb", "participle"})
_NOMINAL_KINDS: frozenset[str] = frozenset({"decline", "copula"})
_NOMINAL_POS: frozenset[str] = frozenset({"noun", "adj", "adv", "pron", "num",
                                          "postp", "conj", "det", "interj", "dup", "ques"})

# Yalın-biçim izole önceliği (SPEC §1.3)
_KIND_PRIOR: dict[str, int] = {
    "decline": 2, "conjugate": 2, "copula": 1, "participle": 0, "converb": 0,
}

# Güven skaleri ağırlıkları (SPEC §2) — yalnız gösterim; SIRA §1 tuple'ından.
_W_FREQ, _W_POS, _W_KIND, _W_MORPH = 100.0, 10.0, 3.0, 1.0

_PosArg = Mapping[str, str] | Callable[[str], str | None] | None
_FreqArg = Mapping[str, float] | None


def _pos_of(pos: _PosArg, lemma: str) -> str | None:
    if pos is None:
        return None
    if callable(pos):
        return pos(lemma)
    return pos.get(lemma)


def _freq_score(freq: _FreqArg, lemma: str) -> float:
    if freq is None:
        return 0.0
    return float(freq.get(lemma, 0.0))


def _pos_consistency(a: Analysis, pos: _PosArg) -> int:
    """+1 tutarlı / 0 bilinmiyor / -1 tutarsız (SPEC §1.2)."""
    p = _pos_of(pos, a.lemma)
    if p is None:
        return 0
    if p == "verb":
        return 1 if a.kind in _VERB_KINDS else -1
    if p in _NOMINAL_POS:
        return 1 if a.kind in _NOMINAL_KINDS else -1
    return 0


def _rank_key(a: Analysis, freq: _FreqArg, pos: _PosArg) -> tuple:
    """Best-first artan tuple anahtarı (SPEC §1)."""
    return (
        -_freq_score(freq, a.lemma),
        -_pos_consistency(a, pos),
        -_KIND_PRIOR.get(a.kind, 0),
        len(a.segments),
        _sort_key(a),
    )


def rank(analyses: Sequence[Analysis], *, freq: _FreqArg = None,
         pos: _PosArg = None) -> list[Analysis]:
    """Adayları olabilirlik sırasına koy (best-first). Yeni liste döndürür.

    Args:
        analyses: `analyze` çıktısı (değiştirilmez).
        freq: lemma→ağırlık (yüksek=daha olası). None → sıklık terimi etkisiz.
        pos: lemma→POS map/callable (ör. `lexicon.pos_map()`). None → POS sinyali yok.

    Returns:
        Sıralı yeni Analysis listesi (SPEC §1 lexicographic öncelik).
    """
    return sorted(analyses, key=lambda a: _rank_key(a, freq, pos))


def _raw_score(a: Analysis, freq: _FreqArg, pos: _PosArg) -> float:
    """Güven softmax'ı için skaler ham puan (SPEC §2). Yalnız gösterim."""
    return (
        _W_FREQ * math.log1p(_freq_score(freq, a.lemma))
        + _W_POS * _pos_consistency(a, pos)
        + _W_KIND * _KIND_PRIOR.get(a.kind, 0)
        - _W_MORPH * len(a.segments)
    )


def disambiguate(analyses: Sequence[Analysis], *, freq: _FreqArg = None,
                 pos: _PosArg = None) -> list[tuple[Analysis, float]]:
    """Best-first sıralı (Analysis, güven) çiftleri. Güven ∈ [0,1], toplam ≈ 1 (softmax).

    Tek aday → güven 1.0. Eşit ham puan → eşit güven. Boş girdi → [].
    """
    ranked = rank(analyses, freq=freq, pos=pos)
    if not ranked:
        return []
    raws = [_raw_score(a, freq, pos) for a in ranked]
    m = max(raws)
    exps = [math.exp(r - m) for r in raws]  # sayısal kararlılık
    total = sum(exps)
    return [(a, e / total) for a, e in zip(ranked, exps)]
