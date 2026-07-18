# m-İkileme Nominal-Yeniden-Kurulum — Tasarım Dokümanı

**Tarih:** 2026-07-18
**Faz:** E-devamı (ikileme adverbial-yeniden-kurulumun nominal kardeşi)
**Durum:** Onaylandı (kullanıcı kararı: NP temsili + reduplikant upos=NOUN) → SPEC + plan + implementasyon

---

## 1. Amaç ve bağlam

m-İkileme (`kitap mitap`, `araba maraba`) MORFOLOJİK olarak çözülü (Faz 9d:
`_try_reduplication_all` → `reduplication_m`, `m_reduplicate(token1)==surface` yüzey testi).
Ama bu **birleşik (multi-token)** analiz; `parse_phrase` **token-başına** analiz tüketir. İkinci
token (`mitap`) gerçek sözcük DEĞİL → tek başına analizsiz → parser'da **`X` etiketi** alır.

İkileme adverbial işinde (2026-07-18, AdvP) m-ikileme bilinçli **kapsam dışı** bırakılmıştı:
adverbial değil, **genelleyici/pekiştirici ad** (nesne/özne rolü) — "kitaplar ve benzeri şeyler".
Ayrı nominal iş olarak ertelenmişti. Bu doküman onu açar.

**Şu anki bozuk davranış (ölçüldü):**
- `kitap mitap aldı` → `S(NP(kitap), X(mitap), VP(aldı))` — `kitap` yalın NP (özne sanılır),
  `mitap` **başıboş X**, birlikte tek nominal öbek KURULMAZ.
- `araba maraba aldı` → aynı bozukluk (`maraba` başıboş X).

---

## 2. Kapsam (kullanıcı kararı)

**NOUN-tabanlı m-ikileme → NP:**
- `kitap mitap` ("kitaplar ve benzeri"), `araba maraba`, `para mara` → tek **`NP`** öbeği.
- Baş = ilk token (gerçek isim); m-parçası (ikinci token) reduplikant.

**ADJ-tabanlı m-ikileme → AdjP (V2, 2026-07-18 genişletme):**
- `güzel müzel`, `yeşil meşil` — sıfat m-ikilemesi, **adjectival** (isim niteler:
  `güzel müzel elbise`). Taban ADJ → tek **`AdjP`** öbeği; R1 onu isim niteleyicisi olarak alır
  (`NP(AdjP(güzel müzel), elbise)`), R5 AdjP'yi absorbe eder. Baş = taban sıfat.
- Reduplikant upos = **taban POS'undan miras** (NOUN taban→NOUN, ADJ taban→ADJ). Tek `MRED`
  iç etiketi korunur; upos `deps` head-bağından (compound:redup) türetilir → iki tag GEREKMEZ.
- `_find_head_leaf` AdjP "en sağdaki ADJ" mantığı tabanı zaten baş bulur (MRED≠ADJ) + fallback
  MRED-atlama guard (NP emsali).

**Kapsam DIŞI (defer):**
- **`çocuk mocuk` gibi disambiguation-quirk** [ölçüldü]: `çocuk` izole analizinde ADJ etiketlenir
  (disambiguation tuhaflığı) → NOUN-taban guard'ıyla tetiklenmez. m-ikilemeye özgü DEĞİL, ayrı
  disambiguation açığı. Defer.
- m-ikilemenin anlamsal yorumu (genelleyici mi pekiştirici mi) — uygulamaya bırakılır.
- Tam ikileme + ulaç ikilemesi → **AdvP** (ayrı iş, 2026-07-18 TAMAMLANDI).

**Etiket:** `NP` (kullanıcı kararı) — ismin özne/nesne rolünü R1/R5 makinesi DOĞRUDAN oynar,
ek entegrasyon (RedupP → R1/R2/R4/R5 eklemesi) GEREKMEZ. Reduplikant iç etiketi: **`MRED`**
(yalnız `_child_deprel` compound:redup + upos eşleme için; öbek dışına sızmaz).

---

## 3. Çekirdek mimari karar — yüzey-tabanlı parser kuralı (R8_redup emsali)

### 3.1 Mekanizma: parser içi yüzey-tabanlı yeniden-kurulum

R8_redup/R6_ki/R7_diye emsali. Parser bitişik tokenlerden m-ikilemeyi doğrudan yeniden kurar;
**birleşik (multi-token) `reduplication_m` analizini HİÇ kullanmaz** (R8'in birleşik ikileme
analizini kullanmaması gibi) → token:analiz arayüz uyuşmazlığını atlar.

### 3.2 Tespit — bitişik NOUN + m-reduplikant

Yeni kural **R9_mredup** (`_apply_r9_mredup`):
- İki bitişik yaprak `a`, `b` (ikisi de `LeafNode`).
- `a.tag in ("NOUN", "ADJ")` (taban gerçek isim VEYA sıfat).
- **Yüzey m-testi:** `m_reduplicate(_tr_lower(a.token)) == _tr_lower(a.token) + " " + _tr_lower(b.token)`.
  - `_tr_lower` İ/I güvenli (cümle-başı büyük harf: `Kitap Mitap` → küçültülüp test edilir).
  - `m_reduplicate` boş/m-başlı tabanda `ValueError` → `try/except` ile atla (recall-güvenli).
- Eşleşirse — taban etikete göre öbek: `a.tag=="NOUN"` → `PhraseNode.make("NP", (a, mred))`;
  `a.tag=="ADJ"` → `PhraseNode.make("AdjP", (a, mred))`. `mred = LeafNode("MRED", b.token, None)`.
  Taban `a` DEĞİŞMEZ (NOUN/ADJ, analizli). İ ilerleme +2.
- Eşleşmezse çıktıya `a`, ilerleme +1.

**Recall-güvenli belirsizlik [bilinçli]:** `adam madam` — `madam` gerçek sözcük (madame) ama
`m_reduplicate("adam")=="adam madam"` → m-ikileme kurulur (baskın okuma: "adamlar ve benzeri").
Ayrık "adam + madam" okuması nadir; V1 m-ikilemeyi tercih eder (doc philosophy: recall-güvenli).
İkinci token'ın `X` olma şartı KOYULMAZ (gerçek-sözcük reduplikantları da yakalanır).

### 3.3 Kural sırası

- **R9_mredup en önde, R8_redup'tan hemen sonra, R0/R3/R1'den ÖNCE.** Gerekçe: R1 `kitap`'ı tek
  başına NP'ye almadan / R3 AdjP kurmadan m-çiftini yakala.
- R8 (özdeş çift, `a==b`) ve R9 (m-çift, `a≠b`) **ayrık** — `kitap mitap` R8'i tetiklemez (özdeş
  değil), R9 yakalar. `yavaş yavaş` R9'u tetiklemez (m-test başarısız), R8 yakalar.
- **NP rolü BEDAVA:** R9 çıktısı `NP` PhraseNode → R1/R2/R5 onu nominal olarak zaten işler
  (`_tag(n)=="NP"`). Ayrı entegrasyon YOK. R5 `_node_is_nominative(NP)` → baş `kitap` yalın →
  nominatif → özne konumu (yapısal olarak `kitap aldı` ile TUTARLI; indefinite-nom-nesne yapısal
  belirsizliği pre-existing SOV sınırı, m-ikilemeye özgü değil).

---

## 4. Düğüm yapısı ve dependency

- `PhraseNode.make("NP"|"AdjP", (base_leaf, mred_leaf))` — `base_leaf` orijinal NOUN/ADJ (analizli),
  `mred_leaf = LeafNode("MRED", token2, None)`. Ek alan YOK.

**Dependency (`dependency.py`) — açık MRED işlemesi:**
1. `_find_head_leaf("NP"/"AdjP")` — **mantık DEĞİŞMEZ**: "en sağdaki NOUN/ADJ" zaten `base_leaf`'i
   bulur (`MRED ≠ NOUN/ADJ`, atlanır). Baş = taban. Fallback'e MRED-atlama guard eklenir (defansif).
2. `_child_deprel` **top-level** `if child_tag == "MRED": return "compound:redup"` (parent NP VEYA
   AdjP fark etmez; reduplikant → baş). Aksi halde MRED son `return "dep"`'e düşer.
3. **upos = taban(head) POS'undan MİRAS:** `to_conllu`/DepToken `upos = lf.tag` doğrudan → `MRED`
   GEÇERSİZ UD upos. Çözüm: MRED için `deps` head-bağından (`compound:redup` → base id) tabanı bul,
   `upos = base.tag` (NOUN taban→NOUN, ADJ taban→ADJ). Tek `MRED` etiketi iki taban POS'unu da kapsar.
   feats: `MRED` analizsiz → `_analysis_to_feats` erken `"_"` döner (çökme yok).
4. Dependency golden: `kitap mitap aldı` → baş `kitap` fiile `nsubj`; id2(mitap) MRED→NOUN, head=1,
   `compound:redup`; id3(aldı) root. `güzel müzel elbise` → id1(güzel) ADJ amod→3; id2(müzel) MRED→ADJ
   head=1 compound:redup; id3(elbise) NOUN root.

**NOT — R8(AdvP) `compound:redup` emsali:** ikinci token birinciye `compound:redup` ile bağlanır;
aynı UD ilişkisi burada nominal bağlamda kullanılır (tutarlı).

---

## 5. Kapsam dışı / bilinçli sınır

- **ADJ-taban m-ikileme** (`güzel müzel`) → AdjP (V2, kapsama ALINDI, §2).
- **`çocuk mocuk`** (çocuk→ADJ disambiguation quirk): V2'de ADJ-taban desteğiyle **AdjP** olarak
  tetiklenir (semantik olarak isim; çocuk→ADJ yanlış-etiketi disambiguation açığı, m-ikilemeye özgü
  değil). Başıboş X bırakmaz — kabul edilebilir; doğru NOUN-etiketi ayrı disambiguation işi.
- **Üç+ token** / araya sözcük (`kitap mitap kalem`) → R1 sonraki NOUN'u m-NP'ye modifikatör olarak
  ekleyebilir; nadir, V1 defer (bitişik ikili şart).
- **Gerçek-sözcük reduplikant belirsizliği** (`adam madam`) → recall-güvenli m-ikileme (§3.2).
- **Ayrık m-ikileme** / araya sözcük girmesi — kapsam dışı (bitişiklik şart).
- **p-ikileme** (`çer çöp` gibi lexik ikilemeler) — m-ikileme değil, kapsam dışı.

---

## 6. İş akışı (CLAUDE.md §2 DEĞİŞMEZ)

1. **SPEC/tasarım** — bu doküman (R9_mredup + NP temsili + MRED reduplikant + guard elle yazıldı).
2. **Golden** — `tests/golden_parse.py` + `tests/golden_dependency.py`'ye ek, motordan BAĞIMSIZ
   (elle-doğrulanmış dilbilgisinden): NOUN-m-ikileme NP (`kitap mitap aldı`), ünlü-başlı
   (`araba maraba aldı`), yüklemsiz (`kitap mitap` → NP kök), **dependency compound:redup** (CoNLL-U),
   regresyon (mevcut parse ağaçları + AdvP). upos AMPİRİK doğrulanır (motor olgusu).
3. **Motor** — `_apply_r9_mredup` + pipeline R8'den sonra + `dependency.py` `_child_deprel` MRED→
   compound:redup + upos MRED→NOUN eşleme. `_find_head_leaf` DEĞİŞMEZ.
4. **Hakem + doğrulama** — golden + korpus tarama (parse çökme yok) + mevcut E/AdvP testleri yeşil +
   tam paket regresyonsuz + adversarial hakem.

---

## 7. Değişmezler (test sonrası doğrulanacak)

- `kitap mitap aldı` → `S(NP(kitap mitap), VP(aldı))`; `mitap` başıboş X DEĞİL, NP içinde MRED.
- `araba maraba aldı` → `S(NP(araba maraba), VP(aldı))`.
- `kitap mitap` (yüklemsiz) → `NP` kök (X başıboş kalmaz).
- Dependency: m-NP başı (`kitap`) fiile `nsubj`; reduplikant (`mitap`) başa `compound:redup`,
  upos=NOUN.
- Mevcut parse ağaçları (E2/E3/E4 + AdvP testleri) DEĞİŞMEZ (R9 yalnız NOUN + m-test-eşleşen çift).
- m-ikileme olmayan bitişik NOUN çiftleri (`kitap kalem`) DEĞİŞMEZ (m-test başarısız).
- Yeni etiket/kural geriye uyumu kırmaz.
