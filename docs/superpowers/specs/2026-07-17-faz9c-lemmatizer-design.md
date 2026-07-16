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
    """Tek kelime veya çok-token string → lemma.
    
    Çözümsüz → None. Boş string → ValueError.
    Çok-token string (ör. "göz ardı etti") desteklenir; analyze() delegasyonuyla.
    """

def lemmatize_text(
    text: str,
    *,
    roots: Collection[str] | None = None,
    freq: dict[str, int] | None = None,
) -> list[str | None]:
    """Metin → token başına lemma listesi. Çözümsüz token → None.
    
    NOT: roots, tokenize+analyze döngüsüyle her token'a ayrı ayrı uygulanır
    (parse_text roots parametresi almadığından doğrudan kullanılmaz).
    Boş string → ValueError.
    """
```

### 2.2 Zengin (nesne) API

```python
@dataclass(frozen=True)
class LemmaResult:
    lemma: str
    pos: str
    confidence: float   # disambiguation.disambiguate softmax skoru; freq=None → dilbilimsel ağırlıklı
    corrected: bool     # True = spellcheck fallback kullanıldı

def lemmatize_detail(
    word: str,
    *,
    roots: Collection[str] | None = None,
    freq: dict[str, int] | None = None,
) -> LemmaResult | None:
    """Tek kelime → LemmaResult. Çözümsüz → None. Boş string → ValueError."""

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

**NOT:** TR sarmalayıcılar `_tr_lower` ÇAĞIRMAZ — içeride `analyze` ve `spellcheck`
zaten normalleştirir (CLAUDE.md §9b pattern'i).

### 2.4 `__init__.py` export

`lemmatize`, `lemmatize_text`, `lemmatize_detail`, `lemmatize_text_detail`, `LemmaResult`

---

## 3. Pipeline ve Fallback Zinciri

### 3.1 `_lemmatize_inner(word, roots, freq, corrected=False)` — ortak özel yardımcı

Tüm public fonksiyonların paylaştığı tek implementasyon noktası:

```
analyze(word, roots=roots)
  → boş değilse:
      ranked = disambiguate(results, freq=freq)
      # disambiguate → list[tuple[Analysis, float]]
      best, confidence = ranked[0]
      → LemmaResult(lemma=best.lemma, pos=best.pos,
                    confidence=confidence, corrected=corrected)
  → boşsa:
      spellcheck.suggest(word, roots=roots, max_distance=2.0)
      → öneri varsa:
          _lemmatize_inner(suggest[0], roots, freq, corrected=True)
      → öneri yoksa:
          None
```

`lemmatize(word)` = `_lemmatize_inner(...).lemma` (veya `None`)  
`lemmatize_detail(word)` = `_lemmatize_inner(...)` (veya `None`)

### 3.2 `lemmatize_text(text)` akışı

```
tokens = tokenize(text)
# parse_text roots parametresi almadığından, roots geçilmesi gerektiğinde
# token bazlı analyze() döngüsü kullanılır; roots=None ise parse_text kısayolu:
if roots is None:
    analyses_per_token = parse_text(text)   # _cached_analyze ile önbellekli
else:
    analyses_per_token = [analyze(t, roots=roots) for t in tokens]

ranked_per_token = context.rank_in_context(tokens, analyses_per_token, freq=freq)

for i, ranked in enumerate(ranked_per_token):
    if ranked:
        → ranked[0].lemma  (corrected=False)
    else:
        → spellcheck fallback: _lemmatize_inner(tokens[i], roots, freq)
          → .lemma veya None
          # NOT: fallback token'lar bağlam yeniden sıralamasından yararlanamaz;
          #      bu bilinçli bir tradeoff (bağlam bilgisi olmayan düzeltme yeterli).
```

`lemmatize_text_detail` aynı akışı izler, ancak `LemmaResult` nesneleri döndürür.
Spellcheck fallback `corrected=True` olarak işaretlenir.

### 3.3 Tasarım kararları

- **`_lemmatize_inner` özel yardımcı:** `lemmatize` ve `lemmatize_detail` aynı kodu
  çalıştırır; kod tekrarı yok, ikisi de `_lemmatize_inner` üzerine inşa edilir.
- **`confidence` her zaman `float`:** `disambiguate` softmax skoru daima döner;
  `freq=None` olsa da dilbilimsel ağırlıklı güven üretilir, `None` olmaz.
- **`max_distance=2.0` sabit:** spellcheck fallback eşiği parametrize edilmez (YAGNI).
- **`roots=None` + `parse_text` kısayolu:** `roots` verildiğinde `parse_text` atlanır,
  per-token `analyze(token, roots=roots)` döngüsü kullanılır — `roots` asla sessizce görmezden gelinmez.
- **Boş string → `ValueError`:** her public fonksiyon için (analyze() davranışıyla tutarlı).
- **Noktalama token'ları** (`analyze → []`, `suggest → []`) → `None` döner (beklenen).

---

## 4. Bağımlılıklar

| Modül | Kullanım |
|---|---|
| `analysis.analyze` | Kök adayı + oracle |
| `analysis.parse_text` | Metin düzeyi toplu analiz (roots=None kısayolu) |
| `tokenize.tokenize` | Metin → token listesi |
| `disambiguation.disambiguate` | En-iyi seçimi + `tuple[Analysis, float]` |
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
- Bileşik token: `"göz ardı etti" → "göz ardı etmek"` (`lemmatize` çok-token destekler)
- Spellcheck fallback: `"dag" → "dağ"` (`corrected=True`), `"gozluk" → "gözlük"`
- `None` beklentisi: `"xyzabc" → None`
- Noktalama: `"." → None`

### 5.2 `tests/test_lemmatize.py` — runner

- Golden üzerinden parametrik testler
- `lemmatize_text` cümle testleri (K1–K4 bağlam kurallarını tetikleyen örnekler)
- `LemmaResult` alanları doğrulaması (`lemma`, `pos`, `confidence: float`, `corrected`)
- TR API denklik: `temel_biçim(w) == lemmatize(w)`
- `ValueError` guard: boş string → her dört public fonksiyon için
- `corrected=True` propagasyon: `lemmatize_text_detail` spellcheck fallback testi

### 5.3 `tools/sweep_lemmatize.py` — korpus taraması

- 26k leksikon lemması üzerinden **0 çökme** hedefi
- `lemmatize(lemma) == lemma` ihlalleri loglanır ama test başarısızlığı sayılmaz
  (belirsiz lemma'lar farklı bir kök döndürebilir — bu hata değil, disambiguation kararıdır)

**Tahmini yeni test sayısı:** ~60 → toplam ~3943

---

## 6. Kapsam Dışı

- Zincirli türetme lemmatizasyonu (`gözlükçü → göz` değil, `gözlük`) — tek katman yeterli.
- Edat öbeği lemmatizasyonu — sözdizimsel bağlam gerektirir, defer.
- `max_distance` parametresi — YAGNI, ileride eklenebilir.
- İkileme (Faz 9d) — ayrı faz.
