# Zincirli Türetme Analizi Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `analyze()` fonksiyonunu zincirli leksik türetmeyi çözümleyecek şekilde genişlet — `gözlükçülük` → kök `göz`, pedagojik `chain` alanı ile.

**Architecture:** BFS tabanlı `_try_derivation_chain` fonksiyonu; mevcut `_try_derivation_all` (tek katman) değişmez. `Analysis.chain` frozen tuple pedagoji ağacını taşır; `segments` düz liste geriye uyumu korur. `max_derivation_depth=1` varsayılanı sıfır kırılma garantisi verir.

**Tech Stack:** Python 3.11+, pytest, turkgram (editable install). Windows: komutlar `PYTHONUTF8=1 python` ile çalıştırılır.

---

## Dosya Haritası

| Dosya | Değişiklik türü |
|-------|----------------|
| `turkgram/derivation.py` | Modify: `-sAl` eki `_NOUN_TO_NOUN` + `_LEXICAL_SUFFIXES` + `_DERIVED_POS` |
| `turkgram/analysis.py` | Modify: `Analysis.chain` alanı; `_strip_one_layer` refactor; `_try_derivation_chain`; `_build_chain_analysis`; `analyze()` `max_derivation_depth` parametresi |
| `tests/golden_derivation_chain.py` | Create: bağımsız golden veri (motor-körü) |
| `tests/test_derivation_chain.py` | Create: test runner |
| `tools/sweep_derivation_chain.py` | Create: korpus tarama aracı |

---

## Task 1: `-sAl` Eki (Ön Koşul)

**Files:**
- Modify: `turkgram/derivation.py` (satır 34-43, 111-142, 144-180)

**Bağlam:** `_NOUN_TO_NOUN` 5-tuple `(cat, label, template, vowel_initial, produces_verb)`. `_LEXICAL_SUFFIXES` 3-tuple `(cat, label, src_pos)`. `_DERIVED_POS` dict label→pos.

- [ ] **Step 1: `_NOUN_TO_NOUN`'a `-sAl` ekle** (`turkgram/derivation.py` satır 43 sonrası)

```python
    ("isim → isim", "-sAl", "sAl", False, False),   # toplumsal, ulusal, evrensel
```

- [ ] **Step 2: `_LEXICAL_SUFFIXES`'e `-sAl` ekle** (satır ~120, diğer isim→isim eklerin sonuna)

```python
    ("isim → isim", "-sAl",  "noun"),
```

- [ ] **Step 3: `_DERIVED_POS`'a ekle** (satır ~151, `-lI` ile aynı blok)

```python
    "-sAl":  "adj",
```

- [ ] **Step 4: Manuel doğrulama**

```bash
PYTHONUTF8=1 python -c "
from turkgram.derivation import derivations
print(derivations('toplum', 'noun'))
print(derivations('evren', 'noun'))
"
```

Beklenen çıkışta `-sAl` allomorfu olan `toplumsal` ve `evrensel` görünmeli.

- [ ] **Step 5: Tam paket testi**

```bash
pytest --tb=short -q
```

Beklenen: 3651 passed (sıfır regresyon).

- [ ] **Step 6: Commit**

```bash
git add turkgram/derivation.py
git commit -m "feat(derivation): -sAl eki — toplumsal/ulusal/evrensel (zincirli türetme ön koşulu)"
```

---

## Task 2: `Analysis.chain` Alanı

**Files:**
- Modify: `turkgram/analysis.py` (satır 54-62)

**Bağlam:** `Analysis` `@dataclass(frozen=True)`. Mevcut alanlar: `lemma`, `pos`, `kind`, `kwargs`, `segments`, `hypothetical`. Yeni alan sona eklenir, varsayılan `()` → mevcut `Analysis(...)` çağrıları etkilenmez.

- [ ] **Step 1: `chain` alanını ekle**

```python
@dataclass(frozen=True)
class Analysis:
    """Tek çözümleme: kanonik kwargs, segmentasyon, hypothetical bayrağı."""
    lemma: str
    pos: str
    kind: str
    kwargs: Mapping[str, Any]
    segments: tuple[Segment, ...]
    hypothetical: bool
    chain: tuple = ()   # tuple["Analysis", ...] — pedagoji zinciri; boş = tek katman
```

- [ ] **Step 2: Tam paket testi**

```bash
pytest --tb=short -q
```

Beklenen: 3651 passed. `chain=()` varsayılanı tüm mevcut `Analysis(...)` yapıcı çağrılarını kırmaz.

- [ ] **Step 3: Commit**

```bash
git add turkgram/analysis.py
git commit -m "feat(analysis): Analysis.chain tuple alanı — pedagoji zinciri için (varsayılan boş)"
```

---

## Task 3: `_strip_one_layer` Refactoring

**Files:**
- Modify: `turkgram/analysis.py` (satır 1090-1152)

**Bağlam:** `_try_derivation_all` şu an `_LEXICAL_SUFFIXES` üzerinde dönerek `_strip_derivation(surface, label, src_pos)` çağırıyor. Bu döngü dışarı çıkarılacak — hem `_try_derivation_all` hem yeni BFS bunu kullanacak.

- [ ] **Step 1: `_strip_one_layer` fonksiyonunu ekle** (`_try_derivation_all`'ın hemen üstüne, satır ~1090)

```python
def _strip_one_layer(
    surface: str,
) -> list[tuple[str, str, str, str]]:
    """Verilen yüzeyden tek katman leksik suffix soy.

    Returns:
        List of (stem, label, suffix_surface, src_pos).
        Boş liste = hiç eşleşme yok.
    """
    from .derivation import _LEXICAL_SUFFIXES, _DERIVED_POS
    from .morphology import low_vowel

    results: list[tuple[str, str, str, str]] = []
    for (cat, label, src_pos) in _LEXICAL_SUFFIXES:
        for stem in _strip_derivation(surface, label, src_pos):
            if not stem:
                continue
            suffix_surface = surface[len(stem):]
            results.append((stem, label, suffix_surface, src_pos))
    return results
```

- [ ] **Step 2: `_try_derivation_all`'ı `_strip_one_layer` kullanacak şekilde güncelle**

Mevcut `for (cat, label, src_pos) in _LEXICAL_SUFFIXES: for stem in _strip_derivation(...)` döngüsünü şununla değiştir:

```python
def _try_derivation_all(
    surface: str,
    analyses: list,
    seen: set,
    roots: "set[str] | None" = None,
) -> None:
    """...(docstring aynı kalır)..."""
    from .derivation import _DERIVED_POS
    from .morphology import low_vowel

    for (stem, label, suffix_surface, src_pos) in _strip_one_layer(surface):
        # Fiil-kaynaklı → mastar yeniden kur (seç → seçmek)
        if src_pos == "verb":
            try:
                lemma = stem + "m" + low_vowel(stem) + "k"
            except (ValueError, IndexError):
                continue
        else:
            lemma = stem
        # §8.1 precision filtresi
        if roots is not None and lemma not in roots:
            continue
        # Oracle: derivations() ile doğrula
        from .derivation import derivations as _derivations
        try:
            derived = _derivations(lemma, src_pos)
        except Exception:
            continue
        if not derived:
            continue
        for r in derived:
            if r["form"] != surface or r["suffix"] != label:
                continue
            key = ("derivation", lemma, label)
            if key in seen:
                continue
            seen.add(key)
            derived_pos = _DERIVED_POS.get(label, "noun")
            segs = _segs_to_tuple([(stem, "kök"), (suffix_surface, label)])
            analyses.append(
                Analysis(
                    kind="derivation",
                    lemma=lemma,
                    pos=derived_pos,
                    kwargs={"suffix": label, "src_pos": src_pos},
                    segments=segs,
                    hypothetical=(roots is None),
                )
            )
```

- [ ] **Step 3: Tam paket testi**

```bash
pytest --tb=short -q
```

Beklenen: 3651 passed. Refactoring davranışı değiştirmez.

- [ ] **Step 4: Commit**

```bash
git add turkgram/analysis.py
git commit -m "refactor(analysis): _strip_one_layer — suffix döngüsü _try_derivation_all'dan çıkarıldı"
```

---

## Task 4: Bağımsız Golden (Motor-Körü)

**Files:**
- Create: `tests/golden_derivation_chain.py`

**Bağlam:** Golden SPECT + dilbilgisinden elde edilir; motor koduna BAKILMAZ. Bu aşamada motorun henüz zinciri çözemediği kabul edilir. Dispatch: "motoru/başka modülü GÖRME, yalnız SPEC + dilbilgisi."

- [ ] **Step 1: Golden dosyasını oluştur**

Dosya yalnız veri içerir (pytest toplamaz), `test_*.py` runner bunu import eder.

```python
# tests/golden_derivation_chain.py
# Bağımsız golden — motor-körü, elle doğrulanmış (SPEC + Korkmaz §134)
# Her eleman: (yüzey, beklenen_kök, zincir_uzunluğu, ara_lemmalar, roots_modu)
# roots_modu: "precision" (roots=lexicon) | "hypothetical" (roots=None)

CHAIN_CASES: list[tuple] = [
    # (yüzey, en_derin_kök, zincir_uzunluğu, [ara_lemmalar], roots_modu)

    # 2-katman precision
    ("yakınlık",        "yak",    2, ["yakın"],                "precision"),
    ("güzelleşme",      "güzel",  2, ["güzelleş"],             "precision"),
    ("toplumsal",       "toplum", 1, [],                       "precision"),   # -sAl tek katman

    # 3-katman precision
    ("gözlükçülük",     "göz",    3, ["gözlük", "gözlükçü"],  "precision"),
    ("gözlemlemek",     "göz",    3, ["gözle", "gözlem"],      "precision"),

    # 3-katman precision (ek örnek)
    # doğalcılık: doğa(-lI)→doğal(-CI)→doğalcı(-lIk)→doğalcılık
    ("doğalcılık",      "doğa",   3, ["doğal", "doğalcı"],       "precision"),
    # NOT: 4-katman örnek (işletmecilik gibi) fiilimsi (-mA) zincire karışıyor.
    # Motor tamamlandıktan sonra sweep ile doğrulanabilecek 4-katman örnek eklenecek.

    # Çatı sınırı örnekleri (precision)
    # biçimsizleştirici: biç→biçim→biçimsiz→biçimsizleş- (çatı: -tIr- dur; -IcI ulaşılamaz)
    ("biçimsizleşme",   "biç",    3, ["biçim", "biçimsiz"],   "precision"),

    # Hypothetical (roots=None): kut leksikonda olmayabilir
    ("kutsallaşmak",    "kut",    2, ["kutsal"],               "hypothetical"),

    # Regresyon: max_depth=1 → chain boş (tek katman mevcut davranış)
    ("gözlük",          "göz",    1, [],                       "precision"),   # tek katman
]

# Segmentasyon doğrulama: (yüzey, beklenen_segments ilk 2 eleman)
SEGMENTS_CASES: list[tuple] = [
    ("gözlükçülük", [("göz", "kök"), ("lük", "-lIk")]),
    ("doğalcılık", [("doğa", "kök"), ("l", "-lI")]),
]
```

- [ ] **Step 2: Golden mantığını dilbilgisiyle çapraz doğrula**

```
gözlükçülük:   göz(isim) + -lIk → gözlük + -CI → gözlükçü + -lIk → gözlükçülük   ✓ 3 katman
gözlemlemek:   göz(isim) + -lA- → gözlemek + -Im → gözlem(isim) + -lA- → gözlemlemek  ✓ 3 katman
doğalcılık:    doğa(isim) + -lI → doğal(sıf) + -CI → doğalcı(isim) + -lIk → doğalcılık  ✓ 3 katman
biçimsizleşme: biç(fiil) + -Im → biçim(isim) + -sIz → biçimsiz(sıf) + -lAş- → biçimsizleşmek ✓ 3 katman
```

Not: 4-katman temiz örnek zincir ortasında fiilimsi gerektirdiğinden kapsam dışı. Motor tamamlandıktan sonra sweep ile gerçek 4-katman örnekler tespit edilecek.

- [ ] **Step 3: Commit**

```bash
git add tests/golden_derivation_chain.py
git commit -m "test(golden): zincirli türetme golden — motor-körü bağımsız (Spec §10)"
```

---

## Task 5: `_try_derivation_chain` + `_build_chain_analysis`

**Files:**
- Modify: `turkgram/analysis.py`

**Bağlam:** BFS. `seen` anahtarı `("derivation_chain", surface, chain_key)` tuple — `Analysis` nesnesi değil (mevcut `seen` ile çakışmaz). Döngü tespiti: `stem` hem `chain_so_far` lemmaları hem gövdeleri ile karşılaştırılır.

- [ ] **Step 1: `_build_chain_analysis` yardımcısını ekle** (`_try_derivation_all`'ın altına)

```python
def _build_chain_analysis(
    surface: str,
    chain: list,   # list[Analysis], en içten dışa: [kök_analizi, ..., üst_analiz]
    top_label: str,
    top_suffix_surface: str,
    top_src_pos: str,
    top_pos: str,
    top_lemma: str,
    hypothetical: bool,
) -> Analysis:
    """BFS zincirinden Analysis üret.

    segments: tüm katmanların segmentleri art arda düzleştirilir.
    chain: iç içe Analysis tuple (en içteki = kök, boş chain = kök).
    """
    from .derivation import _DERIVED_POS

    # Düz segments: chain'deki tüm segmentler + bu katmanın suffix'i
    # chain[0] = en derin kök analizi, chain[-1] = bir önceki (dış) katman
    # "chain boş" → BFS henüz ilk katmanda; bu durum _try_derivation_chain'de
    #   en az 2 katman garantisi olduğundan üretim aşamasında oluşmaz.
    stem_surface = surface[: len(surface) - len(top_suffix_surface)]
    flat_segs: list[tuple[str, str]] = []
    if chain:
        for a in chain:
            flat_segs.extend(list(a.segments))
        flat_segs.append((stem_surface, top_label))   # bu katmanın gövde kısmı
        flat_segs.append((top_suffix_surface, top_label))  # bu katmanın suffix'i
    else:
        flat_segs = [(stem_surface, "kök"), (top_suffix_surface, top_label)]

    return Analysis(
        kind="derivation",
        lemma=top_lemma,
        pos=top_pos,
        kwargs={"suffix": top_label, "src_pos": top_src_pos},
        segments=_segs_to_tuple(flat_segs),
        hypothetical=hypothetical,
        chain=tuple(chain),
    )
```

- [ ] **Step 2: `_try_derivation_chain` fonksiyonunu ekle** (`_build_chain_analysis`'ın altına)

```python
def _try_derivation_chain(
    surface: str,
    analyses: list,
    seen: set,
    roots: "set[str] | None" = None,
    max_depth: int = 5,
) -> None:
    """Zincirli leksik türetme analizi — BFS, max_depth katmana kadar.

    Tek katman (_try_derivation_all) sonuçlarını tekrar üretmez (min 2 katman).
    seen anahtarı: ("derivation_chain", surface, chain_key) — mevcut seen ile çakışmaz.
    Döngü tespiti: stem, chain_so_far'daki tüm lemma ve gövdelerle karşılaştırılır.
    Çatı ekleri _LEXICAL_SUFFIXES dışında olduğundan otomatik dışlanır.
    """
    from collections import deque
    from .derivation import _DERIVED_POS
    from .morphology import low_vowel

    if max_depth < 2:
        return

    # queue: (kalan_yüzey, zincir [Analysis listesi], kalan_derinlik)
    # ZİNCİR YÖN TANIMI: chain[0] = en derin kök (ilk soyulan katman),
    #   chain[-1] = yüzeye en yakın katman.
    # Spec §4'teki iç-içe ağaç gösterimi farklıdır; burada düz liste kullanılır.
    # Test runner da chain[0].lemma == expected_root ile doğrular (tutarlı).
    queue: deque = deque([(surface, [], max_depth)])

    while queue:
        current, chain_so_far, depth = queue.popleft()

        if depth == 0:
            continue

        for (stem, label, suffix_surface, src_pos) in _strip_one_layer(current):
            # Fiil-kaynaklı → mastar yeniden kur
            if src_pos == "verb":
                try:
                    lemma = stem + "m" + low_vowel(stem) + "k"
                except (ValueError, IndexError):
                    continue
            else:
                lemma = stem

            # Döngü tespiti: stem + lemma her ikisi de kontrol (fiil vs mastar farkı)
            chain_lemmas = {a.lemma for a in chain_so_far}
            chain_stems = set()
            for a in chain_so_far:
                chain_stems.add(a.lemma)
                if a.kwargs.get("src_pos") == "verb" and a.lemma.endswith(("mak", "mek")):
                    chain_stems.add(a.lemma[:-3])  # yaklaşık gövde
            if stem in chain_lemmas or lemma in chain_lemmas or stem in chain_stems:
                continue

            # Precision kontrolü
            is_hypothetical = (roots is not None and lemma not in roots)
            if roots is not None and lemma not in roots:
                # Hypothetical intermediate → zinciri sürdür ama işaretle
                pass  # hypothetical=True ile devam

            # Oracle doğrulama
            from .derivation import derivations as _derivations
            try:
                derived = _derivations(lemma, src_pos)
            except Exception:
                continue
            oracle_ok = any(
                r["form"] == current and r["suffix"] == label
                for r in (derived or [])
            )
            if not oracle_ok:
                continue

            # Yeni chain: mevcut zincire bu katmanı ekle
            derived_pos = _DERIVED_POS.get(label, "noun")
            leaf = Analysis(
                kind="derivation",
                lemma=lemma,
                pos=derived_pos,
                kwargs={"suffix": label, "src_pos": src_pos},
                segments=_segs_to_tuple([(stem, "kök"), (suffix_surface, label)]),
                hypothetical=is_hypothetical,
            )
            new_chain = [leaf] + chain_so_far  # leaf = bu katman (içten dışa)

            # Zincir en az 2 katmansa → tam analiz üret
            if len(new_chain) >= 2:
                chain_key = tuple(a.lemma for a in new_chain)
                seen_key = ("derivation_chain", surface, chain_key)
                if seen_key not in seen:
                    seen.add(seen_key)
                    top = _build_chain_analysis(
                        surface=surface,
                        chain=new_chain,
                        top_label=label,
                        top_suffix_surface=suffix_surface,
                        top_src_pos=src_pos,
                        top_pos=derived_pos,
                        top_lemma=lemma,
                        hypothetical=is_hypothetical or (roots is None),
                    )
                    analyses.append(top)

            # Daha derin araştır
            queue.append((stem, new_chain, depth - 1))
```

- [ ] **Step 3: Tam paket testi** (henüz `analyze()` bağlı değil, import testi)

```bash
pytest --tb=short -q
```

Beklenen: 3651 passed.

- [ ] **Step 4: Commit**

```bash
git add turkgram/analysis.py
git commit -m "feat(analysis): _try_derivation_chain BFS + _build_chain_analysis"
```

---

## Task 6: `analyze()` Entegrasyonu

**Files:**
- Modify: `turkgram/analysis.py` (satır 833-834 ve ~915)

**Bağlam:** Mevcut imza: `def analyze(surface: str, pos: str | None = None, *, roots: Collection[str] | None = None)`. Yeni keyword-only parametre eklenir.

- [ ] **Step 1: `analyze()` imzasını güncelle**

```python
def analyze(
    surface: str,
    pos: str | None = None,
    *,
    roots: Collection[str] | None = None,
    max_derivation_depth: int = 1,
) -> list[Analysis]:
```

Docstring'e ekle:
```
        max_derivation_depth: Zincirli türetme derinliği. 1=tek katman (varsayılan,
            mevcut davranış). 2+ → _try_derivation_chain devreye girer. Araştırma
            modu için 10+ verilebilir.
```

- [ ] **Step 2: `_try_derivation_chain` çağrısını ekle** (satır ~915, `_try_derivation_all` çağrısının hemen altına)

```python
        _try_derivation_all(surface_token, analyses, seen, roots=roots)
        if max_derivation_depth >= 2:
            _try_derivation_chain(
                surface_token, analyses, seen,
                roots=roots, max_depth=max_derivation_depth,
            )
```

- [ ] **Step 3: Tam paket testi**

```bash
pytest --tb=short -q
```

Beklenen: 3651 passed.

- [ ] **Step 4: Hızlı manuel doğrulama**

```bash
PYTHONUTF8=1 python -c "
from turkgram import analyze
from turkgram.lexicon import load

roots = load()
results = analyze('gözlükçülük', roots=roots, max_derivation_depth=5)
for r in results:
    if r.kind == 'derivation' and r.chain:
        print(r.lemma, '->', [a.lemma for a in r.chain])
"
```

Beklenen çıktı: `göz -> [Analysis(gözlük...), Analysis(gözlükçü...)]` benzeri zincir.

- [ ] **Step 5: Commit**

```bash
git add turkgram/analysis.py
git commit -m "feat(analysis): analyze() max_derivation_depth parametresi — zincirli türetme etkinleştirildi"
```

---

## Task 7: Test Runner

**Files:**
- Create: `tests/test_derivation_chain.py`

- [ ] **Step 1: Runner dosyasını oluştur**

```python
"""test_derivation_chain.py — zincirli türetme analizi runner."""
import pytest
from turkgram import analyze
from turkgram.lexicon import load as _load_lex

from .golden_derivation_chain import CHAIN_CASES, SEGMENTS_CASES

_ROOTS = _load_lex()


def _get_chain_result(surface: str, roots_modu: str) -> list:
    """max_depth=5 ile zincirli analiz; kind=derivation, chain dolu sonuçları döndür."""
    roots = _ROOTS if roots_modu == "precision" else None
    results = analyze(surface, roots=roots, max_derivation_depth=5)
    return [r for r in results if r.kind == "derivation" and r.chain]


@pytest.mark.parametrize(
    "surface,expected_root,chain_len,intermediate,roots_modu",
    CHAIN_CASES,
)
def test_chain_root(surface, expected_root, chain_len, intermediate, roots_modu):
    """En derin kök ve zincir uzunluğunu doğrula."""
    results = _get_chain_result(surface, roots_modu)
    assert results, f"{surface!r} için zincirli analiz bulunamadı"
    # En derin köke ulaşan sonucu bul
    found = [r for r in results if r.chain and r.chain[0].lemma == expected_root]
    assert found, (
        f"{surface!r} için kök={expected_root!r} bulunamadı. "
        f"Bulunan kökler: {[r.chain[0].lemma for r in results if r.chain]}"
    )
    best = found[0]
    assert len(best.chain) == chain_len, (
        f"Zincir uzunluğu: beklenen {chain_len}, bulunan {len(best.chain)}"
    )
    for lemma in intermediate:
        chain_lemmas = [a.lemma for a in best.chain]
        assert lemma in chain_lemmas, (
            f"Ara lemma {lemma!r} zincirde yok: {chain_lemmas}"
        )


def test_regression_max_depth_1():
    """max_depth=1 → chain boş (mevcut davranış korunur)."""
    results = analyze("gözlükçülük", roots=_ROOTS, max_derivation_depth=1)
    chain_results = [r for r in results if r.kind == "derivation" and r.chain]
    assert chain_results == [], "max_depth=1'de chain dolu olmamalı"


@pytest.mark.parametrize("surface,expected_first_two", SEGMENTS_CASES)
def test_segments_flat(surface, expected_first_two):
    """Düz segments geriye uyum: ilk iki segment beklenenle eşleşmeli."""
    results = _get_chain_result(surface, "precision")
    assert results, f"{surface!r} için sonuç yok"
    segs = list(results[0].segments)
    for i, (text, label) in enumerate(expected_first_two):
        assert segs[i][0] == text and segs[i][1] == label, (
            f"segments[{i}]: beklenen ({text!r},{label!r}), bulunan {segs[i]}"
        )


def test_sal_single_layer():
    """-sAl eki tek katman analizi çalışıyor."""
    results = analyze("toplumsal", roots=_ROOTS)
    deriv = [r for r in results if r.kind == "derivation"]
    assert any(r.lemma == "toplum" for r in deriv), "toplumsal → toplum bulunamadı"
```

- [ ] **Step 2: Testleri çalıştır**

```bash
pytest tests/test_derivation_chain.py -v
```

Beklenen: tüm testler geçer.

- [ ] **Step 3: Tam paket testi**

```bash
pytest --tb=short -q
```

Beklenen: 3651 + yeni testler passed.

- [ ] **Step 4: Commit**

```bash
git add tests/golden_derivation_chain.py tests/test_derivation_chain.py
git commit -m "test(derivation-chain): runner + golden — zincirli türetme testleri"
```

---

## Task 8: Korpus Tarama + Hakem

**Files:**
- Create: `tools/sweep_derivation_chain.py`

- [ ] **Step 1: Tarama aracını oluştur**

```python
"""sweep_derivation_chain.py — zincirli türetme corpus taraması.

Leksikon 26k lemma × max_depth=3: 0 çökme kontrolü.
Kullanım: PYTHONUTF8=1 python tools/sweep_derivation_chain.py
"""
import sys
from turkgram import analyze
from turkgram.lexicon import load

def main():
    roots = load()
    lemmas = sorted(roots)
    total = len(lemmas)
    errors = []
    chain_found = 0

    print(f"Taranıyor: {total} lemma × max_depth=3 ...", flush=True)
    for i, lemma in enumerate(lemmas):
        if i % 2000 == 0:
            print(f"  {i}/{total} ({100*i//total}%)", flush=True)
        try:
            results = analyze(lemma, roots=roots, max_derivation_depth=3)
            chain_results = [r for r in results if r.kind == "derivation" and r.chain]
            chain_found += len(chain_results)
        except Exception as e:
            errors.append((lemma, str(e)))

    print(f"\nSonuç: {total} lemma tarandı")
    print(f"  Çökme: {len(errors)}")
    print(f"  Zincirli analiz bulunan: {chain_found}")
    if errors:
        print("\nHATALAR:")
        for lemma, err in errors[:20]:
            print(f"  {lemma}: {err}")
        sys.exit(1)
    else:
        print("OK — 0 çökme")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Taramayı çalıştır**

```bash
PYTHONUTF8=1 python tools/sweep_derivation_chain.py
```

Beklenen: `0 çökme`.

- [ ] **Step 3: Tam paket testi (son kontrol)**

```bash
pytest --tb=short -q
```

Beklenen: tüm testler yeşil.

- [ ] **Step 4: Son commit**

```bash
git add tools/sweep_derivation_chain.py
git commit -m "feat(analysis): zincirli türetme analizi tamamlandı — BFS, chain, -sAl, max_derivation_depth"
```

---

## Notlar

**`işletmecilik` zinciri dikkat:** `iş → işlemek (-lA-) → işletme (fiilimsi -mA, kapsam dışı!) → işletmeci → işletmecilik`. Aradaki `-mA` fiilimsi olduğundan motor bu zinciri tam göremez. Golden Task 4 Step 2'de temiz 4-katman örnek bulunmalı.

**`biçimsizleştirici` zinciri dikkat:** `-IcI` çatı eki değil leksik ektir; ama `-tIr-` (ettirgen) çatı öncesindedir ve leksikonda `biçimsizleştirmek` varsa motor `-IcI`'yı bulabilir. Test bunu ayrıca doğrular.

**`seen` çakışma güvencesi:** Mevcut `("derivation", lemma, label)` anahtarları ile yeni `("derivation_chain", surface, chain_key)` anahtarları `"derivation"` ≠ `"derivation_chain"` farkıyla hiç çakışmaz.
