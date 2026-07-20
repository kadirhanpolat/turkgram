"""Cümle çözümleme katmanı — öge etiketleme + cümle türü sınıflandırma.

SPEC: docs/superpowers/specs/2026-07-20-cumle-cozumleme-design.md.

`parse.py`/`dependency.py` çıktısının fragile yapısına GÜVENMEZ; öge grubunu doğrudan
token-düzeyi en-iyi analiz + morfolojik durumdan kurar (daha sağlam). `değil`/`mI` motor
tarafından çözülmediği için yüzey kapalı-set kullanır (interjection/conjunction emsali).

Çekirdek değişmez ihlali YOK — yeni morfoloji/üreteç yok, analyze()/parse()/dependency()
DOKUNULMAZ. OPT-IN. Kullanım: `analyze_sentence(text, roots=lexicon.load())`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Collection, Optional

from .tokenize import tokenize as _tokenize
from .analysis import parse_text, _tr_lower
from .disambiguation import rank as _rank
from .postposition import _POSTPOSITIONS as _POSTPOSITION_TABLE
from .interjection import INTERJECTIONS as _INTERJECTIONS

__all__ = ["Element", "SentenceType", "Clause", "SentenceAnalysis", "analyze_sentence"]

# "Pür" ünlemler — yaygın isim/fiil homografı OLMAYAN alt küme. Cümle-başı bunlar
# cümle dışı unsur (hitap/seslenme) sayılır; homograflar (of/ay/ey/işte) HARİÇ
# (best.pos==ünlem ranklanırsa zaten _R_UNLEM olur, ayrıca zorlamaya gerek yok).
_HOMOGRAPH_INTERJECTIONS: frozenset[str] = frozenset({
    "of", "ay", "oh", "ey", "hay", "na", "be", "işte", "hah", "üf", "yazık",
    "marş", "yaşa", "deh",   # içerik-sözcük homografı (marş=şarkı, yaşa=yaşamak imp)
})
_PURE_INTERJECTIONS: frozenset[str] = _INTERJECTIONS - _HOMOGRAPH_INTERJECTIONS

# ── Yüzey kapalı-setler (motor bunları düzgün çözmez → yüzey tespiti) ──────────
# Soru edatı mI: yalın + kişili ek-fiil biçimleri (miyim/misin/mısınız/mudur…).
_QUESTION_PARTICLE_RE = re.compile(
    r"^(mı|mi|mu|mü)"
    r"(y[ıiuü]m|s[ıiuü]n|y[ıiuü]z|s[ıiuü]n[ıiuü]z|d[ıiuü]r|ler|lar)?$"
)
_NEG_PARTICLE = "değil"          # nominal olumsuzluk (isim cümlesi)
_NEG_EXISTENTIAL = frozenset({"yok"})   # yok = olumsuz var-lık yüklemi

# Edat (yüzey) — homograf disambiguation'ı atla (için/doğru/gibi…)
_POSTP_SURFACE: frozenset[str] = frozenset(_POSTPOSITION_TABLE.keys())

# Şart (dilek-şart) yüklem yüzeyi: -sa/-se (+ kişi). Motor tense=aorist verir (gelirse),
# koşul eki yüzeyde görünür → non-final finit fiil şart-yan-yargısı tespiti.
_COND_SURFACE_RE = re.compile(r"(sa|se)(m|n|k|nız|niz|nuz|nüz)?$")

# -CA türevli tarz zarfı (yavaşça, hızlıca) — leksikonda yok, durumsuz.
_CA_ADVERB_RE = re.compile(r"[çc][ae]$")

# Demonstratif/belirteç (best=None olsa da MOD): bu/şu/o + çoğul
_DEMONSTRATIVES: frozenset[str] = frozenset({
    "bu", "şu", "o", "bunlar", "şunlar", "onlar",
})

# Kişi zamiri eğik/suppletif biçimleri → yüzey kapalı-set (durum). Motor bana/sana'yı
# banmak/sanmak FİİL rank eder (çok yaygın: 'Bana verdi') → zamir olarak zorla (AD + durum).
_PRONOUN_OBLIQUE: dict[str, str] = {
    "bana": "dat", "sana": "dat", "ona": "dat", "bize": "dat", "size": "dat",
    "onlara": "dat",
    "beni": "acc", "seni": "acc", "onu": "acc", "bizi": "acc", "sizi": "acc",
    "onları": "acc",
    "bende": "loc", "sende": "loc", "onda": "loc", "bizde": "loc", "sizde": "loc",
    "onlarda": "loc",
    "benden": "abl", "senden": "abl", "ondan": "abl", "bizden": "abl",
    "sizden": "abl", "onlardan": "abl",
    "benim": "gen", "senin": "gen", "onun": "gen", "bizim": "gen", "sizin": "gen",
    "onların": "gen",
}

# Zaman adları (kapalı küme) — DURUM-EKLİ (dat/loc/abl) biçim zarf tümleci sayılır
# (akşama gittik → akşama = zarf tümleci, dolaylı tümleç DEĞİL). nom BİLİNÇLİ hariç
# (Sabah güzeldi = özne belirsizliği); acc = belirtili nesne (sabahı bekledim). Lemma
# eşleşmesi → çekimli biçim (akşam+a) tabana iner.
# NOT: çok-anlamlı somut adlar (saat=nesne, sıra=yer, son/ilk/an/ay=uzay, devir/çağ)
# DIŞLANDI — dat/loc/abl'de zarf sanmak yanlış (Saate baktık=nesne, Aya gittik=uzay).
_TIME_NOUNS: frozenset[str] = frozenset({
    "sabah", "öğle", "akşam", "gece", "gündüz", "akşamüstü", "öğleüstü",
    "gün", "hafta", "yıl", "sene", "yaz", "kış", "ilkbahar",
    "sonbahar", "bahar", "güz", "zaman", "vakit", "asır", "yüzyıl",
    "geçmiş", "gelecek", "bugün", "dün", "yarın",
})

# Yüklem kipi (Analysis kwargs['tense']) → cümle-türü kip ekseni
_TENSE_TO_KIP = {
    "imp": "emir", "opt": "istek", "cond": "şart", "necess": "gereklilik",
    "wish": "dilek",
}

# Bağlaç (bağlı cümle) — cümle-düzeyi bağlayıcılar (context/conjunction emsali)
_COORD_CONJ = frozenset({
    "ve", "ama", "fakat", "lakin", "ancak", "yoksa", "veya", "ya da", "yahut",
})

# Modifier POS (leksikon pos_map) — niteleyici/belirteç öbek-içi kalır
_MOD_POS = frozenset({"adj", "num", "det"})

# Derece sözcükleri (parse.py emsali) — modifier zinciri bunlarla BAŞLARSA zarf tümleci
# (çok hızlı), yoksa son token isim başı sayılır (küçük çocuk → özne). pos_map birçok
# ismi adj etiketlediği için (çocuk/ali=adj) baş-tespiti pos_map'e güvenemez.
_DEGREE_WORDS: frozenset[str] = frozenset({
    "çok", "oldukça", "pek", "biraz", "en", "daha", "az", "fazla", "epey", "gayet",
})


@dataclass(frozen=True)
class Element:
    """Cümle ögesi (öbek)."""
    label: str                          # kanonik öge etiketi
    tokens: tuple[str, ...]
    head_id: int                        # ögenin başının 1-tabanlı token id'si
    aliases: tuple[str, ...] = ()       # tanıdık eşanlamlı (KARMA gelenek)


@dataclass(frozen=True)
class SentenceType:
    """Cümlenin çok-eksenli türü."""
    yuklem_turu: str        # 'fiil' | 'isim'
    yuklem_yeri: str        # 'kurallı' | 'devrik'
    olumluluk: str          # 'olumlu' | 'olumsuz'
    soru: bool
    kip: Optional[str]      # 'emir'|'istek'|'dilek'|'şart'|'gereklilik'|'haber'|None
    yapi: str               # 'basit' | 'birleşik' | 'sıralı' | 'bağlı'
    eksiltili: bool


@dataclass(frozen=True)
class Clause:
    """Yargı (cümle-içi bağımsız/yan cümle) — V3 clause segmentation.

    SPEC: docs/superpowers/specs/2026-07-20-clause-segmentation-design.md.
    `role`: 'temel' | 'yan' | 'bağımsız' (SPEC §3). `predicate_id`: yüklemin
    1-tabanlı GLOBAL token id'si (yüklemsiz→0). `connector`: bu yargıyı bağlayan
    koordinat bağlaç yüzeyi ('ve'/'ama'…) veya None (ilk yargı + yan cümleler).
    """
    role: str
    elements: tuple[Element, ...]
    predicate_id: int
    connector: Optional[str] = None


@dataclass(frozen=True)
class SentenceAnalysis:
    text: str
    elements: tuple[Element, ...]
    sentence_type: SentenceType
    clauses: tuple["Clause", ...] = ()


# ── Token rolü ────────────────────────────────────────────────────────────────
@dataclass
class _Tok:
    idx: int                # 1-tabanlı
    surface: str
    best: object            # Analysis | None
    role: str               # aşağıdaki sabitlerden
    case: Optional[str]     # nominal durumu (kwargs['case']; None=nom veya yok)
    pos: Optional[str]      # leksikon-refine POS (adj/adv/num/det/noun…)


# rol sabitleri
_R_SORU = "SORU"; _R_NEG = "NEG"; _R_FIIL = "FIIL"; _R_ULAC = "ULAC"
_R_ORTAC = "ORTAC"; _R_NOMPRED = "NOMPRED"; _R_ADP = "ADP"; _R_CONJ = "CONJ"
_R_UNLEM = "UNLEM"; _R_MOD = "MOD"; _R_ADV = "ADV"; _R_AD = "AD"; _R_X = "X"

_FINITE_VERB_KINDS = frozenset({"conjugate"})
_NONFINITE_VERB_KINDS = frozenset({"converb", "converb_casina", "converb_ken"})

# Anlatı (bildirme) zamanları — gövdedeki finit fiil KOORDİNAT yüklem sayılması için
# anlatı zamanında olmalı VEYA açık bağlaç bulunmalı. imperatif/optatif homografı
# (Kar/Yaz/Gül gibi ad-fiil eşsesi) sıralı-yüklem sanılmaz → özne.
_NARRATIVE_TENSES = frozenset({"past", "evid", "pres", "fut", "aorist"})


def _classify(idx: int, surface: str, best, pos_map: dict) -> _Tok:
    low = _tr_lower(surface)
    case = best.kwargs.get("case") if best is not None else None
    # ── Yüzey kapalı-setler önce (motor bunları homograf/OOV nedeniyle çözemez) ──
    if _QUESTION_PARTICLE_RE.match(low):
        return _Tok(idx, surface, best, _R_SORU, None, None)
    if low == _NEG_PARTICLE:
        return _Tok(idx, surface, best, _R_NEG, None, None)
    if low in _POSTP_SURFACE:
        return _Tok(idx, surface, best, _R_ADP, None, "postp")
    if low in _COORD_CONJ or low in ("ki", "de", "da"):
        return _Tok(idx, surface, best, _R_CONJ, None, "conj")
    if low in _DEMONSTRATIVES:
        return _Tok(idx, surface, best, _R_MOD, None, "det")
    if low in _PRONOUN_OBLIQUE:
        # kişi zamiri eğik biçimi (bana/sana/beni…) — fiil homografını geçersiz kıl
        pc = _PRONOUN_OBLIQUE[low]
        return _Tok(idx, surface, best, _R_AD, None if pc == "nom" else pc, "pron")
    # Cümle-başı pür ünlem (eyvah/haydi/aferin) → cümle dışı unsur; homograf-rank ünlem
    # (of/aman/vay) zaten aşağıda best.pos==ünlem ile yakalanır.
    if idx == 1 and low in _PURE_INTERJECTIONS:
        return _Tok(idx, surface, best, _R_UNLEM, None, "ünlem")
    if best is None:
        # OOV: -CA zarfı? yoksa Baş-harf büyük → özel ad (isim); değilse X
        if _CA_ADVERB_RE.search(low):
            return _Tok(idx, surface, None, _R_ADV, None, "adv")
        role = _R_AD if surface[:1].isupper() else _R_X
        return _Tok(idx, surface, None, role, None, "noun" if role == _R_AD else None)
    p = best.pos
    if p == "ünlem" or p == "yansıma":
        return _Tok(idx, surface, best, _R_UNLEM, None, p)
    if p == "conj":
        return _Tok(idx, surface, best, _R_CONJ, None, "conj")
    if p == "postp":
        return _Tok(idx, surface, best, _R_ADP, None, "postp")
    if best.kind in _FINITE_VERB_KINDS:
        return _Tok(idx, surface, best, _R_FIIL, None, "verb")
    if best.kind in _NONFINITE_VERB_KINDS:
        return _Tok(idx, surface, best, _R_ULAC, None, "verb")
    if best.kind == "participle":
        return _Tok(idx, surface, best, _R_ORTAC, None, "verb")
    if best.kind == "copula":
        return _Tok(idx, surface, best, _R_NOMPRED, case, "noun")
    # nominal (decline) — leksikon POS refine. TUZAK: niteleme sıfatı morfolojik olarak
    # ÇIPLAKtır; çekim eki (çoğul/iyelik) alan adj-etiketli token aslında İSİMdir (Çocuklar,
    # Annem) → pos_map ali/çocuk=adj kuruntusunu çekimli biçimlerde geçersiz kılar (özne kaybı fix).
    inflected = bool(best.kwargs.get("number") or best.kwargs.get("possessive"))
    lex_pos = pos_map.get(best.lemma) or pos_map.get(low)
    if case is None and not inflected:
        if lex_pos == "adv" or (_CA_ADVERB_RE.search(low) and lex_pos != "noun"):
            return _Tok(idx, surface, best, _R_ADV, None, "adv")
        if lex_pos in _MOD_POS:
            return _Tok(idx, surface, best, _R_MOD, None, lex_pos)
    return _Tok(idx, surface, best, _R_AD, case, "noun")


# ── Öge etiketleme + tür ──────────────────────────────────────────────────────
def _best_per_token(text: str, roots) -> list:
    """Her token için (best, verb_reading). verb_reading = ilk finit fiil analizi (varsa)
    → yüklem tespiti top-rank noun homografına (verdi=noun) takılmaz."""
    analyses = parse_text(text, roots=roots)
    out = []
    for al in analyses:
        real = [a for a in al if not a.hypothetical]
        best = _rank(real)[0] if real else None
        verb = next((a for a in real if a.kind == "conjugate"), None)
        out.append((best, verb))
    return out


def _label_nominal(case: Optional[str]) -> tuple[str, tuple[str, ...]]:
    """Nominal öbek başının durumundan etiket (özne/nesne heuristiği ÇAĞIRANDA)."""
    if case == "acc":
        return "belirtili nesne", ()
    if case in ("dat", "loc", "abl"):
        return "dolaylı tümleç", ("yer tamlayıcısı",)
    return "özne", ()   # nom — özne/belirtisiz-nesne ayrımı sonradan


def _label_body(body: "list[_Tok]") -> "tuple[list[Element], bool]":
    """Yüklem-dışı gövde tokenlarını ögelere etiketle (özne/tümleç/zarf/edat…).

    Düz yol (`analyze_sentence`) ve yargı yolu (`_segment_clauses`) PAYLAŞIR → tek
    doğruluk kaynağı. `subordinate` = gövdede fiilimsi/şart yan-yargı görüldü mü
    (birleşik tespiti). Özne/belirtisiz-nesne heuristiği + yüklem ögesi ÇAĞIRANDA.
    """
    elements: list[Element] = []
    subordinate = False  # birleşik tespiti
    has_conj_body = any(t.role == _R_CONJ for t in body)
    i = 0
    m = len(body)
    while i < m:
        t = body[i]
        if t.role == _R_UNLEM or t.role == _R_CONJ:
            elements.append(Element("cümle dışı unsur", (t.surface,), t.idx))
            i += 1
            continue
        if t.role in (_R_ULAC, _R_ORTAC):
            # fiilimsi yan-yargı → zarf tümleci + birleşik. Sol case'li tümleci içine çek.
            subordinate = True
            grp = [t]
            if (elements and i > 0 and body[i - 1].role == _R_AD
                    and body[i - 1].case in ("dat", "loc", "abl", "acc")
                    and elements[-1].head_id == body[i - 1].idx):  # hizalama guard
                elements.pop()
                grp = [body[i - 1], t]
            toks_srt = tuple(x.surface for x in sorted(grp, key=lambda x: x.idx))
            elements.append(Element("zarf tümleci", toks_srt, t.idx))
            i += 1
            continue
        if t.role == _R_ADV:
            elements.append(Element("zarf tümleci", (t.surface,), t.idx))
            i += 1
            continue
        if t.role == _R_FIIL:
            # yüklem-dışı finit fiil: şart yan-yargısı (birleşik) / koordinat yüklem / ad-homograf
            surf = _tr_lower(t.surface)
            tense = t.best.kwargs.get("tense") if t.best else None
            if tense == "cond" or (tense == "aorist" and _COND_SURFACE_RE.search(surf)):
                subordinate = True
                elements.append(Element("zarf tümleci", (t.surface,), t.idx))
            elif tense in _NARRATIVE_TENSES or has_conj_body:
                # anlatı zamanı VEYA açık bağlaç → gerçek koordinat/sıralı yüklem
                elements.append(Element("yüklem", (t.surface,), t.idx))
            else:
                # imperatif/optatif homografı (Kar/Yaz/Gül) → sıralı-yüklem DEĞİL, özne
                elements.append(Element("özne", (t.surface,), t.idx))
            i += 1
            continue
        if t.role in (_R_MOD, _R_AD, _R_NOMPRED, _R_X):
            # nominal öbek: modifier* zinciri; isimle biterse nominal öge, bitmezse zarf
            grp = [t]
            j = i + 1
            # TUZAK: demonstratif (MOD) eğik ZAMİRİ yutmamalı (O bana → iki ayrı zamir,
            # 'O bana' değil). Belirteç yalnız ortak adı niteler, zamiri değil (pos!=pron).
            while (t.role == _R_MOD and j < m and body[j].role in (_R_MOD, _R_AD, _R_X)
                   and body[j].pos != "pron"):
                grp.append(body[j])
                t = body[j]
                j += 1
            head = grp[-1]
            # following ADP → edat tümleci (baş = edat, geleneksel işlevsel baş)
            if j < m and body[j].role == _R_ADP:
                adp = body[j]
                grp.append(adp)
                elements.append(Element(
                    "edat tümleci", tuple(x.surface for x in grp), adp.idx))
                i = j + 1
                continue
            # modifier/zarf ile biten zincir (case'li isim başı YOK): derece sözcüğüyle
            # başlıyorsa zarf tümleci (çok hızlı); yoksa son token isim başı (küçük çocuk).
            if head.role in (_R_MOD, _R_ADV):
                adverbial = (_tr_lower(grp[0].surface) in _DEGREE_WORDS
                             or (len(grp) == 1 and grp[0].role == _R_ADV))
                if adverbial:
                    elements.append(Element(
                        "zarf tümleci", tuple(x.surface for x in grp), head.idx))
                    i = j
                    continue
            # Zaman adı + yönelme/bulunma/çıkma → zarf tümleci (akşama gittik), dolaylı DEĞİL
            head_lemma = head.best.lemma if head.best is not None else None
            if head.case in ("dat", "loc", "abl") and head_lemma in _TIME_NOUNS:
                elements.append(Element(
                    "zarf tümleci", tuple(x.surface for x in grp), head.idx))
                i = j
                continue
            label, aliases = _label_nominal(head.case)
            elements.append(Element(
                label, tuple(x.surface for x in grp), head.idx, aliases))
            i = j
            continue
        if t.role == _R_ADP:
            # edat önceki nominal/zarf ögeyi yönetir → tek edat tümleci'ne birleştir
            # (Sabaha kadar, bana göre). Önceki öge yoksa tek başına edat.
            _GOVERNABLE = ("dolaylı tümleç", "zarf tümleci", "özne",
                           "belirtili nesne", "belirtisiz nesne")
            # adjacency guard: önceki öge edat'a bitişik olmalı (i>0 ve öge başı i-1 token)
            if (elements and i > 0 and elements[-1].label in _GOVERNABLE
                    and elements[-1].head_id == body[i - 1].idx):
                prev = elements.pop()
                elements.append(Element(
                    "edat tümleci", prev.tokens + (t.surface,), t.idx))
            else:
                elements.append(Element("edat tümleci", (t.surface,), t.idx))
            i += 1
            continue
        elements.append(Element("cümle dışı unsur", (t.surface,), t.idx))
        i += 1
    return elements, subordinate


def _apply_subj_object_heuristic(elements: "list[Element]") -> "list[Element]":
    """nom öbekler: gövdede yüklem yok + ≥2 nom 'özne' → sonuncusu belirtisiz nesne.
    Tek yargıda (yargı yolu) güvenli; düz yolda V2 çok-cümle gate ayrıca uygular."""
    body_has_verb = any(e.label == "yüklem" for e in elements)
    nom_subj = [e for e in elements if e.label == "özne"]
    if not body_has_verb and len(nom_subj) >= 2:
        last = max(nom_subj, key=lambda e: e.head_id)
        return [
            Element("belirtisiz nesne", e.tokens, e.head_id, e.aliases)
            if e is last else e
            for e in elements
        ]
    return elements


def _pred_is_yan(t: "_Tok") -> bool:
    """Yargı yüklemi bağımlı mı (fiilimsi/şart) → 'yan' rolü sinyali."""
    if t.role in (_R_ULAC, _R_ORTAC):
        return True
    if t.role == _R_FIIL:
        tense = t.best.kwargs.get("tense") if t.best else None
        if tense == "cond" or (
                tense == "aorist" and _COND_SURFACE_RE.search(_tr_lower(t.surface))):
            return True
    return False


def _segment_clauses(toks: "list[_Tok]", tail: int, pred_i: int,
                     trailing: "list[_Tok]") -> "tuple[Clause, ...]":
    """Cümleyi yargılara böl (SPEC §4). Yüklem-sınırı token akışını segmentler;
    koordinat bağlaç sonraki yargının connector'ı; devrik kuyruk son yargıya iliştirilir.
    Her yargı `_label_body` ile öge-etiketlenir (yüklem hariç → fiilimsi kendi tümlecini
    yutmaz). `analyze_sentence`/düz `elements` DOKUNULMAZ (bu SALT-EK)."""
    if tail <= 0:
        return ()
    has_conj = any(t.role == _R_CONJ and _tr_lower(t.surface) in _COORD_CONJ
                   for t in toks[:tail])

    def _is_boundary(k: int) -> bool:
        if k == pred_i:
            return True
        t = toks[k]
        if t.role in (_R_ULAC, _R_ORTAC):
            return True
        if t.role == _R_NOMPRED:
            # ek-fiilli nominal yüklem (güzeldi/öğretmendi) → finit yüklem → sınır
            # (copula-yüklem koordinasyonu: 'Hava güzeldi ve deniz sıcaktı'). Copulasız
            # çıplak nominal (güzel=decline) tespit edilemez → best-effort sınır (§6).
            return True
        if t.role == _R_FIIL:
            tense = t.best.kwargs.get("tense") if t.best else None
            surf = _tr_lower(t.surface)
            if tense == "cond" or (tense == "aorist" and _COND_SURFACE_RE.search(surf)):
                return True
            if tense in _NARRATIVE_TENSES or has_conj:
                return True
            return False   # imperatif/optatif homografı → sınır değil (özne)
        return False

    bidx = sorted({k for k in range(tail) if _is_boundary(k)} | {pred_i})

    # Segmentle: [prev .. b] (b dahil); kuyruk (devrik) son segmente iliştir
    segments: list[tuple[list["_Tok"], int]] = []
    prev = 0
    for b in bidx:
        segments.append((toks[prev:b + 1], b))
        prev = b + 1
    if prev < tail:                       # devrik: son yüklemden sonra kalan tümleç
        if segments:
            seg, b = segments[-1]
            segments[-1] = (seg + toks[prev:tail], b)
        else:                             # yüklem yok → tek yargı, predicate yok
            segments.append((toks[0:tail], -1))

    non_yan = sum(1 for _seg, b in segments if b >= 0 and not _pred_is_yan(toks[b]))
    last_i = len(segments) - 1

    clauses: list[Clause] = []
    for si, (seg, b) in enumerate(segments):
        connector = None
        # baştaki koordinat bağlacı sıyır → connector (yargı ögesi değil)
        while seg and seg[0].role == _R_CONJ and _tr_lower(seg[0].surface) in _COORD_CONJ:
            connector = seg[0].surface
            seg = seg[1:]
        pred = toks[b] if b >= 0 else None
        pred_trailing = trailing if si == last_i else []
        body = [t for t in seg if t is not pred]
        els, _sub = _label_body(body)
        # yargı yüklemi imperatif → yalın ad özne = hitap (V1 §7b emsali)
        if pred is not None and pred.role == _R_FIIL:
            if (pred.best.kwargs.get("tense") if pred.best else None) == "imp":
                els = [Element("cümle dışı unsur", e.tokens, e.head_id)
                       if e.label == "özne" else e for e in els]
        els = _apply_subj_object_heuristic(els)
        if pred is not None:
            pred_surf = (pred.surface,) + tuple(t.surface for t in pred_trailing)
            els.append(Element("yüklem", pred_surf, pred.idx))
        els.sort(key=lambda e: e.head_id)
        yan = pred is not None and _pred_is_yan(pred)
        if yan and non_yan >= 1:
            role = "yan"
        elif non_yan >= 2:
            role = "bağımsız"
        else:
            role = "temel"
        pid = pred.idx if pred is not None else 0
        clauses.append(Clause(role, tuple(els), pid, connector))
    return tuple(clauses)


def analyze_sentence(text: str, *, roots: "Collection[str] | None" = None) -> SentenceAnalysis:
    """Cümleyi öge + tür olarak çözümle (SPEC §4-§5).

    roots=lexicon.load() ÖNERİLİR (gerçek POS için); roots=None gürültü modu → etiketler
    güvenilmez.
    """
    surfaces = _tokenize(text)
    from .lexicon import pos_map as _pos_map_fn
    try:
        pos_map = _pos_map_fn()
    except Exception:
        pos_map = {}
    pairs = _best_per_token(text, roots)
    bests = [b for b, _v in pairs]
    verbs = [v for _b, v in pairs]
    toks = [_classify(i + 1, s, b, pos_map) for i, (s, b) in enumerate(zip(surfaces, bests))]

    n = len(toks)
    if n == 0:
        return SentenceAnalysis(text, (), SentenceType(
            "isim", "kurallı", "olumlu", False, None, "basit", True))

    # 1. Soru: HERHANGİ bir token ayrı mI ise soru cümlesi (yüklem-bitişik olmasa da)
    soru = any(t.role == _R_SORU for t in toks)
    neg_nominal = False

    # Sondaki soru edatı + değil'i yüklem eklentisi olarak ayır (yüklem-bitişik)
    tail = n  # yüklem-bloğu sonrası ekler bitişi
    trailing: list = []
    while tail > 0 and toks[tail - 1].role in (_R_SORU, _R_NEG):
        t = toks[tail - 1]
        if t.role == _R_NEG:
            neg_nominal = True
        trailing.insert(0, t)
        tail -= 1

    if tail == 0:
        return SentenceAnalysis(text, (), SentenceType(
            "isim", "kurallı", "olumlu", soru, "haber", "basit", True))

    # 2. Yüklem = en sağdaki FİİL-yeteneği olan token; yoksa son NOMİNAL (edat/bağlaç atla)
    _NONPRED_ROLES = (_R_SORU, _R_NEG, _R_ADP, _R_CONJ, _R_UNLEM)
    # Adım 1: en sağdaki TOP-RANK gerçek fiil (role FIIL/ULAC/ORTAC) → devrik yüklem
    # yakalar (Gittim okula). göre=gör-e gibi ADP homografı NONPRED ile atlanır.
    pred_i = None
    for k in range(tail - 1, -1, -1):
        if toks[k].role in _NONPRED_ROLES:
            continue
        if toks[k].role in (_R_FIIL, _R_ULAC, _R_ORTAC):
            pred_i = k
            break
    # Adım 2: gerçek fiil yok → en sağdaki içerik token (yüklem SON'dadır). verb_reading'i
    # varsa fiil yüklem (verdi=noun-rank ama fiil), yoksa nominal yüklem (yanlış). Bu,
    # cümle-BAŞI fiil-homografının (Bana=banmak) yüklem sanılmasını ÖNLER.
    if pred_i is None:
        for k in range(tail - 1, -1, -1):
            if toks[k].role not in _NONPRED_ROLES:
                pred_i = k
                break
    if pred_i is None:
        return SentenceAnalysis(text, (), SentenceType(
            "isim", "kurallı", "olumlu", soru, "haber", "basit", True))

    pred = toks[pred_i]
    pred_verb = verbs[pred_i]           # yüklemin fiil-okuması (varsa)
    is_verb_pred = pred_verb is not None or pred.role in (_R_FIIL, _R_ULAC, _R_ORTAC)
    yuklem_turu = "fiil" if is_verb_pred else "isim"

    pred_tokens = [pred] + trailing
    pred_tokens.sort(key=lambda t: t.idx)

    # 3. Olumluluk
    pred_ana = pred_verb if pred_verb is not None else pred.best
    olumsuz = neg_nominal
    if pred_ana is not None and pred_ana.kwargs.get("negative"):
        olumsuz = True
    if _tr_lower(pred.surface) in _NEG_EXISTENTIAL:
        olumsuz = True
    olumluluk = "olumsuz" if olumsuz else "olumlu"

    # 4. Soru: yüklem Analysis'inde question=True de sayılır
    if pred_ana is not None and pred_ana.kwargs.get("question"):
        soru = True

    # 5. Kip (yalnız fiil yüklem)
    if is_verb_pred and pred_verb is not None:
        tense = pred_verb.kwargs.get("tense")
        if tense == "aorist" and _COND_SURFACE_RE.search(_tr_lower(pred.surface)):
            kip = "şart"
        else:
            kip = _TENSE_TO_KIP.get(tense, "haber")
    else:
        kip = "haber"

    # 6. Yüklemin yeri: yüklem bloğu (pred + trailing) cümle sonunda mı?
    last_pred_idx = max(t.idx for t in pred_tokens)
    yuklem_yeri = "kurallı" if last_pred_idx == n else "devrik"

    # 7. Öge çözümleme — yüklem DIŞI tüm gövde tokenları (yüklem-öncesi + devrik-kuyruk)
    body = [t for k, t in enumerate(toks)
            if k != pred_i and t.role not in (_R_SORU, _R_NEG)]

    elements, subordinate = _label_body(body)
    has_conj_body = any(t.role == _R_CONJ for t in body)

    # 7b. Emir cümlesinde özne kişi ekinde gramerleşir → yalın ad = hitap (cümle dışı unsur)
    if kip == "emir":
        elements = [
            Element("cümle dışı unsur", e.tokens, e.head_id)
            if e.label == "özne" else e
            for e in elements
        ]

    # 7c. özne / belirtisiz nesne heuristiği (nom öbekler) — YALNIZ tek-cümlede.
    # Çok-cümlede (sıralı/bağlı: gövdede koordinat yüklem VAR) her nom kendi cümlesinin
    # öznesi olabilir → heuristiği uygulama (Ali geldi ve Veli gitti: Veli=özne, nesne DEĞİL).
    body_has_verb = any(e.label == "yüklem" for e in elements)
    nom_subj = [e for e in elements if e.label == "özne"]
    if not body_has_verb and len(nom_subj) >= 2:
        last = max(nom_subj, key=lambda e: e.head_id)
        elements = [
            Element("belirtisiz nesne", e.tokens, e.head_id, e.aliases)
            if e is last else e
            for e in elements
        ]

    # 8. Yüklem ögesi
    pred_surf = tuple(t.surface for t in pred_tokens)
    elements.append(Element("yüklem", pred_surf, pred.idx))
    elements.sort(key=lambda e: e.head_id)

    # 9. Yapı: basit / birleşik / sıralı / bağlı
    main_verbs = [e for e in elements if e.label == "yüklem"]
    if subordinate:
        yapi = "birleşik"
    elif len(main_verbs) >= 2:
        yapi = "bağlı" if has_conj_body else "sıralı"
    else:
        yapi = "basit"

    eksiltili = not any(e.label == "yüklem" for e in elements)

    stype = SentenceType(
        yuklem_turu=yuklem_turu, yuklem_yeri=yuklem_yeri, olumluluk=olumluluk,
        soru=soru, kip=kip, yapi=yapi, eksiltili=eksiltili,
    )
    clauses = _segment_clauses(toks, tail, pred_i, trailing)
    return SentenceAnalysis(text, tuple(elements), stype, clauses)
