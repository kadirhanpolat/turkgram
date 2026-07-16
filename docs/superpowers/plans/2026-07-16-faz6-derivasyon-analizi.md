# Faz 6 — Derivasyon Analizi Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `derivation.py`'ye `_LEXICAL_SUFFIXES` + `_DERIVED_POS` sabitleri ekle; `analysis.py`'ye `_try_derivation_all` + `_strip_derivation` fonksiyonlarıyla `kind="derivation"` desteği ekle; mevcut `türet()` ve `derivations` export değişmeden kalır.

**Architecture:** Oracle analysis-by-generation deseni (`_try_number_all` emsali). Her leksik suffix için yüzey → ters harmoni → root adayları → `derivations(root, src_pos)` oracle doğrulama → `form == surface` şartı. `_LEXICAL_SUFFIXES` fiilimsi ve çatı eklerini dışlar; exclusion `(category, label)` çiftiyle yapılır (−Ar− çakışması için kritik).

**Tech Stack:** Python 3.10+, pytest; harici bağımlılık yok. Tüm harmoni yardımcıları `morphology.py`'den.

**Spec:** `docs/superpowers/specs/2026-07-16-faz6-derivasyon-design.md`

---

## Değişen Dosyalar

| Dosya | İşlem |
|---|---|
| `turkgram/derivation.py` | `_LEXICAL_SUFFIXES`, `_DERIVED_POS` sabitleri eklenir; `derivations()` dokunulmaz |
| `turkgram/analysis.py` | `_strip_derivation`, `_try_derivation_all` eklenir; `_KINDS` + `analyze()` güncellenir |
| `tests/golden_derivation_analysis.py` | Yeni — bağımsız analiz golden (motor-körü; elle veya Opus) |
| `tests/test_derivation_analysis.py` | Yeni — analiz runner |
| `tests/test_derivation.py` | Mevcut — `_LEXICAL_SUFFIXES` + `_DERIVED_POS` testleri eklenir |

**Dokunulmayan dosyalar:** `turkgram/tr.py` (`türet()` zaten var), `turkgram/__init__.py` (`derivations` zaten export'ta).

---

## Task 1: `derivation.py` — `_LEXICAL_SUFFIXES` + `_DERIVED_POS`

**Files:**
- Modify: `turkgram/derivation.py` (mevcut sabitlerin altına, `derivations()` fonksiyonunun üstüne)
- Test: `tests/test_derivation.py`

- [ ] **Step 1: `test_derivation.py`'ye yeni testler ekle (önce yaz — FAIL beklenir)**

`tests/test_derivation.py` sonuna ekle:

```python
from turkgram.derivation import _LEXICAL_SUFFIXES, _DERIVED_POS


def test_lexical_suffixes_structure():
    """Her eleman (category, label, src_pos) üçlüsü olmalı."""
    for item in _LEXICAL_SUFFIXES:
        assert len(item) == 3, f"Beklenen 3-tuple, alınan: {item}"
        cat, label, src_pos = item
        assert src_pos in ("noun", "verb"), f"Geçersiz src_pos: {src_pos}"


def test_lexical_suffixes_fiilimsi_excluded():
    """Fiilimsi ekleri _LEXICAL_SUFFIXES'te OLMAMALI."""
    excluded_labels = {"-mA", "-Iş", "-An", "-mAz", "-DIk", "-AcAk", "-mIş",
                       "-AsI", "-ArAk", "-Ip", "-IncA", "-mAdAn", "-AlI", "-DIkçA"}
    labels_in = {label for (_, label, _) in _LEXICAL_SUFFIXES}
    overlap = excluded_labels & labels_in
    assert not overlap, f"Fiilimsi ekleri dışlanmalı: {overlap}"


def test_lexical_suffixes_voice_excluded():
    """Çatı ekleri (fiil→fiil) _LEXICAL_SUFFIXES'te OLMAMALI."""
    voice_cats = {"fiil → fiil (çatı)"}
    cats_in = {cat for (cat, _, _) in _LEXICAL_SUFFIXES}
    assert not (voice_cats & cats_in), "Çatı kategorisi dışlanmalı"


def test_ar_collision_resolution():
    """-Ar- yalnız isim→fiil olarak dahil, fiil→fiil(çatı) dışarıda."""
    ar_entries = [(cat, label) for (cat, label, _) in _LEXICAL_SUFFIXES
                  if "-Ar-" in label or "-Ar" == label]
    for cat, label in ar_entries:
        assert cat == "isim → fiil", f"-Ar- yalnız isim→fiil'de olmalı: ({cat}, {label})"


def test_derived_pos_adj_suffixes():
    """-lI, -sIz, -CIl, -IcI, -gAn, -Ik vb. sıfat üretmeli."""
    adj_suffixes = {"-lI", "-sIz", "-CIl", "-CA", "-IcI", "-gAn", "-Ik", "-gIn"}
    for sfx in adj_suffixes:
        assert _DERIVED_POS.get(sfx) == "adj", f"{sfx} → 'adj' olmalı, alınan: {_DERIVED_POS.get(sfx)}"


def test_derived_pos_covers_all_lexical():
    """_LEXICAL_SUFFIXES'teki her label _DERIVED_POS'ta olmalı."""
    missing = [label for (_, label, _) in _LEXICAL_SUFFIXES if label not in _DERIVED_POS]
    assert not missing, f"_DERIVED_POS'ta eksik label'lar: {missing}"
```

- [ ] **Step 2: Testleri çalıştır — ImportError / AttributeError beklenir**

```
PYTHONUTF8=1 python -m pytest tests/test_derivation.py::test_lexical_suffixes_structure tests/test_derivation.py::test_derived_pos_covers_all_lexical -v
```

Beklenen: `ImportError: cannot import name '_LEXICAL_SUFFIXES'`

- [ ] **Step 3: `derivation.py`'ye `_LEXICAL_SUFFIXES` + `_DERIVED_POS` ekle**

`derivation.py`'de `_FIILIMSI` tanımının altına, `_expand` fonksiyonunun üstüne ekle:

```python
# ── Analiz için leksik suffix kümesi (fiilimsi + çatı DIŞLANMIŞ) ────────────
# Her eleman: (category, label, src_pos)
# Exclusion (category, label) çiftiyle yapılır — -Ar- çakışmasını doğru çözer:
#   ("isim → fiil", "-Ar-") DAHİL; ("fiil → fiil (çatı)", "-Ar- (ettirgen)") DIŞLI.
_LEXICAL_SUFFIXES: tuple[tuple[str, str, str], ...] = (
    # isim → isim
    ("isim → isim", "-lIk",  "noun"),
    ("isim → isim", "-CI",   "noun"),
    ("isim → isim", "-lI",   "noun"),
    ("isim → isim", "-sIz",  "noun"),
    ("isim → isim", "-CIk",  "noun"),
    ("isim → isim", "-DAş",  "noun"),
    ("isim → isim", "-CA",   "noun"),
    ("isim → isim", "-CIl",  "noun"),
    # isim → fiil
    ("isim → fiil", "-lA-",   "noun"),
    ("isim → fiil", "-lAn-",  "noun"),
    ("isim → fiil", "-lAş-",  "noun"),
    ("isim → fiil", "-Al-",   "noun"),
    ("isim → fiil", "-A-",    "noun"),
    ("isim → fiil", "-sA-",   "noun"),
    ("isim → fiil", "-ImsA-", "noun"),
    ("isim → fiil", "-Ar-",   "noun"),   # isim→fiil: morar-, sarar- (DIŞLI DEĞİL)
    # fiil → isim (leksik; fiilimsi DIŞLI)
    ("fiil → isim", "-Im",   "verb"),
    ("fiil → isim", "-gI",   "verb"),
    ("fiil → isim", "-gIn",  "verb"),
    ("fiil → isim", "-gAn",  "verb"),
    ("fiil → isim", "-Ak",   "verb"),
    ("fiil → isim", "-I",    "verb"),
    ("fiil → isim", "-mAn",  "verb"),
    ("fiil → isim", "-IcI",  "verb"),
    ("fiil → isim", "-Ik",   "verb"),
    ("fiil → isim", "-Inç",  "verb"),
    ("fiil → isim", "-IntI", "verb"),
)

# Türetilmiş sözcüğün POS'u — suffix etiketine göre
_DERIVED_POS: dict[str, str] = {
    # isim → isim (sıfat üretenler adj)
    "-lI":   "adj",    # kirli, tuzlu
    "-sIz":  "adj",    # evsiz, tuzsuz
    "-CIl":  "adj",    # evcil, bencil
    "-CA":   "adj",    # Türkçe, insanca
    "-lIk":  "noun",   # gözlük, kitaplık
    "-CI":   "noun",   # gözcü, kitapçı
    "-CIk":  "noun",   # küçücük
    "-DAş":  "noun",   # meslektaş
    # isim → fiil
    "-lA-":   "verb",
    "-lAn-":  "verb",
    "-lAş-":  "verb",
    "-Al-":   "verb",
    "-A-":    "verb",
    "-sA-":   "verb",
    "-ImsA-": "verb",
    "-Ar-":   "verb",   # isim→fiil: morarmak
    # fiil → isim / fiil → sıfat
    "-IcI":  "adj",    # yapıcı, alıcı
    "-gAn":  "adj",    # çalışkan, atılgan
    "-Ik":   "adj",    # açık, kesik, bozuk
    "-gIn":  "adj",    # yorgun, düşkün
    "-Im":   "noun",   # ölüm, seçim
    "-gI":   "noun",   # sevgi, bilgi
    "-Ak":   "noun",   # durak, kaçak
    "-I":    "noun",   # yazı, sürü
    "-mAn":  "noun",   # yönetmen, öğretmen
    "-Inç":  "noun",   # sevinç, korkunç
    "-IntI": "noun",   # akıntı, esinti
}
```

- [ ] **Step 4: Testleri çalıştır — PASS beklenir**

```
PYTHONUTF8=1 python -m pytest tests/test_derivation.py -v
```

Beklenen: Tüm testler PASS (yeniler dahil).

- [ ] **Step 5: Commit**

```
git add turkgram/derivation.py tests/test_derivation.py
git commit -m "feat(derivation): _LEXICAL_SUFFIXES + _DERIVED_POS sabitleri (Faz 6)"
```

---

## Task 2: `analysis.py` — `_strip_derivation` fonksiyonu

**Files:**
- Modify: `turkgram/analysis.py` (yeni yardımcı fonksiyon, `_try_derivation_all`'ın hemen önüne)

- [ ] **Step 1: `analysis.py`'de `_try_number_all` fonksiyonunun hemen üstüne `_strip_derivation` ekle**

```python
def _strip_derivation(
    surface: str,
    label: str,
    src_pos: str,
) -> list[str]:
    """Yüzeyden derivasyon suffix'ini soy → olası kök adayları listesi.

    Ters harmoni: suffix'in her ünlü alloformunu dener.
    Fiil suffix'leri (src_pos=="verb"): mastar -mAk da soyulur → kök gövde.
    Ünlü-başlı suffix + kaynaştırma -y-: son -y de atılır.
    Başarısız soyma → boş liste (oracle zaten false döner → precision güvenli).
    """
    from .derivation import _NOUN_TO_NOUN, _NOUN_TO_VERB, _VERB_TO_NOUN

    # Suffix tablolarından template bul
    all_specs = _NOUN_TO_NOUN + _NOUN_TO_VERB + _VERB_TO_NOUN
    template: str | None = None
    vowel_initial: bool = False
    is_verb_output: bool = False
    for (cat, lbl, tmpl, vinit, pv) in all_specs:
        if lbl == label:
            template = tmpl
            vowel_initial = vinit
            is_verb_output = pv
            break
    if template is None:
        return []

    # Fiil çıktısı ise mastar -mAk soy
    work = surface
    if is_verb_output:
        for ending in ("mak", "mek"):
            if work.endswith(ending):
                work = work[: -len(ending)]
                break
        else:
            return []   # -mAk yoksa bu surface fiil türevi olamaz

    # Olası suffix realizasyonlarını üret (harmoni + sertleşme varyantları)
    # Template arşifonemleri: I→ıiuü, A→ae, C→cç, D→dt, G→gk
    suffixes: list[str] = _template_to_allomorphs(template)

    candidates: list[str] = []
    for suf in suffixes:
        if not work.endswith(suf):
            continue
        root = work[: -len(suf)]
        if not root:
            continue
        # Kaynaştırma -y- geri al (ünlü-başlı suffix + ünlü-final kök)
        if vowel_initial and root.endswith("y"):
            candidates.append(root[:-1])   # y'siz kök
        candidates.append(root)
    return candidates


_VOWELS_TR = "aeıiouü"
_HIGH_VOWELS = "ıiuü"
_LOW_VOWELS  = "ae"

def _template_to_allomorphs(template: str) -> list[str]:
    """Arşifonem template → tüm olası realize biçimler.

    Birden fazla arşifonem içeren template'ler için kartezyen çarpım:
    I→[ı,i,u,ü], A→[a,e], C→[c,ç], D→[d,t], G→[g,k].
    Küçük küme (max ~32 varyant / suffix) — performans sorunu yok.
    """
    import itertools
    _ARCH: dict[str, list[str]] = {
        "I": list(_HIGH_VOWELS),
        "A": list(_LOW_VOWELS),
        "C": ["c", "ç"],
        "D": ["d", "t"],
        "G": ["g", "k"],
    }
    # Her pozisyon için olası karakterler
    positions: list[list[str]] = []
    for ch in template:
        positions.append(_ARCH.get(ch, [ch]))
    return ["".join(combo) for combo in itertools.product(*positions)]
```

- [ ] **Step 2: `_template_to_allomorphs` manuel test — REPL**

```
PYTHONUTF8=1 python -c "
from turkgram.analysis import _template_to_allomorphs
print(_template_to_allomorphs('lIk'))   # lık lık luk lük vb.
print(_template_to_allomorphs('CI'))    # cı ci cu cü çı çi çu çü
"
```

Beklenen: Her arşifonem için 2-4 varyant, ör. `lIk` → `['lık','lik','luk','lük']`.

- [ ] **Step 3: `_strip_derivation` manuel test — REPL**

```
PYTHONUTF8=1 python -c "
from turkgram.analysis import _strip_derivation
print(_strip_derivation('gözlük',  '-lIk', 'noun'))   # ['göz']
print(_strip_derivation('kirli',   '-lI',  'noun'))   # ['kir']
print(_strip_derivation('gözlemek','-lA-', 'noun'))   # ['göz'] (mastar+kaynaştırma)
print(_strip_derivation('yapıcı',  '-IcI', 'verb'))   # ['yap...'] + mastar soyma
"
```

Beklenen: Her biri için doğru kök adayı listesi.

- [ ] **Step 4: Commit**

```
git add turkgram/analysis.py
git commit -m "feat(analysis): _strip_derivation + _template_to_allomorphs yardımcıları (Faz 6)"
```

---

## Task 3: `analysis.py` — `_try_derivation_all` + `analyze()` entegrasyonu

**Files:**
- Modify: `turkgram/analysis.py`

- [ ] **Step 1: `_strip_derivation` altına `_try_derivation_all` ekle**

```python
def _try_derivation_all(
    surface: str,
    analyses: list[Analysis],
    seen: set[tuple],
    roots: Collection[str] | None = None,
) -> None:
    """Leksik türetme çözümlemesi — oracle desen (_try_number_all emsali).

    _LEXICAL_SUFFIXES üzerinde döner (fiilimsi + çatı DIŞLI).
    roots verilirse lemma∉roots → atla (precision modu).
    Çıktı: kind='derivation', kwargs={'suffix', 'src_pos'}, segments, hypothetical.

    TUZAK — fiil → isim (src_pos='verb'): _strip_derivation bare stem döndürür
    (seçim → seç); oracle ve lemma için mastar yeniden kurulur (seç → seçmek).
    """
    from .derivation import derivations as _derivations, _LEXICAL_SUFFIXES, _DERIVED_POS
    from .morphology import low_vowel

    for (cat, label, src_pos) in _LEXICAL_SUFFIXES:
        for stem in _strip_derivation(surface, label, src_pos):
            if not stem:
                continue

            # fiil → isim: bare stem → mastar yeniden kur (seç → seçmek)
            if src_pos == "verb":
                try:
                    lemma = stem + "m" + low_vowel(stem) + "k"
                except ValueError:
                    continue
            else:
                lemma = stem   # isim → * : stem == lemma (göz, kitap, mor)

            if roots is not None and lemma not in roots:
                continue
            try:
                derived = _derivations(lemma, src_pos)
            except Exception:
                continue
            if not derived:
                continue
            for r in derived:
                if r["form"] != surface or r["suffix"] != label:
                    continue
                key = ("derivation", lemma, label)   # plain tuple, codebase konvansiyonu
                if key in seen:
                    continue
                seen.add(key)
                derived_pos = _DERIVED_POS.get(label, "noun")
                suffix_surf = surface[len(stem):]
                segs = _segs_to_tuple([(stem, "kök"), (suffix_surf, label)])
                analyses.append(Analysis(
                    kind="derivation",
                    lemma=lemma,
                    pos=derived_pos,
                    kwargs={"suffix": label, "src_pos": src_pos},
                    segments=segs,
                    hypothetical=(roots is None),
                ))
```

- [ ] **Step 2: `_KINDS`'a `"derivation"` ekle**

`analysis.py` satır 68-71'deki `_KINDS` tuple'ına SONA ekle:

```python
_KINDS = ("conjugate", "decline", "copula", "converb",
          "converb_casina", "converb_ken", "participle",
          "intensify", "diminutive", "ordinal", "distributive",
          "conjunction", "derivation")   # ← sona eklendi
```

- [ ] **Step 3: `analyze()` içinde `_try_derivation_all` çağrısı ekle**

`analysis.py`'de `analyze()` fonksiyonunun içinde, `_try_number_all` çağrısının hemen **sonrasına** ekle (satır ~911):

```python
    # Adım 7: Türetme çözümlemesi (leksik, fiilimsi+çatı dışlı)
    if pos in (None, "noun", "verb", "adj"):
        _try_derivation_all(surface_token, analyses, seen, roots)
```

Çok-token dalında da (satır ~867, `num_analyses` bloğunun altına):

```python
        # Bileşik türetme — çok-token surface'te henüz desteklenmez (defer)
        # Tek-token derivasyon yeterli; çok-token case'e not düşüldü.
```

- [ ] **Step 4: Hızlı smoke test — REPL**

```
PYTHONUTF8=1 python -c "
from turkgram import analyze
from turkgram.lexicon import load
roots = load()
r = analyze('gözlük', roots=roots)
print(r)
r2 = analyze('kirli', roots=roots)
print(r2)
r3 = analyze('gözlemek', roots=roots)
print(r3)
"
```

Beklenen: Her birinde `kind='derivation'` içeren Analysis nesnesi görünmeli.

- [ ] **Step 5: Commit**

```
git add turkgram/analysis.py
git commit -m "feat(analysis): _try_derivation_all + kind='derivation' (Faz 6)"
```

---

## Task 4: Bağımsız Analiz Golden'ı yaz

**Files:**
- Create: `tests/golden_derivation_analysis.py`

Golden dosyası **motora bakmadan** yalnız gramer kuralından türetilir. Aşağıdaki içeriği yaz:

- [ ] **Step 1: `tests/golden_derivation_analysis.py` oluştur**

```python
"""Derivasyon analizi bağımsız golden (motor-körü).

Her satır: (yüzey, beklenen_lemma, beklenen_pos, beklenen_suffix, beklenen_src_pos)
Gramerden elle doğrulandı; motora bakılmadı.
"""

GOLDEN_ANALYSIS: list[tuple[str, str, str, str, str]] = [
    # isim → isim (noun)
    ("gözlük",    "göz",     "noun", "-lIk",  "noun"),
    ("kitaplık",  "kitap",   "noun", "-lIk",  "noun"),
    ("gözcü",     "göz",     "noun", "-CI",   "noun"),
    ("kitapçı",   "kitap",   "noun", "-CI",   "noun"),
    ("meslektaş", "meslek",  "noun", "-DAş",  "noun"),
    # isim → isim (adj)
    ("kirli",     "kir",     "adj",  "-lI",   "noun"),
    ("tuzlu",     "tuz",     "adj",  "-lI",   "noun"),
    ("gözsüz",    "göz",     "adj",  "-sIz",  "noun"),
    ("evsiz",     "ev",      "adj",  "-sIz",  "noun"),
    ("türkçe",    "türk",    "adj",  "-CA",   "noun"),   # analyze() lowercase normalize eder
    ("evcil",     "ev",      "adj",  "-CIl",  "noun"),
    # isim → fiil
    ("gözlemek",  "göz",     "verb", "-lA-",  "noun"),
    ("evlenmek",  "ev",      "verb", "-lAn-", "noun"),
    ("gözleşmek", "göz",     "verb", "-lAş-", "noun"),
    ("morarmak",  "mor",     "verb", "-Ar-",  "noun"),
    ("susamak",   "su",      "verb", "-sA-",  "noun"),
    # fiil → isim (noun)
    ("seçim",     "seçmek",  "noun", "-Im",   "verb"),
    ("ölüm",      "ölmek",   "noun", "-Im",   "verb"),
    ("sevgi",     "sevmek",  "noun", "-gI",   "verb"),
    ("bilgi",     "bilmek",  "noun", "-gI",   "verb"),
    ("durak",     "durmak",  "noun", "-Ak",   "verb"),
    ("sevinç",    "sevinmek","noun", "-Inç",  "verb"),
    ("akıntı",    "akmak",   "noun", "-IntI", "verb"),
    # fiil → sıfat
    ("yapıcı",    "yapmak",  "adj",  "-IcI",  "verb"),
    ("alıcı",     "almak",   "adj",  "-IcI",  "verb"),
    ("açık",      "açmak",   "adj",  "-Ik",   "verb"),
    ("kesik",     "kesmek",  "adj",  "-Ik",   "verb"),
]
```

- [ ] **Step 2: Commit**

```
git add tests/golden_derivation_analysis.py
git commit -m "test(derivation): bağımsız analiz golden (motor-körü, Faz 6)"
```

---

## Task 5: Analiz runner yaz + geçir

**Files:**
- Create: `tests/test_derivation_analysis.py`

- [ ] **Step 1: `tests/test_derivation_analysis.py` oluştur**

```python
"""Derivasyon analizi runner — golden_derivation_analysis.py'yi çalıştırır."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from turkgram import analyze
from turkgram.lexicon import load
from tests.golden_derivation_analysis import GOLDEN_ANALYSIS


@pytest.fixture(scope="module")
def roots():
    return load()


@pytest.mark.parametrize("surface,exp_lemma,exp_pos,exp_suffix,exp_src_pos", GOLDEN_ANALYSIS)
def test_derivation_analysis(surface, exp_lemma, exp_pos, exp_suffix, exp_src_pos, roots):
    results = analyze(surface, roots=roots)
    deriv = [r for r in results if r.kind == "derivation"]
    assert deriv, (
        f"'{surface}' için kind='derivation' analiz bulunamadı. "
        f"Mevcut kind'lar: {[r.kind for r in results]}"
    )
    match = next(
        (r for r in deriv
         if r.lemma == exp_lemma
         and r.pos == exp_pos
         and r.kwargs.get("suffix") == exp_suffix
         and r.kwargs.get("src_pos") == exp_src_pos),
        None,
    )
    assert match is not None, (
        f"'{surface}': beklenen (lemma={exp_lemma!r}, pos={exp_pos!r}, "
        f"suffix={exp_suffix!r}, src_pos={exp_src_pos!r}) bulunamadı.\n"
        f"Mevcut derivation analizler: {[(r.lemma,r.pos,r.kwargs) for r in deriv]}"
    )


def test_derivation_segments_present(roots):
    """Derivasyon analizlerinde segments dolu olmalı."""
    results = analyze("gözlük", roots=roots)
    deriv = [r for r in results if r.kind == "derivation"]
    assert deriv
    assert deriv[0].segments, "segments boş olmamalı"
    labels = [s.label for s in deriv[0].segments]
    assert "kök" in labels, f"'kök' segmenti eksik: {labels}"


def test_derivation_hypothetical_false_with_roots(roots):
    """roots verildiğinde hypothetical=False olmalı."""
    results = analyze("gözlük", roots=roots)
    deriv = [r for r in results if r.kind == "derivation"]
    assert deriv
    assert not deriv[0].hypothetical, "roots verilince hypothetical=False olmalı"


def test_derivation_hypothetical_true_no_roots():
    """roots=None iken hypothetical=True olmalı."""
    results = analyze("gözlük")
    deriv = [r for r in results if r.kind == "derivation"]
    if deriv:   # gürültü modunda çıkabilir
        assert deriv[0].hypothetical, "roots=None iken hypothetical=True olmalı"


def test_derivation_no_fiilimsi(roots):
    """Fiilimsi ekleri kind='derivation' olarak DÖNMEMELİ."""
    # 'gelmek' için gelme/gelen/gelince → converb/participle, derivation değil
    results = analyze("gelme", roots=roots)
    deriv_suffixes = [r.kwargs.get("suffix") for r in results if r.kind == "derivation"]
    assert "-mA" not in deriv_suffixes, "'-mA' fiilimsi derivation olarak çıkmamalı"


def test_derivation_no_voice(roots):
    """Çatı ekleri kind='derivation' olarak DÖNMEMELİ."""
    results = analyze("sevilmek", roots=roots)
    deriv_suffixes = [r.kwargs.get("suffix") for r in results if r.kind == "derivation"]
    assert "-Il-" not in deriv_suffixes, "'-Il-' edilgen derivation olarak çıkmamalı"


def test_derivation_pos_filter(roots):
    """pos='verb' filtresi çalışmalı: isim→isim türevler (gözlük) görünmemeli."""
    results = analyze("gözlük", pos="verb", roots=roots)
    # pos="verb" verilince derivation kind varsa pos="verb" olmalı
    for r in results:
        if r.kind == "derivation":
            assert r.pos == "verb", (
                f"pos='verb' filtresiyle noun derivation döndü: {r}"
            )


def test_existing_analyses_unaffected(roots):
    """Mevcut kind'lar derivasyon eklenmesiyle bozulmamalı — regresyon."""
    # 'geldim' → conjugate, derivation DEĞİL
    results = analyze("geldim", roots=roots)
    kinds = [r.kind for r in results]
    assert "conjugate" in kinds, "Mevcut 'conjugate' kind'ı regresyon olmamalı"
```

- [ ] **Step 2: Testleri çalıştır — PASS beklenir**

```
PYTHONUTF8=1 python -m pytest tests/test_derivation_analysis.py -v
```

Beklenen: Tüm testler PASS. Başarısız olanlar varsa `_strip_derivation` / `_try_derivation_all`'da debug yap.

- [ ] **Step 3: Commit**

```
git add tests/test_derivation_analysis.py
git commit -m "test(derivation): analiz runner (Faz 6)"
```

---

## Task 6: Tam paket regresyon + korpus taraması

**Files:**
- Read: `turkgram/lexicon.py` (load() API)

- [ ] **Step 1: Tam test paketi çalıştır**

```
PYTHONUTF8=1 python -m pytest tests/ -x -q
```

Beklenen: Tüm önceki testler (3523+) PASS; yeni testler de PASS.

- [ ] **Step 2: Korpus taraması — derivasyon çökmesi yok**

`tools/` altında geçici script yaz:

```python
# tools/check_derivation_corpus.py
import sys
sys.path.insert(0, ".")
from turkgram import analyze
from turkgram.lexicon import load
from turkgram.derivation import _LEXICAL_SUFFIXES

roots = load()
lemmas = list(roots)
errors = []
total = 0
for lemma in lemmas:
    for (cat, label, src_pos) in _LEXICAL_SUFFIXES:
        if src_pos == "noun" and lemma.endswith(("mak", "mek")):
            continue   # fiil lemması isim suffix'iyle deneme
        try:
            results = analyze(lemma, roots=roots)
            total += 1
        except Exception as e:
            errors.append((lemma, label, str(e)))

print(f"Toplam çağrı: {total}")
print(f"Hata sayısı: {len(errors)}")
for err in errors[:10]:
    print(err)
```

```
PYTHONUTF8=1 python tools/check_derivation_corpus.py
```

Beklenen: `Hata sayısı: 0`

- [ ] **Step 3: Commit (gerekirse)**

```
git add turkgram/analysis.py turkgram/derivation.py
git commit -m "fix(derivation): korpus taraması sonrası düzeltmeler (Faz 6)"
```

---

## Task 7: CLAUDE.md güncelleme

**Files:**
- Modify: `CLAUDE.md` (§7 Yol haritası)

- [ ] **Step 1: CLAUDE.md §7'ye Faz 6 tamamlama notu ekle**

`CLAUDE.md`'de `## 7. Yol haritası ve DURUM` bölümünde en üste ekle:

```markdown
- **Faz 6 ✅** — Derivasyon analizi (`analysis.py` + `derivation.py`):
  `kind="derivation"` — `_try_derivation_all` oracle, `_strip_derivation` ters-harmoni,
  `_LEXICAL_SUFFIXES` (fiilimsi+çatı DIŞLI, (category,label) çiftiyle), `_DERIVED_POS`
  (adj/noun/verb POS haritası). Tek katman; zincir defer. [TEST SAYISI] test yeşil.
```

(Test sayısını `pytest tests/ -q` çıktısından al.)

- [ ] **Step 2: Commit**

```
git add CLAUDE.md
git commit -m "docs(claude): Faz 6 derivasyon analizi tamamlandı"
```

---

## Hızlı Referans

**Tüm testi çalıştır:**
```
PYTHONUTF8=1 python -m pytest tests/ -q
```

**Yalnız derivasyon testleri:**
```
PYTHONUTF8=1 python -m pytest tests/test_derivation.py tests/test_derivation_analysis.py -v
```

**Windows UTF-8 notu:** `PYTHONUTF8=1` olmadan Türkçe karakter yazan komutlar `UnicodeEncodeError` verir.

**Editable kurulum:** Değişiklikler anında yansır (`pip install -e .` zaten yapıldı).

**Analiz.py'de ekleme yerleri:**
- `_strip_derivation` + `_template_to_allomorphs`: `_try_number_all` (satır ~1011) hemen önüne
- `_try_derivation_all`: `_strip_derivation`'ın hemen altına
- `analyze()` çağrısı: satır ~911, `_try_number_all` çağrısının hemen sonrasına
