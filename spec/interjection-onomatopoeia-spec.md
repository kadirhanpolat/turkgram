# SPEC — Ünlem (interjection) + Yansıma (onomatope) tanıma

Referans: Korkmaz *Türkiye Türkçesi Grameri — Şekil Bilgisi* (ünlemler ve yansıma
sözcükler bölümü); Ergin *Türk Dil Bilgisi*. Yalnız KURAL + § referansı; düzyazı/örnek
kopyalanmaz (CLAUDE.md §3). Wikipedia "Türkçe dilbilgisi" navbox: *Ünlem* başlığı.

## 1. Amaç ve kapsam

turkgram şu an ünlem (ah, of, eyvah, haydi) ve yansıma (şır, çat, güm) sözcükleri
tanımıyor — hepsi `analyze()` gürültü modunda hypothetical fiil/isim'e düşüyor
(`_POS`'ta `ünlem`/`yansıma` yok). Bu SPEC iki **kapalı sözcük sınıfını** `analyze()`'a
**tanıma (recognition)** olarak ekler.

**Desen:** `_try_conjunction_all` / `_try_postposition_all`'un birebir aynası —
kapalı-liste, oracle-DIŞI, **additive** (aday budamaz, mevcut analizlerin YANINA ekler),
her zaman döner (roots-bağımsız), `hypothetical=False`.

**Neden closed-set + additive:** Bu iki sınıf çekim/türetme almaz (asıl ünlemler ve asıl
yansımalar donmuş biçimlerdir) → üreteç oracle'ı YOK. Bağlaç/edat emsali: kapalı küme
üyeliği tek sinyal. Additive olduğu için recall-güvenli (yanlış budayamaz); belirsizlik
kendiliğinden oluşur (aşağıda §4) ve disambiguation sıralar.

### 1.1 Kapsam DIŞI (V1 — bilinçli sınır)

- **Ünlem türetmesi:** ah→ahlamak, of→oflamak, ünlem→ünlemek (ünlem→fiil `-lA-`).
  Ayrı yapım-eki alt-sistemi; leksikonda yansıma/ünlem tabanı yok → ertelendi.
- **Yansıma türetmesi:** -TI (şırıl→şırıltı, gür→gürültü), -dA- (şırıl→şırıldamak),
  -kIr- (fış→fışkır-). Düzensiz tabanlı (taban çoğu kez ikileme gövdesi: şırıl/gümbür,
  çıplak şır/güm değil) + leksikon-dışı → ertelendi. `derivation.py` -IntI (fiil→isim,
  akıntı) BUNDAN AYRI, karıştırma.
- **Üretim (generation):** bu sınıflar donmuş → üretilecek bir şey yok. Yalnız tanıma.
  TR API'ye üretim sarmalayıcısı EKLENMEZ (bağlaç `bağla` gibi bir muadili yok).

## 2. Ünlem (interjection)

### 2.1 Envanter — `interjection.INTERJECTIONS` (asıl ünlemler, kapalı küme)

Korkmaz'ın "asıl ünlemler" sınıfı temel alınır (türemiş/ünlem-değeri-kazanmış adlar
DIŞLANIR — onlar zaten isim olarak çözülür). Duygu, seslenme, gösterme, buyurma/teşvik,
onay alt-öbekleri:

```
ah, of, öf, üf, oh, vah, vay, ay, ey, hay, eyvah, aman, eyvallah,
hah, hıh, ıh, oho, hoppala, pöh, tüh, yazık,
hey, hişt, pist, bre, be, yahu,
işte, na,
haydi, hadi, haydin, marş, deh, hoşt, kışt, çüş,
bravo, aferin, yaşa, maşallah, inşallah,
```

Normalizasyon: `analyze()` girişte `_tr_lower` uygular (İ→i, I→ı) → küme küçük harf tutar.

### 2.2 Analiz çıktısı

```
Analysis(lemma=<yüzey>, pos="ünlem", kind="interjection", kwargs={},
         segments=[(yüzey, "kök")], hypothetical=False)
```

`_POS` += `"ünlem"`; `_KINDS` += `"interjection"` (SONA — çekim/türetme önceliklenir).

## 3. Yansıma (onomatope)

### 3.1 Envanter — `onomatopoeia.ONOMATOPOEIA` (asıl yansımalar, kapalı küme)

Ses/hareket taklidi çıplak yansımalar (Korkmaz). Açık-uçlu bir sınıf; küratörlenmiş
yaygın çekirdek (betimleyici değer; tamlık iddiası YOK — ünlem gibi):

```
şır, şar, fır, vır, vız, cız, cız, fış, hış, pır, gür, hır, zır,
çat, pat, küt, güm, tık, tak, tik, çıt, gıcır, gümbür, şırıl, patır,
hav, miyav, me, mö, vak, cik, gak, üf,
```

### 3.2 Analiz çıktısı

```
Analysis(lemma=<yüzey>, pos="yansıma", kind="onomatopoeia", kwargs={},
         segments=[(yüzey, "kök")], hypothetical=False)
```

`_POS` += `"yansıma"`; `_KINDS` += `"onomatopoeia"` (SONA).

## 4. Belirsizlik (bilinçli, recall-güvenli)

Additive olduğu için homograflar birden çok analiz verir; disambiguation sıralar:

- `of` = ünlem + `ofmak` imp-2sg (hypothetical) + `of` çıplak isim.
- `ay` = ünlem + `ay` isim (gökcisim/zaman).
- `çat` = yansıma + `çatmak` imp-2sg.
- `güm` = yansıma + (leksikon açığı).
- `işte` = ünlem + `iş` loc (`işte` = iş+te). İkisi de geçerli, bağlam ayırır.

`INTERJECTIONS` ve `ONOMATOPOEIA` kümeleri **ayrık** (kesişim boş) — bir yüzey iki
sınıftan yalnız birinde olur (drift-lock testi kesişimin boş kaldığını sabitler).

**Homograf sıralaması:** `interjection`/`onomatopoeia` `disambiguation._KIND_PRIOR`'da
YOK → öncelik 0 (edat/bağlaç emsali) → çekim/isim okuması tepede kalır. Drift-lock testi
mevcut homografların sıralamasını sabitler.

## 5. Motor wiring

`analysis.py` dispatch (`_try_conjunction_all` çağrısının yanı, ~satır 1110):
`_try_interjection_all(surface_token, analyses, seen)` +
`_try_onomatopoeia_all(surface_token, analyses, seen)`.

`seen` anahtarı: `("interjection", lemma, frozenset())` / `("onomatopoeia", lemma, frozenset())`.

`_analysis_pos` (statistical.py) eşlemesi: `ünlem`→`Intj`, `yansıma`→`Onom` (veya en
yakın Oflazer etiketi; istatistiksel golden'ı kırmamaya dikkat — pos yoksa Noun geriye
uyum korunur).

## 6. Test planı

- Golden (bağımsız, motor-körü, Opus): her iki küme temsili + §4 belirsizlik yüzeyleri
  (of/ay/işte/üf) `want ⊆ got` (additive → beklenen alt-küme).
- Homograf drift-lock: `disambiguation.rank` tepe POS'u sabitlenir (of→noun/verb, ünlem alt).
- Regresyon: tam paket + korpus çökme taraması (leksikon × yeni dallar, 0 çökme).

## 7. Türkçe API

Üretim yok → `tr.py`'ye fonksiyon eklenmez. Kümeler `__init__.py`'den export edilir
(`INTERJECTIONS`, `ONOMATOPOEIA`) — kullanıcı özelleştirmesi/kontrolü için.
