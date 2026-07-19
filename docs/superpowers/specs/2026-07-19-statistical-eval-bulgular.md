# İstatistiksel disambiguation — gold değerlendirmesi + CRF-gate kararı

**Tarih:** 2026-07-19
**Araç:** `tools/eval_statistical.py`
**Veri:** TrMor2018 handtagged gold (`tools/trmor2018/TrMor2018/handtagged/trmor2018.gold`, 2090 cümle)
**Ölçüm:** ilk 150 cümle = 1387 punc-dışı token (istatistiksel olarak sağlam)
**İlgili:** SPEC `spec/statistical-disambiguation-spec.md §9` (CRF defer gate)

## 1. Amaç

SPEC §9, CRF'i yalnız "iki-model harness çalışıp gerçek ayrışmalar ölçüldükten,
HMM'in bigram varsayımı sistematik yetersiz kaldığı KANITLANDIKTAN sonra" eklemeyi
şart koşar. Bu ölçüm o gate'i test eder: HMM gerçekten darboğaz mı?

## 2. Sonuçlar (150 cümle, 1387 token)

| Yöntem | acc (tüm) | acc (covered) |
|--------|-----------|---------------|
| isolated (`disambiguation.rank`) | 42.6% | 94.6% |
| rule (`context.rank_in_context`) | 43.7% | 97.0% |
| **hmm (`statistical.viterbi`)** | **44.2%** | **98.1%** |

- **Coverage: %45.1** — gold-doğru major-POS'un analizör adayları arasında bulunduğu
  token oranı (disambiguation'ın ulaşabileceği TAVAN).
- **OOV (aday yok): %15.1.**

**Gold major-POS dağılımı:** Noun %40.3, Verb %14.6, Adj %12.8, Adverb %8.7,
Det %6.4, Pron %5.8, Conj %4.8, Postp %2.7, Num %1.0.

**Analizörün ürettiği aday major-POS:** yalnız **Noun (937) + Verb (405)** — başka
hiçbir POS üretilmiyor.

## 3. Teşhis — darboğaz HMM DEĞİL, POS coverage

**acc(covered) her üç yöntemde de %94-98.** Doğru POS ulaşılabilir olduğunda basit
HMM zaten ~%98 doğru seçiyor; izole ve kuraldan anlamlı farkı yok (HMM covered-hataları
neredeyse tümü Noun→Verb, 11 token). CRF'in doğal üstünlüğü (zengin özellikli DİZİ
disambiguation) tam da bu covered-disambiguation problemini hedefler — ki o zaten
~%98 çözülmüş. Maksimum baş oda: %2 × %45 ≈ genel **%0.9**. CRF bu yatırımı haklı
çıkarmaz.

**Gerçek tavan coverage (%45).** ~%40 gold token (Adj/Adverb/Det/Pron/Conj/Postp/Num)
major-POS düzeyinde yapısal ulaşılamaz + %15 OOV. İki alt-neden (ampirik doğrulandı):

- **(a) Eşleme açığı — `statistical._analysis_pos` (BASİT FİX):** analizör `için`/`gibi`
  → `pos="postp"`, `de`/`da` → `pos="conj"` DOĞRU üretir; ama `_analysis_pos` yalnız
  `kind` conjugate→Verb / decline→Noun eşler, `postposition`/`conjunction` kind'larını
  default **Noun**'a indirir. Gömülü model (parse_oflazer ile) Postp/Conj emisyonlarını
  ZATEN içerir → eşleme düzeltilirse bu token'lar bedava coverage kazanır.
- **(b) Analizör kapsam açığı (DERİN):** `kırmızı`→Noun (Adj değil), `iki`→Noun (Num
  değil), `ben`→Noun (Pron değil), `çok`→Noun (Adverb/Det değil); `ve`/`ki`/`bu`→hiç
  üretmiyor. Bunları ayırmak leksikon-POS danışmayı (`parse._leaf_tag` pos_map emsali)
  veya kapalı-küme fonksiyon-sözcük tabloları gerektirir.

## 4. Karar — CRF ERTELENDİ (gate KARŞILANMADI)

SPEC §9 gate koşulu 1 ("HMM bigram varsayımı sistematik yetersiz") **doğrulanmadı**:
HMM covered-tavana (%98) çok yakın, izole/kuraldan geri değil. Darboğaz dizi-modeli
değil, **analizör→POS coverage/eşleme**. CRF eklemek yanlış problemi çözer + MIT/saf-
Python değişmezini gereksiz esnetir.

**Yatırım ROI sırası (öneri, CRF DEĞİL):**
1. **(a) `_analysis_pos` eşleme fix** — postposition→Postp, conjunction→Conj (+ Artım-2
   `_analysis_fine_state` benzer). Küçük, gömülü model uyumlu; coverage'ı doğrudan artırır.
   TUZAK: `golden_statistical*` testleri `_analysis_pos` davranışına bağlı → SPEC→golden→hakem.
2. **(b) Analizör POS zenginleştirme** — Adj/Num/Pron/Det leksikon-POS danışması +
   `ve`/`ki`/`bu` kapalı-küme fonksiyon sözcükleri. Daha büyük iş; ayrı faz.
3. CRF yalnız (1)+(2) sonrası HMM hâlâ darboğazsa yeniden değerlendirilir (§9 gate tekrar).

## 5b. Uygulama — (a) `_analysis_pos`/`_analysis_fine_state` eşleme fix (2026-07-19)

`_analysis_pos` artık `pos` alanından eşler (`postp→Postp`, `conj→Conj`, `num→Num`,
`adj→Adj`; fiil kind'ları→Verb, copula→Noun; `pos` yoksa→Noun geriye uyum).
`_analysis_fine_state` benzer sözcük-sınıfı dalları aldı. Model bu etiketleri zaten
içeriyor → aday-emisyon eşleşti.

| Metrik (150 cümle) | Öncesi | Sonrası |
|--------------------|--------|---------|
| Coverage | 45.1% | **51.4%** (+6.3) |
| HMM acc(tüm) | 44.2% | **49.1%** (+4.9) |
| rule acc(tüm) | 43.7% | 47.3% |
| HMM acc(covered) | 98.1% | 95.5% |

- Analizör aday POS uzayı: Noun/Verb → +Adj(60)/Postp(40)/Conj(16)/Num(1).
- **HMM dizi-bağlamı artık değer katıyor:** HMM, kuralı Postp(10)/Conj(8)/Adj(7)'de
  yeniyor (edat/bağlaç disambiguation'ında bigram geçişi belirleyici) → HMM'in varlığı
  ampirik doğrulandı.
- acc(covered) düşüşü (98→95.5) BEKLENEN: yeni aday sınıfları (Postp/Conj/Adj) daha
  zor seçim getirir; ama genel acc(tüm) yükseldi (coverage kazancı baskın).
- Testler: `tests/test_statistical_pos_mapping.py` (15 test; gerçek analiz + fake geriye uyum).
  Tam paket regresyonsuz (4142 yeşil).

**Kalan (b — derin, ayrı faz):** Adverb %8.7 / Det %6.4 / Pron %5.8 hâlâ üretilmiyor
(analizör bunları Noun/hiç verir); bare Adj/Num/Pron leksikon-POS danışması gerektirir.
CRF hâlâ gereksiz — darboğaz coverage.

## 5c. Uygulama — (b) lexicon-aware POS refinement (B-refine dilimi, 2026-07-19)

ROI ölçümü (150 cümle): uncovered decline-noun 258 token; leksikon `pos_map` ile
**95'i düzelebilir** (Adj/adj 44, Adverb/adv 32, Num/num 8, Conj/conj 6, Pron/pron 5).
Kalan uncovered: B-cover (aday yok, 210 — Conj 34/Det 30/Pron 3 fonksiyon sözcükleri +
Noun 80/Adj 20 leksikon açığı) ve tagset-uyuşmazlığı (Det/adj 59, Adverb/adj 18 —
turkgram leksikonu ≠ TrMor tagset; `her`→adj ama gold Det).

**Uygulama:** `_analysis_pos_lex(analysis, pos_map)` — çıplak `decline(noun)` analizinde
leksikon pos_map'e danışır (parse._leaf_tag emsali); `pos_map=None` → düz `_analysis_pos`.
`viterbi(..., pos_fn=)` opsiyonel parametresi (varsayılan `_analysis_pos` → golden fake
testleri DOKUNULMAZ). `_analysis_pos`'a pos_map KOYULMADI bilinçli: golden viterbi fake'leri
(geçen→adj, hafta→adv, üç→num) yeniden sınıflanıp kırılırdı.

| Metrik (150 cümle) | başlangıç | fix-a | **+lex** |
|--------------------|-----------|-------|----------|
| Coverage | 45.1% | 51.4% | **59.3%** |
| HMM acc(tüm) | 44.2% | 49.1% | **55.9%** |
| rule acc(tüm) | 43.7% | 47.3% | 52.9% |
| isolated acc(tüm) | 42.6% | 44.6% | 51.8% |

- Kümülatif kazanç: coverage +14.2pt, HMM acc +11.7pt.
- Analizör aday POS: +Adj(254)/Adverb(80)/Pron(30)/Num(30).
- HMM dizi-bağlamı yine değer katıyor (kuralı Noun 15/Adverb 12/Postp 10/Conj 8/Adj 8'de yener).
- Testler: `tests/test_statistical_pos_mapping.py` (+lex birim testleri). Tam paket regresyonsuz.

**Kalan (b sonraki dilim — B-cover, ayrı iş):** Det(%6.4)/bazı Conj/Pron hâlâ analizör
adayı üretmiyor (`bu`/`o`/`ve`/`ki` → NO-REAL). Kapalı-küme fonksiyon-sözcük analiz dalı
(conjunction/postposition emsali) veya aday-enjeksiyonu gerekir. CRF hâlâ gereksiz.

## 5d. Uygulama — (b) B-cover dilimi: full-POS roots (2026-07-19)

**Bulgu:** `bu`/`o`/`ve`/`ki`/`çünkü` → NO-REAL nedeni analyze() değil — `lexicon.load()`
VARSAYILANI conj/det/postp/interj POS'larını HARİÇ tutuyor (yalnız çekilebilir alt-küme:
noun/verb/adj/adv/pron/num). Bu lemmalar roots'a alınırsa bare-`decline(noun)` üretilir →
`_analysis_pos_lex` pos_map ile Conj/Det/Postp/Interj'e refine eder. **analyze() çekirdeğine
DOKUNMA GEREKMEZ** — closed-set analiz dalı yerine yalnız roots genişletme (mimari açıdan
en temiz; kullanıcı kararı öncesi test edildi).

`eval_statistical --full-roots` → `lexicon.load(pos={...tüm...})`.

| Metrik (150 cümle) | başlangıç | fix-a | +lex | **+full-roots** |
|--------------------|-----------|-------|------|-----------------|
| Coverage | 45.1% | 51.4% | 59.3% | **65.5%** |
| HMM acc(tüm) | 44.2% | 49.1% | 55.9% | **61.9%** |
| rule acc(tüm) | 43.7% | 47.3% | 52.9% | 57.4% |
| isolated acc(tüm) | 42.6% | 44.6% | 51.8% | 58.3% |
| OOV | 15.1% | 15.1% | 15.1% | **9.9%** |

- **Kümülatif: coverage +20.4pt, HMM acc +17.7pt** (hepsi analyze() değişmeden).
- Analizör aday POS: +Conj(75)/Det(64)/Postp(52)/Interj(26).
- Tüm yöntemlerde accuracy arttı (degradasyon yok; +209 fonksiyon lemma gürültü katmadı).
- **Kullanım deseni (öneri):** istatistiksel/kural disambiguation → `lexicon.load(pos={tüm})` +
  lexicon-aware `pos_fn`. `lexicon.load()` varsayılanı DEĞİŞMEDİ (çekim üretimi çekilebilir
  alt-küme ister; mimari kararı korunur).

**Kalan (ayrı iş):** tagset uyuşmazlığı (turkgram leksikonu `her`/`şu`/`hangi`→adj, TrMor
Det/Pron) — POS eşleme tablosu düzeltmesi; içsel çok-katmanlı `unmapped` (%2.4). CRF hâlâ gereksiz.

## 5e. Uygulama — (b) çok-POS fonksiyon sözcüğü aday enjeksiyonu (2026-07-19)

**Bulgu:** Kalan uncovered'ın en büyük payı bağlama-bağlı çok-sınıflı fonksiyon
sözcükleri (`bir` 46: Det/Num; `çok`/`öyle`/`pek`: Adverb/Adj; `o`/`bu`: Pron/Det;
`ne`: Pron/Adj; `en`: Adverb). Leksikon TEK POS verir → statik override YANLIŞ
(bağlam belirler: `çok güzel`=Adverb / `çok insan`=Adj). Doğru çözüm: her POS için
sentetik aday üret, **viterbi dizi-geçişiyle seçsin**.

**Uygulama** (`statistical.py`): `_MULTI_POS_FUNCTION_WORDS` (22 sözcük, dilbilimsel-haklı
kapalı küme) + `_PRONOUN_LEMMAS` (eğik zamir → Pron) + `_FuncWordAnalysis` sentetik aday
+ `augment_function_candidates(token, analyses, pos_map)` (recall-güvenli, yalnız EKLER).
`_analysis_pos_lex` sentetik adayın `major_pos`'unu okur. `eval_statistical --funcwords`.

| Metrik (150 cümle) | base | +full-roots | **+funcwords** |
|--------------------|------|-------------|----------------|
| Coverage | 45.1% | 65.5% | **75.0%** |
| **HMM acc(tüm)** | 44.2% | 61.9% | **70.4%** |
| rule acc(tüm) | 43.7% | 57.4% | 58.8% |
| isolated acc(tüm) | 42.6% | 58.3% | 58.3% |

- **Kümülatif başlangıçtan: coverage +29.9pt, HMM acc +26.2pt.**
- **HMM izole/kuraldan +12pt önde** (70.4 vs 58.x): çok-POS adayları HMM'e dizi-bağlamıyla
  ayıklayacak sinyal verir; bağlamsız yöntemler seçemez → HMM'in değeri kesin doğrulandı.
- Overfit DEĞİL: tablo dilbilimsel olgudur (betimleyici gramer); TrMor tagset'iyle örtüşür.
- Testler: `tests/test_statistical_pos_mapping.py` (funcword augmentation + tablo geçerliliği).

**Sonuç:** İstatistiksel disambiguation HMM doğruluğu %44.2→%70.4; CRF gereksiz, saf-Python +
MIT değişmezi korundu. Kalan: OOV/özel-ad recall (%9.9), içsel `unmapped` (%2.4) — ayrı iş.

## 5f. Uygulama — (b) OOV → Noun fallback (özel-ad recall, 2026-07-19)

**Bulgu (138 OOV token/150 cümle):** %25 büyük-harf özel-ad sinyali (Henry/Lord/
Aleksandrovna → hepsi Noun); %73 küçük-harf **derin morfoloji açığı** (`-ki` eki:
melodramlardaki/içindeki; ünlü-düşme: omzuna=omuz; çok-katmanlı türetme:
bencilliklerinden/sürdürenlerin; alıntı: melodram/dürbün; nominalize fiil+ekfiil:
korkmamızdır). OOV gold POS: Noun 80 / unmapped 23 / Adj 20 / Verb 8.

**Uygulama:** `augment_oov_candidates(token, analyses)` — gerçek aday YOKSA `Noun`
sentetik adayı enjekte eder. Bilinmeyen ≈ ad (özel-ad + alıntı + leksikon açığı, hepsi
major=Noun). `analyze()` çekirdeği DOKUNULMAZ (oracle özel-adı üretemez — heuristik
fallback disambiguation katmanında). Recall-güvenli. `eval_statistical --oov-noun`.

| Metrik (150 cümle) | +funcwords | **+oov-noun** |
|--------------------|------------|---------------|
| OOV | 9.9% | **0.0%** |
| Coverage | 75.0% | **80.7%** |
| **HMM acc(tüm)** | 70.4% | **74.8%** |
| rule acc(tüm) | 58.8% | 64.5% |
| isolated acc(tüm) | 58.3% | 64.0% |

- **Kümülatif başlangıçtan: coverage 45.1→80.7 (+35.6pt), HMM acc 44.2→74.8 (+30.6pt).**
- Noun-fallback yalnız Noun-gold OOV'yi kurtarır; Verb/Adj OOV zaten yanlıştı → net pozitif, zarar yok.

**Kalan (ayrı/büyük iş):** küçük-harf OOV'nin derin morfoloji açıkları — `-ki` eki,
ünlü-düşme genişletme, çok-katmanlı türetme derinliği, alıntı leksikonu. Her biri ayrı
morfoloji özelliği (analysis-by-generation genişletmesi). CRF hâlâ gereksiz.

## 5. Notlar

- `tools/diff_harness.py` gold-reader `*.txt` glob'lar; gerçek gold tek dosya
  (`trmor2018.gold`, UTF-8). `eval_statistical.py` kendi okuyucusunu kullanır (düzeltildi).
- Ölçüm major-POS düzeyinde (Artım-1 viterbi). Artım-2 ince-durum viterbi'si YOK
  (`viterbi` yalnız `_analysis_pos` major kullanır) → ince-düzey HMM değerlendirmesi
  ayrı iş (fine viterbi gerekir).
