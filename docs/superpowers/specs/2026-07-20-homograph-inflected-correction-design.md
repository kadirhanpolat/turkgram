# SPEC/Tasarım — Homograf disambiguation: çekimli-üstünlük düzeltmesi

Tarih: 2026-07-20. Ana oturum. Referans: `disambiguation-spec.md` (§1 sıralama önceliği).
Öncül bulgu: cümle katmanı (öge + yargı bölme) `topu`/`verdi` homograflarında yanlış.

---

## 1. Sorun

`disambiguation.rank` freq'siz çağrıldığında (cümle katmanı `_best_per_token` böyle yapar),
sıralama anahtarı `(-freq, -pos_tutarlılık, -kind_önceliği, len(segments), _sort_key)` →
freq=0 olunca **morfem-ekonomisi** (`len(segments)`) belirleyici olur: **az segmentli bare
lemma** çok segmentli çekimli okumayı yener. Sonuç:

- `topu` → `decline('topu')` [bare pron, 0 ek] kazanır; doğru okuma `top`+acc (belirtili
  nesne) kaybeder. `Çocuk topu bahçede oynadı` → topu belirtisiz nesne (yanlış).
- `verdi` → `decline('verdi')` [bare noun] kazanır; doğru okuma `vermek` past (yüklem)
  kaybeder. `Ali kitabı aldı Veli defteri verdi` → verdi yüklem sanılmaz → yargı
  under-segment + öge yanlış.

**Ama** freq'i topluca eklemek RİSKLİ: `yüz`/`var`/`kar`/`yaz` gibi **bare-vs-bare** homograflar
(hem isim hem fiil-emir 0-ekli) yanlış tarafa devrilir; `dolu`→`do` (rakip **derivation**
lemması yüksek freq) bozulur. Yani ham freq çözüm değil.

## 2. Çözüm — çekimli-üstünlük düzeltmesi (opt-in, prensipli)

**Kural:** en-iyi aday bir **bare decline** (kind=decline, kwargs BOŞ = case/possessive/number
yok) ise VE **çok daha sık** bir lemmanın **DAR çekimli** okuması varsa → çekimliyi tercih et.

**DAR rakip** (`_is_infl_competitor`) — YALNIZ net-çekimli fiil (imperatif/aorist/gen/poss
HARİÇ, isim-homograf tuzağı yazar/yarın):
- `conjugate` + tense ∈ {past, evid, pres, fut} + voice_chain YOK (-di/-miş/-iyor/-ecek
  ayırt edici son ekler; gerçek adla nadir çakışır → güvenilir).

**HAKEM HIGH (2026-07-20) — acc-isim dalı ÇIKARILDI:** İlk tasarım `decline case=='acc'`
rakibini de içeriyordu (topu→top:acc için). Adversarial geniş tarama (top-2000 ad × sentence)
gösterdi ki bu **sistematik yanlış-flip** üretiyor: `-CI` sonlu gerçek adlar/sıfatlar
(yarı→yar:acc, arı→ar:acc, salı, koyu, sıkı, dişi, testi, tipi, çalı, katı, birileri, diğeri)
kısa-stem freq'i yüksek olduğu için haksız deviriliyordu (`Arı bal yapar`→Arı belirtili nesne).
`topu`(gerçek pron) ile `yarı`(gerçek noun) POS'la AYRILAMIYOR (ikisi de gerçek lemma) →
acc-dalı geri-dönüşsüz güvensiz. **Çıkarıldı.** Kayıp: `topu`→top:acc artık YOK (Çocuk topu →
belirtisiz, golden 1 skip). Korunan yüksek-değer: `verdi/girdi/çıktı`→fiil (leksikon-çöpü
ad→net-fiil past; segmentasyon + yüklem tespiti düzelir).

```
en_iyi = rank(analyses)[0]                          # freq'siz + pos'suz dilbilimsel (eski base)
if en_iyi.kind == 'decline' and not en_iyi.kwargs:  # yalnız BARE decline
    bf = freq[en_iyi.lemma]  (yoksa 0)
    eşik = max(bf * RATIO, FLOOR)                    # RATIO=2.0, FLOOR=1000
    adaylar = [a for a in geri kalan
               if _is_infl_competitor(a)                     # DAR: net fiil / acc-isim
               and len(a.segments) > len(en_iyi.segments)   # DAHA çekimli
               and freq[a.lemma] >= eşik]                    # ÇOK daha sık
    if adaylar: en_iyi = en-sık-çekimli(adaylar)
```

**Neden temiz (test + adversarial-doğrulandı):**
- `verdi`→`vermek:past` ✓, `girdi`→`girmek:past` ✓, `çıktı`→`çıkmak:past` ✓ (leksikon-çöpü ad → net-fiil).
- `yüz`/`var`/`kar`/`yaz`/`gül` DOKUNULMAZ — en-iyi zaten `conjugate:imp` (bare-decline DEĞİL).
- `dolu` DOKUNULMAZ — rakip `derivation:do` DAR-rakip DEĞİL.
- `Yarın`(tomorrow) DOKUNULMAZ — rakip `yarmak:imp`(imperatif) DAR-dışı.
- `yazar`(writer) DOKUNULMAZ — rakip `yazmak:aorist` DAR-dışı (aorist isim-homograf tuzağı).
- `topu`/`yarı`/`arı`/`salı`/`koyu`/`sıkı`/`dişi`/`birileri` DOKUNULMAZ (acc-dalı çıkarıldı; gerçek ad/sıfat/pron).
- `kitabı`/`geldi`/`defteri`/`evi`/`sıra`/`sabah` DOKUNULMAZ (rakip bare yok / en-iyi bare değil).
- **base FREQ'SİZ + POS'SUZ** (eski `_rank(real)` ile birebir) → 44 cümle golden `elements`
  DEĞİŞMEZ; freq YALNIZ DAR düzeltmede.

## 3. Arayüz (DEĞİŞMEZ default)

`disambiguation.rank(analyses, *, freq=None, pos=None, prefer_inflected=False)` — **yeni
`prefer_inflected` param, default False → mevcut davranış BİREBİR** (tüm golden_disambiguation
/ statistical / context testleri DOKUNULMAZ). `prefer_inflected=True` + `freq` verilince §2
düzeltmesi son-adım olarak uygulanır (yalnız en-iyi'yi öne alır; gerisi sıra korur).

**Cümle katmanı** (`sentence.py::_best_per_token`): freq (`lexicon.load_freq()`) + pos
(`lexicon.pos_map()`) + `prefer_inflected=True` ile çağırır. Böylece `Çocuk topu…` →
belirtili nesne + `…verdi` → yüklem/yargı bölme düzelir. `analyze`/`rank` default DOKUNULMAZ.

## 4. Kapsam DIŞI

- Bare-vs-bare homograf (yüz=isim/fiil-emir) — izole çözülemez (bağlam gerekir; K-kuralları
  ayrı iş). Kural bilinçli olarak yalnız bare-decline-vs-çekimli asimetrisini hedefler.
- `topu` = 'topu' nom lemma zaten çekimli rakip `top:acc` ile çözülür; leksikon-prune YOK
  (spurious lemma silinmez, sıralama düzeltilir → geri-dönüşsüz veri kaybı yok).
- Genel lemmatizer/analyze tüketicileri opt-in (isterlerse `prefer_inflected=True` geçer).

## 5. Test planı

- `tests/test_homograph_correction.py` — bare-vs-çekimli (topu/verdi flip) + değişmeyenler
  (yüz/var/dolu/kar/kitabı) + default-unchanged kanıtı (`prefer_inflected=False` == eski).
- Cümle: clause golden `Ali kitabı aldı Veli defteri verdi` → 2 yargı (verdi verb-flip).
  `Çocuk topu bahçede oynadı` golden skip KALIR (topu acc-dalı çıkarıldı → belirtisiz).
- Regresyon: tam paket + `golden_disambiguation` DEĞİŞMEZ. Sweep 0 çökme.
- Hakem: adversarial — yanlış flip (bare-vs-bare devrilme), default davranış ihlali.

## 6. Dosyalar

- `turkgram/disambiguation.py` — `_PLAIN_KINDS`, `_INFL_RATIO`/`_INFL_FLOOR`,
  `_inflected_correction`, `rank(prefer_inflected=)`.
- `turkgram/sentence.py` — `_best_per_token` freq+pos+prefer_inflected.
- `tests/test_homograph_correction.py` + cümle/clause golden güncellemesi.
- Bu doküman.
