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

**YALNIZ NOUN-tabanlı m-ikileme → NP:**
- `kitap mitap` ("kitaplar ve benzeri"), `araba maraba`, `para mara` → tek **`NP`** öbeği.
- Baş = ilk token (gerçek isim); m-parçası (ikinci token) reduplikant.

**Kapsam DIŞI (defer):**
- **ADJ/başka tabanlı m-ikileme** (`güzel müzel`, `yeşil meşil`) — sıfat m-ikilemesi. V1 yalnız
  NOUN taban (nesne/özne rolü net). Baş-bulma NP mantığı NOUN arar → ADJ taban baş-belirsizliği
  yaratır. Defer.
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
- `a.tag == "NOUN"` (taban gerçek isim; V1 scope).
- **Yüzey m-testi:** `m_reduplicate(_tr_lower(a.token)) == _tr_lower(a.token) + " " + _tr_lower(b.token)`.
  - `_tr_lower` İ/I güvenli (cümle-başı büyük harf: `Kitap Mitap` → küçültülüp test edilir).
  - `m_reduplicate` boş/m-başlı tabanda `ValueError` → `try/except` ile atla (recall-güvenli).
- Eşleşirse: `PhraseNode.make("NP", (a, mred_leaf))` — `mred_leaf = LeafNode("MRED", b.token, None)`.
  Taban `a` DEĞİŞMEZ (NOUN, analizli). İ ilerleme +2.
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

- `PhraseNode.make("NP", (base_leaf, mred_leaf))` — `base_leaf` orijinal NOUN (analizli),
  `mred_leaf = LeafNode("MRED", token2, None)`. Ek alan YOK.

**Dependency (`dependency.py`) — açık MRED işlemesi:**
1. `_find_head_leaf("NP")` — **DEĞİŞMEZ**: mevcut "en sağdaki NOUN" mantığı zaten `base_leaf`'i
   bulur (`MRED ≠ NOUN`, atlanır). Baş = taban isim. ✓
2. `_child_deprel` NP dalına: `if child_tag == "MRED": return "compound:redup"` (reduplikant → baş,
   UD nominal reduplikasyon ilişkisi). Aksi halde MRED son `return "dep"`'e düşer.
3. **upos eşleme:** `to_conllu`/DepToken `upos = lf.tag` doğrudan → `MRED` GEÇERSİZ UD upos.
   `upos = "NOUN" if lf.tag == "MRED" else lf.tag` (kullanıcı kararı: reduplikant NOUN, baş isimle
   aynı; UD nominal-compound geleneği). feats: `MRED` analizsiz (`analysis=None`) → `_analysis_to_feats`
   NOUN+case=None dalını verir (impl'de doğrulanır; çökme yok).
4. Dependency golden: `kitap mitap aldı` → id1(kitap) NOUN head=3? HAYIR — `kitap mitap` özne-NP,
   baş `kitap` fiile `nsubj`; id2(mitap) MRED→NOUN, head=1(kitap), `compound:redup`; id3(aldı) root.

**NOT — R8(AdvP) `compound:redup` emsali:** ikinci token birinciye `compound:redup` ile bağlanır;
aynı UD ilişkisi burada nominal bağlamda kullanılır (tutarlı).

---

## 5. Kapsam dışı / bilinçli sınır

- **ADJ/başka tabanlı m-ikileme** (`güzel müzel`) → defer (§2).
- **`çocuk mocuk`** (çocuk→ADJ disambiguation quirk) → NOUN-guard'la tetiklenmez, defer (§2).
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
