# Syllabify Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `turkgram/syllabify.py` modülünü ekle — Türkçe hecelemleme (`syllabify`), vurgu indeksi (`stress`), vurgu işaretli gösterim (`stress_mark`).

**Architecture:** Kural-tabanlı, morfoloji-agnostik, bağımsız modül. O(n) doğrusal hecelemleme algoritması; `_STRESS_EXCEPTIONS` kapalı listesiyle vurgu. `_tr_upper()` yardımcı fonksiyon Türkçe büyük harf dönüşümünü (i→İ, ı→I) sağlar.

**Tech Stack:** Python 3.10+, pytest, mevcut `turkgram` proje altyapısı.

**Spec:** `docs/superpowers/specs/2026-07-16-syllabify-design.md`

---

## Dosya Yapısı

| Dosya | İşlem | Sorumluluk |
|-------|--------|------------|
| `turkgram/syllabify.py` | Oluştur | Çekirdek algoritma + sabitler + public API |
| `tests/golden_syllabify.py` | Oluştur | Motor-körü bağımsız golden (elle-doğrulanmış) |
| `tests/test_syllabify.py` | Oluştur | pytest runner + TR denklik testleri |
| `turkgram/tr.py` | Değiştir | `hecele()`, `vurgu()`, `vurgu_işaretle()` sarmalayıcılar ekle |
| `turkgram/__init__.py` | Değiştir | `syllabify`, `stress`, `stress_mark` export ekle |
| `tools/sweep_syllabify.py` | Oluştur | Korpus tarama aracı (kalıcı, diğer sweep araçları gibi) |

---

## Task 1: Bağımsız Golden Yaz (motor-körü)

**Önemli:** Bu task `turkgram/syllabify.py` oluşturulmadan tamamlanmalı. Golden motoru GÖRMEZ.

**Files:**
- Create: `tests/golden_syllabify.py`

- [ ] **Adım 1: Golden dosyasını oluştur**

```python
# tests/golden_syllabify.py
"""Syllabify + stress bağımsız golden — motor-körü, elle-doğrulanmış.

Bu dosya pytest tarafından toplanmaz (test_ öneki yok).
Türkçe hece kurallarına göre elle doğrulanmıştır:
- Her hecede tam bir ünlü
- V+C+V → V·CV; V+CC+V → VC·CV; V+CCC+V → VCC·CV; VV → V·V
- Vurgu varsayılan: son hece (0-tabanlı, baştan)
- İstisnalar: yer adları, kapalı-küme alıntılar
"""

# (surface, expected_syllables, expected_stress_index)
# stress_index: 0-tabanlı baştan; None = boş string
SYLLABIFY_CASES = [
    # --- Temel CV örüntüleri ---
    ("ara",       ["a", "ra"],           1),   # V+CV → son hece
    ("oku",       ["o", "ku"],           1),
    ("eve",       ["e", "ve"],           1),

    # --- CVC / VC ---
    ("gel",       ["gel"],               0),   # tek hece
    ("al",        ["al"],                0),
    ("ev",        ["ev"],                0),

    # --- VV (bitişik ünlü): ikinci ünlü yeni hece başlatır ---
    ("ait",       ["a", "it"],           1),   # a·it
    ("saat",      ["sa", "at"],          1),   # sa·at
    ("aile",      ["a", "i", "le"],      2),   # a·i·le
    ("şair",      ["şa", "ir"],          1),   # şa·ir

    # --- V+CC+V → VC·CV ---
    ("aldı",      ["al", "dı"],          1),
    ("erken",     ["er", "ken"],         1),
    ("elbise",    ["el", "bi", "se"],    2),

    # --- V+CCC+V → VCC·CV ---
    ("Türkçe",    ["Türk", "çe"],        1),   # son hece
    ("kartlı",    ["kart", "lı"],        1),

    # --- Çok heceli ---
    ("geldi",        ["gel", "di"],               1),
    ("geldiğimiz",   ["gel", "di", "ği", "miz"],  3),
    ("okuyorum",     ["o", "ku", "yo", "rum"],     3),
    ("öğrenci",      ["öğ", "ren", "ci"],          2),
    ("çalışıyor",    ["ça", "lı", "şı", "yor"],   3),
    ("kitap",        ["ki", "tap"],                1),
    ("anlatıyordu",  ["an", "la", "tı", "yor", "du"], 4),

    # --- İstisna: yer adları ---
    ("ankara",      ["an", "ka", "ra"],          0),   # AN·ka·ra
    ("istanbul",    ["is", "tan", "bul"],         1),   # is·TAN·bul
    ("izmir",       ["iz", "mir"],                0),   # İZ·mir
    ("bursa",       ["bur", "sa"],                0),   # BUR·sa
    ("adana",       ["a", "da", "na"],            1),   # a·DA·na
    ("konya",       ["kon", "ya"],                0),   # KON·ya
    ("erzurum",     ["er", "zu", "rum"],          0),   # ER·zu·rum
    ("trabzon",     ["trab", "zon"],              0),   # TRAB·zon
    ("samsun",      ["sam", "sun"],               0),   # SAM·sun
    ("malatya",     ["ma", "lat", "ya"],          1),   # ma·LAT·ya
    ("eskişehir",   ["es", "ki", "şe", "hir"],   0),   # ES·ki·şe·hir
    ("kayseri",     ["kay", "se", "ri"],          0),   # KAY·se·ri
    ("diyarbakır",  ["di", "yar", "ba", "kır"],  0),   # Dİ·yar·ba·kır
    ("gaziantep",   ["ga", "zi", "an", "tep"],   2),   # ga·zi·AN·tep
    ("antalya",     ["an", "tal", "ya"],          1),   # an·TAL·ya
    ("denizli",     ["de", "niz", "li"],          2),   # de·niz·Lİ

    # --- İstisna: alıntı sözcükler ---
    ("stres",     ["stres"],             0),
    ("tren",      ["tren"],              0),
    ("spor",      ["spor"],              0),

    # --- Circumflex ünlü ---
    ("kâtip",     ["kâ", "tip"],         1),   # kâ·tip (â ünlü sayılır)
    ("rûh",       ["rûh"],               0),   # tek hece

    # --- Edge case ---
    ("",          [],                    None),  # boş
    ("a",         ["a"],                 0),     # tek ünlü
    ("krt",       ["krt"],               0),     # ünlüsüz (kısaltma pasif geçiş)
]

# stress_mark beklentileri: (surface, expected_mark)
# Ayraç: U+00B7 (·); vurgulu hece tamamı büyük harf (_tr_upper ile: i→İ, ı→I)
# stress_mark() girdiyi önce _tr_lower ile normalize eder
STRESS_MARK_CASES = [
    ("geldi",      "gel·Dİ"),           # i→İ
    ("aldı",       "al·DI"),            # ı→I
    ("ankara",     "AN·ka·ra"),
    ("istanbul",   "is·TAN·bul"),
    ("izmir",      "İZ·mir"),           # i→İ
    ("bursa",      "BUR·sa"),
    ("adana",      "a·DA·na"),
    ("konya",      "KON·ya"),
    ("okuyorum",   "o·ku·yo·RUM"),
    ("geldiğimiz", "gel·di·ği·MİZ"),   # i→İ
    ("öğrenci",    "öğ·ren·Cİ"),       # i→İ
    ("ait",        "a·İT"),             # VV + i→İ
    ("saat",       "sa·AT"),
    ("kâtip",      "kâ·TİP"),          # circumflex + i→İ
    ("",           ""),
    ("krt",        "KRT"),
    ("a",          "A"),
    ("stres",      "STRES"),
    ("tren",       "TREN"),
]
```

- [ ] **Adım 2: Golden dosyasının pytest tarafından toplanmadığını doğrula**

```bash
PYTHONUTF8=1 pytest tests/golden_syllabify.py -v
```
Beklenen: "no tests ran" (toplama yok, `test_` öneki yok)

- [ ] **Adım 3: Golden'ı commit et**

```bash
git add tests/golden_syllabify.py
git commit -m "test(syllabify): bağımsız golden (motor-körü)"
```

---

## Task 2a: Sabitler ve Yardımcı Fonksiyonlar

**Files:**
- Create: `turkgram/syllabify.py` (yalnız sabitler ve yardımcılar)

- [ ] **Adım 1: Sabitler + `_tr_upper` + `_tr_lower` + `_STRESS_EXCEPTIONS` yaz**

```python
# turkgram/syllabify.py
"""Türkçe hecelemleme ve vurgu."""

__all__ = ["syllabify", "stress", "stress_mark"]

_VOWELS = frozenset("aeıioöuüâîû")

_SYLLABLE_SEP = "·"  # U+00B7 MIDDLE DOT

# str.upper() kullanılmaz: i→I (hatalı). _tr_upper i→İ, ı→I yapar.
_TR_UPPER_MAP = str.maketrans(
    "aeıioöuübcçdfgğhjklmnprsştvyz",
    "AEIİOÖUÜBCÇDFGĞHJKLMNPRSŞTVYZ",
)


def _tr_upper(s: str) -> str:
    return s.translate(_TR_UPPER_MAP)


def _tr_lower(s: str) -> str:
    return s.replace("İ", "i").replace("I", "ı").lower()


# Anahtar: _tr_lower() normalize edilmiş; Değer: 0-tabanlı vurgulu hece (baştan)
# Kaynak: elle küratörlenmiş, üçüncü taraf kaynak yok.
_STRESS_EXCEPTIONS: dict[str, int] = {
    # Yer adları
    "ankara": 0,
    "istanbul": 1,
    "izmir": 0,
    "bursa": 0,
    "adana": 1,
    "konya": 0,
    "erzurum": 0,
    "trabzon": 0,
    "samsun": 0,
    "malatya": 1,
    "eskişehir": 0,
    "kayseri": 0,
    "diyarbakır": 0,
    "gaziantep": 2,
    "mersin": 0,
    "kocaeli": 2,
    "antalya": 1,
    "denizli": 2,
    "sivas": 0,
    "van": 0,
    "muş": 0,
    "batman": 0,
    "rize": 0,
    "artvin": 0,
    # Alıntı sözcükler (kapalı küme — yalnız kesin olanlar)
    "stres": 0,
    "tren": 0,
    "spor": 0,
    "klima": 1,
    "bisiklet": 1,
    "otobüs": 1,
    "trafik": 0,
}
```

- [ ] **Adım 2: Sözdizimi + temel import kontrolü**

```bash
PYTHONUTF8=1 python -c "from turkgram.syllabify import _tr_upper, _tr_lower, _STRESS_EXCEPTIONS; print(_tr_upper('geldi'), _tr_lower('İSTANBUL'), len(_STRESS_EXCEPTIONS))"
```
Beklenen: `GELDİ istanbul 32` (sayı farklı olabilir, 0 hata önemli)

- [ ] **Adım 3: Commit**

```bash
git add turkgram/syllabify.py
git commit -m "feat(syllabify): sabitler + _tr_upper + _STRESS_EXCEPTIONS"
```

---

## Task 2b: Çekirdek Algoritma

**Files:**
- Modify: `turkgram/syllabify.py` (public fonksiyonlar eklenir)

- [ ] **Adım 1: `syllabify()` fonksiyonunu ekle**

```python
def syllabify(word: str) -> list[str]:
    """Sözcüğü hecelerine böl.

    syllabify("geldiğimiz")  # → ["gel", "di", "ği", "miz"]
    syllabify("Türkçe")      # → ["Türk", "çe"]
    syllabify("ait")         # → ["a", "it"]   (VV → V·V)
    syllabify("")            # → []
    syllabify("krt")         # → ["krt"]        (ünlüsüz pasif geçiş)
    """
    if not word:
        return []

    vowel_positions = [i for i, c in enumerate(word) if c in _VOWELS]

    if not vowel_positions:
        return [word]

    syllables: list[str] = []
    start = 0

    for idx, vpos in enumerate(vowel_positions[:-1]):
        next_vpos = vowel_positions[idx + 1]
        consonants_start = vpos + 1
        n_consonants = next_vpos - consonants_start

        if n_consonants == 0:
            # VV: ikinci ünlü yeni hece başlatır
            cut = next_vpos
        elif n_consonants == 1:
            # V·CV: ünsüz sağa
            cut = consonants_start
        elif n_consonants == 2:
            # VC·CV: ortadan
            cut = consonants_start + 1
        else:
            # VCC·CV (ve daha uzun kümeler): maksimal onset — son ünsüz sağa kalır
            cut = consonants_start + (n_consonants - 1)

        syllables.append(word[start:cut])
        start = cut

    syllables.append(word[start:])
    return syllables
```

- [ ] **Adım 2: `stress()` ve `stress_mark()` fonksiyonlarını ekle**

**Kritik:** `stress_mark()` içinde hem `syllabify()` hem `stress()` çağrısı `_tr_lower(word)` üzerinden yapılır — orijinal string üzerinden değil. Bu iki çağrının aynı normalize edilmiş string'i kullanması zorunludur; aksi halde indeks uyuşmazlığı oluşur.

```python
def stress(word: str) -> int | None:
    """Vurgulu heceye 0-tabanlı indeks (baştan). Boş string için None.

    stress("geldi")    # → 1  (son hece)
    stress("ankara")   # → 0  (istisna)
    stress("istanbul") # → 1  (istisna: is·TAN·bul)
    stress("")         # → None
    stress("krt")      # → 0  (ünlüsüz: tek "hece"; anlamlı vurgu yok,
                       #        yalnız indeks tutarlılığı)
    """
    if not word:
        return None
    syllables = syllabify(word)
    if not syllables:
        return None
    key = _tr_lower(word)
    if key in _STRESS_EXCEPTIONS:
        return _STRESS_EXCEPTIONS[key]
    return len(syllables) - 1


def stress_mark(word: str) -> str:
    """Vurgulu heceyi büyük harfle + U+00B7 ayracıyla göster.

    Girdi _tr_lower ile normalize edilir; her iki iç çağrı (syllabify + stress)
    normalize edilmiş string üzerinden yapılır.

    stress_mark("geldi")    # → "gel·Dİ"
    stress_mark("istanbul") # → "is·TAN·bul"
    stress_mark("ankara")   # → "AN·ka·ra"
    stress_mark("")         # → ""
    stress_mark("krt")      # → "KRT"
    """
    if not word:
        return ""
    normalized = _tr_lower(word)          # tek normalize noktası
    syllables = syllabify(normalized)     # normalize üzerinden
    if not syllables:
        return ""
    idx = stress(normalized)              # normalize üzerinden (istisna tablosu aynı key)
    if idx is None:
        return ""
    marked = [
        _tr_upper(s) if i == idx else s
        for i, s in enumerate(syllables)
    ]
    return _SYLLABLE_SEP.join(marked)
```

- [ ] **Adım 3: Hızlı smoke test**

```bash
PYTHONUTF8=1 python -c "
from turkgram.syllabify import syllabify, stress, stress_mark
print(syllabify('geldi'))       # ['gel', 'di']
print(syllabify('ait'))         # ['a', 'it']
print(stress('istanbul'))       # 1
print(stress('ankara'))         # 0
print(stress(''))               # None
print(stress_mark('geldi'))     # gel·Dİ
print(stress_mark('istanbul'))  # is·TAN·bul
print(stress_mark('izmir'))     # İZ·mir
"
```

- [ ] **Adım 4: Commit**

```bash
git add turkgram/syllabify.py
git commit -m "feat(syllabify): syllabify + stress + stress_mark algoritması"
```

---

## Task 3: Test Runner Yaz

**Files:**
- Create: `tests/test_syllabify.py`

- [ ] **Adım 1: Test runner dosyasını oluştur**

```python
# tests/test_syllabify.py
import pytest
from turkgram.syllabify import syllabify, stress, stress_mark
from tests.golden_syllabify import SYLLABIFY_CASES, STRESS_MARK_CASES


@pytest.mark.parametrize("surface,expected_syllables,expected_stress", SYLLABIFY_CASES)
def test_syllabify_and_stress(surface, expected_syllables, expected_stress):
    assert syllabify(surface) == expected_syllables
    assert stress(surface) == expected_stress


@pytest.mark.parametrize("surface,expected_mark", STRESS_MARK_CASES)
def test_stress_mark(surface, expected_mark):
    assert stress_mark(surface) == expected_mark
```

- [ ] **Adım 2: Testleri çalıştır — hepsi geçmeli**

```bash
PYTHONUTF8=1 pytest tests/test_syllabify.py -v
```
Beklenen: Tüm testler PASS. Fail varsa `turkgram/syllabify.py`'i düzelt — golden'ı değiştirme.

- [ ] **Adım 3: Commit**

```bash
git add tests/test_syllabify.py
git commit -m "test(syllabify): pytest runner"
```

---

## Task 4: TR API ve Export

**Files:**
- Modify: `turkgram/tr.py`
- Modify: `turkgram/__init__.py`

- [ ] **Adım 1: `tr.py`'ye import ve sarmalayıcıları ekle**

`turkgram/tr.py` içindeki diğer import satırlarının yanına ekle (relative import, proje standardı):
```python
from .syllabify import syllabify as _syllabify, stress as _stress, stress_mark as _stress_mark
```

Diğer sarmalayıcıların yanına ekle:
```python
def hecele(kelime: str) -> list[str]:
    """syllabify() Türkçe sarmalayıcı."""
    return _syllabify(kelime)


def vurgu(kelime: str) -> int | None:
    """stress() Türkçe sarmalayıcı."""
    return _stress(kelime)


def vurgu_işaretle(kelime: str) -> str:
    """stress_mark() Türkçe sarmalayıcı."""
    return _stress_mark(kelime)
```

- [ ] **Adım 2: `__init__.py`'ye export ekle (relative import)**

Mevcut diğer satırların yanına (`.syllabify` relative import, proje standardı):
```python
from .syllabify import syllabify, stress, stress_mark
```

- [ ] **Adım 3: TR denklik testlerini `test_syllabify.py`'e ekle**

```python
from turkgram.tr import hecele, vurgu, vurgu_işaretle


def test_tr_hecele_denklik():
    assert hecele("geldi") == syllabify("geldi")


def test_tr_vurgu_denklik():
    assert vurgu("ankara") == stress("ankara")


def test_tr_vurgu_isaretle_denklik():
    assert vurgu_işaretle("istanbul") == stress_mark("istanbul")
```

- [ ] **Adım 4: Testleri çalıştır**

```bash
PYTHONUTF8=1 pytest tests/test_syllabify.py -v
```
Beklenen: Tüm testler PASS (önceki + 3 yeni TR testi).

- [ ] **Adım 5: Commit**

```bash
git add turkgram/tr.py turkgram/__init__.py tests/test_syllabify.py
git commit -m "feat(syllabify): TR API hecele/vurgu/vurgu_işaretle + export"
```

---

## Task 5: Tam Paket Regresyon + Korpus Taraması

- [ ] **Adım 1: Tam test paketi çalıştır**

```bash
PYTHONUTF8=1 pytest --tb=short -q
```
Beklenen: Tüm mevcut testler PASS + yeni syllabify testleri. 0 regresyon.

- [ ] **Adım 2: Korpus tarama scriptini oluştur**

```python
# tools/sweep_syllabify.py
"""Syllabify + stress korpus taraması — lexicon.load() tüm lemmalar."""
import sys
sys.stdout.reconfigure(encoding="utf-8")

from turkgram.lexicon import load
from turkgram.syllabify import syllabify, stress, stress_mark, _STRESS_EXCEPTIONS

roots = load()
errors: list[tuple[str, str]] = []

for lemma in roots:
    try:
        s = syllabify(lemma)
        st = stress(lemma)
        sm = stress_mark(lemma)
    except Exception as e:
        errors.append((lemma, str(e)))

# İstisna tablosu sweep
for word in _STRESS_EXCEPTIONS:
    try:
        assert stress(word) is not None, f"stress('{word}') returned None"
    except AssertionError as e:
        errors.append((word, str(e)))
    except Exception as e:
        errors.append((word, str(e)))

print(f"Tarandı: {len(roots)} lemma + {len(_STRESS_EXCEPTIONS)} istisna")
print(f"Hata: {len(errors)}")
for word, err in errors[:20]:
    print(f"  {word!r}: {err}")
```

- [ ] **Adım 3: Taramayı çalıştır**

```bash
PYTHONUTF8=1 python tools/sweep_syllabify.py
```
Beklenen: `Hata: 0`

- [ ] **Adım 4: Commit**

```bash
git add tools/sweep_syllabify.py
git commit -m "test(syllabify): tam paket regresyon + korpus 0 hata"
```

---

## Task 6: Adversarial Hakem Review

Bağımsız Opus ajanına devredilir. Hakem `turkgram/syllabify.py` ve `tests/golden_syllabify.py`'i inceler.

- [ ] **Adım 1: Hakem ajan dispatch et**

Aşağıdaki prompt ile bağımsız bir Opus ajanı çalıştır:

```
Turkgram Python kütüphanesi için syllabify modülünü adversarial review et.
Dosyaları oku: turkgram/syllabify.py, tests/golden_syllabify.py

Türkçe hece kuralları açısından şunları kontrol et:
1. VV (bitişik ünlü) bölme: syllabify("ait") → ["a","it"], syllabify("saat") → ["sa","at"]
2. VCC·CV: syllabify("Türkçe") → ["Türk","çe"] doğru mu?
3. 4+ ünsüz kümesi: n_consonants>=3 formülü ne üretiyor? Mantıklı mı?
4. _tr_upper: "geldi" → "Dİ" (i→İ, str.upper() kullanılmıyor mu?)
5. stress_mark() içinde syllabify() ve stress() çağrıları _tr_lower(word) üzerinden mi yapılıyor?
6. "istanbul" stress index 1 mi (is·TAN·bul)?
7. stress("") → None mı?
8. stress_mark("izmir") → "İZ·mir" (i→İ doğru)?
9. Golden'da VV, circumflex, edge case senaryoları var mı?
10. _STRESS_EXCEPTIONS'da en az 25 giriş var mı?

Bulgular: CRITICAL / HIGH / MEDIUM / LOW. Boş seviye yazma.
Verdict: APPROVED / NEEDS_FIX.
```

- [ ] **Adım 2: CRITICAL/HIGH bulgu varsa düzelt ve testleri yeniden çalıştır**

- [ ] **Adım 3: Final commit**

```bash
git commit -m "feat(syllabify): Faz 9 tamamlandı — hakem onaylı"
```

---

## Kontrol Listesi (Tamamlandı Sayıldığında)

- [ ] `syllabify()`, `stress()`, `stress_mark()` implement edildi
- [ ] `_tr_upper()` Türkçe duyarlı (str.upper() kullanılmıyor: i→İ, ı→I)
- [ ] VV bitişik ünlü doğru bölünüyor (ait → a·it)
- [ ] `_STRESS_EXCEPTIONS` en az 25 giriş, istanbul→1
- [ ] `stress_mark()` içinde tüm çağrılar `_tr_lower(word)` üzerinden
- [ ] Golden: VV + circumflex + istisna (~40 giriş, 16 istisna)
- [ ] TR API: `hecele()`, `vurgu()`, `vurgu_işaretle()` relative import ile `tr.py`'de
- [ ] `__init__.py` relative import (`.syllabify`)
- [ ] Tam paket: 0 regresyon
- [ ] Korpus taraması: `syllabify` + `stress` + `stress_mark` 3'ü de, 0 hata
- [ ] Hakem: APPROVED
