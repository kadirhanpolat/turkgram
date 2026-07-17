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

# Kapalı küme converb fiilleri — analiz sistemi dışında yüzey tabanlı VERB etiketi
_CONVERB_VERB_TOKENS: frozenset[str] = frozenset({"diye"})

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
    # Adım 0b2: yüzey tabanlı — converb fiil (diye)
    if tok in _CONVERB_VERB_TOKENS:
        return "VERB"
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


def _apply_r0(nodes: list) -> list:
    """R0: NOUN[gen] NOUN[poss] → NP (belirtili isim tamlaması)."""
    out, i = [], 0
    while i < len(nodes):
        if (isinstance(nodes[i], LeafNode)
                and nodes[i].tag == "NOUN"
                and nodes[i].analysis is not None
                and nodes[i].analysis.kwargs.get("case") == "gen"
                and i + 1 < len(nodes)
                and isinstance(nodes[i + 1], LeafNode)
                and nodes[i + 1].tag == "NOUN"
                and nodes[i + 1].analysis is not None
                and nodes[i + 1].analysis.kwargs.get("possessive") is not None):
            out.append(PhraseNode.make("NP", (nodes[i], nodes[i + 1])))
            i += 2
        else:
            out.append(nodes[i])
            i += 1
    return out


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


def _apply_r6_ki(nodes: list) -> list:
    """R6: bağlam-duyarlı ki gruplaması.

    Sol ∈ {VERB, VP, S}  + CCONJ[ki] + sağ_sequence → CompP
    Sol ∈ {NP}           + CCONJ[ki] + sağ_sequence → RelP
    Aksi halde (ADJ, PP, index=0, vb.)              → değiştirme

    Tek geçiş: ilk ki'de ateşlenir, sağ tüm sequence alınır.
    """
    for i, node in enumerate(nodes):
        if not (isinstance(node, LeafNode)
                and node.tag == "CCONJ"
                and node.token.lower() == "ki"):
            continue
        # Sol komşu kontrolü (i==0 ise sol yok → atla)
        if i == 0:
            continue
        left = nodes[i - 1]
        left_tag = _tag(left)
        if left_tag in ("VERB", "VP", "S"):
            phrase_tag = "CompP"
        elif left_tag == "NP":
            phrase_tag = "RelP"
        else:
            continue  # ADJ, PP, AdjP, vb. → atla
        # Sol komşu + ki + sağ tüm sequence → yeni öbek
        right_seq = nodes[i + 1:]
        children = (left, node) + tuple(right_seq)
        new_node = PhraseNode.make(phrase_tag, children)
        return nodes[: i - 1] + [new_node]
    return nodes


def _apply_r7_diye(nodes: list) -> list:
    """R7: diye subordinator → DiyeP (sol-sequence + VERB[diye]).

    "diye" kapalı küme subordinator (demek opt-3sg kökenli, donmuş form).
    Yüzey tabanlı tespit — ki/ve gibi işlevsel sözcük olarak davranır.
    VERB etiketi _CONVERB_VERB_TOKENS ile garantilidir.

    Sol tüm node'lar + diye tokenı → DiyeP.
    DiyeP cümle-düzeyi adjunct: R5 VP'ye çekmez.
    """
    for i, node in enumerate(nodes):
        if not isinstance(node, LeafNode):
            continue
        if node.tag != "VERB":
            continue
        if node.token.lower() != "diye":
            continue
        # Sol sequence + diye → DiyeP
        left_seq = nodes[:i]
        if not left_seq:
            # Cümle-başı diye: sol yok → atla (aşırı nadir)
            continue
        children = tuple(left_seq) + (node,)
        diye_p = PhraseNode.make("DiyeP", children)
        right_seq = nodes[i + 1:]
        return [diye_p] + list(right_seq)
    return nodes


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
            # Yan cümle öbekleri cümle-düzeyi adjunct — VP'ye çekilmez
            if tag in ("DiyeP", "CompP", "RelP"):
                break
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
    nodes = _apply_r0(nodes)      # NP: NOUN[gen] NOUN[poss] (belirtili tamlama)
    nodes = _apply_r3(nodes)      # AdjP: ADJ ADJ+
    nodes = _apply_r1(nodes)      # NP: modifer* NOUN
    nodes = _apply_r1b(nodes)     # NP: participle NOUN
    nodes = _apply_r2(nodes)      # PP: NP ADP
    nodes = _apply_r6_ki(nodes)   # CompP / RelP: ki bağlam-duyarlı
    nodes = _apply_r7_diye(nodes) # DiyeP: diye yan cümle
    nodes = _apply_r4(nodes)      # CoordP: NP CCONJ NP
    nodes = _apply_r5(nodes)      # S: özne VP(nesne VERB)
    nodes = _wrap_bare_vp(nodes)

    # 3. Kök düğüm — tek PhraseNode ise olduğu gibi döndür, çok ise S'ye sar
    if len(nodes) == 1 and isinstance(nodes[0], PhraseNode):
        return nodes[0]
    return PhraseNode.make("S", tuple(nodes))


__all__ = ["LeafNode", "PhraseNode", "parse_phrase"]
