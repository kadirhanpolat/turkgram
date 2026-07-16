# parse_text + Tokenizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `tokenize(text) → list[str]` ve `parse_text(text, roots=None) → list[list[Analysis]]` API'lerini ekle.

**Architecture:** Ayrı `tokenize.py` modülü (boşluk+noktalama+apostrof bölme); `parse_text` `analysis.py`'e eklenir ve `_cached_analyze` (lru_cache maxsize=4096) üzerinden `analyze()` çağırır. `rank_in_context` entegrasyonu H-10'u doğal çözer — mevcut guard zaten var.

**Tech Stack:** Python 3.10+, `re`, `functools.lru_cache`, `pytest`. Saf Python, ML yok.

**Spec:** `docs/superpowers/specs/2026-07-16-parse-text-tokenizer-design.md`

---

## Dosya Haritası

| İşlem | Dosya | Sorumluluk |
|---|---|---|
| Oluştur | `turkgram/tokenize.py` | `tokenize()` public API |
| Değiştir | `turkgram/analysis.py` | `_cached_analyze` + `parse_text` ekle |
| Değiştir | `turkgram/__init__.py` | `tokenize`, `parse_text` export |
| Oluştur | `tests/golden_tokenize.py` | Bağımsız tokenizer golden (motor-körü) |
| Oluştur | `tests/test_tokenize.py` | Golden runner |
| Oluştur | `tests/test_parse_text.py` | `parse_text` davranış testleri |

---

## Task 1: `tokenize.py` — Bağımsız Golden

**Files:**
- Create: `tests/golden_tokenize.py`

Golden verisi motordan bağımsız, elle-doğrulanmış olmalı. `tokenize()` henüz yazılmamış — golden önce geliyor (TDD).

- [ ] **Step 1: `golden_tokenize.py` dosyasını yaz**

```python
# tests/golden_tokenize.py
# Bağımsız golden — tokenize() motoruna BAKMADAN elle doğrulanmış.
# SAF VERİ — pytest toplamaz (test_ öneki yok, sınıf yok).

GOLDEN_TOKENIZE = [
    # (girdi, beklenen çıktı)

    # Temel boşluk bölme
    ("Ali geldi", ["Ali", "geldi"]),
    ("", []),
    ("  ", []),

    # Son noktalama
    ("Ali geldi.", ["Ali", "geldi", "."]),
    ("Nereye gidiyorsun?", ["Nereye", "gidiyorsun", "?"]),
    ("Dur!", ["Dur", "!"]),

    # İç noktalama (virgül)
    ("geldi, gitti", ["geldi", ",", "gitti"]),
    ("bir, iki, üç", ["bir", ",", "iki", ",", "üç"]),

    # Parantez
    ("(eve) gitti", ["(", "eve", ")", "gitti"]),
    ("Ali (öğretmen) geldi", ["Ali", "(", "öğretmen", ")", "geldi"]),

    # Apostrof bölme — apostrof sağ parçada kalır
    ("Ankara'nın", ["Ankara", "'nın"]),
    ("Türkiye'de", ["Türkiye", "'de"]),
    ("İstanbul'dan", ["İstanbul", "'dan"]),

    # Apostrof + cümle noktalama
    ("Ankara'nın sınırı.", ["Ankara", "'nın", "sınırı", "."]),

    # Saf noktalama metin
    ("...", [".", ".", "."]),
    ("!?", ["!", "?"]),

    # Karma cümle
    ("Ali geldi, Ayşe gitti.", ["Ali", "geldi", ",", "Ayşe", "gitti", "."]),

    # İki nokta / noktalı virgül
    ("şöyle:", ["şöyle", ":"]),
    ("birinci; ikinci", ["birinci", ";", "ikinci"]),

    # Tırnak
    ('"merhaba"', ['"', "merhaba", '"']),

    # Apostrof olmayan kelime ortasında özel karakter yok
    ("okul", ["okul"]),
    ("gidiyorum", ["gidiyorum"]),

    # Çoklu boşluk
    ("ali   geldi", ["ali", "geldi"]),

    # Sayı + noktalama
    ("3.", ["3", "."]),
    ("2026'da", ["2026", "'da"]),

    # Kıvrık apostrof (U+2019) bölünmez — tek token olarak kalır (bilinen sınır)
    ("Türkiye’de", ["Türkiye’de"]),
]
```

- [ ] **Step 2: Commit (golden only)**

```bash
git add tests/golden_tokenize.py
git commit -m "test(tokenize): bağımsız golden (motor-körü, 25 giriş)"
```

---

## Task 2: `tokenize.py` Implementasyonu

**Files:**
- Create: `turkgram/tokenize.py`
- Create: `tests/test_tokenize.py`

- [ ] **Step 1: `test_tokenize.py` runner'ı yaz (önce — RED)**

```python
# tests/test_tokenize.py
import pytest
from turkgram import tokenize
from tests.golden_tokenize import GOLDEN_TOKENIZE


@pytest.mark.parametrize("text,expected", GOLDEN_TOKENIZE)
def test_tokenize_golden(text, expected):
    assert tokenize(text) == expected
```

- [ ] **Step 2: Testi çalıştır — FAIL bekleniyor**

```
pytest tests/test_tokenize.py -v
```

Beklenen: `ImportError: cannot import name 'tokenize' from 'turkgram'`

- [ ] **Step 3: `tokenize.py` implementasyonunu yaz**

```python
# turkgram/tokenize.py
import re

# Boşluk+noktalama+apostrof tokenizer.
# Kapsam dışı: büyük harf normalizasyonu (analyze() içinde),
# klitik ayrıştırma (analyze()' delege), birleşik fiil birleştirme.

_PUNCT = set('.,!?:;"()[]{}…—–')


def tokenize(text: str) -> list[str]:
    """Metni tokenlara böler: boşluk + noktalama + apostrof."""
    tokens: list[str] = []
    for word in text.split():
        _split_word(word, tokens)
    return tokens


def _split_word(word: str, out: list[str]) -> None:
    """Tek kelimeyi baş/son noktalama + apostrof kurallarıyla böler."""
    # Baş noktalama karakterlerini soy
    while word and word[0] in _PUNCT:
        out.append(word[0])
        word = word[1:]

    if not word:
        return

    # Son noktalama karakterlerini topla (sonradan eklemek için)
    trailing: list[str] = []
    while word and word[-1] in _PUNCT:
        trailing.append(word[-1])
        word = word[:-1]

    if not word:
        # Tüm kelime noktalama idi
        out.extend(reversed(trailing))
        return

    # Apostrof bölme: ilk apostrofu bul (kelime ortasında)
    apos = word.find("'")
    if apos > 0:  # 0 değil: baş apostrof tokenizer'ın işi değil
        left = word[:apos]
        right = word[apos:]   # apostrof sağ parçada kalır
        out.append(left)
        if right and right != "'":
            out.append(right)
    else:
        out.append(word)

    out.extend(reversed(trailing))
```

- [ ] **Step 4: Testi çalıştır — PASS bekleniyor**

```
pytest tests/test_tokenize.py -v
```

Beklenen: tüm 25 test PASS. Başarısız test varsa golden ile karşılaştır, implementasyonu düzelt.

- [ ] **Step 5: Tam paket regresyon**

```
pytest --tb=short -q
```

Beklenen: mevcut test sayısı + 25 yeni, 0 FAIL.

- [ ] **Step 6: Commit**

```bash
git add turkgram/tokenize.py tests/test_tokenize.py
git commit -m "feat(tokenize): tokenize() — boşluk+noktalama+apostrof bölme (25 test)"
```

---

## Task 3: `__init__.py` Export

**Files:**
- Modify: `turkgram/__init__.py`

- [ ] **Step 1: `__init__.py`'e `tokenize` import'u ekle**

`turkgram/__init__.py`'i aç. En üstteki import bloğuna şunu ekle (mevcut import'ların yanına, alfabetik sıra önemli değil):

```python
from .tokenize import tokenize
```

- [ ] **Step 2: Export kontrolü**

```
python -c "from turkgram import tokenize; print(tokenize('Ali geldi.'))"
```

Beklenen: `['Ali', 'geldi', '.']`

- [ ] **Step 3: Commit**

```bash
git add turkgram/__init__.py
git commit -m "feat(tokenize): __init__.py export"
```

---

## Task 4: `_cached_analyze` + `parse_text`

**Files:**
- Modify: `turkgram/analysis.py`
- Create: `tests/test_parse_text.py`

- [ ] **Step 1: `test_parse_text.py` yaz (önce — RED)**

```python
# tests/test_parse_text.py
from turkgram import tokenize, parse_text, analyze
from turkgram.analysis import Analysis


def test_parse_text_empty():
    assert parse_text("") == []


def test_parse_text_length_matches_tokens():
    text = "Ali geldi."
    result = parse_text(text)
    assert len(result) == len(tokenize(text))


def test_parse_text_punctuation_empty_list():
    result = parse_text("Ali geldi.")
    tokens = tokenize("Ali geldi.")
    # "." token'ı için boş liste
    dot_idx = tokens.index(".")
    assert result[dot_idx] == []


def test_parse_text_returns_list_of_list_of_analysis():
    result = parse_text("geldi")
    assert isinstance(result, list)
    assert isinstance(result[0], list)
    assert all(isinstance(a, Analysis) for a in result[0])


def test_parse_text_apostrophe_strip():
    # "Ankara'nın" → ["Ankara", "'nın"]
    # "'nın" → baştaki ' soyulur → analyze("nın")
    result = parse_text("Ankara'nın")
    tokens = tokenize("Ankara'nın")
    assert len(result) == len(tokens)  # 2 token → 2 liste
    # "'nın" için analiz (boş olabilir ama çökmemeli)
    assert isinstance(result[1], list)


def test_parse_text_cache_hit(monkeypatch):
    """Aynı surface+roots ikinci kez analyze() çağırmamalı."""
    call_count = {"n": 0}
    original_analyze = __import__("turkgram.analysis", fromlist=["analyze"]).analyze

    def counting_analyze(*args, **kwargs):
        call_count["n"] += 1
        return original_analyze(*args, **kwargs)

    import turkgram.analysis as _mod
    monkeypatch.setattr(_mod, "analyze", counting_analyze)

    # Önbelleği sıfırla
    _mod._cached_analyze.cache_clear()

    parse_text("geldi geldi geldi")
    # "geldi" 3 kez geçiyor ama analyze 1 kez çağrılmalı
    assert call_count["n"] == 1


def test_parse_text_roots_none_vs_empty_set():
    """roots=None ve roots=set() farklı cache slotları kullanmalı."""
    import turkgram.analysis as _mod
    _mod._cached_analyze.cache_clear()

    r1 = parse_text("geldi", roots=None)
    r2 = parse_text("geldi", roots=set())
    # Her ikisi de list[Analysis] döner (içerik farklı olabilir)
    assert isinstance(r1, list)
    assert isinstance(r2, list)
    # Cache'de 2 ayrı giriş olmalı
    info = _mod._cached_analyze.cache_info()
    assert info.currsize >= 2


def test_parse_text_all_punctuation():
    result = parse_text("...")
    assert result == [[], [], []]
```

- [ ] **Step 2: Testi çalıştır — FAIL bekleniyor**

```
pytest tests/test_parse_text.py -v
```

Beklenen: `ImportError: cannot import name 'parse_text' from 'turkgram'`

- [ ] **Step 3: `analysis.py`'e `_cached_analyze` + `parse_text` ekle**

`turkgram/analysis.py` dosyasının en üstündeki import bloğunu kontrol et:
- `lru_cache` zaten import edilmişse `from functools import lru_cache` EKLEME, mevcut import'u koru.
- Yoksa ekle: `from functools import lru_cache`
- Her durumda ekle: `from .tokenize import tokenize as _tokenize`

Ardından dosyanın sonuna (tüm mevcut koddan sonra) şunları ekle:

```python
# ---------------------------------------------------------------------------
# parse_text — toplu analiz
# ---------------------------------------------------------------------------

@lru_cache(maxsize=4096)
def _cached_analyze(
    surface: str,
    roots_key: "frozenset[str] | None",
    depth: int,
) -> "tuple[Analysis, ...]":
    """analyze() sonucunu önbellekler. Analysis frozen=True → cache güvenli.

    Not: pos filtresi iletilmez — parse_text genel amaçlı API'dir.
    pos filtresi gerekirse analyze() doğrudan çağrılmalı.
    """
    roots = set(roots_key) if roots_key is not None else None
    return tuple(analyze(surface, roots=roots, max_derivation_depth=depth))


def parse_text(
    text: str,
    roots: "Collection[str] | None" = None,
    *,
    max_derivation_depth: int = 1,
) -> "list[list[Analysis]]":
    """Metni tokenize edip her token için analyze() döndürür.

    Dönüş uzunluğu == len(tokenize(text)) — indeks hizalaması garantili.
    Noktalama tokenları için boş liste döner.
    """
    roots_key: "frozenset[str] | None" = (
        frozenset(roots) if roots is not None else None
    )
    result: list[list[Analysis]] = []
    for token in _tokenize(text):
        # Apostrof-başlı token: tam olarak bir düz apostrof (U+0027) soy
        surface = token[1:] if token and token[0] == "'" else token
        if not surface:
            result.append([])
            continue
        result.append(list(_cached_analyze(surface, roots_key, max_derivation_depth)))
    return result
```

**Dikkat:** `analyze` fonksiyonu aynı dosyada tanımlı, `_cached_analyze` içinden doğrudan çağrılır.

- [ ] **Step 4: Testi çalıştır — PASS bekleniyor**

```
pytest tests/test_parse_text.py -v
```

Beklenen: tüm testler PASS. `test_parse_text_cache_hit` başarısız olursa `_cached_analyze` cache'inin doğru `surface` key'iyle çağrıldığını kontrol et.

- [ ] **Step 5: Tam paket regresyon**

```
pytest --tb=short -q
```

Beklenen: mevcut test sayısı + 8 yeni, 0 FAIL.

- [ ] **Step 6: Commit**

```bash
git add turkgram/analysis.py tests/test_parse_text.py
git commit -m "feat(analysis): _cached_analyze + parse_text (H-08, toplu analiz)"
```

---

## Task 5: `parse_text` Export + H-10 Doğrulama

**Files:**
- Modify: `turkgram/__init__.py`
- Modify: `tests/test_parse_text.py` (H-10 entegrasyon testi ekle)

- [ ] **Step 1: `__init__.py`'e `parse_text` export ekle**

```python
from .analysis import parse_text
```

- [ ] **Step 2: H-10 entegrasyon testi ekle**

`tests/test_parse_text.py` sonuna ekle:

```python
def test_parse_text_rank_in_context_integration():
    """parse_text çıktısı rank_in_context'e doğrudan beslenebilmeli (H-10)."""
    from turkgram import rank_in_context, lexicon

    text = "Ali eve geldi."
    tokens = tokenize(text)
    roots = lexicon.load()
    analyses = parse_text(text, roots=roots)

    # Uzunluk eşleşmeli
    assert len(tokens) == len(analyses)

    # rank_in_context çökmemeli (noktalama slotları [] → guard var)
    result = rank_in_context(tokens, analyses)
    assert len(result) == len(tokens)
    # Noktalama slotu boş kalmalı
    dot_idx = tokens.index(".")
    assert result[dot_idx] == []
```

- [ ] **Step 3: Testi çalıştır**

```
pytest tests/test_parse_text.py::test_parse_text_rank_in_context_integration -v
```

Beklenen: PASS. FAIL olursa `rank_in_context`'in `if not cands: out.append([]); continue` guard'ını (`context.py` satır ~242) kontrol et.

- [ ] **Step 4: Tam paket regresyon**

```
pytest --tb=short -q
```

Beklenen: mevcut sayı + 1, 0 FAIL.

- [ ] **Step 5: Export kontrolü**

```
python -c "from turkgram import parse_text; print(parse_text('Ali geldi.'))"
```

Beklenen: `[[...], [...], []]` (`"."` için boş liste)

- [ ] **Step 6: Commit**

```bash
git add turkgram/__init__.py tests/test_parse_text.py
git commit -m "feat(analysis): parse_text __init__ export + H-10 rank_in_context entegrasyon testi"
```

---

## Task 6: Son Doğrulama

- [ ] **Step 1: Tam paket (slow dahil)**

```
pytest --tb=short -q
pytest -m slow --tb=short -q
```

Her iki komut da 0 FAIL.

- [ ] **Step 2: Windows UTF-8 kontrol**

```
PYTHONUTF8=1 python -c "
from turkgram import tokenize, parse_text
tokens = tokenize('Ankara\'nın sınırı geldi.')
print(tokens)
result = parse_text('geldi')
print(result[0][0].lemma if result[0] else 'boş')
"
```

- [ ] **Step 3: Bellek güncellemesi**

`faz-durumu.md` memory dosyasını güncelle: parse_text tamamlandı, test sayısı eklendi.

- [ ] **Step 4: Final commit (gerekirse)**

```bash
git add turkgram/tokenize.py turkgram/analysis.py turkgram/__init__.py tests/golden_tokenize.py tests/test_tokenize.py tests/test_parse_text.py
git commit -m "chore: parse_text + tokenizer tamamlandı"
```
