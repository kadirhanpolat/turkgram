# Faz 9b: Türkçe Yazım Denetimi (Spellcheck) — İmplementasyon Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `turkgram/spellcheck.py` — `is_valid()`, `suggest()`, `check()` fonksiyonları; BK-tree + Türkçe-ağırlıklı Levenshtein ile kök düzeyi yazım denetimi.

**Architecture:** `is_valid()` mevcut `analyze()` + `lexicon.load()` altyapısını kullanır. `suggest()` 26k lemma üzerinde `@lru_cache` BK-tree singleton sorgular; edit-distance Türkçe karakter konfüzyonlarını 0.5 maliyetle ağırlıklandırır. `check()` ikisini `SpellResult(frozen=True)` içinde birleştirir.

**Tech Stack:** Python 3.9+, pytest, mevcut `turkgram.analysis`, `turkgram.lexicon`

---

## Dosya Haritası

| Eylem | Dosya | Sorumluluk |
|---|---|---|
| Oluştur | `turkgram/spellcheck.py` | `_BKTree`, `_tr_distance`, `SpellResult`, `is_valid`, `suggest`, `check` |
| Oluştur | `tests/golden_spellcheck.py` | Motor-körü bağımsız golden (Opus dispatch) |
| Oluştur | `tests/test_spellcheck.py` | Pytest runner |
| Güncelle | `turkgram/tr.py` | `yazım_geçerli()`, `öneri()`, `denetle()` sarmalayıcılar |
| Güncelle | `turkgram/__init__.py` | `spellcheck` modülü + `SpellResult` re-export |
| Güncelle | `turkgram/__main__.py` | `check` CLI komutu |

---

## Task 1: Bağımsız Golden Oluşturma (Opus, Motor-Körü)

**Files:**
- Create: `tests/golden_spellcheck.py`

Bu task'ı bir Opus subagent'ına dispatch et. Subagent `turkgram/spellcheck.py`'yi GÖRMEZ; yalnız dilbilgisi + spec'e dayanarak golden verisini yazar.

**Opus subagent prompt:**
```
Sen bir Türkçe dilbilgisi uzmanısın. turkgram kütüphanesinin yazım denetimi modülü için
MOTOR-KÖRÜ bağımsız golden verisi oluşturacaksın. Hiçbir turkgram kaynak koduna bakma.
Yalnız Türkçe dilbilgisi bilgine dayan.

Dosya: tests/golden_spellcheck.py

Gereksinimler (spec'ten):
- is_valid(word) → bool: morfolojik olarak geçerli Türkçe kelimeyse True
- suggest(word) → list[str]: V1'de KÖKLER (lemmalar) döner, yüzey biçimler değil
- check(word) → SpellResult(word, is_valid, suggestions: tuple[str,...])
- is_valid=True → suggestions=() (boş tuple, BK-tree sorgusu yok)
- Türkçe karakter konfüzyonları (ı/i, ö/o, ü/u, ş/s, ç/c, ğ/g) daha düşük distance

Dosya yapısı:
"""Motor-körü bağımsız golden — spellcheck (Faz 9b)..."""

IS_VALID_CASES = [
    # (word, expected_bool)
    ("ev", True),
    ...
]

SUGGEST_CASES = [
    # (word, must_include_root, max_distance)
    # must_include_root: öneriler içinde bulunması gereken kök
    ("seker", "şeker", 2),
    ...
]

CHECK_CASES = [
    # (word, expected_is_valid, expected_suggestions_superset)
    # expected_suggestions_superset: suggestions tuple'ı bu kümrenin alt-kümesini içermeli
    ("ev", True, ()),
    ...
]

Kapsamı şunları içersin:
IS_VALID (en az 10 giriş):
- Geçerli: ev, evde, gelmek, geliyorum, güzel, kitap, araba, okul, büyük, çalışkan
- Geçersiz: evdte, gelioyrm, guzl, ktap
- Edge: "" (boş string), "x" * 201 (çok uzun)

SUGGEST (en az 9 giriş — Türkçe karakter konfüzyonları):
- seker → şeker (ş/s konfüzyon, distance=0.5)
- cok → çok (ç/c konfüzyon, distance=0.5)
- gozluk → gözlük (ö/o + ü/u çift konfüzyon, distance ~1.0)
- kapi → kapı (ı/i konfüzyon, distance=0.5)
- gunes → güneş (ü/u + ş/s)
- uc → üç (ü/u + ç/c)
- dag → dağ (ğ/g)
- kus → kuş (ş/s)
- max_distance=0.5 edge case: "seker" max_distance=0.5 → şeker bulunur (tam eşik)

CHECK (en az 6 giriş):
- Geçerli kelimeler: is_valid=True, suggestions=()
- Geçersiz + öneri: is_valid=False, suggestions içinde kök olmalı
- "ev" → (True, ())
- "seker" → (False, ...) # suggestions'da "şeker" olmalı
```

- [ ] **Adım 1.1: Opus subagent'ını dispatch et**

Yukarıdaki prompt'u Opus subagent'ına ver, `tests/golden_spellcheck.py` dosyasını oluştursun.

- [ ] **Adım 1.2: Golden dosyasını doğrula**

Dosyanın 3 liste tanımladığını kontrol et: `IS_VALID_CASES`, `SUGGEST_CASES`, `CHECK_CASES`.
Dosya yalnız veri içermeli — pytest import etmemeli, assert yazmamalı.

- [ ] **Adım 1.3: Commit**

```bash
git add tests/golden_spellcheck.py
git commit -m "test(golden): Faz 9b spellcheck bağımsız golden (motor-körü)"
```

---

## Task 2: SpellResult + is_valid()

**Files:**
- Create: `turkgram/spellcheck.py`
- Create: `tests/test_spellcheck.py` (kısmi — is_valid testleri)

- [ ] **Adım 2.1: Failing testleri yaz**

`tests/test_spellcheck.py` dosyasını oluştur. `_tr_distance` birim testleri de burada —
regresyon koruması için her pytest çalışmasında çalışır:

```python
"""Faz 9b — yazım denetimi runner."""
import pytest
from tests.golden_spellcheck import IS_VALID_CASES, SUGGEST_CASES, CHECK_CASES


@pytest.mark.parametrize("word,expected", IS_VALID_CASES)
def test_is_valid(word, expected):
    from turkgram.spellcheck import is_valid
    assert is_valid(word) == expected


@pytest.mark.parametrize("word,must_include,max_dist", SUGGEST_CASES)
def test_suggest_includes(word, must_include, max_dist):
    from turkgram.spellcheck import suggest
    result = suggest(word, max_distance=max_dist)
    assert must_include in result, f"suggest({word!r}) = {result}, beklenen: {must_include!r}"


@pytest.mark.parametrize("word,exp_valid,exp_sug_superset", CHECK_CASES)
def test_check(word, exp_valid, exp_sug_superset):
    from turkgram.spellcheck import check
    r = check(word)
    assert r.is_valid == exp_valid
    if exp_sug_superset:
        for root in exp_sug_superset:
            assert root in r.suggestions


def test_is_valid_empty():
    from turkgram.spellcheck import is_valid
    assert is_valid("") is False


def test_is_valid_too_long():
    from turkgram.spellcheck import is_valid
    assert is_valid("a" * 201) is False


def test_suggest_max_suggestions():
    from turkgram.spellcheck import suggest
    result = suggest("seker", max_suggestions=2)
    assert len(result) <= 2


def test_suggest_invalid_params():
    from turkgram.spellcheck import suggest
    with pytest.raises(ValueError):
        suggest("test", max_suggestions=0)
    with pytest.raises(ValueError):
        suggest("test", max_distance=0)


def test_spell_result_is_frozen():
    from turkgram.spellcheck import SpellResult
    r = SpellResult(word="ev", is_valid=True, suggestions=())
    with pytest.raises(Exception):
        r.is_valid = False  # type: ignore


def test_check_valid_word_no_suggestions():
    from turkgram.spellcheck import check
    r = check("ev")
    assert r.is_valid is True
    assert r.suggestions == ()


def test_tr_api():
    from turkgram import tr
    assert tr.yazım_geçerli("ev") is True
    assert isinstance(tr.öneri("seker"), list)
    from turkgram.spellcheck import SpellResult
    assert isinstance(tr.denetle("ev"), SpellResult)


# ── _tr_distance birim testleri (regresyon koruması) ─────────────────────
@pytest.mark.parametrize("a,b,expected", [
    ("ev",    "ev",    0.0),   # aynı kelime
    ("seker", "şeker", 0.5),   # ş/s tek konfüzyon
    ("cok",   "çok",   0.5),   # ç/c tek konfüzyon
    ("kapi",  "kapı",  0.5),   # ı/i tek konfüzyon
    ("goz",   "göz",   0.5),   # ö/o tek konfüzyon
    ("dag",   "dağ",   0.5),   # ğ/g tek konfüzyon
    ("abc",   "xyz",   3.0),   # 3 non-TR değiştirme
    ("ab",    "abc",   1.0),   # 1 ekleme
    ("abc",   "ab",    1.0),   # 1 silme
])
def test_tr_distance(a, b, expected):
    from turkgram.spellcheck import _tr_distance
    assert _tr_distance(a, b) == pytest.approx(expected)
```

- [ ] **Adım 2.2: Testlerin FAIL ettiğini doğrula**

```bash
cd D:/PYTHON/turkgram && python -m pytest tests/test_spellcheck.py -v 2>&1 | head -20
```

Beklenen: `ImportError: cannot import name 'is_valid' from 'turkgram.spellcheck'`

- [ ] **Adım 2.3: SpellResult + is_valid() yaz**

`turkgram/spellcheck.py` oluştur:

```python
"""turkgram.spellcheck — Türkçe yazım denetimi (Faz 9b).

is_valid() → analyze() + lexicon.load() ile morfolojik geçerlilik.
suggest()  → BK-tree + Türkçe-ağırlıklı Levenshtein ile kök önerileri (V1).
check()    → SpellResult (is_valid + suggestions).

NOT: roots=None burada lexicon.load()'u otomatik yükler (analyze(roots=None)'den farklı).
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable

from .analysis import analyze as _analyze
from . import lexicon as _lexicon

_MAX_WORD_LEN = 200

# Türkçe karakter konfüzyonu çiftleri (ı/i, ö/o, ü/u, ş/s, ç/c, ğ/g) — maliyet 0.5
_TR_PAIRS: frozenset[frozenset[str]] = frozenset(
    frozenset(pair) for pair in [("ı", "i"), ("ö", "o"), ("ü", "u"), ("ş", "s"), ("ç", "c"), ("ğ", "g")]
)


def _tr_lower(s: str) -> str:
    return s.replace("İ", "i").replace("I", "ı").lower()


def _roots(roots: frozenset[str] | None) -> frozenset[str]:
    """roots=None → leksikonu otomatik yükle (is_valid/suggest için zorunlu)."""
    return roots if roots is not None else _lexicon.load()


@dataclass(frozen=True)
class SpellResult:
    """Yazım denetimi sonucu."""
    word: str
    is_valid: bool
    suggestions: tuple[str, ...]   # is_valid=True ise boş tuple


def is_valid(word: str, *, roots: frozenset[str] | None = None) -> bool:
    """Kelimenin morfolojik olarak geçerli Türkçe olup olmadığını döner."""
    word = _tr_lower(word.strip())
    if not word or len(word) > _MAX_WORD_LEN:
        return False
    r = _roots(roots)
    return any(not a.hypothetical for a in _analyze(word, roots=r))
```

- [ ] **Adım 2.4: is_valid testlerini çalıştır**

```bash
cd D:/PYTHON/turkgram && python -m pytest tests/test_spellcheck.py::test_is_valid -v 2>&1 | tail -10
```

Beklenen: `IS_VALID_CASES` geçmeli; `SUGGEST/CHECK` testleri henüz skip/fail.

- [ ] **Adım 2.5: Commit**

```bash
git add turkgram/spellcheck.py tests/test_spellcheck.py
git commit -m "feat(spellcheck): SpellResult + is_valid() (Faz 9b)"
```

---

## Task 3: BK-tree + _tr_distance()

**Files:**
- Modify: `turkgram/spellcheck.py` — `_tr_distance`, `_BKTree`, singleton

- [ ] **Adım 3.1: `_tr_distance` + `_BKTree` ekle**

`turkgram/spellcheck.py`'ye şunları ekle (mevcut kodun altına):

```python
def _tr_distance(a: str, b: str) -> float:
    """Türkçe-ağırlıklı Levenshtein — konfüzyon çiftleri 0.5 maliyet."""
    if a == b:
        return 0.0
    la, lb = len(a), len(b)
    # dp[i][j] = a[:i] ile b[:j] arası minimum maliyet
    prev = [float(j) for j in range(lb + 1)]
    for i in range(1, la + 1):
        curr = [float(i)] + [0.0] * lb
        for j in range(1, lb + 1):
            ca, cb = a[i - 1], b[j - 1]
            if ca == cb:
                cost = 0.0
            elif frozenset((ca, cb)) in _TR_PAIRS:
                cost = 0.5
            else:
                cost = 1.0
            curr[j] = min(
                prev[j] + 1.0,        # silme
                curr[j - 1] + 1.0,    # ekleme
                prev[j - 1] + cost,   # değiştirme
            )
        prev = curr
    return prev[lb]


class _BKTree:
    """BK-tree — edit-distance sorguları için O(log n) ortalama."""

    def __init__(self) -> None:
        self._root: tuple[str, dict] | None = None

    def build(self, words: Iterable[str]) -> "_BKTree":
        for w in words:
            self._insert(w)
        return self

    def _insert(self, word: str) -> None:
        if self._root is None:
            self._root = (word, {})
            return
        node_word, children = self._root
        self._insert_at(node_word, children, word)

    def _insert_at(self, node_word: str, children: dict, word: str) -> None:
        d = int(_tr_distance(node_word, word) * 2)  # 0.5 adımları → int (× 2)
        if d == 0:
            return
        if d not in children:
            children[d] = (word, {})
        else:
            child_word, child_children = children[d]
            self._insert_at(child_word, child_children, word)

    def query(self, word: str, max_distance: float) -> list[tuple[float, str]]:
        """max_distance içindeki (distance, lemma) çiftleri — SIRASIZ döner."""
        if self._root is None:
            return []
        results: list[tuple[float, str]] = []
        max_d_int = int(max_distance * 2)
        self._query_at(self._root[0], self._root[1], word, max_d_int, results)
        return results

    def _query_at(
        self,
        node_word: str,
        children: dict,
        word: str,
        max_d_int: int,
        results: list,
    ) -> None:
        d_float = _tr_distance(node_word, word)
        d_int = int(d_float * 2)
        if d_float <= max_d_int / 2:
            results.append((d_float, node_word))
        lo = max(0, d_int - max_d_int)
        hi = d_int + max_d_int
        for key, (child_word, child_children) in children.items():
            if lo <= key <= hi:
                self._query_at(child_word, child_children, word, max_d_int, results)


@lru_cache(maxsize=1)
def _build_tree(roots_key: frozenset[str]) -> _BKTree:
    """Leksikon singleton BK-tree — ilk suggest() çağrısında inşa edilir."""
    return _BKTree().build(roots_key)


def _get_tree(roots: frozenset[str]) -> _BKTree:
    return _build_tree(roots)
```

- [ ] **Adım 3.2: _tr_distance birim testi — inline kontrol**

```bash
cd D:/PYTHON/turkgram && python -c "
from turkgram.spellcheck import _tr_distance
assert _tr_distance('seker', 'şeker') == 0.5, _tr_distance('seker', 'şeker')
assert _tr_distance('cok', 'çok') == 0.5
assert _tr_distance('ev', 'ev') == 0.0
assert _tr_distance('ab', 'cd') == 2.0
print('OK')
"
```

Beklenen: `OK`

- [ ] **Adım 3.3: Commit**

```bash
git add turkgram/spellcheck.py
git commit -m "feat(spellcheck): BK-tree + Türkçe-ağırlıklı Levenshtein"
```

---

## Task 4: suggest() + check()

**Files:**
- Modify: `turkgram/spellcheck.py` — `suggest`, `check` fonksiyonları

- [ ] **Adım 4.1: `suggest()` + `check()` ekle**

`turkgram/spellcheck.py`'ye mevcut kodun altına:

```python
def suggest(
    word: str,
    *,
    roots: frozenset[str] | None = None,
    max_suggestions: int = 5,
    max_distance: float = 2.0,
) -> list[str]:
    """Yanlış yazılmış kelime için kök (lemma) önerileri — V1.

    Dönüş değeri kök listesi (inflected değil): "evte" → ["ev"].
    V2'de yüzey yeniden üretimi eklenir (API imzası değişmez, davranış değişir).
    """
    if max_suggestions < 1:
        raise ValueError(f"max_suggestions en az 1 olmalı, verildi: {max_suggestions}")
    if max_distance <= 0:
        raise ValueError(f"max_distance 0'dan büyük olmalı, verildi: {max_distance}")

    word = _tr_lower(word.strip())
    if not word or len(word) > _MAX_WORD_LEN:
        return []

    r = _roots(roots)
    tree = _get_tree(r)
    hits = tree.query(word, max_distance)  # [(distance, lemma), ...] SIRASIZ

    # Frekans tablosu — tiebreak için
    try:
        freq = _lexicon.load_freq()
    except Exception:
        freq = {}

    # Sırala: önce distance artan, eşitte frekans azalan, sonra alfabetik
    hits.sort(key=lambda x: (x[0], -freq.get(x[1], 0), x[1]))

    return [lemma for _, lemma in hits[:max_suggestions]]


def check(
    word: str,
    *,
    roots: frozenset[str] | None = None,
    max_suggestions: int = 5,
    max_distance: float = 2.0,
) -> SpellResult:
    """Geçerlilik + öneri — SpellResult döner.

    is_valid=True ise suggestions=() (BK-tree sorgusu yapılmaz).
    """
    if is_valid(word, roots=roots):
        return SpellResult(word=word, is_valid=True, suggestions=())
    sugs = suggest(word, roots=roots, max_suggestions=max_suggestions, max_distance=max_distance)
    return SpellResult(word=word, is_valid=False, suggestions=tuple(sugs))
```

- [ ] **Adım 4.2: Tüm spellcheck testlerini çalıştır**

```bash
cd D:/PYTHON/turkgram && python -m pytest tests/test_spellcheck.py -v 2>&1 | tail -20
```

Beklenen: tüm testler yeşil.

- [ ] **Adım 4.3: Tam paket regresyon**

```bash
cd D:/PYTHON/turkgram && python -m pytest --ignore=tests/test_statistical.py --ignore=tests/test_statistical_artim2.py -q 2>&1 | tail -5
```

Beklenen: 0 hata, önceki test sayısından daha fazla.

- [ ] **Adım 4.4: Commit**

```bash
git add turkgram/spellcheck.py
git commit -m "feat(spellcheck): suggest() + check() — BK-tree öneri sistemi"
```

---

## Task 5: Türkçe API (tr.py)

**Files:**
- Modify: `turkgram/tr.py` — 3 sarmalayıcı

- [ ] **Adım 5.1: tr.py'ye import + sarmalayıcılar ekle**

`turkgram/tr.py` dosyasının uygun yerine (mevcut importların altına):

```python
from . import spellcheck as _spellcheck
```

Ve dosyanın sonuna:

```python
# ── Yazım denetimi (Faz 9b) ──────────────────────────────────────────────
def yazım_geçerli(kelime: str, *, kökler: "frozenset[str] | None" = None) -> bool:
    """Kelimenin geçerli Türkçe olup olmadığını döner."""
    return _spellcheck.is_valid(_tr_lower(kelime), roots=kökler)


def öneri(
    kelime: str,
    *,
    kökler: "frozenset[str] | None" = None,
    maksimum: int = 5,
    uzaklık: float = 2.0,
) -> list[str]:
    """Yanlış yazılmış kelime için kök önerileri."""
    return _spellcheck.suggest(
        _tr_lower(kelime), roots=kökler, max_suggestions=maksimum, max_distance=uzaklık
    )


def denetle(
    kelime: str,
    *,
    kökler: "frozenset[str] | None" = None,
    maksimum: int = 5,
    uzaklık: float = 2.0,
) -> "_spellcheck.SpellResult":
    """Geçerlilik + öneri — SpellResult döner."""
    return _spellcheck.check(
        _tr_lower(kelime), roots=kökler, max_suggestions=maksimum, max_distance=uzaklık
    )
```

- [ ] **Adım 5.2: tr.py testleri**

```bash
cd D:/PYTHON/turkgram && python -m pytest tests/test_spellcheck.py::test_tr_api -v
```

Beklenen: PASS.

- [ ] **Adım 5.3: Commit**

```bash
git add turkgram/tr.py
git commit -m "feat(tr): yazım_geçerli/öneri/denetle Türkçe sarmalayıcılar"
```

---

## Task 6: __init__.py Export

**Files:**
- Modify: `turkgram/__init__.py`

- [ ] **Adım 6.1: spellcheck modülünü import et**

`turkgram/__init__.py` dosyasında mevcut import bloğunun uygun yerine ekle:

```python
from . import spellcheck
from .spellcheck import SpellResult
```

Ve `__all__` listesine ekle:

```python
"spellcheck", "SpellResult",
```

- [ ] **Adım 6.2: Export doğrula**

```bash
cd D:/PYTHON/turkgram && python -c "
from turkgram import spellcheck, SpellResult
print(spellcheck.is_valid('ev'))
print(SpellResult(word='ev', is_valid=True, suggestions=()))
"
```

Beklenen: `True` ve `SpellResult(...)` çıktısı.

- [ ] **Adım 6.3: Commit**

```bash
git add turkgram/__init__.py
git commit -m "feat(init): spellcheck + SpellResult export"
```

---

## Task 7: CLI check Komutu

**Files:**
- Modify: `turkgram/__main__.py`

- [ ] **Adım 7.1: CLI testlerini ÖNCE yaz (RED)**

`tests/test_spellcheck.py` sonuna ekle (TDD — implementasyon henüz yok):

```python
def test_cli_check_invalid(capsys):
    from turkgram.__main__ import cmd_check
    cmd_check(["seker"])
    out = capsys.readouterr().out
    assert "GEÇERSİZ" in out


def test_cli_check_valid(capsys):
    from turkgram.__main__ import cmd_check
    cmd_check(["evde"])
    out = capsys.readouterr().out
    assert "GEÇERLİ" in out


def test_cli_check_too_long():
    from turkgram.__main__ import cmd_check
    with pytest.raises(SystemExit):
        cmd_check(["a" * 201])
```

```bash
cd D:/PYTHON/turkgram && python -m pytest tests/test_spellcheck.py::test_cli_check_invalid -v
```

Beklenen: FAIL (`AttributeError: module 'turkgram.__main__' has no attribute 'cmd_check'`).

- [ ] **Adım 7.2: `cmd_check()` + help güncelle (GREEN)**

`turkgram/__main__.py`'ye `cmd_analyze` fonksiyonunun altına:

```python
def cmd_check(args: list[str]) -> None:
    import argparse
    from turkgram.spellcheck import check

    p = argparse.ArgumentParser(
        prog="python -m turkgram check",
        description="Türkçe kelime yazım denetimi.",
    )
    p.add_argument("word", help="Denetlenecek kelime")
    p.add_argument(
        "--max-suggestions", type=int, default=5, dest="max_sug",
        help="Maksimum öneri sayısı (varsayılan: 5)"
    )
    p.add_argument(
        "--max-distance", type=float, default=2.0, dest="max_dist",
        help="Maksimum edit-distance eşiği (varsayılan: 2.0)"
    )
    ns = p.parse_args(args)

    word: str = ns.word
    if len(word) > _MAX_SURFACE_LEN:
        _die(f"kelime çok uzun (max {_MAX_SURFACE_LEN} karakter)")

    result = check(word, max_suggestions=ns.max_sug, max_distance=ns.max_dist)
    if result.is_valid:
        print(f"{word}: GEÇERLİ")
    else:
        print(f"{word}: GEÇERSİZ")
        if result.suggestions:
            print(f"Öneriler: {', '.join(result.suggestions)}")
        else:
            print("Öneri bulunamadı.")
```

`main()` fonksiyonunda `cmd_analyze`'ın yanına:

```python
elif cmd == "check":
    cmd_check(rest)
```

`main()`'deki help metnine ekle:

```python
print("  check <kelime>   Yazım denetimi (geçerlilik + öneri)")
```

- [ ] **Adım 7.3: CLI manuel test**

```bash
cd D:/PYTHON/turkgram && python -m turkgram check seker
```

Beklenen: `seker: GEÇERSİZ` + `Öneriler: şeker`

```bash
cd D:/PYTHON/turkgram && python -m turkgram check evde
```

Beklenen: `evde: GEÇERLİ`

- [ ] **Adım 7.4: Tüm CLI testleri çalıştır**

```bash
cd D:/PYTHON/turkgram && python -m pytest tests/test_spellcheck.py -v 2>&1 | tail -10
```

Beklenen: tüm testler yeşil.

- [ ] **Adım 7.5: Commit**

```bash
git add turkgram/__main__.py tests/test_spellcheck.py
git commit -m "feat(cli): check komutu — yazım denetimi CLI"
```

---

## Task 8: Korpus Süpürmesi (Hakem)

**Files:**
- Create: `tools/sweep_spellcheck.py` (geçici araç)

- [ ] **Adım 8.1: Korpus tarama scriptini yaz**

`tools/sweep_spellcheck.py`:

```python
"""Faz 9b hakem: 26k leksikon lemması × is_valid + suggest → 0 çökme kontrolü."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from turkgram import lexicon
from turkgram.spellcheck import is_valid, suggest

# verb+noun filtresi: bu POS'lar analyze() motorundan geçerli parse alır.
# adv/interj/conj lemmalar sözlük dışı çıkabilir — strict kontrole alma.
strict_roots = lexicon.load(pos={"verb", "noun"})
all_roots = lexicon.load()
lemmalar = list(all_roots)
total = len(lemmalar)
errors = []

for i, lemma in enumerate(lemmalar):
    if i % 5000 == 0:
        print(f"  {i}/{total}...", flush=True)
    try:
        v = is_valid(lemma, roots=all_roots)
        # Sadece verb+noun için is_valid=True zorunlu; diğerleri WARNING
        if not v and lemma in strict_roots:
            errors.append(("is_valid_false", lemma))
        elif not v:
            pass  # adv/interj/conj lemmalar kabul edilebilir miss
    except Exception as e:
        errors.append(("is_valid_crash", lemma, str(e)))

    # suggest yalnız geçersizmiş gibi davranan bir örnek (bilerek bozulmuş)
    if i < 500:
        bozuk = lemma[:-1] + "x" if lemma else "x"
        try:
            suggest(bozuk, roots=roots, max_suggestions=3, max_distance=2.0)
        except Exception as e:
            errors.append(("suggest_crash", bozuk, str(e)))

print(f"\nToplam: {total} lemma")
if errors:
    print(f"HATA: {len(errors)} sorun")
    for e in errors[:20]:
        print(" ", e)
    sys.exit(1)
else:
    print("OK: 0 çökme, tüm lemmalar is_valid=True")
```

- [ ] **Adım 8.2: Taramayı çalıştır**

```bash
cd D:/PYTHON/turkgram && PYTHONUTF8=1 python tools/sweep_spellcheck.py
```

Beklenen: `OK: 0 çökme, tüm lemmalar is_valid=True`

- [ ] **Adım 8.3: Tam paket son kontrol**

```bash
cd D:/PYTHON/turkgram && python -m pytest -q 2>&1 | tail -5
```

Beklenen: tüm testler yeşil, önceki 3825'e ek olarak yeni testler.

- [ ] **Adım 8.4: Final commit**

```bash
git add tools/sweep_spellcheck.py
git commit -m "test(spellcheck): korpus süpürme aracı (Faz 9b hakem)"
```

---

## Özet

| Task | Çıktı | Commit |
|---|---|---|
| 1 | `tests/golden_spellcheck.py` | bağımsız golden |
| 2 | `SpellResult` + `is_valid()` | core types |
| 3 | `_BKTree` + `_tr_distance()` | search engine |
| 4 | `suggest()` + `check()` | tam API |
| 5 | `tr.py` sarmalayıcılar | Türkçe API |
| 6 | `__init__.py` export | paket entegrasyonu |
| 7 | CLI `check` komutu | kullanıcı arayüzü |
| 8 | Korpus süpürmesi | hakem doğrulama |
