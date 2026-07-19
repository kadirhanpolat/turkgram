# `-ki` aitlik eki ÇÖZÜMLEMESİ — Tasarım

**Tarih:** 2026-07-19
**Kapsam:** `analysis.py` + `analysis_candidates.py` (yeni kind `with_ki`)
**Statü:** SPEC (ana oturum) → bağımsız golden → motor → hakem
**Köken:** İstatistiksel eval OOV teşhisi — `evdeki`/`masadaki`/`içindeki` NO-REAL (küçük-harf OOV'nin bir dilimi).

## 1. Amaç

Üretim VAR (`morphology_noun.with_ki`), çözümleme YOK. Faz 2b "motor-dışı biçimlerin
çözümlemesi" deseni (casina/ken emsali): motor üretir, analizör tersine çözmez → ekle.

- `evdeki` → (ev, with_ki, {case: loc})
- `benimki` → (ben, with_ki, {case: gen})
- `bugünkü`/`dünkü` → (bugün/dün, with_ki, {case: loc}) — Kİ_ROUND -kü istisnası
- `içindeki` → (iç, with_ki, {case: loc, possessive: 3sg})

## 2. Üretim (mevcut, DEĞİŞMEZ)

`with_ki(headword, case="loc", **core)`:
- `base = decline(headword, case=case, **core)`, dön `base + "ki"`.
- **Kİ_ROUND istisnası** (`{bugün, dün, gün, öbür}`): `prefix + root + "k" + high_vowel(root)`
  (loc/gen atlanır) → `bugünkü`.

## 3. Çözümleme (yeni)

### 3.1 Yeni kind `with_ki`

`_KINDS`'a eklenir (isim grubu; casina/ken emsali). `pos="noun"`.

### 3.2 Enumerate (`_enumerate_ki`, candidates.py)

**Marker filtresi (recall-güvenli):** yüzey `k[ıiuü]$` ile bitmeli (ki/kı/ku/kü —
loc/gen -ki + Kİ_ROUND -kü). Marker yoksa hiç enumerate etme.

Hipotezler: `case ∈ {loc, gen}` × `possessive ∈ {None, 3sg}` = 4 hipotez.
(possessive 3sg → `içindeki`; V1 yalnız 3sg — diğer iyelikler + çoğul defer.)

Oracle (`with_ki(lemma, case=…, possessive=…)==surface`) doğrular → precision inşa gereği.
Kök adayı mevcut `_root_candidates` (önek + ters-mutasyon) üretir; yeni kök mantığı GEREKMEZ.

### 3.3 Delegasyonlu segmentasyon (`_segment_with_ki`, casina §6g emsali)

`base_form = decline(lemma, case=case, **core)` (Kİ_ROUND'da `with_ki` çıktısından türet);
`base_segs = _segment_decline(...)`; üstüne tek `(surface[len(base_form):], "ki")` dilimi.
Kİ_ROUND'da base decline'a eşlenmez → güvenli geri-düşüş `(surface, "KÖK")` kabul edilir
(pedagoji ikincil; round-trip iddiası yok, casina emsali).

### 3.4 Kanon (`_canon_ki`)

`case` daima; `possessive` yalnız None-dışı tutulur (nom/None atılır — §4 genel kural).

### 3.5 Wiring

`_KIND_FUNCS["with_ki"]=with_ki`; `_call_generator` dalı
(`case=kwargs.pop("case","loc"); return fn(lemma, case=case, **kwargs)`);
`_ENUMERATE_FN["with_ki"]`; `_canonicalize`/`_raw_from_canon` dalları; `_try_noun` kind
listesine `"with_ki"` (SONA — decline/copula sonrası); `_segment` dispatch.

## 4. TUZAKLAR

- **Belirsizlik bilinçli:** `benimki` hem with_ki (ben+gen+ki) hem çıplak decline
  (leksikonda "benimki" yoksa çözülmez; roots'a bağlı). `sonraki` = sonra+ki (with_ki
  gen? sonra ünsüz-final değil…) — oracle neyi üretiyorsa o çözülür.
- **precision roots-garantili** (§8.1): `roots` verilmezse hypothetical gürültü.
- **Stacked -ki DEFER (V2):** `dakileri` (ki+ler+i), `evdekinin` (ki+gen) — ki-gövdesinin
  yeniden çekimi (A3 istifleme emsali); V1 yalnız base with_ki.
- **_root_candidates sınırı:** disharmonic/düşen-ünlü kökler (pre-existing) with_ki'de de kaçar.

## 5. Test planı

**Bağımsız golden (Opus, motor-körü):** evdeki/masadaki/kapıdaki (loc), benimki/seninki (gen),
bugünkü/dünkü (Kİ_ROUND), içindeki (poss3sg). Belirsizlik: sonraki. Negatif: "kirli"
(k[ıiuü]$ değil → with_ki YOK). ~12-16 giriş.

**Hakem:** korpus sweep (leksikon isimleri × loc/gen → with_ki round-trip, 0 çökme);
tam paket regresyonsuz; adversarial (marker/enumerate/delegasyon).

## 6. Kapsam dışı (V1)

Stacked -ki (dakileri/evdekinin), possessive≠3sg + çoğul with_ki, `_root_candidates`
pre-existing sınırları.
