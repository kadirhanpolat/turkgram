# Faz 5 D1 — Sayı Morfolojisi İmplementasyon Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Türkçe sayı sözcüklerine ordinal (-IncI: birinci/ikinci) ve distributif (-şAr: birer/ikişer) ekleri üreten `number.py` modülü; üretilen biçimler mevcut `decline()` motoruyla doğrudan çekilebilir.

**Architecture:** Turkgram iş akışı: SPEC → bağımsız golden (Opus, motor-körü) → motor → hakem (adversarial). Yeni morfoloji primitifleri `morphology.py`'deki `high_vowel`/`low_vowel`/`hardens`/`ends_in_vowel`'ı IMPORT eder, kopyalamaz. Sayı biçimlerinin çekimi `decline()` delegasyonuyla ücretsiz gelir (birincinin/birinciye vb.).

**Tech Stack:** Python 3.10+, pytest; saf Python, sıfır dış bağımlılık. `PYTHONUTF8=1` Windows zorunluluğu.

---

## Kapsam Notu

Bu plan yalnız **D1** (ordinal + distributif üretimi). D2 (edat) ve D3 (analiz) ayrı planlar alır.

---

## Dosya Yapısı

| Yol | Durum | Sorumluluk |
|-----|-------|-----------|
| `spec/number-spec.md` | YENİ | Linguistik SPEC: ordinal/distributif kuralları, istisnalar, örnekler |
| `turkgram/number.py` | YENİ | `ordinal(kök)`, `distributive(kök)` üretici fonksiyonlar |
| `tests/golden_number.py` | YENİ | Bağımsız golden veri (saf liste, pytest toplaması YOK) |
| `tests/test_number.py` | YENİ | Runner — golden'ı import eder, parametrik test çalıştırır |
| `turkgram/__init__.py` | DEĞİŞİR | `ordinal`, `distributive` export eklenir |
| `turkgram/tr.py` | DEĞİŞİR | `sıralı()`, `dağıtımlı()` Türkçe sarmalayıcılar |

---

## Task 1: SPEC Yaz (`spec/number-spec.md`)

**Files:**
- Create: `spec/number-spec.md`

> **NOT:** SPEC ana oturum tarafından elle yazılır. Subagent KULLANILMAZ — morfoloji hataları incedir, Korkmaz §97-100 (sayı sözcükleri) ve §113 (yapım ekleri) referans alınır.

- [ ] **Adım 1.1: Ordinal kurallarını doğrula**

  Beklenen biçimler (elle kontrol, Korkmaz §97):
  ```
  bir   → birinci      (son ünlü i, ünsüz-final → +inci)
  iki   → ikinci       (son ünlü i, ünlü-final  → +nci)
  üç    → üçüncü       (son ünlü ü, ünsüz-final → +üncü)
  dört  → dördüncü     (son ünlü ö→ü harm., ün.-fin., t→d sedalılaşma [ünlü-başlı ek]; sertleşme (hard-cons kayması) YOK → +üncü)
  beş   → beşinci      (son ünlü e, ünsüz-final → +inci)
  altı  → altıncı      (son ünlü ı, ünlü-final  → +ncı)
  yedi  → yedinci      (son ünlü i, ünlü-final  → +nci)
  sekiz → sekizinci    (son ünlü i, ünsüz-final → +inci)
  dokuz → dokuzuncu    (son ünlü u, ünsüz-final → +uncu)
  on    → onuncu       (son ünlü o→u harm., ün.-fin. → +uncu)
  yüz   → yüzüncü     (son ünlü ü, ünsüz-final → +üncü)
  bin   → bininci      (son ünlü i, ünsüz-final → +inci)
  sıfır → sıfırıncı   (son ünlü ı, ünsüz-final → +ıncı)
  ```
  Kural özeti: -(I)ncI; I=yüksek-ünlü (4'lü harmoni); ünlü-final → başta I düşer (-nCI); C daima c (n sonrası sedalılaşma).

- [ ] **Adım 1.2: Distributif kurallarını doğrula**

  Beklenen biçimler (elle kontrol):
  ```
  bir   → birer        (son ünlü i, ünsüz-final → +er; ş YOK)
  iki   → ikişer       (son ünlü i, ünlü-final  → +şer)
  üç    → üçer         (son ünlü ü→e harm., ünsüz-final → +er)
  dört  → dörder       (son ünlü ö→e harm., ünsüz-final, t→d önce +er → dörder)
  beş   → beşer        (son ünlü e, ünsüz-final → +er)
  altı  → altışar      (son ünlü ı, ünlü-final  → +şar)
  yedi  → yedişer      (son ünlü i, ünlü-final  → +şer)
  sekiz → sekizer      (son ünlü i, ünsüz-final → +er)
  dokuz → dokuzar      (son ünlü u, ünsüz-final → +ar)
  on    → onar         (son ünlü o→a harm., ünsüz-final → +ar)
  yüz   → yüzer        (son ünlü ü→e harm., ünsüz-final → +er)
  bin   → biner        (son ünlü i, ünsüz-final → +er)
  ```
  Kural özeti: ünlü-final → -şAr; ünsüz-final → -Ar (ş YOK). A=alçak-ünlü (2'li harmoni, arka→a, ön→e). Ünsüz-final ekte son ünsüz sedalılaşması: t→d (dörder), diğerleri sabit.

- [ ] **Adım 1.3: SPEC dosyasını yaz**

  `spec/number-spec.md` asgari bölümler:
  - §1 Kapsam (ordinal/distributif; çekim delegasyon)
  - §2 Ordinal (-IncI): kural + istisna tablosu + 1-1000 temsili örnekler
  - §3 Distributif (-şAr/-Ar): kural + sedalılaşma + örnekler
  - §4 Bileşik sayılarda uygulama (yirmi bir → yirmi birinci)
  - §5 Çekim entegrasyonu (birincinin/birinciye → `decline(ordinal("bir"))`)
  - §6 Sınır/kapsam-dışı (kesir, yaklaşık, vs.)

- [ ] **Adım 1.4: SPEC'i commit et**

  ```bash
  git add spec/number-spec.md
  git commit -m "spec(number): Faz 5 D1 sayı morfolojisi SPEC (ordinal + distributif)"
  ```

---

## Task 2: Bağımsız Golden (`tests/golden_number.py`)

**Files:**
- Create: `tests/golden_number.py`

> **ZORUNLU:** Bu adım bağımsız bir Opus subagent'a dispatch edilir. Subagent `turkgram/number.py`'yi GÖRMEZ (henüz yok). Yalnız SPEC + dilbilgisi kullanır. Golden = motor-körü, elle-doğrulanmış beklentiler.

- [ ] **Adım 2.1: Bağımsız golden subagent'ı dispatch et**

  Subagent prompt'u:
  ```
  Sen bir Türkçe dilbilgisi uzmanısın. turkgram projesindeki number.py motorunu
  HİÇ GÖRME VE OKUMA. Yalnız spec/number-spec.md ve Korkmaz'ın ordinal/distributif
  kurallarına dayanarak tests/golden_number.py dosyasını oluştur.

  Dosya formatı (saf veri, pytest toplaması YOK — test_* fonksiyon YOK):
  ```python
  # Ordinal golden: (girdi_kök, beklenen_ordinal)
  ORDINAL_CASES = [
      ("bir", "birinci"),
      ("iki", "ikinci"),
      ...  # 1-20 + 30,40,50,100,200,1000 + bileşik örnekler (yirmi bir→yirmi birinci)
  ]

  # Distributif golden: (girdi_kök, beklenen_distributif)
  DISTRIBUTIVE_CASES = [
      ("bir", "birer"),
      ("iki", "ikişer"),
      ...  # 1-12 tek basamak + bileşik (yirmi bir→yirmi birer, kırk iki→kırk ikişer)
  ]

  # Decline round-trip golden: (ordinal_form, durum, beklenen)
  DECLINE_CASES = [
      ("birinci", "gen", "birincinin"),
      ("ikinci",  "dat", "ikinciye"),
      ("üçüncü",  "acc", "üçüncüyü"),
      ("onuncu",  "abl", "onuncudan"),
      ("birinci", "ins", "birinciyle"),
      ("beşinci", "loc", "beşincide"),
  ]
  ```
  En az 20 ordinal (bileşik dahil), 15 distributif (bileşik dahil), 8 decline test girdisi.
  Hiçbiri motor çıktısına bakarak üretilmeyecek — dilbilgisinden elle doğrula.
  ```

- [ ] **Adım 2.2: Golden'ı gözden geçir**

  `tests/golden_number.py` açıp beklentileri Adım 1.1/1.2 listesiyle karşılaştır.
  Hatalı satır varsa elle düzelt (motor çıktısına BAKMA).

- [ ] **Adım 2.3: Runner iskelet oluştur**

  > **Import stili:** Mevcut `tests/test_adjective.py`'nin import stilini AYNEN izle (göreli vs. mutlak import).

  ```python
  # tests/test_number.py
  # Import stili: tests/test_adjective.py'den kopyala (göreli import varsa .golden_number, yoksa golden_number)
  import pytest
  from turkgram import ordinal, distributive
  from turkgram.morphology_noun import decline
  from .golden_number import ORDINAL_CASES, DISTRIBUTIVE_CASES, DECLINE_CASES

  @pytest.mark.parametrize("kok,beklenen", ORDINAL_CASES)
  def test_ordinal(kok, beklenen):
      assert ordinal(kok) == beklenen

  @pytest.mark.parametrize("kok,beklenen", DISTRIBUTIVE_CASES)
  def test_distributive(kok, beklenen):
      assert distributive(kok) == beklenen

  @pytest.mark.parametrize("form,durum,beklenen", DECLINE_CASES)
  def test_ordinal_decline(form, durum, beklenen):
      assert decline(form, case=durum) == beklenen
  ```

- [ ] **Adım 2.4: Runner'ın henüz başarısız olduğunu doğrula**

  ```bash
  PYTHONUTF8=1 python -m pytest tests/test_number.py -v 2>&1 | head -20
  ```
  Beklenen: `ImportError` veya `ModuleNotFoundError` (number.py yok).

- [ ] **Adım 2.5: Golden + runner'ı commit et**

  ```bash
  git add tests/golden_number.py tests/test_number.py
  git commit -m "test(number): bağımsız golden + runner (Faz 5 D1)"
  ```

---

## Task 3: Motor — `turkgram/number.py`

**Files:**
- Create: `turkgram/number.py`

- [ ] **Adım 3.1: Temel iskelet**

  ```python
  # turkgram/number.py
  """number.py — sayı morfolojisi: ordinal (-IncI) ve distributif (-şAr/-Ar)."""
  from __future__ import annotations
  from .morphology import ends_in_vowel, high_vowel, low_vowel

  # Distributif sedalılaşma: yalnız bu harita → diğer ünsüzler değişmez.
  # hardens() KULLANILMAZ — o ek-başı sertleşmesini ölçer, gövde-sonu sedalılaşmasını değil.
  _VOICE_MAP: dict[str, str] = {"t": "d", "ç": "c", "k": "ğ", "p": "b"}

  def _voice_final(s: str) -> str:
      """Son harfi sedalılaştır (yalnız _VOICE_MAP içindekiler; beş→beş, sekiz→sekiz)."""
      return s[:-1] + _VOICE_MAP.get(s[-1], s[-1])

  def ordinal(kok: str) -> str:
      """Sayı köküne ordinal eki ekle: bir→birinci, iki→ikinci."""
      kok = kok.strip().lower()
      if not kok:
          raise ValueError("Boş kök")
      # TODO: uygula
      raise NotImplementedError

  def distributive(kok: str) -> str:
      """Sayı köküne distributif eki ekle: bir→birer, iki→ikişer."""
      kok = kok.strip().lower()
      if not kok:
          raise ValueError("Boş kök")
      # TODO: uygula
      raise NotImplementedError
  ```

- [ ] **Adım 3.2: Test'in hâlâ başarısız olduğunu doğrula**

  ```bash
  PYTHONUTF8=1 python -m pytest tests/test_number.py -v 2>&1 | head -10
  ```
  Beklenen: `NotImplementedError`.

- [ ] **Adım 3.3: Ordinal motorunu uygula**

  Kural (SPEC §2):
  - Yüksek ünlü: `high_vowel(kok)` → ı/i/u/ü
  - Ünlü-final: gövde + "n" + "c" + high_vowel; ünsüz-final: gövde + high_vowel + "n" + "c" + high_vowel
  - C daima "c" (n sonrası sedalı kalır, sertleşme yok)

  ```python
  def ordinal(kok: str) -> str:
      kok = kok.strip().lower()
      if not kok:
          raise ValueError("Boş kök")
      hv = high_vowel(kok)            # ı/i/u/ü
      if ends_in_vowel(kok):
          return kok + "nc" + hv      # iki → ikinci
      else:
          return kok + hv + "nc" + hv # bir → birinci
  ```

- [ ] **Adım 3.4: Ordinal testlerini çalıştır**

  ```bash
  PYTHONUTF8=1 python -m pytest tests/test_number.py::test_ordinal -v
  ```
  Beklenen: tüm `ORDINAL_CASES` geçer.

- [ ] **Adım 3.5: Distributif motorunu uygula**

  Kural (SPEC §3):
  - Alçak ünlü: `low_vowel(kok)` → a/e
  - Ünlü-final: gövde + "ş" + low_vowel + "r"  (ikişer, altışar, yedişer)
  - Ünsüz-final: `_voice_final(gövde)` + low_vowel + "r"  (birer, üçer, dörder, beşer…)
  - `_voice_final`: `t→d` (dörder), `ç→c`, `k→ğ`, `p→b`; diğerleri (ş, z, r, n) DEĞİŞMEZ.
  - **`hardens()` KULLANILMAZ** — o ek-başı sertleşmesini ölçer, gövde-sonu sedalılaşmasını değil;
    `hardens('beş')=True` ama `beşer` beklenir, `bejer` değil. _VOICE_MAP kararını verir.

  ```python
  def distributive(kok: str) -> str:
      kok = kok.strip().lower()
      if not kok:
          raise ValueError("Boş kök")
      lv = low_vowel(kok)              # a/e
      if ends_in_vowel(kok):
          return kok + "ş" + lv + "r"  # iki → ikişer
      else:
          stem = _voice_final(kok)      # dört→dördleştirme, beş→beş (haritada yok)
          return stem + lv + "r"        # dört→dörder, bir→birer, beş→beşer
  ```

- [ ] **Adım 3.6: Distributif testlerini çalıştır**

  ```bash
  PYTHONUTF8=1 python -m pytest tests/test_number.py::test_distributive -v
  ```
  Başarısız olanlar: SPEC ile golden karşılaştır, motoru güncelle.

- [ ] **Adım 3.7: Decline round-trip testlerini çalıştır**

  ```bash
  PYTHONUTF8=1 python -m pytest tests/test_number.py::test_ordinal_decline -v
  ```
  Beklenen: `decline(ordinal(...), case=...)` zaten çalışıyor (yeni morfoloji yok).

- [ ] **Adım 3.8: Tüm number testlerini çalıştır**

  ```bash
  PYTHONUTF8=1 python -m pytest tests/test_number.py -v
  ```
  Beklenen: tümü yeşil.

- [ ] **Adım 3.9: Motor commit**

  ```bash
  git add turkgram/number.py
  git commit -m "feat(number): ordinal (-IncI) + distributif (-şAr/-Ar) motoru (Faz 5 D1)"
  ```

---

## Task 4: `__init__.py` ve `tr.py` Entegrasyonu

**Files:**
- Modify: `turkgram/__init__.py`
- Modify: `turkgram/tr.py`

- [ ] **Adım 4.1: `__init__.py` export ekle**

  ```python
  # turkgram/__init__.py'ye ekle (mevcut import bloğuna)
  from .number import ordinal, distributive
  ```

  Doğrula:
  ```bash
  PYTHONUTF8=1 python -c "from turkgram import ordinal, distributive; print(ordinal('iki'), distributive('iki'))"
  ```
  Beklenen: `ikinci ikişer`

- [ ] **Adım 4.2: `tr.py` sarmalayıcıları ekle**

  Turkgram `tr.py` deseni: Türkçe parametre adları + değer normalizasyonu.
  ```python
  # turkgram/tr.py'ye ekle
  from .number import ordinal as _ordinal, distributive as _distributive

  def sıralı(kök: str) -> str:
      """Sayı köküne sıra eki ekle: 'bir'→'birinci', 'iki'→'ikinci'."""
      return _ordinal(kök)

  def dağıtımlı(kök: str) -> str:
      """Sayı köküne dağılım eki ekle: 'bir'→'birer', 'iki'→'ikişer'."""
      return _distributive(kök)
  ```

  Doğrula:
  ```bash
  PYTHONUTF8=1 python -c "from turkgram.tr import sıralı, dağıtımlı; print(sıralı('üç'), dağıtımlı('üç'))"
  ```
  Beklenen: `üçüncü üçer`

- [ ] **Adım 4.3: tr.py için çeviri denkliği testi**

  `tests/test_number.py`'ye TR denklik testi ekle:
  ```python
  from turkgram.tr import sıralı, dağıtımlı

  def test_tr_ordinal_denklik():
      from turkgram import ordinal
      for kok, _ in ORDINAL_CASES:
          assert sıralı(kok) == ordinal(kok)

  def test_tr_distributive_denklik():
      from turkgram import distributive
      for kok, _ in DISTRIBUTIVE_CASES:
          assert dağıtımlı(kok) == distributive(kok)
  ```

- [ ] **Adım 4.4: Tam test koşusu**

  ```bash
  PYTHONUTF8=1 python -m pytest tests/test_number.py -v
  ```
  Beklenen: tümü yeşil.

- [ ] **Adım 4.5: Entegrasyon commit**

  ```bash
  git add turkgram/__init__.py turkgram/tr.py tests/test_number.py
  git commit -m "feat(tr): sıralı/dağıtımlı sarmalayıcılar + __init__ export (Faz 5 D1)"
  ```

---

## Task 5: Regresyon Kontrolü

**Files:** (değişmez)

- [ ] **Adım 5.1: Tam paket testleri çalıştır**

  ```bash
  PYTHONUTF8=1 python -m pytest --tb=short -q
  ```
  Beklenen: önceki 3372 test + yeni number testleri, tümü yeşil, 0 regresyon.

- [ ] **Adım 5.2: Hızlı korpus kontrolü**

  Gömülü leksikondaki isimlerle decline entegrasyonu test et:
  ```bash
  PYTHONUTF8=1 python -c "
  from turkgram import ordinal
  from turkgram.morphology_noun import decline
  forms = ['bir','iki','üç','dört','beş','on','yüz','bin']
  for k in forms:
      o = ordinal(k)
      for case in ['nom','gen','dat','acc','abl','loc','ins']:
          decline(o, case=case)  # çökme olmamalı
  print('korpus kontrolü OK, 0 çökme')
  "
  ```

---

## Task 6: Hakem (Adversarial Doğrulama)

**Files:** (değişmez)

> Bu adım ayrı bir Opus subagent'a dispatch edilir.

- [ ] **Adım 6.1: Hakem subagent'ı dispatch et**

  Prompt:
  ```
  turkgram Faz 5 D1 sayı morfolojisi hakemi olarak görev yap.
  
  İnceleme kapsamı:
  - spec/number-spec.md — linguistik doğruluk
  - turkgram/number.py — implementasyon doğruluğu
  - tests/golden_number.py — golden bağımsızlığı ve kapsam
  
  Adversarial kontrol listesi:
  1. Ordinal -IncI: ünlü-final/ünsüz-final ayrımı doğru mu? C sertleşmesi yok mu (c her zaman c)?
  2. Distributif -şAr/-Ar: ünlü-final ş'li, ünsüz-final ş'siz — doğru mu?
  3. dört→dörder: son t sedalılaşması var mı, doğru işleniyor mu?
  4. Bileşik sayılar (yirmi bir → yirmi birinci): son sözcük kuralı doğru uygulanıyor mu?
  5. decline() round-trip: birincinin/birinciye — mevcut motor bozulmadı mı?
  6. Golden motora körü kurulmuş mu (implementasyona bakılmadan)?
  7. Edge case boşlukları: sıfır, bin, bileşik — golde'de temsil edilmiş mi?
  
  CRITICAL/HIGH/MEDIUM/LOW seviyeli bulgular. Her bulgu: açıklama + düzeltme önerisi.
  ```

- [ ] **Adım 6.2: Hakem bulgularını işle**

  - CRITICAL/HIGH → derhal düzelt, testi yeniden çalıştır
  - MEDIUM → düzelt (mümkünse)
  - LOW → CLAUDE.md notuna al veya ertelenmiş issue olarak kaydet

- [ ] **Adım 6.3: Hakem sonrası commit (gerekirse)**

  ```bash
  git add -A
  git commit -m "fix(number): hakem bulguları düzeltildi (Faz 5 D1)"
  ```

---

## Task 7: CLAUDE.md Güncelleme ve Final Commit

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Adım 7.1: CLAUDE.md §7 güncelle**

  §7'de Faz 4 bloğunun hemen altına **yeni Faz 5 satırı ekle** (mevcut satır yok, ilk kez ekleniyor):
  `- **Faz 5** — sözcük-sınıfı tamamlama: ✅ D1 sayı morfolojisi (`number.py`)…`
  Ayrıca test sayısını ve yeni dosyalar listesini güncelle.

- [ ] **Adım 7.2: Memory güncelle**

  `~/.claude/projects/D--PYTHON-turkgram/memory/faz-durumu.md` güncelle:
  D1 tamamlandı, D2 sırada.

- [ ] **Adım 7.3: Final commit**

  ```bash
  git add CLAUDE.md
  git commit -m "docs(claude): Faz 5 D1 tamamlandı — sayı morfolojisi (ordinal + distributif)"
  ```

---

## Özet: Beklenen Çıktı

| Bileşen | Durum |
|---------|-------|
| `spec/number-spec.md` | ✅ Linguistik SPEC |
| `turkgram/number.py` | ✅ `ordinal()` + `distributive()` |
| `tests/golden_number.py` | ✅ Bağımsız golden (20+ ordinal, 15+ distributif, 8+ decline) |
| `tests/test_number.py` | ✅ Runner + TR denklik testleri |
| `turkgram/__init__.py` | ✅ Export eklendi |
| `turkgram/tr.py` | ✅ `sıralı()` + `dağıtımlı()` |
| Regresyon | ✅ 0 regresyon |
| Hakem | ✅ Adversarial doğrulandı |
