# SPEC/Tasarım — Bağlam-tabanlı acc-nesne homografı (K6)

Tarih: 2026-07-20. Ana oturum. Referans: `spec/sentence-disambiguation-spec.md` (K1-K5).
Öncül: izole homograf çekimli-üstünlük düzeltmesinde (2026-07-20) acc-dalı ÇIKARILMIŞTI —
`-CI` gerçek adları (yarı/arı) bozuyordu; `topu`(top:acc) ile `yarı`(half) izole ayırt
edilemez. **Karar: bağlam gerekir** (kullanıcı). Bu, context.py'ye K6 ekler.

---

## 1. Problem

`topu` izolede `decline(topu, bare pron)` ranklanır (morfem-ekonomisi); ama nesne konumunda
(`Çocuk topu bahçede oynadı`) doğru okuma `decline(top, acc)` (belirtili nesne). İzole freq/
morfem ayıramaz (`topu` gerçek quantifier-pron lemma; acc-dalı `yarı`/`arı`/`birileri`'yi bozar).

**Neden CURATED set:** `birileri`(bare pron "someone" DOĞRU), `kimi`(bağlam: quantifier vs
kim+acc), `hepsi`/`çoğu`(rakipsiz) — genel "object→acc" kuralı bunları bozar. Yalnız acc'nin
BASKIN olduğu homograflar (top→topu) curated kümede.

## 2. K6 kuralı (context.py)

**`_ACC_OBJECT_PRON`** kapalı-set (curated, genişletilebilir): bare-quantifier-pron ama acc
okuması nesne konumunda BASKIN. V1: `{"topu"}` (top:acc). Yeni doğrulanmış vaka → sete eklenir.

**`_k6(a, i, tokens, analyses, freq, pos) → int`:**
- token `_tr_lower(tokens[i])` sette değilse → 0 (etkisiz).
- aday nominal değilse → 0.
- **Nesne bağlamı** koşulu: cümlede finit fiil VAR (herhangi j≠i, izole-top kind∈_VERB_KINDS)
  VE i'den ÖNCE bir nominal (özne adayı; izole-top kind∈_NOMINAL_KINDS) VAR. Aksi → 0 (nesne
  bağlamı yok → `Topu geldi` tek-nominal → dokunma).
- Koşul sağlanırsa: `_case_of(a)=="acc"` → **+_W_K6**; `=="nom"` → **-_W_K6**; diğer → 0.

**Recall-güvenli:** kanıt (int) ekler, aday BUDAMAZ; kural ateşlemezse izole `_rank_key`'e düşer.
`_RULES`'a eklenir → `rank_in_context` (ve tüketicileri: lemmatize_text) K6'yı alır.

## 3. sentence.py wiring (contained)

sentence.py `_best_per_token` izole `_rank` kullanıyor (44 golden'a bağlı). K6'yı YALNIZ
`_ACC_OBJECT_PRON` tokenlarına uygula → 44 golden ETKİLENMEZ (bu kelimeleri içermez). Diğer
tokenlar izole `prefer_inflected` (aynen). Homograf tokenda: `context.context_evidence` ile
cümle-bağlamı yeniden sıralama. `pos_map` + real-analiz-listesi `_best_per_token`'a geçer.

**Sonuç:** `Çocuk topu bahçede oynadı` → topu=top:acc → **belirtili nesne** (golden skip kalkar).

**TUZAK — freqless tiebreak sentence.py-LOCAL (hakem MEDIUM):** sentence.py wiring `_rank_key(a, None,
None)` (freqless) kullanır → `Topu geldi` bare kalır. Ama `rank_in_context(freq=…)` geçen DİĞER tüketiciler
(lemmatize_text) izole freq-sırasıyla topu→top:acc çözer (freq(top)>freq(topu)), K6 ateşlemese de. Bu
K6 regresyonu DEĞİL (pre-existing izole freq); K6 koruması yalnız sentence.py tüketicisinde geçerli.
lemmatize davranışı bu değişiklikle DEĞİŞMEZ (zaten öyleydi).

## 4. Kapsam DIŞI

- Geçişlilik (valence) sözlüğü YOK → `Topu geldi`(intransitive, topu=özne olabilir) vs `Topu ver`
  (transitive, topu=nesne, ama önünde nominal yok → K6 ateşlemez) ayrımı yaklaşık. Önceki-nominal
  heuristiği `Çocuk topu`'yu çözer; sentence-initial nesne (`Topu ver`) V1 kapsam dışı.
- `birileri`/`kimi` gibi bağlam-bağımlı ama bare-baskın homograflar → sette YOK (bilinçli).
- Genel object-detection (tam sözdizim) → defer.

## 5. Test planı

- **context golden** (`tests/test_context.py` varsa; yoksa yeni): `rank_in_context(["Çocuk","topu",
  "bahçede","oynadı"])` → topu top:acc üstte; `["Topu","geldi"]` → dokunma (önceki-nominal yok);
  negatif `["birileri","geldi"]` → bare korunur (sette değil).
- **sentence:** `Çocuk topu bahçede oynadı` → belirtili nesne; `test_sentence` skip kalkar.
- **Regresyon:** 44 cümle golden + K1-K5 golden DEĞİŞMEZ (K6 yalnız curated set). Tam paket.
- **Hakem:** adversarial — yanlış flip (birileri/yarı benzeri), object-bağlam koşulu, recall.

## 6. Dosyalar

- `turkgram/context.py` — `_ACC_OBJECT_PRON`, `_k6`, `_W_K6`, `_RULES`+=k6.
- `turkgram/sentence.py` — `_best_per_token` homograf-token context re-rank.
- `tests/test_context_k6.py` (+ `test_sentence` skip kalkar).
- Bu doküman.
