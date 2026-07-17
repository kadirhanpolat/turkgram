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
    "için":  {"üret": "nom", "üret_zamir": "gen", "yönet": frozenset({"nom", "gen"}),      "üretilebilir": True},
    "ile":   {"üret": "nom",                       "yönet": frozenset({"nom", "gen"}),      "üretilebilir": True},
    "gibi":  {"üret": "nom",                       "yönet": frozenset({"nom", "gen"}),      "üretilebilir": True},
    "kadar": {"üret": "dat",                       "yönet": frozenset({"nom", "gen", "dat"}), "üretilebilir": True},
    "sonra": {"üret": "abl",                       "yönet": frozenset({"abl"}),             "üretilebilir": True},
    "dair":  {                                     "yönet": frozenset({"dat"}),             "üretilebilir": False},
    ...
}
```

- `üret` — `postposition()` üretiminin seçtiği tek case (mevcut mantık KORUNUR).
- `üret_zamir` — yalnız `için` için asimetri (zamir → gen); yoksa `üret` kullanılır.
  `_ICIN_GEN_PRONOUNS` kümesi **korunur** — `üret_zamir` yalnız *hangi case* seçileceğini söyler,
  zamir kümesini kodlamaz (`onlar→nom` istisnası dahil mevcut mantık aynen kalır). [hakem #9]
- `yönet` — K2 doğrulaması + tek-token analiz için **kabul edilen case KÜMESİ**.
  **KRİTİK [hakem #1]:** `yönet` tek-case `üret`'ten TÜRETİLMEZ — elle, tam kabul-kümesi olarak yazılır.
  `ile`/`gibi` zamirlerde genitif alır (*benim ile*, *benim gibi*), `kadar` hem gen hem dat
  (*senin kadar*, *bana kadar*). Bunlar dilbilimsel olarak yüklü ve K2'de zaten var:
  `ile→{nom,gen}`, `gibi→{nom,gen}`, `kadar→{nom,gen,dat}` **aynen korunmalı**.
- `üretilebilir` — `False` ise `postposition()` `ValueError` (donmuş kalıp edatlar; bkz §5).

**K2 mantığı (algoritma) DEĞİŞMEZ.** Yalnız veri kaynağı değişir:
```python
# context.py
_POSTP_GOV = {edat: v["yönet"] for edat, v in _POSTPOSITIONS.items()}
```
K2 algoritması (yumuşak ağırlık +4/−2, recall-güvenli) aynen kalır.

**Regresyon kilidi [hakem #1]:** Golden'da build-time assertion —
`{e: v["yönet"] for e,v in _POSTPOSITIONS.items()}`'ın mevcut 19 edat için mevcut `_POSTP_GOV`'a
**birebir eşit** olduğu (yeni 4 edatla genişletilmiş) test edilir. Böylece `ile`/`gibi`/`kadar`'ın
`gen`/`nom` kümesi sessizce daralırsa test kırmızı olur — "testler yeşil kalsın" temennisine güvenilmez.

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
# analyze() içinde, _try_conjunction_all'ın YANINDA (her ikisi yüzey closed-set), derivation'dan ÖNCE
if pos in (None, "postp"):
    _try_postposition_all(surface_token, analyses, seen)
```
- `_KINDS`'a `"postposition"` (SONA), `_POS`'a `"postp"` eklenir.
- **Dispatch sırası [hakem #4a]:** conjunction ile aynı grupta (yüzey closed-set), number/derivation'dan
  ÖNCE. Sıra `seen` set'i ve `_sort_key` (`_KINDS.index`) için önemli.
- **`pos="postp"` çağrısı [hakem #4b]:** Tüm branch guard'ları `pos in (None, X)` olduğundan, `pos="postp"`
  ile çağrı YALNIZ postposition dalını çalıştırır (verb/noun/num/conj/derivation atlanır). Bu kapalı
  davranış BİLİNÇLİ ve doğru.
- **`_POS_TO_TAG` [hakem #8]:** `parse.py`'ye `"postp": "ADP"` eklenir (robustluk; `_leaf_tag` zaten
  yüzeyden ADP etiketliyor ama gelecekteki yollar için).

---

## 4. PP doğrulaması (`parse.py` R2)

Şu an ADP yaprağı postposition analizi taşımıyor (`_leaf_tag` yüzeyden ADP etiketler). Değişiklik:
- `_try_postposition_all` sayesinde ADP tokeninin `LeafNode.analysis`'i artık `Analysis(kind="postposition")`
  taşır → R2 buna güvenebilir.
- R2, PP düğümüne **`governs` (yönetilen durum kümesi)** iliştirir.
- NP tümlecinin durumu `governs`'a uyuyor mu → **yumuşak uyum işareti** (K2 gibi: işaretle, **ASLA reddetme**).
  Recall-güvenli — geçerli hiçbir PP yapısı budanmaz.

**`PhraseNode` şema değişikliği [hakem #7]:** `PhraseNode` `@dataclass(frozen=True)`. `governs` "bedava
iliştirme" DEĞİL — yeni opsiyonel alan gerekir: `governs: frozenset[str] | None = None`. Varsayılan `None`
→ R0/R1/R3… düğümleri eşitlik karşılaştırmasında DEĞİŞMEZ (mevcut PhraseNode testleri kırılmaz). Yalnız
PP düğümü dolu `governs` taşır.

**Asıl kazanç:** Bu case bilgisi E5/E6 dependency/CoNLL-U katmanında `case` ilişkisini besler.

**`için`/zamir asimetrisi burada çözülür:** Tek-token analizde `için`'in tümlecini bilmeyiz →
analiz `yönet={nom,gen}` der. Asimetri (isim→nom, zamir→gen) *yalnız PP doğrulamasında* devreye girer,
çünkü orada tümleci (önceki NP) görürüz. İki-alanlı tablonun (`üret` vs `yönet`) varlık gerekçesi budur.
**Zamir yolu [hakem #7]:** `benim için`'de `benim` pronoun-genitif → `_leaf_tag` NOUN/NP etiketler mi
doğrula (R2 eşleşmesi için); çıplak `ben` (durumsuz) R2'yi tetiklemez — bu doğal sınır.

---

## 5. Tablo uzlaştırması — gramer olgusu

Birleşim: 23 edat. İhtilaflı 8'in her biri standart Türkçe gramer (Korkmaz/Ergin/Deny/Vural teyitli):

**K2'de olup üretimde olmayanlar → `üretilebilir: False` (donmuş kalıp, `yönet`-only):**
| Edat | yönet | Örnek | Not |
|------|-------|-------|-----|
| dair | {dat} | buna dair, konuya dair | `-e dair`; donmuş, `postposition()` üretmez |
| ilişkin | {dat} | soruna ilişkin | `-e ilişkin`; donmuş |
| ait | {dat} | bana ait, okula ait | `-e ait`; donmuş |
| yana | {abl} | benden yana | `-den yana`; donmuş |

Bu 4 edat `parse.py` ADP tanıma kümesine de eklenir (aksi halde R2 *buna dair* için PP kurmaz) [hakem #3].

**Üretimde olup K2'de olmayanlar → `yönet` kümesine eklenir (K2 artık doğrular):**
| Edat | yönet | Örnek |
|------|-------|-------|
| dek | {dat} | eve dek |
| üzere | {nom} | bu şart üzere |
| başka | {abl} | evden başka |
| aşkın | {acc} | yüzü aşkın |

**Neden `yönet`-only edatlar üretilemez?** `dair`/`ilişkin`/`ait`/`yana` donmuş sözcükler; `postposition()`
onları üretmeye çalışırsa yanlış olur → `üretilebilir: False` guard, `ValueError`. Ama analiz + K2 tanır.
Bu, gizli bir envanter tutarsızlığı bug'ını da kapatır.

**`postposition()` iki ayrı ValueError [hakem #5]:**
- `edat not in _POSTPOSITIONS` → bilinmeyen edat; `Geçerliler:` listesi **yalnız `üretilebilir:True`**.
- `not v["üretilebilir"]` → donmuş edat: ayrı mesaj (`'dair' donmuş bir edat, üretilemez`).
`dair` "Geçerliler" listesinde GÖRÜNMEZ (kullanıcı geçerli sanıp farklı hata almaz).

**K2 kapsamı — genişleme bir DAVRANIŞ değişikliğidir [hakem #2]:** §5'teki 4 yeni edat (`dek`/`üzere`/
`başka`/`aşkın`) `yönet`'e girince K2 artık onlar için de tetiklenir (önceden sessizdi). "K2 DEĞİŞMEZ"
değişmezi bu yüzden şöyle daraltılır: *K2 mevcut 19 edat için davranışı DEĞİŞMEZ; 4 yeni edat için K2 artık
doğrular (yeni davranış, recall-güvenli olduğu hakemle teyit edilir).* `aşkın→{acc}` çok yaygın
`aşk+ın` (isim gen/2sg-poss) okumasıyla çakışır → §7 golden adversarial homograf içermeli.

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
   tek-token analiz (19+4 edat) + belirsizlik (`sonra`/`göre`) + **adversarial homograflar** [hakem #6]
   (`aşkın`=isim, `başka`=sıfat, `üzere`=`üzer+e`) — postposition okuması doğru okumayı geçmemeli +
   PP uyum örnekleri. Ayrıca **`_POSTP_GOV` eşitlik assertion'ı** [hakem #1].
3. **Motor** — `_POSTPOSITIONS` konsolidasyonu + `_try_postposition_all` + `parse.py` R2 (`governs` alanı) +
   `context.py` kaynak değişimi + `parse.py` ADP kümesi genişletme + `_POS_TO_TAG`.
4. **Hakem + doğrulama** — golden + korpus tarama (26k leksikon, 0 çökme) + K2 testleri yeşil (mevcut 19
   davranış korundu; 4 yeni recall-güvenli teyit) + `postposition()` 86-girdi golden yeşil (üretim korundu)
   + tam paket regresyonsuz.

---

## 8. Değişmezler (test sonrası doğrulanacak)

- `analyze(roots=None)` postposition dalıyla **her zaman** postposition okuması döner (closed-set).
- `postposition()` üretim çıktısı **DEĞİŞMEZ** (mevcut 86-girdi golden yeşil kalır).
- K2 **mevcut 19 edat** için davranışı **DEĞİŞMEZ**; 4 yeni edat için doğrular (recall-güvenli). [hakem #2]
- `_POSTP_GOV` (türetilen) mevcut 19 kabul-kümesine **birebir eşit** (build-time golden). [hakem #1]
- PP doğrulaması hiçbir geçerli yapıyı budamaz (recall-güvenli).
- `PhraseNode.governs` varsayılan `None` → mevcut düğüm eşitlik testleri kırılmaz. [hakem #7]
- `_KINDS`/`_POS` genişlemesi geriye uyumu kırmaz.
