# Faz 9d: İkileme (Reduplication) — Tasarım SPEC

**Tarih:** 2026-07-17  
**Durum:** Onaylı  
**Kapsam:** Üretim + analiz; üç tür: tam ikileme, -A ulaç ikilemesi, m-ikileme

---

## 1. Genel Bakış

Türkçe'de üç düzenli ikileme türü morfolojik/fonotaktik kurallarla üretilebilir:

| Tür | Örnek | Mekanizma |
|-----|-------|-----------|
| Tam ikileme | `yavaş yavaş` | sözcük tekrarı → yoğunlaştırılmış zarf |
| -A ulaç ikilemesi | `koşa koşa` | -A ulacı × 2 → tarz zarfı |
| M-ikileme | `kitap mitap` | ilk ünsüz → m (ünlü-başlı: m+word) |

Yansıma ikilemesi (`tık tık`, `şırıl şırıl`) leksik; bu SPEC kapsamı dışında.

---

## 2. Mimari

**Yeni modül:** `turkgram/reduplication.py`

**Değişen dosyalar:**
- `turkgram/analysis.py` — `_try_reduplication_all()` + `_KINDS` güncellemesi
- `turkgram/__init__.py` — üretim fonksiyonları export
- `turkgram/tr.py` — Türkçe sarmalayıcılar

**Bağımlılıklar:**
- `morphology.py` — `ends_in_vowel`, `_last_vowel`
- `nonfinite.py` — `converb(lemma, "optative")` → -A ulaç biçimi

**Tasarım ilkesi:** Yaklaşım B — tek modül, ayrı fonksiyonlar (`adjective.py`, `conjunction.py` emsali). `kind` string parametresi kullanılmaz; her türün kendi fonksiyonu vardır.

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
- Sözcük sınıfı kısıtı yok; her POS uygulanabilir

### 3.2 `converb_reduplicate(lemma: str) → str`

-A ulaç biçimini ikiler. Mekanizma: `nonfinite.converb(lemma, "optative")` → biçim × 2.

```python
converb_reduplicate("koşmak")   # → "koşa koşa"
converb_reduplicate("ağlamak")  # → "ağlaya ağlaya"
converb_reduplicate("gülmek")   # → "güle güle"
converb_reduplicate("gitmek")   # → "gide gide"
converb_reduplicate("yemek")    # → "yiye yiye"
converb_reduplicate("okumak")   # → "okua okua"  ← kontrol et
```

**Tuzaklar:**
- `ye_de` yumuşama (`gitmek→gide`, `gitmek→gide`) `converb()` tarafından zaten üretilir; sıfır ek mantık.
- Glide (`yemek→yiye`) aynı şekilde `converb()` çıktısından gelir.
- Mastar olmayan girdi → `converb()` hatası → `ValueError` olarak yayılır.

### 3.3 `m_reduplicate(word: str) → str`

İlk ünsüzü `m` ile değiştirir; ünlü-başlı sözcüklerde başa `m` ekler.

```python
m_reduplicate("kitap")   # → "kitap mitap"   (k→m)
m_reduplicate("çiçek")   # → "çiçek miçek"   (ç→m)
m_reduplicate("para")    # → "para mara"      (ünlü-başlı: m+word)
m_reduplicate("araba")   # → "araba maraba"   (ünlü-başlı: m+word)
m_reduplicate("insan")   # → "insan minsan"   (ünlü-başlı)
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

### 4.1 `_try_reduplication_all(surface, analyses, seen, roots)` (`analysis.py`)

`_KINDS`'ta son sıraya eklenir (derivation'dan sonra):
```
... → derivation → reduplication_full → reduplication_converb → reduplication_m
```

Üç alt-dal sırasıyla çalışır; `seen` ile duplikat engellenir.

### 4.2 Tam ikileme analizi

Tetikleyici koşul: `surface == X + " " + X` (boşlukla ayrılmış iki eş token).

```python
analyze("yavaş yavaş")
# → Analysis(lemma="yavaş", kind="reduplication_full", pos="adj", ...)

analyze("güzel güzel")
# → Analysis(lemma="güzel", kind="reduplication_full", pos="adj", ...)
```

**Oracle:** `full_reduplicate(X) == surface` → precision garantili.  
**POS:** `X`'i `_cached_analyze(X)` ile çöz → en yüksek güven adayının `pos`'u; aday yoksa `None`.  
**`roots` filtresi:** `roots is not None and X not in roots → atla` (§8.1).

### 4.3 Converb ikilemesi analizi

Tetikleyici koşul: `surface == Y + " " + Y` (iki eş token) VE tam ikileme oracle başarısız VE fiil leksikonu mevcut.

```python
analyze("koşa koşa", roots=lexicon.load())
# → Analysis(lemma="koşmak", kind="reduplication_converb", pos="verb", ...)

analyze("güle güle", roots=lexicon.load())
# → Analysis(lemma="gülmek", kind="reduplication_converb", pos="verb", ...)
```

**Oracle:** `roots`'taki her fiil lemması için `converb_reduplicate(lemma) == surface` → eşleşen lemma.  
**`roots` filtresi:** `roots is None → hypothetical=True` (fiil listesi olmadan converb oracle çalışamaz; gürültü modu kabul edilir).  
**Bilinçli belirsizlik:** `güle güle` → hem `reduplication_converb` (gülmek) hem `reduplication_full` (güle) — disambiguation sıralar.

### 4.4 M-ikileme analizi (`_analyze_multi_token` genişletme)

`analyze("kitap mitap")` → multi-token path (`len(tokens) == 2`):

```python
analyze("kitap mitap")
# → Analysis(lemma="kitap", kind="reduplication_m", pos="noun", ...)

analyze("para mara")
# → Analysis(lemma="para", kind="reduplication_m", pos="noun", ...)
```

**Kontrol:**
```
token1, token2 = tokens
token2[0] == 'm' VE (
    token1 başlıyorsa ünsüzle: token2[1:] == token1[1:]
    token1 başlıyorsa ünlüyle: token2 == "m" + token1
)
```
**Oracle:** `m_reduplicate(token1) == surface` → precision garantili.  
**`roots` filtresi:** `roots is not None and token1 not in roots → atla`.  
**Tek-token `mitap` kısıtı:** `analyze("mitap")` → m-ikileme analizi yapılmaz (doğru davranış, §3.3 kararı).

### 4.5 `Analysis` nesnesi

| Alan | Tam | Converb | M |
|------|-----|---------|---|
| `lemma` | `X` (tekrarlanan sözcük) | fiil mastarı | `token1` |
| `kind` | `"reduplication_full"` | `"reduplication_converb"` | `"reduplication_m"` |
| `pos` | özgün POS | `"verb"` | özgün POS |
| `hypothetical` | `roots is None` | `roots is None` | `roots is None` |

**Segmentasyon:** `segments = ((X, "kök"), (X, "ikileme"))` tam için; converb için `((converb_form, "kök"), (converb_form, "ikileme"))`; m için `((token1, "kök"), (m_form, "m-ikileme"))`.

---

## 5. TR API (`tr.py`)

```python
tam_ikile(kelime: str) → str     # full_reduplicate
ulaç_ikile(mastar: str) → str    # converb_reduplicate
m_ikile(kelime: str) → str       # m_reduplicate
```

Her sarmalayıcı `_tr_lower` normalizasyonu uygular (`İ→i`, `I→ı`). Test = çeviri denkliği.

---

## 6. Test Stratejisi

### Golden dosyaları (bağımsız, motor-körü, Opus)
- `tests/golden_reduplication.py` — üretim golden: ~55 giriş (15 tam + 20 converb + 20 m)
- `tests/golden_reduplication_analysis.py` — analiz golden: ~30 giriş (10+10+10)

### Runner dosyaları
- `tests/test_reduplication.py` — üretim + TR denklik (~70 test)
- `tests/test_reduplication_analysis.py` — analiz + belirsizlik (~35 test)

### Korpus tarama
- `tools/sweep_reduplication.py` — leksikon fiilleri × converb_reduplicate + leksikon isimleri × m_reduplicate; 0 çökme hedefi

### Tahmini toplam: ~85 yeni test → **~4007 test**

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
- Converb analizi `roots` olmadan hypothetical (fiil listesi gerekir)
- `güle güle` bilinçli belirsizlik: converb (gülmek) + full (güle) — disambiguation sıralar
- `parse_text()` multi-token kısıtı: compound verb ile aynı pre-existing sınır
