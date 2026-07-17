# Faz E — Sözdizim Genişletme İmplementasyon Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Turkgram kütüphanesine zengin öbek üretimi (E1), constituency parser (E2), dependency graph çıkarımı (E5) ve CoNLL-U export (E6) ekle.

**Architecture:** E1 mevcut `syntax.py`'yi 4 yeni fonksiyonla genişletir; E2 yeni `parse.py` modülü ile kural-tabanlı constituency ağacı üretir; E5+E6 yeni `dependency.py` modülü ile ağacı UD-uyumlu dependency graph'a ve CoNLL-U metnine dönüştürür. Tüm veri yapıları `frozen=True` dataclass; sıfır dış bağımlılık.

**Tech Stack:** Python 3.10+, pytest, mevcut turkgram primitifleri (decline, conjugate, postposition, conjunction.coordinate, disambiguation.rank, analysis.parse_text, tokenize)

**Spec:** `docs/superpowers/specs/2026-07-17-faz-e-sozdizim-design.md`

**İş akışı (CLAUDE.md §2):** SPEC → bağımsız golden (motor-körü) → motor → hakem (regresyon + 0 çökme)

**Windows notu:** Türkçe karakter yazan `python` komutlarını `PYTHONUTF8=1 python ...` ile çalıştır. `pytest` komutlarında bu şart değil.

---

## Dosya Yapısı

| Dosya | Durum | Sorumluluk |
|-------|-------|-----------|
| `turkgram/syntax.py` | Değiştirilecek | E1: np_uret, pp_uret, degmod_uret, koordine_np |
| `turkgram/parse.py` | Yeni | E2: LeafNode, PhraseNode, parse_phrase |
| `turkgram/dependency.py` | Yeni | E5+E6: DepToken, constituency_to_dep, to_conllu |
| `turkgram/__init__.py` | Değiştirilecek | Yeni API'lerin export'u |
| `turkgram/tr.py` | Değiştirilecek | Türkçe sarmalayıcılar |
| `tests/golden_syntax_rich.py` | Yeni | E1 bağımsız golden (elle doğrulanmış) |
| `tests/test_syntax_rich.py` | Yeni | E1 runner |
| `tests/golden_parse.py` | Yeni | E2 bağımsız golden |
| `tests/test_parse.py` | Yeni | E2 runner |
| `tests/golden_dependency.py` | Yeni | E5 bağımsız golden |
| `tests/golden_conllu.py` | Yeni | E6 bağımsız golden |
| `tests/test_dependency.py` | Yeni | E5+E6 runner |
| `tools/sweep_syntax_e.py` | Yeni | Corpus hakem aracı |

---

## Task 1: E1 — Bağımsız Golden Testi Yaz (Motor-Körü)

**Files:**
- Create: `tests/golden_syntax_rich.py`

Bu golden motordan bağımsız, dilbilgisinden elle doğrulanmış biçimler içerir.  
**ÖNEMLİ:** Bu dosyayı yazarken `syntax.py`'yi AÇMA — yalnız spec §3 + Türkçe dilbilgisini kullan.

- [x] **Step 1: Golden dosyasını oluştur**

```python
# tests/golden_syntax_rich.py
"""E1 zengin öbek üretimi — bağımsız golden (motor-körü, elle doğrulanmış).

Her giriş: (fonksiyon, kwargs, beklenen_çıktı)
"""

NP_URET_CASES = [
    # (head, kwargs, beklenen)
    ("kapı",  {"durum": "nom"},                              "kapı"),
    ("kapı",  {"tamlayan": "ev"},                           "evin kapısı"),
    ("kapı",  {"tamlayan": "ev", "durum": "acc"},           "evin kapısını"),
    ("kapı",  {"on_sifatlar": ("büyük",), "tamlayan": "ev", "durum": "acc"}, "büyük evin kapısını"),
    ("kitap", {"miktar": "üç", "durum": "dat"},             "üç kitaba"),
    ("araba", {"on_sifatlar": ("kırmızı", "büyük")},        "kırmızı büyük araba"),
    ("ev",    {"iyelik": "1sg"},                            "evim"),
    ("ev",    {"iyelik": "2sg", "durum": "dat"},            "evine"),
    ("öğrenci", {"tamlayan": "okul"},                       "okulun öğrencisi"),
]

PP_URET_CASES = [
    # (isim, edat, kwargs, beklenen)
    ("ev",    "göre",  {},                  "eve göre"),
    ("okul",  "için",  {},                  "okul için"),
    ("okul",  "ile",   {"bitişik": True},   "okulla"),
    ("araba", "kadar", {},                  "arabaya kadar"),
    ("ben",   "göre",  {},                  "bana göre"),
]

DEGMOD_URET_CASES = [
    # (baş, kwargs, beklenen)
    ("hızlı",   {},                    "hızlı"),
    ("hızlı",   {"derece": "çok"},     "çok hızlı"),
    ("güzel",   {"derece": "oldukça"}, "oldukça güzel"),
    ("iyi",     {"derece": "en"},      "en iyi"),
    ("büyük",   {"derece": "daha"},    "daha büyük"),
]

KOORDINE_NP_CASES = [
    # (ogeler, baglac, beklenen)
    (["kitap", "defter"],         "ve",   "kitap ve defter"),
    (["kitap", "defter"],         "veya", "kitap veya defter"),
    (["kitap", "defter", "kalem"], "ve",  "kitap, defter ve kalem"),
    (["ev", "araba"],             "ama",  "ev ama araba"),
]
```

- [x] **Step 2: Golden'ı manuel gözden geçir**

Her satırı Türkçe morfoloji açısından kontrol et:
- `evin kapısını`: ev→gen=evin; kapı→3sg-poss+acc=kapısını ✓
- `üç kitaba`: kitap→dat=kitaba; miktar önde ✓
- `bana göre`: ben→dat=bana (zamir); için değil göre ✓

---

## Task 2: E1 — Runner Testi Yaz

**Files:**
- Create: `tests/test_syntax_rich.py`

- [x] **Step 1: Runner dosyasını oluştur**

```python
# tests/test_syntax_rich.py
"""E1 zengin öbek üretimi runner."""
import pytest
from tests.golden_syntax_rich import (
    NP_URET_CASES, PP_URET_CASES, DEGMOD_URET_CASES, KOORDINE_NP_CASES,
)
from turkgram.syntax import np_uret, pp_uret, degmod_uret, koordine_np


@pytest.mark.parametrize("head,kwargs,expected", NP_URET_CASES)
def test_np_uret(head, kwargs, expected):
    assert np_uret(head, **kwargs) == expected


@pytest.mark.parametrize("isim,edat,kwargs,expected", PP_URET_CASES)
def test_pp_uret(isim, edat, kwargs, expected):
    assert pp_uret(isim, edat, **kwargs) == expected


@pytest.mark.parametrize("bas,kwargs,expected", DEGMOD_URET_CASES)
def test_degmod_uret(bas, kwargs, expected):
    assert degmod_uret(bas, **kwargs) == expected


@pytest.mark.parametrize("ogeler,baglac,expected", KOORDINE_NP_CASES)
def test_koordine_np(ogeler, baglac, expected):
    assert koordine_np(ogeler, baglac) == expected
```

- [x] **Step 2: Testlerin başarısız olduğunu doğrula**

```bash
pytest tests/test_syntax_rich.py -v
```

Beklenti: `ImportError: cannot import name 'np_uret' from 'turkgram.syntax'`

---

## Task 3: E1 — Implementasyon

**Files:**
- Modify: `turkgram/syntax.py`

- [x] **Step 1: np_uret fonksiyonunu ekle**

`turkgram/syntax.py` sonuna ekle (mevcut `__all__` öncesi):

```python
# ---------------------------------------------------------------------------
# §4 — Zengin öbek üretimi (E1)
# ---------------------------------------------------------------------------

def np_uret(
    head: str,
    *,
    on_sifatlar: tuple[str, ...] = (),
    tamlayan: str | None = None,
    miktar: str | None = None,
    durum: str = "nom",
    iyelik: str | None = None,
) -> str:
    """Karmaşık isim öbeği üret (spec §3.1).

    Üretim sırası: miktar? + on_sifatlar* + tamlayan-GEN? + head-case-poss
    """
    parts: list[str] = []
    if miktar is not None:
        parts.append(miktar.lower().strip())
    for sifat in on_sifatlar:
        parts.append(sifat.lower().strip())
    if tamlayan is not None:
        parts.append(decline(tamlayan, case="gen"))
    kwargs: dict[str, str] = {"case": durum}
    if iyelik is not None:
        kwargs["possessive"] = iyelik
    if tamlayan is not None and iyelik is None:
        kwargs["possessive"] = "3sg"
    parts.append(decline(head, **kwargs))
    return " ".join(parts)


def pp_uret(isim: str, edat: str, *, bitişik: bool = False) -> str:
    """Edat öbeği üret (spec §3.2). postposition() sarmalayıcı."""
    from .postposition import postposition
    return postposition(isim, edat, bitişik=bitişik)


def degmod_uret(baş: str, *, derece: str | None = None) -> str:
    """Derece değiştiricili öbek üret (spec §3.3)."""
    _VALID_DERECE = {"çok", "oldukça", "pek", "biraz", "en", "daha"}
    if derece is not None and derece not in _VALID_DERECE:
        raise ValueError(
            f"Geçersiz derece: {derece!r}. Geçerli: {sorted(_VALID_DERECE)}"
        )
    if derece is None:
        return baş.lower().strip()
    return f"{derece} {baş.lower().strip()}"


def koordine_np(
    ogeler: tuple[str, ...] | list[str],
    baglac: str = "ve",
) -> str:
    """Koordinasyon öbeği üret (spec §3.4). conjunction.coordinate() sarmalayıcı."""
    from .conjunction import coordinate
    # "ile" kapsam dışı — conjunction._VALID_CONJ'de yok (comitative postposition)
    _SIMPLE_CONJ = {"ve", "veya", "ya da", "ama", "fakat", "ancak"}
    if baglac not in _SIMPLE_CONJ:
        raise ValueError(
            f"Korelatif bağlaçlar desteklenmez: {baglac!r}. Geçerli: {sorted(_SIMPLE_CONJ)}"
        )
    return coordinate(list(ogeler), baglac)
```

- [x] **Step 2: `__all__`'ı güncelle**

```python
__all__ = [
    "isim_tamlamasi",
    "sifat_tamlamasi",
    "cumle_uret",
    "np_uret",
    "pp_uret",
    "degmod_uret",
    "koordine_np",
]
```

- [x] **Step 3: Testleri çalıştır**

```bash
pytest tests/test_syntax_rich.py -v
```

Beklenti: Tüm testler yeşil. Başarısız olanlar varsa golden'ı değil implementasyonu düzelt.

- [x] **Step 4: Tüm paketi çalıştır**

```bash
pytest --ignore=tests/test_slow_roundtrip.py -q
```

Beklenti: Önceki test sayısına yeni testler eklendi; regresyon yok.

- [x] **Step 5: Commit**

```bash
git add turkgram/syntax.py tests/golden_syntax_rich.py tests/test_syntax_rich.py
git commit -m "feat(syntax): E1 zengin öbek üretimi — np_uret/pp_uret/degmod_uret/koordine_np"
```

---

## Task 4: E1 — TR API

**Files:**
- Modify: `turkgram/tr.py`

- [x] **Step 1: Türkçe sarmalayıcıları ekle**

`tr.py` içinde uygun yere (diğer sarmalayıcıların yanına) ekle:

```python
# E1 — Zengin öbek üretimi (syntax.py sarmalayıcılar)
def isim_obeği(
    baş: str,
    *,
    on_sifatlar: tuple[str, ...] = (),
    tamlayan: str | None = None,
    miktar: str | None = None,
    durum: str = "yalın",
    iyelik: str | None = None,
) -> str:
    """Türkçe isim öbeği. np_uret() sarmalayıcı."""
    from .syntax import np_uret
    _durum = _DURUM.get(_tr_lower(durum), durum)
    _iyelik = _KISI.get(_tr_lower(iyelik), iyelik) if iyelik else None
    return np_uret(baş, on_sifatlar=on_sifatlar, tamlayan=tamlayan,
                   miktar=miktar, durum=_durum, iyelik=_iyelik)


def edat_obeği_zengin(isim: str, edat: str, *, bitişik: bool = False) -> str:
    """Edat öbeği (pp_uret sarmalayıcı — edat_obeği adı zaten mevcut)."""
    from .syntax import pp_uret
    return pp_uret(isim, edat, bitişik=bitişik)


def derece_obeği(baş: str, *, derece: str | None = None) -> str:
    """Derece değiştirici öbek. degmod_uret() sarmalayıcı."""
    from .syntax import degmod_uret
    return degmod_uret(baş, derece=derece)


def koordinasyon(
    ogeler: tuple[str, ...] | list[str],
    baglac: str = "ve",
) -> str:
    """Koordinasyon öbeği. koordine_np() sarmalayıcı."""
    from .syntax import koordine_np
    return koordine_np(ogeler, baglac)
```

- [x] **Step 2: TR denklik testi ekle**

`tests/test_syntax_rich.py`'ye ekle:

```python
def test_tr_isim_obeği_denklik():
    from turkgram.tr import isim_obeği
    assert isim_obeği("kapı", tamlayan="ev") == np_uret("kapı", tamlayan="ev")

def test_tr_derece_obeği_denklik():
    from turkgram.tr import derece_obeği
    assert derece_obeği("hızlı", derece="çok") == degmod_uret("hızlı", derece="çok")
```

- [x] **Step 3: Testleri çalıştır ve commit et**

```bash
pytest tests/test_syntax_rich.py -v
git add turkgram/tr.py tests/test_syntax_rich.py
git commit -m "feat(tr): E1 Türkçe sarmalayıcılar — isim_obeği/derece_obeği/koordinasyon"
```

---

## Task 5: E2 — parse.py Veri Yapıları

**Files:**
- Create: `turkgram/parse.py`

- [x] **Step 1: Temel dosyayı oluştur**

```python
# turkgram/parse.py
"""parse.py — Constituency parser (Faz E2).

API:
    LeafNode       — yaprak düğüm (token + analiz + etiket)
    PhraseNode     — öbek düğüm (tag + children + surface)
    parse_phrase   — token listesi → PhraseNode ağacı
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .analysis import Analysis


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


__all__ = ["LeafNode", "PhraseNode", "parse_phrase"]
```

- [x] **Step 2: parse_phrase taslak ekle (ImportError vermemesi için)**

```python
def parse_phrase(
    tokens: list[str],
    analyses: list[list["Analysis"]],
) -> PhraseNode:
    """Token listesi + analiz listesi → constituency ağacı (kök: 'S').

    Giriş:
        tokens:   tokenize() çıktısı
        analyses: parse_text() çıktısı (her token için analiz listesi)
    Çıkış:
        PhraseNode(tag='S', ...)
    """
    raise NotImplementedError("E2 parser henüz implemente edilmedi")
```

- [x] **Step 3: Commit**

```bash
git add turkgram/parse.py
git commit -m "feat(parse): E2 LeafNode/PhraseNode dataclass'lar + parse_phrase taslak"
```

---

## Task 6: E2 — Bağımsız Golden Testi Yaz (Motor-Körü)

**Files:**
- Create: `tests/golden_parse.py`

**ÖNEMLİ:** Bu dosyayı yazarken `parse.py`'yi AÇMA — yalnız spec §4 + Türkçe dilbilgisi.  
Golden, beklenen ağaç yapısını `dict` formatında tanımlar (dataclass gerektirmez).

- [x] **Step 1: Golden dosyasını oluştur**

```python
# tests/golden_parse.py
"""E2 constituency parser — bağımsız golden (motor-körü, elle doğrulanmış).

Her giriş:
    text:     giriş cümlesi
    roots:    analyze() roots kümesi (precision için)
    expected: beklenen ağaç {tag, surface, children: [{tag, surface, token?}]}

Basit cümleler: özne + yüklem veya yalnız öbek.
"""

PARSE_CASES = [
    {
        "text": "öğrenci okudu",
        "roots": {"öğrenci", "okumak"},
        "expected": {
            "tag": "S",
            "surface": "öğrenci okudu",
            "children": [
                {"tag": "NP", "surface": "öğrenci",
                 "children": [{"tag": "NOUN", "token": "öğrenci"}]},
                {"tag": "VP", "surface": "okudu",
                 "children": [{"tag": "VERB", "token": "okudu"}]},
            ],
        },
    },
    {
        "text": "büyük ev",
        "roots": {"büyük", "ev"},
        "expected": {
            "tag": "NP",
            "surface": "büyük ev",
            "children": [
                {"tag": "ADJ",  "token": "büyük"},
                {"tag": "NOUN", "token": "ev"},
            ],
        },
    },
    {
        "text": "eve göre",
        "roots": {"ev"},
        "expected": {
            "tag": "PP",
            "surface": "eve göre",
            "children": [
                {"tag": "NP",  "surface": "eve",  "children": [{"tag": "NOUN", "token": "eve"}]},
                {"tag": "ADP", "token": "göre"},
            ],
        },
    },
    {
        "text": "kitap ve defter",
        "roots": {"kitap", "defter"},
        "expected": {
            "tag": "CoordP",
            "surface": "kitap ve defter",
            "children": [
                {"tag": "NP", "surface": "kitap",  "children": [{"tag": "NOUN", "token": "kitap"}]},
                {"tag": "CCONJ", "token": "ve"},
                {"tag": "NP", "surface": "defter", "children": [{"tag": "NOUN", "token": "defter"}]},
            ],
        },
    },
    {
        # AdjP+NOUN: derece+sıfat → AdjP; AdjP+NOUN → NP (_apply_r1 backtracking)
        # Invariant: R3 çalıştıktan sonra her `nodes[k]` (start<=k<i) tam 1 slot kaplar
        "text": "çok büyük ev",
        "roots": {"büyük", "ev"},
        "expected": {
            "tag": "NP",
            "surface": "çok büyük ev",
            "children": [
                {"tag": "AdjP", "surface": "çok büyük",
                 "children": [
                     {"tag": "ADJ", "token": "çok"},
                     {"tag": "ADJ", "token": "büyük"},
                 ]},
                {"tag": "NOUN", "token": "ev"},
            ],
        },
    },
    {
        "text": "öğrenci kitabı okudu",
        "roots": {"öğrenci", "kitap", "okumak"},
        "expected": {
            "tag": "S",
            "surface": "öğrenci kitabı okudu",
            "children": [
                {"tag": "NP", "surface": "öğrenci",
                 "children": [{"tag": "NOUN", "token": "öğrenci"}]},
                {"tag": "VP", "surface": "kitabı okudu",
                 "children": [
                     {"tag": "NP", "surface": "kitabı",
                      "children": [{"tag": "NOUN", "token": "kitabı"}]},
                     {"tag": "VERB", "token": "okudu"},
                 ]},
            ],
        },
    },
]
```

- [x] **Step 2: Golden'ı gözden geçir**

Her ağacı Türkçe dilbilgisiyle kontrol et:
- `büyük ev`: sıfat + isim → NP, sıfat çekilmez ✓
- `eve göre`: `göre` datif yönetir → `ev → eve`; `göre` ADP ✓
- `kitap ve defter`: `ve` CCONJ → CoordP ✓

---

## Task 7: E2 — Runner Testi Yaz

**Files:**
- Create: `tests/test_parse.py`

- [x] **Step 1: Runner dosyasını oluştur**

```python
# tests/test_parse.py
"""E2 constituency parser runner."""
import pytest
from tests.golden_parse import PARSE_CASES
from turkgram import tokenize, parse_text
from turkgram.parse import LeafNode, PhraseNode, parse_phrase


def _node_matches(node: PhraseNode | LeafNode, expected: dict) -> bool:
    """Ağaç düğümünü beklenen sözlükle karşılaştır."""
    if isinstance(node, LeafNode):
        return (
            node.tag == expected.get("tag")
            and node.token == expected.get("token")
        )
    if node.tag != expected.get("tag"):
        return False
    if "surface" in expected and node.surface != expected["surface"]:
        return False
    exp_children = expected.get("children", [])
    if len(node.children) != len(exp_children):
        return False
    return all(_node_matches(c, e) for c, e in zip(node.children, exp_children))


@pytest.mark.parametrize("case", PARSE_CASES, ids=[c["text"] for c in PARSE_CASES])
def test_parse_phrase(case):
    tokens = tokenize(case["text"])
    analyses = parse_text(case["text"])
    tree = parse_phrase(tokens, analyses)
    assert _node_matches(tree, case["expected"]), (
        f"\nBeklenen:\n{case['expected']}\nAlınan:\n{tree}"
    )
```

- [x] **Step 2: Testin başarısız olduğunu doğrula**

```bash
pytest tests/test_parse.py -v
```

Beklenti: `NotImplementedError: E2 parser henüz implemente edilmedi`

---

## Task 8: E2 — parse_phrase İmplementasyonu

**Files:**
- Modify: `turkgram/parse.py`

- [x] **Step 1: Etiket üretim yardımcısını ekle**

`parse.py`'nin başına import'ları ekle ve `_leaf_tag` fonksiyonunu yaz:

```python
from .postposition import _POSTPOSITION_CASE as _POSTPOSITION_CASE_MAP

_POSTPOSITIONS: frozenset[str] = frozenset(_POSTPOSITION_CASE_MAP.keys())


def _leaf_tag(token: str, analysis: "Analysis | None") -> str:
    """İki adımlı etiket üretimi (spec §4.4)."""
    # Adım 0: yüzey tabanlı (edat — analiz sistemi dışında)
    if token.lower() in _POSTPOSITIONS:
        return "ADP"
    if analysis is None:
        return "X"
    # Adım 1: kind tabanlı geçersiz kılmalar
    if analysis.kind == "copula":
        return "VERB"
    # participle: pos='verb' ama R1b kuralı için VERB kalır
    # Adım 2: pos tabanlı
    _POS_TO_TAG = {
        "verb": "VERB",
        "noun": "NOUN",
        "adj":  "ADJ",
        "num":  "NUM",
        "conj": "CCONJ",
    }
    return _POS_TO_TAG.get(analysis.pos, "X")
```

- [x] **Step 2: parse_phrase implementasyonunu yaz**

```python
def parse_phrase(
    tokens: list[str],
    analyses: list[list["Analysis"]],
) -> PhraseNode:
    """Token listesi + analiz listesi → constituency ağacı (kök: 'S')."""
    from .disambiguation import rank as _rank

    # 1. Yaprak düğümleri oluştur
    leaves: list[LeafNode] = []
    for token, token_analyses in zip(tokens, analyses):
        # hypothetical analizleri filtrele
        real = [a for a in token_analyses if not a.hypothetical]
        best = _rank(real)[0] if real else None
        tag = _leaf_tag(token, best)
        leaves.append(LeafNode(tag=tag, token=token, analysis=best))

    # 2. Bottom-up gruplama
    nodes: list[PhraseNode | LeafNode] = list(leaves)
    nodes = _apply_r3(nodes)   # AdjP önce (derece + baş)
    nodes = _apply_r1(nodes)   # NP (sıfat* + isim + tamlama*)
    nodes = _apply_r1b(nodes)  # fiilimsi NP
    nodes = _apply_r2(nodes)   # PP (NP + ADP)
    nodes = _apply_r4(nodes)   # CoordP (NP + CCONJ + NP)
    nodes = _apply_r5(nodes)   # S (NP*/PP*/AdjP* + VP)
    nodes = _wrap_bare_vp(nodes)

    # 3. Kök düğüm
    if len(nodes) == 1 and isinstance(nodes[0], PhraseNode):
        root = nodes[0]
        if root.tag != "S":
            root = PhraseNode.make("S", (root,))
    else:
        root = PhraseNode.make("S", tuple(nodes))
    return root
```

- [x] **Step 3: Kural yardımcılarını yaz**

```python
def _tag(node: PhraseNode | LeafNode) -> str:
    return node.tag if isinstance(node, LeafNode) else node.tag


def _apply_r3(nodes: list) -> list:
    """R3: ADJ ADJ* → AdjP (derece + baş)."""
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
    """R1: (ADJ|NUM|AdjP)* NOUN (GEN-NOUN POSS-NOUN)* → NP."""
    out, i = [], 0
    while i < len(nodes):
        node = nodes[i]
        if _tag(node) == "NOUN":
            # sola doğru modifierleri topla
            start = i
            while start > 0 and _tag(nodes[start - 1]) in ("ADJ", "NUM", "AdjP"):
                start -= 1
            # sağa doğru belirtili tamlama: GEN-NOUN + POSS-NOUN çiftleri
            end = i + 1
            while (end + 1 < len(nodes)
                   and _tag(nodes[end]) == "NOUN"
                   and isinstance(nodes[end], LeafNode)
                   and nodes[end].analysis is not None
                   and nodes[end].analysis.kwargs.get("case") == "gen"
                   and _tag(nodes[end + 1]) == "NOUN"):
                end += 2
            group = tuple(nodes[start:end])
            # önceden işlenmiş modifieri geri al
            out = out[:len(out) - (i - start)]
            out.append(PhraseNode.make("NP", group))
            i = end
        else:
            out.append(node)
            i += 1
    return out


def _apply_r1b(nodes: list) -> list:
    """R1b: VERB[kind=participle] NOUN → NP."""
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
    """R2: NP ADP → PP."""
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
                and _tag(nodes[i + 2]) in ("NP",)):
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
    """R5: (NP|PP|AdjP|CoordP)* VP → S."""
    verb_indices = [
        i for i, n in enumerate(nodes)
        if _tag(n) == "VERB" or (isinstance(n, PhraseNode) and n.tag == "VP")
    ]
    if not verb_indices:
        return nodes
    vi = verb_indices[-1]  # son fiil = yüklem
    vp_node = nodes[vi]
    if isinstance(vp_node, LeafNode):
        # VP'nin solundaki bağımlıları topla
        vp_children: list = [vp_node]
        left = vi - 1
        while left >= 0 and _tag(nodes[left]) in ("NP", "PP", "AdjP", "CoordP", "NOUN"):
            np = nodes[left]
            if isinstance(np, LeafNode) and np.tag == "NOUN":
                np = PhraseNode.make("NP", (np,))
            vp_children.insert(0, np)
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
```

- [x] **Step 4: Testleri çalıştır**

```bash
pytest tests/test_parse.py -v
```

Beklenti: Tüm PARSE_CASES yeşil.

- [x] **Step 5: Regresyon kontrolü**

```bash
pytest --ignore=tests/test_slow_roundtrip.py -q
```

Beklenti: Tüm önceki testler hâlâ yeşil.

- [x] **Step 6: Commit**

```bash
git add turkgram/parse.py tests/golden_parse.py tests/test_parse.py
git commit -m "feat(parse): E2 constituency parser — parse_phrase R1-R5 kuralları"
```

---

## Task 9: E5+E6 — Bağımsız Golden Testleri Yaz (Motor-Körü)

**Files:**
- Create: `tests/golden_dependency.py`
- Create: `tests/golden_conllu.py`

**ÖNEMLİ:** `dependency.py`'yi AÇMA — yalnız spec §5-6 + UD standardı.

- [x] **Step 1: Dependency golden'ı oluştur**

```python
# tests/golden_dependency.py
"""E5 dependency graph — bağımsız golden (motor-körü).

Her giriş: cümle metni + beklenen DepToken listesi (dict formatında).
"""

DEP_CASES = [
    {
        "text": "öğrenci okudu",
        "roots": {"öğrenci", "okumak"},
        "expected": [
            {"id": 1, "form": "öğrenci", "lemma": "öğrenci", "upos": "NOUN",
             "head": 2, "deprel": "nsubj"},
            {"id": 2, "form": "okudu",   "lemma": "okumak",  "upos": "VERB",
             "head": 0, "deprel": "root"},
        ],
    },
    {
        "text": "öğrenci kitabı okudu",
        "roots": {"öğrenci", "kitap", "okumak"},
        "expected": [
            {"id": 1, "form": "öğrenci", "lemma": "öğrenci", "upos": "NOUN",
             "head": 3, "deprel": "nsubj"},
            {"id": 2, "form": "kitabı",  "lemma": "kitap",   "upos": "NOUN",
             "head": 3, "deprel": "obj"},
            {"id": 3, "form": "okudu",   "lemma": "okumak",  "upos": "VERB",
             "head": 0, "deprel": "root"},
        ],
    },
    {
        "text": "evin kapısını gördüm",
        "roots": {"ev", "kapı", "görmek"},
        "expected": [
            {"id": 1, "form": "evin",     "lemma": "ev",     "upos": "NOUN",
             "head": 2, "deprel": "nmod:poss"},
            {"id": 2, "form": "kapısını", "lemma": "kapı",   "upos": "NOUN",
             "head": 3, "deprel": "obj"},
            {"id": 3, "form": "gördüm",   "lemma": "görmek", "upos": "VERB",
             "head": 0, "deprel": "root"},
        ],
    },
]
```

- [x] **Step 2: CoNLL-U golden'ı oluştur**

```python
# tests/golden_conllu.py
"""E6 CoNLL-U export — bağımsız golden."""

CONLLU_CASES = [
    {
        "sent_id": "1",
        "text": "öğrenci okudu",
        # CoNLL-U sütun sırası: ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC
        # DEPS = _ (sütun 9), MISC = _ (sütun 10)
        "expected": (
            "# sent_id = 1\n"
            "# text = öğrenci okudu\n"
            "1\töğrenci\töğrenci\tNOUN\tdecline\tCase=Nom|Number=Sing\t2\tnsubj\t_\t_\n"
            "2\tokudu\tokumak\tVERB\tconjugate\tNumber=Sing|Person=3|Tense=Past\t0\troot\t_\t_\n"
        ),
    },
]
```

---

## Task 10a: E5+E6 — Runner Testi Yaz (RED adımı)

**Files:**
- Create: `tests/test_dependency.py`

- [x] **Step 1: Runner dosyasını oluştur**

```python
# tests/test_dependency.py
"""E5+E6 dependency graph + CoNLL-U runner."""
import pytest
from tests.golden_dependency import DEP_CASES
from tests.golden_conllu import CONLLU_CASES
from turkgram import tokenize, parse_text
from turkgram.parse import parse_phrase
from turkgram.dependency import DepToken, constituency_to_dep, to_conllu


@pytest.mark.parametrize("case", DEP_CASES, ids=[c["text"] for c in DEP_CASES])
def test_constituency_to_dep(case):
    tokens = tokenize(case["text"])
    analyses = parse_text(case["text"])
    tree = parse_phrase(tokens, analyses)
    dep = constituency_to_dep(tree)
    assert len(dep) == len(case["expected"])
    for got, exp in zip(dep, case["expected"]):
        assert got.id     == exp["id"]
        assert got.form   == exp["form"]
        assert got.upos   == exp["upos"]
        assert got.head   == exp["head"]
        assert got.deprel == exp["deprel"]
        if "lemma" in exp:
            assert got.lemma == exp["lemma"]


@pytest.mark.parametrize("case", CONLLU_CASES, ids=[c["text"] for c in CONLLU_CASES])
def test_to_conllu(case):
    tokens = tokenize(case["text"])
    analyses = parse_text(case["text"])
    tree = parse_phrase(tokens, analyses)
    dep = constituency_to_dep(tree)
    result = to_conllu(dep, sent_id=case["sent_id"], text=case["text"])
    assert result == case["expected"]
```

- [x] **Step 2: Testin başarısız olduğunu doğrula**

```bash
pytest tests/test_dependency.py -v
```

Beklenti: `ImportError: cannot import name 'constituency_to_dep'`

---

## Task 10: E5+E6 — dependency.py İmplementasyonu

**Files:**
- Create: `turkgram/dependency.py`

- [x] **Step 1: Temel yapıyı oluştur**

```python
# turkgram/dependency.py
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
```

- [x] **Step 2: feats üretim yardımcısını yaz**

```python
def _analysis_to_feats(analysis: "object | None", upos: str) -> str:
    """Analysis.kwargs → UD feats string (alfabetik sıra, §5.4)."""
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
        feats["Case"] = "Nom"  # varsayılan

    # Number + Person (person kwarg: '1sg', '3pl' vb.)
    person_str = kwargs.get("person")
    if person_str:
        num_part = "Plur" if person_str.endswith("pl") else "Sing"
        per_part = person_str[0]
        feats["Number"] = num_part
        feats["Person"] = per_part
    elif upos in ("NOUN", "NUM"):
        feats["Number"] = "Sing"  # varsayılan

    # Possessive
    poss = kwargs.get("possessive")
    if poss:
        poss_num = "Plur" if poss.endswith("pl") else "Sing"
        poss_per = poss[0]
        feats["Number[psor]"] = poss_num
        feats["Person[psor]"] = poss_per

    # Tense
    _TENSE_MAP = {"past": "Past", "pres": "Pres", "fut": "Fut", "aorist": "Aor"}
    tense = kwargs.get("tense")
    if tense in _TENSE_MAP:
        feats["Tense"] = _TENSE_MAP[tense]

    # Evidential
    aux = kwargs.get("aux")
    if aux == "evid":
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
```

- [x] **Step 3: constituency_to_dep'i yaz**

```python
def constituency_to_dep(tree: "PhraseNode") -> list[DepToken]:
    """PhraseNode ağacı → DepToken listesi (1-tabanlı ID, head-finding)."""
    from .parse import LeafNode, PhraseNode as PN

    # 1. Yaprakları sırayla topla
    def _leaves(node: "PN | LeafNode") -> list[LeafNode]:
        if isinstance(node, LeafNode):
            return [node]
        return [l for c in node.children for l in _leaves(c)]

    all_leaves = _leaves(tree)
    leaf_ids = {id(lf): i + 1 for i, lf in enumerate(all_leaves)}

    # 2. Her yaprak için (head_id, deprel) belirle
    deps: dict[int, tuple[int, str]] = {}  # leaf_id → (head_id, deprel)

    def _find_head_leaf(node: "PN | LeafNode") -> LeafNode:
        """Öbek başını (head LeafNode) bul."""
        if isinstance(node, LeafNode):
            return node
        tag = node.tag
        children = node.children
        if tag == "NP":
            # possessed (iyelik taşıyan) en sağdaki NOUN; yoksa en sağdaki NOUN
            for c in reversed(children):
                if isinstance(c, LeafNode) and c.tag == "NOUN":
                    if c.analysis and c.analysis.kwargs.get("possessive"):
                        return c
            for c in reversed(children):
                if isinstance(c, LeafNode) and c.tag == "NOUN":
                    return c
            return _find_head_leaf(children[-1])
        if tag in ("VP", "S"):
            for c in children:
                if isinstance(c, LeafNode) and c.tag == "VERB":
                    return c
            for c in children:
                if isinstance(c, PhraseNode) and c.tag == "VP":
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
            return _find_head_leaf(children[-1])
        if tag == "CoordP":
            return _find_head_leaf(children[0])
        return _find_head_leaf(children[-1])

    def _process(node: "PN | LeafNode", parent_head_leaf: "LeafNode | None", deprel: str) -> None:
        if isinstance(node, LeafNode):
            if parent_head_leaf is None:
                deps[leaf_ids[id(node)]] = (0, "root")
            else:
                deps[leaf_ids[id(node)]] = (leaf_ids[id(parent_head_leaf)], deprel)
            return
        tag = node.tag
        head_leaf = _find_head_leaf(node)
        # Kök bağı
        if parent_head_leaf is None:
            deps[leaf_ids[id(head_leaf)]] = (0, "root")
        else:
            deps[leaf_ids[id(head_leaf)]] = (leaf_ids[id(parent_head_leaf)], deprel)
        # Çocukları işle
        for child in node.children:
            child_head = _find_head_leaf(child)
            if id(child_head) == id(head_leaf):
                continue  # baş zaten işlendi
            child_deprel = _child_deprel(tag, child, head_leaf)
            _process(child, head_leaf, child_deprel)

    def _child_deprel(parent_tag: str, child: "PN | LeafNode", head_leaf: LeafNode) -> str:
        child_tag = _tag_of(child)
        if parent_tag == "NP":
            if child_tag == "ADJ":           return "amod"
            if child_tag == "NUM":           return "nummod"
            if child_tag in ("NP", "NOUN"):
                # GEN tamlayan → nmod:poss
                cl = _find_head_leaf(child) if isinstance(child, PN) else child
                if cl.analysis and cl.analysis.kwargs.get("case") == "gen":
                    return "nmod:poss"
                return "nmod"
            if child_tag == "AdjP":          return "amod"
        if parent_tag == "PP":
            if child_tag in ("NP", "NOUN"):  return "nmod"
        if parent_tag == "AdjP":
            if child_tag == "ADJ":           return "advmod"
        if parent_tag == "CoordP":
            if child_tag == "CCONJ":         return "cc"
            if child_tag in ("NP",):         return "conj"
        if parent_tag in ("VP", "S"):
            cl = _find_head_leaf(child) if isinstance(child, PN) else child
            case = cl.analysis.kwargs.get("case") if cl.analysis else None
            if child_tag in ("NP", "NOUN", "CoordP"):
                if case == "acc":            return "obj"
                if case in ("dat", "loc", "abl", "ins"): return "obl"
                return "nsubj"
            if child_tag == "PP":            return "obl"
            if child_tag in ("AdjP", "AdvP"): return "advmod"
        return "dep"

    def _tag_of(node: "PN | LeafNode") -> str:
        return node.tag

    _process(tree, None, "root")

    # 3. DepToken listesi oluştur
    result = []
    for i, lf in enumerate(all_leaves, 1):
        a = lf.analysis
        head_id, deprel = deps.get(i, (0, "root"))
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
```

- [x] **Step 4: to_conllu'yu yaz**

```python
def to_conllu(
    tokens: list[DepToken],
    *,
    sent_id: str = "",
    text: str = "",
) -> str:
    """list[DepToken] → CoNLL-U formatında metin string."""
    lines = []
    if sent_id:
        lines.append(f"# sent_id = {sent_id}")
    if text:
        lines.append(f"# text = {text}")
    for t in tokens:
        lemma = t.lemma if t.lemma is not None else "_"
        # CoNLL-U: ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC
        lines.append(
            f"{t.id}\t{t.form}\t{lemma}\t{t.upos}\t{t.xpos}\t"
            f"{t.feats}\t{t.head}\t{t.deprel}\t_\t{t.misc}"
        )
    return "\n".join(lines) + "\n"


__all__ = ["DepToken", "constituency_to_dep", "to_conllu"]
```

- [x] **Step 5: Testleri çalıştır** (runner Task 10a'da yazıldı)

```bash
pytest tests/test_dependency.py -v
```

Beklenti: Tüm yeşil. Başarısız olan varsa implementasyonu düzelt.

- [x] **Step 7: Commit**

```bash
git add turkgram/dependency.py tests/golden_dependency.py tests/golden_conllu.py tests/test_dependency.py
git commit -m "feat(dependency): E5+E6 constituency_to_dep + to_conllu (UD/CoNLL-U)"
```

---

## Task 11: Exports + __init__.py

**Files:**
- Modify: `turkgram/__init__.py`

- [x] **Step 1: Yeni modülleri export et**

`__init__.py`'de ilgili bölüme ekle:

```python
# parse.py — E2
from .parse import LeafNode, PhraseNode, parse_phrase

# dependency.py — E5+E6
from .dependency import DepToken, constituency_to_dep, to_conllu
```

`__all__` listesine de ekle: `"LeafNode"`, `"PhraseNode"`, `"parse_phrase"`, `"DepToken"`, `"constituency_to_dep"`, `"to_conllu"`.

- [x] **Step 2: Import testi**

```bash
PYTHONUTF8=1 python -c "from turkgram import parse_phrase, constituency_to_dep, to_conllu; print('OK')"
```

Beklenti: `OK`

- [x] **Step 3: Tüm test paketini çalıştır**

```bash
pytest --ignore=tests/test_slow_roundtrip.py -q
```

Beklenti: Yeni test sayısı = önceki + E1 + E2 + E5 + E6; 0 başarısız.

- [x] **Step 4: Commit**

```bash
git add turkgram/__init__.py
git commit -m "feat(__init__): E1-E2-E5-E6 yeni API'ler export edildi"
```

---

## Task 12: Hakem — Corpus Sweep + Regresyon

**Files:**
- Create: `tools/sweep_syntax_e.py`

- [x] **Step 1: Sweep aracını oluştur**

```python
# tools/sweep_syntax_e.py
"""Faz E hakem: leksikon × E1/E2 0 çökme taraması."""
import sys, traceback
sys.stdout.reconfigure(encoding="utf-8")

from turkgram.lexicon import load
from turkgram import tokenize, parse_text
from turkgram.parse import parse_phrase
from turkgram.dependency import constituency_to_dep, to_conllu
from turkgram.syntax import np_uret, pp_uret

roots = load()
lemmas = list(roots)[:500]   # ilk 500 lemma
errors = []

for lemma in lemmas:
    # E1: np_uret
    try:
        np_uret(lemma, durum="acc")
        np_uret(lemma, tamlayan="ev")
    except Exception as e:
        errors.append(f"np_uret({lemma!r}): {e}")

    # E1: pp_uret
    try:
        pp_uret(lemma, "için")
    except Exception as e:
        errors.append(f"pp_uret({lemma!r}): {e}")

    # E2: parse_phrase + E5/E6
    try:
        tokens = tokenize(lemma)
        analyses = parse_text(lemma)
        tree = parse_phrase(tokens, analyses)
        dep = constituency_to_dep(tree)
        conllu = to_conllu(dep)
        # CoNLL-U sütun sayısı doğrulaması (10 sütun)
        for line in conllu.splitlines():
            if line.startswith("#") or not line.strip():
                continue
            cols = line.split("\t")
            if len(cols) != 10:
                errors.append(f"CoNLL-U sütun hatası ({lemma!r}): {len(cols)} sütun: {line!r}")
    except Exception as e:
        errors.append(f"parse({lemma!r}): {e}")
        traceback.print_exc()

print(f"Tarandı: {len(lemmas)} lemma")
print(f"Hata: {len(errors)}")
for err in errors[:20]:
    print(" ", err)
```

- [x] **Step 2: Sweep'i çalıştır**

```bash
PYTHONUTF8=1 python tools/sweep_syntax_e.py
```

Beklenti: `Hata: 0`. Hata varsa kök nedeni araştır, düzelt, yeniden çalıştır.

- [x] **Step 3: Tüm test paketini son kez çalıştır**

```bash
pytest --ignore=tests/test_slow_roundtrip.py -q
```

- [x] **Step 4: Final commit**

```bash
git add tools/sweep_syntax_e.py
git commit -m "test(sweep): Faz E hakem corpus tarama aracı — E1/E2/E5/E6"
```

---

## Özet

| Görev | Dosyalar | Amaç |
|-------|----------|-------|
| 1 | `golden_syntax_rich.py` | E1 motor-körü golden |
| 2 | `test_syntax_rich.py` | E1 runner |
| 3 | `syntax.py` | E1 implementasyon |
| 4 | `tr.py` | E1 TR API |
| 5 | `parse.py` | E2 dataclass'lar |
| 6 | `golden_parse.py` | E2 motor-körü golden |
| 7 | `test_parse.py` | E2 runner |
| 8 | `parse.py` | E2 parse_phrase implementasyon |
| 9 | `golden_dependency.py`, `golden_conllu.py` | E5+E6 motor-körü golden |
| 10 | `dependency.py`, `test_dependency.py` | E5+E6 implementasyon + runner |
| 11 | `__init__.py` | Export |
| 12 | `sweep_syntax_e.py` | Hakem corpus tarama |
