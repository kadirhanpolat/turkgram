# Faz 5 D2 — Edat/İlgeç Yönetimi + D3 Sayı Çözümlemesi Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `postposition.py` ile ~20 Türkçe edatın kapalı-küme yönetimi; decline() entegrasyonu; zamir desteği; D3'te `analyze()` içinde `ordinal`/`distributive` kind'ları.

**Architecture:** CLAUDE.md §2 akışı: SPEC (ana oturum) → bağımsız golden (Opus, motor-körü) → motor → hakem. D2 ve D3 ayrı mini-döngüler. Motor yeni morfoloji oluşturmaz — mevcut `decline()` oracle'ına delege eder.

**Tech Stack:** Python 3.10+, pytest, turkgram.morphology_noun.decline(), turkgram.analysis.analyze()

---

## Dosya Haritası

| İşlem | Dosya | Sorumluluk |
|-------|-------|------------|
| CREATE | `spec/postposition-spec.md` | Edat kapalı-kümesi, durum tablosu, ile allomorfu, SPEC |
| CREATE | `turkgram/postposition.py` | `postposition(lemma, edat, bitisik=False)` |
| CREATE | `tests/golden_postposition.py` | Bağımsız golden veri (Opus, motor-körü) |
| CREATE | `tests/test_postposition.py` | Parametrik runner |
| MODIFY | `turkgram/__init__.py` | `postposition` export |
| MODIFY | `turkgram/tr.py` | `edat_obeği(isim, edat, bitisik=False)` sarmalayıcı |
| CREATE | `tests/golden_number_analysis.py` | D3 ordinal/distributive analiz golden (Opus) |
| CREATE | `tests/test_number_analysis.py` | D3 runner |
| MODIFY | `turkgram/analysis.py` | D3: `_try_number_all()` + ordinal/distributive kind |

---

## Phase 1 — D2 SPEC (Ana Oturum)

### Task 1: postposition-spec.md Yaz

**Files:** CREATE `spec/postposition-spec.md`

- [ ] **Adım 1:** `spec/postposition-spec.md` oluştur. İçerik:

  **§1 Kapsam** — kapalı küme (~20 edat), kapsam dışı (sözdizimsel edatlar, defer).

  **§2 Edat–Durum Tablosu:**

  | Edat | Yönettiği durum | Örnek |
  |------|-----------------|-------|
  | için | gen | evin için |
  | ile (ayrı) | nom | ev ile |
  | ile (bitişik -lA) | ins | evle / eviyle |
  | göre | dat | eve göre |
  | kadar | dat | eve kadar |
  | karşı | dat | eve karşı |
  | rağmen | dat | eve rağmen |
  | doğru | dat | eve doğru |
  | dek | dat | eve dek |
  | değin | dat | eve değin |
  | üzere | dat | eve üzere |
  | önce | abl | evden önce |
  | sonra | abl | evden sonra |
  | beri | abl | evden beri |
  | itibaren | abl | evden itibaren |
  | başka | abl | evden başka |
  | dolayı | abl | evden dolayı |
  | ötürü | abl | evden ötürü |
  | gibi | nom | ev gibi |
  | aşkın | acc | evi aşkın |

  **§3 ile allomorfu** — ayrı vs bitişik:
  - Ayrı: `decline(lemma, case='nom') + ' ile'`
  - Bitişik: `decline(lemma, case='ins')` (ins hali zaten -lA eki = ile morfolojik muadili)
  - `postposition(lemma, 'ile', bitisik=True)` → ins biçimini döndürür, ' ile' EKLEMEz

  **§4 Zamir entegrasyonu** — `decline()` zaten zamir morfolojisini bilir (ben→benim/bana, o→onun/ona). `postposition()` DOĞRUDAN `decline()` çağırır; zamir özel kodu YOKTUR.

  **§5 API:**
  ```python
  postposition(lemma: str, edat: str, bitisik: bool = False) -> str
  # lemma: Türkçe kelime kökü (ev, okul, ben, o)
  # edat: edat adı (küçük harf Türkçe)
  # bitisik: yalnız 'ile' için geçerli; True → ins biçimi döner (evle)
  # Döner: tam edat öbeği ("evin için", "evle")
  # Hata: bilinmeyen edat → ValueError (geçerli listeyle)
  # Hata: bitisik=True + edat!='ile' → ValueError
  ```

  **§6 Kapsam Dışı:**
  - Çok-kelimeli edat öbekleri (bir türlü, ilgili olarak) → sözdizimsel, defer
  - Edat çözümlemesi (analyze) → sözdizimsel bağlam gerektirir, defer (CLAUDE.md §7 D3 notu)

- [ ] **Adım 2:** SPEC'i gözden geçir — dilbilgisi doğruluğu, kapsam netliği.

---

## Phase 2 — D2 Bağımsız Golden (Opus Subagent, Motor-Körü)

### Task 2: Golden Subagent Dispatch

**Files:** CREATE `tests/golden_postposition.py`

- [ ] **Adım 1:** Opus subagent'a gönder. Prompt:

  > Sen bağımsız bir dilbilim uzmanısın. `turkgram/postposition.py` DOSYASINI GÖRME — yalnız `spec/postposition-spec.md` ve temel Türkçe dilbilgisini kullan.
  >
  > `tests/golden_postposition.py` dosyasını yaz. İçerik: saf Python dict listesi `GOLDEN = [...]`, her giriş:
  > ```python
  > {"lemma": "ev", "edat": "için", "bitisik": False, "expected": "evin için"}
  > ```
  > Kapsam: aşağıdaki kombinasyonlar, elle doğrulanmış:
  > - Her edattan en az 1 örnek (§2 tablodaki ~20 edat)
  > - Ünsüz-final isim: ev, okul, kap
  > - Ünlü-final isim: araba, köy, ağaç
  > - Zamir: ben, sen, o, biz, siz, onlar, bu, şu
  > - ile ayrı (bitisik=False) + ile bitişik (bitisik=True) — ünlü-final ve ünsüz-final
  > - Minimum 60 giriş
  >
  > YALNIZ saf veri: `GOLDEN = [...]` listesi. Test kodu yazma, import yapma.
  > Motor çıktısını TAHMİN ETME — kendi dilbilgisi bilginle türet.

- [ ] **Adım 2:** Golden sonucu `tests/golden_postposition.py`'a kaydet.

- [ ] **Adım 3:** Golden'ı elle oku — açık hatalar varsa düzelt (motor-körü doğrulama).

---

## Phase 3 — D2 Motor İmplementasyonu

### Task 3: postposition.py

**Files:** CREATE `turkgram/postposition.py`

- [ ] **Adım 1:** Motor yaz:

  ```python
  """postposition.py — Türkçe edat/ilgeç yönetimi."""
  from __future__ import annotations
  from .morphology_noun import decline

  _POSTPOSITION_CASE: dict[str, str] = {
      "için":    "gen",
      "ile":     "nom",   # ayrı; bitisik=True ise ins
      "göre":    "dat",
      "kadar":   "dat",
      "karşı":   "dat",
      "rağmen":  "dat",
      "doğru":   "dat",
      "dek":     "dat",
      "değin":   "dat",
      "üzere":   "dat",
      "önce":    "abl",
      "sonra":   "abl",
      "beri":    "abl",
      "itibaren":"abl",
      "başka":   "abl",
      "dolayı":  "abl",
      "ötürü":   "abl",
      "gibi":    "nom",
      "aşkın":   "acc",
  }


  def postposition(lemma: str, edat: str, bitisik: bool = False) -> str:
      """İsim lemmasi + edat → edat öbeği.

      bitisik=True yalnız 'ile' için: decline(lemma, case='ins') → evle/eviyle.
      """
      if edat not in _POSTPOSITION_CASE:
          raise ValueError(
              f"Bilinmeyen edat: {edat!r}. Geçerliler: {sorted(_POSTPOSITION_CASE)}"
          )
      if bitisik and edat != "ile":
          raise ValueError(f"bitisik=True yalnız 'ile' için geçerlidir, {edat!r} değil.")
      if bitisik:
          return decline(lemma, case="ins")
      case = _POSTPOSITION_CASE[edat]
      declined = decline(lemma, case=case)
      return declined + " " + edat
  ```

- [ ] **Adım 2:** `turkgram/__init__.py`'a export ekle: `from .postposition import postposition`.

- [ ] **Adım 3:** `turkgram/tr.py`'a sarmalayıcı ekle:

  ```python
  from .postposition import postposition as _postposition

  def edat_obeği(isim: str, edat: str, bitisik: bool = False) -> str:
      """İsim + edat → edat öbeği (Türkçe API)."""
      return _postposition(isim, edat, bitisik)
  ```

### Task 4: Test Runner Yaz

**Files:** CREATE `tests/test_postposition.py`

- [ ] **Adım 1:** Runner yaz:

  ```python
  import pytest
  from tests.golden_postposition import GOLDEN
  from turkgram import postposition

  @pytest.mark.parametrize("case", GOLDEN, ids=[
      f"{g['lemma']}+{g['edat']}{'(bit)' if g.get('bitisik') else ''}" for g in GOLDEN
  ])
  def test_postposition(case):
      result = postposition(case["lemma"], case["edat"], case.get("bitisik", False))
      assert result == case["expected"], (
          f"postposition({case['lemma']!r}, {case['edat']!r}) = {result!r}, "
          f"beklenen {case['expected']!r}"
      )
  ```

- [ ] **Adım 2:** Testleri koş:
  ```
  PYTHONUTF8=1 python -m pytest tests/test_postposition.py -v
  ```
  Başarısız testleri analiz et; motor hatalarını düzelt (golden'ı değiştirme).

- [ ] **Adım 3:** Tüm test paketi regresyon kontrolü:
  ```
  PYTHONUTF8=1 python -m pytest --ignore=tests/test_slow_roundtrip.py -q
  ```
  Sıfır regresyon beklenir.

- [ ] **Adım 4:** Commit:
  ```
  git add spec/postposition-spec.md turkgram/postposition.py turkgram/__init__.py turkgram/tr.py tests/golden_postposition.py tests/test_postposition.py
  git commit -m "feat(postposition): edat öbeği motoru (~20 edat, decline entegrasyonu, zamir)"
  ```

---

## Phase 4 — D2 Hakem (Opus Adversarial)

### Task 5: Hakem Subagent

- [ ] **Adım 1:** Opus subagent'a gönder:

  > `spec/postposition-spec.md` + `turkgram/postposition.py` + `tests/golden_postposition.py` oku.
  > Adversarial hakem: aşağıdaki soruları cevapla.
  > 1. SPEC'te tanımlanan her edat implementasyonda var mı?
  > 2. `ile` allomorfu (ayrı vs bitişik) doğru mı? Ünlü-final glide (-y-) var mı?
  > 3. Zamir decline() entegrasyonu doğru mu? ben/benim/bana, o/onun/ona...
  > 4. `bitisik=True + edat!='ile'` ValueError fırlatıyor mu?
  > 5. Bilinmeyen edat ValueError + liste veriyor mu?
  > 6. Golden'da gözden kaçan hata var mı? (Elle 5 rasgele giriş doğrula.)
  > 7. `postposition-spec.md §6 kapsam dışı` — SPEC dışında gizlice eklenen özellik var mı?
  >
  > Bulgular: CRITICAL / HIGH / MEDIUM / LOW + öneri.

- [ ] **Adım 2:** CRITICAL + HIGH bulguları gider, testi yeniden koş.

- [ ] **Adım 3:** CLAUDE.md `§7 Faz 5 D2 ✅` notunu güncelle.

---

## Phase 5 — D3 Sayı Çözümlemesi

### Task 6: D3 SPEC Hazırlığı + Bağımsız Golden

**Files:** CREATE `tests/golden_number_analysis.py`

Referans: `spec/number-spec.md` §1-§3 (zaten mevcut). D3 için ek SPEC bölümü gerekmiyor — kind tanımı CLAUDE.md §7'de açık.

- [ ] **Adım 1:** Opus subagent golden:

  > `spec/number-spec.md` + `turkgram/number.py` çıktılarını kullan — ancak `analysis.py`'yı GÖRME.
  > `tests/golden_number_analysis.py` yaz: `GOLDEN = [...]`, her giriş:
  > ```python
  > {"surface": "birinci", "lemma": "bir", "kind": "ordinal", "axes": {}}
  > {"surface": "ikişer", "lemma": "iki", "kind": "distributive", "axes": {}}
  > ```
  > Kapsam: ordinal (1-10 + bileşik 2 örnek) + distributive (1-10 + bileşik 2 örnek).
  > Toplam ≥ 24 giriş. Saf veri — test kodu yazma.

- [ ] **Adım 2:** Golden'ı `tests/golden_number_analysis.py`'a kaydet.

### Task 7: D3 Motor — analysis.py Genişletme

**Files:** MODIFY `turkgram/analysis.py`

- [ ] **Adım 1:** `analysis.py`'da `_try_number_all()` ekle:

  ```python
  from .number import ordinal, distributive

  def _try_number_all(surface: str) -> list[Analysis]:
      """Ordinal/distributive analiz — analysis-by-generation."""
      results = []
      # Ordinal: gövde -(I)ncI ile bitiyor mu?
      # Distributive: gövde -(ş)Ar ile bitiyor mu?
      # Her ikisi için de: kök adaylarını türet, oracle'ı sına
      ...
  ```

  **Implementasyon notu:** Ordinal suffix pattern: `[ıiuü]nc[ıiuü]$` (ünsüz-final) veya `nc[ıiuü]$` (ünlü-final). Distributive: `şer|şar|er|ar$`. Brute-force: leksikondaki sayı köklerini gezdirip `ordinal/distributive(kök)==surface` oracle'ını sor.

  Daha pratik yaklaşım: önek kesme. `ordinal` suffix min 3 char, `distributive` suffix min 2 char. Suffix çıkar → aday kök → `ordinal(aday)==surface`? Evet → `Analysis(lemma=aday, kind='ordinal', axes={}, segments=[...])`.

- [ ] **Adım 2:** `analyze()` içinde `_try_number_all()` çağrısını entegre et (diğer `_try_*` fonksiyonlarının yanına).

- [ ] **Adım 3:** `tr.py` `çözümle()` sarmalayıcısı zaten `analyze()` çağırdığından otomatik çalışır — test et.

### Task 8: D3 Runner + Hakem

**Files:** CREATE `tests/test_number_analysis.py`

- [ ] **Adım 1:** Runner:

  ```python
  import pytest
  from tests.golden_number_analysis import GOLDEN
  from turkgram.analysis import analyze

  @pytest.mark.parametrize("case", GOLDEN, ids=[g["surface"] for g in GOLDEN])
  def test_number_analysis(case):
      results = analyze(case["surface"])
      found = [r for r in results if r.lemma == case["lemma"] and r.kind == case["kind"]]
      assert found, (
          f"analyze({case['surface']!r}): {case['lemma']!r}/{case['kind']!r} bulunamadı. "
          f"Sonuçlar: {[(r.lemma, r.kind) for r in results]}"
      )
  ```

- [ ] **Adım 2:** Testleri koş:
  ```
  PYTHONUTF8=1 python -m pytest tests/test_number_analysis.py -v
  ```

- [ ] **Adım 3:** Regresyon:
  ```
  PYTHONUTF8=1 python -m pytest --ignore=tests/test_slow_roundtrip.py -q
  ```

- [ ] **Adım 4:** Hakem subagent (Opus) — D3 için:

  > `analysis.py`'daki `_try_number_all()` + `tests/golden_number_analysis.py` oku. Adversarial:
  > 1. Suffix tespiti recall-güvenli mi (yanlış budama var mı)?
  > 2. Bileşik sayı yüzeyleri (yirmi birinci, kırk ikişer) çözülüyor mu?
  > 3. Yanlış pozitif riski var mı (sayı olmayan kelimeler yanlış ordinal/distributive olarak mı analiz ediliyor)?
  > 4. `analyze()` imzası DEĞİŞTİRİLMEDİ mi? (`roots=None` davranışı korundu mu?)

- [ ] **Adım 5:** Commit:
  ```
  git add turkgram/analysis.py tests/golden_number_analysis.py tests/test_number_analysis.py
  git commit -m "feat(analysis): ordinal + distributive kind desteği (D3)"
  ```

- [ ] **Adım 6:** CLAUDE.md `§7 Faz 5 D2+D3 ✅` güncelle + memory güncelle.

---

## Başarı Kriterleri

- [ ] D2: ~20 edat × temsili isimler × zamir = ≥60 test, hepsi yeşil
- [ ] D3: ≥24 ordinal/distributive analiz testi, hepsi yeşil
- [ ] Tam paket regresyon = 0
- [ ] Hakem CRITICAL/HIGH bulgu = 0
- [ ] `analyze()` imzası değişmedi, `roots=None` davranışı korundu
