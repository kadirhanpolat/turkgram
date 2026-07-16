# Faz 9b: Türkçe Yazım Denetimi (Spellcheck) — Tasarım Dokümanı

Tarih: 2026-07-16

## Özet

`turkgram/spellcheck.py` — Türkçe yazım geçerliliği kontrolü ve kök tabanlı öneri sistemi.
Mevcut `analyze()` + `lexicon` altyapısı üzerine BK-tree indeksi ve Türkçe-ağırlıklı
Levenshtein mesafesi ekler. Saf Python, dış bağımlılık yok.

---

## 1. Public API

```python
from turkgram import spellcheck, SpellResult

# Geçerlilik kontrolü
spellcheck.is_valid("evde")          # True
spellcheck.is_valid("evdte")         # False

# Öneri listesi (kök düzeyi, V1)
spellcheck.suggest("seker")          # ["şeker"]
spellcheck.suggest("cok", max_suggestions=3, max_distance=2)  # ["çok", ...]

# Birleşik sonuç
result = spellcheck.check("gozluk")
# SpellResult(word="gozluk", is_valid=False, suggestions=["gözlük"])
```

### Fonksiyon İmzaları

```python
def is_valid(word: str, *, roots: frozenset[str] | None = None) -> bool
def suggest(word: str, *, roots: frozenset[str] | None = None,
            max_suggestions: int = 5, max_distance: int = 2) -> list[str]
def check(word: str, *, roots: frozenset[str] | None = None,
          max_suggestions: int = 5, max_distance: int = 2) -> SpellResult
```

`roots=None` → `lexicon.load()` lazy singleton kullanılır (opt-in deseniyle tutarlı).
Çağıran kendi kök kümesini geçirebilir.

### SpellResult

```python
@dataclass(frozen=True)
class SpellResult:
    word: str
    is_valid: bool
    suggestions: list[str]   # is_valid=True ise boş liste
```

---

## 2. Türkçe API (tr.py)

```python
from turkgram import tr

tr.yazım_geçerli("evde")      # True
tr.öneri("seker")              # ["şeker"]
tr.denetle("gozluk")          # SpellResult(...)
```

Sarmalayıcılar `_tr_lower` ile normalize eder, İngilizce API'ye delege eder.

---

## 3. İç Mimari

### 3.1 is_valid()

```python
def is_valid(word, *, roots=None):
    r = _roots(roots)
    return any(not a.hypothetical for a in analyze(word, roots=r))
```

`analyze()` + `lexicon` — sıfır yeni morfoloji. Agglütinasyon tam kapsanır
(`evlerde`, `gelmişti` vb. geçerli sayılır).

### 3.2 BK-tree İndeksi

`_BKTree` iç sınıfı (~60 satır saf Python):

- `build(words: Iterable[str]) → _BKTree`
- `query(word: str, max_distance: float) → list[tuple[float, str]]`

Leksikon 26k lemma üzerinden `@lru_cache` singleton olarak bir kez inşa edilir.
Sonraki `suggest()` çağrıları O(log n) ile çalışır (~1ms).

### 3.3 Türkçe-Ağırlıklı Levenshtein: _tr_distance(a, b) → float

Standart Levenshtein'dan tek fark: Türkçe karakter konfüzyonlarında maliyet 0.5.

| Konfüzyon çifti | Maliyet |
|---|---|
| ı ↔ i | 0.5 |
| ö ↔ o | 0.5 |
| ü ↔ u | 0.5 |
| ş ↔ s | 0.5 |
| ç ↔ c | 0.5 |
| ğ ↔ g | 0.5 |
| Diğer ekleme/silme/değiştirme | 1.0 |

Bu sayede `"seker"` → `"şeker"` (distance 0.5) `"teker"` (distance 1.0)'den önce sıralanır.
`max_distance=2` eşiği float-safe çalışır.

### 3.4 Öneri Sıralama

1. BK-tree çıktısını distance'a göre artan sırala
2. Eşit distance'ta `lexicon.load_freq()` sıklık sayımına göre sırala (opsiyonel)
3. `max_suggestions` ile kırp

---

## 4. Hata Yönetimi

| Durum | Davranış |
|---|---|
| Boş string / yalnız boşluk | `is_valid=False`, `suggestions=[]` |
| 200+ karakter | `is_valid=False`, `suggestions=[]` |
| `max_suggestions < 1` | `ValueError` |
| `max_distance < 1` | `ValueError` |

---

## 5. CLI Entegrasyonu

```bash
python -m turkgram check evdte
# evdte: GEÇERSİZ
# Öneriler: evde

python -m turkgram check evde
# evde: GEÇERLİ
```

`__main__.py`'deki mevcut `analyze` komutuna paralel.

---

## 6. Test Stratejisi

- `tests/golden_spellcheck.py` — bağımsız golden (motor-körü, Opus), elle-doğrulanmış
- `tests/test_spellcheck.py` — runner

Golden kapsamı:
- Geçerli kelimeler: ev, evde, gelmek, geliyorum, güzel
- Geçersiz + öneri beklentisi: seker→şeker, cok→çok, gozluk→gözlük, inek→inek (zaten geçerli)
- Türkçe karakter konfüzyonları: ı/i, ö/o, ü/u, ş/s, ç/c, ğ/g
- Edge case: boş string, 201 karakter, `max_suggestions=1`, `max_distance=1`
- Parametrik: `roots=` özel küme ile geçerlilik

Hakem: 26k leksikon lemması tam taraması → 0 çökme.

---

## 7. Entegrasyon Noktaları

- `turkgram/__init__.py` → `spellcheck`, `SpellResult` export
- `turkgram/tr.py` → `yazım_geçerli()`, `öneri()`, `denetle()`
- `turkgram/__main__.py` → `check` komutu
- `docs/superpowers/specs/` → bu dosya

---

## 8. V2 Yolu (Kapsam Dışı)

Yaklaşım C (yüzey yeniden üretimi): `suggest()` kök döndükten sonra orijinal kelimenin
morfolojik şablonu soyulup önerilen köke aynı ekle yeniden uygulanır
(`"evte"` → öneri kök `"ev"` → yeniden üret `"evde"`).
API imzası değişmez, iç implementasyon güncellenir. Bu aşamada defer.
