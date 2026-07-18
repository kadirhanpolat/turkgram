"""parse.py — Constituency parser (Faz E2).

API:
    LeafNode       — yaprak düğüm (token + analiz + etiket)
    PhraseNode     — öbek düğüm (tag + children + surface)
    parse_phrase   — token listesi → PhraseNode ağacı
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .postposition import _POSTPOSITIONS as _POSTPOSITIONS_TABLE

if TYPE_CHECKING:
    from .analysis import Analysis

# ADP tanıma: TÜM edatlar (donmuş dair/ilişkin/ait/yana dahil — aksi halde
# R2 'buna dair' için PP kurmaz).
_POSTPOSITIONS: frozenset[str] = frozenset(_POSTPOSITIONS_TABLE.keys())

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
    tag: str                                    # 'NP'|'VP'|'S'|'AdjP'|'PP'|'CoordP'|'CompP'|'RelP'|'DiyeP'|'AdvP'
    children: tuple["PhraseNode | LeafNode", ...]
    surface: str                                # özyinelemeli yaprak birleşimi
    governs: "frozenset[str] | None" = None    # yalnız PP; yönetilen durum kümesi

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
        governs: "frozenset[str] | None" = None,
    ) -> "PhraseNode":
        """Factory — surface'i özyinelemeli hesaplar."""
        surface = " ".join(t for child in children for t in cls._collect_tokens(child))
        return cls(tag=tag, children=children, surface=surface, governs=governs)


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
        "verb":  "VERB",
        "noun":  "NOUN",
        "adj":   "ADJ",
        "num":   "NUM",
        "conj":  "CCONJ",
        "postp": "ADP",
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


# Apostrof-ek → durum sınıflandırıcı (yumuşama-FREE, deterministik; SPEC §2.2).
# Türkçe imlada apostrof yalnız özel-ad/sayı + çekim eki sınırında kullanılır →
# ekin kendisi kesin sinyaldir. Motorun yumuşaması (Ahmet→Ahmed) imlaya UYMAZ
# (Ahmet'in) → merged-surface oracle yerine ekin doğrudan sınıflandırılması.
# Regex'ler karşılıklı dışlayıcı (anchored); tam-bir eşleşme yoksa → merge yok.
_APOS_CASE_PATTERNS: tuple[tuple[str, "re.Pattern[str]"], ...] = (
    ("gen", re.compile(r"^n?[ıiuü]n$")),   # nin/nın/nun/nün, in/ın/un/ün
    ("abl", re.compile(r"^[dt][ae]n$")),   # den/dan, ten/tan
    ("loc", re.compile(r"^[dt][ae]$")),    # de/da, te/ta
    ("ins", re.compile(r"^y?l[ae]$")),     # yle/yla, le/la
    ("dat", re.compile(r"^y?[ae]$")),      # ye/ya, e/a
    ("acc", re.compile(r"^y?[ıiuü]$")),    # yi/yı/yu/yü, i/ı/u/ü
)


def _classify_apostrophe_suffix(suffix: str) -> "str | None":
    """Apostrof-eki (küçültülmüş, apostrofsuz) → durum adı; belirsiz → None."""
    hits = [case for case, pat in _APOS_CASE_PATTERNS if pat.match(suffix)]
    return hits[0] if len(hits) == 1 else None


def _apply_r_proper(nodes: list) -> list:
    """R_proper: NAME yaprağı + 'EK yaprağı → tek NOUN[case] yaprağı (SPEC §2).

    Özel-isim + apostrof-ek yeniden kurulum. Tokenizer `Ali'nin`'i
    `["Ali", "'nin"]` böler; bu ön-geçiş ikiliyi tek genitif/durum NOUN yaprağına
    birleştirir. Yüzey tabanlı (apostrof kesin sinyal) — leksikon ŞART DEĞİL.
    Sınıflanamayan ek → dokunma (recall-güvenli).
    """
    from .analysis import Analysis, _segs_to_tuple, _tr_lower
    out, i = [], 0
    while i < len(nodes):
        a = nodes[i]
        b = nodes[i + 1] if i + 1 < len(nodes) else None
        if (b is not None
                and isinstance(a, LeafNode) and isinstance(b, LeafNode)
                and b.token.startswith("'") and len(b.token) > 1):
            case = _classify_apostrophe_suffix(_tr_lower(b.token[1:]))
            if case is not None:
                merged_token = a.token + b.token
                seg_label = {"gen": "tamlayan", "acc": "belirtme", "dat": "yönelme",
                             "loc": "bulunma", "abl": "ayrılma", "ins": "vasıta"}[case]
                analysis = Analysis(
                    lemma=a.token,                 # VERBATIM özel-ad (CoNLL-U lemma)
                    pos="noun",
                    kind="decline",
                    kwargs={"case": case},
                    segments=_segs_to_tuple([(a.token, "KÖK"),
                                             (b.token[1:], seg_label)]),
                    hypothetical=False,
                )
                out.append(LeafNode(tag="NOUN", token=merged_token, analysis=analysis))
                i += 2
                continue
        out.append(a)
        i += 1
    return out


def _is_gen_noun_leaf(node: "PhraseNode | LeafNode") -> bool:
    """Yaprak, genitif durumda NOUN mı? (R_gencoord tetiği)."""
    return (isinstance(node, LeafNode)
            and node.tag == "NOUN"
            and node.analysis is not None
            and node.analysis.kwargs.get("case") == "gen")


def _apply_r_gencoord(nodes: list) -> list:
    """R_gencoord: NOUN[gen] (CCONJ NOUN[gen])+ → CoordP (SPEC §3.1; R0'dan ÖNCE).

    Koordine genitif tamlayanlar tek CoordP olur; her konjunkt kendi NP'sine
    sarılır (golden_parse `kitap ve defter` emsali). R0'dan önce çalışır → R0'ın
    sağdaki `NOUN[gen] head` çiftini erken yakalaması engellenir.
    """
    out, i = [], 0
    while i < len(nodes):
        if (_is_gen_noun_leaf(nodes[i])
                and i + 2 < len(nodes)
                and _tag(nodes[i + 1]) == "CCONJ"
                and _is_gen_noun_leaf(nodes[i + 2])):
            group = [PhraseNode.make("NP", (nodes[i],))]
            j = i + 1
            while (j + 1 < len(nodes)
                   and _tag(nodes[j]) == "CCONJ"
                   and _is_gen_noun_leaf(nodes[j + 1])):
                group.extend([nodes[j], PhraseNode.make("NP", (nodes[j + 1],))])
                j += 2
            out.append(PhraseNode.make("CoordP", tuple(group)))
            i = j
        else:
            out.append(nodes[i])
            i += 1
    return out


def _is_gen_coord(node: "PhraseNode | LeafNode") -> bool:
    """Düğüm, tüm konjunktları genitif NP olan bir CoordP mi? (R0-genel possessor)."""
    if not (isinstance(node, PhraseNode) and node.tag == "CoordP"):
        return False
    conjuncts = [c for c in node.children if getattr(c, "tag", None) != "CCONJ"]
    if not conjuncts:
        return False
    for c in conjuncts:
        if isinstance(c, PhraseNode) and c.tag == "NP":
            head = c.children[0] if c.children else None
            if not _is_gen_noun_leaf(head):
                return False
        elif not _is_gen_noun_leaf(c):
            return False
    return True


def _apply_r8_redup(nodes: list) -> list:
    """R8: bitişik özdeş çift → AdvP (ikileme adverbial-yeniden-kurulum).

    Tam ikileme (yavaş yavaş) + ulaç ikilemesi (koşa koşa) → AdvP.
    Sınıflama: VERB çifti → ulaç-tipi (guard'sız); ADJ/NOUN çifti → tam-tipi
    (sonraki NOUN ise adnominal → skip, R1'e bırak). m-ikileme kapsam dışı.
    """
    from .analysis import _tr_lower  # Türkçe İ/I güvenli küçültme (cycle yok)
    out, i = [], 0
    while i < len(nodes):
        a = nodes[i]
        b = nodes[i + 1] if i + 1 < len(nodes) else None
        if (b is not None
                and isinstance(a, LeafNode) and isinstance(b, LeafNode)
                and _tr_lower(a.token) == _tr_lower(b.token)
                and a.tag == b.tag
                and a.tag in ("VERB", "ADJ", "NOUN")):
            # NOUN-takip guard (yalnız tam-tipi ADJ/NOUN): sonraki çıplak NOUN → adnominal, skip
            next_is_noun = (i + 2 < len(nodes) and _tag(nodes[i + 2]) == "NOUN")
            if a.tag in ("ADJ", "NOUN") and next_is_noun:
                out.append(a)
                i += 1
                continue
            out.append(PhraseNode.make("AdvP", (a, b)))
            i += 2
        else:
            out.append(a)
            i += 1
    return out


def _apply_r9_mredup(nodes: list) -> list:
    """R9: bitişik NOUN/ADJ + m-reduplikant → NP/AdjP (m-ikileme yeniden-kurulum).

    NOUN-taban (kitap mitap, araba maraba) → tek NP öbeği (özne/nesne rolü);
    ADJ-taban (güzel müzel) → tek AdjP öbeği (adjectival, isim niteler). Baş = taban,
    reduplikant `MRED` etiketiyle (compound:redup + upos=taban POS'undan miras dependency'de).
    Yüzey testi: m_reduplicate(taban) == taban + " " + reduplikant. m-test başarısızsa
    dokunmaz (recall-güvenli).
    """
    from .analysis import _tr_lower          # Türkçe İ/I güvenli küçültme
    from .reduplication import m_reduplicate  # yüzey m-testi (cycle yok)
    out, i = [], 0
    while i < len(nodes):
        a = nodes[i]
        b = nodes[i + 1] if i + 1 < len(nodes) else None
        matched = False
        if (b is not None
                and isinstance(a, LeafNode) and isinstance(b, LeafNode)
                and a.tag in ("NOUN", "ADJ")):
            la, lb = _tr_lower(a.token), _tr_lower(b.token)
            try:
                # Bilinçli belirsizlik (tasarım §3.2): reduplikant gerçek sözcük olsa
                # da (adam madam) m-ikileme tercih edilir — recall-güvenli, baskın okuma.
                if m_reduplicate(la) == la + " " + lb:
                    mred = LeafNode(tag="MRED", token=b.token, analysis=None)
                    phrase_tag = "NP" if a.tag == "NOUN" else "AdjP"
                    out.append(PhraseNode.make(phrase_tag, (a, mred)))
                    i += 2
                    matched = True
            except ValueError:
                pass  # boş/m-başlı taban → m-ikileme değil
        if not matched:
            out.append(a)
            i += 1
    return out


def _apply_r0(nodes: list) -> list:
    """R0: possessor + head → NP (belirtili isim tamlaması; SPEC §3.2).

    possessor = NOUN[gen] VEYA gen-CoordP (R_gencoord çıktısı, koordine tamlayan).
    head = bitişik NOUN | NP. **Head poss-etiketi ŞART DEĞİL** (recall-güvenli):
    head poss/acc homografı acc sıralanabilir; Türkçede yalın genitif zorunlu
    possessed-head ister → gen-possessor + bitişik ad = tamlama.
    """
    out, i = [], 0
    while i < len(nodes):
        node = nodes[i]
        if ((_is_gen_noun_leaf(node) or _is_gen_coord(node))
                and i + 1 < len(nodes)
                and _tag(nodes[i + 1]) in ("NOUN", "NP")):
            out.append(PhraseNode.make("NP", (node, nodes[i + 1])))
            i += 2
        else:
            out.append(node)
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


_ADJ_COORD_TAGS: tuple[str, ...] = ("ADJ", "AdjP")


def _apply_r3c_adj_coord(nodes: list) -> list:
    """R3c: sıfat koordinasyonu — (ADJ|AdjP) (CCONJ (ADJ|AdjP))+ → CoordP.

    R1'den ÖNCE çalışır: koordine sıfat niteleyicileri (`kırmızı ve mavi`,
    `güzel müzel ve çirkin mirkin`) tek CoordP olur → R1 onu isim niteleyicisi
    olarak alır (aksi halde R1 son sıfatı isme kapar, ilki başıboş kalır).
    Karışık ADJ/AdjP konjunkt serbest (`çok güzel ve kırmızı`).
    """
    out, i = [], 0
    while i < len(nodes):
        if (_tag(nodes[i]) in _ADJ_COORD_TAGS
                and i + 2 < len(nodes)
                and _tag(nodes[i + 1]) == "CCONJ"
                and _tag(nodes[i + 2]) in _ADJ_COORD_TAGS):
            group = [nodes[i]]
            j = i + 1
            while (j + 1 < len(nodes)
                   and _tag(nodes[j]) == "CCONJ"
                   and _tag(nodes[j + 1]) in _ADJ_COORD_TAGS):
                group.extend([nodes[j], nodes[j + 1]])
                j += 2
            out.append(PhraseNode.make("CoordP", tuple(group)))
            i = j
        else:
            out.append(nodes[i])
            i += 1
    return out


def _apply_r1(nodes: list) -> list:
    """R1: (ADJ|NUM|AdjP|CoordP)* NOUN → NP (CoordP = R3c sıfat koordinasyonu)."""
    out, i = [], 0
    while i < len(nodes):
        node = nodes[i]
        if _tag(node) == "NOUN":
            start = i
            while start > 0 and _tag(nodes[start - 1]) in ("ADJ", "NUM", "AdjP", "CoordP"):
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
    """R2: NP|NOUN ADP → PP (yönetilen durum işaretlemesiyle)."""
    out, i = [], 0
    while i < len(nodes):
        if (_tag(nodes[i]) in ("NP", "NOUN")
                and i + 1 < len(nodes)
                and _tag(nodes[i + 1]) == "ADP"):
            np_node = nodes[i]
            if isinstance(np_node, LeafNode):
                np_node = PhraseNode.make("NP", (np_node,))
            adp = nodes[i + 1]
            edat = adp.token.lower() if isinstance(adp, LeafNode) else adp.surface.lower()
            governs = _POSTPOSITIONS_TABLE.get(edat, {}).get("yönet")
            out.append(PhraseNode.make("PP", (np_node, adp), governs=governs))
            i += 2
        else:
            out.append(nodes[i])
            i += 1
    return out


_COORDINABLE: tuple[str, ...] = ("NP", "AdjP", "AdvP")


def _apply_r4(nodes: list) -> list:
    """R4: X (CCONJ X)+ → CoordP; X ∈ {NP, AdjP, AdvP}, AYNI kategori.

    NP koordinasyonu (`kitap ve kalem`) + koordine zarf (`yavaş yavaş ve hızlı
    hızlı`) + serbest koordine sıfat (`güzel müzel ve çirkin mirkin`). Konjunktlar
    aynı kategoriden olmalı (NP ve AdvP karışmaz). AdjP+isim koordinasyonu R1
    sıralaması nedeniyle kapsam dışı (ikinci AdjP isme kapılır).
    """
    out, i = [], 0
    while i < len(nodes):
        ti = _tag(nodes[i])
        # Eşleşecek konjunkt kategorisi: koordine öbek ise kendi etiketi; mevcut
        # CoordP (defansif/legacy) ise NP.
        cat = ti if ti in _COORDINABLE else ("NP" if ti == "CoordP" else None)
        if (cat is not None
                and i + 2 < len(nodes)
                and _tag(nodes[i + 1]) == "CCONJ"
                and _tag(nodes[i + 2]) == cat):
            group = [nodes[i]]
            j = i + 1
            while (j + 1 < len(nodes)
                   and _tag(nodes[j]) == "CCONJ"
                   and _tag(nodes[j + 1]) == cat):
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
            if tag not in ("NP", "PP", "AdjP", "CoordP", "NOUN", "AdvP"):
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
    nodes = _apply_r_proper(nodes)  # NOUN[case]: özel-isim + apostrof-ek merge (EN BAŞTA)
    nodes = _apply_r8_redup(nodes)  # AdvP: bitişik özdeş çift (R3/R1'den ÖNCE)
    nodes = _apply_r9_mredup(nodes) # NP: bitişik NOUN + m-reduplikant (m-ikileme)
    nodes = _apply_r_gencoord(nodes)  # CoordP: koordine genitif tamlayan (R0'dan ÖNCE)
    nodes = _apply_r0(nodes)      # NP: possessor(NOUN[gen]|gen-CoordP) + head
    nodes = _apply_r3(nodes)      # AdjP: ADJ ADJ+
    nodes = _apply_r3c_adj_coord(nodes)  # CoordP: sıfat koordinasyonu (R1'den ÖNCE)
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
