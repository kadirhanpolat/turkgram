# Tasarım: Bağlaç Morfolojisi (D4)

**Tarih:** 2026-07-16  
**Kapsam:** Faz 5 D4 — `conjunction.py` bağımsız modül  
**Durum:** Onaylı

---

## Genel Bakış

Turkish conjunction module: closed-set coordination, `de/da` clitic phonology, correlative phrase synthesis, `analyze()` extension (`kind='conjunction'`), TR API wrappers. Follows the existing modular pattern (number.py, postposition.py, adjective.py).

---

## Modül Yapısı

**`turkgram/conjunction.py`**

### Public API

```python
CONJUNCTIONS: frozenset[str]
# Closed set: ve, ama, fakat, lakin, ancak, çünkü, oysa, halbuki,
# yoksa, ya da, veya, yahut, üstelik, hatta, bile, dahi, ise, ki
# Correlative keys: de/da, hem_hem, ya_ya, ne_ne, ister_ister, gerek_gerek

def conjoin(word: str, conj: str) -> str:
    """Attach conjunction to word.
    
    de/da: vowel harmony applied to last vowel of word.
    Other conjunctions: word + " " + conj (space-separated).
    """

def coordinate(items: list[str], conj: str) -> str:
    """Coordinate a list of items with conjunction.
    
    Two items:   "X conj Y"
    3+ items:    "X, Y, ... conj Z"
    Correlative: "HEM X HEM Y" / "YA X YA Y" / "NE X NE Y" etc.
    """
```

### Parametreler

| `conj` değeri | Üretilen biçim |
|---|---|
| `"ve"` | `X ve Y` |
| `"ama"`, `"fakat"`, `"lakin"`, ... | `X ama Y` (bağımsız) |
| `"de/da"` | ses uyumuyla `X de` / `X da` |
| `"hem_hem"` | `hem X hem Y` |
| `"ya_ya"` | `ya X ya Y` |
| `"ne_ne"` | `ne X ne Y` |
| `"ister_ister"` | `ister X ister Y` |
| `"gerek_gerek"` | `gerek X gerek Y` |

---

## `de/da` Klitik Fonolojisi

Son ünlüye göre allomorf seçimi:

| Son ünlü | Klitik |
|---|---|
| a, ı, o, u (art ünlü) | `da` |
| e, i, ö, ü (ön ünlü) | `de` |

- `_last_vowel()` primitifi kullanılır (yeniden implementasyon YASAK).
- Klitik **her zaman ayrı yazılır**: `eve de`, `okula da`.
- Ünsüz yumuşaması/sertleşmesi uygulanmaz (bağımsız sözcük).

---

## `analyze()` Genişletmesi

Klitik `de/da` ayrı token olduğundan tek-kelime analizi yeterlidir:

```python
analyze("de") → Analysis(lemma="de", kind="conjunction", pos="conj",
                          axes={}, segments=[("de", "conj")])
analyze("da") → Analysis(lemma="de", kind="conjunction", pos="conj",
                          axes={}, segments=[("da", "conj")])
```

- `kind="conjunction"` yeni kind — mevcut kind'larla çakışmaz.
- Bağımsız bağlaçlar (`ve`, `ama`, ...) `analyze()` scope dışı (sözdizimsel bağlam gerektirir).
- `ki` bağlacı: kapalı kümeye girer, `conjoin()`/`coordinate()` scope dışı (bağımlı cümle → sözdizimi defer).

---

## TR API

**`tr.py`** sarmalayıcılar:

```python
def bağla(kelime: str, bağlaç: str) -> str:
    """conjoin() Türkçe sarmalayıcı."""

def sırala(ögeler: list[str], bağlaç: str) -> str:
    """coordinate() Türkçe sarmalayıcı."""
```

TR parametre eşlemesi (`_BAĞLAÇ` sözlüğü):

```python
_BAĞLAÇ = {
    "ve": "ve", "ama": "ama", "fakat": "fakat", "lakin": "lakin",
    "çünkü": "çünkü", "ancak": "ancak", "oysa": "oysa",
    "halbuki": "halbuki", "yoksa": "yoksa", "ya da": "ya da",
    "veya": "veya", "yahut": "yahut", "üstelik": "üstelik",
    "hatta": "hatta", "bile": "bile", "dahi": "dahi", "ise": "ise",
    "de/da": "de/da",
    "hem hem": "hem_hem", "ya ya": "ya_ya", "ne ne": "ne_ne",
    "ister ister": "ister_ister", "gerek gerek": "gerek_gerek",
}
```

---

## Test Stratejisi

| Dosya | İçerik |
|---|---|
| `spec/conjunction-spec.md` | Dilbilgisi kuralları, kapalı küme, de/da uyumu |
| `tests/golden_conjunction.py` | Bağımsız golden — motor-körü, Opus |
| `tests/test_conjunction.py` | Runner |

**Tahmini test dağılımı (~75 test):**

- `conjoin` de/da uyumu: ~16 (8 ünlü × art/ön)
- `conjoin` diğer bağlaçlar: ~10
- `coordinate` ikili/üçlü: ~15
- `coordinate` korelatif: ~10
- `analyze("de"/"da")`: ~6
- TR denklik (`bağla`/`sırala`): ~18

---

## İş Akışı

Mevcut CLAUDE.md §2 iş akışı:

1. `spec/conjunction-spec.md` — dilbilgisi kuralları (elle, ana oturum)
2. `tests/golden_conjunction.py` — bağımsız golden (Opus, motor-körü)
3. `turkgram/conjunction.py` — motor
4. `tests/test_conjunction.py` — runner
5. Hakem + korpus taraması (leksikon × de/da, 0 çökme)

---

## Kapsam Dışı

- `ki` bağlacı koordinasyonu (bağımlı cümle, sözdizimi katmanı gerektirir)
- Bağımsız bağlaçların `analyze()` desteği (sözdizimsel bağlam gerektirir)
- `de/da` çok-token cümle analizi (context.py K2 genişletmesiyle ele alınabilir — gelecek)
