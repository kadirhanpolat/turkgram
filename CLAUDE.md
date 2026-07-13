# CLAUDE.md — turkgram (Türkiye Türkçesi grameri, kod olarak)

Bu dosya, bu repoda çalışan herhangi bir ajanın **ilk fırsatta yanlış yapacağı**
kararları listeler. Betimleyici gramerlerden (Korkmaz *Türkiye Türkçesi Grameri —
Şekil Bilgisi*, Ergin, Deny, Vural) elle küratörlenmiş kuralları çalıştırılabilir
kod eden **bağımsız, dağıtılabilir** bir kütüphane.

Köken: İngilizce–Türkçe sözlük projesinden (`D:\PYTHON\dictionary`) Faz 0'da ayrıldı.
Sözlük bu paketi `pip install -e ../turkgram` ile tüketir.

---

## 1. Ne ÜRETİR, ne SAKLAMAZ (çekirdek değişmez)

Motor **çekilmiş biçimleri** RUNTIME ÜRETİR, SAKLAMAZ. Kök + morfofonolojik sınıftan
üretir; kombinatoryal çekim tablolarını diske dizmez. (Sözlük projesi #5 emsali.)
**İSTİSNA — referans verisi (Faz 2b):** leksikon (`data/lexicon_tr.tsv`) ve lemma-frekans
(`data/lemma_freq_tr.tsv`) gömülüdür. Bunlar çekilmiş biçim DEĞİL, **kök/olgu verisidir**
(lemma listesi + POS + sayım) → değişmezi ihlal etmez. Üretilmiş çekim tablosu asla gömülmez.

- **İngilizce çekirdek:** `morphology.py` (fiil çekimi), `morphology_noun.py` (isim
  çekimi + `copula`, `aux="ken"` nominal -ken), `nonfinite.py` (ulaç `converb` + fiilimsi
  `participle` + biçim-eklenen `converb_casina`/`converb_ken`), `compound.py` (bileşik zaman
  `compound`), `voice.py` (çatı `apply_voice`), `derivation.py` (yapım eki). Genel API `__init__.py`.
- **Çözümleme (Faz 2a):** `analysis.py` (`analyze`: yüzey→kök+eksen+segment) +
  `analysis_candidates.py` (öneri üretimi). Analysis-by-generation: üreteç oracle (bkz. #6).
- **Kök leksikonu + frekans (Faz 2b, opt-in):** `lexicon.py` — gömülü `data/lexicon_tr.tsv`
  (Zemberek Apache-2.0'dan lemma+POS) ve `data/lemma_freq_tr.tsv` (hermitdave MIT'ten türetilmiş
  lemma-frekans). `load()` → `analyze(roots=…)` için lemma kümesi (gürültü eler); `load_freq()`
  → `disambiguation.rank(freq=…)` için {lemma:sayım}. `analyze(roots=None)` DOKUNULMAZ (bkz. #7).
- **Disambiguation (Faz 2b, opt-in):** `disambiguation.py` — `rank`/`disambiguate` aday
  sıralar + güven (olasılık). Dilbilimsel öncelik (sıklık>POS-tutarlılık>kind>morfem-ekonomisi)
  + opsiyonel `freq=`. `analyze` imzası/sırası DOKUNULMAZ (bkz. #7). SPEC: `disambiguation-spec.md`.
- **Cümle-bağlamı disambiguation (Faz 2b, opt-in):** `context.py` — `rank_in_context(tokens,
  analyses_per_token, freq=, pos=)` bir cümlenin token'larını komşuluk kanıtıyla (K1 niteleyici+ad,
  K2 edat yönetimi, K3 ayrı soru mI, K4 kişi uyumu, K5 tamlayan-iyelik) yeniden sıralar. Kural-tabanlı
  (kapalı listeler), izole `disambiguation._rank_key`'in ÜSTÜNE biner; kural yoksa izoleye düşer.
  Recall-güvenli (aday budamaz). `analyze`/izole `rank` DOKUNULMAZ. SPEC: `sentence-disambiguation-spec.md`.
- **Türkçe yüz:** `tr.py` — Türkçe-karakterli sarmalayıcılar (`çekimle`/`ad_çekimle`/
  `ekfiil`/`ulaç`/`fiilimsi`/`gibilik`/`iken`/`birleşik_çekim`/`türet`/`çözümle`), içeride
  İngilizce çekirdeği çağırır (bkz. #4).

---

## 2. İŞ AKIŞI — SPEC → BAĞIMSIZ golden → motor → hakem (DEĞİŞMEZ)

Her yeni dilbilgisi özelliği ŞU sırayla eklenir (sözlük #5 emsali, kanıtlanmış):

1. **SPEC** (`spec/*-spec.md`) — grammatical-invariant, **ANA OTURUM elle yazar**.
   Alt-modele BIRAKMA: Türkçe morfoloji hataları ince. Korkmaz'dan KURAL alınır,
   düzyazı/örnek KOPYALANMAZ (telif — bkz. #3).
2. **Golden** (`tests/golden_*.py`) — beklenen biçimler **motordan BAĞIMSIZ** kurulur
   (elle-doğrulanmış, dilbilgisinden; motora BAKMADAN). Bu bağımsızlık gerçek bug
   yakalar (copula yumuşama açığı, aspect aux-aorist, genç isim-motoru açığı — hepsi
   bağımsız golden'la ortaya çıktı). Bağımsız golden ajanına dispatch: "motoru/başka
   modülü GÖRME, yalnız SPEC + dilbilgisi".
3. **Motor** — golden'ı geçecek minimal kod; mevcut morfofonoloji primitiflerini
   (`_stem_before_suffix`, harmoni, yumuşama, kaynaştırma) YENİDEN KULLAN.
4. **Hakem + doğrulama** — golden koş + **korpus çökme taraması** (dict-db'deki tüm TR
   fiil/isim × yeni eksen, 0 çökme) + tam paket regresyonsuz. Karmaşık/hataya-açık işte
   (çatı A1 gibi) 3-5 oy adversarial verify.

Golden Korkmaz'ın ÖRNEĞİNDEN değil, elle-doğrulanmış biçimden türetilir.

---

## 3. Telif: bu paket DAĞITILABİLİR (MIT)

Sözlük DB'si telifli kaynaklardan besleniyordu ve DAĞITILAMAZ. **Gramer kuralları
OLGUDUR, telifli değildir** (istisna tabloları gibi). Bu yüzden turkgram MIT/açık
kaynak yapılabilir — **AMA Korkmaz'ın düzyazısı/örnek cümleleri pakete GİRMEZ**.
`work/turkgram_faz1/korkmaz_toc.txt` gibi çıkarılmış PDF metni sözlük reposunun
`work/`'ünde (gitignore) kalır, buraya kopyalanmaz. SPEC'ler yalnız § referansı +
kendi analizini içerir.

**Gömülü üçüncü-taraf veri (Faz 2b):** leksikon Zemberek'ten (Apache-2.0), lemma-frekans
hermitdave'den (MIT) türetilir. İkisi de MIT-uyumlu + yalnız OLGU (lemma/POS/sayım) çıkarılır,
kaynak kod/düzyazı KOPYALANMAZ → `THIRD_PARTY_LICENSES.md`'de atıf + değişiklik beyanı zorunlu.
Yeni gömülü veri eklenirse: lisans MIT-uyumlu mu doğrula, olgu-çıkarımı yap, THIRD_PARTY güncelle.

---

## 4. Türkçe API (`tr.py`) — tasarım (docs/tr-api-tasarim.md)

Paralel modül; Türkçe param adı → İngilizce kwarg, Türkçe değer → tek-yönlü sözlük
(`_KIP`/`_KISI`/`_DURUM`…) → çekirdek anahtarı. İngilizce API DOKUNULMAZ.

- **Terim geleneği KARMA** (kullanıcı kararı): kanonik akademik (TDK/Korkmaz) + tanıdık
  alias (`görülen_geçmiş` ≡ `dili_geçmiş` ≡ `geçmiş`; `de` ≡ `bulunma`).
- **Tanımlayıcılar gerçek Türkçe harf** (`çekimle`/`kişi`/`işteş`) — Python 3 destekler.
- Değer normalizasyonu `_tr_lower` (#10 emsali: İ→i, I→ı ardından küçült); bilinmeyen
  değer → geçerli seçenekleri sıralayan `ValueError`.
- **TUZAK — `not core` korunması:** `yüklem`/`ki_ekle` sarmalayıcıları yalın adda
  çekirdeğe SADECE varsayılan-dışı kwarg geçirmeli (`_core` yardımcısı). `predicative`'in
  yumuşama/ön-harmoni dalı `not core` gerektirir (gencim); `case='nom'` geçirmek onu bozar.
  `ekfiil` `durum=None` default (yalın present softening için).
- Test = ÇEVİRİ DENKLİĞİ (`tr.çekimle == morphology.conjugate`); biçim doğruluğu
  çekirdek golden'da. Katman yalnız çeviriyi + alias + hata sınar.

---

## 5. Windows / araç tuzakları

- **PYTHONUTF8=1 ŞART:** Windows konsolu cp1254 — Türkçe/özel karakter yazan her python
  komutunu `PYTHONUTF8=1 python …` ile koş (yoksa UnicodeEncodeError). Testler pytest'te
  sorunsuz; sorun yalnız stdout'a print eden ad-hoc komutlarda.
- **Korpus taraması dict-db'den:** turkgram bağımsız (korpus YOK). Çökme taraması için
  sözlük dict-db'sinden (`127.0.0.1:5434`, `PGPASSWORD=dict`, db=`postgres`) TR başlıkları
  çek. Windows python `/tmp`'i görmez → repo-içi yola yaz.
- **Editable kurulu:** değişiklikler anında yansır (`pip install -e .`).

---

## 6. Morfofonoloji ince ayrımları (golden'ın yakaladığı, tekrar etme)

- **Yumuşama/ye_de YALNIZ ünlü-başlı ek önünde** (`_stem_before_suffix(vs, True)`):
  git→gid, ye→yi. Ünsüz-başlı ekte tetiklenmez: gitmeden/gittikçe, yemeden/yedik.
- **Yüksek ünlü 4'lü vs düz:** `-Ip`/`-IncA` yuvarlak-duyarlı (okuyup/gülüp); `-AlI`/
  `-AsIyA`/`-mAksIzIn` -A sonrası YÜKSEK-DÜZ (okuyalı/okumaksızın, yuvarlaklık düşer).
- **Aspect aux-aorist (A2):** ver/dur/gel/kal → -Ir (yapıverir), yaz → -Ar (düşeyazar).
  Motorun "çok-heceli → -Ir" sezgisi tasvir gövdesinde yaz'ı bozardı → `VerbStem.aorist_forced`
  alanı tasvir aoristini yardımcıdan ZORLAR (normal getirir etkilenmez).
- **A3 DELEGASYON deseni:** fiilimsi+iyelik/durum, bare gövdeyi `decline`'a besler → k→ğ,
  pronominal -n-, iyelik/durum İSİM motorundan gelir (sıfır ek morfoloji). Sonraki
  istifleme işleri de bu deseni kullanmalı.
- **genç istisnası:** tek-heceli-yumuşayan (genci/gence) → `SOFTEN_YES`. Benzer
  monosyllabik-softening eksikler çıkarsa oraya ekle.
- **A1 çatı (`voice.py`) DELEGASYON:** çatı zinciri köke sırayla uygulanır, türetilmiş
  gövde `VerbStem`'e sarılır → NORMAL çekilir (aorist -Ir hece sayımından; softens/ye_de
  yalnız İLK ekte, orijinal köke). İki TUZAK (golden+adversarial yakaladı):
  (a) **ettirgen ünlü-final -t YALNIZ çok-heceli** (oku→okut) — tek-heceli ünlü-final
  -DIr (de→dedir, ye→yedir; "det" DEĞİL); tek-heceli -l/-r de -DIr (gör→gördür, "gört" DEĞİL).
  (b) **edilgen/dönüşlü -n (ünlü-final) ye_de'yi TETİKLEMEZ** (de→den, "din" DEĞİL): -n
  ünsüz-başlı, allomorf başına ünlü-başlılık ayrımı şart. Ettirgen leksik -Ir/-Ar/-It kapalı
  küme (`CAUSATIVE_LEXICAL`); yeni leksik ettirgen çıkarsa oraya ekle.
- **Faz 2a çözümleyici (`analysis.py`+`analysis_candidates.py`) analysis-by-generation:**
  yüzey → önek-tabanlı kök adayı (+ters-mutasyon) → ses-filtreli grid → ÜRETEÇ ORACLE doğrular
  (`çıktı==yüzey`). **Precision inşa gereği** (analizör dili ⊆ üreteç dili); recall = önerici
  kapsamı (round-trip süpürme + korpusla kapatılır). TUZAKLAR: (a) **precision golden `roots`
  ile test edilir** — leksikonsuz her yüzey kendini çıplak-isim olarak çözer (gürültü,
  `hypothetical=True`; SPEC §8.1). (b) **`-Iyor` gövde ünlüsünü düşürür** (oyna→oynuyor) → kök
  yüzey öneki değil; `_root_candidates` -Iyor'da düşen-ünlü tabanını geri üretir. (c) golden
  HİBRİT kurulur: üreteç-ground-truth (brute-force) + motor-körü audit (recall denetimi).
  Ses filtreleri YALNIZ gereklilik önermesi (yanlış budayamaz → recall güvenli).
  (d) **suppletif zamir DAT** (`bana`/`sana`) önek türetemez → `_SUPPLETIVE_PRONOUN_ROOTS`
  kapalı-küme ters tablosu; diğer eğik biçimler (`onu`/`beni`/`bende`) önekten zaten çözülür.
  (e) **nominal ekfiil soru** (`evde miydi`) çok-token: soru dalı isim-gövde → `copula(question=True)`
  de dener; `_segment_copula` build-up peeling (KÖK|case|mI|aux|kişi), bare present `-dir`
  tabanını KULLANMAZ (case sınırı `decline`'dan, soru/aux copula deltasından ölçülür).
  (f) **birleşik çok-token fiil** (`göz ardı etti` → `göz ardı etmek`; Faz 2b, SPEC §8.2):
  `_analyze_multi_token` birleşik-önek kalıbı `len==2` → `len>=2` genellendi (`tokens[:-1]` =
  DEĞİŞMEZ nominal önek, son token = çekimli fiil); `analyze` `len>2→[]` erken-kesimi KALKTI.
  Motor birleşik lemmayı zaten çeker (`conjugate` boşlukta böler) → yeni morfoloji YOK, yalnız
  önek genellemesi. Precision roots-garantili (§8.1); roots=None → hypothetical gürültü.
  **Birleşik + soru** (`göz ardı etti mi`, `kabul ediyor musun`) BEDAVA geldi: `len>2→[]`
  kalkınca soru dalı (§8 madde 1) erişilir oldu; `_root_candidates` boşluk-üstü grid birleşik
  mastarı üretir → `conjugate(question=True)` oracle doğrular, ayrı N-token soru dalı GEREKMEZ.
  Kalan: ikileme adverbial-yeniden-kurulumu (sözdizimsel, defer).
- **(g) `-cAsInA` çözümlemesi (Faz 2b, yeni kind `converb_casina`):** finit-taban-üstü ek →
  segmentasyon DELEGASYON (A3 emsali, §6c): `base_form=conjugate(lemma,base,"3sg",neg)` dilimlerini
  `_segment_conjugate`'ten al, üstüne tek `(surface[len(base_form):], "cAsInA")` dilimi ekle. Enum
  yalnız `base∈{aorist,evid}×negative` (4 hipotez) + `_CASINA_MARKER` (`[cç][ae]s[ıi]n[ae]$`)
  gereklilik filtresi → marker yoksa hiç enumerate etme (recall-güvenli). Kök adayı yeni mantık
  GEREKMEZ (mevcut önek+ters-mutasyon yeter). **Disharmonic-mastar sınırı:** `_root_candidates`
  öneki düzenli harmoniyle mastara çevirir (inhi→inhimek); disharmonic alıntı `inhimak` (leksikonda
  tek) TÜM kind'larda round-trip kaçırır — casina'ya özgü DEĞİL, genel pre-existing sınır.
- **(h) `-ken` çözümlemesi (Faz 2b):** İKİ yol. Fiil = yeni kind `converb_ken`, casina §6g ile
  aynı delegasyonlu segmentasyon (`base_form=conjugate` + tek `(surface[len:], "ken")`, glide YOK).
  Nominal = MEVCUT `copula` kind'ı `aux="ken"` (yeni kind YOK; üretim de öyle). TUZAK — **ken
  KİŞİSİZ + soru YOK:** `_enumerate_copula` aux==ken'de person=("3sg",)+question=(False,)'a kilitler
  (kombinasyon patlaması yok); `_canon_copula` aux==ken dalı person/question eksenlerini ATAR (aksi
  halde her yüzey 6 kişi × soru duplike verir, hepsi aynı yüzeye eşlenir). `("copula_aux","ken")→/ken/`
  filtresi. Segmentasyon mevcut `_segment_copula` aux dalını kullanır (kaynaştırma -y- SAĞdaki `ken`
  diliminde: ev|de|yken). BELİRSİZLİK bilinçli: gelirken hem fiil (converb_ken) hem isim (gelir+copula)
  → roots ikisini içerirse iki analiz (precision golden 3 belirsiz yüzeyle sabitler).

---

## 7. Yol haritası ve DURUM (2026-07-12)

- **Faz 0 ✅** — bağımsız paket + motor/testler taşındı + sözlük bağlandı. Türkçe API (`tr.py`).
- **Faz 1** (fiil çekim derinleştirme, `docs/faz1-implementation-plan.md`):
  - ✅ **A4** nominal ek-fiil (`morphology_noun.copula`): öğrenciydim/evdeymiş/hastaysa.
  - ✅ **A5 + A6** ulaç envanteri (`nonfinite.converb`, 8 ek) + aorist -Ir listesi doğrulandı.
  - ✅ **A2** tasvir fiilleri (`conjugate(aspect=)`): tezlik/sürerlik/kalma/yaklaşma.
  - ✅ **A3** fiilimsi + iyelik/durum istifi (`nonfinite.participle`): okuduğum/gitmesini.
  - ✅ **A1** çatı entegre çekim + yığılma (`voice.py::apply_voice`, `conjugate(voice_chain=)`):
    ettirgen/edilgen/dönüşlü/işteş → dövüştürüldü. **Faz 1 fiil çekimi TAMAMLANDI.**
- **Faz 2a çözümleyici ✅** (`analysis.py`, `tr.çözümle`; `docs/faz2a-*`): yüzey → kök+eksen
  (analysis-by-generation, kind'lar: conjugate/decline/copula/converb/converb_casina/converb_ken/participle) + pedagojik
  segmentasyon. Round-trip sistematik sınıflarda doğrulandı; korpus 0 çökme. `-Iyor` ünlü-düşmesi,
  **suppletif zamir eğik durumu (`bana`/`sana`)** ve **nominal ekfiil soru grubu (`evde miydi`)**
  KAPATILDI. `-ken` ulacı doğru kapsam-dışı.
- **Faz 2b** — gerçek-metin sağlamlığı:
  - ✅ **Birleşik çok-token fiil** (SPEC §8.2, `göz ardı etti`→`göz ardı etmek`): değişken-uzunluk
    nominal önek genellemesi (§6f). Hakem: 1888 dict-db birleşik lemma × 4 zaman = 7552 analiz,
    **0 çökme + 0 recall miss**.
  - ✅ **Birleşik + soru** (`göz ardı etti mi`, `kabul ediyor musun`): önceki genellemeyle
    BEDAVA açıldı (§6f); 17-giriş bağımsız golden + korpus (1888 lemma × 4 soru biçimi = 7552
    analiz, 0 çökme + 0 miss). Kalan: ikileme adverbial-yeniden-kurulum (sözdizimsel, defer).
  - ✅ **Geniş kök leksikonu** (`turkgram/lexicon.py` + gömülü `data/lexicon_tr.tsv`): Zemberek
    `master-dictionary` (Apache-2.0) → 26.632 lemma (POS'lu; fiil mastar, isim-soylu çıplak).
    **OPT-IN** (TUZAK): `lexicon.load()` çağıran alır; `analyze(roots=None)` davranışı DEĞİŞMEZ
    (gürültü modu korunur, kırılma yok). Üretilebilirlik `tools/build_lexicon.py`; Apache atıf
    `THIRD_PARTY_LICENSES.md` (§3 olgu-listesi savunması). Kurcalama beyanı: yalnız lemma+POS
    çıkarıldı, Zemberek kodu/düzyazısı KOPYALANMADI. Gömülü veri wheel/sdist'e MANIFEST + package-data
    ile girer. `load(pos=)` POS filtreli; varsayılan çekilebilir alt-küme (verb+noun+adj+adv+pron+num).
  - ✅ **Olasılıksal disambiguation** (`disambiguation.py`, SPEC `disambiguation-spec.md`):
    `rank`/`disambiguate` — dilbilimsel öncelik (sıklık>POS-tutarlılık>kind-önceliği>morfem-
    ekonomisi>deterministik tiebreak) + opsiyonel `freq=` kancası + normalize güven (softmax).
    **OPT-IN** (`analyze` DOKUNULMAZ). freq=None → dilbilimsel önceliklere düşer. TUZAK: güven
    yalnız gösterim; KESİN SIRA tuple-anahtarından (float sıralamaya sızmaz). Kanca sıklık
    tablosunu sonra kırılmadan alır. Hakem: korpus rank/disambiguate 0 çökme + güven∑=1.
  - ✅ **Gömülü lemma-frekans tablosu** (`lexicon.load_freq()` + `data/lemma_freq_tr.tsv`):
    hermitdave/FrequencyWords (OpenSubtitles, MIT) yüzey-frekansı → lemma-frekans. **Rebuild
    (`tools/build_surface_freq.py`):** analyze() yerine lemma→motor→enumerate→dict-lookup;
    her lemmanın tüm yüzey biçimleri üretilip listede aranır (mutation gid-/git- yakalanır).
    4033→**20429 lemma** (~2dk). Detay (`data/lemma_freq_detail_tr.tsv`, yüzey-dökümü) + sıfır-lemma
    listesi opsiyonel. `disambiguation.rank(freq=lexicon.load_freq())` kancasını besler; atıf
    `THIRD_PARTY_LICENSES.md`. Ham kaynak `tools/tr_full.txt` gitignore'lu.
  - ✅ **Motor-dışı biçimler — biçim-eklenen ulaçlar + bileşik zaman** (3 madde, kolay→zor;
    her biri SPEC→bağımsız golden(Opus,motor-körü)→motor→hakem):
    - **`-cAsInA`** gibilik ulacı (`nonfinite.converb_casina`, `tr.gibilik`): gülercesine/
      gelmişçesine. Aorist+evid tabanı; C(ç/c son-ses)+A+s+Iyi(YÜKSEK-DÜZ)+n+A. SPEC `casina-spec.md`.
    - **`-ken`** zaman ulacı (`nonfinite.converb_ken` fiil + `copula(aux="ken")` nominal;
      `tr.iken`): gelirken/geliyorken/evdeyken. `ken` DONMUŞ (ünlü uyumu YOK); nominal glide
      yalnız ünlü-final. SPEC `ken-spec.md`.
    - **Bileşik zaman** (`compound.compound`, `tr.birleşik_çekim`): geliyordu/gelirmiş.
      TUZAK — **3pl=tabanda -lAr, ek-fiil 3sg** → geliyorlardı (geliyordular DEĞİL). Taban
      `conjugate`'ten aynen; ek-fiil `_copula_suffix`'e delege (sıfır yeni morfoloji). SPEC
      `compound-tense-spec.md`. Hakem: 237.262 çağrı 0 çökme (2 leksikon-çöpü pre-existing guard).
  - ✅ **Motor-dışı biçimlerin ÇÖZÜMLEMESİ** (3 artım, kolay→zor; her biri SPEC-çözümleme-bölümü
    →bağımsız golden(Opus,motor-körü)→motor→hakem):
    - **`-cAsInA` çözümlemesi** (yeni kind `converb_casina`, SPEC `casina-spec.md` §Çözümleme):
      gülercesine→(gülmek, converb_casina, {base:aorist}). Enum base×negative=4 hipotez, `-CAsInA`
      marker filtresi (recall-güvenli). Segmentasyon DELEGASYON (A3 emsali): tabanı `_segment_conjugate`'e
      ver + tek `cAsInA` dilimi (§6g). `tr.çözümle` kwargs `taban`/olumsuz. Hakem: gömülü leksikon
      3250 fiil × 2 base × 2 neg = 13.000 çağrı, 0 çökme, 0 casina-miss (4 miss = 1 disharmonic
      alıntı `inhimak`, `_root_candidates` düzenli-harmoni varsayımından TÜM kind'ları eşit kırar,
      pre-existing; leksikondaki tek disharmonic mastar).
    - **`-ken` çözümlemesi** (SPEC `ken-spec.md` §Çözümleme): İKİ yol — **fiil** yeni kind
      `converb_ken` (gelirken/geliyorken; enum base∈{aorist,pres,evid,fut}×negative=8 + `ken$`
      marker; delegasyonlu segmentasyon + tek `ken` dilimi, glide YOK), **nominal** MEVCUT `copula`
      kind'ı `aux="ken"` ile (çocukken/evdeyken; yeni kind YOK). ken KİŞİSİZ+soru YOK → copula enum
      person=3sg/question=False'a kilitler, `_canon_copula` aux==ken dalı person/question ATAR (§6h).
      BELİRSİZLİK: gelirken=(gelmek converb_ken)|(gelir isim copula); golden 3 belirsiz yüzey kapsar.
      Hakem: 42.000 çağrı (26k fiil + 16k nominal), 0 çökme, 0 ken-özgü miss (21 miss = pre-existing
      kök-aday sınırları: somak monosyllabic -Iyor, inhimak disharmonic, nakil/kavim düşen-ünlü dat;
      hepsi basit çekim/çekimde de kaçar + ben/sen dat+ken sentetik suppletif niş).
    - **Bileşik zaman çözümlemesi — REGRESYON KİLİDİ** (SPEC `compound-tense-spec.md` §Çözümleme):
      YENİ MOTOR YOK. `compound(l,base,cop,person,neg)` == `conjugate(l,base,person,aux=cop,neg)`
      (216.000 gen çağrı 0 fark, şart-2pl fix sonrası) → çözümleyici bu yüzeyleri `kind="conjugate"`
      + `aux` olarak zaten çözer (geliyordu→{tense:pres,person:3sg,aux:hikaye}). `compound` kind'ı
      analizde KULLANILMAZ (tek kanonik okuma). Golden (13 yüzey precision `want<=got` + 240-kombo
      round-trip) ileride aux çözüm yolu kırılırsa yakalar. Hakem: 78.000 çağrı, 0 çökme, 0 compound-özgü
      miss (78 miss = 10 pre-existing lemma: monosyllabic -Iyor ünlü-düşme damak/somak/çomak, "yor"-alt-dizi
      çakışması yorgalamak/yorumlamak, disharmonic inhimak — HEPSİ basit çekimde de kaçar, `_root_candidates`
      sınırı, compound'a özgü değil).
  - **Faz 2b motor-dışı biçimlerin ÇÖZÜMLEMESİ TAMAMLANDI** (3 artım: -cAsInA, -ken, bileşik zaman).
  - ✅ **Cümle-bağlamı disambiguation** (`context.py::rank_in_context`, SPEC `sentence-disambiguation-spec.md`):
    kural-tabanlı sözdizimsel katman (karar: kural-tabanlı > istatistiksel; MIT-dağıtılabilir, deterministik).
    5 kural kapalı-listelerle (K1 niteleyici+ad, K2 edat yönetimi, K3 ayrı soru mI, K4 kişi uyumu —
    **conjugate+copula ikisi de**, K5 tamlayan-iyelik). Bağlam kanıtı (int) izole `_rank_key`'in ÜSTÜNE
    biner → kural yoksa izoleye düşer (geriye-uyum). Recall-güvenli (aday budamaz; hakem 7500+4800 cümle
    0 çökme 0 recall ihlali). Tokenizasyon+analyze ÇAĞIRANIN (sözdizimi defer). **OPT-IN.** TUZAK (hakem
    HIGH yakaladı): K4 person ekseni olan HER kind'e uygulanmalı (conjugate+copula) — `_VERB_KINDS` değil
    `_K4_PERSON_KINDS`; `ben öğretmenim`→copula. Golden reconcile: nom/question=False default kanonik
    kwargs'tan atılır (beklenen {}); `bunun`→lemma `bun` (bu'nun düzensiz tamlayanı, önceden var olan
    zamir açığı — bu katmana özgü değil). Kalan: olasılıksal dizi etiketleme; FST araçları adopt-referans.
- **Faz 3/4** — türetme genişletme; sıfat/zamir; sözdizimi (defer). Bkz. `docs/faz1-bosluk-analizi.md`.

Test durumu: son ölçüm **2819 test yeşil** (+ round-trip süpürme `-m slow`: recall tam +
p95 bütçe). Her commit'te regresyonsuz + korpus 0 çökme (biçim-eklenen ulaç + bileşik zaman
237.262 çağrı 0 çökme; birleşik fiil 7552 analiz 0 miss; -cAsInA çözümleme 13.000 çağrı 0 çökme;
-ken çözümleme 42.000 çağrı 0 çökme 0 ken-özgü miss; bileşik zaman çözümleme 78.000 çağrı
0 çökme 0 compound-özgü miss).
Leksikon wheel/sdist'e gömülü doğrulandı. Ayrıca `_copula_suffix` şart-2pl yuvarlama fix'i
(geliyorsanuz→geliyorsanız): compound==conjugate(aux) 216.000 çağrı 0 fark.
