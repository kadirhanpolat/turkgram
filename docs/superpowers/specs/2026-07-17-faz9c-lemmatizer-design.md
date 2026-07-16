# Faz 9c — Lemmatizer Tasarım Dokümanı

Tarih: 2026-07-17  
Durum: Onaylı

---

## 1. Amaç

Yüzey biçimden lemma (sözlük biçimi) döndüren `turkgram/lemmatize.py` modülünü ekle.
Mevcut pipeline'ı (`analyze` → `disambiguation` → `context`) ince bir sarmalayıcıyla
orkestre eder; yeni morfoloji yazılmaz.

---

## 2. API Yüzeyi

### 2.1 Sade (string) API

```python
def lemmatize(
    word: str,
    *,
    roots: Collection[str] | None = None,
    freq: dict[str, int] | None = None,
) -> str | None:
    """Tek kelime → lemma. Çözümsüz → None."""

def lemmatize_text(
    text: str,
    *,
    roots: Collection[str] | None = None,
    freq: dict[str, int] | None = None,
) -> list[str | None]:
    """Metin → token başına lemma listesi. Çözümsüz token → None."""
```

### 2.2 Zengin (nesne) API

```python
@dataclass(frozen=True)
class LemmaResult:
    lemma: str
    pos: str
    confidence: float | None  # disambiguation.disambiguate çıktısından; None = freq yok
    corrected: bool           # True = spellcheck fallback kullanıldı

def lemmatize_detail(
    word: str,
    *,
    roots: Collection[str] | None = None,
    freq: dict[str, int] | None = None,
) -> LemmaResult | None:
    """Tek kelime → LemmaResult. Çözümsüz → None."""

def lemmatize_text_detail(
    text: str,
    *,
    roots: Collection[str] | None = None,
    freq: dict[str, int] | None = None,
) -> list[LemmaResult | None]:
    """Metin → token başına LemmaResult listesi. Çözümsüz token → None."""
```

### 2.3 Türkçe API (`tr.py`)

```python
temel_biçim(kelime, *, kökler=None, sıklık=None) -> str | None
temel_biçim_metin(metin, *, kökler=None, sıklık=None) -> list[str | None]
temel_biçim_detay(kelime, *, kökler=None, sıklık=None) -> LemmaResult | None
temel_biçim_metin_detay(metin, *, kökler=None, sıklık=None) -> list[LemmaResult | None]
```

### 2.4 `__init__.py` export

`lemmatize`, `lemmatize_text`, `lemmatize_detail`, `lemmatize_text_detail`, `LemmaResult`

---

## 3. Pipeline ve Fallback Zinciri

### 3.1 `lemmatize(word)` akışı

```
analyze(word, roots=roots)
  → boş değilse:
      disambiguate(results, freq=freq)
      → [0].lemma  (corrected=False)
  → boşsa:
      spellcheck.suggest(word, roots=roots)
      → öneri varsa:
          analyze(suggest[0], roots=roots)
          → disambiguate → [0].lemma  (corrected=True)
      → öneri yoksa:
          None
```

### 3.2 `lemmatize_text(text)` akışı

```
tokenize(text) → tokens
parse_text(text) → analyses_per_token   # _cached_analyze (lru_cache 4096) ile önbellekli
context.rank_in_context(tokens, analyses_per_token, freq=freq)
  → her token için sıralı analyses[0].lemma
  → boş token (çözümsüz):
      spellcheck fallback (3.1 ile aynı)
      → None
```

### 3.3 Tasarım kararları

- `lemmatize_detail` = `lemmatize` sonucunu `LemmaResult`'a sarmalar; kod tekrarı yok.
- `lemmatize_text_detail` = `lemmatize_text` iç adımlarını `LemmaResult`'a çevirir.
- `freq=None` → `disambiguation` frekansız çalışır (dilbilimsel öncelik kuralları).
- Noktalama ve bilinmeyen token'lar (`analyze → []`, `suggest → []`) → `None` döner.
- Spellcheck fallback sırasında `suggest()[0]` (en yakın öneri) kullanılır; `max_distance=2.0` varsayılan.

---

## 4. Bağımlılıklar

| Modül | Kullanım |
|---|---|
| `analysis.analyze` | Kök adayı + oracle |
| `analysis.parse_text` | Metin düzeyi toplu analiz |
| `tokenize.tokenize` | Metin → token listesi |
| `disambiguation.disambiguate` | İzole en-iyi seçimi + güven |
| `context.rank_in_context` | Bağlamsal yeniden sıralama |
| `spellcheck.suggest` | Fallback düzeltmesi |

`lemmatize.py` bu modülleri içe aktarır; tersi bağımlılık yok (döngü riski yok).

---

## 5. Test Planı

### 5.1 `tests/golden_lemmatize.py` — bağımsız (motor-körü, Opus)

~30 giriş:
- Fiil çekim → lemma: `"geliyorum" → "gelmek"`, `"okumuştu" → "okumak"`
- İsim+durum → lemma: `"evlerde" → "ev"`, `"kitabın" → "kitap"`
- Zamir: `"bana" → "ben"`, `"seni" → "sen"`
- Bileşik token: `"göz ardı etti" → "göz ardı etmek"`
- Spellcheck fallback: `"dag" → "dağ"` (`corrected=True`), `"gozluk" → "gözlük"`
- `None` beklentisi: `"xyzabc" → None`
- Noktalama: `"." → None`

### 5.2 `tests/test_lemmatize.py` — runner

- Golden üzerinden parametrik testler
- `lemmatize_text` cümle testleri (K1–K4 bağlam kurallarını tetikleyen örnekler)
- `LemmaResult` alanları doğrulaması (`lemma`, `pos`, `corrected`)
- TR API denklik: `temel_biçim(w) == lemmatize(w)`
- `ValueError` guard: boş string

### 5.3 `tools/sweep_lemmatize.py` — korpus taraması

- 26k leksikon lemması: `lemmatize(lemma) == lemma` sanity check
- 0 çökme hedefi; beklenebilir istisnalar (hypothetical gürültü) loglanır

**Tahmini yeni test sayısı:** ~60 → toplam ~3943

---

## 6. Kapsam Dışı

- Zincirli türetme lemmatizasyonu (`gözlükçü → göz` değil, `gözlük`) — tek katman yeterli.
- Edat öbeği lemmatizasyonu — sözdizimsel bağlam gerektirir, defer.
- İkileme (Faz 9d) — ayrı faz.
