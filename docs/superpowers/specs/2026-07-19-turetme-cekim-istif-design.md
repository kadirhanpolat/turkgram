# Türetilmiş gövde + çekim istifi ÇÖZÜMLEMESİ — Tasarım

**Tarih:** 2026-07-19
**Kapsam:** `analysis.py` (`_try_derivation_inflected` yeni pass)
**Statü:** SPEC (ana oturum) → bağımsız golden → motor → hakem
**Köken:** İstatistiksel eval OOV teşhisi — `bencilliği`/`evsizliğini`/`bencilliklerinden` NO-REAL.

## 1. Amaç ve gerçek açık

**Saf çok-katmanlı türetme ZATEN çalışıyor** (Faz A `_try_derivation_chain`):
`gözlükçülük`(gözlük→gözlükçü→lük), `evsizlik`(ev→evsiz→lik) ✓.

**Açık: türetilmiş gövde + ÇEKİM istifi.** Türetilmiş gövde (`bencillik`, leksikonda
lemma DEĞİL) durum/iyelik/çoğul alamıyor:
- `bencilliği` = bencillik + acc → NO-REAL
- `evsizliğini` = evsizlik + poss3sg + acc → NO-REAL
- `bencilliklerinden` = bencillik + pl + poss3sg + abl → NO-REAL

## 2. Feasibility (ampirik doğrulandı, 2026-07-19)

- `decline` türetilmiş gövdede sorunsuz: `decline("bencillik", case="acc")`=`bencilliği`,
  `decline("evsizlik", poss3sg, acc)`=`evsizliğini`, `decline("bencillik", pl, poss3sg, abl)`=`bencilliklerinden`.
- Ara türetilmiş gövde `_root_candidates(surface)`'te MEVCUT: `bencillik` ∈ candidates("bencilliği"),
  `evsizlik` ∈ candidates("evsizliğini"). → yeni kök-aday mantığı GEREKMEZ.

## 3. Algoritma (`_try_derivation_inflected`, A3 istifleme emsali)

FORWARD kompozisyon (analysis-by-generation):

```
for D in _root_candidates(surface):        # ara türetilmiş gövde adayı (bencillik)
    if D == surface: continue              # çekim yok → saf türetme (zaten kapsandı)
    # 1) D geçerli bir türetme (zinciri) mi? — mevcut pass'leri D üzerinde koştur
    sub = []
    _try_derivation_all(D, sub, seen_local, roots)
    _try_derivation_chain(D, sub, seen_local, roots, max_depth)
    if not sub: continue                   # D türetme değil → atla
    # 2) Çekim: decline(D, infl) == surface mı?
    for raw in _enumerate_decline(surface, D):
        canon = _canon_decline(raw)
        if not canon: continue             # nom-only (çekimsiz) → atla (D==surface değilse zaten var)
        if decline(D, **_raw_from_canon("decline", canon)) == surface:
            compose(best_sub, canon) → Analysis
```

Oracle çift: (a) türetme oracle (`derivations`), (b) decline oracle (`decline==surface`).
Precision inşa gereği (her iki oracle + roots §8.1).

## 4. Analysis temsili

Mevcut `kind="derivation"` GENİŞLETİLİR (yeni kind YOK):
- `lemma` = base kök (ben/ev) — DEĞİŞMEZ.
- `chain` = türetme katmanları (mevcut BFS çıktısı, DEĞİŞMEZ).
- `kwargs` = türetme meta (`suffix`, `src_pos`) + **çekim ekseni** (`case`/`possessive`/`number`,
  non-default olanlar; §4 genel kural nom/None/sg atılır).
- `pos` = türetilmiş POS (decline nominal → mevcut `_DERIVED_POS`).
- `segments` = türetme segmentleri + çekim dilimleri (DELEGASYON: `_segment_decline(D, canon)`
  çekim dilimlerini verir; türetme segmentleri `sub` chain'inden). Tam segment kompozisyonu:
  `[kök + türetme-ekleri...] + [çekim-ekleri...]`.

## 5. TUZAKLAR

- **Perf (hakem MEDIUM, ölçülen):** ~50 kök-aday × türetme-BFS × decline-enum → iç içe.
  `_strip_one_layer`/`_strip_derivation`/`_template_to_allomorphs` lru_cache'li (98→66ms/çağrı
  distinct sözcük; warm ~17ms). **Gerçek maliyet depth=5'te ~100-120ms/çağrı** ve türetme
  İÇERMEYEN düz isimlerde de ödenir (gate yalnız roots+depth>=2, sözcüğün türetilebilirliğine
  bakmaz). **GATE: `max_derivation_depth>=2`** (default depth=1 ETKİLENMEZ — saf çok-katman
  türetme de depth>=2 ister; opt-in). Kabul: opt-in, cache-amortize, analiz hot-path değil.
  İleride ucuz ön-filtre (çekim-eki markerı) opsiyonel. NOT: tam-leksikon analyze zaten
  ~165ms (`_try_adj_all` O(roots), pre-existing) — bu feature'a özgü değil.
- **Belirsizlik/dedup:** `seen` anahtarı `("derivation_infl", surface, base_lemma, chain_key, infl_key)`;
  mevcut derivation seen ile çakışmaz.
- **Saf türetme çift-üretimi:** `D==surface` (çekimsiz) atlanır → mevcut `_try_derivation_*` tek üretir.
- **precision roots-garantili** (§8.1): roots yoksa hypothetical (base ∉ roots kontrolü sub-pass'te).
- **`_root_candidates` düşen-ünlü sınırı** pre-existing (`naklınki` emsali) — bu feature'a özgü değil.

## 6. Test planı

**Bağımsız golden (Opus, motor-körü):**
- `bencilliği`(ben, chain ben→bencil→bencillik, case=acc)
- `evsizliğini`(ev, ev→evsiz→evsizlik, poss3sg+acc)
- `bencilliklerinden`(ben, …, number=pl+poss3sg+abl)
- `gözlükçülüğü`(göz? → gözlük→gözlükçü→gözlükçülük, acc)
- `sporcuların`(spor→sporcu, pl+gen) — tek türetme katmanı + çekim
- Regresyon: `bencillik`/`evsizlik` (çekimsiz saf türetme DEĞİŞMEZ, tek analiz)
- Negatif: `evler` (saf çekim, türetme yok → derivation_infl ÜRETMEZ)

**Hakem:** korpus sweep (leksikon lemma → türet → çek → round-trip, 0 çökme); tam paket
regresyonsuz; adversarial (çift-üretim, precision, perf, yanlış-pozitif).

## 7. Kapsam dışı (V1)

Fiil-türevli çekim (fiilimsi zaten ayrı), çatı+türetme, `_root_candidates` düşen-ünlü.
