# Faz 8 — Metin Normalleştirme + IPA Transkripsiyon Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** İki yeni modül: `normalization.py` (sayı/tarih/kısaltma/sembol→sözel) ve `phonology.py` (IPA transkripsiyon); TR API sarmalayıcıları ve export'lar.

**Architecture:** Saf-Python, bağımlılıksız, MIT. Her fonksiyon bağımsız; `normalize()` pipeline olarak birleştirir. SPEC→bağımsız golden(motor-körü, Opus)→motor→hakem döngüsü.

**Tech Stack:** Python 3, pytest, itertools (standart kütüphane)

**Spec:** `docs/superpowers/specs/2026-07-16-faz7-faz8-design.md` §Faz 8

---

## Dosya Haritası

| İşlem | Dosya | Sorumluluk |
|-------|-------|-----------|
| Create | `turkgram/normalization.py` | `number_to_words`, `float_to_words`, `date_to_words`, `time_to_words`, `expand_abbreviation`, `normalize` |
| Create | `turkgram/phonology.py` | `to_ipa`, `ipa_table` |
| Modify | `turkgram/tr.py` | `sayıya_çevir`, `ondalığa_çevir`, `tarihe_çevir`, `saate_çevir`, `kısaltma_aç`, `normalleştir`, `ipa` |
| Modify | `turkgram/__init__.py` | normalization + phonology export'ları |
| Create | `tests/golden_normalization.py` | Bağımsız golden — motor-körü |
| Create | `tests/test_normalization.py` | Runner |
| Create | `tests/golden_phonology.py` | Bağımsız golden — motor-körü |
| Create | `tests/test_phonology.py` | Runner |

---

## Task 1: `normalization.py` Golden (motor-körü, Opus subagent)

**Files:**
- Create: `tests/golden_normalization.py`

- [ ] **Adım 1.1: Bağımsız golden dispatch**

Opus subagent'a dispatch et: "normalization.py'yi GÖRME; yalnız spec §Faz8 ve Türkçe dilbilgisine göre bu fonksiyonlar için elle-doğrulanmış golden girdileri yaz."

Spec'ten zorunlu kapsamlar:

```python
# tests/golden_normalization.py
# Motor-körü bağımsız golden

NUMBER_WORDS = [
    # (n, beklenen)
    (0,            "sıfır"),
    (1,            "bir"),
    (10,           "on"),
    (11,           "on bir"),
    (19,           "on dokuz"),
    (100,          "yüz"),
    (101,          "yüz bir"),
    (200,          "iki yüz"),
    (1000,         "bin"),          # "bir bin" DEĞİL
    (1001,         "bin bir"),
    (2000,         "iki bin"),
    (10000,        "on bin"),
    (100000,       "yüz bin"),
    (1000000,      "bir milyon"),
    (1000001,      "bir milyon bir"),
    (-42,          "eksi kırk iki"),
    (42,           "kırk iki"),
    (2026,         "iki bin yirmi altı"),
    (999999999999, "dokuz yüz doksan dokuz milyar dokuz yüz doksan dokuz milyon dokuz yüz doksan dokuz bin dokuz yüz doksan dokuz"),
]

FLOAT_WORDS = [
    (3.14,  "üç virgül bir dört"),
    (-3.14, "eksi üç virgül bir dört"),
    (0.5,   "sıfır virgül beş"),
    (-0.5,  "eksi sıfır virgül beş"),   # negatif sıfır guard testi
]

DATE_WORDS = [
    ((15, "Temmuz", 2026), "on beş Temmuz iki bin yirmi altı"),
    ((1,  "Ocak",   2000), "bir Ocak iki bin"),
    ((1,  1,        2025), "bir Ocak iki bin yirmi beş"),  # ay int
]

TIME_WORDS = [
    ((14, 30), "on dört otuz"),
    ((9,   5), "dokuz beş"),
    ((9,   0), "dokuz"),
    ((0,   5), "sıfır beş"),
    ((0,   0), "sıfır"),
]

ABBREV = [
    ("TL",   "türk lirası"),
    ("km",   "kilometre"),
    ("%",    "yüzde"),
    ("@",    "et"),
    ("vb",   "ve benzeri"),
    ("xyz",  "xyz"),       # bilinmeyen → aynen
]

NORMALIZE = [
    ("42 km yol",   "kırk iki kilometre yol"),
    ("TL 100",      "türk lirası yüz"),
    ("merhaba",     "merhaba"),   # değişmeyen
]
```

- [ ] **Adım 1.2: Golden dosyayı kaydet** (subagent çıktısından)

---

## Task 2: `normalization.py` Implementasyon

**Files:**
- Create: `turkgram/normalization.py`

- [ ] **Adım 2.1: Dosyayı oluştur — skeleton**

```python
# turkgram/normalization.py
"""Metin normalleştirme: sayı→sözel, tarih/saat, kısaltma, IPA-öncesi pipeline."""
from __future__ import annotations
import re

_ONES = ["", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
_TENS = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]
_MONTHS = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
    7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık",
}
_MONTH_ABBR = {v.lower(): k for k, v in _MONTHS.items()}

_ABBREV_TABLE: dict[str, str] = {
    "TL": "türk lirası", "USD": "dolar", "EUR": "euro",
    "km": "kilometre", "cm": "santimetre", "m": "metre",
    "kg": "kilogram", "gr": "gram", "g": "gram",
    "m²": "metrekare", "m³": "metreküp",
    "%": "yüzde", "@": "et",
    "No": "numara", "no": "numara",
    "Dr": "doktor", "Prof": "profesör", "Öğr": "öğrenci",
    "vb": "ve benzeri", "vd": "ve diğerleri",
    "TDK": "Türk Dil Kurumu",
    "TBMM": "Türkiye Büyük Millet Meclisi",
    "TC": "Türkiye Cumhuriyeti",
    "MEB": "Millî Eğitim Bakanlığı",
    "TRT": "Türkiye Radyo ve Televizyon Kurumu",
    "BM": "Birleşmiş Milletler",
    "AB": "Avrupa Birliği",
    "NATO": "NATO",
    "TV": "televizyon",
    "PC": "bilgisayar",
    "vb.": "ve benzeri", "vd.": "ve diğerleri",
    "vs": "ve saire", "vs.": "ve saire",
    "sn": "sayın", "Sn": "sayın",
}


def _chunk_to_words(n: int) -> str:
    """0-999 arasını sözel çevirir."""
    if n == 0:
        return ""
    parts = []
    hundreds = n // 100
    remainder = n % 100
    tens = remainder // 10
    ones = remainder % 10
    if hundreds == 1:
        parts.append("yüz")
    elif hundreds > 1:
        parts.append(_ONES[hundreds] + " yüz")
    if tens:
        parts.append(_TENS[tens])
    if ones:
        parts.append(_ONES[ones])
    return " ".join(parts)


def number_to_words(n: int) -> str:
    """Tam sayıyı Türkçe sözel gösterimine çevirir."""
    if not isinstance(n, int):
        raise TypeError(f"int beklendi, {type(n).__name__} geldi")
    if n == 0:
        return "sıfır"
    if n < 0:
        return "eksi " + number_to_words(-n)
    parts = []
    trilyon = n // 1_000_000_000_000
    n %= 1_000_000_000_000
    milyar = n // 1_000_000_000
    n %= 1_000_000_000
    milyon = n // 1_000_000
    n %= 1_000_000
    bin_ = n // 1_000
    remainder = n % 1_000
    if trilyon:
        parts.append(_chunk_to_words(trilyon) + " trilyon")
    if milyar:
        parts.append(_chunk_to_words(milyar) + " milyar")
    if milyon:
        parts.append(_chunk_to_words(milyon) + " milyon")
    if bin_ == 1:
        parts.append("bin")        # "bir bin" değil "bin"
    elif bin_ > 1:
        parts.append(_chunk_to_words(bin_) + " bin")
    if remainder:
        parts.append(_chunk_to_words(remainder))
    return " ".join(parts)


def float_to_words(n: float) -> str:
    """Ondalık sayıyı Türkçe sözel gösterimine çevirir."""
    if n < 0:
        return "eksi " + float_to_words(-n)  # negatif sıfır (-0.5) guard
    s = str(n)
    if "." in s:
        int_part, dec_part = s.split(".", 1)
    else:
        int_part, dec_part = s, ""
    result = number_to_words(int(int_part))
    if dec_part:
        digits = " ".join(number_to_words(int(d)) for d in dec_part)
        result += " virgül " + digits
    return result


def date_to_words(gün: int, ay: "str | int", yıl: int) -> str:
    """Tarih bileşenlerini Türkçe sözel biçime çevirir."""
    if isinstance(ay, int):
        ay_adı = _MONTHS[ay]
    else:
        ay_lower = ay.lower()
        if ay_lower in _MONTH_ABBR:
            ay_adı = _MONTHS[_MONTH_ABBR[ay_lower]]
        else:
            ay_adı = ay  # bilinmeyeni aynen bırak
    return f"{number_to_words(gün)} {ay_adı} {number_to_words(yıl)}"


def time_to_words(saat: int, dakika: int) -> str:
    """Saat ve dakikayı Türkçe sözel biçime çevirir."""
    if dakika == 0:
        return number_to_words(saat)
    if saat == 0:
        return f"sıfır {number_to_words(dakika)}"
    return f"{number_to_words(saat)} {number_to_words(dakika)}"


def expand_abbreviation(token: str) -> str:
    """Kapalı tabloda kısaltmayı genişletir; bilinmeyen → aynen döner."""
    return _ABBREV_TABLE.get(token, _ABBREV_TABLE.get(token.upper(), token))


def normalize(text: str) -> str:
    """Token bazlı pipeline: sayı + kısaltma + sembol genişletme."""
    tokens = text.split()
    result = []
    for token in tokens:
        if re.fullmatch(r"-?\d+", token):
            result.append(number_to_words(int(token)))
        else:
            expanded = expand_abbreviation(token)
            result.append(expanded)
    return " ".join(result)
```

- [ ] **Adım 2.2: Runner yaz**

```python
# tests/test_normalization.py
import pytest
from turkgram.normalization import (
    number_to_words, float_to_words, date_to_words,
    time_to_words, expand_abbreviation, normalize,
)
from tests.golden_normalization import (
    NUMBER_WORDS, FLOAT_WORDS, DATE_WORDS, TIME_WORDS, ABBREV, NORMALIZE,
)

@pytest.mark.parametrize("n,expected", NUMBER_WORDS)
def test_number_to_words(n, expected):
    assert number_to_words(n) == expected

@pytest.mark.parametrize("n,expected", FLOAT_WORDS)
def test_float_to_words(n, expected):
    assert float_to_words(n) == expected

@pytest.mark.parametrize("args,expected", DATE_WORDS)
def test_date_to_words(args, expected):
    assert date_to_words(*args) == expected

@pytest.mark.parametrize("args,expected", TIME_WORDS)
def test_time_to_words(args, expected):
    assert time_to_words(*args) == expected

@pytest.mark.parametrize("token,expected", ABBREV)
def test_expand_abbreviation(token, expected):
    assert expand_abbreviation(token) == expected

@pytest.mark.parametrize("text,expected", NORMALIZE)
def test_normalize(text, expected):
    assert normalize(text) == expected

def test_number_to_words_type_error():
    with pytest.raises(TypeError):
        number_to_words(3.14)
```

- [ ] **Adım 2.3: Testleri çalıştır**

```
PYTHONUTF8=1 pytest tests/test_normalization.py -v
```

Beklenen: tüm testler PASS. Fail olursa golden veya implementasyon hatası — düzelt.

- [ ] **Adım 2.4: Commit**

```bash
git add turkgram/normalization.py tests/golden_normalization.py tests/test_normalization.py
git commit -m "feat(normalization): number/float/date/time/abbrev + normalize pipeline (Faz 8)"
```

---

## Task 3: `phonology.py` Golden (motor-körü, Opus subagent)

**Files:**
- Create: `tests/golden_phonology.py`

- [ ] **Adım 3.1: Bağımsız golden dispatch**

Opus subagent: "phonology.py'yi GÖRME; spec §Faz8 phonology bölümü ve standart Türkçe IPA'ya göre golden yaz."

```python
# tests/golden_phonology.py
# Motor-körü bağımsız golden — Türkçe IPA transkripsiyon

IPA_CHARS = [
    # (girdi_char, beklenen_ipa_substring)
    ("a",  "a"),
    ("b",  "b"),
    ("c",  "dʒ"),
    ("ç",  "tʃ"),
    ("d",  "d"),
    ("e",  "e"),
    ("f",  "f"),
    ("g",  "ɡ"),
    ("h",  "h"),
    ("ı",  "ɯ"),
    ("i",  "i"),
    ("j",  "ʒ"),
    ("k",  "k"),    # art-ünlü yanında
    ("l",  "l"),    # ön-ünlü yanında
    ("m",  "m"),
    ("n",  "n"),
    ("o",  "o"),
    ("ö",  "ø"),
    ("p",  "p"),
    ("r",  "ɾ"),
    ("s",  "s"),
    ("ş",  "ʃ"),
    ("t",  "t"),
    ("u",  "u"),
    ("ü",  "y"),
    ("v",  "v"),
    ("y",  "j"),
    ("z",  "z"),
]

IPA_WORDS = [
    # (sözcük, beklenen_ipa)
    ("merhaba",   "meɾhaba"),
    ("Türkiye",   "tyɾcije"),
    ("öğrenci",   "øːɾendʒi"),   # ğ → önceki ö uzar
    ("dağ",       "da"),           # kelime-sonu ğ atlanır (kapsam dışı uzama)
    ("kırk",      "kɯɾk"),        # art-ünlü: k→/k/
    ("kelime",    "celime"),       # ön-ünlü: k→/c/
    ("gül",       "ɡyl"),
    ("çay",       "tʃaj"),
    ("şeker",     "ʃeceɾ"),       # k ön-ünlü yanında → /c/
]
```

- [ ] **Adım 3.2: Golden dosyayı kaydet**

---

## Task 4: `phonology.py` Implementasyon

**Files:**
- Create: `turkgram/phonology.py`

- [ ] **Adım 4.1: Dosyayı oluştur**

```python
# turkgram/phonology.py
"""IPA transkripsiyon — karakter düzeyinde, kapsam: harf eşleme + ğ/k/l bağlam."""
from __future__ import annotations

_FRONT_VOWELS = set("eiöü")
_BACK_VOWELS  = set("aıou")
_ALL_VOWELS   = _FRONT_VOWELS | _BACK_VOWELS

_BASE: dict[str, str] = {
    "a": "a",  "b": "b",  "c": "dʒ", "ç": "tʃ",
    "d": "d",  "e": "e",  "f": "f",  "g": "ɡ",
    "h": "h",  "ı": "ɯ",  "i": "i",  "j": "ʒ",
    "k": "k",  "l": "l",  "m": "m",  "n": "n",  # k/l bağlam-duyarlı ama tabloda varsayılan
    "o": "o",  "ö": "ø",  "p": "p",  "r": "ɾ",
    "s": "s",  "ş": "ʃ",  "t": "t",  "u": "u",
    "ü": "y",  "v": "v",  "y": "j",  "z": "z",
    # ğ bağlam-duyarlı (uzama), tabloya eklenmez; to_ipa özel işler
}


def ipa_table() -> dict[str, str]:
    """Türkçe harf → IPA sembol tablosu (bağlam-bağımsız temel eşleme)."""
    return dict(_BASE)


def _neighbor_vowel(chars: list[str], idx: int) -> str | None:
    """Sol-komşu ünlü, yoksa sağ-komşu ünlü, yoksa None."""
    for i in range(idx - 1, -1, -1):
        if chars[i] in _ALL_VOWELS:
            return chars[i]
    for i in range(idx + 1, len(chars)):
        if chars[i] in _ALL_VOWELS:
            return chars[i]
    return None


def to_ipa(text: str) -> str:
    """Türkçe metin → IPA transkripsiyon dizesi."""
    chars = list(text.lower())
    result: list[str] = []
    i = 0
    while i < len(chars):
        ch = chars[i]

        # ğ: kelime-ortası → önceki ünlüyü uzat; değilse sessiz atla
        # NOT: result[-1] IPA karakteridir (ø,ɯ,...), Türkçe set'te yok.
        # Orijinal chars[i-1] ile kontrol et.
        if ch == "ğ":
            if i > 0 and chars[i - 1] in _ALL_VOWELS:
                result.append("ː")
            # kelime-sonu/başı: sessiz atlanır
            i += 1
            continue

        # k: bağlam-duyarlı
        if ch == "k":
            neighbor = _neighbor_vowel(chars, i)
            result.append("c" if neighbor in _FRONT_VOWELS else "k")
            i += 1
            continue

        # l: bağlam-duyarlı
        if ch == "l":
            neighbor = _neighbor_vowel(chars, i)
            result.append("l" if neighbor in _FRONT_VOWELS else "ɫ")
            i += 1
            continue

        if ch in _BASE:
            result.append(_BASE[ch])
        else:
            result.append(ch)  # bilinmeyen (boşluk, noktalama) aynen
        i += 1

    return "".join(result)
```

- [ ] **Adım 4.2: Runner yaz**

```python
# tests/test_phonology.py
import pytest
from turkgram.phonology import to_ipa, ipa_table
from tests.golden_phonology import IPA_CHARS, IPA_WORDS

@pytest.mark.parametrize("ch,expected_sub", IPA_CHARS)
def test_ipa_char(ch, expected_sub):
    result = to_ipa(ch)
    assert expected_sub in result, f"{ch!r} → {result!r}, beklenen {expected_sub!r}"

@pytest.mark.parametrize("word,expected", IPA_WORDS)
def test_ipa_word(word, expected):
    assert to_ipa(word) == expected

def test_ipa_table_complete():
    table = ipa_table()
    for ch in "abcçdefghıijklmnoöprsştuüvyz":
        assert ch in table or ch == "ğ", f"{ch!r} tabloda yok"
```

- [ ] **Adım 4.3: Testleri çalıştır**

```
PYTHONUTF8=1 pytest tests/test_phonology.py -v
```

Beklenen: tüm testler PASS. Fail olursa `to_ipa` mantığını düzelt.

- [ ] **Adım 4.4: Commit**

```bash
git add turkgram/phonology.py tests/golden_phonology.py tests/test_phonology.py
git commit -m "feat(phonology): to_ipa + ipa_table — karakter-düzeyi IPA transkripsiyon (Faz 8)"
```

---

## Task 5: TR API Sarmalayıcıları

**Files:**
- Modify: `turkgram/tr.py`

- [ ] **Adım 5.1: Import ve fonksiyonları ekle**

`tr.py`'nin import bölümüne ekle:
```python
from .normalization import (
    number_to_words as _nw, float_to_words as _fw,
    date_to_words as _dw, time_to_words as _tw,
    expand_abbreviation as _ea, normalize as _norm,
)
from .phonology import to_ipa as _to_ipa
```

Fonksiyonları ekle (dosyanın uygun bir yerine, diğer sarmalayıcıların yanına):
```python
def sayıya_çevir(n: int) -> str:
    return _nw(n)

def ondalığa_çevir(n: float) -> str:
    return _fw(n)

def tarihe_çevir(gün: int, ay, yıl: int) -> str:
    return _dw(gün, ay, yıl)

def saate_çevir(saat: int, dakika: int) -> str:
    return _tw(saat, dakika)

def kısaltma_aç(token: str) -> str:
    return _ea(token)

def normalleştir(text: str) -> str:
    return _norm(text)

def ipa(text: str) -> str:
    return _to_ipa(text)
```

- [ ] **Adım 5.2: TR denklik testleri**

`tests/test_normalization.py`'ye ekle (veya ayrı dosyada):
```python
import turkgram.tr as tr
from turkgram.normalization import number_to_words, normalize

def test_tr_sayiya_cevir():
    assert tr.sayıya_çevir(42) == number_to_words(42)

def test_tr_normallesir():
    assert tr.normalleştir("42 km yol") == normalize("42 km yol")

def test_tr_ipa():
    from turkgram.phonology import to_ipa
    assert tr.ipa("merhaba") == to_ipa("merhaba")
```

- [ ] **Adım 5.3: Testleri çalıştır**

```
PYTHONUTF8=1 pytest tests/test_normalization.py -v -k "tr_"
```

- [ ] **Adım 5.4: Commit**

```bash
git add turkgram/tr.py tests/test_normalization.py
git commit -m "feat(tr): sayıya_çevir/ondalığa_çevir/tarihe_çevir/saate_çevir/kısaltma_aç/normalleştir/ipa sarmalayıcılar (Faz 8)"
```

---

## Task 6: `__init__.py` Export + Tam Paket Regresyon + Hakem

**Files:**
- Modify: `turkgram/__init__.py`

- [ ] **Adım 6.1: Export ekle**

`__init__.py`'deki mevcut import bloğuna ekle:
```python
from .normalization import (
    number_to_words, float_to_words, date_to_words,
    time_to_words, expand_abbreviation, normalize,
)
from .phonology import to_ipa, ipa_table
```

- [ ] **Adım 6.2: Tam paket regresyon**

```
PYTHONUTF8=1 pytest --tb=short -q
```

Beklenen: 3600+ PASS (önceki 3564 + ~50 yeni), 0 FAIL

- [ ] **Adım 6.3: Hakem subagent**

Opus subagent: "normalization.py ve phonology.py'yi incele — 1000 için 'bin', 11 için 'on bir', ğ-uzama, k/l bağlam seçimi doğru mu? CRITICAL/HIGH/MEDIUM/LOW."

- [ ] **Adım 6.4: Final commit**

```bash
git add turkgram/__init__.py
git commit -m "feat(init): normalization + phonology export (Faz 8)"
```

- [ ] **Adım 6.5: Push**

```bash
git push
```

---

## Başarı Kriterleri

- [ ] `number_to_words(1000) == "bin"` (bir bin değil)
- [ ] `number_to_words(-42) == "eksi kırk iki"`
- [ ] `to_ipa("öğrenci")` → ğ öncesi uzama doğru
- [ ] `to_ipa("kelime")` → k önünde ön-ünlü → `/c/`
- [ ] Tam paket 3600+ PASS, 0 regresyon
- [ ] Hakem: CRITICAL/HIGH bulgu yok
