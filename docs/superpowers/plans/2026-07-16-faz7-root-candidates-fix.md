# Faz 7 — `_root_candidates` 3 Sınır Fix Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `analysis_candidates.py`'deki üç bilinen miss sebebini kapatmak: disharmonik alıntı mastarlama, monosilab -Iyor guard, "yor" alt-dizi rfind.

**Architecture:** Her fix tek satır veya iki satırlık minimal patch; mevcut davranış korunur. TDD: önce bağımsız golden (motor-körü, Opus subagent), sonra fix, sonra tam paket regresyon.

**Tech Stack:** Python 3, pytest, `turkgram.analysis`, `turkgram.lexicon`

**Spec:** `docs/superpowers/specs/2026-07-16-faz7-faz8-design.md` §Faz 7

---

## Dosya Haritası

| İşlem | Dosya | Ne |
|-------|-------|-----|
| Modify | `turkgram/analysis_candidates.py` | 3 minimal patch (satır 207–211, 230, 223) |
| Create | `tests/golden_root_candidates_fix.py` | Bağımsız golden — bilinen miss yüzeyleri |
| Create | `tests/test_root_candidates_fix.py` | Runner |

---

## Task 1: Bağımsız Golden (motor-körü, Opus subagent)

**Files:**
- Create: `tests/golden_root_candidates_fix.py`

Önce golden'ı motora BAKMADAN kur. Aşağıdaki yüzeyler için beklenen kök adayını CLAUDE.md + spec'ten elle doğrula:

| Yüzey | Beklenen kök | Fix |
|-------|-------------|-----|
| `inhiyor` | `inhimak` | Fix 1 (disharmonik) |
| `suyor` | `somak` | Fix 2 (monosilab) |
| `çuyor` | `çomak` | Fix 2 (monosilab) |
| `yorgalıyor` | `yorgalamak` | Fix 3 (yor-alt-dizi) |
| `yorumluyor` | `yorumlamak` | Fix 3 (yor-alt-dizi) |

- [ ] **Adım 1.1: Bağımsız golden dosyasını yaz**

Opus subagent'a dispatch et: "motoru/analysis_candidates.py'yi GÖRME; yalnız spec §Faz7 ve bu yüzeyler için elle-doğrulanmış beklentileri listele."

Dosya şablonu:

```python
# tests/golden_root_candidates_fix.py
# Motor-körü bağımsız golden — elle doğrulanmış kök aday beklentileri

GOLDEN = [
    # (yüzey, beklenen_kök_listede_mi, açıklama)
    ("inhiyor",     "inhimak",    "Fix1: disharmonik alıntı her iki mastar varyantı"),
    ("suyor",       "somak",      "Fix2: monosilab ünlü-düşme, taban='s' vowelsiz"),
    ("çuyor",       "çomak",      "Fix2: monosilab ünlü-düşme, taban='ç' vowelsiz"),
    ("yorgalıyor",  "yorgalamak", "Fix3: rfind — yor_idx=0 guard'ı atlatır"),
    ("yorumluyor",  "yorumlamak", "Fix3: rfind — yor ilk oluşum konumu düzeltildi"),
]
```

- [ ] **Adım 1.2: Runner yaz**

```python
# tests/test_root_candidates_fix.py
import pytest
from turkgram.analysis_candidates import _root_candidates
from tests.golden_root_candidates_fix import GOLDEN

@pytest.mark.parametrize("surface,expected_root,desc", GOLDEN)
def test_root_candidate_present(surface, expected_root, desc):
    """Fix sonrası beklenen kök aday listesinde bulunmalı."""
    candidates = _root_candidates(surface)  # dict[str, list[str]]
    assert expected_root in candidates, (
        f"{desc}\n  yüzey={surface!r}, aranan={expected_root!r}\n"
        f"  bulunan kökler={sorted(candidates.keys())}"
    )
```

- [ ] **Adım 1.3: Testleri çalıştır — FAIL beklenir (fix öncesi)**

```
PYTHONUTF8=1 pytest tests/test_root_candidates_fix.py -v
```

Beklenen: 5 test FAIL

---

## Task 2: Fix 1 — Disharmonik Alıntı Her İki Mastar

**Files:**
- Modify: `turkgram/analysis_candidates.py` (~satır 207–211)

- [ ] **Adım 2.1: İKİ ayrı bloğu bul**

`analysis_candidates.py`'de `msuffix`/`suffix` seçim kodu **iki yerde** vardır:

**Blok A** — primary (satır 192–199, doğrudan önek):
```python
last_v = next((c for c in reversed(prefix) if c in _VOWELS), None)
if last_v in ("e", "i", "ü", "ö"):
    suffix = "mek"
else:
    suffix = "mak"
_add(prefix + suffix, "verb")
```

**Blok B** — ters-mutasyon (satır 206–211, `_reverse_mutations` içi):
```python
last_mv = next((c for c in reversed(mutated) if c in _VOWELS), None)
if last_mv in ("e", "i", "ü", "ö"):
    msuffix = "mek"
else:
    msuffix = "mak"
_add(mutated + msuffix, "verb")
```

- [ ] **Adım 2.2: Her iki bloğu düzelt**

**Blok A** → değiştir:
```python
# Her iki mastar varyantı — disharmonik alıntılar için (primary)
for suffix in ("mak", "mek"):
    _add(prefix + suffix, "verb")
```
Eski `if last_v … suffix … _add(prefix + suffix, "verb")` satırlarını sil.

**Blok B** → değiştir:
```python
# Her iki mastar varyantı — disharmonik alıntılar için (ters-mutasyon)
for msuffix in ("mak", "mek"):
    _add(mutated + msuffix, "verb")
```
Eski `if last_mv … msuffix … _add(mutated + msuffix, "verb")` satırlarını sil.

- [ ] **Adım 2.3: Fix 1 testini çalıştır**

```
PYTHONUTF8=1 pytest "tests/test_root_candidates_fix.py::test_root_candidate_present[inhiyor-inhimak-Fix1: disharmonik alıntı her iki mastar varyantı]" -v
```

Beklenen: PASS

---

## Task 3: Fix 2 — Monosilab -Iyor Guard

**Files:**
- Modify: `turkgram/analysis_candidates.py` (~satır 230)

- [ ] **Adım 3.1: Guard satırını bul**

```python
if taban and any(c in _VOWELS for c in taban):
```

- [ ] **Adım 3.2: Guard'ı değiştir**

```python
if taban:  # monosilab (ünlüsüz) tabanlar da 8-ünlü denemeden geçebilir
```

- [ ] **Adım 3.3: Fix 2 testlerini çalıştır**

```
PYTHONUTF8=1 pytest tests/test_root_candidates_fix.py -k "suyor or çuyor" -v
```

Beklenen: 2 test PASS

---

## Task 4: Fix 3 — "yor"-Alt-Dizi rfind

**Files:**
- Modify: `turkgram/analysis_candidates.py` (~satır 223)

- [ ] **Adım 4.1: find satırını bul**

```python
yor_idx = surface_token.find("yor")
```

- [ ] **Adım 4.2: rfind ile değiştir**

```python
yor_idx = surface_token.rfind("yor")  # son oluşum — ek her zaman sonda
```

- [ ] **Adım 4.3: Tüm fix testlerini çalıştır**

```
PYTHONUTF8=1 pytest tests/test_root_candidates_fix.py -v
```

Beklenen: 5/5 PASS

---

## Task 5: Tam Paket Regresyon + Hakem

**Files:** (değişiklik yok)

- [ ] **Adım 5.1: Tam paket çalıştır**

```
PYTHONUTF8=1 pytest --tb=short -q
```

Beklenen: 3564+ test PASS, 0 FAIL

- [ ] **Adım 5.2: Korpus taraması (opsiyonel)**

```
PYTHONUTF8=1 python -c "
from turkgram import lexicon, analysis
roots = lexicon.load('verb')
miss = []
for lemma in list(roots)[:500]:
    import turkgram as tg
    try:
        tg.conjugate(lemma, 'pres', '3sg')
    except Exception as e:
        miss.append((lemma, str(e)))
print(f'Miss: {len(miss)}/500')
for m in miss[:5]: print(m)
"
```

Beklenen: 0 yeni hata

- [ ] **Adım 5.3: Hakem subagent**

Opus subagent dispatch: "3 fix doğrula: Fix1 inhimak, Fix2 somak/çomak, Fix3 yorgalamak — `_root_candidates` çıktısı beklenen kökü içeriyor mu? Yan etki var mı?"

- [ ] **Adım 5.4: Commit**

```bash
git add turkgram/analysis_candidates.py tests/golden_root_candidates_fix.py tests/test_root_candidates_fix.py
git commit -m "fix(analysis): _root_candidates 3 sınır fix — disharmonik/monosilab-Iyor/yor-rfind (Faz 7)"
```

---

## Başarı Kriterleri

- [ ] 5 golden test PASS
- [ ] Tam paket 3564+ PASS, 0 regresyon
- [ ] Hakem: CRITICAL/HIGH bulgu yok
