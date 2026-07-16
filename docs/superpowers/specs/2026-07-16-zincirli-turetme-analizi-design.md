# Zincirli Türetme Analizi — Tasarım Dokümanı

**Tarih:** 2026-07-16  
**Durum:** Onaylı  
**Referans:** CLAUDE.md §6 (Faz 6 tek-katman emsali), Korkmaz §134 (üst üste yapım ekleri)

---

## 1. Amaç

`analyze()` fonksiyonunu zincirli leksik türetmeyi çözümleyecek şekilde genişletmek:

1. **Derin kök bulma:** `gözlükçülük` → kök `göz` (3 katman türetme)
2. **Pedagojik zincir:** `Analysis.chain` alanıyla türetme ağacı

**Kapsam dışı:** Fiilimsi (-mAk/-mA/-Iş), çatı ekleri (-DIr/-Il/-In/-Iş; ettirgen/edilgen/dönüşlü/işteş). Zincir ortasında çatı ekine rastlandığında **çatı sınırında durulur**, daha derine gidilmez. `-IcI` gibi leksik ekler çatı değildir ve zincire dahildir.

---

## 2. Dilbilgisel Zemin

Korkmaz (Türkiye Türkçesi Grameri, s. 134):

> "Hatta bu gövdeler gör-üş-tür-ül-mek, iş+le-t-me+ci+lik, yak+ın+lık örneklerindeki gibi belirli birleşme kuralları çerçevesinde **üst üste getirilmiş yapım ekleri** de alabilirler."

Gerçekçi örneklerdeki maksimum derinlik:

| Kelime | Zincir | Leksik katman |
|--------|--------|--------------|
| yakınlık | yak→yakın→yakınlık | 2 |
| gözlükçülük | göz→gözlük→gözlükçü→gözlükçülük | 3 |
| gözlemlemek | göz→gözle-→gözlem→gözlemle-→gözlemlemek | 3 |
| işletmecilik | iş→işle-→işletme→işletmeci→işletmecilik | 4 |

Teorik maksimum: **5 katman**. Varsayılan üst sınır 5, override edilebilir (araştırma modu için `10+`).

---

## 3. Ön Koşul: `-sAl` Eki

`_LEXICAL_SUFFIXES`'e eksik bir isim→sıfat eki eklenir:

```python
("isim → isim", "-sAl", "noun"),   # toplumsal, ulusal, evrensel, duygusal
```

`_DERIVED_POS`'a: `"-sAl": "adj"` (kategori etiketi `"isim → isim"` olsa da çıktı POS sıfat; `-lI`/`-sIz`/`-CIl`/`-CA` ile aynı pattern).

**Neden şimdi:** `-sAl` olmadan `kut→kutsal→kutsallaş-` gibi zincirler sessizce yarıda kesilir. Faz 6 motoru değişmez, yalnız suffix listesi genişler.

---

## 4. Veri Yapısı

`Analysis` nesnesine yeni opsiyonel alan (`analysis.py`):

```python
@dataclass(frozen=True)
class Analysis:
    # ... mevcut alanlar (değişmez) ...
    chain: tuple = ()   # tuple[Analysis, ...] — pedagoji zinciri; boş = tek katman
```

`Analysis` frozen dataclass olduğundan `chain` içindeki iç içe `Analysis` nesneleri de hashlenebilir — `set` kullanımında sorun yok.

### Düz `segments` (geriye uyum)

Tüm katmanların segmentleri art arda düzleştirilir:

```
gözlükçülük →
  [("göz", "kök"), ("lük", "isim→isim:-lIk"), ("çü", "isim→isim:-CI"), ("lük", "isim→isim:-lIk")]
```

### `chain` (pedagoji ağacı)

İç içe `Analysis` nesneleri — en içteki = kök, en dıştaki = yüzey:

```
Analysis(lemma="gözlükçülük", kind="derivation", chain=(
  Analysis(lemma="gözlükçü", kind="derivation", chain=(
    Analysis(lemma="gözlük", kind="derivation", chain=(
      Analysis(lemma="göz", kind="derivation", chain=())
    ))
  ))
))
```

`chain=()` → tek katman veya kök (mevcut davranış); mevcut tüm çağrılar etkilenmez.

---

## 5. İç Yardımcı: `_strip_one_layer`

Mevcut `_try_derivation_all` içindeki suffix döngüsü **ayrı bir fonksiyona çıkarılır** (refactoring):

```python
def _strip_one_layer(
    surface: str,
) -> list[tuple[str, str, str, str]]:
    """
    Verilen yüzeyden tek katman suffix soyar.
    Döndürür: [(stem, label, suffix_surface, src_pos), ...]
    Her eleman bir (kök_adayı, ek_etiketi, yüzey_ek, kaynak_POS) dörtlüsü.
    """
```

`_try_derivation_all` bu fonksiyonu çağırır — davranışı değişmez, yalnız döngü dışarı alınır.  
`_try_derivation_chain` de aynı fonksiyonu kullanır — kod tekrarı yok.

---

## 6. Algoritma: `_try_derivation_chain` (BFS)

`analysis.py`'e yeni fonksiyon, `_try_derivation_all`'ın yanına:

```python
def _try_derivation_chain(
    surface: str,
    analyses: list,
    seen: set,
    roots: set | None,
    max_depth: int = 5,
) -> None:
```

**BFS akışı:**

```python
from collections import deque

queue = deque([(surface, [], max_depth)])
# her eleman: (kalan_yüzey, [Analysis, ...] zincir, kalan_derinlik)

while queue:
    current, chain_so_far, depth = queue.popleft()

    if depth == 0:
        continue

    for (stem, label, suffix_surface, src_pos) in _strip_one_layer(current):

        # Döngü tespiti: stem VE lemma her ikisi de kontrol edilir.
        # (fiil→isim zincirinde stem="seç" ama chain'deki lemma="seçmek" olabilir)
        chain_lemmas = {a.lemma for a in chain_so_far}
        chain_stems = {a.kwargs.get("_stem", a.lemma) for a in chain_so_far}
        if stem in chain_lemmas or stem in chain_stems:
            continue

        # Precision kontrolü (Bölüm 7)
        is_hypothetical = (roots is not None and stem not in roots)

        leaf = _make_derivation_analysis(stem, label, src_pos,
                                         hypothetical=is_hypothetical)
        new_chain = chain_so_far + [leaf]

        # seen anahtarı: tuple (kind, surface, chain_key) — Analysis nesnesi değil
        chain_key = tuple(a.lemma for a in new_chain)
        seen_key = ("derivation_chain", surface, chain_key)
        if seen_key not in seen:
            seen.add(seen_key)
            top = _build_chain_analysis(surface, new_chain, label, suffix_surface)
            analyses.append(top)

        # Daha derin araştır
        queue.append((stem, new_chain, depth - 1))
```

`_build_chain_analysis(surface, chain, last_label, last_suffix)` → düz `segments` (tüm katmanlar) + `chain` tuple'ını birleştirerek `Analysis` üretir.

**`_try_derivation_all` değişmez** — tek katman olarak çalışmaya devam eder; `seen` anahtarları çakışmaz (BFS `"derivation_chain"` prefix'i kullanır).

---

## 7. Precision / Recall (C Modu)

### `roots` verilince (precision)

Her intermediate kök `roots`'ta olmalı. Zincir kırılma davranışı:

| Durum | Davranış |
|-------|----------|
| `göz` ∈ roots **ve** `gözlük` ∈ roots | Tam zincir üretilir, `hypothetical=False` |
| `gözlük` ∈ roots, `göz` ∉ roots | `gözlük` katmanında zincir kesilir (`hypothetical=True` olan `göz`'e inilmez — BFS o dalı sürdürür ama `hypothetical=True` kalır) |
| `gözlük` ∉ roots | O dal tamamen atlanır |

**Önemli:** `roots` filtresi intermediate kök için uygulanır. `hypothetical=True` olan analizler listeye eklenir ama işaretlidir — çağıran isterse filtreleyebilir.

### `roots=None` (hypothetical)

Tüm intermediate kökler kabul edilir, `hypothetical=True` ile işaretlenir.  
§8.1 emsali: yanlış pozitifler çağıranın sorumluluğunda.

---

## 8. `analyze()` İmzası

```python
def analyze(
    surface: str,
    roots: set | None = None,
    pos: str | None = None,
    max_derivation_depth: int = 1,   # YENİ — default 1 = mevcut davranış
) -> list[Analysis]:
```

- `max_derivation_depth=1` → yalnız `_try_derivation_all` (mevcut, kırılma yok)
- `max_derivation_depth=2+` → `_try_derivation_chain` ek olarak devreye girer
- `max_derivation_depth=5` → varsayılan "tam" mod
- Daha yüksek değer (ör. `10`) → teorik/araştırma modu

**Geriye tam uyumlu:** Mevcut 3651 test `max_derivation_depth=1` varsayılanıyla hiç değişmez.

---

## 9. Çatı Sınırı

Zincir ortasında çatı eki (`-DIr`/`-Il`/`-In`/`-Iş`) gelince **durulur**. `-IcI` gibi leksik ekler çatı değildir, zincire dahildir.

| Kelime | Motorun görebildiği zincir | Nerede durur |
|--------|---------------------------|-------------|
| biçimsizleştirici | biç→biçim→biçimsiz→biçimsizleş-→biçimsizleştirici | `-tIr-` (ettirgen) çatı; `-IcI` leksik olduğundan ondan önceki `biçimsizleştir-` gövdesine ulaşılamaz |
| kutsallaştırılmak | kut→kutsal→kutsallaş- | `-tIr-` (ettirgen) çatı sınırı |

`_strip_one_layer` zaten `_LEXICAL_SUFFIXES` dışını denemez — çatı otomatik dışarıda kalır.

**Not — `kut` leksikonda olmayabilir:** `kut` arkaik bir kök; `lexicon.load()` içermeyebilir. Precision modda bu dal `hypothetical=True` döner. Golden'da `roots=None` ile test edilmeli.

---

## 10. Test Stratejisi

### `tests/golden_derivation_chain.py` (bağımsız, motor-körü, Opus)

| Yüzey | Beklenen en derin kök | Zincir derinliği | Mod |
|-------|----------------------|-----------------|-----|
| `gözlükçülük` | `göz` | 3 | precision (`roots` ile) |
| `işletmecilik` | `iş` | 4 | precision |
| `yakınlık` | `yak` | 2 | precision |
| `gözlemlemek` | `göz` | 3 | precision |
| `güzelleştirme` | `güzel` | 2 | precision |
| `biçimsizleştirici` | `biç` | 4 (çatı öncesi son leksik) | precision |
| `kutsallaştırılmak` | `kut` (hypothetical) | 2 | `roots=None` |
| `görüştürülmek` | `gör` (hypothetical) | — | `roots=None` |

Golden doğrulama:
- `analysis.lemma` (en derin kök)
- `len(analysis.chain)` (zincir uzunluğu)
- `analysis.chain[i].lemma` (ara kökler)
- `analysis.segments` (düz liste, geriye uyum)
- `analysis.hypothetical` (precision/hypothetical bayrağı)

### `tests/test_derivation_chain.py`

- Precision testleri: `roots=lexicon.load()`, `max_derivation_depth=5`
- Hypothetical testleri: `roots=None`, `max_derivation_depth=4`
- Regresyon kilidi: `max_derivation_depth=1` → `chain == ()` (tüm mevcut analizler etkilenmez)
- `-sAl` eki: `toplumsal`, `evrensel` tek katman doğrulaması

### Hakem taraması

```
leksikon 26k lemma × max_derivation_depth=3, roots=lexicon.load() → 0 çökme
```

Roots filtreli → kombinasyon patlaması yok. `roots=None` taraması yapılmaz (precision dışı).

---

## 11. Dosya Değişiklikleri

| Dosya | Değişiklik |
|-------|-----------|
| `turkgram/derivation.py` | `_LEXICAL_SUFFIXES`'e `-sAl` + `_DERIVED_POS`'a `adj` |
| `turkgram/analysis.py` | `_strip_one_layer` (refactoring: `_try_derivation_all`'dan çıkarılır) |
| `turkgram/analysis.py` | `Analysis.chain: tuple = ()` alanı |
| `turkgram/analysis.py` | `_try_derivation_chain`, `_build_chain_analysis`, `_make_derivation_analysis` |
| `turkgram/analysis.py` | `analyze()` `max_derivation_depth` parametresi |
| `tests/golden_derivation_chain.py` | Bağımsız golden (motor-körü, Opus) |
| `tests/test_derivation_chain.py` | Runner |
| `tools/sweep_derivation_chain.py` | Korpus tarama aracı |
