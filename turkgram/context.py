"""Cümle-bağlamı disambiguation — kural-tabanlı sözdizimsel katman (Faz 2b).

SPEC: `spec/sentence-disambiguation-spec.md`. İzole `disambiguation.rank` yalnız kelimenin
kendi adaylarına bakar; belirsizlik komşuluk kanıtıyla çözülür (ör. `üç gelin` → isim,
`ben geldim` → 1sg). Bu modül bir cümlenin token'larını yerel (±1 token + soldan en yakın
zamir/tamlayan) yüzeysel kanıtla YENİDEN sıralar. Tam ayrıştırıcı DEĞİL (sözdizimi defer).

DEĞİŞMEZ (SPEC §0): OPT-IN, geriye-uyumlu. `analyze`/izole `rank` DOKUNULMAZ. Recall-güvenli
— kurallar aday BUDAMAZ, yalnız kanıt (int) ekler; kural ateşlemezse sıralama tümüyle izole
`disambiguation._rank_key`'e düşer. Girdi mutasyonu YOK (yeni liste-listesi döndürülür).

Kullanım:
    from turkgram import analysis, context, lexicon
    roots = lexicon.load(); pm = lexicon.pos_map()
    tokens = ["üç", "gelin"]
    per_token = [analysis.analyze(t, roots=roots) for t in tokens]
    ranked = context.rank_in_context(tokens, per_token, pos=pm)
    ranked[1][0].lemma  # -> "gelin" (isim; sayı niteleyici bağlamından)
"""
from __future__ import annotations

import re
from typing import Sequence

from .analysis import Analysis, _tr_lower
from . import disambiguation as dis

# ---------------------------------------------------------------------------
# Kind aileleri (SPEC §3) — casina/ken/participle fiil-kind'ları dâhil
# ---------------------------------------------------------------------------
_VERB_KINDS: frozenset[str] = frozenset(
    {"conjugate", "converb", "converb_ken", "converb_casina", "participle"}
)
_NOMINAL_KINDS: frozenset[str] = frozenset({"decline", "copula"})
# person ekseni olan kind'lar (SPEC §3 K4): fiil çekimi + nominal ek-fiil (copula).
_K4_PERSON_KINDS: frozenset[str] = frozenset({"conjugate", "copula"})

# ---------------------------------------------------------------------------
# Kapalı kelime listeleri (SPEC §3) — leksikon-bağımsız, deterministik
# ---------------------------------------------------------------------------
_NUM_WORDS: frozenset[str] = frozenset({
    "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz", "on",
    "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan",
    "yüz", "bin", "milyon", "milyar",
})
_QUANT_WORDS: frozenset[str] = frozenset({
    "birkaç", "çok", "az", "birçok", "her", "bazı", "tüm", "bütün", "hiçbir",
    "kimi", "birtakım", "hangi", "nice", "onlarca", "yüzlerce", "binlerce",
})

# Edat → nitelediği adın kabul edilen durumları (SPEC §3 K2)
_POSTP_GOV: dict[str, frozenset[str]] = {
    "ile": frozenset({"nom", "gen"}),
    "için": frozenset({"nom", "gen"}),
    "gibi": frozenset({"nom", "gen"}),
    "kadar": frozenset({"nom", "gen", "dat"}),
    "göre": frozenset({"dat"}),
    "doğru": frozenset({"dat"}),
    "karşı": frozenset({"dat"}),
    "rağmen": frozenset({"dat"}),
    "dair": frozenset({"dat"}),
    "ilişkin": frozenset({"dat"}),
    "ait": frozenset({"dat"}),
    "değin": frozenset({"dat"}),
    "önce": frozenset({"abl"}),
    "sonra": frozenset({"abl"}),
    "beri": frozenset({"abl"}),
    "dolayı": frozenset({"abl"}),
    "ötürü": frozenset({"abl"}),
    "itibaren": frozenset({"abl"}),
    "yana": frozenset({"abl"}),
}

_QUESTION_PARTICLES: frozenset[str] = frozenset({"mı", "mi", "mu", "mü"})

# Yalın kişi zamiri → kişi (SPEC §3 K4)
_PRON_PERSON: dict[str, str] = {
    "ben": "1sg", "sen": "2sg", "o": "3sg",
    "biz": "1pl", "siz": "2pl", "onlar": "3pl",
}
# Tamlayan zamir → kabul edilen iyelik kümesi (SPEC §3 K5)
_GEN_PRON_POSS: dict[str, frozenset[str]] = {
    "benim": frozenset({"1sg"}), "senin": frozenset({"2sg"}),
    "onun": frozenset({"3sg"}), "bizim": frozenset({"1pl"}),
    "sizin": frozenset({"2pl"}), "onların": frozenset({"3sg", "3pl"}),
}

_DIGIT_RE = re.compile(r"^\d")

# Ağırlıklar (SPEC §3)
_W_K1, _W_K2_POS, _W_K2_NEG = 3, 4, 2
_W_K3, _W_K4, _W_K4_O, _W_K5 = 2, 3, 1, 3


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------
def _case_of(a: Analysis) -> str | None:
    """Nominal-kind adayının durumu; kwargs'ta yoksa nom (SPEC: nom atılır)."""
    if a.kind in _NOMINAL_KINDS:
        return a.kwargs.get("case") or "nom"
    return None


def _isolated_top(cands: Sequence[Analysis], freq, pos) -> Analysis | None:
    """Bir token'ın izole en olası okuması (komşu özelliklerini yoklamak için)."""
    if not cands:
        return None
    return dis.rank(cands, freq=freq, pos=pos)[0]


def _is_qualifier(tok: str, cands: Sequence[Analysis], freq, pos) -> bool:
    """i−1 sayı/miktar-belirteci/sıfat niteleyicisi mi (SPEC §3 K1)."""
    low = _tr_lower(tok)
    if _DIGIT_RE.match(low) or low in _NUM_WORDS or low in _QUANT_WORDS:
        return True
    top = _isolated_top(cands, freq, pos)
    if top is None or top.kind not in _NOMINAL_KINDS:
        return False
    p = dis._pos_of(pos, top.lemma)
    return p in ("adj", "num")


def _nearest_pronoun_person(i: int, tokens: Sequence[str]) -> str | None:
    """i'den soldan en yakın yalın kişi zamirinin kişisi (SPEC §3 K4)."""
    for j in range(i - 1, -1, -1):
        person = _PRON_PERSON.get(_tr_lower(tokens[j]))
        if person is not None:
            return person
    return None


def _nearest_genitive_poss(i: int, tokens: Sequence[str],
                           analyses: Sequence[Sequence[Analysis]],
                           freq, pos) -> frozenset[str] | None:
    """i'den soldan en yakın tamlayan (zamir veya ad+gen) → kabul iyelik kümesi (K5)."""
    for j in range(i - 1, -1, -1):
        poss = _GEN_PRON_POSS.get(_tr_lower(tokens[j]))
        if poss is not None:
            return poss
        top = _isolated_top(analyses[j], freq, pos)
        if top is not None and _case_of(top) == "gen":
            return frozenset({"3sg", "3pl"})
    return None


# ---------------------------------------------------------------------------
# Kanıt kuralları
# ---------------------------------------------------------------------------
def _k1(a: Analysis, i: int, tokens, analyses, freq, pos) -> int:
    """Niteleyici + ad → i nominal (SPEC §3 K1)."""
    if i == 0 or not _is_qualifier(tokens[i - 1], analyses[i - 1], freq, pos):
        return 0
    if a.kind in _NOMINAL_KINDS:
        return _W_K1
    if a.kind in _VERB_KINDS:
        return -_W_K1
    return 0


def _k2(a: Analysis, i: int, tokens, analyses, freq, pos) -> int:
    """Edat yönetimi → i belirli durumda nominal (SPEC §3 K2)."""
    if i + 1 >= len(tokens):
        return 0
    gov = _POSTP_GOV.get(_tr_lower(tokens[i + 1]))
    if gov is None or a.kind not in _NOMINAL_KINDS:
        return 0
    return _W_K2_POS if _case_of(a) in gov else -_W_K2_NEG


def _k3(a: Analysis, i: int, tokens, analyses, freq, pos) -> int:
    """Ayrı soru parçacığı mI → i question=False (SPEC §3 K3)."""
    if i + 1 >= len(tokens):
        return 0
    if _tr_lower(tokens[i + 1]) not in _QUESTION_PARTICLES:
        return 0
    if a.kind not in ("conjugate", "copula"):
        return 0
    return _W_K3 if not a.kwargs.get("question", False) else -_W_K3


def _k4(a: Analysis, i: int, tokens, analyses, freq, pos) -> int:
    """Özne–yüklem kişi uyumu (SPEC §3 K4)."""
    person = _nearest_pronoun_person(i, tokens)
    if person is None or a.kind not in _K4_PERSON_KINDS:
        return 0
    a_person = a.kwargs.get("person")
    if a_person is None:
        return 0
    w = _W_K4_O if person == "3sg" else _W_K4
    return w if a_person == person else -1


def _k5(a: Analysis, i: int, tokens, analyses, freq, pos) -> int:
    """Tamlayan–iyelik uyumu (SPEC §3 K5)."""
    poss_set = _nearest_genitive_poss(i, tokens, analyses, freq, pos)
    if poss_set is None:
        return 0
    if a.kind in _NOMINAL_KINDS:
        return _W_K5 if a.kwargs.get("possessive") in poss_set else -1
    if a.kind in _VERB_KINDS:
        return -1
    return 0


_RULES = (_k1, _k2, _k3, _k4, _k5)


def context_evidence(a: Analysis, i: int, tokens: Sequence[str],
                     analyses: Sequence[Sequence[Analysis]],
                     *, freq=None, pos=None) -> int:
    """Token i'nin adayı `a` için sözdizimsel kanıt toplamı (SPEC §3). Yüksek = daha olası."""
    return sum(rule(a, i, tokens, analyses, freq, pos) for rule in _RULES)


# ---------------------------------------------------------------------------
# Ana arayüz (SPEC §1, §2)
# ---------------------------------------------------------------------------
def rank_in_context(tokens: Sequence[str],
                    analyses_per_token: Sequence[Sequence[Analysis]],
                    *, freq=None, pos=None) -> list[list[Analysis]]:
    """Cümle token'larını komşuluk kanıtıyla yeniden sırala (SPEC §1, §2).

    Args:
        tokens: yüzey token'ları (tokenizasyon ÇAĞIRANIN işi).
        analyses_per_token: her token için `analyze(...)` çıktısı (tokens ile eş uzunlukta).
        freq/pos: izole `disambiguation._rank_key`'e aynen geçirilir (opsiyonel).

    Returns:
        Her token için best-first YENİDEN sıralı YENİ liste. Öğe silme/ekleme YOK
        (recall-güvenli); yalnız sıra bağlam kanıtına göre değişir.

    Raises:
        ValueError: `tokens` ile `analyses_per_token` uzunlukları uyuşmazsa.
    """
    if len(tokens) != len(analyses_per_token):
        raise ValueError(
            f"tokens ({len(tokens)}) ile analyses_per_token "
            f"({len(analyses_per_token)}) uzunlukları uyuşmuyor"
        )
    out: list[list[Analysis]] = []
    for i, cands in enumerate(analyses_per_token):
        if not cands:
            out.append([])
            continue
        key = lambda a, i=i: (
            -context_evidence(a, i, tokens, analyses_per_token, freq=freq, pos=pos),
            *dis._rank_key(a, freq, pos),
        )
        out.append(sorted(cands, key=key))
    return out
