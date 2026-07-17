# Edat Analizi Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `analyze()`'ın edatları `kind="postposition"` olarak tanıması + `parse.py` PP düğümlerinin yönetilen-durum bilgisi taşıması; üç ayrı edat tablosunu tek `_POSTPOSITIONS` kaynağına konsolide etmek.

**Architecture:** `postposition.py`'de tek zengin tablo (`üret`/`üret_zamir`/`yönet`/`üretilebilir`); üretim (`postposition()`), analiz (`_try_postposition_all`), K2 (`context._POSTP_GOV` türetme) hepsi oradan beslenir. Analiz bağlaç deseninin aynası: closed-set, oracle-free, additive. PP doğrulaması recall-güvenli (işaretle, reddetme).

**Tech Stack:** Python 3, pytest, mevcut turkgram morfoloji motoru.

**Kaynaklar:** SPEC `spec/postposition-spec.md §7-§9`; tasarım `docs/superpowers/specs/2026-07-17-edat-analizi-design.md`.

**Windows notu:** UTF-8 için ad-hoc python komutlarını `PYTHONUTF8=1 python …` ile koş (pytest sorunsuz).

---

## Dosya Yapısı

- **Modify** `turkgram/postposition.py` — `_POSTPOSITIONS` konsolide tablo; `postposition()` refactor + iki ValueError; `_POSTPOSITION_CASE` uyumluluk görünümü korunur.
- **Modify** `turkgram/context.py:52-72` — `_POSTP_GOV` `_POSTPOSITIONS`'tan türetilir; K2 (`_k2`) mantığı DEĞİŞMEZ.
- **Modify** `turkgram/analysis.py:117-122` (`_POS`/`_KINDS`) + `:1058-1064` (dispatch) + yeni `_try_postposition_all`.
- **Modify** `turkgram/parse.py:13,18` (tablo importu + ADP kümesi) + `:42-63` (`PhraseNode.governs`) + `:95-102` (`_POS_TO_TAG`) + `:205-220` (R2 governs).
- **Create** `tests/golden_postposition_analysis.py` — bağımsız golden (motor-körü, Opus).
- **Create** `tests/test_postposition_analysis.py` — runner.
- **Modify** `tests/test_postposition.py` — frozen-edat ValueError + `_POSTP_GOV` drift-lock assertion.
- **Create** `tools/sweep_postposition_analysis.py` — korpus tarama (hakem).

---

## Task 1: `_POSTPOSITIONS` konsolide tablo + `postposition()` refactor

**Files:**
- Modify: `turkgram/postposition.py`
- Test: `tests/test_postposition.py`

**Not:** Bu görev üretim davranışını KORUR. Mevcut `tests/test_postposition.py` (86-girdi golden) yeşil kalmalı. Yalnız iki YENİ ValueError davranışı eklenir.

- [ ] **Step 1: Mevcut üretim testinin yeşil olduğunu doğrula (baseline)**

Run: `python -m pytest tests/test_postposition.py -q`
Expected: PASS (mevcut tüm testler)

- [ ] **Step 2: Yeni davranış testlerini yaz (RED)**

`tests/test_postposition.py` sonuna ekle:

```python
import pytest
from turkgram.postposition import postposition, _POSTPOSITIONS


def test_frozen_edat_raises_distinct_error():
    """dair/ilişkin/ait/yana donmuş — üretilemez, ayrı ValueError."""
    for edat in ("dair", "ilişkin", "ait", "yana"):
        with pytest.raises(ValueError, match="donmuş"):
            postposition("ev", edat)


def test_unknown_edat_lists_only_producible():
    """Bilinmeyen edat mesajındaki 'Geçerliler' donmuş edatları İÇERMEZ."""
    with pytest.raises(ValueError) as exc:
        postposition("ev", "zzz")
    msg = str(exc.value)
    assert "dair" not in msg and "ilişkin" not in msg
    assert "için" in msg  # üretilebilir edat listelenir


def test_new_edats_present_in_table():
    """Konsolide tablo 23 edat içerir (19 üretilebilir + 4 donmuş)."""
    assert set(_POSTPOSITIONS) >= {
        "dair", "ilişkin", "ait", "yana",  # donmuş
        "dek", "üzere", "başka", "aşkın",  # K2'ye yeni
    }
    assert _POSTPOSITIONS["dair"]["üretilebilir"] is False
    assert _POSTPOSITIONS["için"]["üretilebilir"] is True


def test_yonet_sets_preserve_pronoun_cases():
    """KRİTİK: ile/gibi/kadar zamir-genitifi korunur (üret'ten türetilmez)."""
    assert _POSTPOSITIONS["ile"]["yönet"] == frozenset({"nom", "gen"})
    assert _POSTPOSITIONS["gibi"]["yönet"] == frozenset({"nom", "gen"})
    assert _POSTPOSITIONS["kadar"]["yönet"] == frozenset({"nom", "gen", "dat"})
```

- [ ] **Step 3: Testi koş, başarısız olduğunu gör**

Run: `python -m pytest tests/test_postposition.py::test_frozen_edat_raises_distinct_error -v`
Expected: FAIL (`_POSTPOSITIONS` import edilemez / donmuş edat mantığı yok)

- [ ] **Step 4: `_POSTPOSITIONS` tablosunu yaz + `postposition()` refactor**

`turkgram/postposition.py`'de `_POSTPOSITION_CASE` dict'ini (satır 14-34) ŞUNUNLA değiştir:

```python
# Tek doğruluk kaynağı — üretim + analiz + K2 (context._POSTP_GOV) buradan beslenir.
# yönet KÜMESİ elle yazılır (üret'ten TÜRETİLMEZ): zamir çok-case edatları korunur.
_POSTPOSITIONS: dict[str, dict] = {
    # üretilebilir (19) — postposition() üretir
    "için":     {"üret": "nom", "üret_zamir": "gen", "yönet": frozenset({"nom", "gen"}),        "üretilebilir": True},
    "ile":      {"üret": "nom",                       "yönet": frozenset({"nom", "gen"}),        "üretilebilir": True},
    "gibi":     {"üret": "nom",                       "yönet": frozenset({"nom", "gen"}),        "üretilebilir": True},
    "kadar":    {"üret": "dat",                       "yönet": frozenset({"nom", "gen", "dat"}), "üretilebilir": True},
    "göre":     {"üret": "dat",                       "yönet": frozenset({"dat"}),               "üretilebilir": True},
    "karşı":    {"üret": "dat",                       "yönet": frozenset({"dat"}),               "üretilebilir": True},
    "rağmen":   {"üret": "dat",                       "yönet": frozenset({"dat"}),               "üretilebilir": True},
    "doğru":    {"üret": "dat",                       "yönet": frozenset({"dat"}),               "üretilebilir": True},
    "dek":      {"üret": "dat",                       "yönet": frozenset({"dat"}),               "üretilebilir": True},
    "değin":    {"üret": "dat",                       "yönet": frozenset({"dat"}),               "üretilebilir": True},
    "üzere":    {"üret": "nom",                       "yönet": frozenset({"nom"}),               "üretilebilir": True},
    "önce":     {"üret": "abl",                       "yönet": frozenset({"abl"}),               "üretilebilir": True},
    "sonra":    {"üret": "abl",                       "yönet": frozenset({"abl"}),               "üretilebilir": True},
    "beri":     {"üret": "abl",                       "yönet": frozenset({"abl"}),               "üretilebilir": True},
    "itibaren": {"üret": "abl",                       "yönet": frozenset({"abl"}),               "üretilebilir": True},
    "başka":    {"üret": "abl",                       "yönet": frozenset({"abl"}),               "üretilebilir": True},
    "dolayı":   {"üret": "abl",                       "yönet": frozenset({"abl"}),               "üretilebilir": True},
    "ötürü":    {"üret": "abl",                       "yönet": frozenset({"abl"}),               "üretilebilir": True},
    "aşkın":    {"üret": "acc",                       "yönet": frozenset({"acc"}),               "üretilebilir": True},
    # donmuş (4) — analiz + K2 tanır, postposition() ÜRETMEZ
    "dair":     {"yönet": frozenset({"dat"}), "üretilebilir": False},
    "ilişkin":  {"yönet": frozenset({"dat"}), "üretilebilir": False},
    "ait":      {"yönet": frozenset({"dat"}), "üretilebilir": False},
    "yana":     {"yönet": frozenset({"abl"}), "üretilebilir": False},
}

# Geriye uyum görünümü — parse.py ADP kümesi TÜM edatları ister (donmuş dahil),
# ama eski _POSTPOSITION_CASE importları yalnız üretilebilir üret-case bekler.
_POSTPOSITION_CASE: dict[str, str] = {
    e: v["üret"] for e, v in _POSTPOSITIONS.items() if v["üretilebilir"]
}
```

`postposition()` gövdesinde edat doğrulama bloğunu (satır 65-79) ŞUNUNLA değiştir:

```python
    if edat not in _POSTPOSITIONS:
        producible = sorted(e for e, v in _POSTPOSITIONS.items() if v["üretilebilir"])
        raise ValueError(f"Bilinmeyen edat: {edat!r}. Geçerliler: {producible}")
    if not _POSTPOSITIONS[edat]["üretilebilir"]:
        raise ValueError(
            f"{edat!r} donmuş bir edat (donmuş kalıp), postposition() üretmez."
        )
    if bitişik and edat != "ile":
        raise ValueError(
            f"bitişik=True yalnız 'ile' için geçerlidir, {edat!r} değil."
        )
    if bitişik:
        return decline(lemma, case="ins")
    # için: kişi/n-gövde zamirleri genitif (üret_zamir), düz isimler yalın (üret)
    entry = _POSTPOSITIONS[edat]
    if edat == "için" and lemma.lower() in _ICIN_GEN_PRONOUNS:
        case = entry["üret_zamir"]
    else:
        case = entry["üret"]
    declined = decline(lemma, case=case)
    return declined + " " + edat
```

- [ ] **Step 5: Testleri koş (yeni + regresyon)**

Run: `python -m pytest tests/test_postposition.py -q`
Expected: PASS (86 mevcut + 4 yeni)

- [ ] **Step 6: Commit**

```bash
git add turkgram/postposition.py tests/test_postposition.py
git commit -m "feat(postposition): _POSTPOSITIONS konsolide tablo + donmuş edat ValueError"
```

---

## Task 2: `context._POSTP_GOV` türetme + drift-lock golden

**Files:**
- Modify: `turkgram/context.py:52-72`
- Test: `tests/test_postposition.py`

**Not:** K2 algoritması (`_k2`, satır ~161-168) DEĞİŞMEZ. Yalnız `_POSTP_GOV`'un veri kaynağı değişir. Drift-lock golden, mevcut 19 anahtarın kabul-kümesinin daralmadığını garantiler.

- [ ] **Step 1: Drift-lock testini yaz (RED)**

`tests/test_postposition.py` sonuna ekle:

```python
def test_postp_gov_derived_preserves_current_keys():
    """K2 _POSTP_GOV türetildikten sonra mevcut 19 anahtarın kabul-kümesi DEĞİŞMEZ.

    Mevcut _POSTP_GOV snapshot (konsolidasyon ÖNCESİ değerler) — bu daralırsa
    ile/gibi/kadar zamir-genitifi kaybolur → K2 recall kırılır.
    """
    from turkgram.context import _POSTP_GOV
    from turkgram.postposition import _POSTPOSITIONS

    current_snapshot = {
        "ile": frozenset({"nom", "gen"}),
        "için": frozenset({"nom", "gen"}),
        "gibi": frozenset({"nom", "gen"}),
        "kadar": frozenset({"nom", "gen", "dat"}),
        "göre": frozenset({"dat"}), "doğru": frozenset({"dat"}),
        "karşı": frozenset({"dat"}), "rağmen": frozenset({"dat"}),
        "dair": frozenset({"dat"}), "ilişkin": frozenset({"dat"}),
        "ait": frozenset({"dat"}), "değin": frozenset({"dat"}),
        "önce": frozenset({"abl"}), "sonra": frozenset({"abl"}),
        "beri": frozenset({"abl"}), "dolayı": frozenset({"abl"}),
        "ötürü": frozenset({"abl"}), "itibaren": frozenset({"abl"}),
        "yana": frozenset({"abl"}),
    }
    derived = {e: v["yönet"] for e, v in _POSTPOSITIONS.items()}
    for edat, gov in current_snapshot.items():
        assert derived[edat] == gov, f"{edat}: {derived[edat]} != {gov}"
        assert _POSTP_GOV[edat] == gov, f"_POSTP_GOV {edat} daraldı"
```

- [ ] **Step 2: Testi koş, başarısız olduğunu gör**

Run: `python -m pytest tests/test_postposition.py::test_postp_gov_derived_preserves_current_keys -v`
Expected: FAIL (`_POSTP_GOV` hâlâ hardcoded — türetilen tabloyla senkron değil / import döngüsü)

- [ ] **Step 3: `_POSTP_GOV`'u türet**

`turkgram/context.py`'de `_POSTP_GOV` literalini (satır 51-72) ŞUNUNLA değiştir:

```python
# Edat → nitelediği adın kabul edilen durumları (SPEC §3 K2).
# Tek doğruluk kaynağı postposition._POSTPOSITIONS'tan TÜRETİLİR (drift önlenir).
from .postposition import _POSTPOSITIONS as _POSTPOSITIONS_TABLE
_POSTP_GOV: dict[str, frozenset[str]] = {
    e: v["yönet"] for e, v in _POSTPOSITIONS_TABLE.items()
}
```

**İçe aktarma döngüsü kontrolü:** `postposition.py` yalnız `morphology_noun`'a bağlı; `context.py`'yi import etmez → döngü yok. Import'u dosyanın en üstündeki diğer importların yanına taşımak da olur; yerel import da güvenli.

- [ ] **Step 4: Drift-lock + tüm K2/context testlerini koş**

Run: `python -m pytest tests/test_postposition.py tests/test_context.py -q`
Expected: PASS (K2 davranışı korundu; mevcut context testleri yeşil)

- [ ] **Step 5: Commit**

```bash
git add turkgram/context.py tests/test_postposition.py
git commit -m "refactor(context): _POSTP_GOV _POSTPOSITIONS'tan türetilir (K2 mantığı değişmez)"
```

---

## Task 3: Bağımsız golden — tek-token edat analizi (motor-körü)

**Files:**
- Create: `tests/golden_postposition_analysis.py`
- Create: `tests/test_postposition_analysis.py`

**Not (CLAUDE.md §2):** Golden motordan BAĞIMSIZ kurulur — Opus subagent'a dispatch: "motoru/analysis.py'yi GÖRME, yalnız SPEC §7 + dilbilgisi". Aşağıdaki içerik golden'ın YAPISINI verir; beklenen değerler dilbilgisinden elle doğrulanır.

- [ ] **Step 1: Bağımsız golden dosyasını yaz**

`tests/golden_postposition_analysis.py` oluştur (motor-körü, elle-doğrulanmış):

```python
"""Bağımsız golden — edat analizi (SPEC §7). Motor-körü kuruldu.

Her giriş: (yüzey, beklenen_postposition_okuması_var_mı, beklenen_lemma).
Precision stili: postposition okuması GÖT içinde olmalı (want ⊆ got).
"""

# Tüm 23 edat postposition okuması döndürmeli (closed-set, additive)
POSTPOSITION_PRESENT = [
    "için", "ile", "gibi", "kadar", "göre", "karşı", "rağmen", "doğru",
    "dek", "değin", "üzere", "önce", "sonra", "beri", "itibaren", "başka",
    "dolayı", "ötürü", "aşkın", "dair", "ilişkin", "ait", "yana",
]

# Adversarial homograflar: postposition okuması EKLENİR ama disambiguation'da
# doğru okumayı GEÇMEZ. (yüzey, doğru_okuma_pos)
# NOT [hakem C1]: analyze() düz sözcük için pos="adj" ÜRETMEZ (adj yalnız
# intensify/diminutive kind'larında); "başka" bare-noun okuması pos="noun" alır
# (kind=decline, _KIND_PRIOR=2 > postposition=0). Sıfat baskınlığı _leaf_tag
# leksikon-override'ında test edilir, disambiguation.rank'ta DEĞİL.
HOMOGRAPH_NOT_TOP = [
    ("aşkın", "noun"),   # aşk+ın (gen/2sg-poss) baskın (decline > postposition)
    ("başka", "noun"),   # bare-noun decline okuması baskın
]

# Belirsizlik: hem postposition hem başka okuma DÖNER (ikisi de got içinde).
# NOT [hakem M1]: 2. okuma MOTOR olgusudur — Task 4'te ampirik doğrulanır.
# "göre" = gör+(-A ulaç) → converb okuması beklenir (gör _ROOTS'ta).
# "sonra" DÜŞÜRÜLDÜ: analyze'da zarf kind'ı yok, güvenilir 2. okuma round-trip etmez.
AMBIGUOUS = [
    ("göre", "postposition"),   # + gör-e ulaç (Task 4'te doğrulanır)
]
```

- [ ] **Step 2: Runner testini yaz (RED)**

`tests/test_postposition_analysis.py` oluştur:

```python
import pytest
from turkgram.analysis import analyze
from turkgram.lexicon import load
from tests.golden_postposition_analysis import (
    POSTPOSITION_PRESENT, HOMOGRAPH_NOT_TOP, AMBIGUOUS,
)

_ROOTS = load()


def _kinds(surface):
    return [a.kind for a in analyze(surface, roots=_ROOTS)]


@pytest.mark.parametrize("edat", POSTPOSITION_PRESENT)
def test_postposition_reading_present(edat):
    analyses = analyze(edat, roots=_ROOTS)
    postp = [a for a in analyses if a.kind == "postposition"]
    assert postp, f"{edat}: postposition okuması yok"
    assert postp[0].lemma == edat
    assert postp[0].pos == "postp"


def test_postposition_always_returns_without_roots():
    """Closed-set: roots=None olsa da postposition okuması gelir."""
    analyses = analyze("için", roots=None)
    assert any(a.kind == "postposition" for a in analyses)


@pytest.mark.parametrize("surface,_pos", AMBIGUOUS)
def test_ambiguous_returns_both(surface, _pos):
    kinds = _kinds(surface)
    assert "postposition" in kinds
    assert len(set(kinds)) >= 2, f"{surface}: belirsizlik yok, yalnız {kinds}"


@pytest.mark.parametrize("surface,correct_pos", HOMOGRAPH_NOT_TOP)
def test_homograph_postposition_not_top(surface, correct_pos):
    """Adversarial: postposition okuması sıralama tepesinde OLMAMALI."""
    from turkgram.disambiguation import rank
    ranked = rank(analyze(surface, roots=_ROOTS), freq=None)
    assert ranked[0].pos == correct_pos, (
        f"{surface}: tepe {ranked[0].pos}/{ranked[0].kind}, beklenen {correct_pos}"
    )
```

- [ ] **Step 3: Testi koş, başarısız olduğunu gör**

Run: `python -m pytest tests/test_postposition_analysis.py -q`
Expected: FAIL (`_try_postposition_all` yok → postposition okuması hiç gelmez)

*(Golden bu noktada motora bağımlı DEĞİL; motor Task 4'te eklenince yeşile döner. `disambiguation.rank` imzasını doğrula — `rank(analyses, freq=None)` mevcut mu; değilse runner'ı mevcut imzaya uyarla.)*

- [ ] **Step 4: Commit (RED golden)**

```bash
git add tests/golden_postposition_analysis.py tests/test_postposition_analysis.py
git commit -m "test(postposition): bağımsız edat analizi golden (motor-körü, RED)"
```

---

## Task 4: `_try_postposition_all` motoru + dispatch (GREEN)

**Files:**
- Modify: `turkgram/analysis.py:117` (`_POS`) + `:118-122` (`_KINDS`); dispatch: conjunction'dan (satır 1060) SONRA, number'dan (1062) ÖNCE; yeni fonksiyon `_try_conjunction_all`'dan (1517-1536) SONRA.

- [ ] **Step 1: `_POS`/`_KINDS` genişlet**

`turkgram/analysis.py:117-122`:

```python
_POS = ("verb", "noun", "adj", "num", "conj", "postp")
_KINDS = ("conjugate", "decline", "copula", "converb",
          "converb_casina", "converb_ken", "participle",
          "intensify", "diminutive", "ordinal", "distributive",
          "conjunction", "derivation",
          "reduplication_full", "reduplication_converb", "reduplication_m",
          "postposition")
```

- [ ] **Step 2: `_try_postposition_all` fonksiyonunu yaz**

`_try_conjunction_all`'dan (1517-1536) hemen SONRA ekle:

```python
def _try_postposition_all(surface: str, analyses: list[Analysis], seen: set[tuple]) -> None:
    """Edat çözümlemesi — oracle dışı, kapalı-liste (SPEC §7.1).

    Bağlaç deseninin aynası: closed-set, additive, her zaman döner.
    Yönetilen durum lemmadan/tablodan türetilebilir → kwargs BOŞ.
    Bilinçli belirsizlik: 'sonra' = edat + zarf; 'göre' = edat + gör-e ulaç.
    """
    from .postposition import _POSTPOSITIONS
    edat = surface.lower()
    if edat not in _POSTPOSITIONS:
        return
    key = ("postposition", edat, frozenset())
    if key in seen:
        return
    seen.add(key)
    analyses.append(Analysis(
        lemma=edat,
        pos="postp",
        kind="postposition",
        kwargs={},
        segments=_segs_to_tuple([(surface, "kök")]),
        hypothetical=False,
    ))
```

- [ ] **Step 3: Dispatch ekle**

`turkgram/analysis.py:1058-1060`, bağlaç dispatch'inin hemen ardına:

```python
    # Adım 5: Bağlaç çözümlemesi (kapalı liste, oracle dışı)
    if pos in (None, "conj"):
        _try_conjunction_all(surface_token, analyses, seen)

    # Adım 5b: Edat çözümlemesi (kapalı liste, oracle dışı, additive)
    if pos in (None, "postp"):
        _try_postposition_all(surface_token, analyses, seen)
```

- [ ] **Step 4: `göre` belirsizliğini ampirik doğrula [hakem M1]**

`göre`'nin 2. okuması (gör-e ulaç) MOTOR olgusu — golden körü varsaydı, şimdi teyit:

Run: `PYTHONUTF8=1 python -c "from turkgram.analysis import analyze; from turkgram.lexicon import load; print([(a.kind,a.lemma) for a in analyze('göre', roots=load())])"`
Expected: hem `postposition` hem `converb` (lemma `görmek`) görünür.

Görünmüyorsa (pre-existing `_root_candidates` recall açığı): `AMBIGUOUS`'u boşalt + golden'a "0 belirsiz yüzey — göre converb recall açığı pre-existing, edat analizine özgü değil" notu yaz. Motoru golden'a uydurma.

- [ ] **Step 5: `_KIND_PRIOR` drift-lock testini ekle [hakem H1]**

`aşkın`/`başka` homografının doğru sıralanması, `postposition`'ın `disambiguation._KIND_PRIOR`'da OLMAMASINA (öncelik 0) bağlı. Gelecekte biri eklerse sessizce kırılır → kilit:

`tests/test_postposition_analysis.py` sonuna ekle:
```python
def test_postposition_stays_out_of_kind_prior():
    """Homograf sıralaması postposition'ın düşük kind-önceliğine (0) bağlı."""
    from turkgram.disambiguation import _KIND_PRIOR
    assert "postposition" not in _KIND_PRIOR, (
        "postposition _KIND_PRIOR'a eklenirse aşkın/başka homografı kırılır"
    )
```

- [ ] **Step 6: Task 3 golden'ını koş (GREEN)**

Run: `python -m pytest tests/test_postposition_analysis.py -q`
Expected: PASS (postposition okumaları geldi; homograf `noun` tepede; `_KIND_PRIOR` kilidi)

*Homograf testi kırmızıysa:* `analyze("aşkın")`'in `aşk+ın` decline (pos=noun) okumasını ürettiğini doğrula (`aşk` `_ROOTS`'ta olmalı). `postposition` `_KINDS` SONUNDA + `_KIND_PRIOR` dışında olduğundan sıralama düşük — motoru golden'a uydurma.

- [ ] **Step 7: Tam regresyon**

Run: `python -m pytest -q -m "not slow"`
Expected: PASS (4061 + yeni testler; geriye uyum kırılmadı)

- [ ] **Step 8: Commit**

```bash
git add turkgram/analysis.py tests/test_postposition_analysis.py
git commit -m "feat(analysis): _try_postposition_all — closed-set additive edat analizi"
```

---

## Task 5: `parse.py` — ADP kümesi genişletme + PP governs

**Files:**
- Modify: `turkgram/parse.py:13,18` (tablo import + ADP kümesi), `:42-63` (`PhraseNode.governs`), `:95-102` (`_POS_TO_TAG`), `:205-220` (R2)
- Test: `tests/test_parse.py`

- [ ] **Step 1: PP governs + donmuş edat ADP testini yaz (RED)**

`tests/test_parse.py` sonuna ekle:

```python
def test_pp_carries_governs():
    """R2 PP düğümü yönetilen durum kümesini taşır."""
    from turkgram import tokenize, parse_text
    from turkgram.parse import parse_phrase
    tokens = tokenize("ev için")
    analyses = parse_text("ev için")
    tree = parse_phrase(tokens, analyses)
    # ağaçta bir PP düğümü olmalı, governs={nom,gen}
    def find_pp(node):
        if getattr(node, "tag", None) == "PP":
            return node
        for ch in getattr(node, "children", ()):
            r = find_pp(ch)
            if r:
                return r
        return None
    pp = find_pp(tree)
    assert pp is not None, "PP düğümü kurulmadı"
    assert pp.governs == frozenset({"nom", "gen"})


def test_frozen_edat_forms_pp():
    """Donmuş edat (dair) ADP kümesinde → R2 PP kurar."""
    from turkgram.parse import _leaf_tag
    assert _leaf_tag("dair", None) == "ADP"
```

*(`parse_phrase`/`parse_text` çağrı imzalarını mevcut `tests/test_parse.py`'den doğrula; yukarıdaki iskelet gerekirse mevcut yardımcılarla hizala.)*

- [ ] **Step 2: Testi koş (RED)**

Run: `python -m pytest tests/test_parse.py::test_pp_carries_governs tests/test_parse.py::test_frozen_edat_forms_pp -v`
Expected: FAIL (`governs` alanı yok; `dair` ADP kümesinde değil)

- [ ] **Step 3: parse.py — tablo import + ADP kümesi (donmuş dahil)**

`turkgram/parse.py:13`:

```python
from .postposition import _POSTPOSITIONS as _POSTPOSITIONS_TABLE
```

`turkgram/parse.py:18`:

```python
# ADP tanıma: TÜM edatlar (donmuş dair/ilişkin/ait/yana dahil — aksi halde
# R2 'buna dair' için PP kurmaz).
_POSTPOSITIONS: frozenset[str] = frozenset(_POSTPOSITIONS_TABLE.keys())
```

- [ ] **Step 4: `PhraseNode`'a `governs` opsiyonel alanı ekle**

`turkgram/parse.py:42-63`, `PhraseNode`:

```python
@dataclass(frozen=True)
class PhraseNode:
    """Öbek düğüm — constituency ağaç düğümü."""
    tag: str
    children: tuple["PhraseNode | LeafNode", ...]
    surface: str
    governs: "frozenset[str] | None" = None   # yalnız PP; yönetilen durum kümesi

    @staticmethod
    def _collect_tokens(node: "PhraseNode | LeafNode") -> list[str]:
        if isinstance(node, LeafNode):
            return [node.token]
        return [t for child in node.children for t in PhraseNode._collect_tokens(child)]

    @classmethod
    def make(
        cls,
        tag: str,
        children: tuple["PhraseNode | LeafNode", ...],
        governs: "frozenset[str] | None" = None,
    ) -> "PhraseNode":
        """Factory — surface'i özyinelemeli hesaplar."""
        surface = " ".join(t for child in children for t in cls._collect_tokens(child))
        return cls(tag=tag, children=children, surface=surface, governs=governs)
```

**Not:** `governs` varsayılan `None` → mevcut `PhraseNode.make(...)` çağrıları ve eşitlik testleri DEĞİŞMEZ.

- [ ] **Step 5: `_POS_TO_TAG`'e postp ekle**

`turkgram/parse.py:95-101`:

```python
    _POS_TO_TAG = {
        "verb": "VERB",
        "noun": "NOUN",
        "adj":  "ADJ",
        "num":  "NUM",
        "conj": "CCONJ",
        "postp": "ADP",
    }
```

- [ ] **Step 6: R2'yi governs iliştirmek için güncelle**

`turkgram/parse.py:205-220` (`_apply_r2`):

```python
def _apply_r2(nodes: list) -> list:
    """R2: NP|NOUN ADP → PP (yönetilen durum işaretlemesiyle)."""
    out, i = [], 0
    while i < len(nodes):
        if (_tag(nodes[i]) in ("NP", "NOUN")
                and i + 1 < len(nodes)
                and _tag(nodes[i + 1]) == "ADP"):
            np_node = nodes[i]
            if isinstance(np_node, LeafNode):
                np_node = PhraseNode.make("NP", (np_node,))
            adp = nodes[i + 1]
            edat = adp.token.lower() if isinstance(adp, LeafNode) else adp.surface.lower()
            governs = _POSTPOSITIONS_TABLE.get(edat, {}).get("yönet")
            out.append(PhraseNode.make("PP", (np_node, adp), governs=governs))
            i += 2
        else:
            out.append(nodes[i])
            i += 1
    return out
```

- [ ] **Step 7: Testleri koş (GREEN)**

Run: `python -m pytest tests/test_parse.py -q`
Expected: PASS (governs + donmuş edat PP + mevcut parse testleri)

- [ ] **Step 8: Commit**

```bash
git add turkgram/parse.py tests/test_parse.py
git commit -m "feat(parse): PP governs alanı + donmuş edat ADP tanıma"
```

---

## Task 6: Hakem — korpus tarama + tam doğrulama

**Files:**
- Create: `tools/sweep_postposition_analysis.py`

- [ ] **Step 1: Korpus tarama aracını yaz**

`tools/sweep_postposition_analysis.py`:

```python
"""Edat analizi korpus taraması — 0 çökme + additive değişmez kontrolü."""
import sys
from turkgram.analysis import analyze
from turkgram.lexicon import load
from turkgram.postposition import _POSTPOSITIONS

def main():
    roots = load()
    crashes = 0
    # 1) Tüm 23 edat → postposition okuması var mı
    for edat in _POSTPOSITIONS:
        try:
            kinds = [a.kind for a in analyze(edat, roots=roots)]
            if "postposition" not in kinds:
                print(f"MISS: {edat} postposition okuması yok")
        except Exception as e:
            crashes += 1
            print(f"CRASH {edat!r}: {e}")
    # 2) Leksikon geneli çökme taraması (edat dalı her token'da çalışır)
    for i, lemma in enumerate(roots):
        try:
            analyze(lemma, roots=roots)
        except Exception as e:
            crashes += 1
            print(f"CRASH {lemma!r}: {e}")
        if i % 5000 == 0:
            print(f"...{i} lemma tarandı", flush=True)
    print(f"\nTARAMA BİTTİ. Çökme: {crashes}")
    return 1 if crashes else 0

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Taramayı koş**

Run: `PYTHONUTF8=1 python tools/sweep_postposition_analysis.py`
Expected: `Çökme: 0`, MISS satırı yok.

- [ ] **Step 3: Adversarial hakem (3-5 oy) — CLAUDE.md §2**

Karmaşık/hataya-açık kısımlar için subagent hakem dispatch et:
1. `yönet` kümesi konsolidasyonu ile-gibi-kadar zamir-genitifini gerçekten koruyor mu? (drift-lock golden yeterli mi)
2. Homograf sıralaması (`aşkın`/`başka`) tüm leksikon bağlamlarında doğru mu, yoksa golden'daki 2 örneğe mi özgü?
3. PP governs iliştirmesi hiçbir mevcut parse ağacını (E2/E3/E4 testleri) kırmıyor mu?

- [ ] **Step 4: Tam paket + slow round-trip**

Run: `python -m pytest -q` sonra `python -m pytest -q -m slow`
Expected: PASS (regresyonsuz)

- [ ] **Step 5: Commit + belge**

```bash
git add tools/sweep_postposition_analysis.py
git commit -m "test(sweep): edat analizi korpus taraması (0 çökme hakem)"
```

Ardından CLAUDE.md §7 + README + memory `faz-durumu.md` güncellenir (edat analizi TAMAMLANDI, test sayısı).

---

## Bitiş Kontrol Listesi

- [ ] `postposition()` üretim çıktısı DEĞİŞMEZ (86-girdi golden yeşil)
- [ ] K2 mevcut 19 edat davranışı DEĞİŞMEZ (drift-lock + context testleri yeşil)
- [ ] `analyze()` 23 edat için postposition okuması döner (roots=None dahil)
- [ ] Homograf sıralaması doğru (`aşkın`=isim, `başka`=sıfat tepede)
- [ ] PP düğümü `governs` taşır; donmuş edat PP kurar
- [ ] `PhraseNode.governs` varsayılan None → mevcut testler kırılmaz
- [ ] Korpus tarama 0 çökme
- [ ] Tam paket regresyonsuz + slow round-trip yeşil
- [ ] Docs güncel (CLAUDE.md §7, README, memory)
