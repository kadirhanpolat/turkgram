# Faz 9d: İkileme (Reduplication) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Türkçe üç ikileme türü için üretim + analiz: tam ikileme (`yavaş yavaş`), -A ulaç ikilemesi (`koşa koşa`), m-ikileme (`kitap mitap`).

**Architecture:** Tek yeni modül `turkgram/reduplication.py` (conjunction.py emsali). Analiz `_analyze_multi_token` içine eklenir — `_KINDS` zincirine eklenmez. Converb analizi `roots` zorunlu; tam ve m-ikileme `roots` opsiyonel.

**Tech Stack:** Python 3.10+, pytest, mevcut `nonfinite.converb`, `morphology.ends_in_vowel`.

**Spec:** `docs/superpowers/specs/2026-07-17-reduplication-design.md`

---

## File Map

| Dosya | Eylem | Sorumluluk |
|-------|-------|------------|
| `turkgram/reduplication.py` | Yeni | `full_reduplicate`, `converb_reduplicate`, `m_reduplicate` |
| `turkgram/__init__.py` | Değiştir | export ekle |
| `turkgram/tr.py` | Değiştir | `tam_ikile`, `ulaç_ikile`, `m_ikile` sarmalayıcılar |
| `turkgram/analysis.py` | Değiştir | `_try_reduplication_all` + `_analyze_multi_token` genişletme |
| `tests/golden_reduplication.py` | Yeni | üretim golden (~55 giriş, motor-körü) |
| `tests/test_reduplication.py` | Yeni | üretim runner (~70 test) |
| `tests/golden_reduplication_analysis.py` | Yeni | analiz golden (~30 giriş, motor-körü) |
| `tests/test_reduplication_analysis.py` | Yeni | analiz runner (~35 test) |
| `tools/sweep_reduplication.py` | Yeni | korpus tarama (0 çökme hedefi) |

---

## Task 1: `turkgram/reduplication.py` — Üretim Modülü

**Files:**
- Create: `turkgram/reduplication.py`

- [ ] **Step 1: Dosyayı oluştur**

```python
"""reduplication.py — Türkçe ikileme üretimi (Faz 9d).

Üç tür:
  full_reduplicate  : yavaş → yavaş yavaş
  converb_reduplicate: koşmak → koşa koşa   (-A ulacı × 2)
  m_reduplicate     : kitap → kitap mitap   (ilk C→m)
"""
from __future__ import annotations

from .morphology import ends_in_vowel
from .nonfinite import converb as _converb

__all__ = ["full_reduplicate", "converb_reduplicate", "m_reduplicate"]

_VOWELS: frozenset[str] = frozenset("aeıioöuüâîû")


def full_reduplicate(word: str) -> str:
    """Sözcüğü kendisiyle tekrarla: yavaş → yavaş yavaş."""
    if not word:
        raise ValueError("Boş sözcük")
    return word + " " + word


def converb_reduplicate(lemma: str) -> str:
    """-A ulaç biçimini ikile: koşmak → koşa koşa.

    Parameters
    ----------
    lemma:
        Fiil mastarı (-mAk biçimi). Mastar olmayan girdi ValueError fırlatır.
    """
    if not lemma:
        raise ValueError("Boş sözcük")
    form = _converb(lemma, "optative")   # → -A ulaç biçimi
    return form + " " + form


def m_reduplicate(word: str) -> str:
    """İlk ünsüzü m ile değiştir: kitap → kitap mitap.

    Ünlü-başlı sözcüklerde başa m eklenir: araba → araba maraba.
    m-başlı sözcükler için ValueError fırlatılır (p-ikileme kapsam dışı).
    """
    if not word:
        raise ValueError("Boş sözcük")
    if word[0] == "m":
        raise ValueError(
            f"m-başlı sözcüğe m-ikileme uygulanamaz: {word!r}"
        )
    if word[0] in _VOWELS:
        m_form = "m" + word
    else:
        m_form = "m" + word[1:]
    return word + " " + m_form
```

- [ ] **Step 2: Smoke test (PYTHONUTF8=1 zorunlu)**

```bash
PYTHONUTF8=1 python -c "
from turkgram.reduplication import full_reduplicate, converb_reduplicate, m_reduplicate
print(full_reduplicate('yavaş'))
print(converb_reduplicate('koşmak'))
print(m_reduplicate('kitap'))
print(m_reduplicate('araba'))
"
```

Beklenen:
```
yavaş yavaş
koşa koşa
kitap mitap
araba maraba
```

- [ ] **Step 3: Commit**

```bash
git add turkgram/reduplication.py
git commit -m "feat(reduplication): full/converb/m_reduplicate üretim fonksiyonları (Faz 9d)"
```

---

## Task 2: Bağımsız Golden — Üretim (motor-körü Opus subagent)

**Files:**
- Create: `tests/golden_reduplication.py`

- [ ] **Step 1: Opus subagent'e dispatch et — MOTORU GÖRME**

Subagent talimatı (motor-körü):

> Sen bir Türkçe dilbilgisi uzmanısın. `tests/golden_reduplication.py` dosyasını oluştur. turkgram kodu veya mevcut test dosyalarına BAKMA — yalnız aşağıdaki kurallardan ve kendi dilbilgisi bilginden üret.
>
> **Kurallar:**
> - `full_reduplicate(word)` → `word + " " + word` (her POS)
> - `converb_reduplicate(lemma)` → `-A` ulaç biçimi × 2 (`koşmak→koşa`, `gitmek→gide`, `ağlamak→ağlaya`, `yemek→yiye`, `okumak→okuya`, `gülmek→güle`)
> - `m_reduplicate(word)` → ünsüz-başlı: `m+word[1:]`; ünlü-başlı: `m+word`; m-başlı: ValueError
>
> **Format:**
> ```python
> GOLDEN_FULL = [
>     ("yavaş", "yavaş yavaş"),
>     ...  # 15 giriş: sıfat/zarf/isim/zamir/fiil karışık
> ]
>
> GOLDEN_CONVERB = [
>     ("koşmak", "koşa koşa"),
>     ...  # 20 giriş: ye_de yumuşama + glide + düzensiz fiiller dahil
> ]
>
> GOLDEN_M = [
>     ("kitap", "kitap mitap"),
>     ...  # 20 giriş: ünsüz-başlı + ünlü-başlı + ValueError örnekleri
> ]
>
> GOLDEN_M_ERROR = [
>     "masa",   # m-başlı → ValueError
>     ...  # 3-4 giriş
> ]
> ```
>
> Önemli: `converb` için yalnız `-A` ulaç (optative) biçimi — `-ArAk` değil.

- [ ] **Step 2: Golden dosyayı kaydet ve gözden geçir**

`tests/golden_reduplication.py` dosyasını oluştur. Her girdiyi elle doğrula:
- `ağlamak → ağlaya ağlaya` (glide y: ağla+y+a)
- `gitmek → gide gide` (ye_de: git→gid)
- `okumak → okuya okuya` (ünlü-final: oku+y+a)
- `araba → araba maraba` (ünlü-başlı m-ikileme)

- [ ] **Step 3: Commit**

```bash
git add tests/golden_reduplication.py
git commit -m "test(reduplication): bağımsız üretim golden (motor-körü, Faz 9d)"
```

---

## Task 3: `tests/test_reduplication.py` — Üretim Runner

**Files:**
- Create: `tests/test_reduplication.py`

- [ ] **Step 1: Runner dosyasını oluştur**

```python
"""test_reduplication.py — Faz 9d ikileme üretim runner."""
import pytest
from tests.golden_reduplication import GOLDEN_FULL, GOLDEN_CONVERB, GOLDEN_M, GOLDEN_M_ERROR
from turkgram.reduplication import full_reduplicate, converb_reduplicate, m_reduplicate
from turkgram import tr


@pytest.mark.parametrize("word,expected", GOLDEN_FULL)
def test_full_reduplicate(word, expected):
    assert full_reduplicate(word) == expected


@pytest.mark.parametrize("lemma,expected", GOLDEN_CONVERB)
def test_converb_reduplicate(lemma, expected):
    assert converb_reduplicate(lemma) == expected


@pytest.mark.parametrize("word,expected", GOLDEN_M)
def test_m_reduplicate(word, expected):
    assert m_reduplicate(word) == expected


@pytest.mark.parametrize("word", GOLDEN_M_ERROR)
def test_m_reduplicate_m_initial_raises(word):
    with pytest.raises(ValueError, match="m-başlı"):
        m_reduplicate(word)


def test_full_reduplicate_empty_raises():
    with pytest.raises(ValueError):
        full_reduplicate("")


def test_converb_reduplicate_empty_raises():
    with pytest.raises(ValueError):
        converb_reduplicate("")


def test_m_reduplicate_empty_raises():
    with pytest.raises(ValueError):
        m_reduplicate("")


# TR API denklik testleri
@pytest.mark.parametrize("word,expected", GOLDEN_FULL[:3])
def test_tr_tam_ikile_equiv(word, expected):
    assert tr.tam_ikile(word) == full_reduplicate(word)


@pytest.mark.parametrize("lemma,expected", GOLDEN_CONVERB[:3])
def test_tr_ulac_ikile_equiv(lemma, expected):
    assert tr.ulaç_ikile(lemma) == converb_reduplicate(lemma)


@pytest.mark.parametrize("word,expected", GOLDEN_M[:3])
def test_tr_m_ikile_equiv(word, expected):
    assert tr.m_ikile(word) == m_reduplicate(word)
```

- [ ] **Step 2: Testlerin FAIL ettiğini doğrula (TR API henüz yok)**

```bash
PYTHONUTF8=1 python -m pytest tests/test_reduplication.py -v 2>&1 | head -20
```

- [ ] **Step 3: Commit**

```bash
git add tests/test_reduplication.py
git commit -m "test(reduplication): üretim runner (Faz 9d)"
```

---

## Task 4: TR API — `turkgram/tr.py`

**Files:**
- Modify: `turkgram/tr.py` (sona ekle)

- [ ] **Step 1: tr.py'ye sarmalayıcıları ekle**

Dosyanın sonuna ekle (diğer sarmalayıcıların hemen ardından, `# ── İkileme` başlığıyla):

```python
# ── İkileme (Faz 9d) ──────────────────────────────────────────────────────────
from . import reduplication as _redup


def tam_ikile(kelime: str) -> str:
    """Sözcüğü kendisiyle tekrarla: yavaş → yavaş yavaş."""
    return _redup.full_reduplicate(_tr_lower(kelime))


def ulaç_ikile(mastar: str) -> str:
    """-A ulaç biçimini ikile: koşmak → koşa koşa."""
    return _redup.converb_reduplicate(_tr_lower(mastar))


def m_ikile(kelime: str) -> str:
    """M-ikileme: kitap → kitap mitap."""
    return _redup.m_reduplicate(_tr_lower(kelime))
```

- [ ] **Step 2: Testlerin geçtiğini doğrula**

```bash
PYTHONUTF8=1 python -m pytest tests/test_reduplication.py -v
```

Beklenen: tüm testler PASS.

- [ ] **Step 3: Commit**

```bash
git add turkgram/tr.py
git commit -m "feat(tr): tam_ikile/ulaç_ikile/m_ikile TR API sarmalayıcıları (Faz 9d)"
```

---

## Task 5: `turkgram/__init__.py` — Export

**Files:**
- Modify: `turkgram/__init__.py`

- [ ] **Step 1: Export ekle**

`from .conjunction import ...` satırının altına:

```python
from .reduplication import full_reduplicate, converb_reduplicate, m_reduplicate
```

- [ ] **Step 2: Import smoke test**

```bash
PYTHONUTF8=1 python -c "from turkgram import full_reduplicate, converb_reduplicate, m_reduplicate; print('OK')"
```

- [ ] **Step 3: Commit**

```bash
git add turkgram/__init__.py
git commit -m "feat(__init__): reduplication export eklendi (Faz 9d)"
```

---

## Task 6: Bağımsız Golden — Analiz (motor-körü Opus subagent)

**Files:**
- Create: `tests/golden_reduplication_analysis.py`

- [ ] **Step 1: Opus subagent'e dispatch et — MOTORU GÖRME**

Subagent talimatı (motor-körü):

> Sen bir Türkçe dilbilgisi uzmanısın. `tests/golden_reduplication_analysis.py` dosyasını oluştur. turkgram kodu veya mevcut test dosyalarına BAKMA.
>
> **`analyze(surface)` için beklenen kind değerleri:**
> - `"reduplication_full"`: tam ikileme (`yavaş yavaş`)
> - `"reduplication_converb"`: -A ulaç ikilemesi (`koşa koşa`) — yalnız roots sağlandığında
> - `"reduplication_m"`: m-ikileme (`kitap mitap`)
>
> **Format:**
> ```python
> # (surface, roots_needed, expected_lemma, expected_kind)
> # roots_needed=True → analyze(surface, roots=lexicon.load()) ile test et
> GOLDEN_ANALYSIS = [
>     # Tam ikileme (roots gerekmez)
>     ("yavaş yavaş", False, "yavaş", "reduplication_full"),
>     ("güzel güzel", False, "güzel", "reduplication_full"),
>     ...  # 10 giriş
>
>     # Converb ikilemesi (roots gerekir)
>     ("koşa koşa", True, "koşmak", "reduplication_converb"),
>     ("güle güle", True, "gülmek", "reduplication_converb"),
>     ...  # 10 giriş
>
>     # M-ikileme (roots gerekmez)
>     ("kitap mitap", False, "kitap", "reduplication_m"),
>     ("para mara", False, "para", "reduplication_m"),
>     ...  # 10 giriş
> ]
>
> # Belirsizlik: güle güle → hem converb hem full (roots'ta güle varsa)
> GOLDEN_AMBIGUOUS = [
>     # (surface, expected_kinds_subset)
>     ("güle güle", {"reduplication_converb", "reduplication_full"}),
> ]
>
> # roots=None → converb döndürülmez
> GOLDEN_CONVERB_REQUIRES_ROOTS = [
>     "koşa koşa",
>     "gide gide",
> ]
> ```
>
> Önemli kurallar:
> - Tam ikileme: her iki token aynı (`X X`)
> - Converb: -A ulaç biçiminin ikilemesi (koşa, gide, güle, ağlaya, yiye, okuya...)
> - M-ikileme: `token2[0]=='m'` ve `token2[1:]==token1[1:]` (ünsüz) veya `token2=='m'+token1` (ünlü)
> - `güle güle` bilinçli belirsizlik: hem gülmek converb hem güle full (güle sözcük olarak roots'ta varsa)

- [ ] **Step 2: Kaydet ve gözden geçir**

- [ ] **Step 3: Commit**

```bash
git add tests/golden_reduplication_analysis.py
git commit -m "test(reduplication): bağımsız analiz golden (motor-körü, Faz 9d)"
```

---

## Task 7: `turkgram/analysis.py` — Analiz Entegrasyonu

**Files:**
- Modify: `turkgram/analysis.py`

Bu task'ın üç adımı var: (a) `_KINDS` güncelle, (b) `_try_reduplication_all` fonksiyonu yaz (`-> None`, analyses'e append), (c) `_analyze_multi_token`'a entegre et.

**UYARI (H1):** `_try_reduplication_all` dönüş tipi `-> None` — sonuçlar `analyses.append(...)` ile eklenir, return değeri YOK. `_try_conjunction_all` ve `_try_derivation_all` ile aynı pattern.

**UYARI (H3):** `_KINDS` tuple'ına `"reduplication_full"`, `"reduplication_converb"`, `"reduplication_m"` eklenmeli — `_analyze_multi_token` bu chain'i kullanmasa da downstream disambiguation/validation `_KINDS`'tan okur.

**UYARI (M2):** `pos` değerleri: tam=`_cached_analyze`→pos; converb=`"verb"`; m=`_cached_analyze`→pos.

- [ ] **Step 1: `_KINDS` tuple'ına üç yeni kind ekle (H3)**

`_KINDS` tanımını bul (analysis.py'de `_KINDS = (...)` satırı). Sona ekle:
```python
"reduplication_full", "reduplication_converb", "reduplication_m",
```

- [ ] **Step 2: Import ve `_try_reduplication_all` ekle**

`analysis.py`'nin import bölümüne:

```python
from .reduplication import full_reduplicate, converb_reduplicate, m_reduplicate
```

Ardından `_try_conjunction_all` fonksiyonunun HEMEN ardından yeni fonksiyonu ekle:

```python
def _try_reduplication_all(
    surface: str,
    token1: str,
    token2: str,
    analyses: list[Analysis],
    seen: set[tuple],
    roots: "Collection[str] | None",
) -> None:
    """İkileme analizleri — _analyze_multi_token içinden çağrılır.

    Üç dal bağımsız çalışır (birbirini engellemez).
    Spec: docs/superpowers/specs/2026-07-17-reduplication-design.md §4
    """
    # Dal 1: Tam ikileme (token1 == token2)
    if token1 == token2:
        try:
            if full_reduplicate(token1) == surface:
                if roots is None or token1 in roots:
                    hyp = roots is None
                    # POS: token1'i analiz et (roots=None, döngü yok)
                    inner = _cached_analyze(token1, roots=None)
                    pos = inner[0].pos if inner else "noun"
                    segs = (
                        Segment(token1, "kök", (0, len(token1))),
                        Segment(token1, "ikileme", (len(token1) + 1, len(surface))),
                    )
                    key = ("reduplication_full", token1)
                    if key not in seen:
                        seen.add(key)
                        analyses.append(Analysis(
                            lemma=token1, pos=pos,
                            kind="reduplication_full", kwargs={},
                            segments=tuple(segs), hypothetical=hyp,
                        ))
        except (ValueError, Exception):
            pass

    # Dal 2: Converb ikilemesi (token1 == token2, roots zorunlu)
    if token1 == token2 and roots is not None:
        for lemma in roots:
            try:
                if converb_reduplicate(lemma) == surface:
                    conv_form = surface.split()[0]
                    segs = (
                        Segment(conv_form, "kök", (0, len(conv_form))),
                        Segment(conv_form, "ikileme", (len(conv_form) + 1, len(surface))),
                    )
                    key = ("reduplication_converb", lemma)
                    if key not in seen:
                        seen.add(key)
                        analyses.append(Analysis(
                            lemma=lemma, pos="verb",
                            kind="reduplication_converb", kwargs={},
                            segments=tuple(segs), hypothetical=False,
                        ))
            except (ValueError, Exception):
                pass

    # Dal 3: M-ikileme (token1 != token2)
    if token1 != token2 and token2 and token2[0] == "m":
        # Kontrol: ünsüz-başlı veya ünlü-başlı
        from .reduplication import _VOWELS
        is_m = False
        if token1 and token1[0] in _VOWELS and token2 == "m" + token1:
            is_m = True
        elif token1 and token1[0] not in _VOWELS and len(token2) > 1 and token2[1:] == token1[1:]:
            is_m = True

        if is_m:
            if roots is None or token1 in roots:
                hyp = roots is None
                try:
                    if m_reduplicate(token1) == surface:
                        inner = _cached_analyze(token1, roots=None)
                        pos = inner[0].pos if inner else "noun"
                        segs = (
                            Segment(token1, "kök", (0, len(token1))),
                            Segment(token2, "m-ikileme", (len(token1) + 1, len(surface))),
                        )
                        key = ("reduplication_m", token1)
                        if key not in seen:
                            seen.add(key)
                            analyses.append(Analysis(
                                lemma=token1, pos=pos,
                                kind="reduplication_m", kwargs={},
                                segments=tuple(segs), hypothetical=hyp,
                            ))
                except (ValueError, Exception):
                    pass
```

- [ ] **Step 3: `_analyze_multi_token`'a entegre et**

`_analyze_multi_token` fonksiyonunun `return results` satırından hemen önce ekle:

```python
    # 3. İkileme analizi (tam + converb + m)
    if len(tokens) == 2:
        t1, t2 = tokens[0], tokens[1]
        seen_redup: set[tuple] = set()
        _try_reduplication_all(
            " ".join(tokens), t1, t2,
            results, seen_redup, roots,
        )
```

- [ ] **Step 4: `_cached_analyze` imzasını kontrol et**

```bash
PYTHONUTF8=1 python -c "
from turkgram import analyze
print(analyze('yavaş yavaş'))
print(analyze('koşa koşa'))
print(analyze('kitap mitap'))
"
```

- [ ] **Step 5: Commit**

```bash
git add turkgram/analysis.py
git commit -m "feat(analysis): ikileme analizi — _try_reduplication_all + _analyze_multi_token + _KINDS (Faz 9d)"
```

---

## Task 8: `tests/test_reduplication_analysis.py` — Analiz Runner

**Files:**
- Create: `tests/test_reduplication_analysis.py`

- [ ] **Step 1: Runner oluştur**

```python
"""test_reduplication_analysis.py — Faz 9d ikileme analiz runner."""
import pytest
from tests.golden_reduplication_analysis import (
    GOLDEN_ANALYSIS,
    GOLDEN_AMBIGUOUS,
    GOLDEN_CONVERB_REQUIRES_ROOTS,
)
from turkgram import analyze
from turkgram import lexicon


def _get_roots():
    return lexicon.load()


@pytest.mark.parametrize("surface,roots_needed,expected_lemma,expected_kind", GOLDEN_ANALYSIS)
def test_analyze_reduplication(surface, roots_needed, expected_lemma, expected_kind):
    roots = _get_roots() if roots_needed else None
    results = analyze(surface, roots=roots)
    kinds = {a.kind for a in results}
    lemmas = {a.lemma for a in results}
    assert expected_kind in kinds, (
        f"{surface!r}: kind={expected_kind!r} bulunamadı. Bulunanlar: {kinds}"
    )
    assert expected_lemma in lemmas, (
        f"{surface!r}: lemma={expected_lemma!r} bulunamadı. Bulunanlar: {lemmas}"
    )


@pytest.mark.parametrize("surface,expected_kinds", GOLDEN_AMBIGUOUS)
def test_analyze_ambiguous(surface, expected_kinds):
    roots = _get_roots()
    results = analyze(surface, roots=roots)
    kinds = {a.kind for a in results}
    for k in expected_kinds:
        assert k in kinds, f"{surface!r}: beklenen kind={k!r} bulunamadı"


@pytest.mark.parametrize("surface", GOLDEN_CONVERB_REQUIRES_ROOTS)
def test_converb_requires_roots(surface):
    """roots=None → converb analizi döndürülmez."""
    results = analyze(surface)
    kinds = {a.kind for a in results}
    assert "reduplication_converb" not in kinds, (
        f"{surface!r}: roots=None iken converb analizi döndürüldü"
    )
```

- [ ] **Step 2: Testleri çalıştır**

```bash
PYTHONUTF8=1 python -m pytest tests/test_reduplication_analysis.py -v
```

- [ ] **Step 3: Commit**

```bash
git add tests/test_reduplication_analysis.py
git commit -m "test(reduplication): analiz runner (Faz 9d)"
```

---

## Task 9: `tools/sweep_reduplication.py` — Korpus Tarama

**Files:**
- Create: `tools/sweep_reduplication.py`

- [ ] **Step 1: Tarama aracını oluştur**

```python
"""sweep_reduplication.py — İkileme üretim + analiz korpus taraması.

Çalıştır: PYTHONUTF8=1 python tools/sweep_reduplication.py
"""
from __future__ import annotations
import sys

from turkgram import lexicon
from turkgram.reduplication import (
    full_reduplicate, converb_reduplicate, m_reduplicate
)
from turkgram import analyze

roots = lexicon.load()
verbs = {l for l in roots if l.endswith(("mak", "mek"))}
nouns = {l for l in roots if not l.endswith(("mak", "mek"))}

errors: list[str] = []
ok_converb = ok_m = ok_full = 0

# Converb tarama
for lemma in verbs:
    try:
        surface = converb_reduplicate(lemma)
        results = analyze(surface, roots=roots)
        kinds = {a.kind for a in results}
        if "reduplication_converb" not in kinds:
            errors.append(f"MISS converb: {lemma!r} → {surface!r}")
        ok_converb += 1
    except Exception as e:
        errors.append(f"CRASH converb: {lemma!r} → {e}")

# M-ikileme tarama (m-başlı hariç)
for word in nouns:
    if word and word[0] == "m":
        continue
    try:
        surface = m_reduplicate(word)
        ok_m += 1
    except Exception as e:
        errors.append(f"CRASH m: {word!r} → {e}")

# Tam ikileme tarama (örneklem)
for word in list(nouns)[:500]:
    try:
        surface = full_reduplicate(word)
        ok_full += 1
    except Exception as e:
        errors.append(f"CRASH full: {word!r} → {e}")

print(f"Converb: {ok_converb} OK")
print(f"M-ikileme: {ok_m} OK")
print(f"Tam ikileme: {ok_full} OK (örneklem)")
if errors:
    print(f"\nHATALAR ({len(errors)}):")
    for e in errors[:20]:
        print(" ", e)
    sys.exit(1)
else:
    print("\n0 hata — PASS")
```

- [ ] **Step 2: Taramayı çalıştır**

```bash
PYTHONUTF8=1 python tools/sweep_reduplication.py
```

Beklenen: `0 hata — PASS`

- [ ] **Step 3: Commit**

```bash
git add tools/sweep_reduplication.py
git commit -m "tools(sweep): reduplication korpus tarama aracı (Faz 9d)"
```

---

## Task 10: Tam Regresyon + CLAUDE.md Güncelleme

**Files:**
- Modify: `CLAUDE.md` (§7 Faz 9d bölümü ekle)

- [ ] **Step 1: Tam paket testi çalıştır**

```bash
PYTHONUTF8=1 python -m pytest --tb=short -q
```

Beklenen: tüm testler PASS (mevcut 3922 + ~85 yeni ≈ 4007).

- [ ] **Step 2: CLAUDE.md §7'ye Faz 9d ekle**

`**FAZ 9c TAMAMLANDI**` bloğunun ardına:

```markdown
**FAZ 9d TAMAMLANDI (2026-07-17, ~4007 test):** İkileme (reduplication, `turkgram/reduplication.py`).
- `full_reduplicate(word)` → `word word`; `converb_reduplicate(lemma)` → -A ulacı × 2; `m_reduplicate(word)` → ilk C→m.
- Analiz: `analyze("yavaş yavaş")→reduplication_full`, `analyze("koşa koşa",roots=...)→reduplication_converb`, `analyze("kitap mitap")→reduplication_m`.
- Tuzaklar: m-başlı sözcük→ValueError; converb analizi roots=None→döndürülmez; `güle güle` bilinçli belirsizlik (converb+full).
- Tüm ikileme analizi `_analyze_multi_token` üzerinden, `_KINDS` dışında.
- TR API: `tam_ikile()`, `ulaç_ikile()`, `m_ikile()`.
- Hakem: leksikon fiilleri×converb + isimler×m, 0 çökme.
```

- [ ] **Step 3: Yeni dosyaları CLAUDE.md §7 "Yeni dosyalar" bölümüne ekle**

```
Yeni dosyalar (2026-07-17, Faz 9d ikileme):
- `docs/superpowers/specs/2026-07-17-reduplication-design.md` — onaylı tasarım SPEC
- `docs/superpowers/plans/2026-07-17-faz9d-reduplication.md` — implementasyon planı
- `turkgram/reduplication.py` — `full_reduplicate`, `converb_reduplicate`, `m_reduplicate`
- `turkgram/__init__.py` — reduplication export
- `turkgram/tr.py` — `tam_ikile()`, `ulaç_ikile()`, `m_ikile()` sarmalayıcılar
- `turkgram/analysis.py` — `_try_reduplication_all` + `_analyze_multi_token` genişletme
- `tests/golden_reduplication.py` — ~55 girdi bağımsız golden (motor-körü, Opus)
- `tests/golden_reduplication_analysis.py` — ~30 girdi bağımsız analiz golden (motor-körü, Opus)
- `tests/test_reduplication.py` — runner (~70 test)
- `tests/test_reduplication_analysis.py` — runner (~35 test)
- `tools/sweep_reduplication.py` — korpus tarama aracı
```

- [ ] **Step 4: Son commit**

```bash
git add CLAUDE.md
git commit -m "docs(claude): Faz 9d ikileme tamamlandı; CLAUDE.md §7 güncellendi"
```

---

## Checklist — Tamamlanma Kriterleri

- [ ] `full_reduplicate`, `converb_reduplicate`, `m_reduplicate` üretim testleri PASS
- [ ] TR API (`tam_ikile`, `ulaç_ikile`, `m_ikile`) testleri PASS
- [ ] Analiz testleri PASS: tam + converb (roots ile) + m
- [ ] `roots=None` → converb analizi döndürülmez doğrulandı
- [ ] Korpus taraması: 0 çökme
- [ ] Tam paket regresyon: 0 kırmızı test
- [ ] CLAUDE.md güncellendi
