"""parse.py — Constituency parser (Faz E2).

API:
    LeafNode       — yaprak düğüm (token + analiz + etiket)
    PhraseNode     — öbek düğüm (tag + children + surface)
    parse_phrase   — token listesi → PhraseNode ağacı
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .postposition import _POSTPOSITION_CASE as _POSTPOSITION_CASE_MAP

if TYPE_CHECKING:
    from .analysis import Analysis

_POSTPOSITIONS: frozenset[str] = frozenset(_POSTPOSITION_CASE_MAP.keys())

# Kapalı küme bağlaçlar — yüzey tabanlı (edat gibi, analiz sisteminin dışında)
_SIMPLE_CONJ_TOKENS: frozenset[str] = frozenset({
    "ve", "veya", "ama", "fakat", "ancak", "ki",
})

# Derece sözcükleri — her zaman ADJ (R3 AdjP kuralı için)
_DEGREE_WORDS: frozenset[str] = frozenset({
    "çok", "oldukça", "pek", "biraz", "en", "daha", "az", "fazla", "epey",
})


@dataclass(frozen=True)
class LeafNode:
    """Yaprak düğüm — tek token."""
    tag: str              # 'NOUN' | 'VERB' | 'ADJ' | 'NUM' | 'ADP' | 'CCONJ' | 'X'
    token: str            # yüzey biçimi
    analysis: "Analysis | None"


@dataclass(frozen=True)
class PhraseNode:
    """Öbek düğüm — constituency ağaç düğümü."""
    tag: str                                    # 'NP'|'VP'|'S'|'AdjP'|'PP'|'CoordP'
    children: tuple["PhraseNode | LeafNode", ...]
    surface: str                                # özyinelemeli yaprak birleşimi

    @staticmethod
    def _collect_tokens(node: "PhraseNode | LeafNode") -> list[str]:
        if isinstance(node, LeafNode):
            return [node.token]
        return [t for child in node.children for t in PhraseNode._collect_tokens(child)]

    @classmethod
    def make(
        cls,
        tag: str,
        children: tuple["PhraseNode | LeafNode", ...],
    ) -> "PhraseNode":
        """Factory — surface'i özyinelemeli hesaplar."""
        surface = " ".join(t for child in children for t in cls._collect_tokens(child))
        return cls(tag=tag, children=children, surface=surface)


def _leaf_tag(token: str, analysis: "Analysis | None") -> str:
    """İki adımlı etiket üretimi (spec §4.4)."""
    tok = token.lower()
    # Adım 0a: yüzey tabanlı — edat (analiz sistemi dışında)
    if tok in _POSTPOSITIONS:
        return "ADP"
    # Adım 0b: yüzey tabanlı — bağlaç
    if tok in _SIMPLE_CONJ_TOKENS:
        return "CCONJ"
    # Adım 0c: derece sözcüğü — R3 AdjP için ADJ
    if tok in _DEGREE_WORDS:
        return "ADJ"
    if analysis is None:
        return "X"
    # Adım 1: kind tabanlı geçersiz kılmalar
    if analysis.kind == "copula":
        return "VERB"
    # Adım 1b: leksikon POS geçersiz kılması — decline pos='noun' ama leksikonda adj
    if analysis.pos == "noun" and analysis.lemma:
        try:
            from .lexicon import pos_map as _pos_map
            if _pos_map().get(analysis.lemma) == "adj":
                return "ADJ"
        except Exception:
            pass
    # Adım 2: pos tabanlı
    _POS_TO_TAG = {
        "verb": "VERB",
        "noun": "NOUN",
        "adj":  "ADJ",
        "num":  "NUM",
        "conj": "CCONJ",
    }
    return _POS_TO_TAG.get(analysis.pos, "X")


def _tag(node: "PhraseNode | LeafNode") -> str:
    return node.tag


def _node_is_nominative(node: "PhraseNode | LeafNode") -> bool:
    """NP/NOUN baş yalın (nominative) mı? Özne tespiti için R5'te kullanılır."""
    if isinstance(node, LeafNode):
        if node.analysis is None:
            return True
        return node.analysis.kwargs.get("case") in (None, "nom")
    # PhraseNode — en sağdaki NOUN yaprağını kontrol et
    for child in reversed(node.children):
        if isinstance(child, LeafNode) and child.tag == "NOUN":
            if child.analysis is None:
                return True
            return child.analysis.kwargs.get("case") in (None, "nom")
        if isinstance(child, PhraseNode) and child.tag == "NP":
            return _node_is_nominative(child)
    return True


def _apply_r3(nodes: list) -> list:
    """R3: ADJ ADJ+ → AdjP (derece + baş)."""
    out, i = [], 0
    while i < len(nodes):
        if _tag(nodes[i]) == "ADJ":
            j = i + 1
            while j < len(nodes) and _tag(nodes[j]) == "ADJ":
                j += 1
            if j > i + 1:
                out.append(PhraseNode.make("AdjP", tuple(nodes[i:j])))
            else:
                out.append(nodes[i])
            i = j
        else:
            out.append(nodes[i])
            i += 1
    return out


def _apply_r1(nodes: list) -> list:
    """R1: (ADJ|NUM|AdjP)* NOUN → NP."""
    out, i = [], 0
    while i < len(nodes):
        node = nodes[i]
        if _tag(node) == "NOUN":
            start = i
            while start > 0 and _tag(nodes[start - 1]) in ("ADJ", "NUM", "AdjP"):
                start -= 1
            end = i + 1
            group = tuple(nodes[start:end])
            out = out[:len(out) - (i - start)]
            out.append(PhraseNode.make("NP", group))
            i = end
        else:
            out.append(node)
            i += 1
    return out


def _apply_r1b(nodes: list) -> list:
    """R1b: VERB[kind=participle] NOUN|NP → NP."""
    out, i = [], 0
    while i < len(nodes):
        node = nodes[i]
        if (isinstance(node, LeafNode)
                and node.tag == "VERB"
                and node.analysis is not None
                and node.analysis.kind == "participle"
                and i + 1 < len(nodes)
                and _tag(nodes[i + 1]) in ("NOUN", "NP")):
            out.append(PhraseNode.make("NP", (node, nodes[i + 1])))
            i += 2
        else:
            out.append(node)
            i += 1
    return out


def _apply_r2(nodes: list) -> list:
    """R2: NP|NOUN ADP → PP."""
    out, i = [], 0
    while i < len(nodes):
        if (_tag(nodes[i]) in ("NP", "NOUN")
                and i + 1 < len(nodes)
                and _tag(nodes[i + 1]) == "ADP"):
            np_node = nodes[i]
            if isinstance(np_node, LeafNode):
                np_node = PhraseNode.make("NP", (np_node,))
            out.append(PhraseNode.make("PP", (np_node, nodes[i + 1])))
            i += 2
        else:
            out.append(nodes[i])
            i += 1
    return out


def _apply_r4(nodes: list) -> list:
    """R4: NP (CCONJ NP)+ → CoordP."""
    out, i = [], 0
    while i < len(nodes):
        if (_tag(nodes[i]) in ("NP", "CoordP")
                and i + 2 < len(nodes)
                and _tag(nodes[i + 1]) == "CCONJ"
                and _tag(nodes[i + 2]) == "NP"):
            group = [nodes[i]]
            j = i + 1
            while (j + 1 < len(nodes)
                   and _tag(nodes[j]) == "CCONJ"
                   and _tag(nodes[j + 1]) == "NP"):
                group.extend([nodes[j], nodes[j + 1]])
                j += 2
            out.append(PhraseNode.make("CoordP", tuple(group)))
            i = j
        else:
            out.append(nodes[i])
            i += 1
    return out


def _apply_r5(nodes: list) -> list:
    """R5: özne(NP-nom)* + VP(nesne(NP-acc)* + VERB) → S."""
    verb_indices = [
        i for i, n in enumerate(nodes)
        if _tag(n) == "VERB" or (isinstance(n, PhraseNode) and n.tag == "VP")
    ]
    if not verb_indices:
        return nodes
    vi = verb_indices[-1]  # son fiil = yüklem
    vp_node = nodes[vi]
    if isinstance(vp_node, LeafNode):
        vp_children: list = [vp_node]
        left = vi - 1
        while left >= 0:
            n = nodes[left]
            tag = _tag(n)
            if tag not in ("NP", "PP", "AdjP", "CoordP", "NOUN"):
                break
            # Yalın NP = özne → VP dışında bırak
            if tag in ("NP", "NOUN") and _node_is_nominative(n):
                break
            if isinstance(n, LeafNode) and n.tag == "NOUN":
                n = PhraseNode.make("NP", (n,))
            vp_children.insert(0, n)
            left -= 1
        vp = PhraseNode.make("VP", tuple(vp_children))
        remaining = nodes[:left + 1]
        s_children = list(remaining) + [vp]
        return [PhraseNode.make("S", tuple(s_children))]
    return nodes


def _wrap_bare_vp(nodes: list) -> list:
    """Yalnız VERB kaldıysa VP'ye sar."""
    return [
        PhraseNode.make("VP", (n,)) if (isinstance(n, LeafNode) and n.tag == "VERB") else n
        for n in nodes
    ]


def parse_phrase(
    tokens: list[str],
    analyses: list[list["Analysis"]],
) -> PhraseNode:
    """Token listesi + analiz listesi → constituency ağacı.

    Giriş:
        tokens:   tokenize() çıktısı
        analyses: parse_text() çıktısı (her token için analiz listesi)
    Çıkış:
        PhraseNode — tam cümle için 'S', yalnız öbek için 'NP'/'PP'/vb.
    """
    from .disambiguation import rank as _rank

    # 1. Yaprak düğümleri oluştur
    leaves: list[LeafNode] = []
    for token, token_analyses in zip(tokens, analyses):
        real = [a for a in token_analyses if not a.hypothetical]
        best = _rank(real)[0] if real else None
        tag = _leaf_tag(token, best)
        leaves.append(LeafNode(tag=tag, token=token, analysis=best))

    # 2. Bottom-up gruplama (kural sırası önemli)
    nodes: list[PhraseNode | LeafNode] = list(leaves)
    nodes = _apply_r3(nodes)   # AdjP: ADJ ADJ+
    nodes = _apply_r1(nodes)   # NP: modifer* NOUN
    nodes = _apply_r1b(nodes)  # NP: participle NOUN
    nodes = _apply_r2(nodes)   # PP: NP ADP
    nodes = _apply_r4(nodes)   # CoordP: NP CCONJ NP
    nodes = _apply_r5(nodes)   # S: özne VP(nesne VERB)
    nodes = _wrap_bare_vp(nodes)

    # 3. Kök düğüm — tek PhraseNode ise olduğu gibi döndür, çok ise S'ye sar
    if len(nodes) == 1 and isinstance(nodes[0], PhraseNode):
        return nodes[0]
    return PhraseNode.make("S", tuple(nodes))


__all__ = ["LeafNode", "PhraseNode", "parse_phrase"]
