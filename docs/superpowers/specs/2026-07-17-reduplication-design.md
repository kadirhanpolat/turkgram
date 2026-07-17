# Faz 9d: İkileme (Reduplication) — Tasarım SPEC

**Tarih:** 2026-07-17  
**Durum:** Onaylı  
**Kapsam:** Üretim + analiz; üç tür: tam ikileme, -A ulaç ikilemesi, m-ikileme

---

## 1. Genel Bakış

Türkçe'de üç düzenli ikileme türü morfolojik/fonotaktik kurallarla üretilebilir:

| Tür | Örnek | Mekanizma |
|-----|-------|-----------|
| Tam ikileme | `yavaş yavaş` | sözcük tekrarı → yoğunlaştırılmış zarf/sıfat |
| -A ulaç ikilemesi | `koşa koşa` | -A ulacı × 2 → tarz zarfı |
| M-ikileme | `kitap mitap` | ilk ünsüz → m (ünlü-başlı: m+word) |

Yansıma ikilemesi (`tık tık`, `şırıl şırıl`) leksik; bu SPEC kapsamı dışında.

---

## 2. Mimari

**Yeni modül:** `turkgram/reduplication.py`

**Değişen dosyalar:**
- `turkgram/analysis.py` — `_try_reduplication_all()` + `_analyze_multi_token` genişletme
- `turkgram/__init__.py` — üretim fonksiyonları export
- `turkgram/tr.py` — Türkçe sarmalayıcılar

**Bağımlılıklar:**
- `morphology.py` — `ends_in_vowel`, `_last_vowel`
- `nonfinite.py` — `converb(lemma, "optative")` → -A ulaç biçimi (`-A` eki; `koşmak→koşa`, `gülmek→güle`)

**Tasarım ilkesi:** Yaklaşım B — tek modül, ayrı fonksiyonlar (`adjective.py`, `conjunction.py` emsali). `kind` string parametresi kullanılmaz; her türün kendi fonksiyonu vardır.

**Analiz mimarisi notu:** Üç tür de çift-token yüzey üretir (`"X X"`, `"X mX'"`). Dolayısıyla tüm analiz yolları `_analyze_multi_token` üzerinden geçer; `_KINDS` zincirine **eklenmez**. `_try_reduplication_all` `_analyze_multi_token` içinden çağrılır.

---

## 3. Üretim API

### 3.1 `full_reduplicate(word: str) → str`

Sözcüğü kendisiyle tekrarlar.

```python
full_reduplicate("yavaş")  # → "yavaş yavaş"
full_reduplicate("güzel")  # → "güzel güzel"
full_reduplicate("büyük")  # → "büyük büyük"
full_reduplicate("ev")     # → "ev ev"
```

**Kısıtlar:**
- Boş string → `ValueError("Boş sözcük")`
- Sözcük sınıfı kısıtı yok; her POS uygulanabilir (tipik kullanım: sıfat/zarf yoğunlaştırma)

### 3.2 `converb_reduplicate(lemma: str) → str`

Parametre: **fiil mastarı** (`-mAk` biçimi). `-A` ulaç biçimini ikiler.  
Mekanizma: `nonfinite.converb(lemma, "optative")` → `-A` ulaç biçimi × 2.  
`"optative"` converb türü tam olarak `-A` ekini üretir (istek/tarz ulacı; Korkmaz §A5).

```python
converb_reduplicate("koşmak")   # → "koşa koşa"
converb_reduplicate("ağlamak")  # → "ağlaya ağlaya"
converb_reduplicate("gülmek")   # → "güle güle"
converb_reduplicate("gitmek")   # → "gide gide"
converb_reduplicate("yemek")    # → "yiye yiye"
converb_reduplicate("okumak")   # → "okuya okuya"  (ünlü-final → glide y)
```

**Tuzaklar:**
- `ye_de` yumuşama (`gitmek→gide`, `gelmek→gele`) `converb()` tarafından zaten üretilir; sıfır ek mantık.
- Glide (`yemek→yiye`, `okumak→okuya`) aynı şekilde `converb()` çıktısından gelir.
- Mastar olmayan girdi → `converb()` hatası → `ValueError` olarak yayılır.

### 3.3 `m_reduplicate(word: str) → str`

İlk ünsüzü `m` ile değiştirir; ünlü-başlı sözcüklerde başa `m` ekler.

```python
m_reduplicate("kitap")   # → "kitap mitap"   (k→m)
m_reduplicate("çiçek")   # → "çiçek miçek"   (ç→m)
m_reduplicate("para")    # → "para mara"      (ünlü-başlı: m+word)
m_reduplicate("araba")   # → "araba maraba"   (ünlü-başlı: m+word)
m_reduplicate("insan")   # → "insan minsan"   (ünlü-başlı)
m_reduplicate("masa")    # → ValueError        (m-başlı sözcük)
```

**Algoritma:**
```
word başlıyorsa ünlüyle → m_form = "m" + word
word başlıyorsa ünsüzle → m_form = "m" + word[1:]
sonuç = word + " " + m_form
```

**Kısıtlar:**
- `word[0] == 'm'` → `ValueError("m-başlı sözcüğe m-ikileme uygulanamaz")` — p-ikileme kapsam dışı.
- Boş string → `ValueError("Boş sözcük")`

**Ünlü tespiti:** `_VOWELS = frozenset("aeıioöuüâîû")` (`morphology.py` emsali).

---

## 4. Analiz Entegrasyonu

### 4.1 Genel Mimari

Tüm ikileme analizleri **`_analyze_multi_token`** içinde çalışır (compound verb emsali — `len(tokens) == 2`). `_KINDS` zincirine **eklenmez**.

`_try_reduplication_all(surface, token1, token2, seen, roots)` → `_analyze_multi_token`'dan çağrılır. Üç alt-dal **bağımsız** çalışır (birbirini engellemez):
1. Tam ikileme: `token1 == token2`
2. Converb ikilemesi: `token1 == token2` VE `roots is not None` — tamdan bağımsız; ikisi aynı anda üretilebilir (örn. `güle güle`)
3. M-ikileme: `token1 != token2`, m-pattern kontrolü

`seen` ile duplikat engellenir.

### 4.2 Tam ikileme analizi

Tetikleyici koşul: `token1 == token2`.

```python
analyze("yavaş yavaş")
# → Analysis(lemma="yavaş", kind="reduplication_full", pos="adj", ...)

analyze("güzel güzel")
# → Analysis(lemma="güzel", kind="reduplication_full", pos="adj", ...)
```

**Oracle:** `full_reduplicate(token1) == surface` → precision garantili.  
**POS tespiti:** `_cached_analyze(token1, roots=None)` çağrılır (çağıranın `roots`'u değil; sonsuz döngü riski yok çünkü `token1` tek-token, `full_reduplicate(token1)` ≠ `token1`). İlk sonucun `pos` alanı kullanılır; sonuç yoksa `pos=None`.  
**`roots` filtresi:** `roots is not None and token1 not in roots → atla` (§8.1).

**`güle güle` belirsizlik notu:** `güle` `roots`'ta yer almıyorsa `reduplication_full` üretilmez; yalnız `reduplication_converb` (gülmek). `roots`'ta varsa her ikisi → disambiguation sıralar. Bu bilinçli tasarım.

### 4.3 Converb ikilemesi analizi

Tetikleyici koşul: `token1 == token2` VE tam ikileme oracle başarısız VE `roots` sağlanmış.

**`roots=None` → converb analizi yapılmaz.** Prefix-tabanlı kök çıkarımı converb için çalışmaz; lemma kurtarmak fiil listesi gerektirir.

```python
analyze("koşa koşa", roots=lexicon.load())
# → Analysis(lemma="koşmak", kind="reduplication_converb", pos="verb", ...)

analyze("güle güle", roots=lexicon.load())
# → Analysis(lemma="gülmek", kind="reduplication_converb", pos="verb", ...)

analyze("koşa koşa")  # roots=None → converb analizi döndürülmez
# → []
```

**Oracle:** `roots`'taki tüm lemmalar için `converb_reduplicate(lemma)` denenır; mastar olmayan lemmalar `ValueError` fırlatır → sessizce atlanır. Eşleşen lemma → `Analysis` üretilir. (Not: `roots` plain `set[str]`; POS alanı içermez — `ValueError` ile filtreleme fiil-olmayan kökleri otomatik eler.)  
**`roots` filtresi:** `roots is None → skip` (converb). `roots is not None → tüm roots üzerinde dene`.

### 4.4 M-ikileme analizi

Tetikleyici koşul: `token1 != token2`, m-pattern kontrolü.

```python
analyze("kitap mitap")
# → Analysis(lemma="kitap", kind="reduplication_m", pos="noun", ...)

analyze("para mara")
# → Analysis(lemma="para", kind="reduplication_m", pos="noun", ...)
```

**Kontrol:**
```
token2[0] == 'm' VE (
    token1 başlıyorsa ünsüzle: token2[1:] == token1[1:]
    token1 başlıyorsa ünlüyle: token2 == "m" + token1
)
```
**Oracle:** `m_reduplicate(token1) == surface` → precision garantili.  
**`roots` filtresi:** `roots is not None and token1 not in roots → atla`.  
**POS tespiti:** `full_reduplicate` ile aynı — `_cached_analyze(token1, roots=None)` → ilk sonucun `pos`'u.  
**Tek-token `mitap` kısıtı:** `analyze("mitap")` → m-ikileme analizi yapılmaz (doğru davranış, §3.3 kararı).

### 4.5 `Analysis` nesnesi

| Alan | Tam | Converb | M |
|------|-----|---------|---|
| `lemma` | `token1` | fiil mastarı | `token1` |
| `kind` | `"reduplication_full"` | `"reduplication_converb"` | `"reduplication_m"` |
| `pos` | `_cached_analyze(token1)` → pos | `"verb"` | `_cached_analyze(token1)` → pos |
| `hypothetical` | `roots is None` | her zaman `False` (`roots=None → skip`) | `roots is None` |

**Segmentasyon (bilinçli tasarım kararı):**
- Tam: `((token1, "kök"), (token1, "ikileme"))` — ilk token kök, ikinci ikileme etiketi
- Converb: `((converb_form, "kök"), (converb_form, "ikileme"))`
- M: `((token1, "kök"), (m_form, "m-ikileme"))`

---

## 5. TR API (`tr.py`)

```python
tam_ikile(kelime: str) → str     # full_reduplicate
ulaç_ikile(mastar: str) → str    # converb_reduplicate  (mastar = -mAk biçimi)
m_ikile(kelime: str) → str       # m_reduplicate
```

Her sarmalayıcı `_tr_lower` normalizasyonu uygular (`İ→i`, `I→ı`). Test = çeviri denkliği.

---

## 6. Test Stratejisi

### Golden dosyaları (bağımsız, motor-körü, Opus)
- `tests/golden_reduplication.py` — üretim golden: ~55 giriş (15 tam + 20 converb + 20 m)
- `tests/golden_reduplication_analysis.py` — analiz golden: ~30 giriş (10+10+10)

### Runner dosyaları
- `tests/test_reduplication.py` — üretim + TR denklik + ValueError (~70 test)
- `tests/test_reduplication_analysis.py` — analiz + belirsizlik + roots=None davranışı (~35 test)

### Korpus tarama
- `tools/sweep_reduplication.py` — leksikon fiilleri × converb_reduplicate + leksikon isimleri × m_reduplicate; 0 çökme hedefi

### Tahmini toplam: ~85 yeni test → **~4007 test** (mevcut 3922 + 85)

---

## 7. Kapsam Dışı

- **Yansıma ikilemesi** (`tık tık`, `şırıl şırıl`) — leksik, defer
- **m-başlı sözcük p-ikilemesi** (`masa pasa`) — marjinal, defer
- **İkileme analizi `parse_text()` içinde** — pre-existing multi-token kısıtı (compound verb ile aynı); explicit `analyze("X X")` çalışır
- **Zincirli ikileme** — kapsam dışı
- **Adverbial yeniden-kurulum** (`katıla katıla gülmek`) — sözdizimsel, defer (önceden ertelenmiş)

---

## 8. CLAUDE.md Notları (implementasyon sonrası eklenecek)

- `reduplication.py` — `full_reduplicate`, `converb_reduplicate`, `m_reduplicate`
- `m`-başlı sözcük → `ValueError` (p-ikileme kapsam dışı)
- Converb analizi `roots=None` → analiz döndürülmez (fiil listesi zorunlu)
- `güle güle` belirsizliği: `güle` `roots`'ta varsa hem converb hem full; yoksa yalnız converb
- `parse_text()` multi-token kısıtı: compound verb ile aynı pre-existing sınır
- Tüm ikileme analizi `_analyze_multi_token` üzerinden geçer, `_KINDS` zincirine eklenmez
