# Faz 5 D4 — Bağlaç Morfolojisi Implementasyon Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `turkgram/conjunction.py` bağımsız modülü: `de/da` klitik ses uyumu, koordinasyon sentezi (ikili/üçlü/korelatif), `analyze()` `kind='conjunction'` genişletmesi, TR API sarmalayıcıları.

**Architecture:** CLAUDE.md §2 iş akışı — SPEC → bağımsız golden (Opus, motor-körü) → motor → hakem. `conjunction.py` `postposition.py` pattern'ini izler (kapalı-küme + durum yönetimi). `analyze()` oracle-dışı `_try_conjunction_all()` dalıyla genişletilir. TR API `tr.py`'ye eklenir.

**Tech Stack:** Python 3.9+, pytest, mevcut `_last_vowel()` primitifi, `turkgram/analysis.py` dispatch zinciri.

---

## Dosya Haritası

| İşlem | Dosya | Sorumluluk |
|---|---|---|
| Oluştur | `spec/conjunction-spec.md` | Dilbilgisi kuralları (SPEC) |
| Oluştur | `turkgram/conjunction.py` | `conjoin()`, `coordinate()`, `CONJUNCTIONS` |
| Oluştur | `tests/golden_conjunction.py` | Bağımsız golden veri |
| Oluştur | `tests/test_conjunction.py` | pytest runner |
| Değiştir | `turkgram/analysis.py` | `_try_conjunction_all()`, `_KINDS`, `_POS` |
| Değiştir | `turkgram/tr.py` | `bağla()`, `koordine_et()`, `_BAĞLAÇ` |
| Değiştir | `turkgram/__init__.py` | `conjunction`, `conjoin`, `coordinate` export |

---

## Task 1: SPEC Yazımı

**Files:**
- Create: `spec/conjunction-spec.md`

- [ ] **Step 1: SPEC dosyasını yaz**

`spec/conjunction-spec.md` içeriği (dilbilgisi kuralları, kapalı küme, de/da uyumu, tuzaklar):

```markdown
# Bağlaç Morfolojisi SPEC (Faz 5 D4)

## 1. Kapalı Küme

Koordinatif bağlaçlar (değişmez biçimler, ayrı yazılır):
  ve, ama, fakat, lakin, ancak, çünkü, oysa, halbuki,
  yoksa, ya da, veya, yahut, üstelik, hatta, bile, dahi, ise, ki

Klitik: de / da (ses uyumlu; yalnız `conjoin()` içinde dinamik seçilir)

Korelatif çiftler (`coordinate()` için conj parametresi):
  hem_hem    → hem X hem Y
  ya_ya      → ya X ya Y
  ne_ne      → ne X ne Y
  ister_ister → ister X ister Y
  gerek_gerek → gerek X gerek Y
  hem_hem_de → hem X hem de Y

## 2. de/da Klitik Fonolojisi

Türkçe büyük ünlü uyumu: son ünlüye bak:
  art ünlü (a, ı, o, u) → da
  ön ünlü  (e, i, ö, ü) → de

Daima ayrı yazılır: "eve de", "okula da"
Ünsüz mutasyonu UYGULANMAZ.

Fallback (_last_vowel() None dönerse): → "de" (ön ünlü varsayılan)
Örnekler: NATO de, 3 de

## 3. ise Bağlacı

Bağlaç olarak "ise" daima ayrı yazılır, değişmez:
  "elma ise", "araba ise"
Enclitic -sA (koşul kipi eki) FARKLI yapı — bu modül kapsamı dışı.

## 4. conjoin(word, conj) Davranışı

- conj == "de/da": ses uyumu uygula, word + " " + allomorf döndür
- conj diğer koordinatifler: word + " " + conj döndür
- conj bilinmeyen: ValueError (geçerli seçenekleri listele)
- word boş/None: ValueError

## 5. coordinate(items, conj) Davranışı

- items boş ([]) → ValueError
- items tek öğe (["X"]) → "X" (değişmez)
- items iki öğe, koordinatif: "X conj Y"
- items üç+ öğe, koordinatif: "X, Y, ... conj Z"
- items iki öğe, korelatif (hem_hem): "hem X hem Y"
- items iki öğe, korelatif (ya_ya): "ya X ya Y"
- items iki öğe, korelatif (ne_ne): "ne X ne Y"
- items iki öğe, korelatif (ister_ister): "ister X ister Y"
- items iki öğe, korelatif (gerek_gerek): "gerek X gerek Y"
- items iki öğe, korelatif (hem_hem_de): "hem X hem de Y"
- korelatif + 3+ öğe → ValueError (korelatifler yalnız 2 öğe)
- conj bilinmeyen → ValueError

## 6. analyze() Entegrasyonu

_try_conjunction_all(surface) — oracle dışı, kapalı-liste:
  surface == "de" → Analysis(lemma="de", kind="conjunction", pos="conj",
                             axes={}, segments=[("de","conj")])
  surface == "da" → Analysis(lemma="de", kind="conjunction", pos="conj",
                             axes={}, segments=[("da","conj")])
  diğer → []

Bilinçli belirsizlik: analyze("de") hem bağlaç hem demek-imp-2sg döndürür.
Precision golden: want <= got koşuluyla (her iki analizin döndüğünü doğrular).

_KINDS'a "conjunction" eklenir.
_POS'a "conj" eklenir.
```

- [ ] **Step 2: Commit**

```bash
git add spec/conjunction-spec.md
git commit -m "spec(conjunction): Faz 5 D4 bağlaç morfolojisi SPEC"
```

---

## Task 2: Bağımsız Golden

**Files:**
- Create: `tests/golden_conjunction.py`

> **NOT:** Bu task bir subagent (Opus, motor-körü) tarafından yapılmalıdır.
> Subagent'e verilecek bağlam: yalnız `spec/conjunction-spec.md` + dilbilgisi bilgisi.
> Motor/mevcut kod GÖRÜLMEZ. Elle doğrulanmış beklentiler.

- [ ] **Step 1: Opus subagent ile golden oluştur**

Subagent prompt özeti:
```
turkgram Faz 5 D4 bağlaç morfolojisi için bağımsız golden veri dosyası oluştur.
YALNIZ spec/conjunction-spec.md + dilbilgisi bilgisini kullan. Mevcut kodu GÖRME.

Dosya: tests/golden_conjunction.py
Format: GOLDEN_CONJOIN + GOLDEN_COORDINATE + GOLDEN_ANALYZE listeleri.

Her giriş:
  conjoin:    (word, conj, expected)
  coordinate: (items, conj, expected) veya {"items":..., "conj":..., "expected":...}
  analyze:    (surface, want_subset) — want_subset ⊆ got (bilinçli belirsizlik)

Kapsam:
- de/da uyumu: 8 ön ünlü + 8 art ünlü örneği (farklı kelimeler)
- de/da fallback: sayı/yabancı (NATO, 3) — 4 örnek
- ise: ayrı yazılır, değişmez — 4 örnek
- diğer koordinatifler (ve, ama, fakat, vb.) — 10 örnek
- coordinate ikili koordinatif — 8 örnek
- coordinate üçlü koordinatif — 4 örnek
- coordinate korelatif (6 çeşit) — 12 örnek
- coordinate kenar: boş→ValueError, tek→aynen — 4 örnek
- analyze("de") → iki analiz (conjunction + demek) — 2 örnek
- analyze("da") → conjunction — 1 örnek
```

- [ ] **Step 2: Golden dosyayı kaydet ve commit et**

```bash
git add tests/golden_conjunction.py
git commit -m "test(conjunction): bağımsız golden (motor-körü, Opus)"
```

---

## Task 3: conjunction.py Motoru

**Files:**
- Create: `turkgram/conjunction.py`

- [ ] **Step 1: Boş modül iskeletini yaz, testi koş (RED)**

İlk: yalnız import'un çalıştığını doğrula (Task 4'teki runner henüz yok; bu adımda sadece modülü yaz, syntactic doğrulama yap):

```bash
PYTHONUTF8=1 python -c "from turkgram.conjunction import conjoin, coordinate, CONJUNCTIONS; print('OK')"
```

Beklenti: ModuleNotFoundError (henüz dosya yok).

- [ ] **Step 2: conjunction.py'yi yaz**

```python
"""conjunction.py — Türkçe bağlaç koordinasyonu (Faz 5 D4)."""
from __future__ import annotations

from .morphology import _last_vowel   # ses uyumu primitifi

# Kapalı küme — koordinatif bağlaçlar
CONJUNCTIONS: frozenset[str] = frozenset({
    "ve", "ama", "fakat", "lakin", "ancak", "çünkü", "oysa", "halbuki",
    "yoksa", "ya da", "veya", "yahut", "üstelik", "hatta", "bile", "dahi",
    "ise", "ki",
    "de", "da",
    "hem", "ya", "ne", "ister", "gerek",
})

# Tüm geçerli conj değerleri — conjoin()/coordinate() parametresi için
# de ve da ayrı anahtar (ikisi de ses uyumunu _de_da() içinde çözer)
# hem_hem ve hem_hem_de FARKLI korelatifler (her ikisi _VALID_CONJ'da)
_VALID_CONJ: frozenset[str] = frozenset({
    "ve", "ama", "fakat", "lakin", "ancak", "çünkü", "oysa", "halbuki",
    "yoksa", "ya da", "veya", "yahut", "üstelik", "hatta", "bile", "dahi",
    "ise", "ki",
    "de", "da",   # hem "de" hem "da" ayrı; _de_da() zaten doğruyu seçer
    "hem_hem", "ya_ya", "ne_ne", "ister_ister", "gerek_gerek", "hem_hem_de",
})

_CORRELATIVES: frozenset[str] = frozenset({
    "hem_hem", "ya_ya", "ne_ne", "ister_ister", "gerek_gerek", "hem_hem_de",
})

_ART_VOWELS: frozenset[str] = frozenset("aıou")
_ON_VOWELS:  frozenset[str] = frozenset("eiöü")


def _de_da(word: str) -> str:
    """son ünlüye göre 'de' veya 'da' döndür; fallback → 'de'."""
    v = _last_vowel(word)
    if v is None or v in _ON_VOWELS:
        return "de"
    return "da"


def conjoin(word: str, conj: str) -> str:
    """Kelimeye bağlaç ekle.

    de/da: son ünlüye göre ses uyumu uygulanır (ayrı yazılır).
    Diğerleri: word + ' ' + conj (ayrı, değişmez).
    NOT: -de/-da durum eki için decline(case='loc') kullanın.

    Raises:
        ValueError: Boş word veya bilinmeyen conj.
    """
    if not word or not word.strip():
        raise ValueError("word boş olamaz.")
    if conj not in _VALID_CONJ:
        raise ValueError(
            f"Bilinmeyen bağlaç: {conj!r}. Geçerliler: {sorted(_VALID_CONJ)}"
        )
    if conj in ("de", "da"):   # ikisi de ses uyumuna gider; sonuç _de_da()'dan
        return word.strip() + " " + _de_da(word.strip())
    return word.strip() + " " + conj


def coordinate(items: list[str], conj: str) -> str:
    """Öğe listesini bağlaçla koordine et.

    Boş liste → ValueError.
    Tek öğe   → öğeyi değişmez döndür.
    İkili     → 'X conj Y'
    Üçlü+     → 'X, Y, ... conj Z'
    Korelatif → 'HEM X HEM Y' / 'YA X YA Y' vb. (yalnız 2 öğe).

    Raises:
        ValueError: Boş liste, bilinmeyen conj, korelatif + 3+ öğe.
    """
    if not items:
        raise ValueError("items boş olamaz.")
    if conj not in _VALID_CONJ:
        raise ValueError(
            f"Bilinmeyen bağlaç: {conj!r}. Geçerliler: {sorted(_VALID_CONJ)}"
        )
    if len(items) == 1:
        return items[0]
    if conj in _CORRELATIVES:
        if len(items) != 2:
            raise ValueError(
                f"Korelatif '{conj}' yalnız 2 öğeyle kullanılır, {len(items)} verildi."
            )
        return _format_correlative(items[0], items[1], conj)
    # Koordinatif
    if len(items) == 2:
        return f"{items[0]} {conj} {items[1]}"
    return ", ".join(items[:-1]) + f" {conj} {items[-1]}"


def _format_correlative(a: str, b: str, conj: str) -> str:
    """İkili korelatif biçimlendirme."""
    if conj == "hem_hem":
        return f"hem {a} hem {b}"
    if conj == "ya_ya":
        return f"ya {a} ya {b}"
    if conj == "ne_ne":
        return f"ne {a} ne {b}"
    if conj == "ister_ister":
        return f"ister {a} ister {b}"
    if conj == "gerek_gerek":
        return f"gerek {a} gerek {b}"
    if conj == "hem_hem_de":
        return f"hem {a} hem de {b}"
    raise ValueError(f"Bilinmeyen korelatif: {conj!r}")  # savunma
```

- [ ] **Step 3: Import çalışıyor mu doğrula**

```bash
PYTHONUTF8=1 python -c "from turkgram.conjunction import conjoin, coordinate, CONJUNCTIONS; print('OK')"
```

Beklenti: `OK`

- [ ] **Step 4: Commit**

```bash
git add turkgram/conjunction.py
git commit -m "feat(conjunction): conjoin + coordinate motoru (Faz 5 D4)"
```

---

## Task 4: Test Runner

**Files:**
- Create: `tests/test_conjunction.py`

- [ ] **Step 1: Runner yaz**

```python
"""test_conjunction.py — Faz 5 D4 bağlaç runner."""
import pytest
from tests.golden_conjunction import GOLDEN_CONJOIN, GOLDEN_COORDINATE, GOLDEN_ANALYZE
from turkgram.conjunction import conjoin, coordinate
from turkgram import analyze


@pytest.mark.parametrize("word,conj,expected", GOLDEN_CONJOIN)
def test_conjoin(word, conj, expected):
    assert conjoin(word, conj) == expected


@pytest.mark.parametrize("items,conj,expected", GOLDEN_COORDINATE)
def test_coordinate(items, conj, expected):
    assert coordinate(items, conj) == expected


def test_coordinate_empty_raises():
    with pytest.raises(ValueError):
        coordinate([], "ve")


def test_coordinate_unknown_conj_raises():
    with pytest.raises(ValueError):
        coordinate(["a", "b"], "xyz_bilinmeyen")


def test_conjoin_empty_raises():
    with pytest.raises(ValueError):
        conjoin("", "ve")


def test_conjoin_unknown_conj_raises():
    with pytest.raises(ValueError):
        conjoin("ev", "xyz_bilinmeyen")


def test_coordinate_correlative_three_raises():
    with pytest.raises(ValueError):
        coordinate(["a", "b", "c"], "hem_hem")


@pytest.mark.parametrize("surface,want_subset", GOLDEN_ANALYZE)
def test_analyze_conjunction(surface, want_subset):
    """want_subset ⊆ got (bilinçli belirsizlik: de = bağlaç + demek)."""
    results = analyze(surface)
    kinds = {a.kind for a in results}
    lemmas = {a.lemma for a in results}
    for item in want_subset:
        if "kind" in item:
            assert item["kind"] in kinds, f"{surface!r}: kind={item['kind']!r} bulunamadı"
        if "lemma" in item:
            assert item["lemma"] in lemmas, f"{surface!r}: lemma={item['lemma']!r} bulunamadı"
```

- [ ] **Step 2: Testleri koş (kısmen RED — analyze entegrasyonu henüz yok)**

```bash
PYTHONUTF8=1 pytest tests/test_conjunction.py -v 2>&1 | head -40
```

Beklenti: `test_conjoin` ve `test_coordinate` testleri PASS; `test_analyze_conjunction` FAIL (conjunction kind henüz analyze()'de yok).

- [ ] **Step 3: Commit**

```bash
git add tests/test_conjunction.py
git commit -m "test(conjunction): runner (Faz 5 D4)"
```

---

## Task 5: analyze() Entegrasyonu

**Files:**
- Modify: `turkgram/analysis.py` (satır 67-70 + satır 896-908 arası)

- [ ] **Step 1a: _POS'a "conj" ekle (ZORUNLU — önce bu)**

`turkgram/analysis.py`'de `_POS` tuple'ını bul (grep: `_POS = `):

```python
_POS = ("verb", "noun", "adj", "num", "conj")   # "conj" eklendi
```

Bu adım yapılmazsa `analyze(surface, pos="conj")` çağrısı `ValueError` fırlatır.

- [ ] **Step 1b: _KINDS'a "conjunction" ekle — SONA EKLE (sort önceliği = en düşük)**

`_KINDS` tuple'ını bul (grep: `_KINDS = `). `"conjunction"` tuple'ın **sonuna** eklenir (sort key = en yüksek indeks; morfolojik kind'lardan sonra sıralanır):

```python
_KINDS = ("conjugate", "decline", "copula", "converb",
          "converb_casina", "converb_ken", "participle",
          "intensify", "diminutive", "ordinal", "distributive",
          "conjunction")   # SONA eklendi — sort önceliği en düşük
```

- [ ] **Step 2: _try_conjunction_all() fonksiyonunu ekle**

`analysis.py`'nin sonuna (örn. `_try_number_all`'dan sonra) ekle:

```python
def _try_conjunction_all(surface: str, analyses: list[Analysis], seen: set[tuple]) -> None:
    """Bağlaç çözümlemesi — oracle dışı, kapalı-liste.

    Yalnız 'de' ve 'da' tam-token eşleşmesinde tetiklenir.
    Bilinçli belirsizlik: 'de' = bağlaç VE demek imp-2sg.
    """
    if surface not in ("de", "da"):
        return
    key = ("conjunction", "de", frozenset())
    if key in seen:
        return
    seen.add(key)
    analyses.append(Analysis(
        lemma="de",
        pos="conj",
        kind="conjunction",
        kwargs={},
        segments=_segs_to_tuple([(surface, "conj")]),
        hypothetical=False,
    ))
```

- [ ] **Step 3: analyze() dispatch zincirine ekle**

`analyze()` fonksiyonu içindeki tek-token dalına `_try_number_all`'dan ÖNCE ekle.
Bulmak için grep: `_try_number_all(surface_token`. O satırdan önce:

```python
    # Bağlaç çözümlemesi (kapalı liste, oracle dışı)
    # NOT: pos=="conj" geçerli çünkü Step 1a'da _POS'a eklendi
    if pos in (None, "conj"):
        _try_conjunction_all(surface_token, analyses, seen)
```

- [ ] **Step 4: pos filtresi otomatik çalışır — doğrula**

`analyze()` içindeki validation bloğunu bul (grep: `pos not in _POS`):
Step 1a'da `"conj"` _POS'a eklendiği için bu blok otomatik çalışır. Ek değişiklik gerekmez.
Doğrulama:

```bash
PYTHONUTF8=1 python -c "from turkgram import analyze; print(analyze('de', pos='conj'))"
```

Beklenti: conjunction analizi döner (ValueError atılmaz).

- [ ] **Step 5: Tüm testleri koş**

```bash
PYTHONUTF8=1 pytest tests/test_conjunction.py -v
```

Beklenti: Tüm testler PASS.

Regresyon kontrolü:

```bash
PYTHONUTF8=1 pytest --ignore=tests/test_slow.py -q 2>&1 | tail -5
```

Beklenti: Önceki test sayısı + ~80 yeni test, 0 FAIL.

- [ ] **Step 6: Commit**

```bash
git add turkgram/analysis.py
git commit -m "feat(analysis): conjunction kind — _try_conjunction_all, _KINDS, _POS (Faz 5 D4)"
```

---

## Task 6: TR API + __init__.py

**Files:**
- Modify: `turkgram/tr.py`
- Modify: `turkgram/__init__.py`

- [ ] **Step 1: tr.py'ye _BAĞLAÇ + bağla() + koordine_et() ekle**

`turkgram/tr.py`'ye `edat_obeği()`'nin ardından ekle:

```python
from .conjunction import conjoin as _conjoin, coordinate as _coordinate

_BAĞLAÇ: dict[str, str] = {
    # Koordinatifler
    "ve": "ve", "ama": "ama", "fakat": "fakat", "lakin": "lakin",
    "ancak": "ancak", "çünkü": "çünkü", "oysa": "oysa",
    "halbuki": "halbuki", "yoksa": "yoksa", "ya da": "ya da",
    "veya": "veya", "yahut": "yahut", "üstelik": "üstelik",
    "hatta": "hatta", "bile": "bile", "dahi": "dahi", "ise": "ise",
    # Klitik — iki ayrı anahtar; conjoin("de") / conjoin("da") _de_da() içinde çözer
    "de": "de",
    "da": "da",
    # Korelatifler (Türkçe boşluklu → iç alt-çizgili)
    "hem hem": "hem_hem",
    "ya ya": "ya_ya",
    "ne ne": "ne_ne",
    "ister ister": "ister_ister",
    "gerek gerek": "gerek_gerek",
    "hem hem de": "hem_hem_de",
}


def bağla(kelime: str, bağlaç: str) -> str:
    """Kelimeye bağlaç ekle (Türkçe API).

    bağlaç: 've' | 'ama' | 'de' | 'da' | 'hem hem' | 'ya ya' | 've' | ...
    de/da klitik: ses uyumu otomatik uygulanır.

    >>> bağla('eve', 'de')     # 'eve de'
    >>> bağla('okula', 'da')   # 'okula da'
    >>> bağla('elma', 've')    # 'elma ve'
    """
    norm = _tr_lower(bağlaç.strip())
    if norm not in _BAĞLAÇ:
        raise ValueError(
            f"Bilinmeyen bağlaç: {bağlaç!r}. Geçerliler: {sorted(_BAĞLAÇ)}"
        )
    return _conjoin(kelime, _BAĞLAÇ[norm])


def koordine_et(ögeler: list[str], bağlaç: str) -> str:
    """Öğe listesini bağlaçla koordine et (Türkçe API).

    Not: tr.sıralı() (sayı sıra eki) ile karışmaması için 'koordine_et' seçildi.

    >>> koordine_et(['elma', 'armut'], 've')          # 'elma ve armut'
    >>> koordine_et(['elma', 'armut', 'kiraz'], 've') # 'elma, armut ve kiraz'
    >>> koordine_et(['hızlı', 'güçlü'], 'hem hem')   # 'hem hızlı hem güçlü'
    """
    norm = _tr_lower(bağlaç.strip())
    if norm not in _BAĞLAÇ:
        raise ValueError(
            f"Bilinmeyen bağlaç: {bağlaç!r}. Geçerliler: {sorted(_BAĞLAÇ)}"
        )
    return _coordinate(ögeler, _BAĞLAÇ[norm])
```

- [ ] **Step 2: __init__.py'yi güncelle**

`turkgram/__init__.py`'de iki güncelleme:

Import satırına `conjunction` ekle (satır ~28):
```python
    lexicon, disambiguation, compound, context, adjective, syntax, postposition,
    conjunction,   # D4
```

Symbol export'larına ekle (satır ~71'den sonra):
```python
from .conjunction import conjoin, coordinate, CONJUNCTIONS
```

`__all__`'a ekle (satır ~121):
```python
    "postposition", "conjunction",
    "conjoin", "coordinate", "CONJUNCTIONS",
```

- [ ] **Step 3: TR denklik testleri koş**

```bash
PYTHONUTF8=1 python -c "
from turkgram.tr import bağla, koordine_et
print(bağla('eve', 'de'))          # eve de
print(bağla('okula', 'da'))        # okula da (ses uyumu: da)
print(koordine_et(['a','b'], 've')) # a ve b
print(koordine_et(['a','b'], 'hem hem'))  # hem a hem b
"
```

- [ ] **Step 4: Tam paket testi**

```bash
PYTHONUTF8=1 pytest --ignore=tests/test_slow.py -q 2>&1 | tail -5
```

Beklenti: Tüm testler PASS, 0 FAIL.

- [ ] **Step 5: Commit**

```bash
git add turkgram/tr.py turkgram/__init__.py
git commit -m "feat(tr): bağla + koordine_et TR API + __init__ export (Faz 5 D4)"
```

---

## Task 7: Hakem + Korpus Taraması

**Files:**
- Read: `turkgram/lexicon.py` (leksikon yükleme)

- [ ] **Step 1: Korpus taraması — conjoin de/da, 0 çökme**

```python
# tools/check_conjunction_corpus.py (geçici, commit'lenmez)
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
from turkgram.lexicon import load
from turkgram.conjunction import conjoin

roots = load()
errors = []
for lemma in sorted(roots):
    for conj in ["de/da"]:
        try:
            conjoin(lemma, conj)
        except Exception as e:
            errors.append((lemma, conj, str(e)))

print(f"Tarandı: {len(roots)} lemma × de/da = {len(roots)} çağrı")
print(f"Hata: {len(errors)}")
for e in errors[:10]:
    print(e)
```

```bash
PYTHONUTF8=1 python tools/check_conjunction_corpus.py
```

Beklenti: `Hata: 0`

- [ ] **Step 2: Korpus taraması — coordinate, 0 çökme**

```python
# Aynı scripte ekle:
from turkgram.conjunction import coordinate, _VALID_CONJ
coord_conj = [c for c in _VALID_CONJ if c not in ("de/da",)]
sample = list(roots)[:100]
for conj in coord_conj:
    for a, b in zip(sample[::2], sample[1::2]):
        try:
            coordinate([a, b], conj)
        except Exception as e:
            errors.append(([a, b], conj, str(e)))
```

Beklenti: `Hata: 0`

- [ ] **Step 3: Hakem subagent dispatch**

Adversarial hakem için subagent dispatch et. Hakem bağlamı:

```
turkgram/conjunction.py motorunu gözden geçir. Bağımsız golden tests/golden_conjunction.py'yi gör.
Şunları kontrol et:
1. de/da ses uyumu tüm 8 ünlü için doğru mu?
2. coordinate() korelatif biçimleri SPEC ile eşleşiyor mu?
3. _try_conjunction_all() yalnız tam-token "de"/"da"'yı mı yakalıyor?
4. "de" belirsizliği (bağlaç + demek imp-2sg) golden'da doğru test ediliyor mu?
5. analyze() dispatch zinciri doğru sırada mı? Regresyon var mı?
CRITICAL / HIGH / MEDIUM / LOW formatında raporla.
```

- [ ] **Step 4: Hakem bulgularını gider, son commit**

```bash
PYTHONUTF8=1 pytest --ignore=tests/test_slow.py -q 2>&1 | tail -3
git add -A
git commit -m "docs(claude): Faz 5 D4 bağlaç morfolojisi tamamlandı — N test yeşil"
```

---

## Başarı Kriterleri

- [ ] `conjoin(word, "de/da")` 8 ön + 8 art ünlü için doğru allomorf
- [ ] `coordinate()` ikili/üçlü/6 korelatif çeşidi doğru
- [ ] `analyze("de")` hem `kind="conjunction"` hem `demek` imp-2sg döndürüyor
- [ ] `analyze("evde")` conjunction analizini DÖNDÜRMÜYOR (tam-token guard)
- [ ] `bağla()` ve `koordine_et()` TR API çalışıyor
- [ ] Tüm önceki testler yeşil (regresyon yok)
- [ ] Hakem 0 CRITICAL, 0 HIGH bulgu
- [ ] Leksikon korpusu 0 çökme
