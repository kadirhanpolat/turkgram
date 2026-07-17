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
  **NOT [hakem #7]:** `parse.py` şu an `_tr_lower` import etmiyor (`_leaf_tag` Python `.lower()` kullanır);
  R8 İ/I güvenliği için `_tr_lower` import ETMELİ (impl planında).
- **Sınıflama etikete göre** (per-token analizden gelen `_tag`):
  - Çift **VERB** → **ulaç-tipi AdvP** (`koşa koşa`).
  - Çift **ADJ veya NOUN** → **tam-tipi AdvP** — AMA §3.3 NOUN-takip guard'ı.
- İşlev sözcükleri (CCONJ/ADP/X) doğal dışlanır (etiket VERB/ADJ/NOUN değil).

**KRİTİK — VERB sınıflamasının gerçek nedeni [hakem #2]:** Bare `-A` converb morfolojik envanterde YOK
(`nonfinite.CONVERBS` = {arak, ip, inca, eli, esiye, madan, dikce, meksizin}; bare `-A` yok). `koşa` per-token
**optatif** çözülür (`conjugate(koşmak, tense="opt", 3sg)` → `koşa`; `kind="conjugate"`), bu yüzden VERB
etiketlenir — "converb kind'i gizli" değil, `-A` biçimi **optatifle eşsesli**. Ayrıca
`converb_reduplicate(lemma)==surface` oracle'ı `roots` ister; `parse_phrase`'in roots'u YOK → oracle
parser bağlamında KULLANILAMAZ. Sonuç: yüzey-çift + POS sınıflaması **tek uygulanabilir signal**.

### 3.3 KRİTİK — NOUN-takip guard'ı (R1 çakışması)

Özdeş sıfat çifti **adnominal** da olabilir: `uzun uzun yollar` (pekiştirilmiş sıfat niteleyici → doğrusu
`NP(uzun uzun yollar)`, AdvP DEĞİL). Koşulsuz "özdeş çift → AdvP" bunu kırar.

**Guard (R6_ki bağlam-duyarlılığı emsali):** tam-tipi (ADJ/NOUN) çiftte, **sonraki token NOUN ise
AdvP KURMA** — R3/R1'e bırak (adnominal okuma korunur). Sonraki token NOUN değilse (VERB, cümle sonu, vb.)
→ AdvP. **Ulaç-tipi (VERB) çift guard'sız** — adnominal olamaz, her zaman AdvP.

**Guard NOUN yaprağını kontrol eder, NP'yi DEĞİL [hakem #1/#3]:** R8 pipeline'da R1'den ÖNCE çalışır → o anda
`nodes[i+2]` henüz **çıplak NOUN yaprağı**, NP oluşmamış. Guard `_tag(nodes[i+2]) == "NOUN"` bakar; "NP"
kontrolü R8-zamanında ölü koddur. `uzun uzun yollar` → guard `yollar`(NOUN) görür → skip → R3 `AdjP(uzun uzun)`
→ R1 `NP(AdjP, yollar)`. Doğru.

Guard recall-güvenli: geçerli bir adnominal yapıyı budamaz, yalnız AdvP kurmaz.

### 3.4 Kural sırası ve VP entegrasyonu

- **R8_redup pipeline'da R3+R1'den ÖNCE** — pratikte en öne konur. Gerçek kısıt "R3+R1'den önce" (R3 AdjP,
  R1 NP özdeş çifti yutmadan önce). En öne koymak GÜVENLİ ama zorunlu değil: R0 (gen+poss NP) özdeş çifti
  zaten eşleştirmez [hakem #1].
- **AdvP → VP-içi.** R5 absorpsiyon kümesine (`parse.py:335`) `"AdvP"` eklenir. Gerekçeler:
  1. **Dilbilimsel:** tarz zarfı fiil öbeği iç niteleyicisi (`[S özne [VP AdvP V]]`), cümle-kardeşi değil.
  2. **Mimari tutarlılık:** R5 zaten NP/PP/AdjP/CoordP absorbe eder; stop-list yalnız yan cümleler
     (DiyeP/CompP/RelP). AdvP yan cümle değil → doğal sınıfı NP/PP yanı. Stop-list'e DOKUNULMAZ.
     R5 `_node_is_nominative` kontrolü yalnız NP/NOUN'da çağrılır → AdvP özne sanılmaz (güvenli).

---

## 4. Düğüm yapısı ve dependency

- `PhraseNode.make("AdvP", (leaf1, leaf2))` — iki yaprak çocuk. Ek alan YOK (tür `full`/`converb`
  çocuklardan/etiketten kurtarılabilir; YAGNI). PP'nin `governs`'u gibi meta gerekmiyor.

**KRİTİK — AdvP dependency BEDAVA DEĞİL [hakem #5]:** İlk tasarım "advmod bedava gelir" diyordu; YANLIŞ.
`dependency.py` izlendi:
- `_child_deprel` (satır 156-194) `parent_tag in ("VP","S")` dalında child-tag dağıtımı `("NP","NOUN","CoordP")`,
  `"PP"`, `("AdjP",)→"advmod"` ele alır; **`"AdvP"` YOK** → son `return "dep"`'e düşer. Yani AdvP başı
  `deprel="dep"` alır, `advmod` DEĞİL.
- `_find_head_leaf` (satır 117-154) AdvP dalı yok → `children[-1]` (son yaprak) baş olur.

**Gerekli açık değişiklikler:**
1. `_child_deprel` VP/S dalına: `if child_tag in ("AdjP", "AdvP"): return "advmod"` (mevcut AdjP dalını genişlet).
   → AdvP **başı** (ilk yaprak) fiile `advmod`.
2. `_child_deprel`'e **AdvP-ebeveyn dalı** (iç ilişki): AdvP'nin İKİ yaprağı var; ikinci token (tekrar) birinciye
   bağlanır. UD standardı: `if parent_tag == "AdvP": return "compound:redup"`. Aksi halde ikinci yaprak `"dep"`
   alır (belirsiz). Bu, ikileme için doğru UD ilişkisidir.
3. `_find_head_leaf`'e AdvP dalı: `if tag == "AdvP": return _find_head_leaf(children[0])` (ilk yaprak baş;
   özdeş yüzey olduğundan children[0]/[-1] farkı görünmez ama açık kayıt için ilk).
4. Dependency golden: AdvP başının `advmod` (NOT `dep`) + ikinci tokenin `compound:redup` aldığını sabitle.

---

## 5. Kapsam dışı / bilinçli sınır

- **m-ikileme** (`kitap mitap`) → nominal, defer (§2).
- **Ulaç oracle doğrulaması:** V1 tespiti yüzey-çift + POS sınıflaması. `converb_reduplicate(lemma)==surface`
  oracle'ı `roots` ister → parser bağlamında KULLANILAMAZ (§3.2). Sonuç: bitişik özdeş VERB çifti (ör. nadir
  `geldi geldi`) de AdvP olur; recall-güvenli (başka geçerli okuma yok), pekiştirme sayılır.
- **`güle güle` selamlaması** [hakem #7]: VERB çifti → AdvP. Anlamsal olarak ünlem (adverbial değil) ama V1
  bunu bilinçli AdvP'ye toplar (recall-güvenli); anlam ayrımı uygulamaya bırakılır.
- **NUM/ADJ araya girmesi** (`uzun uzun beş yol`) [hakem #3]: guard yalnız hemen sonraki NOUN'a bakar; araya
  NUM girerse tam kapsanmaz — V1 defer, nadir.
- **Üç+ tekrar** (`yavaş yavaş yavaş`) — V1 ilk çifti yakalar; üçlü genelleme defer (üçüncü sıfat başıboş kalır).
- **Koordine zarf** (`yavaş yavaş ve hızlı hızlı`) [hakem #7]: R4 CoordP `NP CCONJ NP` ister, AdvP NP değil →
  koordinasyon kurulmaz. Defer.
- **Ayrık ikileme** / araya sözcük girmesi — kapsam dışı (bitişiklik şart).
- **Derece-sözcük çifti** (`çok çok`) [hakem #2]: özdeş ADJ çifti → sonraki NOUN değilse AdvP olur
  (`çok çok güzel` → AdvP `çok çok`); `çok çok kitap` → NOUN-takip guard skip. Golden ile sabitlenir.

---

## 6. İş akışı (CLAUDE.md §2 DEĞİŞMEZ)

1. **SPEC** — `spec/syntax-spec.md`'ye R8_redup kuralı + AdvP etiketi + guard elle yazılır (parse bölümü).
2. **Golden** — `tests/golden_adverbial.py` (veya mevcut parse golden'a ek), motordan BAĞIMSIZ (Opus,
   motor-körü): tam-AdvP (`yavaş yavaş yürüdü`), ulaç-AdvP (`koşa koşa geldi`), adnominal-guard
   (`uzun uzun yollar` → NP, AdvP YOK), derece-çift (`çok çok güzel` → AdvP; `çok çok kitap` → NP),
   VP-içi absorpsiyon, **dependency `advmod`** (CoNLL-U), regresyon (mevcut parse ağaçları).
3. **Motor** — `_apply_r8_redup` + pipeline R3'ten öne + R5 absorpsiyon kümesine AdvP + `parse.py`'ye
   `_tr_lower` import + `dependency.py` `_child_deprel` (AdvP→advmod) + `_find_head_leaf` (AdvP dalı).
4. **Hakem + doğrulama** — golden + korpus tarama (parse çökme yok) + mevcut E2/E3/E4 parse testleri yeşil +
   tam paket regresyonsuz.

---

## 7. Değişmezler (test sonrası doğrulanacak)

- `yavaş yavaş yürüdü` → `S` içinde `VP(AdvP(yavaş yavaş), yürüdü)`; `AdvP` etiketi, `AdjP` DEĞİL.
- `koşa koşa geldi` → `VP(AdvP(koşa koşa), geldi)`; başıboş VERB kalmaz.
- `uzun uzun yollar` → `NP(...)`, AdvP KURULMAZ (adnominal guard).
- Mevcut parse ağaçları (E2/E3/E4 testleri) DEĞİŞMEZ (AdvP yalnız özdeş-çift + non-NOUN-takip'te).
- E5/E6 AdvP başını fiile `advmod` bağlar — **`dependency.py` açık AdvP dalıyla** (§4; bedava değil).
- Yeni etiket/kural geriye uyumu kırmaz.
