# İkileme Adverbial-Yeniden-Kurulum — Tasarım Dokümanı

**Tarih:** 2026-07-18
**Faz:** E-devamı (Faz 2a/2b'den ertelenen sözdizimsel madde)
**Durum:** Onaylandı (brainstorming) → SPEC + implementasyon planı bekliyor

---

## 1. Amaç ve bağlam

İkileme MORFOLOJİK olarak çözülü (Faz 9d: `_try_reduplication_all` → `reduplication_full`/
`reduplication_converb`/`reduplication_m`). Ama bu **birleşik (multi-token)** bir analiz: `analyze("yavaş
yavaş")` iki tokeni kapsayan tek `Analysis` döndürür. `parse_phrase` ise **token-başına** analiz tüketir
(her tokene bir `LeafNode`). Sonuç: ikileme parse ağacında **hiç temsil edilmiyor**, parser'da **zarf öbeği
(AdvP) etiketi de yok**.

**Şu anki bozuk davranış:**
- `yavaş yavaş yürüdü`: R3 (`ADJ ADJ+ → AdjP`) iki `yavaş`'ı **yanlışlıkla AdjP** olarak yutuyor (derece-
  nitelenmiş sıfat sanıyor), sonra R5 VP'ye alıyor → yanlış etiket.
- `koşa koşa geldi`: `koşa` per-token VERB etiketlenir; R5 absorpsiyon kümesi VERB içermez → iki `koşa`
  **başıboş kalır**, VP yalnız `geldi`'yi sarar → **bozuk parse**.

Bu madde ertelenmişti (sözdizimsel; asıl neden birleşik-analiz ile token-akışı arayüz uyuşmazlığı). Faz E
(`parse.py`) tamamlandığı için açılıyor.

---

## 2. Kapsam (kullanıcı kararı)

**YALNIZ gerçekten adverbial olan iki tür:**
- **Tam ikileme** → `AdvP`: `yavaş yavaş` ("yavaşça"), `hızlı hızlı`.
- **Ulaç ikilemesi** → `AdvP`: `koşa koşa` ("koşarak"), `güle güle`.

**Kapsam DIŞI (defer):**
- **m-ikileme** (`kitap mitap`) → adverbial DEĞİL, genelleyici/pekiştirici **ad** (nesne rolü). Ayrı
  nominal iş, sözdizimsel olarak defer kalır.
- İkilemenin anlamsal yorumu (hangi tarz/derece) — uygulamaya bırakılır.

**Etiket:** `AdvP` (mevcut `NP/VP/PP/AdjP/CoordP/CompP/RelP/DiyeP` İngilizce-kısaltma geleneğine uyar).

---

## 3. Çekirdek mimari karar — yüzey-tabanlı parser kuralı

### 3.1 Mekanizma (A): parser içi yeniden-kurulum

R6_ki/R7_diye emsali (yüzey-tabanlı kapalı tespit). Parser bitişik tokenlerden ikilemeyi doğrudan yeniden
kurar; **birleşik analizi HİÇ kullanmaz** → ertelemeye yol açan token:analiz arayüz sorununu tamamen atlar.

Reddedilen (B): `parse_text`/`parse_phrase`'e birleşik ikileme analizini enjekte etmek → token:analiz
sözleşmesini bozar (asıl erteleme nedeni).

### 3.2 Tespit — bitişik özdeş çift + POS sınıflaması

Yeni kural **R8_redup** (`_apply_r8_redup`):
- İki bitişik yaprak `_tr_lower(token[i]) == _tr_lower(token[i+1])` (özdeş, büyük/küçük harf duyarsız).
- **Sınıflama etikete göre** (per-token analizden gelen `_tag`):
  - Çift **VERB** → **ulaç-tipi AdvP** (`koşa koşa`; converb morfolojisi kind'de görünmez, yüzey-çift signal).
  - Çift **ADJ veya NOUN** → **tam-tipi AdvP** — AMA §3.3 NOUN-takip guard'ı.
- İşlev sözcükleri (CCONJ/ADP/X) doğal dışlanır (etiket VERB/ADJ/NOUN değil).

### 3.3 KRİTİK — NOUN-takip guard'ı (R1 çakışması)

Özdeş sıfat çifti **adnominal** da olabilir: `uzun uzun yollar` (pekiştirilmiş sıfat niteleyici → doğrusu
`NP(uzun uzun yollar)`, AdvP DEĞİL). Koşulsuz "özdeş çift → AdvP" bunu kırar.

**Guard (R6_ki bağlam-duyarlılığı emsali):** tam-tipi (ADJ/NOUN) çiftte, **sonraki token NOUN/NP ise
AdvP KURMA** — R3/R1'e bırak (adnominal okuma korunur). Sonraki token NOUN değilse (VERB, cümle sonu, vb.)
→ AdvP. **Ulaç-tipi (VERB) çift guard'sız** — adnominal olamaz, her zaman AdvP.

Guard recall-güvenli: geçerli bir adnominal yapıyı budamaz, yalnız AdvP kurmaz.

### 3.4 Kural sırası ve VP entegrasyonu

- **R8_redup pipeline'da EN ÖNCE** (R0'dan bile önce). Gerekçe: R3 (AdjP) ve R1 (NP) özdeş çifti yutmadan
  önce yakalanmalı. R0 (gen+poss NP) özdeş çifti zaten eşleştirmez → çakışma yok.
- **AdvP → VP-içi.** R5 absorpsiyon kümesine (`parse.py:335`) `"AdvP"` eklenir. Gerekçeler:
  1. **Dilbilimsel:** tarz zarfı fiil öbeği iç niteleyicisi (`[S özne [VP AdvP V]]`), cümle-kardeşi değil.
  2. **Mimari tutarlılık:** R5 zaten NP/PP/AdjP/CoordP absorbe eder; stop-list yalnız yan cümleler
     (DiyeP/CompP/RelP). AdvP yan cümle değil → doğal sınıfı NP/PP yanı. Stop-list'e DOKUNULMAZ.
  3. **E5/E6 bedava:** `_process_children` VP başını şeffaf geçer → AdvP `advmod` olarak fiile doğru bağlanır.

---

## 4. Düğüm yapısı ve dependency

- `PhraseNode.make("AdvP", (leaf1, leaf2))` — iki yaprak çocuk. Ek alan YOK (tür `full`/`converb`
  çocuklardan/etiketten kurtarılabilir; YAGNI). PP'nin `governs`'u gibi meta gerekmiyor.
- **E5/E6 (`dependency.py`):** AdvP başı = ilk yaprak; fiile `advmod` ilişkisiyle bağlanır. `_process_children`
  şeffaf VP-başı geçişi bunu bedava sağlar (AdvP VP içinde). Yeni özel durum GEREKMEZ — doğrulanacak.

---

## 5. Kapsam dışı / bilinçli sınır

- **m-ikileme** (`kitap mitap`) → nominal, defer (§2).
- **Ulaç oracle doğrulaması:** V1 tespiti yüzey-çift + POS sınıflaması. `converb_reduplicate(lemma)==surface`
  oracle'ıyla sıkılaştırma (yalnız gerçek `-A` converb) OPSİYONEL — V1'de yok. Sonuç: bitişik özdeş VERB
  çifti (ör. nadir `geldi geldi`) de AdvP olur; recall-güvenli (başka geçerli okuma yok), pekiştirme sayılır.
- **Üç+ tekrar** (`yavaş yavaş yavaş`) — V1 ilk çifti yakalar; üçlü genelleme defer.
- **Ayrık ikileme** / araya sözcük girmesi — kapsam dışı (bitişiklik şart).

---

## 6. İş akışı (CLAUDE.md §2 DEĞİŞMEZ)

1. **SPEC** — `spec/syntax-spec.md`'ye R8_redup kuralı + AdvP etiketi + guard elle yazılır (parse bölümü).
2. **Golden** — `tests/golden_adverbial.py` (veya mevcut parse golden'a ek), motordan BAĞIMSIZ (Opus,
   motor-körü): tam-AdvP (`yavaş yavaş yürüdü`), ulaç-AdvP (`koşa koşa geldi`), adnominal-guard
   (`uzun uzun yollar` → NP, AdvP YOK), VP-içi absorpsiyon, regresyon (mevcut parse ağaçları).
3. **Motor** — `_apply_r8_redup` + pipeline en-öne + R5 absorpsiyon kümesine AdvP + `_POS_TO_TAG`/
   dependency `advmod`.
4. **Hakem + doğrulama** — golden + korpus tarama (parse çökme yok) + mevcut E2/E3/E4 parse testleri yeşil +
   tam paket regresyonsuz.

---

## 7. Değişmezler (test sonrası doğrulanacak)

- `yavaş yavaş yürüdü` → `S` içinde `VP(AdvP(yavaş yavaş), yürüdü)`; `AdvP` etiketi, `AdjP` DEĞİL.
- `koşa koşa geldi` → `VP(AdvP(koşa koşa), geldi)`; başıboş VERB kalmaz.
- `uzun uzun yollar` → `NP(...)`, AdvP KURULMAZ (adnominal guard).
- Mevcut parse ağaçları (E2/E3/E4 testleri) DEĞİŞMEZ (AdvP yalnız özdeş-çift + non-NOUN-takip'te).
- E5/E6 `advmod` AdvP başını fiile bağlar (yeni özel durum gerekmez).
- Yeni etiket/kural geriye uyumu kırmaz.
