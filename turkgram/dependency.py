"""dependency.py — Dependency graph çıkarımı + CoNLL-U export (Faz E5+E6).

API:
    DepToken            — UD-uyumlu token veri yapısı
    constituency_to_dep — PhraseNode ağacı → list[DepToken]
    to_conllu           — list[DepToken] → CoNLL-U metin
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .parse import PhraseNode, LeafNode


@dataclass(frozen=True)
class DepToken:
    id: int
    form: str
    lemma: str | None
    upos: str
    xpos: str
    feats: str
    head: int
    deprel: str
    misc: str = "_"


# ---------------------------------------------------------------------------
# Feats üretimi (§5.4)
# ---------------------------------------------------------------------------

def _analysis_to_feats(analysis: "object | None", upos: str) -> str:
    """Analysis.kwargs → UD feats string (alfabetik sıra)."""
    if analysis is None:
        return "_"
    kwargs = getattr(analysis, "kwargs", {})
    kind   = getattr(analysis, "kind", "")
    feats: dict[str, str] = {}

    # Case
    _CASE_MAP = {
        "acc": "Acc", "dat": "Dat", "gen": "Gen",
        "abl": "Abl", "loc": "Loc", "ins": "Ins",
    }
    case = kwargs.get("case")
    if case in _CASE_MAP:
        feats["Case"] = _CASE_MAP[case]
    elif upos in ("NOUN", "NUM") and case is None:
        feats["Case"] = "Nom"

    # Number + Person
    person_str = kwargs.get("person")
    if person_str:
        feats["Number"] = "Plur" if person_str.endswith("pl") else "Sing"
        feats["Person"] = person_str[0]
    elif upos in ("NOUN", "NUM"):
        feats["Number"] = "Sing"

    # Possessive
    poss = kwargs.get("possessive")
    if poss:
        feats["Number[psor]"] = "Plur" if poss.endswith("pl") else "Sing"
        feats["Person[psor]"] = poss[0]

    # Tense
    _TENSE_MAP = {"past": "Past", "pres": "Pres", "fut": "Fut", "aorist": "Aor"}
    tense = kwargs.get("tense")
    if tense in _TENSE_MAP:
        feats["Tense"] = _TENSE_MAP[tense]

    # Evidential aux
    if kwargs.get("aux") == "evid":
        feats["Evident"] = "Nfh"

    # Polarity
    if kwargs.get("negative"):
        feats["Polarity"] = "Neg"

    # VerbForm
    if kind == "participle":
        feats["VerbForm"] = "Part"
    elif kind in ("converb", "converb_ken", "converb_casina"):
        feats["VerbForm"] = "Conv"

    # Voice
    voice_chain = kwargs.get("voice_chain", ())
    if "pass" in voice_chain:
        feats["Voice"] = "Pass"
    elif "caus" in voice_chain:
        feats["Voice"] = "Cau"

    if not feats:
        return "_"
    return "|".join(f"{k}={v}" for k, v in sorted(feats.items()))


# ---------------------------------------------------------------------------
# constituency_to_dep
# ---------------------------------------------------------------------------

def constituency_to_dep(tree: "PhraseNode") -> list[DepToken]:
    """PhraseNode ağacı → DepToken listesi (1-tabanlı ID, head-finding)."""
    from .parse import LeafNode, PhraseNode as PN

    def _leaves(node: "PN | LeafNode") -> list[LeafNode]:
        if isinstance(node, LeafNode):
            return [node]
        return [lf for c in node.children for lf in _leaves(c)]

    all_leaves = _leaves(tree)
    leaf_ids: dict[int, int] = {id(lf): i + 1 for i, lf in enumerate(all_leaves)}

    deps: dict[int, tuple[int, str]] = {}  # leaf_id → (head_id, deprel)

    def _find_head_leaf(node: "PN | LeafNode") -> LeafNode:
        """Öbek başını bul."""
        if isinstance(node, LeafNode):
            return node
        tag = node.tag
        children = node.children
        if tag == "NP":
            # possessed → en sağdaki iyelikli NOUN
            for c in reversed(children):
                if isinstance(c, LeafNode) and c.tag == "NOUN":
                    if c.analysis and c.analysis.kwargs.get("possessive"):
                        return c
            # yoksa en sağdaki NOUN
            for c in reversed(children):
                if isinstance(c, LeafNode) and c.tag == "NOUN":
                    return c
            # m-ikileme reduplikant (MRED) ASLA baş olmaz → fallback'te atla
            # (normal NP'de MRED yok → children ile aynı; davranış korunur)
            non_mred = [c for c in children if getattr(c, "tag", None) != "MRED"]
            return _find_head_leaf((non_mred or list(children))[-1])
        if tag in ("VP", "S"):
            for c in children:
                if isinstance(c, LeafNode) and c.tag == "VERB":
                    return c
            for c in children:
                if isinstance(c, PN) and c.tag == "VP":
                    return _find_head_leaf(c)
            return _find_head_leaf(children[-1])
        if tag == "PP":
            for c in children:
                if isinstance(c, LeafNode) and c.tag == "ADP":
                    return c
            return _find_head_leaf(children[-1])
        if tag == "AdjP":
            for c in reversed(children):
                if isinstance(c, LeafNode) and c.tag == "ADJ":
                    return c
            # m-ikileme reduplikant (MRED) ASLA baş olmaz → fallback'te atla
            non_mred = [c for c in children if getattr(c, "tag", None) != "MRED"]
            return _find_head_leaf((non_mred or list(children))[-1])
        if tag == "AdvP":
            return _find_head_leaf(children[0])  # ilk yaprak = baş
        if tag == "CoordP":
            return _find_head_leaf(children[0])
        return _find_head_leaf(children[-1])

    def _child_deprel(parent_tag: str, child: "PN | LeafNode") -> str:
        child_tag = child.tag
        # m-ikileme reduplikant → baş (parent NP veya AdjP fark etmez)
        if child_tag == "MRED":
            return "compound:redup"
        if parent_tag == "NP":
            if child_tag == "ADJ":
                return "amod"
            if child_tag == "NUM":
                return "nummod"
            if child_tag == "AdjP":
                return "amod"
            if child_tag == "CoordP":
                # koordine sıfat niteleyici (R3c) → amod; koordine isim tamlayan → nmod
                conj_cat = next(
                    (c.tag for c in child.children
                     if getattr(c, "tag", None) != "CCONJ"), None)
                if conj_cat in ("ADJ", "AdjP"):
                    return "amod"
            if child_tag in ("NP", "NOUN"):
                cl = _find_head_leaf(child) if isinstance(child, PN) else child
                if cl.analysis and cl.analysis.kwargs.get("case") == "gen":
                    return "nmod:poss"
                return "nmod"
        if parent_tag == "PP":
            if child_tag in ("NP", "NOUN"):
                return "nmod"
        if parent_tag == "AdjP":
            if child_tag == "ADJ":
                return "advmod"
        if parent_tag == "AdvP":
            return "compound:redup"          # ikinci token (tekrar) → baş
        if parent_tag == "CoordP":
            if child_tag == "CCONJ":
                return "cc"
            if child_tag in ("NP", "CoordP", "AdjP", "AdvP", "ADJ"):
                return "conj"
        if parent_tag in ("VP", "S"):
            # Koordine zarf/sıfat öbeği → advmod (nominal case-based mantıktan ÖNCE)
            if child_tag == "CoordP":
                conj_cat = next(
                    (c.tag for c in child.children
                     if getattr(c, "tag", None) != "CCONJ"), None)
                if conj_cat in ("AdvP", "AdjP"):
                    return "advmod"
            cl = _find_head_leaf(child) if isinstance(child, PN) else child
            case = cl.analysis.kwargs.get("case") if cl.analysis else None
            if child_tag in ("NP", "NOUN", "CoordP"):
                if case == "acc":
                    return "obj"
                if case in ("dat", "loc", "abl", "ins"):
                    return "obl"
                return "nsubj"
            if child_tag == "PP":
                return "obl"
            if child_tag in ("AdjP", "AdvP"):
                return "advmod"
        return "dep"

    def _process_children(node: "PN", head_leaf: "LeafNode") -> None:
        """Node çocuklarını head_leaf altına bağla; baş aynıysa şeffaf geç."""
        for child in node.children:
            child_head = _find_head_leaf(child)
            if id(child_head) == id(head_leaf):
                # Bu child baş pathında — kendi çocuklarını aynı head'e bağla
                if isinstance(child, PN):
                    _process_children(child, head_leaf)
            else:
                dr = _child_deprel(node.tag, child)
                _process(child, head_leaf, dr)

    def _process(node: "PN | LeafNode", parent_head_leaf: "LeafNode | None", deprel: str) -> None:
        if isinstance(node, LeafNode):
            if parent_head_leaf is None:
                deps[leaf_ids[id(node)]] = (0, "root")
            else:
                deps[leaf_ids[id(node)]] = (leaf_ids[id(parent_head_leaf)], deprel)
            return
        head_leaf = _find_head_leaf(node)
        if parent_head_leaf is None:
            deps[leaf_ids[id(head_leaf)]] = (0, "root")
        else:
            deps[leaf_ids[id(head_leaf)]] = (leaf_ids[id(parent_head_leaf)], deprel)
        _process_children(node, head_leaf)

    _process(tree, None, "root")

    result = []
    for i, lf in enumerate(all_leaves, 1):
        a = lf.analysis
        head_id, deprel = deps.get(i, (0, "root"))
        # MRED = m-ikileme reduplikant (parse iç etiketi) → UD upos taban(head) POS'undan
        # miras (NOUN taban→NOUN, ADJ taban→ADJ). head_id compound:redup ile tabanı gösterir.
        if lf.tag == "MRED":
            base = all_leaves[head_id - 1] if head_id else lf
            upos = base.tag if getattr(base, "tag", None) in ("NOUN", "ADJ") else "NOUN"
        else:
            upos = lf.tag
        xpos = a.kind if a else "_"
        feats = _analysis_to_feats(a, upos)
        lemma = a.lemma if a else None
        result.append(DepToken(
            id=i, form=lf.token, lemma=lemma,
            upos=upos, xpos=xpos, feats=feats,
            head=head_id, deprel=deprel,
        ))
    return result


# ---------------------------------------------------------------------------
# to_conllu
# ---------------------------------------------------------------------------

def to_conllu(
    tokens: list[DepToken],
    *,
    sent_id: str = "",
    text: str = "",
) -> str:
    """list[DepToken] → CoNLL-U formatında metin string.

    Sütun sırası: ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC
    DEPS = _ (enhanced bağımlılık yok), MISC = token.misc
    """
    lines = []
    if sent_id:
        lines.append(f"# sent_id = {sent_id}")
    if text:
        lines.append(f"# text = {text}")
    for t in tokens:
        lemma = t.lemma if t.lemma is not None else "_"
        lines.append(
            f"{t.id}\t{t.form}\t{lemma}\t{t.upos}\t{t.xpos}\t"
            f"{t.feats}\t{t.head}\t{t.deprel}\t_\t{t.misc}"
        )
    return "\n".join(lines) + "\n"


__all__ = ["DepToken", "constituency_to_dep", "to_conllu"]
