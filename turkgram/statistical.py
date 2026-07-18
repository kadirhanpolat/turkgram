"""İstatistiksel disambiguation katmanı (Faz 2b, madde A).

SPEC: spec/statistical-disambiguation-spec.md
OPT-IN: analyze/disambiguation.rank/context.rank_in_context DOKUNULMAZ.

İki model (paylaşımlı sayım tabanından):
  - Çarpımsal: aday-başına log-olasılık = emisyon; bağlamsız.
  - HMM + Viterbi: emisyon × geçiş bigram; cümle-düzeyi dizi çözümü.

Artım-1: kök + major POS hizalaması (SPEC §5).
  major_pos: Noun/Verb/Adj/Adverb/Postp/Num/Det/Pron/Punc/Conj/Interj
  Bilinmeyen → "unmapped"

Artım-2: tam eksen eşlemesi (SPEC §5).
  parse_oflazer_full → (lemma, major_pos, axes_dict)
  İnce-taneli HMM durumu: "Verb:past", "Noun:acc" vb.
  _analysis_fine_state(analysis) → ince durum (kind+kwargs'dan)

API (opt-in):
  load_model(emission_path=None, transition_path=None, fine=False) → StatModel
  rank_statistical(analyses, model, surface, fine=False) → sorted list
  viterbi(tokens, analyses_per_token, model, fine=False) → list of sorted lists

Gömülü model:
  data/disambig_emission_tr.tsv   — (major_pos, surface, log_prob)  [Artım-1]
  data/disambig_transition_tr.tsv — (prev_pos, next_pos, log_prob)  [Artım-1]
  data/disambig_emission_fine_tr.tsv   — (fine_state, surface, log_prob)  [Artım-2]
  data/disambig_transition_fine_tr.tsv — (prev_fine, next_fine, log_prob) [Artım-2]
  tools/build_disambig_model.py ile üretilir.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------

_SENTENCE_START = "<S>"
_SENTENCE_END = "</S>"

# Artım-1 Oflazer → major_pos tablosu (SPEC §5)
_OFLAZER_MAJOR: Dict[str, str] = {
    "Noun":   "Noun",
    "Verb":   "Verb",
    "Adj":    "Adj",
    "Adverb": "Adverb",
    "Postp":  "Postp",
    "Num":    "Num",
    "Det":    "Det",
    "Pron":   "Pron",
    "Punct":  "Punc",
    "Punc":   "Punc",
    "Conj":   "Conj",
    "Interj": "Interj",
    "Prop":   "Prop",
    # Diğer / bilinmeyen → unmapped (aşağıda fallback)
}

# Varsayılan düzgünleştirme (Laplace) — sıfır-olasılık önler
_SMOOTHING = 1e-9

# Çarpımsal yöntemde bilinen-dışı emisyon için düşük log-olasılık
_LOG_UNK = math.log(_SMOOTHING)


# ---------------------------------------------------------------------------
# Etiket çözümleme (Artım-1)
# ---------------------------------------------------------------------------

def parse_oflazer(analysis_str: str) -> Tuple[str, str]:
    """Oflazer analiz dizgesi → (lemma, major_pos).

    Kural (SPEC §5 Artım-1):
    - ^DB ile ayrılmış inflectional group'ların SON grubunun major POS'u alınır.
    - Kök (lemma) = ilk group'un başındaki sözcük (+öncesine kadar).
    - Bilinmeyen POS → "unmapped".

    Örnek:
      "hazin+Adj^DB+Noun+Zero+A3sg+Pnon+Dat" → ("hazin", "Noun")
      "yap+Verb+Pos^DB+Adj+PresPart"          → ("yap",   "Adj")
      "hazine+Noun+A3sg+Pnon+Nom"             → ("hazine","Noun")
    """
    if not analysis_str:
        return ("", "unmapped")

    # İlk + ile kök + geri kalan etiketler
    first_plus = analysis_str.find("+")
    if first_plus == -1:
        return (analysis_str, "unmapped")

    lemma = analysis_str[:first_plus]
    rest = analysis_str[first_plus + 1:]  # "Noun+A3sg+..." veya "Verb^DB+Adj+..."

    # ^DB gruplarına böl; son grubun ilk etiketini al
    db_groups = rest.split("^DB")
    last_group = db_groups[-1]  # son inflectional group
    # last_group başında "+" olabilir (^DB+Noun+...) → temizle
    last_group = last_group.lstrip("+")

    first_tag = last_group.split("+")[0]
    major_pos = _OFLAZER_MAJOR.get(first_tag, "unmapped")

    return (lemma, major_pos)


# ---------------------------------------------------------------------------
# Artım-2 etiket sözlükleri (SPEC §5)
# ---------------------------------------------------------------------------

_OFLAZER_PERSON: Dict[str, str] = {
    "A1sg": "1sg", "A2sg": "2sg", "A3sg": "3sg",
    "A1pl": "1pl", "A2pl": "2pl", "A3pl": "3pl",
}

_OFLAZER_POSSESSIVE: Dict[str, Optional[str]] = {
    "Pnon": None,    # iyeliksiz → atlanır
    "P1sg": "1sg", "P2sg": "2sg", "P3sg": "3sg",
    "P1pl": "1pl", "P2pl": "2pl", "P3pl": "3pl",
}

_OFLAZER_CASE: Dict[str, str] = {
    "Nom": "nom", "Acc": "acc", "Dat": "dat",
    "Loc": "loc", "Abl": "abl", "Gen": "gen", "Ins": "ins",
}

_OFLAZER_TENSE: Dict[str, str] = {
    "Past":  "past",
    "Narr":  "evid",    # rivayet -mIş
    "Fut":   "fut",
    "Aor":   "aorist",
    "Prog1": "pres",   # şimdiki -Iyor
    "Prog2": "pres",   # şimdiki -mAktA (daha nadir)
    "Pres":  "pres",   # Oflazer bazı kullanımlarda Pres
    "Cond":  "cond",   # şart -sA
    "Opt":   "opt",    # istek -A
    "Imp":   "imp",    # emir
    "Neces": "neces",  # gereklilik -mAlI
}

_OFLAZER_VOICE: Dict[str, str] = {
    "Caus":   "caus",
    "Pass":   "pass",
    "Reflex": "refl",
    "Recip":  "recip",
}

_OFLAZER_PTYPE: Dict[str, str] = {
    # Participle türleri
    "PresPart": "pres",
    "FutPart":  "fut",
    "PastPart": "past",
    "AorPart":  "aorist",
    # İsim-fiil türleri
    "Inf1": "inf1",
    "Inf2": "inf2",
    "Inf3": "inf3",
    "Ness": "ness",
    # Zarf türleri
    "While": "while",   # -ken/iken adverbial
    "Since": "since",   # -AlI
    "ByDoingSo": "by",  # -ArAk
    "Without":  "without",  # -mAdAn
    "AsLongAs": "aslong",   # -dIkçA
    # Zero → atlanır (sıfır türetme)
}


# ---------------------------------------------------------------------------
# Artım-2 — tam eksen çözümleme
# ---------------------------------------------------------------------------

def parse_oflazer_full(analysis_str: str) -> Tuple[str, str, dict]:
    """Oflazer analiz dizgesi → (lemma, major_pos, axes_dict).

    Artım-2 (SPEC §5): Tüm inflectional özellikler → turkgram eksen sözlüğü.
    ^DB zincirleri taranarak ses özellikleri (voice) toplanır.
    Bilinmeyen etiketler sessizce atlanır.

    axes_dict anahtarları (yalnız varsayılan-dışı değerler dahil):
      tense, person, negative (True), case, number ("pl"),
      possessive, voice (liste), ptype

    Örnek:
      "rahatla+Verb^DB+Verb+Caus+Pos+Past+A3sg"
      → ("rahatla", "Verb", {"tense":"past","person":"3sg","voice":["caus"]})
    """
    if not analysis_str:
        return ("", "unmapped", {})

    lemma, major_pos = parse_oflazer(analysis_str)  # Artım-1 kısmını yeniden kullan

    # Tüm grupları al (^DB sınırında böl)
    first_plus = analysis_str.find("+")
    if first_plus == -1:
        return (lemma, major_pos, {})

    # Tüm tag'leri düz listede topla (^DB işareti çıkarıldıktan sonra)
    rest = analysis_str[first_plus + 1:]  # lemma sonrası
    # ^DB'yi + ile değiştirip düz split
    flat_tags = rest.replace("^DB", "").split("+")
    flat_tags = [t.strip() for t in flat_tags if t.strip()]

    axes: dict = {}
    voice: list = []

    for tag in flat_tags:
        if tag in _OFLAZER_PERSON:
            # A3sg varsayılan (singular); yalnız A3pl özel
            if tag == "A3pl":
                axes["number"] = "pl"
            # person her zaman kaydedilir
            axes["person"] = _OFLAZER_PERSON[tag]
        elif tag in _OFLAZER_POSSESSIVE:
            poss = _OFLAZER_POSSESSIVE[tag]
            if poss is not None:
                axes["possessive"] = poss
        elif tag in _OFLAZER_CASE:
            axes["case"] = _OFLAZER_CASE[tag]
        elif tag in _OFLAZER_TENSE:
            axes["tense"] = _OFLAZER_TENSE[tag]
        elif tag == "Neg":
            axes["negative"] = True
        elif tag == "Pos":
            pass  # varsayılan, atlanır
        elif tag in _OFLAZER_VOICE:
            voice.append(_OFLAZER_VOICE[tag])
        elif tag in _OFLAZER_PTYPE:
            axes["ptype"] = _OFLAZER_PTYPE[tag]
        # Bilinmeyen etiketler (major POS tagları dahil) → sessizce atlanır

    if voice:
        axes["voice"] = voice

    return (lemma, major_pos, axes)


# ---------------------------------------------------------------------------
# Artım-2 — Analysis nesnesi → ince-taneli HMM durumu
# ---------------------------------------------------------------------------

def _analysis_fine_state(analysis) -> str:
    """turkgram Analysis nesnesinden Artım-2 ince-taneli HMM durumu türet.

    Kural (SPEC §5 Artım-2):
      Verb → "Verb:{tense}"   (bilinen tense varsa; yoksa "Verb")
      Noun → "Noun:{case}"    (bilinen case varsa; yoksa "Noun")
      Diğer → major_pos (Adj, Adverb, Postp, …)

    Bu fonksiyon yalnız Artım-2 fine model için kullanılır.
    Artım-1 için _analysis_pos kullanılmaya devam eder.
    """
    kind   = getattr(analysis, "kind",   "") or ""
    kwargs = getattr(analysis, "kwargs", {}) or {}

    # Fiil türleri → "Verb:{tense}"
    if kind in ("conjugate", "converb", "converb_casina", "converb_ken"):
        tense = kwargs.get("tense") or kwargs.get("base")
        if tense:
            return f"Verb:{tense}"
        return "Verb"

    # Sıfat-fiil/ad-fiil → Adj veya Noun (ptype'a göre)
    if kind == "participle":
        ptype = kwargs.get("ptype", "")
        if ptype in ("inf1", "inf2", "inf3", "ness"):
            # İsimleştirilmiş → Noun:{case}
            case = kwargs.get("case")
            if case:
                return f"Noun:{case}"
            return "Noun"
        # Sıfat-fiil → Adj
        return "Adj"

    # İsim çekimi → "Noun:{case}"
    if kind in ("decline",):
        case = kwargs.get("case")
        if case:
            return f"Noun:{case}"
        return "Noun"

    # Nominal ekfiil → "Noun" (kaba; copula Artım-2'de Noun)
    if kind in ("copula",):
        return "Noun"

    # Diğer sözcük sınıfları → `pos` alanından ince durum (Postp/Conj/Num/Adj).
    # Model ince-durum kümesi bu etiketleri içerir (_fine_state_from_oflazer emsali).
    pos = getattr(analysis, "pos", "") or ""
    _FINE = {"postp": "Postp", "conj": "Conj", "num": "Num", "adj": "Adj"}
    if pos in _FINE:
        return _FINE[pos]

    # Bilinmeyen / pos alanı yok (fake) → Noun (güvenli varsayılan, geriye uyum)
    return "Noun"


def _fine_state_from_oflazer(analysis_str: str) -> str:
    """Oflazer analiz dizgesinden ince-taneli HMM durumu türet.

    build_disambig_model.py'nin --fine modunda kullanır.
    Kural (SPEC §5 Artım-2 ince durum):
      Verb → "Verb:{tense}" | "Verb"
      Noun → "Noun:{case}" | "Noun"
      Diğer → major_pos
    """
    lemma, major_pos, axes = parse_oflazer_full(analysis_str)

    if major_pos == "Verb":
        tense = axes.get("tense")
        return f"Verb:{tense}" if tense else "Verb"

    if major_pos in ("Noun", "unmapped"):
        case = axes.get("case")
        return f"Noun:{case}" if case else "Noun"

    return major_pos  # Adj, Adverb, Postp, Num, Det, Pron, Punc, Conj, Interj


# ---------------------------------------------------------------------------
# Veri modeli
# ---------------------------------------------------------------------------

@dataclass
class StatModel:
    """Kompakt istatistiksel model.

    emission: {(major_pos, lower_surface): log_prob}
    transition: {(prev_pos, next_pos): log_prob}
    pos_set: bilinen major_pos'lar kümesi
    """
    emission: Dict[Tuple[str, str], float] = field(default_factory=dict)
    transition: Dict[Tuple[str, str], float] = field(default_factory=dict)
    pos_set: set = field(default_factory=set)

    def emit_lp(self, pos: str, surface: str) -> float:
        """P(yüzey | pos) log-olasılık; bilinmeyene yumuşatma."""
        return self.emission.get((pos, surface.lower()), _LOG_UNK)

    def trans_lp(self, prev: str, nxt: str) -> float:
        """P(nxt | prev) log-olasılık; bilinmeyene yumuşatma."""
        return self.transition.get((prev, nxt), _LOG_UNK)


# ---------------------------------------------------------------------------
# Model yükleme
# ---------------------------------------------------------------------------

_DATA_DIR = Path(__file__).parent / "data"
_DEFAULT_EMISSION   = _DATA_DIR / "disambig_emission_tr.tsv"
_DEFAULT_TRANSITION = _DATA_DIR / "disambig_transition_tr.tsv"


def load_model(
    emission_path: Optional[str | Path] = None,
    transition_path: Optional[str | Path] = None,
) -> StatModel:
    """Gömülü TSV'lerden (veya verilen yoldan) kompakt model yükle.

    TSV format (build_disambig_model.py çıktısı):
      emission_tr.tsv:    major_pos TAB surface TAB log_prob
      transition_tr.tsv:  prev_pos  TAB next_pos TAB log_prob

    Dosyalar yoksa boş model döner (testlerde sayım golden'ı inject eder).
    """
    ep = Path(emission_path) if emission_path else _DEFAULT_EMISSION
    tp = Path(transition_path) if transition_path else _DEFAULT_TRANSITION

    emission: Dict[Tuple[str, str], float] = {}
    transition: Dict[Tuple[str, str], float] = {}
    pos_set: set = set()

    if ep.exists():
        with open(ep, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) != 3:
                    continue
                pos, surf, lp = parts[0], parts[1], float(parts[2])
                emission[(pos, surf)] = lp
                pos_set.add(pos)

    if tp.exists():
        with open(tp, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) != 3:
                    continue
                prev, nxt, lp = parts[0], parts[1], float(parts[2])
                transition[(prev, nxt)] = lp
                pos_set.update([prev, nxt])

    pos_set.discard(_SENTENCE_START)
    pos_set.discard(_SENTENCE_END)
    return StatModel(emission=emission, transition=transition, pos_set=pos_set)


# ---------------------------------------------------------------------------
# Yardımcı — Analysis → (lemma, major_pos) çiftine çevir
# ---------------------------------------------------------------------------

# Analysis.pos → TrMor2018/Oflazer major_pos etiketi (gömülü model kümesiyle uyumlu).
# Bulgu (2026-07-19 eval): eski eşleme yalnız kind'a bakıp postp/conj/num/adj'ı
# Noun'a indiriyordu → HMM coverage %45'e kilitleniyordu. Analizör bu sözcük
# sınıflarını `pos` alanında zaten üretir; model Postp/Conj/Num/Adj emisyonlarına
# sahip → eşleme düzeltilince bedava coverage.
_POS_TO_MAJOR: Dict[str, str] = {
    "noun": "Noun", "verb": "Verb", "adj": "Adj",
    "num": "Num", "conj": "Conj", "postp": "Postp",
}


def _analysis_pos(analysis) -> str:
    """turkgram Analysis nesnesinden kaba major_pos türet.

    Fiil türleri (conjugate/converb*/participle) → Verb; nominal ekfiil (copula)
    → Noun (kaba). Diğer sözcük sınıfları `pos` alanından (postp→Postp, conj→Conj,
    num→Num, adj→Adj, noun→Noun). `pos` alanı yoksa (ör. test fake'i) → Noun (geriye uyum).
    """
    kind = getattr(analysis, "kind", "") or ""
    if kind in ("conjugate", "converb", "converb_casina", "converb_ken", "participle"):
        return "Verb"
    if kind == "copula":
        return "Noun"  # Artım-1: nominal ekfiil → Noun (kaba)
    pos = getattr(analysis, "pos", "") or ""
    return _POS_TO_MAJOR.get(pos, "Noun")


# Leksikon POS → major_pos (opsiyonel lexicon-aware katman; parse._leaf_tag emsali).
# Analizör çıplak sözcükleri decline(noun) verir; leksikon pos_map daha ince POS
# bilir (kırmızı=adj, iki=num, çünkü=conj, hızlı=adj, sen=pron). model pos_set bu
# etiketleri (Adverb/Det/Pron/Interj dahil) içerir → coverage kazancı. TrMor tagset'i
# ile leksikon arasında sistematik uyuşmazlık olabilir (her→adj vs Det) — düzeltmez,
# zarar da vermez (o token zaten yanlıştı). Bulgu: 2026-07-19-statistical-eval-bulgular §5c.
_LEX_POS_TO_MAJOR: Dict[str, str] = {
    "noun": "Noun", "verb": "Verb", "adj": "Adj", "num": "Num",
    "conj": "Conj", "postp": "Postp", "adv": "Adverb", "det": "Det",
    "pron": "Pron", "interj": "Interj",
}


def _analysis_pos_lex(analysis, pos_map: "Optional[Dict[str, str]]" = None) -> str:
    """Lexicon-aware major_pos: çıplak decline(noun) analizinde leksikon pos_map'e
    danış (daha ince sözcük sınıfı); aksi halde `_analysis_pos`.

    `pos_map=None` → dokunmadan `_analysis_pos` (geriye uyum). Fiil/postp/conj/num/adj
    zaten analizden geldiği için yalnız (kind=decline, pos=noun) durumu refine edilir.
    """
    base = _analysis_pos(analysis)
    if pos_map is None or base != "Noun":
        return base
    if getattr(analysis, "kind", "") != "decline":
        return base
    lemma = (getattr(analysis, "lemma", "") or "").lower()
    return _LEX_POS_TO_MAJOR.get(pos_map.get(lemma, ""), base)


# ---------------------------------------------------------------------------
# Çarpımsal skorlama (bağlamsız, token-başına)
# ---------------------------------------------------------------------------

def rank_statistical(
    analyses: Sequence,
    model: StatModel,
    surface: str = "",
    method: str = "product",
) -> List:
    """Analizleri istatistiksel skorlara göre sırala (büyükten küçüğe).

    method="product" : log P(surface | major_pos) — bağlamsız.
    method="hmm"     : tek-token için product ile aynı (HMM cümle için viterbi kullan).

    Girdi liste boşsa boş liste döner. DOKUNULMAZ: analyze/disambiguation.rank imzası.
    """
    if not analyses:
        return []
    surf_lower = surface.lower() if surface else ""

    def _score(a) -> float:
        pos = _analysis_pos(a)
        return model.emit_lp(pos, surf_lower) if surf_lower else _LOG_UNK

    return sorted(analyses, key=_score, reverse=True)


# ---------------------------------------------------------------------------
# HMM Viterbi (cümle-düzeyi dizi çözümü)
# ---------------------------------------------------------------------------

def viterbi(
    tokens: Sequence[str],
    analyses_per_token: Sequence[Sequence],
    model: StatModel,
    pos_fn=None,
) -> List[List]:
    """Viterbi algoritması — cümledeki her token için en iyi POS dizisini bul.

    Döner: analyses_per_token ile aynı uzunlukta liste; her eleman, o token'ın
    mevcut adayları Viterbi-optimal POS'una göre sıralanmış (en iyi baştaki).
    Sıralama: seçilen POS'a ait adaylar öne, diğerleri arkaya; kendi içinde
    girdi sırası korunur (kararlı).

    analyses_per_token[i] = Analysis nesnelerinin listesi.
    Boş aday listesi → çıkışta da boş.

    pos_fn: Analysis → major_pos fonksiyonu (varsayılan `_analysis_pos`).
    Lexicon-aware coverage için `lambda a: _analysis_pos_lex(a, pos_map)` geçilebilir
    (golden fake-testleri varsayılanı kullanır → dokunulmaz).
    """
    if pos_fn is None:
        pos_fn = _analysis_pos
    n = len(tokens)
    if n == 0:
        return []

    # Her token'ın aday pos kümesi
    def _cand_pos(i: int) -> List[str]:
        candidates = analyses_per_token[i]
        if not candidates:
            return [_SENTENCE_END]  # sentinel
        seen: list = []
        for a in candidates:
            p = pos_fn(a)
            if p not in seen:
                seen.append(p)
        return seen

    # Viterbi tablosu
    # vt[i][pos] = (max log-prob, prev_pos)
    vt: List[Dict[str, Tuple[float, str]]] = [{} for _ in range(n)]

    # t=0: <S> → pos × emit(pos, tokens[0])
    surf0 = tokens[0].lower()
    for pos in _cand_pos(0):
        lp = (model.trans_lp(_SENTENCE_START, pos)
              + model.emit_lp(pos, surf0))
        vt[0][pos] = (lp, _SENTENCE_START)

    # t=1..n-1
    for t in range(1, n):
        surf_t = tokens[t].lower()
        for pos in _cand_pos(t):
            best_lp = -math.inf
            best_prev = ""
            for prev_pos, (prev_lp, _) in vt[t - 1].items():
                lp = (prev_lp
                      + model.trans_lp(prev_pos, pos)
                      + model.emit_lp(pos, surf_t))
                if lp > best_lp:
                    best_lp = lp
                    best_prev = prev_pos
            if best_lp > -math.inf:
                vt[t][pos] = (best_lp, best_prev)

    # Son adım: pos → </S> geçişiyle en iyi son pos
    best_final_lp = -math.inf
    best_final_pos = ""
    for pos, (lp, _) in vt[n - 1].items():
        total = lp + model.trans_lp(pos, _SENTENCE_END)
        if total > best_final_lp:
            best_final_lp = total
            best_final_pos = pos

    # Geri-iz (backtrack)
    best_path: List[str] = [""] * n
    best_path[n - 1] = best_final_pos
    for t in range(n - 2, -1, -1):
        best_path[t] = vt[t + 1][best_path[t + 1]][1]

    # Sonuç: her token'ın adaylarını seçilen POS öne gelecek şekilde sırala
    result: List[List] = []
    for i, cands in enumerate(analyses_per_token):
        if not cands:
            result.append([])
            continue
        selected_pos = best_path[i]
        # Seçilen POS'a uyan adaylar öne, geri kalan girdi sırasında
        first  = [a for a in cands if pos_fn(a) == selected_pos]
        second = [a for a in cands if pos_fn(a) != selected_pos]
        result.append(first + second)

    return result


# ---------------------------------------------------------------------------
# Sayım tablosundan model oluşturma (test & build yardımcısı)
# ---------------------------------------------------------------------------

def model_from_counts(
    emission_counts: Dict[Tuple[str, str], int],
    transition_counts: Dict[Tuple[str, str], int],
    smoothing: float = _SMOOTHING,
) -> StatModel:
    """Ham sayım tablolarından normalize edilmiş log-prob modeli üret.

    Emisyon: P(surface | pos) = (count + smoothing) / (pos_total + V * smoothing)
    Geçiş:   P(next | prev)   = (count + smoothing) / (prev_total + S * smoothing)
    V = benzersiz yüzey sayısı, S = benzersiz next_pos sayısı.

    build_disambig_model.py ve sayım golden'ı bu yardımcıyı kullanır.
    """
    # Emisyon
    pos_surf_total: Dict[str, float] = {}
    surf_per_pos: Dict[str, set] = {}
    for (pos, surf), cnt in emission_counts.items():
        pos_surf_total[pos] = pos_surf_total.get(pos, 0) + cnt
        surf_per_pos.setdefault(pos, set()).add(surf)

    emission: Dict[Tuple[str, str], float] = {}
    pos_set: set = set()
    for (pos, surf), cnt in emission_counts.items():
        v = len(surf_per_pos.get(pos, set()))
        denom = pos_surf_total[pos] + v * smoothing
        emission[(pos, surf)] = math.log((cnt + smoothing) / denom)
        pos_set.add(pos)

    # Geçiş
    prev_total: Dict[str, float] = {}
    next_per_prev: Dict[str, set] = {}
    for (prev, nxt), cnt in transition_counts.items():
        prev_total[prev] = prev_total.get(prev, 0) + cnt
        next_per_prev.setdefault(prev, set()).add(nxt)

    transition: Dict[Tuple[str, str], float] = {}
    for (prev, nxt), cnt in transition_counts.items():
        s = len(next_per_prev.get(prev, set()))
        denom = prev_total[prev] + s * smoothing
        transition[(prev, nxt)] = math.log((cnt + smoothing) / denom)

    return StatModel(emission=emission, transition=transition, pos_set=pos_set)
