# Bağlaç Morfolojisi SPEC (Faz 5 D4)

## 1. Kapalı Küme

### Koordinatif Bağlaçlar (değişmez biçimler, daima ayrı yazılır)

```
ve, ama, fakat, lakin, ancak, çünkü, oysa, halbuki,
yoksa, ya da, veya, yahut, üstelik, hatta, bile, dahi, ise, ki
```

### Klitik: de / da

Ses uyumlu; `conjoin()` içinde dinamik seçilir (§2).
Her zaman ayrı yazılır: `eve de`, `okula da`.

### Korelatif Çiftler (`coordinate()` için `conj` parametresi)

| `conj` parametresi | Üretilen biçim |
|---|---|
| `"hem_hem"` | `hem X hem Y` |
| `"ya_ya"` | `ya X ya Y` |
| `"ne_ne"` | `ne X ne Y` |
| `"ister_ister"` | `ister X ister Y` |
| `"gerek_gerek"` | `gerek X gerek Y` |
| `"hem_hem_de"` | `hem X hem de Y` |

`hem_hem` ve `hem_hem_de` **farklı** korelatiflerdir; her ikisi `_VALID_CONJ`'da ayrı anahtar olarak yer alır.

---

## 2. de/da Klitik Fonolojisi

Türkçe büyük ünlü uyumu — son ünlüye bak:

| Son ünlü | Klitik |
|---|---|
| Art ünlü: a, ı, o, u | `da` |
| Ön ünlü: e, i, ö, ü | `de` |

**Fallback:** `_last_vowel()` `None` dönerse (rakam, yabancı kısaltma: `3`, `NATO`) → `"de"` (ön ünlü varsayılan).

Örnekler:
- `eve` → `e` (ön) → `de` → `"eve de"`
- `okula` → `a` (art) → `da` → `"okula da"`
- `NATO` → None → `de` → `"NATO de"`
- `3` → None → `de` → `"3 de"`

Ünsüz mutasyonu UYGULANMAZ (klitik bağımsız sözcüktür).

---

## 3. ise Bağlacı

Bağlaç olarak `ise` daima ayrı yazılır, değişmez, ses uyumu YOKTUR:

- `elma ise`, `araba ise`, `güzel ise`

**Dikkat:** Enclitic `-sA` (koşul kipi eki: `gelse`, `okusa`) **farklı** bir yapıdır — `morphology.py` kapsamında, bu modül dışında.

---

## 4. `conjoin(word, conj)` Davranışı

- `conj in ("de", "da")` → ses uyumu uygula; `word + " " + _de_da(word)` döndür
- `conj` diğer koordinatifler → `word + " " + conj` döndür (boşlukla, değişmez)
- `conj` bilinmeyen → `ValueError` (geçerli seçenekleri listele)
- `word` boş/None → `ValueError`

`conjoin()` yalnız **ayrı yazma** üretir; `-de/-da` durum eki için `decline(case='loc')` kullanılır (docstring'de belirtilir).

---

## 5. `coordinate(items, conj)` Davranışı

| Durum | Davranış |
|---|---|
| `items == []` | `ValueError` |
| `len(items) == 1` | `items[0]` döndür (değişmez) |
| `len(items) == 2`, koordinatif | `"X conj Y"` |
| `len(items) >= 3`, koordinatif | `"X, Y, ... conj Z"` |
| `len(items) == 2`, korelatif | `"HEM X HEM Y"` vb. (§1 tablosu) |
| `len(items) != 2`, korelatif | `ValueError` |
| `conj` bilinmeyen | `ValueError` |

---

## 6. `analyze()` Entegrasyonu

### `_try_conjunction_all(surface, analyses, seen)`

Oracle-dışı, kapalı-liste dalı:

```
surface == "de"  →  Analysis(lemma="de", kind="conjunction", pos="conj",
                              kwargs={}, segments=[("de", "conj")])
surface == "da"  →  Analysis(lemma="de", kind="conjunction", pos="conj",
                              kwargs={}, segments=[("da", "conj")])
diğer            →  [] (hiçbir şey ekleme)
```

**Tam-token guard:** Yalnız `surface in ("de", "da")` eşleşmesinde tetiklenir.
`"evde"`, `"sende"`, `"yerde"` bu dalı GÖRMEZ.

**Bilinçli belirsizlik:** `analyze("de")` hem bağlaç hem `demek` imp-2sg döndürür.
Precision golden `want <= got` koşuluyla test edilir (her iki analizin döndüğünü doğrular).

### `_KINDS` ve `_POS` Güncellemeleri

- `_POS` tuple'a `"conj"` eklenir (yoksa `analyze(surface, pos="conj")` `ValueError` fırlatır).
- `_KINDS` tuple'a `"conjunction"` **sona** eklenir (sort önceliği en düşük = morfolojik kind'lardan sonra).

### Dispatch Sırası

`_try_conjunction_all()` çağrısı `_try_number_all`'dan **önce**, tek-token dalında:

```python
if pos in (None, "conj"):
    _try_conjunction_all(surface_token, analyses, seen)
```

---

## 7. TR API

### `_BAĞLAÇ` Eşleme Tablosu

```python
_BAĞLAÇ = {
    # Koordinatifler (TR == iç anahtar)
    "ve": "ve", "ama": "ama", "fakat": "fakat", "lakin": "lakin",
    "ancak": "ancak", "çünkü": "çünkü", "oysa": "oysa",
    "halbuki": "halbuki", "yoksa": "yoksa", "ya da": "ya da",
    "veya": "veya", "yahut": "yahut", "üstelik": "üstelik",
    "hatta": "hatta", "bile": "bile", "dahi": "dahi", "ise": "ise",
    # Klitik — iki ayrı anahtar; conjoin() içinde ses uyumu çözülür
    "de": "de",
    "da": "da",
    # Korelatifler (TR boşluklu → iç alt-çizgili)
    "hem hem": "hem_hem",
    "ya ya": "ya_ya",
    "ne ne": "ne_ne",
    "ister ister": "ister_ister",
    "gerek gerek": "gerek_gerek",
    "hem hem de": "hem_hem_de",
}
```

### Sarmalayıcı Fonksiyonlar

```python
def bağla(kelime: str, bağlaç: str) -> str:
    """conjoin() Türkçe sarmalayıcı."""

def koordine_et(ögeler: list[str], bağlaç: str) -> str:
    """coordinate() Türkçe sarmalayıcı.
    Not: tr.sıralı() (sayı sıra eki) ile çakışmaması için 'koordine_et' seçildi.
    """
```

Her ikisi `_tr_lower()` ile normalize eder, `_BAĞLAÇ`'tan anahtar alır, ilgili fonksiyona yönlendirir.

---

## 8. Kapsam Dışı

- `ki` bağlacı koordinasyonu (bağımlı cümle, sözdizimi katmanı gerektirir — defer)
- Bağımsız bağlaçların (`ve`, `ama`, …) `analyze()` desteği (sözdizimsel bağlam gerektirir — defer)
- `de/da` çok-token cümle analizi (`context.py` K2 genişletmesi — gelecek)
- Enclitic `-sA` koşul kipi eki (`morphology.py` kapsamı)
