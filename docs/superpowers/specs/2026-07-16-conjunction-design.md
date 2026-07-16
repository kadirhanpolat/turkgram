# Tasarım: Bağlaç Morfolojisi (D4)

**Tarih:** 2026-07-16  
**Kapsam:** Faz 5 D4 — `conjunction.py` bağımsız modül  
**Durum:** Onaylı (reviewer bulgular giderildi)

---

## Genel Bakış

Turkish conjunction module: closed-set coordination, `de/da` clitic phonology, correlative phrase synthesis, `analyze()` extension (`kind='conjunction'`), TR API wrappers. Follows the existing modular pattern (number.py, postposition.py, adjective.py).

---

## Modül Yapısı

**`turkgram/conjunction.py`**

### Kapalı Küme

```python
CONJUNCTIONS: frozenset[str] = frozenset({
    # Koordinatif
    "ve", "ama", "fakat", "lakin", "ancak", "çünkü", "oysa", "halbuki",
    "yoksa", "ya da", "veya", "yahut", "üstelik", "hatta", "bile", "dahi",
    "ise", "ki",
    # Klitik (özel)
    "de", "da",
    # Korelatif iç elemanlar (coordinate() tarafından kullanılır)
    "hem", "ya", "ne", "ister", "gerek",
})
```

### Public API

```python
def conjoin(word: str, conj: str) -> str:
    """Attach conjunction to word.

    de/da: vowel harmony applied to last vowel of word.
    Other conjunctions: word + " " + conj (space-separated).

    NOT for case suffix -de/-da: use decline(case='loc') instead.
    Unknown conj raises ValueError listing valid options.
    """

def coordinate(items: list[str], conj: str) -> str:
    """Coordinate a list of items with conjunction.

    Empty list → ValueError.
    Single item → return item unchanged.
    Two items:   "X conj Y"
    3+ items:    "X, Y, ... conj Z"  (for non-correlatives)
    Correlative: "HEM X HEM Y" / "YA X YA Y" / "NE X NE Y" etc.
    Correlatives require exactly 2 items (ne/ya/ister/gerek) or 2+ for hem.
    Unknown conj raises ValueError.
    """
```

### Korelatif Bağlaçlar

`coordinate()` için `conj` değerleri ve üretilen biçimler:

| `conj` değeri | Üretilen biçim | Not |
|---|---|---|
| `"ve"` | `X ve Y` / `X, Y ve Z` | standart |
| `"ama"`, `"fakat"`, `"lakin"`, ... | `X ama Y` | bağımsız koordinatifler |
| `"de/da"` | ses uyumuyla `X de` / `X da` | yalnız `conjoin()` için |
| `"hem_hem"` | `hem X hem Y` | 2 öğe zorunlu |
| `"ya_ya"` | `ya X ya Y` | 2 öğe zorunlu |
| `"ne_ne"` | `ne X ne Y` | 2 öğe zorunlu |
| `"ister_ister"` | `ister X ister Y` | 2 öğe zorunlu |
| `"gerek_gerek"` | `gerek X gerek Y` | 2 öğe zorunlu |
| `"hem_hem_de"` | `hem X hem de Y` | yalnız 2 öğe |

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
- **Rakam/yabancı kısaltma fallback:** `_last_vowel()` `None` dönerse (ünlü bulunamazsa) → `"de"` varsayılan (ön ünlü default, Türkçe okuma kuralıyla uyumlu: `NATO de`, `3 de`). Docstring'de belirtilir.

---

## `analyze()` Genişletmesi

### Precision Tuzakları ve Çözümleri

**C1 — `_KIND_FUNCS` sorunu:** `conjunction` kind'ı analysis-by-generation oracle'ını kullanamaz (üretici fonksiyon yok; `de`/`da` serbest morfemdir). Çözüm: `_try_conjunction_all()` özel dalı yazar, oracle dışı kapalı-liste kontrolü yapar.

```python
def _try_conjunction_all(surface: str) -> list[Analysis]:
    """Conjunctions are free morphemes — closed-list check, no oracle."""
    if surface in ("de", "da"):
        return [Analysis(lemma="de", kind="conjunction", pos="conj",
                         axes={}, segments=[(surface, "conj")])]
    return []
```

**C2 — `de` = `demek` imp-2sg belirsizliği:** `analyze("de")` meşru iki okuma verir:
1. `kind="conjunction"` (bağlaç `de`)
2. `kind="conjugate"` lemma=`demek`, tense=imp, person=2sg

İkisi de geçerli — tasarım bunu **bilinçli belirsizlik** olarak tescil eder. Disambiguation katmanı (`disambiguation.rank()`) sıklık+bağlam kanıtıyla sıralayabilir. Precision golden her iki analizin `want <= got` koşuluyla test edilir.

**C3 — Bulunma eki çakışması:** `_try_conjunction_all()` YALNIZ tam-token eşleşmesinde tetiklenir: `surface == "de"` veya `surface == "da"` (büyük-küçük harf normalize edilmiş). `"evde"`, `"sende"`, `"yerde"` gibi kelimeler bu dalı hiç görmez (tek-token değil; suffix analyser ayrı iş).

### `analyze()` Entegrasyonu

- `_KINDS` tuple'a `"conjunction"` eklenir (sıralama için; `_rank_key` bilinmeyen → 99).
- `_POS` seti/tuple'a `"conj"` eklenir (`analyze(pos="conj")` filtresi çalışsın).
- `_try_conjunction_all()` `analyze()` içindeki kind dispatch zincirinin başında çağrılır (precision-first: kapalı liste → erken dön).

---

## TR API

**`tr.py`** sarmalayıcılar:

```python
def bağla(kelime: str, bağlaç: str) -> str:
    """conjoin() Türkçe sarmalayıcı."""

def koordine_et(ögeler: list[str], bağlaç: str) -> str:
    """coordinate() Türkçe sarmalayıcı.
    
    Not: tr.sıralı() (sayı sıra) ile karışmaması için 'koordine_et' seçildi.
    """
```

**`_BAĞLAÇ` eşleme tablosu:**

```python
_BAĞLAÇ = {
    # Koordinatifler (TR == İng, aynen geçer)
    "ve": "ve", "ama": "ama", "fakat": "fakat", "lakin": "lakin",
    "ancak": "ancak", "çünkü": "çünkü", "oysa": "oysa",
    "halbuki": "halbuki", "yoksa": "yoksa", "ya da": "ya da",
    "veya": "veya", "yahut": "yahut", "üstelik": "üstelik",
    "hatta": "hatta", "bile": "bile", "dahi": "dahi", "ise": "ise",
    # Klitik de/da — iki ayrı anahtar; harmoni conjoin() içinde otomatik çözülür
    "de": "de/da",   # bağla("ev", "de")  → "ev de"
    "da": "de/da",   # bağla("okul", "da") → "okul da"
    # Korelatifler (Türkçe boşluklu → İng alt-çizgili)
    "hem hem": "hem_hem",
    "ya ya": "ya_ya",
    "ne ne": "ne_ne",
    "ister ister": "ister_ister",
    "gerek gerek": "gerek_gerek",
    "hem hem de": "hem_hem_de",   # yalnız 2 öğe; "hem X hem de Y"
}
```

**`ise` bağlacı notu:** `conjoin(word, "ise")` → `word + " ise"` (boşlukla, harmoni yok). `ise` bağlaç olarak kullanıldığında daima ayrı yazılır ve değişmez. Enclitic `-sA` (koşul kipi eki, `morphology.py` kapsamında) **farklı bir yapıdır** ve bu modülle ilgisi yoktur.

---

## Test Stratejisi

| Dosya | İçerik |
|---|---|
| `spec/conjunction-spec.md` | Dilbilgisi kuralları, kapalı küme, de/da uyumu, tuzaklar |
| `tests/golden_conjunction.py` | Bağımsız golden — motor-körü, Opus |
| `tests/test_conjunction.py` | Runner |

**İş akışı (CLAUDE.md §2):**

1. `spec/conjunction-spec.md` — dilbilgisi kuralları (elle, ana oturum)
2. `tests/golden_conjunction.py` — bağımsız golden (Opus dispatch, motor-körü)
3. `turkgram/conjunction.py` — motor (golden'ı geçecek minimal kod)
4. `tests/test_conjunction.py` — runner
5. Hakem + korpus: leksikon kelimeler × `conjoin()` × `de/da` allomorfu, 0 çökme; `coordinate()` ikili/üçlü/korelatif, 0 çökme

**Tahmini test dağılımı (~80 test):**

- `conjoin` de/da uyumu: ~16 (8 ünlü × art/ön)
- `conjoin` diğer bağlaçlar: ~10
- `conjoin` rakam/yabancı fallback: ~4
- `coordinate` ikili/üçlü: ~15
- `coordinate` korelatif: ~12
- `coordinate` kenar (boş/tek): ~4
- `analyze("de"/"da")` belirsizlik: ~8
- TR denklik (`bağla`/`koordine_et`): ~18

---

## Kapsam Dışı

- `ki` bağlacı koordinasyonu (bağımlı cümle, sözdizimi katmanı gerektirir)
- Bağımsız bağlaçların `analyze()` desteği (sözdizimsel bağlam gerektirir; `ve`, `ama` tek-token olarak gelirse kapalı küme tanır ama kind önerilmez)
- `de/da` çok-token cümle analizi (context.py K2 genişletmesiyle ele alınabilir — gelecek)
