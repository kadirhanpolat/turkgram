# SPEC/Tasarım — Aktarma sağlamlaştırma (V5.1): koordine-içi gömme + homograf-finit + tırnak

Tarih: 2026-07-20. Ana oturum. Öncül: V5 gerçek gömme (`2026-07-20-clause-segmentation-design.md
§5c`). V5 üç best-effort sınır bırakmıştı; bu doküman üçünü de kapatır.

---

## 1. Sınır 1 — koordine-içi gömme + koordinasyon ayrımı

V5 aktarma pass'i önceki (koordinat-bağlanmamış) yargıları yan işaretliyordu → `Ali koştu ve
Veli geldi dedi` yan/bağımsız KARIŞIK. Ayrıca aktarma koşulu "ÖNCESİNDE herhangi finit tümce"
idi → `Ali geldi ve Veli dedi` (koordinasyon) yanlış gömme.

**Fix (iki parça):**
1. **Aktarma koşulu: reporting fiilinden HEMEN önceki token FİİL** (FIIL/ULAC/ORTAC) — gömülü
   tümcenin yüklemi. Bu, koordinasyonu ayırır: `Ali koştu ve Veli **geldi** dedi` (geldi=fiil →
   gömme) vs `Ali geldi ve Veli **dedi**` (Veli=ad, dedi'nin öznesi → koordinasyon, gömme yok).
2. **Gömme pass'i: reporting yargısı KOORDİNAT-bağlı DEĞİLSE → TÜM önceki yargı yan** (koordine
   dahil): `Ali koştu ve Veli geldi dedi` → yan(Ali koştu) + yan(Veli geldi, connector=ve) +
   temel(dedi). Reporting yargısı connector∈_COORD_CONJ ise (`… ve Veli dedi`) → koordinasyon, atla.

## 2. Sınır 2 — homograf-finit gömülü yüklem

`geleceğim` = `gelecek+iyelik` (AD, "geleceğim"="my future") ranklanır AMA `gel+ecek` (fiil,
fut, 1sg) okuması VAR (adaylarda). Reporting öncesi bu AD → gömülü yüklem tanınmaz.

**Fix (analyze_sentence, pred_i sonrası):** ana yüklem reporting fiili + HEMEN önceki token
**nom (case=None)** + **net fiil zamanı** (`verb_reading.tense∈{past,evid,pres,fut}`) verb_reading'i
varsa → o token'ı FİİL'e yeniden sınıfla → aktarma (§1) ateşler, gömülü yüklem olur.
`Yarın geleceğim dedi` → yan(Yarın=zarf tümleci, geleceğim=yüklem) + temel(dedi).

**TUZAK — guard'lar (regresyon):** (a) **case=None ŞART** — dat/loc/abl (`Sana söyledim`,
Sana=oblique arg, sanmak verb_reading'i VAR ama dat) DIŞLANIR; (b) **acc DIŞLANIR** (`Yolu sordu`,
Yolu=nesne); (c) **net zaman ŞART** — imperatif/aorist (`Yaz söyledi`, yaz=yazmak imp) yeniden-
sınıflanmaz (isim/homograf tuzağı). NOT: `Yaz`/`Gel` zaten izole FİİL(imp) ranklanırsa aktarma
onları gömer (imperatif+reporting = alıntı komut, `Gel dedi` emsali) — bu tutarlı, yeniden-sınıflama
DEĞİL.

## 3. Sınır 3 — tırnak aktarma

`"Gel" dedi` → tokenize `['"','Gel','"','dedi']`. Tırnak öge değil + gömme sinyali.

**Fix (analyze_sentence, en başta):** ASCII çift-tırnak `"` (`_QUOTES`) tokenlarını SIYIR
(apostrof `'` HARİÇ — Ali'nin eki). `"Gel" dedi` → `Gel dedi` → aktarma (§1) gömer → yan(Gel) +
temel(dedi). Sıyırma `_best_per_token` pair'lerine hizalı (aynı `keep` indeksi). **Index sıyrılmış
içerik-akışa göre yeniden numaralanır** (tırnak token değil). `"Eve gel" dedi` → yan(Eve, gel)@1-2
+ temel(dedi)@3.

**TUZAK — YALNIZ ASCII `"` (hakem MEDIUM):** dar tokenizer yalnız ASCII `"`'yı ayrı token'a
böler; kıvrık (" ") / guillemet (« ») sözcüğe BİTİŞİK kalır → sıyrılamaz (`_QUOTES` yalnız
`{'"'}`). Kıvrık/guillemet desteği = tokenizer değişikliği (mimari-kararlar dar-kısıt) → V1 dışı.

## 4. Kapsam DIŞI (kalan)

- İç-içe çok-düzey gömme (gömülü tümce içinde gömülü tümce) — en-iyi-çaba.
- Tırnak-içi çok-cümle / karışık noktalama — V1 yalnız çift-tırnak sıyırma.
- Homograf-finit yalnız nom + net-zaman verb_reading; ptype/participle homografı defer.

## 5. Test planı

- **Golden** (`tests/golden_clause_v5b.py`, elle-doğrulanmış): 3 fix + 2 guard (Sana dat / Yolu acc)
  + 1 koordinasyon-ayrımı. **Regresyon:** V3/V4/V5 golden + 44 cümle + K6 + `test_sentence` DEĞİŞMEZ.
- **Sweep:** `sweep_clause.py`'ye aktarma-robustlik cümleleri; 0 çökme.
- **Hakem:** adversarial — koordinasyon/gömme ayrımı, homograf-finit yanlış-pozitif (Sana/Yaz/Ali),
  tırnak index kayması, guard'lar.

## 6. Dosyalar

- `turkgram/sentence.py` — aktarma koşulu (HEMEN-önce-fiil) + gömme pass (koordine dahil) +
  homograf-finit reclassify + `_QUOTES` sıyırma.
- `tests/golden_clause_v5b.py` + `tests/test_clause_v5b.py`.
- Bu doküman.
