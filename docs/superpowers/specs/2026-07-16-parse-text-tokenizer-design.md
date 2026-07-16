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

### H-08 Cache (Performans Borcu Giderimi)

```python
_parse_cache: dict[tuple[str, frozenset | None], list[Analysis]] = {}
```

Key: `(surface, frozenset(roots) if roots else None)`

`parse_text` içinde her token çağrısından önce cache kontrol edilir.
Aynı token aynı roots ile tekrar gelirse (uzun metin, tekrarlayan kelimeler)
`analyze()` yeniden çağrılmaz.

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
| `tests/golden_tokenize.py` | 20-30 giriş: apostrof, noktalama, karma cümle (bağımsız, elle-doğrulanmış) |
| `tests/test_tokenize.py` | golden runner |
| `tests/test_parse_text.py` | davranış testleri: noktalama→`[]`, apostrof strip, cache hit, uzunluk garantisi |

Bağımsız golden (motor-körü) yalnız `tokenize` için — `parse_text` için
`analyze()` davranış garantileri zaten mevcut golden'larda, burada entegrasyon sınır davranışları test edilir.

---

## 7. Tasarım Kararları (Özet)

| Karar | Seçilen | Neden |
|---|---|---|
| Tokenizer yeri | Ayrı `tokenize.py` | Bağımsız test; `analysis.py` büyümez |
| `parse_text` yeri | `analysis.py` | `analyze()` ile aynı modül, doğal sınır |
| Noktalama | `[]` döner, atlanmaz | `tokens[i]↔analyses[i]` indeks korunur |
| Apostrof | Sağ parçada kalır, `parse_text` soyar | Tokenizer saf; strip mantığı tek yerde |
| Cache tipi | `dict` (module-level) | `lru_cache` frozenset key'i destekler |
