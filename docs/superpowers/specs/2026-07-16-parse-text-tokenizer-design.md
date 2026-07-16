# parse_text + Tokenizer Tasarım Dokümanı

**Tarih:** 2026-07-16  
**Kapsam:** `tokenize()` yeni modülü + `parse_text()` public API  
**Durum:** Onaylandı

---

## 1. Bağlam

Turkgram'ın mevcut `analyze(surface) → list[Analysis]` API'si tek token alır.
Gerçek metin pipeline'ı için toplu analiz (`parse_text`) ve tokenizasyon gerekli.
Bu tasarım iki bileşeni kapsar:

- `tokenize(text) → list[str]` — dar tokenizer (boşluk + noktalama + apostrof)
- `parse_text(text, roots=None) → list[list[Analysis]]` — toplu analiz

Tasarım kararları mimari critique sonuçlarına dayanır (2026-07-16, `mimari-kararlar.md`).

---

## 2. Dosya Yapısı

```
turkgram/
  tokenize.py        ← YENİ modül
  analysis.py        ← parse_text eklenir (mevcut dosya)
  __init__.py        ← tokenize + parse_text export eklenir

tests/
  golden_tokenize.py ← bağımsız golden (motor-körü, elle-doğrulanmış)
  test_tokenize.py   ← runner
  test_parse_text.py ← parse_text davranış testleri
```

---

## 3. Tokenizer: `tokenize.py`

### İmza

```python
def tokenize(text: str) -> list[str]:
    ...
```

### Davranış — 3 adım

1. **Boşlukla böl** — `text.split()` temel bölme
2. **Baş/son noktalama ayrıştır** — `.`, `,`, `!`, `?`, `:`, `;`, `"`, `(`, `)` vb.
   her biri ayrı token olarak çıkar
3. **Apostrof bölme** — kelime ortasındaki `'` iki tokena böler;
   apostrof sağ parçada kalır: `"Ankara'nın"` → `["Ankara", "'nın"]`

Saf noktalama tokenları listede **kalır** (`"."`, `","` vb.) — `parse_text`
bunlar için `[]` döner ve indeks hizalaması korunur.

### Örnekler

```
"Ali geldi."          → ["Ali", "geldi", "."]
"Ankara'nın sınırı"   → ["Ankara", "'nın", "sınırı"]
"Nereye gidiyorsun?"  → ["Nereye", "gidiyorsun", "?"]
"(eve) gitti"         → ["(", "eve", ")", "gitti"]
"geldi, gitti"        → ["geldi", ",", "gitti"]
```

### Kapsam Dışı

- Büyük harf normalizasyonu → `analyze()` içinde `_tr_lower` zaten var
- Klitik ayrıştırma (-mı, -de, -ki) → `analyze()`'a delege (morfolojisiz çözülemez)
- Birleşik fiil birleştirme → `analyze()` çok-token dalında zaten mevcut

---

## 4. `parse_text`: `analysis.py`'e Ekleme

### İmza

```python
def parse_text(
    text: str,
    roots: Collection[str] | None = None,
    *,
    max_derivation_depth: int = 1,
) -> list[list[Analysis]]:
```

### Davranış

- `tokenize(text)` → token listesi
- Her token için `analyze(token, roots=roots, max_derivation_depth=max_derivation_depth)`
- Saf noktalama → `[]` (analyze zaten boş döner, özel dal gerekmez)
- Apostrof-başlı token (`'nın`) → baştaki `'` soyulur → `analyze("nın", ...)`
- Dönüş uzunluğu = `len(tokenize(text))` (indeks hizalaması garantili)

### Apostrof Strip Kuralı (C1 + H1 düzeltmesi)

Apostrof-başlı tokendan **tam olarak bir düz apostrof** (`'`, U+0027) soyulur —
`lstrip("'")` DEĞİL; `token[1:]` if `token[0] == "'"` else `token`.
Bu kural yalnız ASCII düz apostrof için geçerlidir; kıvrık apostrof (`'`, U+2018/U+2019)
aynı şekilde işlenmez (girdi normalleştirilmemiş kabul edilir, tokenizer tarafından bölünmez).
`analyze()` içinde `_tr_lower(surface.strip())` uygulandığından büyük harf normalizasyonu
bu strip'ten bağımsız olarak `analyze()` içinde gerçekleşir.

**Bilinen sınır:** `"Ankara'nın"` → `analyze("nın")` → `roots` verilmişse muhtemelen
`hypothetical=True` (özel isim kökleri leksikonda yok). Bu beklenen davranıştır; `parse_text`
apostrof sonrası eki çözümlemeyi garanti etmez.

### H-08 Cache (Performans Borcu Giderimi)

```python
from functools import lru_cache

@lru_cache(maxsize=4096)
def _cached_analyze(surface: str, roots_key: frozenset | None, depth: int) -> tuple[Analysis, ...]:
    roots = set(roots_key) if roots_key is not None else None
    return tuple(analyze(surface, roots=roots, max_derivation_depth=depth))
```

Key: `(surface, frozenset(roots) if roots is not None else None, depth)` —
`if roots is not None` (C1 düzeltmesi: boş `set()` ile `None` çakışmasını önler).

`lru_cache(maxsize=4096)` sınırlı boyut garantisi sağlar (M1 düzeltmesi).
CPython GIL altında tek-iş parçacıklı etkin kullanım güvenlidir; çoklu iş parçacığı
durumunda benign duplicate compute mümkündür, kilit gerekmez (M2 notu).

`parse_text` içinde her token için `_cached_analyze(surface, roots_key, depth)` çağrılır.

### H-10 Entegrasyonu

`parse_text` çıktısı doğrudan `rank_in_context` çiftine beslenir:

```python
tokens = tokenize(text)
analyses = parse_text(text, roots=lexicon.load())
top1 = rank_in_context(tokens, analyses)
```

Böylece `rank_in_context`'in mevcut double-analyze sorunu (H-10)
`parse_text` üzerinden geçince doğal çözülür.

---

## 5. Export

```python
# __init__.py
from .tokenize import tokenize
from .analysis import parse_text
```

CLI genişleme (`python -m turkgram parse-text`) → defer (API önce).

---

## 6. Test Stratejisi

| Dosya | İçerik |
|---|---|
| `tests/golden_tokenize.py` | 20-30 giriş: apostrof, noktalama, karma cümle, boş dizi, saf noktalama (bağımsız, elle-doğrulanmış) |
| `tests/test_tokenize.py` | golden runner |
| `tests/test_parse_text.py` | davranış testleri: noktalama→`[]`, apostrof strip, cache hit, uzunluk garantisi |

Bağımsız golden (motor-körü) yalnız `tokenize` için — `parse_text` için
`analyze()` davranış garantileri zaten mevcut golden'larda, burada entegrasyon sınır davranışları test edilir.

**Zorunlu edge case'ler golden'da:**
- `tokenize("")` → `[]`
- `tokenize("...")` → `[".", ".", "."]`
- `parse_text("", roots=set())` → `[]` (C1: boş roots, None değil)
- Apostrof-başlı token: tam olarak bir `'` soyulur
- `rank_in_context` bağlamı: `parse_text` çıktısı doğrudan beslenebilir (H2: noktalama slotları `[]` → context kuralları gracefully atlar)

### H-10 / rank_in_context Notu (H2)

`rank_in_context` bağlam pencereleri noktalama slotlarını (`[]`) **gracefully atlar**
(boş aday listesi context kuralı oluşturmaz). Bu `parse_text` tasarım hatası değil,
mevcut `rank_in_context` davranışıdır. Doğrulanması implementasyon aşamasında yapılır.

---

## 7. Tasarım Kararları (Özet)

| Karar | Seçilen | Neden |
|---|---|---|
| Tokenizer yeri | Ayrı `tokenize.py` | Bağımsız test; `analysis.py` büyümez |
| `parse_text` yeri | `analysis.py` | `analyze()` ile aynı modül, doğal sınır |
| Noktalama | `[]` döner, atlanmaz | `tokens[i]↔analyses[i]` indeks korunur |
| Apostrof | Sağ parçada kalır, `parse_text` soyar | Tokenizer saf; strip mantığı tek yerde |
| Cache tipi | `lru_cache(maxsize=4096)` | frozenset hashable → key olarak kullanılabilir; sınırlı boyut |
