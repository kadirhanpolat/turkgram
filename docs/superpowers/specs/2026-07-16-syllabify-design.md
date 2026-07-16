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
- Yabancı alıntı için kapalı istisna tablosu (`_STRESS_EXCEPTIONS`)
- `tr.py` Türkçe sarmalayıcılar

**Kapsam dışı:**
- Fonem düzeyinde analiz (IPA modülü ayrı)
- Çekim/türetme eklerinin vurgusunu ayrıştırma (suffix-specific stress, defer)
- Zincirli hece analizi (morfoloji ile entegrasyon, defer)

---

## 3. Mimari

Yeni bağımsız modül: `turkgram/syllabify.py`

Bağımlılık: yalnız Python standart kütüphanesi.
`phonology.py`'a bağımlılık YOK (boru hattı yaklaşımı reddedildi: IPA hataları hecelemeye sızar).

---

## 4. Hece Kuralları

Türkçe hece yapısı: her hecede tam olarak bir ünlü.

| Desen | Bölünme | Örnek |
|-------|---------|-------|
| V + C + V | V · CV | a·ra, o·ku |
| V + CC + V | VC · CV | al·dı, er·ken |
| V + CCC + V | VCC · CV | Türk·çe, kart·lı |
| Sözcük sonu | ünsüzler sol hecede kalır | gel·dim |

**Algoritma:** Tek geçiş O(n).
1. Sözcükteki tüm ünlü konumlarını bul.
2. Ardışık ünlüler arasındaki ünsüz kümesini al.
3. Küme uzunluğuna göre böl: 1→sağa, 2→ortadan, 3→ilk ikisi sola.
4. Sözcük başı ve sonu ünsüz öbeklerini ilgili heceye ekle.

**Ünlü kümesi:** `a e ı i o ö u ü` (ASCII + Türkçe özel).

---

## 5. Vurgu Kuralları

**Varsayılan:** Son hece vurgulu.

**İstisna tablosu:** `_STRESS_EXCEPTIONS: dict[str, int]`
- Anahtar: küçük harfli sözcük
- Değer: 0-tabanlı hece indeksi (baştan)
- İlk sürüm: ~30–50 giriş (yer adları + kesin kural-dışı alıntılar)

**Kapsanan istisna kategorileri:**
- Yer adları: `ankara→0`, `istanbul→0`, `izmir→0`, `bursa→0` …
- Kural-dışı yabancı alıntı (kapalı küme, tartışmalı olanlar varsayılana düşer)

---

## 6. API

```python
# turkgram/syllabify.py

def syllabify(word: str) -> list[str]:
    """Sözcüğü hecelerine böl.

    syllabify("geldiğimiz")  # → ["gel", "di", "ği", "miz"]
    syllabify("Türkçe")      # → ["Türk", "çe"]
    syllabify("")            # → []
    """

def stress(word: str) -> int:
    """Vurgulu heceye 0-tabanlı indeks (baştan).

    İstisna tablosuna bakılır; yoksa son hece.
    stress("geldi")    # → 1  (son hece)
    stress("Ankara")   # → 0  (yer adı istisnası)
    """

def stress_mark(word: str) -> str:
    """Vurgulu heceyi büyük harf + · ayracıyla göster.

    stress_mark("geldi")   # → "gel·Dİ"
    stress_mark("Ankara")  # → "AN·ka·ra"
    """
```

**Edge case sözleşmesi:**
| Giriş | `syllabify` | `stress` | `stress_mark` |
|-------|-------------|----------|----------------|
| `""` | `[]` | `0` | `""` |
| `"krt"` (ünlüsüz) | `["krt"]` | `0` | `"KRT"` |
| sayı/noktalama | ünlüsüz kural | `0` | olduğu gibi |

---

## 7. TR API (`tr.py`)

```python
def hecele(kelime: str) -> list[str]: ...
def vurgu(kelime: str) -> int: ...
def vurgu_işaretle(kelime: str) -> str: ...
```

`__init__.py` export: `syllabify`, `stress`, `stress_mark`.

---

## 8. Test Stratejisi

**Akış:** SPEC → bağımsız golden (Opus, motor-körü) → motor → hakem

- `tests/golden_syllabify.py` — ~40 giriş:
  - CV/CVC/CVCC/CVCC örüntüleri
  - Üç ünsüz kümesi (Türk·çe, kart·lı)
  - Yer adı vurgusu (Ankara, İstanbul)
  - Alıntı istisnaları
  - Edge case: boş, ünlüsüz, tek hece

- `tests/test_syllabify.py` — runner + TR denklik testleri

- **Hakem:** `lexicon.load()` tüm lemmalar üzerinden 0 çökme taraması.

---

## 9. Sıralı Geliştirme Planı

Bu faz tamamlandıktan sonra sıra:
1. ✅ Hecelemleme + vurgu (`syllabify.py`) — **bu faz**
2. Yazım denetimi (`spellcheck.py`)
3. Lemmatizer (`lemmatize.py`)
4. İkileme (reduplication) morfolojisi
