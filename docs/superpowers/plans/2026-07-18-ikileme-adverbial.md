# İkileme Adverbial-Yeniden-Kurulum Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Constituency parser'ın tam ikileme (`yavaş yavaş`) ve ulaç ikilemesini (`koşa koşa`) tek bir `AdvP` öbeği olarak yeniden kurması + dependency katmanında doğru `advmod`/`compound:redup` ilişkileri.

**Architecture:** Yüzey-tabanlı yeni parser kuralı `_apply_r8_redup` (R6_ki/R7_diye emsali) bitişik özdeş token çiftini tespit eder, POS'a göre sınıflar (VERB→ulaç, ADJ/NOUN→tam), NOUN-takip guard'ıyla adnominal okumayı korur, `AdvP` kurar. Pipeline'da R3'ten önce çalışır; R5 AdvP'yi VP'ye alır. `dependency.py` AdvP için açık `advmod` (baş→fiil) + `compound:redup` (ikinci token→baş) dalları alır.

**Tech Stack:** Python 3, pytest, mevcut turkgram parse/dependency motoru.

**Kaynak:** SPEC/tasarım `docs/superpowers/specs/2026-07-18-ikileme-adverbial-design.md`.

**Windows notu:** `python -m pytest ...`; Türkçe basan ad-hoc python → `PYTHONUTF8=1 python ...`.

---

## Dosya Yapısı

- **Modify** `turkgram/parse.py` — `_apply_r8_redup` (yeni), pipeline'a ekle (R0'dan önce), R5 absorpsiyon kümesine `"AdvP"`, `_tr_lower` lazy import.
- **Modify** `turkgram/dependency.py` — `_child_deprel` VP/S dalı `("AdjP","AdvP")→advmod` + AdvP-ebeveyn dalı `compound:redup`; `_find_head_leaf` AdvP dalı.
- **Modify** `tests/golden_parse.py` — AdvP parse ağacı case'leri (bağımsız, motor-körü Opus).
- **Modify** `tests/golden_dependency.py` — AdvP advmod + compound:redup case'leri (motor-körü).
- **Create** `tools/sweep_adverbial.py` — parse korpus tarama (çökme yok).

---

## Task 1: Bağımsız golden — AdvP parse ağaçları + dependency (motor-körü, RED)

**Files:**
- Modify: `tests/golden_parse.py` (yeni case'ler ekle)
- Modify: `tests/golden_dependency.py` (yeni case'ler ekle)

**Not (CLAUDE.md §2):** Golden motordan BAĞIMSIZ — Opus subagent'a dispatch: "parse.py/dependency.py motorunu GÖRME, yalnız SPEC + dilbilgisi + mevcut golden FORMATI". Beklenen ağaçlar dilbilgisinden elle doğrulanır. Aşağıdaki içerik golden'ın YAPISINI ve elle-doğrulanmış beklenen değerleri verir.

- [ ] **Step 1: Mevcut golden formatını incele (yalnız FORMAT)**

`tests/golden_parse.py` `PARSE_CASES` her giriş: `{"text", "roots", "expected": {tag, surface?, children?}}`. `_node_matches` (test_parse.py): `children` yoksa yalnız tag/surface kontrol edilir (opsiyonel alt-ağaç). `tests/golden_dependency.py` `DEP_CASES`: `{"text", "roots", "expected": [{id, form, lemma, upos, head, deprel}]}`.

- [ ] **Step 2: AdvP parse case'lerini `tests/golden_parse.py` `PARSE_CASES` sonuna ekle**

```python
    # --- İkileme adverbial (Faz E-devamı) ---
    {   # tam ikileme → AdvP, VP içinde
        "text": "yavaş yavaş yürüdü",
        "roots": {"yavaş", "yürümek"},
        "expected": {
            "tag": "S",
            "children": [
                {"tag": "VP", "children": [
                    {"tag": "AdvP", "surface": "yavaş yavaş"},
                    {"tag": "VERB", "token": "yürüdü"},
                ]},
            ],
        },
    },
    {   # ulaç ikilemesi → AdvP (VERB çifti), başıboş VERB kalmaz
        "text": "koşa koşa geldi",
        "roots": {"koşmak", "gelmek"},
        "expected": {
            "tag": "S",
            "children": [
                {"tag": "VP", "children": [
                    {"tag": "AdvP", "surface": "koşa koşa"},
                    {"tag": "VERB", "token": "geldi"},
                ]},
            ],
        },
    },
    {   # adnominal guard: uzun uzun yollar → NP, AdvP YOK
        "text": "uzun uzun yollar",
        "roots": {"uzun", "yol"},
        "expected": {"tag": "NP", "surface": "uzun uzun yollar"},
    },
    {   # derece-çift: çok çok güzel → AdvP (sonraki NOUN değil). Kök S (güzel ADJ kalır → S'ye sarılır).
        "text": "çok çok güzel",
        "roots": {"güzel"},
        "expected": {
            "tag": "S",
            "children": [
                {"tag": "AdvP", "surface": "çok çok"},
                {"tag": "ADJ", "token": "güzel"},
            ],
        },
    },
    {   # derece-çift + NOUN: guard skip → NP (adnominal)
        "text": "çok çok kitap",
        "roots": {"kitap"},
        "expected": {"tag": "NP", "surface": "çok çok kitap"},
    },
]
```
NOT [hakem #4]: `çok çok güzel` kökü **S** (AdvP tek başına değil — R8 sonrası nodes=[AdvP, ADJ güzel], VERB
yok → S'ye sarılır). Yukarıdaki beklenen yapı bunu yansıtır. Opus golden'ı yazarken ampirik ağaçla teyit eder.

- [ ] **Step 3: AdvP dependency case'ini `tests/golden_dependency.py` `DEP_CASES` sonuna ekle**

```python
    {   # ikileme: baş→fiil advmod, ikinci→baş compound:redup
        "text": "yavaş yavaş yürüdü",
        "roots": {"yavaş", "yürümek"},
        "expected": [
            {"id": 1, "form": "yavaş", "lemma": "yavaş",   "upos": "ADJ",
             "head": 3, "deprel": "advmod"},
            {"id": 2, "form": "yavaş", "lemma": "yavaş",   "upos": "ADJ",
             "head": 1, "deprel": "compound:redup"},
            {"id": 3, "form": "yürüdü","lemma": "yürümek", "upos": "VERB",
             "head": 0, "deprel": "root"},
        ],
    },
]
```
NOT: `upos`/`lemma` beklenen değerleri motorun leksikon/analiz davranışından türer.

- [ ] **Step 3b (ZORUNLU) [hakem #5]: `yavaş` upos'unu AMPİRİK yakala**

RED'in `upos` yüzünden yanlış nedenle kırılmaması için, golden'ı sabitlemeden önce `yavaş`'ın gerçek upos'unu ölç:

Run: `PYTHONUTF8=1 python -c "from turkgram import tokenize,parse_text; from turkgram.parse import parse_phrase; from turkgram.dependency import constituency_to_dep; t=parse_phrase(tokenize('yavaş yavaş yürüdü'), parse_text('yavaş yavaş yürüdü',{'yavaş','yürümek'})); print([(d.form,d.upos) for d in constituency_to_dep(t)])"`

`yavaş` ADJ değil NOUN dönerse, dependency golden'daki `"upos": "ADJ"` değerlerini gerçek değerle güncelle (upos motor olgusu; motoru golden'a uydurma). deprel/head beklenenleri (advmod/compound:redup) DEĞİŞMEZ — onlar dilbilgisi olgusu.

- [ ] **Step 4: RED doğrula**

Run: `python -m pytest tests/test_parse.py tests/test_dependency.py -q`
Expected: Yeni case'ler FAIL (R8_redup yok → `yavaş yavaş` AdjP olur / `koşa koşa` başıboş; dependency `advmod`/`compound:redup` yerine yanlış ilişki). Mevcut case'ler PASS kalmalı.

- [ ] **Step 5: Commit (RED golden)**

```bash
git add tests/golden_parse.py tests/golden_dependency.py
git commit -m "test(parse): ikileme AdvP bağımsız golden (motor-körü, RED)"
```

---

## Task 2: `_apply_r8_redup` + pipeline + R5 absorpsiyon (parse.py)

**Files:**
- Modify: `turkgram/parse.py` — yeni fonksiyon; pipeline (satır 382-392); R5 absorpsiyon (satır 335)

- [ ] **Step 1: `_apply_r8_redup` fonksiyonunu yaz**

`turkgram/parse.py`'de `_apply_r5`'ten önce (veya diğer `_apply_*`'ların yanına) ekle:

```python
def _apply_r8_redup(nodes: list) -> list:
    """R8: bitişik özdeş çift → AdvP (ikileme adverbial-yeniden-kurulum).

    Tam ikileme (yavaş yavaş) + ulaç ikilemesi (koşa koşa) → AdvP.
    Sınıflama: VERB çifti → ulaç-tipi (guard'sız); ADJ/NOUN çifti → tam-tipi
    (sonraki NOUN ise adnominal → skip, R1'e bırak). m-ikileme kapsam dışı.
    """
    from .analysis import _tr_lower  # Türkçe İ/I güvenli küçültme (cycle yok)
    out, i = [], 0
    while i < len(nodes):
        a, b = nodes[i], nodes[i + 1] if i + 1 < len(nodes) else None
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
```

- [ ] **Step 2: Pipeline'a ekle (R0'dan önce)**

`turkgram/parse.py:382-383`, `_apply_r0`'dan ÖNCE:

```python
    nodes: list[PhraseNode | LeafNode] = list(leaves)
    nodes = _apply_r8_redup(nodes)  # AdvP: bitişik özdeş çift (R3/R1'den ÖNCE)
    nodes = _apply_r0(nodes)      # NP: NOUN[gen] NOUN[poss] (belirtili tamlama)
```

- [ ] **Step 3: R5 absorpsiyon kümesine `"AdvP"` ekle**

`turkgram/parse.py:335`:

```python
            if tag not in ("NP", "PP", "AdjP", "CoordP", "NOUN", "AdvP"):
```

- [ ] **Step 3b [hakem #6]: `PhraseNode` docstring'ini güncelle**

`turkgram/parse.py:45` (bayat — E3/E4 etiketleri de eksik):

```python
    tag: str  # 'NP'|'VP'|'S'|'AdjP'|'PP'|'CoordP'|'CompP'|'RelP'|'DiyeP'|'AdvP'
```

- [ ] **Step 4: Parse golden'ını koş (GREEN, parse ağaçları)**

Run: `python -m pytest tests/test_parse.py -q`
Expected: PASS — `yavaş yavaş yürüdü`/`koşa koşa geldi`/`uzun uzun yollar`/`çok çok güzel`/`çok çok kitap` + tüm mevcut E2/E3/E4 case'leri.

Kırmızıysa: (a) `koşa` gerçekten VERB mi (`PYTHONUTF8=1 python -c "from turkgram import tokenize,parse_text; from turkgram.parse import parse_phrase; print(parse_phrase(tokenize('koşa koşa geldi'), parse_text('koşa koşa geldi',{'koşmak','gelmek'})))"`) — optatif VERB bekleniyor. (b) `uzun uzun yollar` AdvP oldu mu → guard'ı kontrol et (sonraki tag "NOUN" mu). Motoru golden'a uydur, golden'ı motora DEĞİL — ama golden motor-körü doğru kurulduysa motor hatası.

- [ ] **Step 5: Tam parse regresyonu**

Run: `python -m pytest tests/test_parse.py tests/test_parse_text.py tests/test_subordinate.py -q`
Expected: PASS (mevcut ağaçlar değişmedi — AdvP yalnız özdeş-çift + non-NOUN-takip).

- [ ] **Step 6: Commit**

```bash
git add turkgram/parse.py
git commit -m "feat(parse): _apply_r8_redup — ikileme AdvP + NOUN-takip guard + VP absorpsiyon"
```

---

## Task 3: dependency.py — advmod + compound:redup (GREEN, dependency)

**Files:**
- Modify: `turkgram/dependency.py` — `_find_head_leaf` (satır 117-154); `_child_deprel` (satır 156-194)

- [ ] **Step 1: `_find_head_leaf`'e AdvP dalı ekle**

`turkgram/dependency.py`, `_find_head_leaf` içinde `if tag == "CoordP":` (satır 152) DALINDAN ÖNCE ekle:

```python
        if tag == "AdvP":
            return _find_head_leaf(children[0])  # ilk yaprak = baş
```

- [ ] **Step 2: `_child_deprel` VP/S dalını genişlet + AdvP-ebeveyn dalı ekle**

`turkgram/dependency.py:192-193`, VP/S bloğundaki `if child_tag in ("AdjP",):` satırını genişlet:

```python
            if child_tag in ("AdjP", "AdvP"):
                return "advmod"
```

Ayrıca AdvP iç ilişkisi için **top-level** `if parent_tag == "AdvP":` dalı ekle — `if parent_tag == "AdjP":`
bloğundan (satır 173-175) SONRA, `if parent_tag == "CoordP":` bloğundan (satır 176) ÖNCE. **VP/S bloğunun
İÇİNE değil**, kardeş `if parent_tag ==` guard'larıyla aynı nesting seviyesinde:

```python
        if parent_tag == "AdjP":
            if child_tag == "ADJ":
                return "advmod"
        if parent_tag == "AdvP":              # ← YENİ, top-level
            return "compound:redup"           # ikinci token (tekrar) → baş
        if parent_tag == "CoordP":
            ...
```
Bu dal `if parent_tag in ("VP","S")` bloğundan ÖNCE döndüğünden `_find_head_leaf`/case hesabına hiç ulaşmaz
(çökme riski yok).

- [ ] **Step 3: Dependency golden'ını koş (GREEN)**

Run: `python -m pytest tests/test_dependency.py -q`
Expected: PASS — `yavaş yavaş yürüdü` → id1 advmod→3, id2 compound:redup→1, id3 root. Mevcut dependency + CoNLL-U case'leri değişmedi.

Kırmızıysa: `upos` beklenen değeri tutmuyorsa (ör. `yavaş` NOUN döndü) golden upos'unu ampirik değere göre düzelt (upos motor olgusu, motor-körü golden dilbilgisi-varsayımını ampirik doğrular). `deprel` yanlışsa `_child_deprel` dallarını denetle.

- [ ] **Step 4: Commit**

```bash
git add turkgram/dependency.py
git commit -m "feat(dependency): AdvP advmod (baş→fiil) + compound:redup (tekrar→baş)"
```

---

## Task 4: Hakem — korpus tarama + tam doğrulama

**Files:**
- Create: `tools/sweep_adverbial.py`

- [ ] **Step 1: Parse tarama aracını yaz**

`tools/sweep_adverbial.py`:

```python
"""İkileme adverbial parse taraması — çökme yok + AdvP kurulum kontrolü."""
import sys
from turkgram import tokenize, parse_text
from turkgram.parse import parse_phrase
from turkgram.dependency import constituency_to_dep

# Temsili ikileme cümleleri (tam + ulaç + adnominal guard + m-kapsam-dışı)
CASES = [
    ("yavaş yavaş yürüdü", {"yavaş", "yürümek"}),
    ("koşa koşa geldi", {"koşmak", "gelmek"}),
    ("güle güle gitti", {"gülmek", "gitmek"}),
    ("hızlı hızlı koştu", {"hızlı", "koşmak"}),
    ("uzun uzun yollar", {"uzun", "yol"}),      # adnominal → NP, AdvP yok
    ("çok çok güzel", {"güzel"}),
    ("kitap mitap aldı", {"kitap", "almak"}),   # m-ikileme kapsam dışı (AdvP olmamalı)
]

def _has_advp(node):
    if getattr(node, "tag", None) == "AdvP":
        return True
    return any(_has_advp(c) for c in getattr(node, "children", ()))

def main():
    crashes = 0
    for text, roots in CASES:
        try:
            tree = parse_phrase(tokenize(text), parse_text(text, roots))
            dep = constituency_to_dep(tree)  # dependency çökme kontrolü
            print(f"{text!r}: AdvP={_has_advp(tree)}, {len(dep)} token")
        except Exception as e:
            crashes += 1
            print(f"CRASH {text!r}: {e}")
    print(f"\nTARAMA BİTTİ. Çökme: {crashes}")
    return 1 if crashes else 0

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Taramayı koş**

Run: `PYTHONUTF8=1 python tools/sweep_adverbial.py`
Expected: `Çökme: 0`. `uzun uzun yollar` → AdvP=False; `kitap mitap aldı` → AdvP=False (m-ikileme kapsam dışı); diğerleri → AdvP=True.

- [ ] **Step 3: Adversarial hakem (CLAUDE.md §2)**

Subagent hakem dispatch et:
1. `_apply_r8_redup` guard'ı gerçekten yalnız adnominal'ı mı koruyor, yoksa geçerli AdvP'leri de mi buduyor?
2. R8'in R0/R3/R1 ile etkileşimi tüm mevcut parse case'lerini koruyor mu (özdeş-token'lı mevcut cümle var mı)?
3. `compound:redup` iç ilişkisi CoNLL-U çıktısında UD-geçerli mi; ikinci token upos'u doğru mu?

- [ ] **Step 4: Tam paket + slow**

Run: `python -m pytest -q -m "not slow"` sonra `python -m pytest -q -m slow`
Expected: PASS (regresyonsuz).

- [ ] **Step 5: Commit + docs**

```bash
git add tools/sweep_adverbial.py
git commit -m "test(sweep): ikileme adverbial parse taraması (0 çökme hakem)"
```

Ardından CLAUDE.md §7 + README + memory `faz-durumu.md` güncellenir (ikileme adverbial TAMAMLANDI, AdvP etiketi, test sayısı).

---

## Bitiş Kontrol Listesi

- [ ] `yavaş yavaş yürüdü` → `VP(AdvP, yürüdü)`; AdvP etiketi (AdjP değil)
- [ ] `koşa koşa geldi` → `VP(AdvP, geldi)`; başıboş VERB kalmaz
- [ ] `uzun uzun yollar` → `NP` (adnominal guard; AdvP yok)
- [ ] `çok çok güzel` → AdvP; `çok çok kitap` → NP
- [ ] Dependency: AdvP başı `advmod`→fiil, ikinci token `compound:redup`→baş
- [ ] m-ikileme (`kitap mitap`) AdvP kurmaz (kapsam dışı korundu)
- [ ] Mevcut E2/E3/E4 parse + dependency + CoNLL-U testleri değişmez
- [ ] Korpus tarama 0 çökme; tam paket + slow regresyonsuz
- [ ] Docs güncel (CLAUDE.md §7, README, memory)
