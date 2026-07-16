# Faz 6 — Derivasyonel Morfoloji: Tam Paket

**Tarih:** 2026-07-16  
**Kapsam:** `derivation.py` tamamlama + `analysis.py` entegrasyonu + TR API  
**Hedef:** Tek katman leksik türetme üretimi + oracle analizi + Türkçe sarmalayıcı

---

## 1. Motivasyon

Faz 0–5 infleksiyonel morfolojiyi (çekim, ulaç, çatı, sözdizimi, zamir, sıfat, sayı, edat, bağlaç) kapattı. `derivation.py` iskelet halinde mevcut; `derivations()` üreticisi çalışıyor ancak:

- `analysis.py` entegrasyonu yok — `analyze("gözlük")` türetmeyi görmüyor
- Resmi SPEC yok; mevcut testler informel
- `türet()` TR API zaten `tr.py:288`'de mevcut; `derivations` `__init__.py`'de zaten export edilmiş

Faz 6 yalnız **analiz entegrasyonu** ekler; mevcut API'ye dokunmaz.

---

## 2. Kapsam Kararları

| Karar | Seçim | Gerekçe |
|---|---|---|
| Analiz entegrasyonu | Evet | Kütüphane tam değil |
| Türetme derinliği | Tek katman | Aday patlaması; zincir defer |
| Fiilimsi/çatı analizde | Dışla | `nonfinite`/`voice` zaten karşılıyor |
| Analiz yaklaşımı | Oracle (A-by-G) | Kanıtlanmış desen, precision kontrolü |
| TR API | Mevcut `türet()` korunur | `tr.py:288` + `_TUR` map zaten doğru |
| `__init__.py` export | Dokunulmaz | `derivations` zaten `__all__`'da |

---

## 3. Modüller

### 3.1 `derivation.py` (küçük revize)

Mevcut `derivations(headword, pos)` **değişmez**. Eklenen:

**`_LEXICAL_SUFFIXES`** sabiti — analiz için kullanılacak (category, label) çiftleri. Dışlama **(category, label) ikilisiyle** yapılır (label string'e göre değil — `-Ar-` çakışması için kritik):

| Kategori | Ekler |
|---|---|
| isim → isim | `-lIk`, `-CI`, `-lI`, `-sIz`, `-CIk`, `-DAş`, `-CA`, `-CIl` |
| isim → fiil | `-lA-`, `-lAn-`, `-lAş-`, `-Al-`, `-A-`, `-sA-`, `-ImsA-`, `-Ar-` |
| fiil → isim (leksik) | `-Im`, `-gI`, `-gIn`, `-gAn`, `-Ak`, `-I`, `-mAn`, `-IcI`, `-Ik`, `-Inç`, `-IntI` |

**`-Ar-` çakışma notu:** `-Ar-` hem `_NOUN_TO_VERB` (isim→fiil: morar-, sarar-) hem `_VERB_TO_VERB` (fiil→fiil ettirgen: çıkar-, kopar-) içinde bulunur. `_LEXICAL_SUFFIXES` yalnız `("isim → fiil", "-Ar-")` kategorisini içerir; `("fiil → fiil (çatı)", "-Ar- (ettirgen)")` dışlanır. Exclusion kategoriden yapılır, label'dan değil.

**Dışlananlar (analiz için) — `(category, label)` çifti:**
- Tüm `_FIILIMSI` kategorisi → CLAUDE.md §6 uyarınca `kind="converb"/"participle"` zaten karşılıyor
- `("fiil → fiil (çatı)", *)` tümü → `voice.py` + `kind="conjugate"(voice_chain=)` zaten karşılıyor
- Özellikle: `("fiil → fiil (çatı)", "-Ar- (ettirgen)")` dışlanır; `("isim → fiil", "-Ar-")` **dahildir**

**`_DERIVED_POS`** yardımcısı — türetilmiş sözcüğün POS'u:

```python
_DERIVED_POS: dict[str, str] = {
    # isim→isim (sıfat üretenler adj, diğerleri noun)
    "-lI": "adj",        # kirli, tuzlu
    "-sIz": "adj",       # evsiz, tuzsuz
    "-CIl": "adj",       # evcil, bencil
    "-CA": "adj",        # Türkçe, insanca (zarflaşabilir ama başlangıç pos=adj)
    # isim→isim (noun)
    "-lIk": "noun",      # gözlük, kitaplık
    "-CI": "noun",       # gözcü, kitapçı
    "-CIk": "noun",      # küçücük — diminutive; noun umbrella
    "-DAş": "noun",      # meslektaş
    # isim→fiil
    "-lA-": "verb",      # gözlemek
    "-lAn-": "verb",     # evlenmek
    "-lAş-": "verb",     # gözleşmek
    "-Al-": "verb",      # azalmak
    "-A-": "verb",       # yaşamak
    "-sA-": "verb",      # susamak
    "-ImsA-": "verb",    # benimsemek
    "-Ar-": "verb",      # morarmak (isim→fiil)
    # fiil→isim / fiil→sıfat
    "-IcI": "adj",       # yapıcı, alıcı (çoğunlukla sıfat)
    "-gAn": "adj",       # çalışkan, atılgan
    "-Ik": "adj",        # açık, kesik, bozuk
    "-Im": "noun",       # ölüm, seçim
    "-gI": "noun",       # sevgi, bilgi
    "-gIn": "adj",       # yorgun, düşkün
    "-Ak": "noun",       # durak, kaçak
    "-I": "noun",        # yazı, sürü
    "-mAn": "noun",      # yönetmen, öğretmen
    "-Inç": "noun",      # sevinç, korkunç
    "-IntI": "noun",     # akıntı, esinti
}
```

**Tasarım kararı (M1):** `_DERIVED_POS` suffix etiketine göre POS atar; `-lI`/`-sIz`/`-CIl`/`-CA`/`-IcI`/`-gAn`/`-Ik`/`-gIn` sıfat olarak etiketlenir. Bu `_POS` kümesinde `"adj"` zaten mevcut (`analysis.py:67`). Kalan isim/fiil üretenler için `is_verb` flag'i yeterli.

### 3.2 `analysis.py` (genişletme)

**`_try_derivation_all(surface, roots)`** — yeni fonksiyon, mevcut `_try_number_all` emsali:

```python
def _try_derivation_all(surface, roots):
    results = []
    for (cat, label, src_pos) in _LEXICAL_SUFFIXES:
        for root in _strip_derivation(surface, label, src_pos):
            if roots is not None and root not in roots:
                continue
            derived = derivations(root, src_pos)
            if not derived:
                continue
            for r in derived:
                if r["form"] == surface and r["suffix"] == label:
                    derived_pos = _DERIVED_POS.get(label, "noun")
                    segs = _segs_to_tuple([
                        (root, "kök"),
                        (surface[len(root):], label),
                    ])
                    results.append(Analysis(
                        kind="derivation",
                        lemma=root,
                        pos=derived_pos,
                        kwargs={"suffix": label, "src_pos": src_pos},
                        segments=segs,
                        hypothetical=(roots is None),
                    ))
    return results
```

**`_strip_derivation(surface, label, src_pos_hint)`** — ters soyma:

Her suffix label için beklenen son sesler hesaplanır ve yüzeyden soyulur. Ters harmoni: suffix'in son ünlüsünün tüm alloformları denenir (ör. `-lIk` için `lük/luk/lik/lık` — 4 varyant). Ünlü-final kök + ünlü-başlı ek → kaynaştırma `-y-`: soyulurken son `y` de atılır.

**Soyma sınırı (kabul edilen, M2 çözümü):** Ters harmoni `_root_candidates` ile aynı nitelikte bir sınır. İnhimak/disharmonic alıntılar ve bazı nadir ünlü-düşmeli kökler pre-existing olarak kaçabilir; bu sınır SPEC'te belgelenir, kod hata fırlatmaz. Recall-safe: hatalı soyma oracle'dan döner (`form != surface`), precision'ı bozmaz.

**`Analysis` yapısı notu (C1):** Mevcut `Analysis` dataclass `kwargs` dict içerir; `suffix`/`src_pos` top-level field değildir. `kwargs={"suffix": label, "src_pos": src_pos}` ile kurulur; `segments` ve `hypothetical` zorunlu alanlar mevcut `_try_number_all` emsaliyle doldurulur.

**`_KINDS` ve `_POS` güncellemesi:**
- `_KINDS` → `"derivation"` SONA eklenir (`_sort_key` infleksiyonu derivasyona tercih eder)
- `_POS` → `"adj"` zaten var; `"noun"` + `"verb"` zaten var; değişiklik gerekmez

**`analyze()` entegrasyonu:**
- `_try_derivation_all` çağrısı mevcut `_try_*_all` zincirinin **sonuna** eklenir (düşük öncelik)

### 3.3 TR API — değişiklik yok

`tr.py:288`'deki `türet(kelime, tür)` **korunur**. `_TUR` haritası zaten `compound_verb`/`compound_noun` ve ASCII alias'larını kapsar. Spec'e yeni sarmalayıcı yazılmaz.

`tr.çözümle` zaten `analyze()` çağırıyor; yeni `kind="derivation"` otomatik gelir.

### 3.4 `__init__.py` — değişiklik yok

`derivations` zaten `__all__`'da (`:68`, `:110`). Export'a dokunulmaz.

---

## 4. Analiz Eksenleri (Analysis.kwargs)

```python
Analysis(
    kind="derivation",
    lemma="göz",                           # kaynak kök
    pos="noun",                            # türetilmiş sözcüğün POS'u
    kwargs={"suffix": "-lIk", "src_pos": "noun"},
    segments=_segs_to_tuple([("göz", "kök"), ("lük", "-lIk")]),
    hypothetical=True,                     # roots=None ise True
)
```

**Segment notu:** `_segs_to_tuple` (`analysis.py`) `Segment` namedtuple listesi üretir; `"kök"` etiketi `_try_number_all` emsaliyle tutarlı (İngilizce `"root"` değil).

Örnek çıkışlar:

| Yüzey | lemma | pos | suffix | src_pos |
|---|---|---|---|---|
| gözlük | göz | noun | -lIk | noun |
| kirli | kir | adj | -lI | noun |
| gözsüz | göz | adj | -sIz | noun |
| gözlemek | göz | verb | -lA- | noun |
| yapıcı | yapmak | adj | -IcI | verb |
| seviş | sevmek | noun | -Iş | verb |

---

## 5. Precision / Recall Garantileri

**Precision:**
- `roots=` filtresi aktifse yalnız leksikonda olan root'lar → gürültü elenir
- Oracle doğrulama: `r["form"] == surface and r["suffix"] == label` yanlış pozitif engeller
- Exclusion `(category, label)` çiftiyle yapılır — `-Ar-` çakışmasını doğru çözer
- `_KINDS` sonuna eklenme: infleksiyonel kind'lar disambiguate'de türetmeden önce gelir

**Recall sınırı (kabul edilmiş):**
- Ters harmoni kademeli: 4 ünlü varyant × glide kaldırma → major root'ları yakalar
- Disharmonic alıntılar (`inhimak`), rare ünlü-düşme (`nakil`) pre-existing `_root_candidates` sınırıyla aynı — belgelenir, "derivation-özgü" değil

---

## 6. Test Stratejisi

| Dosya | İçerik | Sorumlu |
|---|---|---|
| `spec/derivation-spec.md` | Gramer SPEC (elle) | Ana oturum |
| `tests/golden_derivation.py` | Mevcut üretici testler zaten var | — |
| `tests/golden_derivation_analysis.py` | Analiz golden (motor-körü) | Opus subagent |
| `tests/test_derivation.py` | Mevcut runner — `_LEXICAL_SUFFIXES` + `_DERIVED_POS` testleri eklenir | Motor |
| `tests/test_derivation_analysis.py` | Yeni analiz runner | Motor |

**Hakem:** Opus adversarial — CRITICAL/HIGH/MEDIUM sıfır hedef.

**Korpus taraması:** `lexicon.load()` (26k lemma) × leksik suffix sayısı (19 suffix). Beklenen call-count: ~26k × 19 × avg-candidate ≈ ~500k oracle çağrı; mevcut round-trip sweep'leriyle tutarlı. 0 çökme + 0 kategori-özgü miss hedefi.

---

## 7. Uygulama Sırası

1. `spec/derivation-spec.md` — SPEC yazımı (elle, gramer referansından)
2. `derivation.py` revize — `_LEXICAL_SUFFIXES` + `_DERIVED_POS` sabitleri; `derivations()` değişmez
3. `tests/test_derivation.py` — yeni sabitleri doğrulayan testler eklenir
4. `tests/golden_derivation_analysis.py` — bağımsız analiz golden (Opus, motor-körü)
5. `analysis.py` — `_strip_derivation` + `_try_derivation_all` + `analyze()` zincire ekleme
6. `tests/test_derivation_analysis.py` — analiz runner
7. Hakem (Opus adversarial)
8. Korpus tarama + regresyon (`pytest`)

**Değişmeyen:** `tr.py`, `__init__.py` — dokunulmaz.

---

## 8. Değişmezler (CLAUDE.md uyumu)

- Motor biçim **saklamaz** — `derivations()` runtime üretir, disk yok
- Fiilimsi/çatı `derivation.py`'de üretici olarak kalabilir; yalnız **analiz** dışlanır (`_LEXICAL_SUFFIXES`)
- `analyze(roots=None)` davranışı değişmez — türetme aday kümesi eklenir, önceki sonuçlar etkilenmez
- `türet()` ve `derivations` export'u mevcut halinde korunur (H1, H2 çözümü)
- Telif: yeni gramer kuralı = olgu, telifli değil; Korkmaz düzyazısı/örneği KOPYALANMAZ
- `_KINDS` sonuna ekleme: `_sort_key` infleksiyonu tercih eder, geriye-uyumlu
