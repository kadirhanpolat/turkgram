# Faz E3/E4 — Yan Cümle Desteği İmplementasyon Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `parse.py` bottom-up pipeline'ına `ki`-cümleleri (CompP/RelP) ve `diye`-cümleleri (DiyeP) desteği ekle.

**Architecture:** Mevcut R0–R5 pipeline'ına iki yeni kural eklenir: R6_ki (R4'ten önce, bağlam-duyarlı CompP/RelP), R7_diye (R5'ten önce, DiyeP). `_apply_r5` stop listesi DiyeP/CompP/RelP ile güncellenir. Tüm değişiklik `parse.py` tek dosyasında; `frozen=True` dataclass'lar dokunulmaz.

**Tech Stack:** Python 3.10+, pytest, turkgram mevcut primitifleri (tokenize, parse_text, disambiguation.rank)

**Spec:** `docs/superpowers/specs/2026-07-17-e3-e4-subordinate-clauses-design.md`

**İş akışı (CLAUDE.md §2):** SPEC → bağımsız golden (motor-körü) → motor → hakem (regresyon + 0 çökme)

**Windows notu:** Türkçe karakter yazan `python` komutlarını `PYTHONUTF8=1 python ...` ile çalıştır. `pytest` komutlarında bu şart değil.

---

## Dosya Yapısı

| Dosya | Durum | Sorumluluk |
|-------|-------|-----------|
| `turkgram/parse.py` | Değiştirilecek | R6_ki + R7_diye + R5 stop list güncelleme |
| `tests/golden_subordinate.py` | Yeni | 10-girdi bağımsız golden (motor-körü, Opus) |
| `tests/test_subordinate.py` | Yeni | Runner — mevcut `_node_matches` yeniden kullanılır |
| `tools/sweep_syntax_e.py` | Değiştirilecek | CompP/RelP/DiyeP tag'leri sweep'e dahil |

`turkgram/__init__.py`, `turkgram/tr.py`, `turkgram/dependency.py` **değişmez** — yeni public API yok.

---

## Task 1: Bağımsız Golden Testi Yaz (Motor-Körü)

**Files:**
- Create: `tests/golden_subordinate.py`

**ÖNEMLİ:** Bu adımı yazarken `parse.py`'yi AÇMA — yalnızca spec §3-4 + Türkçe dilbilgisini kullan. Golden, motordan bağımsız kurulur.

- [ ] **Step 1: Golden dosyasını oluştur**

```python
# tests/golden_subordinate.py
"""Faz E3/E4 yan cümle — bağımsız golden (motor-körü, elle doğrulanmış).

Her giriş: {"text", "roots" (opsiyonel), "expected": {tag, surface?, children?}}

Ağaç formatı (test_parse.py ile aynı):
  {"tag": "...", "surface": "...", "children": [...]}
  Yaprak: {"tag": "NOUN"|"VERB"|..., "token": "..."}
  Öbek: {"tag": "NP"|"CompP"|..., "children": [...]}

DiyeP testleri için: root.children[0].tag == "DiyeP" kontrolü zorunludur
(spec §6.1 notu: DiyeP S-düzeyinde olmalı, VP içinde DEĞİL).
"""

SUBORDINATE_CASES = [
    # ── E3: ki-cümleleri ──────────────────────────────────────────────────

    {
        # Case 1: CompP — sol VERB + ki + sağ-VERB
        "text": "biliyorum ki geldi",
        "roots": {"bilmek", "gelmek"},
        "expected": {
            "tag": "CompP",
            "surface": "biliyorum ki geldi",
            "children": [
                {"tag": "VERB", "token": "biliyorum"},
                {"tag": "CCONJ", "token": "ki"},
                {"tag": "VERB", "token": "geldi"},
            ],
        },
    },
    {
        # Case 2: RelP — sol NP + ki + sağ-VERB
        "text": "öyle bir şey ki gördüm",
        "roots": {"öyle", "bir", "şey", "görmek"},
        "expected": {
            "tag": "RelP",
            "surface": "öyle bir şey ki gördüm",
            "children": [
                {
                    "tag": "NP",
                    "surface": "öyle bir şey",
                    "children": [
                        {"tag": "ADJ",  "token": "öyle"},
                        {"tag": "ADJ",  "token": "bir"},
                        {"tag": "NOUN", "token": "şey"},
                    ],
                },
                {"tag": "CCONJ", "token": "ki"},
                {"tag": "VERB", "token": "gördüm"},
            ],
        },
    },
    {
        # Case 3: E3 geçiş — sol ADJ, R6 ateşlemez → S (ki CCONJ olarak kalır)
        "text": "iyi ki geldin",
        "roots": {"iyi", "gelmek"},
        "expected": {
            "tag": "S",
            "surface": "iyi ki geldin",
        },
    },
    {
        # Case 4: Cümle-başı ki — R6 sol komşu yok, atlar → S
        "text": "ki geldi",
        "roots": {"gelmek"},
        "expected": {
            "tag": "S",
            "surface": "ki geldi",
        },
    },
    {
        # Case 5: NP ki NP — R6 sol=NP → RelP (eski davranış CoordP'ydi)
        "text": "ev ki araba",
        "roots": {"ev", "araba"},
        "expected": {
            "tag": "RelP",
            "surface": "ev ki araba",
            "children": [
                {
                    "tag": "NP",
                    "surface": "ev",
                    "children": [{"tag": "NOUN", "token": "ev"}],
                },
                {"tag": "CCONJ", "token": "ki"},
                {
                    "tag": "NP",
                    "surface": "araba",
                    "children": [{"tag": "NOUN", "token": "araba"}],
                },
            ],
        },
    },

    # ── E4: diye-cümleleri ────────────────────────────────────────────────

    {
        # Case 6: DiyeP alıntı — DiyeP S-düzeyinde (VP içinde DEĞİL)
        # children[0].tag == "DiyeP" kontrolü zorunlu
        "text": "gelir diye bekledi",
        "roots": {"gelmek", "beklemek"},
        "expected": {
            "tag": "S",
            "surface": "gelir diye bekledi",
            "children": [
                {
                    "tag": "DiyeP",
                    "surface": "gelir diye",
                    "children": [
                        {"tag": "VERB", "token": "gelir"},
                        {"tag": "VERB", "token": "diye"},
                    ],
                },
                {
                    "tag": "VP",
                    "surface": "bekledi",
                    "children": [{"tag": "VERB", "token": "bekledi"}],
                },
            ],
        },
    },
    {
        # Case 7: DiyeP amaç — nesne VP'de, DiyeP S-düzeyinde
        "text": "okusun diye kitap aldı",
        "roots": {"okumak", "kitap", "almak"},
        "expected": {
            "tag": "S",
            "surface": "okusun diye kitap aldı",
            "children": [
                {
                    "tag": "DiyeP",
                    "surface": "okusun diye",
                    "children": [
                        {"tag": "VERB", "token": "okusun"},
                        {"tag": "VERB", "token": "diye"},
                    ],
                },
                {
                    "tag": "VP",
                    "surface": "kitap aldı",
                    "children": [
                        {
                            "tag": "NP",
                            "surface": "kitap",
                            "children": [{"tag": "NOUN", "token": "kitap"}],
                        },
                        {"tag": "VERB", "token": "aldı"},
                    ],
                },
            ],
        },
    },
    {
        # Case 8: DiyeP varyant
        "text": "okudu diye sevindi",
        "roots": {"okumak", "sevinmek"},
        "expected": {
            "tag": "S",
            "surface": "okudu diye sevindi",
            "children": [
                {
                    "tag": "DiyeP",
                    "surface": "okudu diye",
                    "children": [
                        {"tag": "VERB", "token": "okudu"},
                        {"tag": "VERB", "token": "diye"},
                    ],
                },
                {
                    "tag": "VP",
                    "surface": "sevindi",
                    "children": [{"tag": "VERB", "token": "sevindi"}],
                },
            ],
        },
    },

    # ── Regresyon: mevcut davranış değişmemeli ────────────────────────────

    {
        # Case 9: Regresyon — ki/diye yok, CoordP
        "text": "kitap ve defter",
        "roots": {"kitap", "defter"},
        "expected": {
            "tag": "CoordP",
            "surface": "kitap ve defter",
            "children": [
                {
                    "tag": "NP",
                    "surface": "kitap",
                    "children": [{"tag": "NOUN", "token": "kitap"}],
                },
                {"tag": "CCONJ", "token": "ve"},
                {
                    "tag": "NP",
                    "surface": "defter",
                    "children": [{"tag": "NOUN", "token": "defter"}],
                },
            ],
        },
    },
    {
        # Case 10: Regresyon — fiilimsi NP (R1b), ki/diye yok
        "text": "okuduğunu biliyorum",
        "roots": {"okumak", "bilmek"},
        "expected": {
            "tag": "S",
            "surface": "okuduğunu biliyorum",
        },
    },
]
```

- [ ] **Step 2: Golden'ı Türkçe dilbilgisi açısından gözden geçir**

Her girişi kontrol et:
- Case 1: `biliyorum` = bilmek pres-1sg ✓; `ki` sol=VERB → CompP ✓
- Case 2: `şey` isim, `öyle bir` niteleyici → NP; sol=NP → RelP ✓
- Case 3: `iyi` ADJ, sol=ADJ → R6 ateşlemez → S ✓
- Case 4: `ki` index 0, sol yok → atlar → S ✓
- Case 5: `ev` NP, `araba` NP, `ki` sol=NP → RelP ✓
- Case 6–8: DiyeP `children[0]`; VP bağımsız `children[1]` ✓
- Case 9: `ve` CCONJ, `ki` yok → R4 CoordP ✓

---

## Task 2: Runner Testi Yaz

**Files:**
- Create: `tests/test_subordinate.py`

- [ ] **Step 1: Runner dosyasını oluştur**

```python
# tests/test_subordinate.py
"""Faz E3/E4 yan cümle runner."""
import pytest
from tests.golden_subordinate import SUBORDINATE_CASES
from tests.test_parse import _node_matches          # mevcut yardımcı yeniden kullan
from turkgram import tokenize, parse_text
from turkgram.parse import LeafNode, PhraseNode, parse_phrase


@pytest.mark.parametrize(
    "case",
    SUBORDINATE_CASES,
    ids=[c["text"] for c in SUBORDINATE_CASES],
)
def test_subordinate_parse(case):
    tokens = tokenize(case["text"])
    analyses = parse_text(case["text"], case.get("roots"))
    tree = parse_phrase(tokens, analyses)
    assert _node_matches(tree, case["expected"]), (
        f"\nBeklenen:\n{case['expected']}\nAlınan:\n{tree}"
    )
```

- [ ] **Step 2: Testin başarısız olduğunu doğrula (RED adımı)**

```bash
pytest tests/test_subordinate.py -v
```

Beklenti: Tüm testler FAIL — R6/R7 henüz yok, CompP/RelP/DiyeP üretilmiyor. Örnek: `AssertionError` veya root tag uyumsuzluğu.

---

## Task 3: R5 Stop List Güncellemesi

**Files:**
- Modify: `turkgram/parse.py`

Bu adım R6/R7'den önce yapılmalıdır. R5 mevcut hali `DiyeP`/`CompP`/`RelP`'yi VP argümanı olarak toplar — yanlış yapı üretir. Önce durduralım.

- [ ] **Step 1: `_apply_r5` içindeki VP-argüman toplama döngüsünü güncelle**

`parse.py`'de `_apply_r5` fonksiyonunu bul. Mevcut döngü:

```python
while left >= 0:
    n = nodes[left]
    tag = _tag(n)
    if tag not in ("NP", "PP", "AdjP", "CoordP", "NOUN"):
        break
    # Yalın NP = özne → VP dışında bırak
    if tag in ("NP", "NOUN") and _node_is_nominative(n):
        break
```

Şu satırı değiştir:
```python
    if tag not in ("NP", "PP", "AdjP", "CoordP", "NOUN"):
        break
```

Yeni hali:
```python
    # Yan cümle öbekleri cümle-düzeyi adjunct — VP'ye çekilmez
    if tag in ("DiyeP", "CompP", "RelP"):
        break
    if tag not in ("NP", "PP", "AdjP", "CoordP", "NOUN"):
        break
```

- [ ] **Step 2: Mevcut testlerin hâlâ geçtiğini doğrula**

```bash
pytest tests/test_parse.py tests/test_dependency.py -v
```

Beklenti: Tüm mevcut testler yeşil (R6/R7 henüz yok, sadece R5 stop list güncellendi).

---

## Task 4: R6_ki Implementasyonu

**Files:**
- Modify: `turkgram/parse.py`

- [ ] **Step 1: `_apply_r6_ki` fonksiyonunu yaz**

`_apply_r5` tanımının hemen ÜSTÜNDEKİ konuma ekle (dosya sonuna değil — pipeline sırası: R6 önce çalışmalı):

```python
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
```

- [ ] **Step 2: `parse_phrase` pipeline'ını güncelle**

`parse_phrase` içindeki `# 2. Bottom-up gruplama` bloğunu bul:

```python
nodes = _apply_r0(nodes)   # NP: NOUN[gen] NOUN[poss] (belirtili tamlama)
nodes = _apply_r3(nodes)   # AdjP: ADJ ADJ+
nodes = _apply_r1(nodes)   # NP: modifer* NOUN
nodes = _apply_r1b(nodes)  # NP: participle NOUN
nodes = _apply_r2(nodes)   # PP: NP ADP
nodes = _apply_r4(nodes)   # CoordP: NP CCONJ NP
nodes = _apply_r5(nodes)   # S: özne VP(nesne VERB)
nodes = _wrap_bare_vp(nodes)
```

Şu şekilde güncelle (R6 R4'ten önce, R7 R5'ten önce):

```python
nodes = _apply_r0(nodes)      # NP: NOUN[gen] NOUN[poss] (belirtili tamlama)
nodes = _apply_r3(nodes)      # AdjP: ADJ ADJ+
nodes = _apply_r1(nodes)      # NP: modifer* NOUN
nodes = _apply_r1b(nodes)     # NP: participle NOUN
nodes = _apply_r2(nodes)      # PP: NP ADP
nodes = _apply_r6_ki(nodes)   # CompP / RelP: ki bağlam-duyarlı  ← YENİ
nodes = _apply_r7_diye(nodes) # DiyeP: diye yan cümle            ← YENİ (Task 5)
nodes = _apply_r4(nodes)      # CoordP: NP CCONJ NP
nodes = _apply_r5(nodes)      # S: özne VP(nesne VERB)
nodes = _wrap_bare_vp(nodes)
```

**Not:** `_apply_r7_diye` henüz yazılmadı; geçici olarak `pass` fonksiyonu ekle — `_apply_r6_ki`'nin hemen ALTINA, `_apply_r5`'in hemen ÜSTÜNDEKİ konuma:

```python
def _apply_r7_diye(nodes: list) -> list:
    """R7: diye yan cümle gruplaması — Task 5'te implemente edilecek."""
    return nodes
```

- [ ] **Step 3: E3 testlerini çalıştır**

```bash
pytest tests/test_subordinate.py -v -k "biliyorum or öyle or iyi or ki_geldi or ev_ki"
```

Beklenti: Case 1 (CompP), Case 2 (RelP), Case 3 (S/iyi-ki), Case 4 (S/ki-geldi), Case 5 (RelP/NP-ki-NP) yeşil.

- [ ] **Step 4: Regresyon kontrolü**

```bash
pytest tests/test_parse.py tests/test_dependency.py -v
```

Beklenti: Tüm mevcut testler yeşil.

- [ ] **Step 5: Commit**

```bash
git add turkgram/parse.py tests/golden_subordinate.py tests/test_subordinate.py
git commit -m "feat(parse): E3 ki-cümleleri — R6_ki CompP/RelP + R5 stop-list güncellemesi"
```

---

## Task 5: R7_diye Implementasyonu

**Files:**
- Modify: `turkgram/parse.py`

- [ ] **Step 1: `_apply_r7_diye` fonksiyonunu yaz**

Task 4'te eklenen placeholder'ı gerçek implementasyonla değiştir:

```python
def _apply_r7_diye(nodes: list) -> list:
    """R7: diye converb → DiyeP (sol-sequence + VERB[diye/demek]).

    Koşul: node.tag == "VERB"
           and node.analysis.kind == "converb"
           and node.analysis.lemma == "demek"

    Sol tüm node'lar + diye tokenı → DiyeP.
    DiyeP cümle-düzeyi adjunct: R5 VP'ye çekmez (Task 3'te sabitlendi).
    """
    for i, node in enumerate(nodes):
        if not isinstance(node, LeafNode):
            continue
        if node.tag != "VERB":
            continue
        a = node.analysis
        if a is None:
            continue
        if not (a.kind == "converb" and a.lemma == "demek"):
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
```

- [ ] **Step 2: Tüm yan cümle testlerini çalıştır**

```bash
pytest tests/test_subordinate.py -v
```

Beklenti: Tüm 10 case yeşil. Başarısız olan varsa golden'ı değil implementasyonu düzelt.

- [ ] **Step 3: Tam paket regresyon kontrolü**

```bash
pytest --ignore=tests/test_slow_roundtrip.py -q
```

Beklenti: Önceki test sayısına 10 yeni test eklendi; 0 başarısız.

- [ ] **Step 4: Commit**

```bash
git add turkgram/parse.py
git commit -m "feat(parse): E4 diye-cümleleri — R7_diye DiyeP implementasyonu"
```

---

## Task 6: Sweep Güncellemesi + Hakem

**Files:**
- Modify: `tools/sweep_syntax_e.py`

- [ ] **Step 1: Sweep'e yan cümle kontrolleri ekle**

`sweep_syntax_e.py` içinde `# ── Sonuç` satırından ÖNCE yeni bir bölüm ekle:

```python
    # ── 6. yan cümle öbekleri — CompP / RelP / DiyeP tag kontrolü ─────────
    subordinate_sentences = [
        ("biliyorum ki geldi",    {"bilmek", "gelmek"},   "CompP"),
        ("öyle bir şey ki gördüm", {"şey", "görmek"},     "RelP"),
        ("gelir diye bekledi",    {"gelmek", "beklemek"},  "S"),   # root S, child[0] DiyeP
        ("okusun diye kitap aldı", {"okumak", "kitap", "almak"}, "S"),
    ]
    for text, roots, expected_root_tag in subordinate_sentences:
        total += 1
        try:
            toks = tokenize(text)
            analyses = parse_text(text, roots=roots)
            tree = parse_phrase(toks, analyses)
            assert tree.tag == expected_root_tag, (
                f"{text!r}: beklenen root={expected_root_tag!r}, alınan={tree.tag!r}"
            )
            # DiyeP S-düzeyinde mi? (VP içinde değil)
            if expected_root_tag == "S":
                child_tags = [_tag(c) for c in tree.children]
                if "DiyeP" not in child_tags:
                    # DiyeP bekleniyor ama S-düzeyinde değil — VP içinde mi kaldı?
                    vp_children = []
                    for c in tree.children:
                        if isinstance(c, PhraseNode) and c.tag == "VP":
                            vp_children = [_tag(x) for x in c.children]
                    if "DiyeP" in vp_children:
                        errors.append(f"{text!r}: DiyeP VP içine çekilmiş (S-düzeyi olmalı)")
        except AssertionError as exc:
            errors.append(f"subordinate {text!r}: {exc}")
        except Exception as exc:
            errors.append(f"subordinate {text!r}: ÇÖKME — {exc}")
```

Sweep'in `PhraseNode` ve `_tag` fonksiyonuna erişmesi için dosyanın başına import ekle:

```python
from turkgram.parse import parse_phrase, PhraseNode, _tag
```

(Mevcut `from turkgram.parse import parse_phrase` satırını güncelle.)

- [ ] **Step 2: Sweep'i çalıştır**

```bash
PYTHONUTF8=1 python tools/sweep_syntax_e.py
```

Beklenti: `Hata: 0`. Hata varsa kök nedeni araştır, düzelt, yeniden çalıştır.

- [ ] **Step 3: Son regresyon kontrolü**

```bash
pytest --ignore=tests/test_slow_roundtrip.py -q
```

Beklenti: Önceki 4051 + 10 yeni = **4061 test yeşil**, 0 başarısız.

- [ ] **Step 4: Final commit**

```bash
git add tools/sweep_syntax_e.py
git commit -m "test(sweep): E3/E4 yan cümle hakem kontrolleri sweep'e eklendi"
```

---

## Özet

| Görev | Dosyalar | Amaç |
|-------|----------|-------|
| 1 | `golden_subordinate.py` | 10-girdi bağımsız golden (motor-körü) |
| 2 | `test_subordinate.py` | Runner (RED adımı) |
| 3 | `parse.py` | R5 stop list — DiyeP/CompP/RelP VP dışı |
| 4 | `parse.py` | R6_ki (CompP/RelP) + pipeline bağlantısı |
| 5 | `parse.py` | R7_diye (DiyeP) |
| 6 | `sweep_syntax_e.py` | Hakem — 0 çökme + DiyeP konum kontrolü |
