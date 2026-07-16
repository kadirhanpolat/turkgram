# Tasarım: Türkçe Hecelemleme ve Vurgu — `syllabify.py`

**Tarih:** 2026-07-16
**Faz:** Faz 9 — Hecelemleme & Vurgu

---

## 1. Amaç

Türkçe sözcükleri hecelerine ayır ve vurgulu heceyi belirle.
Birincil kullanım: tireleme, pedagojik gösterim, IPA/TTS altyapısı.

---

## 2. Kapsam

**Dahil:**
- Hece sınırı tespiti (`syllabify`)
- Vurgulu hece indeksi (`stress`)
- Vurgu işaretli gösterim (`stress_mark`)
- Yabancı alıntı + yer adı istisna tablosu (`_STRESS_EXCEPTIONS`)
- `turkgram/tr.py`'ye eklenen Türkçe sarmalayıcılar

**Kapsam dışı:**
- Fonem düzeyinde analiz (IPA modülü ayrı)
- Suffix-specific stress (vurgusuzlaştırıcı ek listesi, defer)
- Zincirli hece+morfoloji entegrasyonu (defer)

**Önemli sınır:** Tüm fonksiyonlar **morfoloji-agnostik** çalışır — yalnız yüzey string alır.
`stress()` doğruluğu bağlaçlar, söylem parçacıkları ve eklenmiş biçimler için garantili değildir.
Güvenilir kullanım: sözlük başlıkları, lemma, taban sözcükler.

**Gelecek entegrasyon notu:** IPA modülü (`phonology.py`) ileride `stress()` çıktısını tüketecek
(IPA stres işareti `ˈ` ekleme). Bu modül sinyal verir, IPA modülü iter.

---

## 3. Mimari

Yeni bağımsız modül: `turkgram/syllabify.py`

Bağımlılık: yalnız Python standart kütüphanesi.
`phonology.py`'a bağımlılık YOK (boru hattı yaklaşımı reddedildi: IPA hataları hecelemeye sızar).

Sabitleri bu modülde tanımlanır:
- `_SYLLABLE_SEP = '·'` (U+00B7 MIDDLE DOT — hece ayırıcı)
- `_VOWELS` (ünlü kümesi)
- `_STRESS_EXCEPTIONS` (istisna tablosu)

---

## 4. Hece Kuralları

Her hecede tam olarak bir ünlü.

**Ünlü kümesi:** `a e ı i o ö u ü â î û` (circumflex dahil; `â î û` normalization öncesi alıntılarda görülür)

**Bölünme kuralları:**

| Desen | Bölünme | Örnek |
|-------|---------|-------|
| V + C + V | V · CV (C sağa) | a·ra, o·ku |
| V + CC + V | VC · CV (ilk C sola, ikinci sağa) | al·dı, er·ken |
| V + CCC + V | VCC · CV (ilk iki C sola, son C sağa) | Türk·çe, kart·lı |
| Sözcük sonu | ünsüzler sol hecede kalır | gel·dim |

**Yabancı onset kümesi politikası:**
Türkçe'de yerli hece-başı kümesi yoktur. N>1 ünsüz kümelerinde **maksimal onset** ilkesi uygulanır:
mümkün olduğunca çok ünsüzü sağ hecenin başına gönder. Bilinmeyen küme → tüm ünsüzü sağa ver.
İstisna tablosunda kayıtlı sözcükler (`stres`, `tren`, `spor`) için heceler önceden sabitlenmiştir.

**Algoritma:** O(n) doğrusal.
1. Sözcükteki tüm ünlü konumlarını bul.
2. Ardışık ünlüler arasındaki ünsüz kümesini al.
3. Küme uzunluğuna göre böl: 1 → sağa, 2 → ortadan, 3 → ilk ikisi sola.
4. Sözcük başı ve sonu ünsüz öbeklerini ilgili heceye ekle.

---

## 5. Vurgu Kuralları

**Varsayılan:** Son hece vurgulu.

**İstisna tablosu:** `_STRESS_EXCEPTIONS: dict[str, int]`
- Anahtar: `_tr_lower()` ile normalize edilmiş küçük harfli sözcük
- Değer: 0-tabanlı vurgulu hece indeksi (baştan)
- Kaynak: **elle küratörlenmiş, üçüncü taraf kaynak yok** (THIRD_PARTY_LICENSES.md'e giriş gerekmez)
- İlk sürüm: ~30–50 giriş; golden en az 15 giriş kapsamalı

**Kapsanan kategoriler (seçili örnekler — doğrulanmış vurgu indeksleri):**

| Sözcük | Hece analizi | Vurgulu hece indeksi |
|--------|-------------|----------------------|
| ankara | an·ka·ra | 0 |
| istanbul | is·tan·bul | 1 |
| izmir | iz·mir | 0 |
| bursa | bur·sa | 0 |
| adana | a·da·na | 1 |
| stres | stres | 0 |
| tren | tren | 0 |
| spor | spor | 0 |

**Suffix-specific stress (kapsam dışı, defer):** `-lI`, `-lIk`, `-sIz`, `-CI`, `-DA` gibi vurgusuzlaştırıcı
ekler bu versiyonda işlenmez. Sınır §2'de belgelenmiştir.

---

## 6. API

**Büyük/küçük harf dönüşümü:**
- `stress_mark()` işlem öncesi girdiyi `_tr_lower()` ile küçük harfe çevirir, ardından
  vurgulu heceyi `_tr_upper()` ile büyük harfe çevirir. Çıktı her zaman normalize edilmiş formdadır.
- `_tr_upper()` zorunludur: Python `str.upper()` kullanılmaz — `i→İ`, `ı→I` (Türkçe duyarlı).
- `syllabify()` ve `stress()` girdiyi normalize etmez; olduğu gibi işler.

**Vurgulu heceyi büyük harfe çevirme:** Yalnızca vurgulu hecenin tüm harfleri büyük harfe çevrilir;
diğer heceler küçük kalır.

```python
# turkgram/syllabify.py

def syllabify(word: str) -> list[str]:
    """Sözcüğü hecelerine böl.

    syllabify("geldiğimiz")  # → ["gel", "di", "ği", "miz"]
    syllabify("Türkçe")      # → ["Türk", "çe"]
    syllabify("ankara")      # → ["an", "ka", "ra"]
    syllabify("")            # → []
    syllabify("krt")         # → ["krt"]  (ünlüsüz; kısaltma pasif geçiş)
    """

def stress(word: str) -> int | None:
    """Vurgulu heceye 0-tabanlı indeks (baştan). Boş string için None.

    İstisna tablosuna _tr_lower(word) anahtarıyla bakılır; yoksa son hece.
    stress("geldi")     # → 1  (son hece, 0-tabanlı; 2 heceli → index 1)
    stress("istanbul")  # → 1  (is·TAN·bul)
    stress("ankara")    # → 0  (AN·ka·ra)
    stress("")          # → None
    stress("krt")       # → 0  (ünlüsüz: tek "hece"; anlamlı vurgu yok,
                        #        yalnız indeks tutarlılığı; stress("ankara")==0
                        #        ile karıştırılmamalı)
    """

def stress_mark(word: str) -> str:
    """Vurgulu heceyi büyük harfle + U+00B7 ayracıyla göster.

    Girdi _tr_lower ile normalize edilir; vurgulu hece _tr_upper ile büyük yapılır.
    stress_mark("geldi")    # → "gel·Dİ"
    stress_mark("istanbul") # → "is·TAN·bul"
    stress_mark("ankara")   # → "AN·ka·ra"   (istisna: index 0)
    stress_mark("")         # → ""
    stress_mark("krt")      # → "KRT"
    """
```

**Edge case sözleşmesi:**

| Giriş | `syllabify` | `stress` | `stress_mark` |
|-------|-------------|----------|----------------|
| `""` | `[]` | `None` | `""` |
| `"krt"` (ünlüsüz) | `["krt"]` | `0` | `"KRT"` |
| `"a"` (tek ünlü) | `["a"]` | `0` | `"A"` |
| `"ankara"` | `["an","ka","ra"]` | `0` | `"AN·ka·ra"` |
| `"istanbul"` | `["is","tan","bul"]` | `1` | `"is·TAN·bul"` |
| `"geldi"` | `["gel","di"]` | `1` | `"gel·Dİ"` |

---

## 7. TR API (`turkgram/tr.py`)

TR sarmalayıcılar `turkgram/tr.py`'ye eklenir (yeni dosya oluşturulmaz).

```python
def hecele(kelime: str) -> list[str]: ...      # syllabify
def vurgu(kelime: str) -> int | None: ...      # stress
def vurgu_işaretle(kelime: str) -> str: ...    # stress_mark
```

`turkgram/__init__.py` export: `syllabify`, `stress`, `stress_mark`.

---

## 8. Test Stratejisi

**Akış:** SPEC → bağımsız golden (Opus, motor-körü) → motor → hakem

- `tests/golden_syllabify.py` — ~40 giriş:
  - CV / CVC / CVCC / CVCCC örüntüleri
  - Üç ünsüz kümesi (Türk·çe, kart·lı)
  - **En az 15 istisna tablosu girişi** — hem `stress()` indeksi hem `stress_mark()` çıktısı test edilmeli
  - Yabancı onset kümesi (stres, tren, spor)
  - Circumflex ünlü içeren sözcükler (kâtip, rûh)
  - Edge case: boş string, ünlüsüz, tek hece, tek ünlü

- `tests/test_syllabify.py` — runner + TR denklik testleri

- **Hakem / korpus taraması:** `lexicon.load()` ile tüm lemmaları çek; her lemma için
  `syllabify(word)` ve `stress(word)` çağır; 0 istisna / çökme.
  Ek kontrol: `for word in _STRESS_EXCEPTIONS: assert stress(word) is not None`

---

## 9. Sıralı Geliştirme Planı

Bu faz tamamlandıktan sonra sıra:
1. ✅ Hecelemleme + vurgu (`syllabify.py`) — **bu faz**
2. Yazım denetimi (`spellcheck.py`)
3. Lemmatizer (`lemmatize.py`)
4. İkileme (reduplication) morfolojisi
