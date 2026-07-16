# Faz 9b: Türkçe Yazım Denetimi (Spellcheck) — Tasarım Dokümanı

Tarih: 2026-07-16

## Özet

`turkgram/spellcheck.py` — Türkçe yazım geçerliliği kontrolü ve kök tabanlı öneri sistemi.
Mevcut `analyze()` + `lexicon` altyapısı üzerine BK-tree indeksi ve Türkçe-ağırlıklı
Levenshtein mesafesi ekler. Saf Python, dış bağımlılık yok.

**V1 kapsam notu:** `suggest()` **kök (lemma) düzeyinde** öneri döner — `"evte"` → `["ev"]`,
`"evde"` değil. V2'de morfolojik şablon korunarak yüzey yeniden üretimi eklenir (§8).

---

## 1. Public API

```python
from turkgram import spellcheck, SpellResult

# Geçerlilik kontrolü
spellcheck.is_valid("evde")          # True
spellcheck.is_valid("evdte")         # False

# Öneri listesi — V1: kök (lemma) döner
spellcheck.suggest("seker")          # ["şeker"]
spellcheck.suggest("cok", max_suggestions=3, max_distance=2)  # ["çok", ...]

# Birleşik sonuç
result = spellcheck.check("gozluk")
# SpellResult(word="gozluk", is_valid=False, suggestions=("gözlük",))
```

### Fonksiyon İmzaları

```python
def is_valid(word: str, *, roots: frozenset[str] | None = None) -> bool
def suggest(word: str, *, roots: frozenset[str] | None = None,
            max_suggestions: int = 5, max_distance: float = 2.0) -> list[str]
def check(word: str, *, roots: frozenset[str] | None = None,
          max_suggestions: int = 5, max_distance: float = 2.0) -> SpellResult
```

**`roots=None` semantiği** — `analyze()`'den FARKLIDIR:
- `analyze(word, roots=None)` → hypothetical mod (gürültü, kısıtlama yok)
- `is_valid(word, roots=None)` → `lexicon.load()` otomatik yüklenir (spellcheck'in amacı gerçek Türkçe doğrulamaktır)
- Çağıran kendi kök kümesini geçerek bu davranışı override edebilir

**Girdi normalizasyonu:** İngilizce API de `_tr_lower` uygular (büyük/küçük harf güvenliği).
Bu normalizasyon `analyze()` içinde de yapılır; ikinci kez uygulanması zararsız ve tutarlıdır.

### SpellResult

```python
@dataclass(frozen=True)
class SpellResult:
    word: str
    is_valid: bool
    suggestions: tuple[str, ...]   # is_valid=True ise boş tuple; immutable (frozen uyum)
```

`is_valid=True` olduğunda `check()` kısa-devre yapar: `analyze()` başarılı → `suggestions=()`
direkt döner, BK-tree sorgusu yapılmaz.

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

### 3.1 _roots() yardımcısı

```python
def _roots(roots: frozenset[str] | None) -> frozenset[str]:
    return roots if roots is not None else lexicon.load()
```

Spellcheck fonksiyonlarında `roots=None` → leksikon zorunlu yüklenir. Bu `analyze()`
semantiğinin bilinçli inversiyonudur: spellcheck'te `roots=None` "her şey geçerli" DEĞİL,
"standart Türkçe leksikonu kullan" demektir.

### 3.2 is_valid()

```python
def is_valid(word, *, roots=None):
    word = _tr_lower(word)
    if not word or len(word) > 200:
        return False
    r = _roots(roots)
    return any(not a.hypothetical for a in analyze(word, roots=r))
```

Agglütinasyon tam kapsanır: `evlerde`, `gelmişti`, `okuyordum` geçerli sayılır.

### 3.3 BK-tree İndeksi

`_BKTree` iç sınıfı (~60 satır saf Python):

- `build(words: Iterable[str]) → _BKTree` — O(n log n) ortalama, O(n²) en kötü durum.
  26k lemma için pratikte 50–200ms, `@lru_cache` singleton ile yalnız bir kez yapılır.
- `query(word: str, max_distance: float) → list[tuple[float, str]]` — SIRASIZ döner;
  sıralama `suggest()` sorumluluğundadır.

Singleton inşası `suggest()` ilk çağrısında yapılır (import-time değil).

### 3.4 Türkçe-Ağırlıklı Levenshtein: _tr_distance(a, b) → float

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

`"seker"` → `"şeker"` (distance 0.5) < `"teker"` (distance 1.0). `max_distance=2.0`
eşiği float-safe; validation: `max_distance <= 0 → ValueError`.

### 3.5 Öneri Sıralama

1. `_BKTree.query(word, max_distance)` çağrısı → sirasız `(distance, lemma)` listesi
2. Distance'a göre artan sırala
3. Eşit distance'ta `lexicon.load_freq()` sıklık sayımına göre azalan sırala —
   frekans verisi her zaman yüklenir (default davranış); fallback: alfabetik (deterministik tiebreak)
4. `max_suggestions` ile kırp → `list[str]` (lemma'lar); `suggest()` `list[str]` döner
5. `check()` bu listeyi `tuple(suggestions)` ile `SpellResult.suggestions` alanına dönüştürür
6. `load_freq()` dict'i YALNIZ `.get(lemma, 0)` lookup ile kullanılır; mutasyon yapılmaz;
   `lru_cache` singleton (leksikon gibi) — ilk `suggest()` çağrısında yüklenir

---

## 4. Hata Yönetimi

| Durum | Davranış | Gerekçe |
|---|---|---|
| Boş string / yalnız boşluk | `is_valid=False`, `suggestions=()` | Kelime değil |
| 200+ karakter | `is_valid=False`, `suggestions=()` | DoS koruması (CLI ile tutarlı) |
| `max_suggestions < 1` | `ValueError` | Programcı hatası |
| `max_distance <= 0` | `ValueError` | Anlamsız eşik |

Not: 200+ karakter `False` döner (sessiz); `ValueError` değil — çağıran bu durumu özel
işlemek istiyorsa `len(word) > 200` önceden kontrol etmelidir.

---

## 5. CLI Entegrasyonu

Tek kelime girişi desteklenir; cümle modu kapsam dışı.

```bash
python -m turkgram check evdte
# evdte: GEÇERSİZ
# Öneriler: evde (V2 — V1'de: ev)

python -m turkgram check evde
# evde: GEÇERLİ
```

`__main__.py`'deki mevcut `analyze` komutuna paralel. `--roots`, `--max-suggestions`,
`--max-distance` opsiyonel flag'ler.

---

## 6. Test Stratejisi

- `tests/golden_spellcheck.py` — bağımsız golden (motor-körü, Opus), elle-doğrulanmış
- `tests/test_spellcheck.py` — runner

Golden kapsamı:
- Geçerli kelimeler: `ev`, `evde`, `gelmek`, `geliyorum`, `güzel` → `is_valid=True, suggestions=()`
- `is_valid=True` kısa-devre: `check("ev")` → `suggestions=()` (BK-tree sorgusu yapılmaz)
- Geçersiz + öneri: `seker→("şeker",)`, `cok→("çok",)`, `gozluk→("gözlük",)`
- Türkçe karakter konfüzyon sıralaması: `seker` önerisi `"şeker"` < `"teker"` (distance önceliği)
- Edge case: boş string, 201 karakter, `max_suggestions=1`, `max_distance=0.5`
- `roots=` özel küme ile geçerlilik override
- `ValueError`: `max_suggestions=0`, `max_distance=0`

Hakem: 26k leksikon lemması tam taraması → 0 çökme.

---

## 7. Entegrasyon Noktaları

- `turkgram/spellcheck.py` → `is_valid`, `suggest`, `check`, `SpellResult`
- `turkgram/__init__.py` → aşağıdaki isimler re-export edilir:
  `from turkgram.spellcheck import is_valid as _sc_is_valid, suggest, check, SpellResult`
  Kullanım: `turkgram.spellcheck` (modül erişimi) veya `from turkgram import SpellResult, check`.
  `is_valid` isim çakışması riski varsa modül erişimi tercih edilir: `turkgram.spellcheck.is_valid()`.
- `turkgram/tr.py` → `yazım_geçerli()`, `öneri()`, `denetle()`
- `turkgram/__main__.py` → `check` komutu

---

## 8. V2 Yolu (Kapsam Dışı — Davranışsal Kırılma Uyarısı)

Yaklaşım C (yüzey yeniden üretimi): `suggest()` kök döndükten sonra orijinal kelimenin
morfolojik şablonu soyulup önerilen köke aynı ekle yeniden uygulanır
(`"evte"` → öneri kök `"ev"` → yeniden üret `"evde"`).

**Uyarı:** API imzası değişmez ama davranış değişir — V1'de `suggest("evte") → ["ev"]`,
V2'de `→ ["evde"]`. Lemma bekleyen çağıranlar kırılır. V2 geçişinde golden testler
güncellenmelidir.
