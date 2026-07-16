# Faz 9c — Lemmatizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `turkgram/lemmatize.py` modülü — yüzey biçimden lemma döndüren sade+zengin API; fallback zinciri (analyze → spellcheck → None); bağlamsal `lemmatize_text`.

**Architecture:** Mevcut pipeline'ın (`analyze` → `disambiguation.disambiguate` → `context.rank_in_context`) ince sarmalayıcısı. Ortak `_lemmatize_inner` özel yardımcısı kod tekrarını önler. `lemmatize_text`: `roots=None` → `parse_text` kısayolu, aksi → per-token `analyze` döngüsü.

**Tech Stack:** Python 3.10+, pytest, `turkgram.analysis`, `turkgram.disambiguation`, `turkgram.context`, `turkgram.spellcheck`, `turkgram.tokenize`

**Spec:** `docs/superpowers/specs/2026-07-17-faz9c-lemmatizer-design.md`

---

## Dosya Haritası

| Dosya | İşlem | Sorumluluk |
|---|---|---|
| `turkgram/lemmatize.py` | Oluştur | `LemmaResult`, `_lemmatize_inner`, public API |
| `turkgram/__init__.py` | Güncelle | `lemmatize*`, `LemmaResult` export |
| `turkgram/tr.py` | Güncelle | `temel_biçim*` TR sarmalayıcılar |
| `tests/golden_lemmatize.py` | Oluştur | Bağımsız golden (motor-körü, Opus) |
| `tests/test_lemmatize.py` | Oluştur | Pytest runner |
| `tools/sweep_lemmatize.py` | Oluştur | 26k leksikon korpus taraması |

---

## Task 1: Bağımsız Golden Oluştur

**Dosyalar:**
- Oluştur: `tests/golden_lemmatize.py`

Bu görev **motoru görmeden** tamamlanmalı. Bir Opus subagent'ına dispatch edilir.

- [ ] **Adım 1: Opus subagent'ına golden yaz**

  Subagent prompt (motor-körü):

  > Sen turkgram projesinin bağımsız test golden'ı yazıyorsun.
  > SADECE spec dosyasını ve Türkçe dilbilgisi kurallarını kullan.
  > `turkgram/lemmatize.py` DOSYASINA BAKMA — motoru görme.
  >
  > Spec: `docs/superpowers/specs/2026-07-17-faz9c-lemmatizer-design.md`
  >
  > `tests/golden_lemmatize.py` dosyasını yaz. İçerik:
  > ```python
  > # Bağımsız golden — motor GÖRÜLMEDEN elle-doğrulanmış lemma beklentileri.
  > # Her giriş: (surface, expected_lemma_or_None)
  > # corrected=True beklentisi ayrı: CORRECTED_CASES = [(surface, lemma), ...]
  >
  > LEMMATIZE_CASES: list[tuple[str, str | None]] = [
  >     # fiil çekim → lemma
  >     ("geliyorum", "gelmek"),
  >     ("okumuştu", "okumak"),
  >     ("gidecekler", "gitmek"),
  >     ("yapıyordum", "yapmak"),
  >     ("söylemiş", "söylemek"),
  >     # isim + durum → lemma
  >     ("evlerde", "ev"),
  >     ("kitabın", "kitap"),
  >     ("masaya", "masa"),
  >     ("kapıdan", "kapı"),
  >     ("arabaları", "araba"),
  >     # zamir
  >     ("bana", "ben"),
  >     ("seni", "sen"),
  >     ("onun", "o"),
  >     # sıfat
  >     ("güzelce", "güzel"),
  >     # bileşik token
  >     ("göz ardı etti", "göz ardı etmek"),
  >     # spellcheck fallback (yanlış yazım → düzeltilmiş lemma)
  >     # NOT: 'dag' kullan, 'seker' değil (seker = sekmek geniş 3sg → GEÇERLİ)
  >     ("dag", "dağ"),
  >     ("gozluk", "gözlük"),
  >     ("kapi", "kapı"),
  >     # None beklentisi
  >     ("xyzabc", None),
  >     ("qqqqq", None),
  >     # noktalama → None
  >     (".", None),
  >     (",", None),
  > ]
  >
  > # corrected=True beklentisi (spellcheck fallback tetiklenen)
  > CORRECTED_CASES: list[tuple[str, str]] = [
  >     ("dag", "dağ"),
  >     ("gozluk", "gözlük"),
  >     ("kapi", "kapı"),
  > ]
  >
  > # lemmatize_text cümle testleri
  > TEXT_CASES: list[tuple[str, list[str | None]]] = [
  >     ("Ali eve geldi", ["ali", "ev", "gelmek"]),
  >     ("Kitabı okudum", ["kitap", "okumak"]),
  > ]
  > ```
  >
  > Her `lemma` değerini dilbilgisinden doğrula — motora BAKMA.
  > Emin olmadığın girişleri ekleme, az ama doğru olsun.

- [ ] **Adım 2: Golden dosyasının mevcut olduğunu doğrula**

  ```bash
  python -c "from tests.golden_lemmatize import LEMMATIZE_CASES; print(len(LEMMATIZE_CASES), 'giriş')"
  ```

---

## Task 2: `LemmaResult` + `_lemmatize_inner` + Kelime-Düzeyi API

**Dosyalar:**
- Oluştur: `turkgram/lemmatize.py`

- [ ] **Adım 1: Temel `LemmaResult` + `_lemmatize_inner` yaz**

  `turkgram/lemmatize.py` dosyasını oluştur:

  ```python
  """turkgram.lemmatize — Lemmatizer (Faz 9c).

  lemmatize()        → str | None        (sade, kelime)
  lemmatize_text()   → list[str | None]  (sade, metin)
  lemmatize_detail() → LemmaResult | None (zengin, kelime)
  lemmatize_text_detail() → list[LemmaResult | None] (zengin, metin)

  Fallback zinciri: analyze → spellcheck.suggest → None.
  """
  from __future__ import annotations

  from dataclasses import dataclass
  from typing import Collection

  from .analysis import analyze as _analyze, parse_text as _parse_text
  from .disambiguation import disambiguate as _disambiguate
  from .context import rank_in_context as _rank_in_context
  from .tokenize import tokenize as _tokenize
  from .spellcheck import suggest as _suggest


  @dataclass(frozen=True)
  class LemmaResult:
      """Zengin lemma sonucu.

      confidence: disambiguation softmax skoru; freq=None → dilbilimsel ağırlıklı.
      corrected: True = spellcheck fallback kullanıldı.
      """
      lemma: str
      pos: str
      confidence: float
      corrected: bool


  def _lemmatize_inner(
      word: str,
      roots: Collection[str] | None,
      freq: dict[str, int] | None,
      corrected: bool = False,
  ) -> LemmaResult | None:
      """Ortak implementasyon — tüm public fonksiyonlar buraya delege eder."""
      results = _analyze(word, roots=roots)
      if results:
          ranked = _disambiguate(results, freq=freq)
          best, confidence = ranked[0]
          return LemmaResult(
              lemma=best.lemma,
              pos=best.pos,
              confidence=confidence,
              corrected=corrected,
          )
      # Fallback: spellcheck
      suggestions = _suggest(word, roots=roots if roots is None else frozenset(roots))
      if suggestions:
          return _lemmatize_inner(suggestions[0], roots, freq, corrected=True)
      return None


  def lemmatize(
      word: str,
      *,
      roots: Collection[str] | None = None,
      freq: dict[str, int] | None = None,
  ) -> str | None:
      """Tek kelime veya çok-token string → lemma. Çözümsüz → None.

      Raises:
          ValueError: Boş string.
      """
      if not isinstance(word, str) or not word.strip():
          raise ValueError(f"geçersiz word: {word!r}")
      result = _lemmatize_inner(word.strip(), roots, freq)
      return result.lemma if result is not None else None


  def lemmatize_detail(
      word: str,
      *,
      roots: Collection[str] | None = None,
      freq: dict[str, int] | None = None,
  ) -> LemmaResult | None:
      """Tek kelime veya çok-token string → LemmaResult. Çözümsüz → None.

      Raises:
          ValueError: Boş string.
      """
      if not isinstance(word, str) or not word.strip():
          raise ValueError(f"geçersiz word: {word!r}")
      return _lemmatize_inner(word.strip(), roots, freq)
  ```

- [ ] **Adım 2: Kelime-düzeyi golden testlerini çalıştır (başlangıçta FAIL beklenir)**

  ```bash
  cd D:\PYTHON\turkgram
  PYTHONUTF8=1 python -m pytest tests/test_lemmatize.py -v -k "lemmatize and not text" 2>&1 | head -30
  ```

  Beklenen: `ImportError: No module named 'tests.test_lemmatize'` — normal, henüz yazılmadı.

- [ ] **Adım 3: Metin-düzeyi API ekle**

  `turkgram/lemmatize.py` sonuna ekle:

  ```python
  def lemmatize_text(
      text: str,
      *,
      roots: Collection[str] | None = None,
      freq: dict[str, int] | None = None,
  ) -> list[str | None]:
      """Metin → token başına lemma listesi. Çözümsüz token → None.

      Raises:
          ValueError: Boş string.
      """
      if not isinstance(text, str) or not text.strip():
          raise ValueError(f"geçersiz text: {text!r}")
      results = lemmatize_text_detail(text, roots=roots, freq=freq)
      return [r.lemma if r is not None else None for r in results]


  def lemmatize_text_detail(
      text: str,
      *,
      roots: Collection[str] | None = None,
      freq: dict[str, int] | None = None,
  ) -> list[LemmaResult | None]:
      """Metin → token başına LemmaResult listesi. Çözümsüz token → None.

      Raises:
          ValueError: Boş string.
      """
      if not isinstance(text, str) or not text.strip():
          raise ValueError(f"geçersiz text: {text!r}")
      tokens = _tokenize(text)
      # roots=None → parse_text kısayolu (_cached_analyze ile önbellekli)
      # roots verilmişse per-token analyze döngüsü (parse_text roots almaz)
      if roots is None:
          analyses_per_token = _parse_text(text)
      else:
          analyses_per_token = [_analyze(t, roots=roots) for t in tokens]

      ranked_per_token = _rank_in_context(tokens, analyses_per_token, freq=freq)

      output: list[LemmaResult | None] = []
      for i, (ranked, all_analyses) in enumerate(zip(ranked_per_token, analyses_per_token)):
          if ranked:
              best = ranked[0]
              # Güven skoru: TAM aday listesi üzerinden disambiguate et,
              # ardından bağlamsal 'best'i bu listede bul.
              # (tek-elemanlı [best] gönderme → softmax=1.0 garantili, anlamsız)
              if all_analyses:
                  all_ranked = _disambiguate(all_analyses, freq=freq)
                  # bağlamsal best'i tam listede ara; bulamazsan ilk sıradan al
                  confidence = next(
                      (conf for a, conf in all_ranked if a.lemma == best.lemma and a.kind == best.kind),
                      all_ranked[0][1],
                  )
              else:
                  confidence = 1.0
              output.append(LemmaResult(
                  lemma=best.lemma,
                  pos=best.pos,
                  confidence=confidence,
                  corrected=False,
              ))
          else:
              # Spellcheck fallback — bağlam dışında işlenir
              output.append(_lemmatize_inner(tokens[i], roots, freq))
      return output
  ```

  **NOT — güven skoru stratejisi:** `rank_in_context` `list[Analysis]` döner (tuple değil).
  Güveni bağlam öncesi TAM aday listesiyle `disambiguate` çağırarak alırız; böylece
  softmax birden fazla adayı karşılaştırır ve güven anlamlı olur. `1.0` sabit değerinden kaçınılır.

- [ ] **Adım 4: Modül import testini çalıştır**

  ```bash
  PYTHONUTF8=1 python -c "from turkgram.lemmatize import lemmatize, lemmatize_detail, lemmatize_text, lemmatize_text_detail, LemmaResult; print('OK')"
  ```

  Beklenen: `OK`

---

## Task 3: `__init__.py` + `tr.py` Güncelle

**Dosyalar:**
- Güncelle: `turkgram/__init__.py`
- Güncelle: `turkgram/tr.py`

- [ ] **Adım 1: `__init__.py`'a lemmatize importlarını ekle**

  `turkgram/__init__.py` içinde `spellcheck` import satırını bul ve hemen altına ekle:

  ```python
  # ── Lemmatizer (Faz 9c) ───────────────────────────────────────────────────
  from .lemmatize import lemmatize, lemmatize_text, lemmatize_detail, lemmatize_text_detail, LemmaResult
  ```

  **NOT:** `from . import lemmatize` (modül) satırını EKLEME — modül adı ile fonksiyon adı
  aynı olduğundan `turkgram.lemmatize` attribute'u fonksiyonu gösterir. `sys.modules`
  üzerinden modüle erişim yine de çalışır; mevcut spellcheck/syllabify pattern'ini izle
  (sadece `from .X import ...` satırı).

  `__all__` listesine de ekle (mevcut listenin uygun yerine):
  ```python
  # lemmatizer
  "lemmatize", "lemmatize_text", "lemmatize_detail", "lemmatize_text_detail", "LemmaResult",
  ```

- [ ] **Adım 2: `tr.py`'a TR sarmalayıcılar ekle**

  `turkgram/tr.py` dosyasının sonuna ekle:

  ```python
  # ── Lemmatizer (Faz 9c) ───────────────────────────────────────────────────
  from . import lemmatize as _lem


  def temel_biçim(kelime: str, *, kökler=None, sıklık=None) -> str | None:
      """Kelime → lemma (sözlük biçimi). Çözümsüz → None.

      NOT: _tr_lower ÇAĞIRILMAZ — içeride analyze + spellcheck normalize eder.

      >>> temel_biçim('geliyorum')  # 'gelmek'
      >>> temel_biçim('evlerde')    # 'ev'
      """
      return _lem.lemmatize(kelime, roots=kökler, freq=sıklık)


  def temel_biçim_metin(metin: str, *, kökler=None, sıklık=None) -> list[str | None]:
      """Metin → token başına lemma listesi.

      >>> temel_biçim_metin('Ali eve geldi')  # ['ali', 'ev', 'gelmek']
      """
      return _lem.lemmatize_text(metin, roots=kökler, freq=sıklık)


  def temel_biçim_detay(kelime: str, *, kökler=None, sıklık=None):
      """Kelime → LemmaResult. Çözümsüz → None."""
      return _lem.lemmatize_detail(kelime, roots=kökler, freq=sıklık)


  def temel_biçim_metin_detay(metin: str, *, kökler=None, sıklık=None):
      """Metin → token başına LemmaResult listesi."""
      return _lem.lemmatize_text_detail(metin, roots=kökler, freq=sıklık)
  ```

- [ ] **Adım 3: Import doğrula**

  ```bash
  PYTHONUTF8=1 python -c "import turkgram; print(turkgram.lemmatize('geliyorum')); import turkgram.tr as tr; print(tr.temel_biçim('evlerde'))"
  ```

  Beklenen: `gelmek` ve `ev`

- [ ] **Adım 4: Commit**

  ```bash
  git add turkgram/lemmatize.py turkgram/__init__.py turkgram/tr.py
  git commit -m "feat(lemmatize): LemmaResult + lemmatize/lemmatize_text API (Faz 9c)"
  ```

---

## Task 4: Test Runner Yaz ve Çalıştır

**Dosyalar:**
- Oluştur: `tests/test_lemmatize.py`

- [ ] **Adım 1: Test runner yaz**

  `tests/test_lemmatize.py` dosyasını oluştur:

  ```python
  """Faz 9c — lemmatizer runner."""
  import pytest
  from tests.golden_lemmatize import LEMMATIZE_CASES, CORRECTED_CASES, TEXT_CASES


  @pytest.mark.parametrize("surface,expected", LEMMATIZE_CASES)
  def test_lemmatize(surface, expected):
      from turkgram.lemmatize import lemmatize
      assert lemmatize(surface) == expected


  @pytest.mark.parametrize("surface,expected_lemma", CORRECTED_CASES)
  def test_lemmatize_corrected_flag(surface, expected_lemma):
      from turkgram.lemmatize import lemmatize_detail
      result = lemmatize_detail(surface)
      assert result is not None
      assert result.lemma == expected_lemma
      assert result.corrected is True


  @pytest.mark.parametrize("text,expected", TEXT_CASES)
  def test_lemmatize_text(text, expected):
      from turkgram.lemmatize import lemmatize_text
      assert lemmatize_text(text) == expected


  def test_lemma_result_frozen():
      from turkgram.lemmatize import LemmaResult
      r = LemmaResult(lemma="ev", pos="noun", confidence=0.9, corrected=False)
      with pytest.raises(Exception):
          r.lemma = "araba"  # type: ignore


  def test_lemma_result_confidence_is_float():
      from turkgram.lemmatize import lemmatize_detail
      result = lemmatize_detail("geliyorum")
      assert result is not None
      assert isinstance(result.confidence, float)


  def test_lemmatize_empty_raises():
      from turkgram.lemmatize import lemmatize
      with pytest.raises(ValueError):
          lemmatize("")


  def test_lemmatize_text_empty_raises():
      from turkgram.lemmatize import lemmatize_text
      with pytest.raises(ValueError):
          lemmatize_text("")


  def test_lemmatize_detail_empty_raises():
      from turkgram.lemmatize import lemmatize_detail
      with pytest.raises(ValueError):
          lemmatize_detail("")


  def test_lemmatize_text_detail_empty_raises():
      from turkgram.lemmatize import lemmatize_text_detail
      with pytest.raises(ValueError):
          lemmatize_text_detail("")


  def test_tr_api_equivalence():
      import turkgram.tr as tr
      from turkgram.lemmatize import lemmatize
      for word in ["geliyorum", "evlerde", "bana"]:
          assert tr.temel_biçim(word) == lemmatize(word)


  def test_tr_api_metin_equivalence():
      import turkgram.tr as tr
      from turkgram.lemmatize import lemmatize_text
      text = "Ali eve geldi"
      assert tr.temel_biçim_metin(text) == lemmatize_text(text)
  ```

- [ ] **Adım 2: Testleri çalıştır**

  ```bash
  PYTHONUTF8=1 python -m pytest tests/test_lemmatize.py -v
  ```

  Beklenen: tüm testler PASS. Hata varsa:
  - `AssertionError: lemmatize("dag") != "dağ"` → spellcheck BK-tree yüklenmemiş olabilir; `from turkgram.spellcheck import _build_tree; _build_tree()` çağrılıyor mu kontrol et
  - `confidence is None` → `_disambiguate([best], freq=None)[0]` çıktısını yazdır

- [ ] **Adım 3: Tam paket regresyon testi**

  ```bash
  PYTHONUTF8=1 python -m pytest --tb=short -q
  ```

  Beklenen: önceki testler PASS, yeni testler PASS, **0 hata**.

- [ ] **Adım 4: Commit**

  ```bash
  git add tests/golden_lemmatize.py tests/test_lemmatize.py
  git commit -m "test(lemmatize): bağımsız golden + runner (Faz 9c)"
  ```

---

## Task 5: Korpus Tarama Aracı

**Dosyalar:**
- Oluştur: `tools/sweep_lemmatize.py`

- [ ] **Adım 1: Sweep aracını yaz**

  `tools/sweep_lemmatize.py` dosyasını oluştur:

  ```python
  """Faz 9c — lemmatizer korpus taraması.

  26k leksikon lemması üzerinden:
  - 0 çökme hedefi (HATA = gerçek bug)
  - lemmatize(lemma) != lemma → belirsizlik logu (hata DEĞİL)
  """
  import sys
  sys.path.insert(0, ".")

  from turkgram.lexicon import load as _load_lexicon
  from turkgram.lemmatize import lemmatize

  def main():
      roots = _load_lexicon()
      mismatches = []
      errors = []

      for i, lemma in enumerate(sorted(roots), 1):
          try:
              result = lemmatize(lemma, roots=roots)
              if result != lemma:
                  mismatches.append((lemma, result))
          except Exception as e:
              errors.append((lemma, str(e)))

          if i % 5000 == 0:
              print(f"  {i}/{len(roots)} işlendi...")

      print(f"\nToplam: {len(roots)} lemma")
      print(f"Çökme (HATA): {len(errors)}")
      print(f"Uyuşmayan (belirsizlik, normal): {len(mismatches)}")

      if errors:
          print("\n--- HATALAR ---")
          for lemma, err in errors[:20]:
              print(f"  {lemma}: {err}")
          sys.exit(1)

      if mismatches:
          print(f"\nİlk 20 uyuşmayan (belirsizlik):")
          for lemma, got in mismatches[:20]:
              print(f"  {lemma!r} → {got!r}")

      print("\nSonuç: 0 çökme ✓")

  if __name__ == "__main__":
      main()
  ```

- [ ] **Adım 2: Sweep çalıştır**

  ```bash
  PYTHONUTF8=1 python tools/sweep_lemmatize.py
  ```

  Beklenen: `Çökme (HATA): 0` — uyuşmazlıklar normal/beklenen.

- [ ] **Adım 3: Commit**

  ```bash
  git add tools/sweep_lemmatize.py
  git commit -m "tools(lemmatize): korpus tarama aracı (Faz 9c)"
  ```

---

## Task 6: Final Doğrulama ve Hakem

- [ ] **Adım 1: Tüm testler yeşil mi?**

  ```bash
  PYTHONUTF8=1 python -m pytest --tb=short -q
  ```

  Beklenen: 3943+ test PASS, 0 hata.

- [ ] **Adım 2: Test sayısını doğrula**

  ```bash
  PYTHONUTF8=1 python -m pytest --collect-only -q 2>&1 | tail -3
  ```

  ~3943 test beklenir (önceki 3883 + ~60 yeni).

- [ ] **Adım 3: README'yi güncelle**

  `README.md` içinde test sayısı ve Faz 9c durumunu güncelle.

- [ ] **Adım 4: Final commit**

  ```bash
  git add README.md
  git commit -m "docs(readme): Faz 9c lemmatizer eklendi; test sayısı güncellendi"
  ```
