# Edat Analizi — Tasarım Dokümanı

**Tarih:** 2026-07-17
**Faz:** 5 D2-devamı (ertelenen edat analizini açma)
**Durum:** Onaylandı (brainstorming) → SPEC + implementasyon planı bekliyor

---

## 1. Amaç ve bağlam

`postposition.py` edat **üretimi** yapıyor (19 edat, `postposition()`), `parse.py` R2 kuralı **PP düğümü**
oluşturuyor, ama `analyze()` edatları **hiç tanımıyor** — `analyze("için")` şu an çöp döndürüyor:
`için`'i isim (`decline`) ve `içinmak` (fiil imp-2sg) sanıyor.

Bu özellik ertelenmişti (`spec/postposition-spec.md §1`: "Edat analizi → sözdizimsel bağlam gerektirir,
defer"). Faz E (`parse.py`) tamamlandığı için sözdizimsel bağlam artık mevcut → erteleme açılıyor.

**Kullanıcı kararı:** İki katman birlikte:
1. **Tek-token analiz** (`_try_postposition_all`) — asıl ertelenen madde.
2. **PP doğrulaması** (`parse.py` R2 zenginleştirme) — üstüne gelen bonus.

---

## 2. Çekirdek mimari karar — tek doğruluk kaynağı

### 2.1 Sorun: üç ayrı, sapmış edat tablosu

Bulgu (brainstorming): edat bilgisi iki yerde, birbirinden sapmış:

| | `postposition.py` (`_POSTPOSITION_CASE`) | `context.py` (`_POSTP_GOV`, K2) |
|---|---|---|
| Amaç | Üretim: **tek** case seçer | K2 doğrulama: **kabul edilen case kümesi** |
| Yalnız burada | `üzere`, `başka`, `dek`, `aşkın` | `dair`, `ilişkin`, `ait`, `yana` |
| `için` | `nom` (isim) / `gen` (zamir asimetrisi) | `{nom, gen}` (birleşik küme) |

Yeni analiz dalı **üçüncü** kopya olacaktı → drift derinleşir. Kod-stili "tek doğruluk kaynağı" ilkesi ihlali.

### 2.2 Çözüm: veriyi konsolide et, K2 mantığına DOKUNMA

`postposition.py`'de **tek zengin tablo**; üretim, analiz ve K2 hepsi oradan beslenir.

```python
# postposition.py — TEK KAYNAK
_POSTPOSITIONS = {
    "için":  {"üret": "nom", "üret_zamir": "gen", "yönet": frozenset({"nom", "gen"}), "üretilebilir": True},
    "sonra": {"üret": "abl",                        "yönet": frozenset({"abl"}),       "üretilebilir": True},
    "dair":  {                                      "yönet": frozenset({"dat"}),       "üretilebilir": False},
    ...
}
```

- `üret` — `postposition()` üretiminin seçtiği tek case (mevcut mantık KORUNUR).
- `üret_zamir` — yalnız `için` için asimetri (zamir → gen); yoksa `üret` kullanılır.
- `yönet` — K2 doğrulaması + tek-token analiz için **kabul edilen case kümesi**.
- `üretilebilir` — `False` ise `postposition()` `ValueError` (donmuş kalıp edatlar; bkz §5).

**K2 mantığı DEĞİŞMEZ.** Yalnız veri kaynağı değişir:
```python
# context.py
_POSTP_GOV = {edat: v["yönet"] for edat, v in _POSTPOSITIONS.items()}
```
K2 algoritması (yumuşak ağırlık +4/−2, recall-güvenli) aynen kalır. Mevcut K2 testleri (7500+4800 cümle)
yeşil kalırsa davranış korunmuş demektir — güvenlik ağı.

---

## 3. Tek-token analiz (`_try_postposition_all`)

### 3.1 Şema

```python
Analysis(
    lemma="için",          # edatın kendisi
    pos="postp",           # yeni POS (mevcut "conj" geleneğiyle uyumlu)
    kind="postposition",   # _KINDS'a SONA eklenir
    kwargs={},             # BOŞ — bağlaç deseni gibi
    segments=(("için", "kök"),),
    hypothetical=False,    # closed-set → her zaman güvenilir
)
```

### 3.2 Davranış — additive, oracle-free, closed-set

Bağlaç `de`/`da` deseninin birebir aynası:
- **Her zaman döner** (roots'tan bağımsız); edatlar çekilmeyen kapalı-küme işlev sözcükleri.
- **Additive** — hiçbir şeyin yerini almaz, mevcut okumaların yanına eklenir.
- **Belirsizlik kendiliğinden düşer:** `analyze("sonra")` hem `postposition` hem (eşsesli) zarf/isim
  okumalarını döner; `analyze("göre")` hem `postposition` hem `gör-e` ulaç okumasını. Disambiguation sıralar.
  (Emsal: `de` = bağlaç + `demek` imp-2sg belirsizliği.)

**`kwargs={}` gerekçesi:** Edatın yönettiği durum lemmadan türetilebilir (tablo lookup). Onu kwargs'a koymak
tabloyu kopyalar + golden'ı şişirir. İlke: kwargs *ayırt edeni* taşır, türetilebilir veriyi değil.

### 3.3 Entegrasyon

```python
# analyze() içinde, mevcut _try_*_all deseninin yanında
if pos in (None, "postp"):
    _try_postposition_all(surface_token, analyses, seen)
```
`_KINDS`'a `"postposition"` (SONA), `_POS`'a `"postp"` eklenir.

---

## 4. PP doğrulaması (`parse.py` R2)

Şu an ADP yaprağı `.analysis` taşımıyor (yüzey-tanıma). Değişiklik:
- ADP tokeni artık `_try_postposition_all`'dan gelen postposition analizini taşır.
- R2, PP düğümüne **`governs` (yönetilen durum kümesi)** iliştirir.
- NP tümlecinin durumu `governs`'a uyuyor mu → **yumuşak uyum işareti** (K2 gibi: işaretle, **ASLA reddetme**).
  Recall-güvenli — geçerli hiçbir PP yapısı budanmaz.

**Asıl kazanç:** Bu case bilgisi E5/E6 dependency/CoNLL-U katmanında `case` ilişkisini besler.

**`için`/zamir asimetrisi burada çözülür:** Tek-token analizde `için`'in tümlecini bilmeyiz →
analiz `yönet={nom,gen}` der. Asimetri (isim→nom, zamir→gen) *yalnız PP doğrulamasında* devreye girer,
çünkü orada tümleci (önceki NP) görürüz. İki-alanlı tablonun (`üret` vs `yönet`) varlık gerekçesi budur.

---

## 5. Tablo uzlaştırması — gramer olgusu

Birleşim: 23 edat. İhtilaflı 8'in her biri standart Türkçe gramer (Korkmaz/Ergin/Deny/Vural teyitli):

**K2'de olup üretimde olmayanlar → `üretilebilir: False` (donmuş kalıp, `yönet`-only):**
| Edat | yönet | Örnek | Not |
|------|-------|-------|-----|
| dair | dat | buna dair, konuya dair | `-e dair`; donmuş, `postposition()` üretmez |
| ilişkin | dat | soruna ilişkin | `-e ilişkin`; donmuş |
| ait | dat | bana ait, okula ait | `-e ait`; donmuş |
| yana | abl | benden yana | `-den yana`; donmuş |

**Üretimde olup K2'de olmayanlar → `yönet` kümesine eklenir (K2 artık doğrular):**
| Edat | yönet | Örnek |
|------|-------|-------|
| dek | dat | eve dek |
| üzere | nom | bu şart üzere |
| başka | abl | evden başka |
| aşkın | acc | yüzü aşkın |

**Neden `yönet`-only edatlar üretilemez?** `dair`/`ilişkin`/`ait`/`yana` donmuş sözcükler; `postposition()`
onları üretmeye çalışırsa yanlış olur → `üretilebilir: False` guard, `ValueError`. Ama analiz + K2 tanır.
Bu, gizli bir envanter tutarsızlığı bug'ını da kapatır.

---

## 6. Kapsam dışı (bilinçli sınır)

- **Çok-kelimeli edatlar** (`-e karşın`, `bir türlü`) — sözdizimsel, defer.
- **Edatın anlamsal seçimi** (hangi edat kullanılmalı) — uygulamaya bırakılır.
- **`bitişik ile` alternatif analiz** (`evle` → ev+ile-bitişik): `evle` zaten `decline(case='ins')`'ten
  gelir; ayrı postposition etiketi V1'de eklenmez (gerekirse sonra, roots-gated).

---

## 7. İş akışı (CLAUDE.md §2 DEĞİŞMEZ)

1. **SPEC** — `spec/postposition-spec.md` §Analiz bölümü elle yazılır (defer notu kaldırılır) + `_POSTPOSITIONS`
   tablosu belgelenr.
2. **Golden** — `tests/golden_postposition_analysis.py`, motordan BAĞIMSIZ (Opus, motor-körü):
   tek-token analiz (19+4 edat) + belirsizlik (`sonra`/`göre`) + PP uyum örnekleri.
3. **Motor** — `_POSTPOSITIONS` konsolidasyonu + `_try_postposition_all` + `parse.py` R2 + `context.py`
   kaynak değişimi.
4. **Hakem + doğrulama** — golden + korpus tarama (26k leksikon, 0 çökme) + K2 testleri yeşil (davranış korundu)
   + tam paket regresyonsuz.

---

## 8. Değişmezler (test sonrası doğrulanacak)

- `analyze(roots=None)` postposition dalıyla **her zaman** postposition okuması döner (closed-set).
- `postposition()` üretim çıktısı **DEĞİŞMEZ** (mevcut 86-girdi golden yeşil kalır).
- K2 davranışı **DEĞİŞMEZ** (context.py testleri yeşil).
- PP doğrulaması hiçbir geçerli yapıyı budamaz (recall-güvenli).
- `_KINDS`/`_POS` genişlemesi geriye uyumu kırmaz.
