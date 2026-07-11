# Faz 2a — Çözümleyici Implementation Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (önerilen)
> veya executing-plans ile görev-görev uygula. Adımlar checkbox (`- [ ]`) ile izlenir.
> **İSTİSNA (CLAUDE.md §2):** Task 1 (SPEC) ANA OTURUM tarafından elle yazılır — alt-ajana
> DİSPATCH EDİLMEZ. Task 2-3 golden'ları motoru GÖRMEYEN bağımsız ajanlara verilir.

**Goal:** Yüzey biçim → kök + eksen değerleri çözümleyicisi (`analyze`/`tr.çözümle`):
üretecin beş giriş noktasının (conjugate/decline/copula/converb/participle) tam dili
üzerinde round-trip + pedagojik segmentasyon.

**Architecture:** Önek-tabanlı kök adayları + ses-filtreli grid enumerasyonu + üreteç
oracle doğrulaması (onaylı tasarım: `docs/faz2a-cozumleyici-tasarim.md`; kritik sicili:
`docs/faz2a-mimari-kritik.md`). Form-precision ve recall by-construction; segmentasyon
ayrı golden-doğrulamalı alt-teslimat.

**Tech Stack:** Saf Python 3, sıfır bağımlılık, pytest. Windows: her ad-hoc python
komutu `PYTHONUTF8=1` ile (CLAUDE.md #5).

**Mevcut durum:** 2005 test yeşil; her task sonunda regresyonsuz kalmalı.

---

## Dosya haritası

| Dosya | Sorumluluk | İşlem |
|-------|-----------|-------|
| `spec/analysis-spec.md` | Ses-filtresi önermeleri, ters-mutasyon envanteri, segmentasyon kesim politikası, kanonik kwargs | Create (Task 1, ANA OTURUM) |
| `tests/golden_analysis.py` | Precision golden: ~40 yüzey → TAM beklenen çözüm kümesi | Create (Task 2, bağımsız ajan) |
| `tests/golden_segments.py` | Segmentasyon golden: ~30 biçim elle kesimli | Create (Task 3, bağımsız ajan) |
| `turkgram/analysis.py` | `Segment`/`Analysis` dataclass'ları, normalizasyon/tokenizasyon, kök adayları, grid+filtreler, oracle, segmentasyon | Create (Task 4-6) |
| `tests/test_analysis.py` | Golden koşucular + hata sözleşmesi + round-trip süpürme + bütçe | Create (Task 4+) |
| `turkgram/tr.py` | `çözümle` + ters değer haritaları + segment etiket Türkçeleştirme | Modify (Task 7) |
| `tests/test_tr.py` | `çözümle` çeviri denkliği | Modify (Task 7) |
| `turkgram/__init__.py` | `analyze`, `Analysis`, `Segment` dışa açma | Modify (Task 6) |
| `CLAUDE.md`, `docs/faz2a-cozumleyici-tasarim.md` | Durum güncelleme | Modify (Task 9) |

`analysis.py` tek dosyada başlar; 800 satırı aşarsa `analysis_candidates.py` (öneri
üretimi) ayrılır — plan bunu Task 6 sonunda değerlendirir.

---

### Task 1: SPEC — `spec/analysis-spec.md` (ANA OTURUM, elle)

**Files:** Create: `spec/analysis-spec.md`

- [ ] **1.1** Tasarım §1'den SPEC'e dönüştür; şunlar SOMUT olmalı:
  - **Ses-filtresi önerme tablosu** — her satır: eksen değeri → zorunlu yüzey izi (regex)
    → gerekçe. YALNIZ kanıtlanabilir olanlar (pres⇒`yor`, fut⇒`c[ae]`, evid/rivayet⇒
    `m[ıiuü]ş`, necess⇒`m[ae]l[ıi]`, question⇒` m[ıiuü]`, aspect⇒aux kökü). Emin
    olunamayan eksene filtre YOK.
  - **Ters-mutasyon envanteri** — üreteç kaynaklı: d→t, ğ→k, b→p, c→ç (yumuşamanın
    tersleri), ye_de i→e, düşen yüksek ünlü geri-ekleme (harmoni-uyumlu, yalnız son hece).
  - **Çatı zinciri kapalı kümesi** — (refl|recip ≤1)→(caus ≤3)→(pass ≤1) = 24 zincir, listele.
  - **Kanonik kwargs tanımı** — default'lar atılır; kind başına default tablosu.
  - **Segmentasyon kesim politikası** — kaynaştırma -y-/-n-/-s- SAĞdaki eke; yumuşama
    yüzey biçimiyle (`oku|duğ|um`); etiketler kanonik (`DIk`); span'ler birleşince yüzey.
  - **Tek-seferlik kontrol:** predicative/with_ki/equative anahtarları beş kind'dan
    biriyle yeniden-üretilebilir mi — değilse §0.1 envanterine ek.
- [ ] **1.2** Commit: `git add spec/analysis-spec.md && git commit -m "docs(spec): çözümleyici SPEC — Faz 2a"`

### Task 2: Precision golden (BAĞIMSIZ ajan — motor/analysis.py GÖRMEDEN)

**Files:** Create: `tests/golden_analysis.py`

- [ ] **2.1** Bağımsız ajana dispatch (talimat: YALNIZ `spec/analysis-spec.md` +
  `docs/faz2a-cozumleyici-tasarim.md` §2 API + dilbilgisi; `turkgram/` içi OKUMA yasak):
  ~40 yüzey için TAM beklenen çözüm kümesi. Kapsam zorunlulukları:
  - Belirsizler: `gelin` (emir-2pl / pass-gövde çözümleri / isim), `evin` (gen / 2sg-poss),
    `okuma` (neg-imp-2sg), `gelmem` (aorist-neg-1sg / isim+poss varsa), `geldik` (past-1pl
    / participle-DIk).
  - Her kind'dan örnek: `okuyor` (conjugate), `evlerde` (decline), `öğrenciydim` (copula),
    `okuyunca` (converb), `okuduğum` (participle+poss).
  - Zor morfofonoloji: `gidiyor` (yumuşama), `yiyecek` (ye_de), `dövüştürüldü` (çatı zinciri),
    `okuyamadı` (-AmA), `geliyor musun` (soru grubu), `aday oldu` (birleşik).
  - Format: `GOLDEN_ANALYSIS = {yüzey: [ {lemma, pos, kind, kwargs}, ... ]}` — TAM küme
    (eksik çözüm = recall hatası, FAZLA çözüm = precision hatası).
- [ ] **2.2** İkinci bağımsız türetme (ayrı ajan, aynı kısıt) → diff → ayrışmaları ana
  oturum dilbilgisiyle tahkim et (A1 emsali).
- [ ] **2.3** Commit: `feat(test): çözümleyici precision golden (bağımsız, iki türetme)`

### Task 3: Segmentasyon golden (BAĞIMSIZ ajan)

**Files:** Create: `tests/golden_segments.py`

- [ ] **3.1** Bağımsız ajana dispatch (SPEC kesim politikası + dilbilgisi; motor yasak;
  talimata ekle: MORFOLOJİK OLARAK TEK-ÇÖZÜMLÜ yüzeyler seç — koşucu `analyze(x)[0]`
  varsayımı belirsiz yüzeyde kırılır):
  ~30 biçim `GOLDEN_SEGMENTS = {yüzey: [(dilim, etiket), ...]}` — kaynaştırma
  (`okuyacağım`: y sağdaki eke), yumuşama (`okuduğum` → `oku|duğ|um`), pronominal -n-
  (`evinde`), düşme (`burnu`), çatı (`dövüştürüldü`) örnekleri dahil. Span'ler dilimlerden
  türetilebilir (birleşince yüzey) — golden yalnız (dilim, etiket) tutar.
- [ ] **3.2** Commit: `feat(test): segmentasyon golden (bağımsız)`

### Task 4: Veri tipleri + giriş sözleşmesi (RED → GREEN)

**Files:** Create: `turkgram/analysis.py`, `tests/test_analysis.py`

- [ ] **4.1** Failing test yaz — `tests/test_analysis.py`:

```python
"""Çözümleyici — golden koşucusu + sözleşme testleri (Faz 2a)."""
import pytest
from turkgram import analysis as an

def test_analysis_frozen_dataclass():
    s = an.Segment(surface="duğ", label="DIk", span=(3, 6))
    a = an.Analysis(lemma="okumak", pos="verb", kind="participle",
                    kwargs={"ptype": "dik", "possessive": "1sg"},
                    segments=(s,), hypothetical=True)
    with pytest.raises(Exception):   # frozen
        a.lemma = "x"

def test_gecersiz_girdi():
    for bad in ("", "   ", None, 42):
        with pytest.raises(ValueError):
            an.analyze(bad)          # type: ignore[arg-type]

def test_bilinmeyen_pos():
    with pytest.raises(ValueError, match="pos"):
        an.analyze("okuyor", pos="olmayan")

def test_cozumsuz_bos_liste():
    assert an.analyze("zzzt") == []

def test_cok_token_mesru_degil():
    assert an.analyze("git git git") == []
```

- [ ] **4.2** Koş: `PYTHONUTF8=1 python -m pytest tests/test_analysis.py -q` → beklenen:
  FAIL/ERROR (modül yok).
- [ ] **4.3** Minimal implement — `turkgram/analysis.py` iskeleti:

```python
"""Çözümleyici (analysis): yüzey → kök+eksenler — Faz 2a.

Mimari (docs/faz2a-cozumleyici-tasarim.md): önek-tabanlı kök adayları + ses-filtreli
grid enumerasyonu + üreteç oracle. Üreteç tek doğruluk kaynağı → form-precision yapısal.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Collection, Mapping

from .morphology import conjugate
from .morphology_noun import decline, copula
from .nonfinite import converb, participle
# _tr_lower YEREL kopya (#10): tr.py'den import ETME — Task 7'de tr.çözümle analysis'i
# çağıracak; döngü tuzağı (voice.py/morphology.py:289 lazy-import emsali). tr.çözümle
# tarafında da analysis lazy import edilir.
def _tr_lower(s: str) -> str:
    return s.replace("İ", "i").replace("I", "ı").lower()

@dataclass(frozen=True)
class Segment:
    surface: str
    label: str
    span: tuple[int, int]

@dataclass(frozen=True)
class Analysis:
    lemma: str
    pos: str            # "verb" | "noun"
    kind: str           # "conjugate"|"decline"|"copula"|"converb"|"participle"
    kwargs: Mapping[str, Any]
    segments: tuple[Segment, ...]
    hypothetical: bool

_POS = ("verb", "noun")
_KINDS = ("conjugate", "decline", "copula", "converb", "participle")

def analyze(surface: str, pos: str | None = None,
            *, roots: Collection[str] | None = None) -> list[Analysis]:
    if not isinstance(surface, str) or not surface.strip():
        raise ValueError(f"geçersiz yüzey: {surface!r}")
    if pos is not None and pos not in _POS:
        raise ValueError(f"pos: bilinmeyen değer {pos!r}. Geçerli: {', '.join(_POS)}")
    surface = _tr_lower(surface.strip())
    ...  # Task 5-6
    return []
```

- [ ] **4.4** Koş → PASS. Tam paket: `PYTHONUTF8=1 python -m pytest -q` → 2005+5 yeşil.
- [ ] **4.5** Commit: `feat(analysis): Analysis/Segment tipleri + giriş sözleşmesi`

### Task 5: Aday üretimi — kök adayları + grid + ses filtreleri

**Files:** Modify: `turkgram/analysis.py`, `tests/test_analysis.py`

- [ ] **5.1** Failing testler (aday üretimi İÇ birimleri — golden'a girmeden hızlı geri-bildirim):

```python
def test_kok_adaylari_mutasyon():
    cands = an._root_candidates("gidiyor")   # önekler + ters-mutasyon
    assert "git" in cands and "gid" in cands  # d→t tersi
    cands2 = an._root_candidates("yiyor")
    assert "ye" in cands2                     # ye_de i→e tersi

def test_ses_filtresi_pres():
    # 'yor' içermeyen yüzeyde pres hücreleri hiç enumerate edilmez
    hyps = an._enumerate("geldi", pos="verb")
    assert all(h.kwargs.get("tense") != "pres" for h in hyps)

def test_cati_zinciri_kapali_kume():
    assert len(an._VOICE_CHAINS) == 24
```

- [ ] **5.2** Koş → FAIL.
- [ ] **5.3** Implement:
  - `_REVERSE_MUT`: SPEC envanterinden (d→t, ğ→k, b→p, c→ç, ye_de i→e); `_root_candidates`
    önekleri üretir + son-ses mutasyon çeşitleri + son-hece ünlü geri-ekleme.
  - `_VOICE_CHAINS`: `[(), ("refl",)…]` — (refl|recip ≤1)×(caus 0-3)×(pass 0-1) = 24, modül sabiti.
  - `_FILTERS`: eksen-değeri → `re`-deseni tablosu (SPEC'ten); `_cell_allowed(surface, axis, value)`.
  - `_enumerate(surface, pos)`: kind başına grid; hücre filtre-geçerse `_Hyp(lemma, pos,
    kind, kwargs)` üret. Soru grubu / birleşik önek tokenizasyonu burada (tasarım §1.0).
  - Kwargs kanonikleştirme: `_canon(kwargs)` default'ları atar.
- [ ] **5.4** Koş → PASS; tam paket regresyonsuz. Commit:
  `feat(analysis): kök adayları + ses-filtreli grid enumerasyonu`

### Task 6: Oracle doğrulama + sıralama + segmentasyon → golden'lar GREEN

**Files:** Modify: `turkgram/analysis.py`, `turkgram/__init__.py`, `tests/test_analysis.py`

- [ ] **6.1** Golden koşucuları ekle (Task 2-3 golden'ları üzerinden failing):

```python
from tests.golden_analysis import GOLDEN_ANALYSIS
from tests.golden_segments import GOLDEN_SEGMENTS

@pytest.mark.parametrize("surface", sorted(GOLDEN_ANALYSIS))
def test_golden_precision_tam_kume(surface):
    got = {(a.lemma, a.pos, a.kind, tuple(sorted(a.kwargs.items())))
           for a in an.analyze(surface)}
    want = {(g["lemma"], g["pos"], g["kind"], tuple(sorted(g["kwargs"].items())))
            for g in GOLDEN_ANALYSIS[surface]}
    assert got == want                      # TAM küme: eksik=recall, fazla=precision

@pytest.mark.parametrize("surface", sorted(GOLDEN_SEGMENTS))
def test_golden_segments(surface):
    a = an.analyze(surface)[0]
    assert [(s.surface, s.label) for s in a.segments] == GOLDEN_SEGMENTS[surface]
    assert "".join(s.surface for s in a.segments) == surface.split()[-1]  # span garantisi

def test_deterministik_siralama():
    r1 = an.analyze("gelin"); r2 = an.analyze("gelin")
    assert r1 == r2 and len(r1) >= 2
```

- [ ] **6.2** Koş → FAIL. Implement:
  - `_KIND_FUNCS` (özel sabit): kind → üreteç fonksiyonu; `_verify(hyp)`:
    `try/except ValueError`, `None`→red, `çıktı == yüzey`→kabul. `functools.lru_cache`
    üreteç sarmalayıcısında.
  - Dedup doğrulamadan ÖNCE `(lemma, pos, kind, canon kwargs)` anahtarıyla.
  - Sıralama: `(len(segments), çatılı?, _KINDS.index(kind), lemma, repr(sorted(kwargs)))`.
  - `roots=` filtre + `hypothetical` bayrağı.
  - `_segment(analysis)`: kwargs doğrulandıktan sonra SPEC politikasıyla kesim (üreteci
    artan-eksen çağrılarıyla yeniden koşup büyüme noktalarından span çıkarma tekniği —
    ör. `decline(k)` vs `decline(k, case=...)` farkından durum ekinin dilimi).
  - `__init__.py`: `analyze`, `Analysis`, `Segment` dışa aç; `parse_verb` ↔ `analyze`
    ayrım cümlesi docstring'e.
- [ ] **6.3** Koş: golden'lar GREEN + tam paket regresyonsuz. Dosya >800 satırsa öneri
  üretimini `analysis_candidates.py`'ye ayır (davranış değişmeden, testler yeşil kalarak).
- [ ] **6.4** Commit: `feat(analysis): oracle doğrulama + segmentasyon — precision/segment golden yeşil`

### Task 7: Türkçe yüz — `tr.çözümle`

**Files:** Modify: `turkgram/tr.py`, `tests/test_tr.py`

- [ ] **7.1** Failing test (`tests/test_tr.py`):

```python
def test_cozumle_denklik():
    sonuçlar = tr.çözümle("okuyor", tür="fiil")
    a = sonuçlar[0]
    assert a.kwargs["kip"] == "şimdiki"              # kanonik Türkçe değer
    assert tr.çekimle(a.lemma, **a.kwargs) == "okuyor"  # Türkçe round-trip

def test_cozumle_bilinmeyen_tur():
    with pytest.raises(ValueError, match="tür"):
        tr.çözümle("okuyor", tür="olmayan")
```

- [ ] **7.2** Koş → FAIL. Implement: `_TERS_KIP/_TERS_KISI/_TERS_DURUM/_TERS_CATI/…`
  ters haritalar (alias çakışmasında kanonik temsilci: `past→görülen_geçmiş`,
  `loc→bulunma`, `caus→ettirgen`); kind→tr-fonksiyon eşlemesi; segment etiket
  Türkçeleştirme (`DIk→ortaç`…); `çözümle(yüzey, tür=None, *, kökler=None)`.
- [ ] **7.3** Koş → PASS; tam paket. Commit: `feat(tr): çözümle — Türkçe çözümleme yüzü`

### Task 8: Round-trip tam süpürme + bütçe bekçisi

**Files:** Modify: `tests/test_analysis.py`, `pyproject.toml`/`pytest.ini` (marker)

- [ ] **8.1** `slow` marker'ı tanımla; süpürme testi:

```python
LEMMA_SETI = ["yapmak", "okumak", "gitmek", "yemek", "gelmek", "aday olmak",
              "görmek", "gülmek", "almak", "yazmak", "düşmek", "öksürmek"]
# sınıf temsilcileri: düz/yumuşayan/ye_de/birleşik + aorist-Ir (almak) vs -Ar (yazmak)
# + ön-yuvarlak çok-heceli (öksürmek) — spec §4.1 sınıf listesi tam
AD_SETI = ["ev", "kitap", "genç", "araba", "burun"]

@pytest.mark.slow
def test_roundtrip_tam_supurme():
    eksik, çağrı_sayıları = [], []
    for kind, üret, girdiler in _sweep_space(LEMMA_SETI, AD_SETI):  # conftest yardımcısı
        yüzey = üret()
        if yüzey is None: continue
        an.reset_call_count()                    # sayaç analysis'in cache'li üreteç
        sonuçlar = an.analyze(yüzey)             # sarmalayıcısında (tek public hook)
        çağrı_sayıları.append(an.call_count())
        if not any((a.lemma, a.kind) == girdiler[:2] and a.kwargs == girdiler[2]
                   for a in sonuçlar):
            eksik.append((yüzey, girdiler))
    assert not eksik, f"recall açığı: {eksik[:10]}"
    p95 = sorted(çağrı_sayıları)[int(len(çağrı_sayıları) * 0.95)]
    assert p95 <= 2000, f"bütçe aşımı: p95={p95}"
```

  (`_sweep_space` ve `_call_counter` test-yardımcıları — analysis.py'de değil
  test dosyasında/conftest'te.)
- [ ] **8.2** Koş: `PYTHONUTF8=1 python -m pytest tests/test_analysis.py -m slow -q` →
  recall açıkları çıkarsa filtre/mutasyon envanterini düzelt (filtre GEVŞETMEK her zaman
  güvenli — recall'u artırır, precision'ı oracle korur). GREEN olana dek.
- [ ] **8.3** Hızlı alt-küme (marker'sız) commit-yolu testine ekle. Commit:
  `test(analysis): round-trip tam süpürme + p95 çağrı bütçesi`

### Task 9: Hakem + korpus + dokümantasyon + kapanış

**Files:** Modify: `CLAUDE.md`, `docs/faz2a-cozumleyici-tasarim.md`; geçici tarama scripti

- [ ] **9.1** **Filtre-sağlamlık hakemliği:** her ses-filtresi için, filtrenin budadığı
  rastgele ~200 hücreyi üret (`üret(hücre)`) → hiçbirinin yüzeyi filtre-desenini
  İÇERMEMELİ (önerme kanıtı). Script çıktısı 0 ihlal.
- [ ] **9.2** **Dilbilimsel adversarial hakem** (A1 emsali, ayrı ajan): golden dışı 30+
  zor yüzeyde analyze çıktısını dilbilgisiyle sına (refute stance); bulgular varsa düzelt.
- [ ] **9.3** **Korpus taraması:** dict-db TR başlıkları (fiil+isim) → temsili çekimler
  üret → hepsi `analyze`: 0 istisna + kendini-içerme + duvar-saati raporu. (Geçici
  script `work_*.py`, commit'lenmez.)
- [ ] **9.4** CLAUDE.md §7 durum + test sayısı; tasarım dokümanına "uygulandı" notu;
  gerekirse §6'ya yeni ince-ayrım maddeleri.
- [ ] **9.5** Tam paket son koşu (slow dahil) → Commit:
  `feat(analysis): çözümleyici — Faz 2a (round-trip + pedagojik segmentasyon)`

---

## Kesişen gereksinimler

- Her task sonunda `PYTHONUTF8=1 python -m pytest -q` REGRESYONSUZ (2005 + yeniler).
- Golden'lar motordan bağımsız kalır — golden dosyalarına motor davranışına göre
  "düzeltme" YAPILMAZ; ayrışmada önce dilbilgisi tahkimi (CLAUDE.md §2).
- Motor biçim SAKLAMAZ (#5): analizör hiçbir biçim listesi diske yazmaz; her şey runtime.
- Korkmaz düzyazı/örneği repoya girmez (#3); golden'lar elle-doğrulanmış biçimlerden.
