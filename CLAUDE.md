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
- **Tokenizer + toplu analiz:** `tokenize.py` (`tokenize`: boşluk+noktalama+apostrof; ASCII U+0027
  ortada → ikiye böler, sağ parçada kalır; kıvrık apostrof bölünmez) + `analysis.py`'de `parse_text`
  (`list[list[Analysis]]`; indeks hizalamalı; `_cached_analyze` lru_cache H-08; `rank_in_context`
  entegrasyonu H-10).
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
- **İstatistiksel disambiguation (Faz 2b, opt-in):** `statistical.py` — `parse_oflazer`
  (Artım-1 Oflazer→major_pos eşlemesi), `model_from_counts` (sayım→log-prob), `load_model`
  (gömülü TSV'den kompakt model), `rank_statistical` (çarpımsal/bağlamsız), `viterbi`
  (HMM Viterbi cümle-düzeyi). `analyze`/`disambiguation.rank`/`context.rank_in_context`
  DOKUNULMAZ. SPEC: `statistical-disambiguation-spec.md`.
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

## 7. Yol haritası ve DURUM (2026-07-14)

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
  - ✅ **İstatistiksel disambiguation katmanı** (`statistical.py`, SPEC `statistical-disambiguation-spec.md`):
    kural-tabanlı `context.py`'nin bağımsız istatistiksel muadili. Saf-Python, opt-in.
    - **Artım-1** (major POS, kaba): `parse_oflazer` (Oflazer→major_pos, son ^DB grubu), `rank_statistical`
      (çarpımsal emisyon skoru), `viterbi` (Viterbi HMM, cümle-düzeyi). Gömülü model: 31.190 emisyon +
      161 geçiş (TrMor2018, 34.673 cümle, 460.669 token). `model_from_counts`, `load_model` (TSV).
      TUZAK: Artım-1 viterbi recall-güvenli — yalniz sıra değiştir, aday budamaz.
    - **Artım-2** (tam eksen): `parse_oflazer_full` (tüm inflectional eksenler: tense/case/person/
      possessive/number/negative/voice/ptype), `_analysis_fine_state` (Analysis→ince-durum),
      `_fine_state_from_oflazer` (Oflazer→ince-durum). İnce-taneli HMM: "Verb:past"/"Noun:acc" vb.
      durumlar; gömülü model: 31.310 emisyon + **726 geçiş** (Artım-1'in 161'ine karşı 4.5×).
      Veri: `tools/build_disambig_model.py --fine`. TUZAK: nom varsayılan → kwargs'tan ATıLIR (golden
      da beklemeyi boş bırakmıştır, CLAUDE.md §4 genel kuralı).
    - Diferansiyel harness (`tools/diff_harness.py`): çarpımsal/HMM/kural/gold dört-yollu;
      ayrışma sınıfları: product_hmm_split/hmm_rule_split/gold_only/all_differ (SPEC §4).
    - İlk harness bulgusu: `üç gelin`, `kırmızı gül` → hmm_rule_split (HMM fiil seçerken kural isim;
      K1 doğru, HMM mini-geçiş görmemiş — SPEC §4'te beklenen kural açığı tespiti).
    - Golden: `tests/golden_statistical.py` (Artım-1, 49 durum) + `tests/golden_statistical_artim2.py`
      (Artım-2, eksen/ince-durum/cümle, 92 test). Her ikisi motor-körü kuruldu.
- **Faz 3** — sözcük-sınıfı genişleme:
  - ✅ **C1 Zamir çekimi** (`morphology_noun.py`, SPEC `spec/pronoun-spec.md`):
    **P1-P2** suppletif çoğul (`ben→biz`/`sen→siz`; `decline('ben',number='pl')` → `'biz'`),
    **P3-P8** n-gövde zamirleri (`hepsi/kendi/hiçbiri/birisi/biri/öteki/öbürü/hangisi/bazısı/çoğu/azı`;
    eğik durumda -n- kaynastrması: `hepsini/hepsine/…`; instrumental istisnası: `hepsiyle`).
    Round-trip otomatik (analysis-by-generation kapsar). 129 yeni golden test.
  - ✅ **C2 Sıfat morfolojisi** (`adjective.py`, SPEC `spec/adjective-spec.md`):
    **Pekiştirme** `intensify()` — ünlü-başlı algoritmik (`ap-`: apaçık, upuzun) +
    ünsüz-başlı kapalı tablo (`INTENSIFIER_PREFIX`: bembeyaz, kapkara, yepyeni, büsbüyük);
    **Küçültme** `diminutive()` — 3 ek: `-CIk` (kısacık/yavaşçık/küçücük; k-düşme), `-Imsı`
    (yeşilimsi/karamsı/mavimsi), `-Imtırak` (sarımtırak/yeşilmtirak). 53 yeni test.
    **`analyze()`** sıfat desteği — `Analysis(kind='intensify'|'diminutive', pos='adj')`;
    analysis-by-generation, roots-garantili precision. 28 analiz testi.
    **`tr.py`** — `yoğunlaştır()` + `küçült()` Türkçe sarmalayıcılar.
- **Faz 4 ✅** — sözdizimi üretim (`syntax.py`, `spec/syntax-spec.md`):
  - `isim_tamlamasi(tamlayan, tamlanan, tur='belirtili'|'belirtisiz')` —
    belirtili: `evin kapısı`, belirtisiz: `taş köprüsü`. gen+3sg-poss mekaniği.
  - `sifat_tamlamasi(sıfat, isim)` — `kırmızı araba` (kongruans yok).
  - `cumle_uret(ozne, yuklem, kip, olumsuz, soru)` — `ben geliyorum`, `o okudu`,
    `onlar gidecekler`; pro-drop Türkçe özneli, kip uyumu otomatik.
  - `zarf_yap(sıfat)` (`adjective.py`'e) — `-CA` eki: `güzelce`, `sıkça`, `hafifçe`.
  57 syntax + 15 zarf golden testi. Toplam: **3372 test**.

Test durumu: son ölçüm **4116 test yeşil** (slow hariç) + slow round-trip ayrıca `-m slow`.

- **Faz 5** — sözcük-sınıfı tamamlama (Faz 3 devamı; D turu):
  - ✅ **D1 Sayı morfolojisi** (`number.py`, SPEC `spec/number-spec.md`):
    - **Ordinal** `ordinal(kök)` — `-(I)ncI`: birinci/ikinci/üçüncü/dördüncü/onuncu; C daima c (n
      sonrası sedalılaşma yok); ünlü-final → baştaki I düşer (-nCI: ikinci); bileşik: son sözcük
      kuralı (`yirmi bir→yirmi birinci`); `_tr_lower` büyük harf güvenliği (I→ı, İ→i).
    - **Distributif** `distributive(kök)` — `-(ş)Ar`: birer/ikişer/dörder/altışar; ünlü-final→+şAr;
      ünsüz-final→+Ar; sedalılaşma YALNIZ `_VOICE_MAP={"t":"d"}` (dörder; üç/kırk sedalılaşmaz).
    - `_split_compound` DRY helper (bileşik bölme tek yerde); `_voice_final` boş-gövde guard.
    - **Çekim delegasyon:** `decline(ordinal("bir"), case="gen")` → `birincinin` — yeni morfoloji
      GEREKMEZ (isim motoru devralır). 7 durum × temsili ordinal, 0 çökme.
    - **TR API** (`tr.py`): `sıralı()` + `dağıtımlı()` sarmalayıcılar.
    - **Hakem bulguları giderildi:** `_tr_lower` HIGH (I→ı), LOW kapsam-dışı t-final SPEC notuna alındı.
    - 116 yeni test (26 ordinal + 24 distributif + 16 decline + 25×2 TR denklik).
    - Sırada: D2 edat/ilgeç yönetimi.

- **Faz 5** — sözcük-sınıfı tamamlama (Faz 3 D turu: sayı + edat; Faz 3 C = zamir+sıfat ✅):
  - ✅ **D1: Sayı morfolojisi** (`number.py`, SPEC `spec/number-spec.md`) — TAMAMLANDI (bkz. §7 Faz 5 ✅):
    - **Ordinal** `-IncI`: birinci/ikinci/üçüncü/dördüncü/… (I-uyumu + ünsüz sertleşmesi: dört→dördüncü).
      Sıfır istisnaları: bir→birinci (ünlü-final: birin+ci değil, birinci leksik); onar=onuncu değil onuncu.
    - **Distributif** `-şAr`: birer/ikişer/üçer/dörder/beşer/altışar/yedişer/sekizer/dokuzar/onar
      (allomorf: ünlü-final kök + şAr → r+şAr → ikişer; ünsüz-final → doğrudan şAr; kural tabanlı).
    - **Sayı çekimi**: ordinal/distributif biçimler `decline()` motoruna tam isim olarak girer
      (birincinin/birinciye/…) — yeni morfoloji GEREKMEZ (delegasyon, A3 emsali).
    - `tr.py` sarmalayıcı: `sıralı(n)`, `dağıtımlı(n)`. **İngilizce API**: `ordinal(n)`, `distributive(n)`.
    - Golden: bağımsız (motor-körü), elle-doğrulanmış ordinal (1-1000) + distributif + çekim örnekleri.
  - ✅ **D2: Edat/ilgeç yönetimi** (`postposition.py`, SPEC `spec/postposition-spec.md`):
    - 19 edat kapalı kümesi: `için`(nom/gen*), `ile`(nom/ins), `göre`(dat), `kadar`(dat), `karşı`(dat),
      `önce`(abl), `sonra`(abl), `rağmen`(dat), `doğru`(dat), `beri`(abl), `itibaren`(abl),
      `dek`(dat), `değin`(dat), `üzere`(nom), `başka`(abl), `dolayı`(abl), `ötürü`(abl),
      `gibi`(nom), `aşkın`(acc).
    - TUZAK — **`için` asimetrisi:** isimler yalın (nom) → `ev için`; kişi+n-gövde zamirleri
      (`ben/sen/o/biz/siz/bu/şu/hepsi/kendi/…`) genitif → `benim için`. `onlar+için` → nom (`onlar için`).
    - TUZAK — **`üzere` nom değil dat:** `ev üzere` doğru; `eve üzere` yanlış.
    - `postposition(lemma, edat, bitişik=False)` — `bitişik=True` yalnız `ile` (→ ins: `evle`, `okulla`);
      TUZAK: `okul+ins` → `okulla` (ünsüz-final -la, NOT -yla). Türkçe parametre adı Python 3 destekler.
    - Zamir entegrasyonu `decline()` delegasyonuyla (sıfır yeni morfoloji): `ben+göre→bana göre`.
    - `tr.py` sarmalayıcı: `edat_obeği(isim, edat, bitişik=False)`.
    - Golden: 86 giriş, bağımsız (motor-körü, Opus), 19 edat × ünsüz/ünlü/zamir.
    - Hakem bulgular giderildi: `için` nom/gen asimetrisi (CRITICAL) + `üzere` nom (MEDIUM).
  - ✅ **D2-devamı: Edat ÇÖZÜMLEMESİ** (2026-07-18, ertelenen açıldı; SPEC `spec/postposition-spec.md §7-§9`,
    tasarım `docs/superpowers/specs/2026-07-17-edat-analizi-design.md`, plan `docs/superpowers/plans/2026-07-17-edat-analizi.md`):
    - **Tek doğruluk kaynağı** `postposition._POSTPOSITIONS` (23 edat): `üret`/`üret_zamir`/`yönet`/`üretilebilir`.
      Üretim (`postposition()`), analiz (`_try_postposition_all`), K2 (`context._POSTP_GOV` TÜRETİLİR), PP (`parse.py`)
      hepsi buradan beslenir. Envanter 19→23 (donmuş dair/ilişkin/ait/yana eklendi).
    - **TUZAK — `yönet` elle yazılır, `üret`'ten TÜRETİLMEZ:** `ile`/`gibi`→{nom,gen}, `kadar`→{nom,gen,dat}
      zamir-genitifi korunmalı; tek-case `üret`'ten türetilirse K2 recall kırılır. Build-time drift-lock golden
      (`test_postp_gov_derived_preserves_current_keys`) mevcut 19 anahtarın daralmadığını sabitler.
    - **`_try_postposition_all`** (`analysis.py`): bağlaç deseninin aynası — closed-set, oracle-dışı, **additive**,
      `kind="postposition"` (`_KINDS` SONA), `pos="postp"`, `kwargs={}`, her zaman döner (roots-bağımsız).
      Belirsizlik kendiliğinden: `göre`=edat+görmek, `sonra`/`aşkın`/`başka` homograf.
    - **TUZAK — homograf sıralaması `_KIND_PRIOR`'a bağlı:** `postposition` `disambiguation._KIND_PRIOR`'da YOK
      (öncelik 0) → `aşkın`(=aşk+ın)/`başka` bare-noun `decline` (öncelik 2) tepede kalır. Drift-lock test kilitler.
    - **TUZAK — `analyze()` düz sözcük için `pos="adj"` ÜRETMEZ:** sıfat baskınlığı yalnız `parse._leaf_tag`
      leksikon-override'ında; `disambiguation.rank`'ta homograf tepe POS = `noun`.
    - **PP `governs`** (`parse.py`): `PhraseNode.governs: frozenset|None=None` (opsiyonel, varsayılan None →
      mevcut eşitlik testleri kırılmaz); R2 PP düğümüne `yönet` iliştirir (işaretle, ASLA reddetme — recall-güvenli).
      E5/E6 dependency/CoNLL-U `case` ilişkisini besler. Donmuş edat ADP kümesine eklendi (`buna dair` PP kurar).
    - **`postposition()` iki ValueError:** bilinmeyen edat (Geçerliler yalnız üretilebilir) vs donmuş edat
      (`'dair' donmuş bir edat`). Üretim çıktısı DEĞİŞMEZ (86-girdi golden yeşil).
    - Hakem: sweep 23 edat + 26k leksikon 0 çökme/0 miss; final adversarial (6 soru) SHIP. **4096 test yeşil** (+slow 2).
    - Kalan defer: olasılıksal dizi etiketleme (FST adopt-referans).
  - ✅ **İkileme adverbial-yeniden-kurulum** (SPEC/tasarım `docs/superpowers/specs/2026-07-18-ikileme-adverbial-design.md`,
    plan `docs/superpowers/plans/2026-07-18-ikileme-adverbial.md`): constituency parser ikilemeyi (tam `yavaş yavaş`
    + ulaç `koşa koşa`) tek **`AdvP`** öbeği olarak yeniden kurar; birleşik (multi-token) analizi HİÇ kullanmaz →
    token:analiz arayüz uyuşmazlığını atlar (asıl erteleme nedeni). Yeni yüzey-tabanlı kural **R8_redup**
    (`parse._apply_r8_redup`, R6_ki/R7_diye emsali): bitişik özdeş çift (`_tr_lower` İ/I-güvenli) + POS sınıflaması
    (VERB çifti → ulaç-tipi guard'sız; ADJ/NOUN çifti → tam-tipi). **TUZAK — NOUN-takip guard'ı:** tam-tipi çiftte
    sonraki token çıplak NOUN ise AdvP KURMA (adnominal `uzun uzun yollar` → `NP`); R8 R1'den ÖNCE çalışır → guard
    NOUN **yaprağını** kontrol eder, NP'yi değil (o an NP yok). VERB çifti guard'sız (adnominal olamaz). **TUZAK —
    `koşa` optatif eşsesli:** bare `-A` converb envanterde YOK (`nonfinite.CONVERBS`); `koşa` optatif çözülür →
    VERB etiketi; yüzey-çift + POS sınıflaması TEK uygulanabilir signal (oracle `roots` ister, parser'da yok).
    Pipeline R0'dan önce; R5 absorpsiyon kümesine `"AdvP"` (VP-içi tarz zarfı). **Dependency BEDAVA DEĞİL:**
    `dependency.py` açık dallar — `_child_deprel` VP/S dalı `("AdjP","AdvP")→advmod` (baş→fiil) + top-level
    `parent_tag=="AdvP"→compound:redup` (ikinci token→baş, UD-geçerli); `_find_head_leaf` AdvP dalı (`children[0]`=baş).
    m-ikileme kapsam DIŞI (nominal, defer). Hakem: sweep 7 cümle 0 çökme + adversarial APPROVE (0 CRITICAL/HIGH).
    **4102 test yeşil** (+6). Kapsam dışı (defer değil): üç+ *yineleme* (`yavaş yavaş yavaş`) gramatik ikileme
    DEĞİL, ifadesel/prozodik tekrardır (ikileme tanımı gereği İKİLİ — Korkmaz) → R8 ilk çifti yakalar, doğru.
    Kalan defer: koordine zarf (SPEC §5).
  - ✅ **m-İkileme nominal-yeniden-kurulum** (SPEC/tasarım `docs/superpowers/specs/2026-07-18-m-ikileme-nominal-design.md`,
    plan `docs/superpowers/plans/2026-07-18-m-ikileme-nominal.md`): AdvP'nin nominal kardeşi. Parser NOUN-tabanlı
    m-ikilemeyi (`kitap mitap`, `araba maraba`) tek **`NP`** öbeği olarak yeniden kurar (genelleyici/pekiştirici ad,
    özne/nesne rolü). Yeni yüzey-tabanlı kural **R9_mredup** (`parse._apply_r9_mredup`, R8 emsali): bitişik `a.tag=="NOUN"`
    + yüzey m-testi `m_reduplicate(_tr_lower(a.token))==la+" "+lb` → `NP(NOUN taban, MRED reduplikant)`. Pipeline R8'den
    sonra, R0/R1'den önce. **NP rolü BEDAVA** (kullanıcı kararı): NP olduğu için R1/R5 nominal argümanı doğrudan işler,
    ek entegrasyon YOK; `kitap mitap` yalın nom → özne konumu (`kitap aldı` emsali, indefinite-nom-nesne yapısal
    belirsizliği pre-existing SOV sınırı). **TUZAK — MRED iç etiketi:** reduplikant (`mitap`) parse-iç `MRED` etiketi
    alır (öbek dışına SIZMAZ, yalnız R9-NP içinde); `_find_head_leaf` en-sağdaki-NOUN mantığı tabanı zaten baş bulur
    (MRED≠NOUN), + fallback'te MRED atlama guard'ı (hakem HIGH sertleştirme, ADJ-taban geleceği için). **Dependency:**
    `_child_deprel` **top-level** `MRED→compound:redup` (parent NP/AdjP fark etmez); DepToken upos MRED için
    **taban(head) POS'undan MİRAS** (`base=all_leaves[head_id-1]; upos=base.tag`) → NOUN taban→NOUN, ADJ taban→ADJ;
    lemma/feats `_` analizsiz. **TUZAK — belirsizlik:** `adam madam` (madam gerçek sözcük) recall-güvenli m-ikilemeye
    toplanır (§3.2 bilinçli). Hakem: sweep 9 cümle 0 çökme + adversarial (0 CRITICAL; HIGH+MEDIUM giderildi).
    **V2 (2026-07-18) — ADJ-taban genişletme:** `a.tag in ("NOUN","ADJ")`; ADJ-taban (`güzel müzel`) → **`AdjP`**
    (adjectival, isim niteler: `güzel müzel elbise`→`NP(AdjP, elbise)`, R1 niteleyici alır). Reduplikant upos taban
    POS'undan miras (tek `MRED` etiketi iki tabanı da kapsar, iki tag GEREKMEZ) → `müzel`=ADJ, `mitap`=NOUN. `çocuk mocuk`
    (çocuk→ADJ quirk) artık AdjP kurar (semantik isim ama başıboş X yok; disambiguation açığı ayrı). Hakem V2: APPROVE
    (0 CRITICAL/HIGH/MEDIUM, 1 LOW ulaşılamaz fallback). **4110 test yeşil** (+3). m-ikileme doğası gereği İKİLİ
    (taban + m-biçim); "üçlü m-ikileme" YOK.
  - ✅ **Koordine ikileme/zarf** (R4 genelleme; AdvP tasarımı §5): CoordP kuralı **R4** artık yalnız `NP CCONJ NP`
    değil, **`_COORDINABLE=("NP","AdjP","AdvP")`** aynı-kategori koordinasyonu yapar → koordine zarf
    (`yavaş yavaş ve hızlı hızlı yürüdü` → `VP(CoordP(AdvP ve AdvP), yürüdü)`) + serbest koordine sıfat
    (`güzel müzel ve çirkin mirkin` → `CoordP(AdjP ve AdjP)`). `cat = ti if ti in _COORDINABLE else ("NP" if
    ti=="CoordP" else None)`; sağ konjunkt da `cat` olmalı (KARIŞIK `NP ve AdvP` koordine OLMAZ). Koordine-NP
    (`kitap ve kalem`, m-ikileme `kitap mitap ve kalem malem`) DEĞİŞMEZ. **Dependency:** `_child_deprel` parent
    CoordP conj seti `("NP","CoordP","AdjP","AdvP")`; VP/S'de child CoordP konjunkt-kategorisi AdvP/AdjP ise
    **`advmod`** (nominal case-based mantıktan ÖNCE), değilse eski nsubj/obj/obl. cc/conj→ilk konjunkt başı,
    compound:redup içeride (mevcut koord konvansiyonu). Hakem: APPROVE (0 CRITICAL/HIGH; MEDIUM+LOW
    ulaşılamaz/pre-existing). **4113 test yeşil** (+3).
  - ✅ **Koordine sıfat niteleyici + isim** (AdvP tasarımı §5): `kırmızı ve mavi araba` / `güzel müzel ve çirkin
    mirkin elbise` → `NP(CoordP(sıfatlar), isim)`. **TUZAK — R1<R4 sıralaması:** koordine sıfat niteleyici R4
    (R1-sonrası) ile çözülemez — R1 ikinci sıfatı isme kapar. Çözüm: **R1'den ÖNCE** çalışan yeni kural **R3c**
    (`_apply_r3c_adj_coord`, R3'ten sonra): `(ADJ|AdjP) (CCONJ (ADJ|AdjP))+ → CoordP` (karışık `çok güzel ve
    kırmızı` serbest). R1 modifier setine `CoordP` eklendi — **GÜVENLİ çünkü R1-zamanında CoordP yalnız R3c'den
    (sıfat)**; NP/AdvP CoordP R4'te (R1-sonrası) kurulur. Dependency: `_child_deprel` NP-child CoordP konjunkt-
    kategorisi ADJ/AdjP ise **`amod`**; CoordP conj setine `ADJ` eklendi. **Sözcük sırası attributive/predicative
    ayırır:** sıfat ÖNCE (`güzel ve sıcak hava`) → `NP(CoordP, isim)`; SONRA (`hava güzel ve sıcak`) → `S(NP, CoordP)`
    predicate (R1 yalnız sola bakar → guard GEREKMEZ). Tek-ADJ koordinasyonu (`kırmızı ve mavi`) da kapsandı.
    Hakem: 2 MEDIUM ikisi de geçersiz (biri yanlış-izleme = doğru predicate davranışı, biri pre-existing özel-isim
    tokenizasyonu, tetiklenmiyor). **4116 test yeşil** (+3).
  - ✅ **Koordine genitif tamlayan + özel-isim apostrof-ek yeniden kurulum** (2026-07-19; SPEC/tasarım
    `docs/superpowers/specs/2026-07-19-koordine-genitif-tamlayan-design.md`): `Ali'nin ve Veli'nin evi` →
    `NP(CoordP(Ali'nin ve Veli'nin), evi)`. İki bağımsız parça, parse katmanında (tokenizer + tokenize golden
    DEĞİŞMEZ — kullanıcı kararı). **B1 — özel-isim apostrof-ek merge (`_apply_r_proper`, EN BAŞTA):** tokenizer
    `Ali'nin`'i `["Ali","'nin"]` böler → ön-geçiş tek `NOUN[case]` yaprağına birleştirir. Yüzey tabanlı (apostrof
    kesin sinyal; leksikon ŞART DEĞİL — edat/bağlaç/diye emsali). **TUZAK — motor yumuşatır, imla yumuşatmaz:**
    `decline("Ahmet","gen")`→`Ahmedin` ama imla `Ahmet'in` → merged-surface oracle yumuşayan isimde KIRILIR →
    çözüm: `_classify_apostrophe_suffix` deterministik regex sınıflandırıcı (`_APOS_CASE_PATTERNS`, karşılıklı
    dışlayıcı anchored; ismi VERBATIM kullanır). Tam-bir eşleşme yoksa (len(hits)!=1) → merge yok (recall-güvenli;
    hakem 32 allomorf 0 çakışma doğruladı). **B2 — genitif tamlama genellemesi:** `_apply_r_gencoord` (R0'dan ÖNCE):
    `NOUN[gen] (CCONJ NOUN[gen])+ → CoordP` (her konjunkt NP'ye sarılı); **R0 GENELLEŞTİ:** possessor
    (`NOUN[gen]`|gen-CoordP) + head (`NOUN`|`NP`) → NP, **head poss-etiketi ŞART DEĞİL** (recall-güvenli — head
    poss/acc homografı `parse_text` rank_in_context UYGULAMADIĞI için acc sıralanabilir; Türkçede yalın genitif
    zorunlu possessed-head ister). Yan fayda: `adamın evi` basit tamlaması da düzeldi (önceden `evi`=acc → R0 fire
    etmiyordu). Common-noun koordinasyonu (`evin ve kapının rengi`) da BEDAVA çalışır. **Dependency:** `_child_deprel`
    NP-child CoordP konjunkt-kategorisi NP/NOUN + baş gen ise **`nmod:poss`** (amod dalının yanına); CoordP içi
    cc/conj mevcut. **Kapsam dışı (V1):** plural/iyelik+durum apostrof ekleri (`Ali'ler`, `Ali'sinin`); sıfat-araya-
    girmiş possessor (`adamın kırmızı arabası` — R0 R1'den önce, ADJ'ı geçemez; pre-existing genel parser sınırı);
    head poss feats disambiguation. Hakem: SHIP (0 CRITICAL/HIGH/MEDIUM; sweep 1540 çağrı 0 çökme). **4127 test yeşil** (+11).
  - ✅ **`-ki` aitlik eki ÇÖZÜMLEMESİ** (2026-07-19, yeni kind `with_ki`; SPEC `docs/superpowers/specs/2026-07-19-ki-aitlik-analizi-design.md`):
    üretim vardı (`morphology_noun.with_ki`) çözümleme yoktu (`evdeki`/`masadaki`→NO-REAL) → Faz 2b casina/ken
    "motor-dışı biçim çözümlemesi" deseni. `evdeki`→(ev,{case:loc}), `benimki`→(ben,{case:gen}),
    `içindeki`→(iç,{case:loc,possessive:3sg}), `bugünkü`→(bugün,{case:loc}). **Enumerate** (`_enumerate_ki`,
    candidates.py): marker `k[ıiuü]$` (değişmez -ki + Kİ_ROUND yuvarlak -kü) yoksa hiç enumerate etme;
    case∈{loc,gen}×possessive∈{None,3sg}=4 hipotez, oracle (`with_ki==surface`) doğrular. **Delegasyonlu
    segmentasyon** (`_segment_with_ki`, §6g emsali): decline tabanını `_segment_decline`'a ver + tek `ki` dilimi
    (`iç|i=3sg|nde=loc|ki`). **TUZAK — Kİ_ROUND 4x belirsizlik (hakem HIGH):** `with_ki` bugün/dün/gün/öbür'de
    case/possessive'i YOK SAYAR (donmuş -kü) → 4 hipotez de oracle geçerdi (çelişkili 4 analiz); `_enumerate_ki`
    stem∈Kİ_ROUND ise TEK hipotez (`case=loc`) üretir. **Kapsam dışı (V1):** stacked -ki (`dakileri`/`evdekinin`,
    ki-gövde yeniden çekimi), possessive≠3sg + çoğul; `_root_candidates` düşen-ünlü sınırı (`naklınki`, pre-existing).
    Wiring: `_KINDS`/`_KIND_FUNCS`/`_ENUMERATE_FN`/`_canon_ki`/`_raw_from_canon`/`_call_generator`/`_try_noun`
    (with_ki SONA). Golden 11+belirsizlik+negatif (Opus motor-körü). Hakem SHIP (1 HIGH giderildi; sweep 1000
    çağrı 0 çökme, 1 pre-existing düşen-ünlü miss). **4179 test yeşil** (+14).
  - ✅ **Türetilmiş gövde + çekim istifi** (2026-07-19; SPEC `docs/superpowers/specs/2026-07-19-turetme-cekim-istif-design.md`):
    saf çok-katman türetme zaten çalışıyordu (`gözlükçülük`), ama türetilmiş gövde ÇEKİM alamıyordu →
    `bencilliği`/`evsizliğini`/`bencilliklerinden` NO-REAL. `_try_derivation_inflected`: `_root_candidates`'ten ara
    türetilmiş gövde D (bencillik, leksikonda lemma değil ama aday kümesinde VAR) → D geçerli türetme (zinciri) ise ve
    `decline(D,infl)==surface` ise birleşik `kind="derivation"` Analysis (lemma=en-derin kök, chain=türetme katmanları,
    kwargs=türetme+çekim ekseni). Çift oracle (türetme + decline) → precision. A3 istifleme emsali. **TUZAK — GATE
    `max_derivation_depth>=2` (perf):** iç içe pass (~50 aday × türetme-BFS) her isim analizinde ~100-120ms'e mal olur;
    default depth=1 ETKİLENMEZ (saf çok-katman türetme de depth>=2 ister — opt-in). depth=1'de çalıştırılınca precision
    golden `gelin`/`okuyunca` bozuluyordu → gate şart. `_strip_one_layer`/`_strip_derivation`/`_template_to_allomorphs`
    lru_cache'lendi (98→66ms). **Kapsam dışı V1:** fiil-türevli çekim, çatı+türetme, `_root_candidates` düşen-ünlü.
    Golden 9 (Opus motor-körü; chain konvansiyonu uzlaştırıldı — motor: single→[], multi→ara-tabanlar). Hakem SHIP
    (0 CRITICAL/HIGH; cache güvenli+yanlış-pozitif yok doğrulandı; 1 MEDIUM perf dokümante, 2 LOW pre-existing).
    sweep 1196 çağrı 0 çökme 0 miss. **4187 test yeşil** (+8). NOT: tam-leksikon analyze ~165ms (`_try_adj_all`
    O(roots)) pre-existing perf borcu — bu feature'a özgü değil.
  - ✅ **İstatistiksel disambiguation COVERAGE artışı** (2026-07-19, `statistical.py`; bulgu+kararlar
    `docs/superpowers/specs/2026-07-19-statistical-eval-bulgular.md`): TrMor2018 gold değerlendirmesi
    (`tools/eval_statistical.py`) → HMM doğruluğu **%44.2→%74.8** (+30.6pt), coverage **%45.1→%80.7** (+35.6pt);
    TAMAMI saf-Python, CRF/dış-bağımlılık YOK, analyze() çekirdeği DEĞİŞMEDEN. Adımlar: (a) `_analysis_pos` pos-tabanlı
    eşleme (postp→Postp, conj→Conj…); (b) `_analysis_pos_lex` lexicon-aware refine + `viterbi(pos_fn=)`; full-POS
    roots (fonksiyon sözcükleri); `augment_function_candidates` çok-POS enjeksiyon (bir/çok/o → HMM bağlamla seçer);
    `augment_oov_candidates` OOV→Noun fallback. **CRF-gate KARARI: ERTELENDİ** (HMM covered'da tavana yakın; darboğaz
    dizi-modeli değil coverage). Hakem: 2 HIGH giderildi (her/hep zamir değil; Kİ_ROUND ayrı). Tüm eval opt-in.
  - ✅ **analyze() PERF ~48× (165→3.5ms/tam-leksikon)** (2026-07-19; üç davranış-korunumlu opt, hepsi
    diferansiyel-testle recall-güvence): **(1) `_try_adj_all` O(roots)→O(aday)** — her lemmayı taramak yerine
    yüzeyden ters aday (`_adj_root_candidates`: intensify PREPEND-only→lemma son-ek; diminutive APPEND-only+k-düşme→
    lemma ön-ek±restore-k), roots∩aday'da oracle (165→59ms; diff 1912 yüzey 0 uyuşmazlık). **(2) `_make_frozen`
    lambda+str elendi** — dict anahtarları benzersiz → `sorted(items)` aynı sıra (59→31ms). **(3) copula+conjugate
    enumerate person-ending prune** — person eki DAİMA en sonda + son-karakter person'a SABİT (copula: 1sg→m/2sg→n/
    1pl→kz/2pl→z/3pl→r hepsi dar; conjugate: yalnız 1sg→m/1pl→kmz/2pl→nz DAR, 2sg/3sg/3pl GENİŞ→prune yok);
    `question=False`'ta yüzey son-karakteri ailede değilse combo atlanır (`_COPULA_PERSON_LASTCHAR`/
    `_CONJ_PERSON_LASTCHAR`); question=True (mI son-ekli) MUAF (31→8→6.3ms). **TUZAK — recall-güvenlik person eki
    en-sonda + aile-tamlığı varsayımına bağlı:** copula 40k + conjugate 50k exhaustive diferansiyel 0 recall-miss;
    aileler morfoloji değişirse `test_copula_prune.py` yakalar (aile-varsayımını motor çıktısıyla sabitler).
    **(4) `_process_kind` verify-first** — raw_kwargs generator-hazır → canonicalize/dedup/raw_from_canon YALNIZ verify'ı
    geçen ~%1'de (545k→birkaç bin); 6.3→3.5ms. **Kümülatif 165→3.5ms ~48×**, test suite ~300→~40-120s.
  - ✅ **Çatı+türetme + disharmonik-düşme analizi + stacked -ki** (2026-07-19): (a-b) **çatı+türetme** (`_try_voice_derivation`, yazdırıcı) **+ çatı+fiilimsi** (`_try_voice_participle`, yazdırma/okutmak/yazdırdığı): voiced gövde `_voiced_stem_root` (conjugate/imp/voice_chain, lru_cache + `_in_voice_pass` re-entrancy guard + `_VOICE_STEM_MARKER` ön-filtre) + türetme/participle oracle; KÖK fiil + voice_chain. çatı+türetme:
    voiced verb gövdesi (yazdır, leksikonda yok) + fiil→isim leksik türetme (yazdırıcı=yaz+CAUS+-IcI); `_voiced_stem_root`
    conjugate/imp/voice_chain ile çözer + `derivations()` oracle; `_VOICE_STEM_MARKER` ([ıiuü][lnrşt]$) ön-filtre
    (re-entrant analyze perf: 5.1→3.56ms). Çatı+fiilimsi (-mA) kapsam DIŞI. (b) **disharmonik-düşme analizi** —
    `_root_candidates` CC-prefix'e 4 yüksek ünlü ekler (nakli→nakil). (c) **stacked -ki** `_try_ki_inflected`
    (evdekileri=evde+ki+ler+i; dış çekim birincil, `ki_case`/`ki_possessive` ekseni → case-çakışması yok). Hepsi roots-gate.
  - ✅ **morphology_noun kapsam** (2026-07-19): DROP_VOWEL +16 (omuz/zihin/…), FRONT_HARMONY +17 (nakil/kontrol/hayal/
    cemaat/…), SOFTEN_NO +2 (cemaat/sadakat), **BACK_HARMONY YENİ** (lütuf→lütfu/lütfa, ters-disharmonik: `_hsrc` back
    dalı sanal arka-ünlü, `back` bayrağı `_high`/`_low`/`_apply_*`'e threadli default False). Set-üyeliği lemma-özel
    → false-drop/false-front YOK; her ekleme TDK-doğrulandı + BACK/NEGATIVE kontrol grupları.
  - ✅ **Ünlü düşmesi kapsam genişletme** (2026-07-19, `morphology_noun.py`; SPEC `docs/superpowers/specs/2026-07-19-unlu-dusme-kapsam-design.md`):
    `DROP_VOWEL` eksikti (omuz→omuzu yanlış). `DROP_VOWEL` += 15 harmonik (omuz/zihin/ilim/beniz/hışım/kahır/kavis/
    kibir/kutur/nabız/remiz/sadır/şahıs/vecih/kayıt); `FRONT_HARMONY` += 4 disharmonik alıntı (nakil/haciz/kavim/kavis
    → nakli/haczi/kavmi/kavsi). **Set-üyeliği lemma-özel → false-drop imkânsız** (yalnız eklenen düşer; NEGATIVE
    kontrol grubu + full suite doğruladı). **TUZAK — lütuf ERTELENDİ:** ters-disharmonik (lütfu/lütfünü ARKA ama
    kalan ünlü ü ÖN; motor kalan-ünlüden lütfü üretir, back-harmony override mekanizması YOK). Harmonik düşme analiz
    roundtrip'i de düzeldi; **disharmonik-düşme ANALİZİ hâlâ kaçar** (`_root_candidates` harmonik ünlü-ekleme:
    nakl→nakıl/nakul, ön 'nakil' değil — pre-existing §6d sınırı; üretim DOĞRU). Golden 19 CASES+8 NEGATIVE (Opus
    motor-körü; ana oturum uzlaştırma: kavis disharmonik-front DOĞRU, lütuf ertelendi). **4229 test yeşil**.
  - ✅ **Ünlem + yansıma tanıma + red→reddi** (2026-07-20, 4339 test; SPEC `spec/interjection-onomatopoeia-spec.md`):
    Wikipedia "Türkçe dilbilgisi" navbox taksonomisi × kapsam haritası çıkarıldı → boşluk: ünlem/yansıma sözcük
    sınıfları `analyze()`'da tanınmıyordu. İki YENİ kapalı sözcük sınıfı — `interjection.py` (`INTERJECTIONS`: asıl
    ünlemler ah/of/eyvah/haydi/işte/bravo…) + `onomatopoeia.py` (`ONOMATOPOEIA`: asıl yansımalar şır/güm/çat/miyav…).
    `_try_interjection_all`/`_try_onomatopoeia_all` **conjunction/postposition deseninin AYNASI** (closed-set,
    oracle-DIŞI, **additive**, roots-bağımsız, `hypothetical=False`); `_POS` += ("ünlem","yansıma"), `_KINDS` +=
    ("interjection","onomatopoeia") SONA. `statistical._POS_TO_MAJOR` += {ünlem→Interj, yansıma→Noun (gömülü modelde
    Onom yok)}. İki küme AYRIK (drift-lock). Homograf sıralaması `_KIND_PRIOR`'da OLMAMASINA bağlı (öncelik 0 →
    of/ay/çat çekim/isim tepede). **Kapsam DIŞI V1** (bilinçli): ünlem→fiil (oflamak) + yansıma türetmesi (-TI şırıltı,
    -dA- şırıldamak) düzensiz-tabanlı+leksikon-dışı. Üretim YOK (donmuş) → tr.py sarmalayıcı yok, yalnız set export.
    **Ayrıca red→reddi:** `morphology_noun.DOUBLE` += "red" (ünsüz ikizleşme; TDK std "ret" ama "red" yaygın varyant;
    set-üyeliği lemma-özel → false-pos yok). Golden 45 (Opus motor-körü, additive `want⊆got`). Hakem APPROVE (0
    CRITICAL/HIGH/MEDIUM, 1 LOW docstring giderildi); sweep 3073 çağrı 0 çökme.
  - ✅ **Cümle çözümleme katmanı — öge etiketleme + cümle türü** (2026-07-20, 4417 test; SPEC
    `docs/superpowers/specs/2026-07-20-cumle-cozumleme-design.md`): YENİ modül `sentence.py`
    `analyze_sentence(text, roots)` → `SentenceAnalysis(elements, sentence_type)`. `parse.py`/
    `dependency.py`/`analyze()` DOKUNULMAZ, opt-in. **MİMARİ KARARI (ampirik):** öge grubu
    constituency ağacından DEĞİL, doğrudan **token-düzeyi en-iyi analiz + morfolojik durumdan**
    (parser yapısı kırılgan: özel-ad/çoğul→ADJ, özne yutulması, değil→VERB, mI düşer). **Öge
    etiketleri:** özne/yüklem/belirtili nesne(acc)/belirtisiz nesne(nom)/dolaylı tümleç(dat/loc/
    abl, alias 'yer tamlayıcısı')/zarf tümleci/edat tümleci/cümle dışı unsur. **Cümle türü 7 eksen:**
    yuklem_turu(fiil/isim), yuklem_yeri(kurallı/devrik), olumluluk, soru, kip(emir/istek/şart/
    gereklilik/haber), yapi(basit/birleşik/sıralı/bağlı), eksiltili. **Yüzey kapalı-set:** mI regex/
    değil/yok/edat(`_POSTPOSITIONS`)/bağlaç/demonstratif/derece sözcükleri (motor çözemez).
    **TUZAKLAR (hakem 2 HIGH giderildi):** (1) fiil-eşsesli ad özne (Kar/Yaz=ad+imperatif homograf)
    → gövde finit-fiil yalnız ANLATI zamanı/bağlaçla koordinat yüklem, imperatif homograf→özne
    (yanlış `sıralı` engellendi); (2) cümle-son olmayan mI → soru GLOBAL taramayla; (3) edat
    fiil-homografı (göre=gör-e) yüklem tespitinde atlanır; (4) modifier-zinciri derece-sözcüğüyle
    başlarsa zarf, yoksa son token isim başı (pos_map ali/çocuk=adj kuruntusu); (5) emir→yalın ad=hitap.
    **KULLANICI KARARI:** kanonik='dolaylı tümleç' (okul grameri), alias='yer tamlayıcısı' (§4 sapma).
    **Dokümante SINIR (§6):** proper-noun-adj homograf + SOV (Ali kitabı/Çocuk topu) öge idealini
    tutturamaz (özne kaybolabilir) → golden 2 vaka skip, TÜR yine tam; leksikon-POS/disambiguation
    kök nedeni, motor değişmeden iyileşir. **ÖGE 38/40 + TÜR 40/40** (golden 40 cümle, Opus motor-körü).
    Hakem WARNING→2 HIGH giderildi; sweep 6508 çağrı 0 çökme. `tr.cümle_çözümle`. **V2 (2026-07-20):**
    çoğul/iyelik özne kurtarma — niteleme sıfatı morfolojik ÇIPLAK, çekim eki (çoğul/iyelik) alan
    adj-etiketli token İSİMdir (`Çocuklar`→özne geri kazanıldı; `kırmızı araba` bozulmadı). Kalan
    sınır yalnız ÇIPLAK tekil homograf (Ali/Çocuk). **V2 TUR-2:** (a) zaman-adı zarf-değeri
    (`_TIME_NOUNS`+dat/loc/abl→zarf tümleci, akşama gittik; polysemik saat/sıra/son/ay DIŞLANDI);
    (b) kişi zamiri eğik biçim (`_PRONOUN_OBLIQUE`: bana/sana banmak/sanmak FİİL rank ediliyordu→zamir
    zorla); (c) cümle-başı pür ünlem (eyvah/haydi→cümle dışı; homograf of/ay/marş/yaşa HARİÇ); (d) edat
    birleştirme (Sabaha kadar, adjacency guard'lı); (e) yüklem tespiti 2-adım (top-rank fiil→devrik;
    yoksa en-sağ içerik token→Bana=banmak yüklem sanılmaz); (f) çok-cümle öge gate (özne/nesne
    heuristiği yalnız tek-cümlede; Ali geldi ve Veli gitti→Veli=özne). **TUZAK (hakem HIGH):**
    demonstratif (O/Bu MOD) eğik ZAMİRİ yutmamalı (O bana→özne+dolaylı, 'O bana' değil) → modifier
    zinciri pos=="pron" atlar. ÖGE 42/44 + TÜR 44/44. Hakem WARNING→1 HIGH+2 MEDIUM+1 LOW giderildi.
    4421→4431 test.
  - ✅ **CÜMLE KATMANI V3 — yargı bölme (clause segmentation)** (2026-07-20, 4449 test; SPEC
    `docs/superpowers/specs/2026-07-20-clause-segmentation-design.md`): `analyze_sentence` artık
    cümleyi yargılara böler + her yargının kendi öge çözümlemesini çıkarır. **ADDITIVE:** düz
    `elements` + `sentence_type` DEĞİŞMEZ (44 V1 golden kilitli); `SentenceAnalysis`'e yeni
    `clauses: tuple[Clause,...]=()` alanı. **Clause** = `(role, elements, predicate_id, connector)`
    (sade — kip/tür YOK, kullanıcı kararı). **Rol (SPEC §3):** yüklem fiilimsi/şart → `yan`;
    yan-olmayan yüklem ≥2 → her biri `bağımsız`; aksi (basit tek yargı / birleşiğin ana yargısı) →
    `temel`. **KAPSAM (kullanıcı kararı):** koordinat (bağlı/sıralı) + fiilimsi/şart yan cümle;
    ki/diye/iç-içe DEFER. **Mimari:** V1'in token-düzeyi yaklaşımı (parser'a güvenmez); `_label_body`
    EXTRACT edildi (düz yol + yargı yolu paylaşır → tek doğruluk kaynağı, davranış-korunumlu).
    **`_segment_clauses`:** yüklem-sınırı token akışını segmentler (ULAC/ORTAC/şart-FIIL/anlatı-FIIL/
    NOMPRED/pred_i); koordinat bağlaç (`_COORD_CONJ`) sonraki yargının connector'ı (öge DEĞİL);
    devrik kuyruk son yargıya iliştirilir; fiilimsi yüklem span'den çıkınca kendi sol tümlecini
    YUTMAZ (V1 flat'te tek zarf tümleci, yargıda dolaylı tümleç+yüklem AYRI). Yargı-içi özne/nesne
    heuristiği güvenli (tek yüklem → V2 çok-cümle gate'e gerek yok). **TUZAK — fiil-eşsesli ad özne
    (Kar/Yaz):** anlatı-dışı/şartsız/bağlaçsız FIIL sınır SAYILMAZ (V1 `_NARRATIVE_TENSES` gate).
    **Hakem SHIP** (0 CRITICAL/HIGH): MEDIUM giderildi — `_is_boundary`'ye NOMPRED dalı (copula-yüklem
    koordinasyonu `Hava güzeldi ve deniz sıcaktı`→2 bağımsız; çıplak nominal `güzel`=decline tespit
    edilemez → best-effort §6). Fiil-homografı under-segment (`…aldı…verdi`, verdi→noun-rank) V1
    `pred_i`'den miras pre-existing borç, V3-özgü değil. Golden 15 (Opus motor-körü; Yorulunca→Görünce
    swap: yorulmak edilgen-türev converb üretmiyor, pre-existing leksikon açığı). sweep 20 cümle 0 çökme.
  - ✅ **CÜMLE KATMANI V4 — ki/diye yan cümle bölme + çok-düzey zincir** (2026-07-20; SPEC §5b;
    kullanıcı kararı: ki+diye+zincir, gerçek gömme DEFER): V3 koordinat+fiilimsi/şart bölüyordu; leksik
    subordinatörler yargı-içi "cümle dışı unsur" kalıyordu. `_segment_clauses` yeniden yazıldı (`records`/
    `_rec_yan`/`_clause_pred`). **`ki` İLERİ** (temel ki yan): ki ÖNCESİ zorla sınır (nominal-yüklem homografı
    `Öyle yorgunum ki` için) + ki SONRASI subordine; **ki-domain** propagasyonu (ki'den sonra HER yargı yan:
    `Biliyorum ki gelince görecek`→temel+yan+yan). **`diye` GERİ** (yan diye temel): diye ÖNCESİ (d-1) zorla
    sınır → önceki yargı yan. ki/diye connector'a gider (öge değil), yüzey kapalı-set (`diye`=demek opt ama
    parser R6/R7 emsali yüzey tespiti). `_DEGREE_WORDS` += öyle/böyle/şöyle (tarz zarfı→zarf tümleci); `yapi`
    ki/diye markörüyle birleşik. **TUZAK — hakem HIGH giderildi:** bare/trailing subordinatör (`Bekledim diye`/
    `Biliyorum ki` sonrası boş) phantom `yüklem=diye` sızdırıyordu / ana yargıyı yan yapıyordu → (1) `ki` yalnız
    segment BAŞINDA subordine eder (trailing değil); (2) marker pred pozisyonunda ise `_clause_pred` kept'ten
    gerçek yüklem, kept boşsa yargı yok. Golden 7 (Opus motor-körü) + robustluk testi; V3 golden DEĞİŞMEZ.
    sweep 27 cümle 0 çökme. Tam paket 4484 yeşil.
  - ✅ **CÜMLE KATMANI V5 — gerçek gömme (aktarma + adlaşmış)** (2026-07-20; SPEC §5c; kullanıcı kararı):
    gömülü tümce = ana yargının argümanı. **Adlaşmış ZATEN çalışıyordu** (-DIK/-mA participle→ORTAC→V3
    fiilimsi yan: `Ali geldiğini biliyorum`→yan+temel) → golden kilidi eklendi, YENİ KOD YOK. **Aktarma
    YENİ:** gömülü FİNİT tümce + bildirme fiili. `_REPORTING_VERBS` kapalı-set (demek/sanmak/zannetmek/
    söylemek/düşünmek/ummak/sormak); ana yüklem reporting fiili VE öncesinde FİNİT tümce (FIIL/ULAC/ORTAC)
    → reporting'ten önce zorla sınır + önceki (koordinat-bağlanmamış) yargı forced_yan gömülü.
    `Yağmur yağacak sandı`→yan+temel, `Gel dedi`→yan+temel. **TUZAK — guard:** `Ali bir şey söyledi`
    (NESNE NP, finit tümce YOK) gömme DEĞİL → "öncesinde finit" guard'ı şart (yoksa nesne NP gömülü sanılır).
    Ayrıca **yapi artık clauses'ten türer** (any yan→birleşik; ki/diye/aktarma tutarlı) + **rol guard**
    `_rec_yan and non_yan>=1` (tek şart `Gelsen`→temel §3). **Kapsam DIŞI:** homograf-finit gömülü yüklem
    (`Yarın geleceğim dedi`, geleceğim=isim rank), tırnak-tabanlı aktarma, koordine-içi gömme (§5c defer).
    **Hakem SHIP** (0 CRITICAL/HIGH/MEDIUM; 1 LOW koordine-içi-aktarma defer). Golden 8 (Opus motor-körü;
    Hasta olduğunu→özne uzlaştırıldı, ad-tümleç belirsiz edge). sweep 35 cümle 0 çökme. Tam paket 4492 yeşil.
  - ✅ **Çıplak-tekil ad tanıma (Ali/Çocuk) — küratlü kapalı-set override** (2026-07-20; kullanıcı
    kararı: veri-rebuild/heuristik DEĞİL, küratlü set): SPEC §6 sınırı (leksikon Zemberek-collapse
    `çocuk`/`ali`'yi 'adj' etiketler → çekimsiz-çıplak token modifier zincirine yutulur, ÖZNE kaybolur).
    `sentence.py` iki kapalı-set + `_classify` `_MOD_POS` guard: **(a) `_PERSON_NAMES`** (~90 kişi adı,
    BÜYÜK-HARF gate'li özel ad — gerçek sıfat olamaz; `ali`=yüce homografı geçersiz) → `Ali kitabı
    okudu`=özne(Ali)+belirtili nesne(kitabı) ✓; **(b) `_NOUN_OVERRIDE`** ad-baskın somut ad (çocuk/memur,
    KONSERVATİF — çift-kullanım genç/ihtiyar/düşman DIŞLANDI: `İhtiyar adam` bozulmaz). `Kırmızı araba`
    (gerçek sıfat, sette yok) + `Küçük çocuk` (çocuk=AD baş) bozulmaz. **`Ali kitabı okudu` skip'ten
    çıktı** (tam geçiyor); `Çocuk topu…` özne kurtuldu ama `topu`→'topu' nom lemması→belirtisiz (AYRI
    nom/acc disambiguation borcu, çocuk=adj değil; golden 1 skip kaldı). Regresyon-kilidi test_bare_noun_override.
  - ✅ **Kural-tabanlı özel-ad etiketleme (proper-noun tagging)** (2026-07-20; SPEC
    `docs/superpowers/specs/2026-07-20-proper-noun-tagging-design.md`; kullanıcı kararı — **NER DEĞİL**):
    mimari-kararlar NER'i kalıcı kapsam-dışı ilan etmişti (ML/treebank); bu KURAL-TABANLI muadil (kapalı-set
    gazetteer + Türkçe imla). YENİ `proper_noun.py`: `PERSON_NAMES`(~90)/`PLACE_NAMES`(81 il+ülke+coğrafya)/
    `ORG_NAMES` gazetteer + `_NEVER_PROPER` (işlev/belgisiz sözcük); `proper_type(surface, sentence_initial,
    is_common)→PER|LOC|ORG|PROPER|None`; `tag(text, roots)→list[ProperNoun]`. **Kural sırası:** _NEVER_PROPER→
    None; **büyük-harf ZORUNLU** (küçük-harf hiçbir kural tetiklemez); gazetteer(büyük-harf); apostrof-ek→PROPER;
    cümle-içi caps→PROPER; cümle-başı caps + analyze()-danışması (gerçek çözümleme→ortak ad, OOV→PROPER).
    **TUZAK — hakem HIGH:** gazetteer büyük-harf gate'i ŞART (deniz/gül/kaya 63 küçük-harf ortak lemma yanlış
    etiketleniyordu). **TUZAK — cümle-başı çekimli ortak** (Onu=o+acc lemma-kümesinde yok) → analyze() danışması
    ("analyze entegrasyonu"); `_NEVER_PROPER` (bu/o/ne/kimi/herkes…) açık liste (analyze hypothetical kaçağı).
    **sentence.py entegrasyon:** `_PERSON_NAMES` proper_noun'a TAŞINDI (tek kaynak); `_classify` çıplak-tekil
    override LOC/ORG'a genişledi (İstanbul→özne). Element'e TÜR alanı EKLENMEDİ. `tr.özel_adlar`. **Hakem
    SHIP** (HIGH+MEDIUM giderildi, LOW apostrof-edge belgeli). Golden 21 + FP sweep 3000 ortak ad **küçük-harf
    %0.00 / cümle-başı %0.03** (1 çöp girdi) 0 çökme. Kimlik uyumu: saf-Python, ML YOK. Tam paket 4525 yeşil.
  - ✅ **Disambiguation homograf çekimli-üstünlük düzeltmesi** (2026-07-20; SPEC
    `docs/superpowers/specs/2026-07-20-homograph-inflected-correction-design.md`): freq'siz rank'te
    morfem-ekonomisi rare **bare-lemma**'yı (verdi/girdi=leksikon-çöpü ad) çok-sık **net-fiil** okumaya
    (vermek/girmek past) tercih ediyordu → yüklem tespiti + yargı bölme yanlış (`…aldı…verdi` tek yargı).
    **`disambiguation.rank(prefer_inflected=False)` YENİ opt-in param** (default BİREBİR aynı — statistical/
    lemmatize/context DOKUNULMAZ): True → base FREQ'SİZ+POS'SUZ (eski `_rank(real)`) + hedefli düzeltme:
    bare-decline en-iyi, **DAR rakip** (yalnız `conjugate` tense∈{past,evid,pres,fut}, voice_chain yok)
    çok daha sıksa (≥2× + taban 1000) → fiili seç. `sentence.py::_best_per_token` freq + prefer_inflected=True.
    **TUZAK — HAKEM HIGH: acc-isim dalı ÇIKARILDI.** İlk tasarım `decline case=='acc'` rakibini de içeriyordu
    (topu→top:acc); adversarial geniş tarama (top-2000 ad) sistematik yanlış-flip buldu: `-CI` sonlu gerçek
    adlar/sıfatlar (yarı→yar:acc, arı→ar:acc, salı/koyu/sıkı/dişi/birileri…) kısa-stem freq'iyle deviriliyordu;
    `topu`(pron) ile `yarı`(noun) POS'la ayrılamıyor → acc-dalı güvensiz, çıkarıldı. Kayıp: topu→top:acc YOK
    (Çocuk topu golden skip kaldı). Korunan yüksek-değer: verdi/girdi/çıktı→net-fiil (segmentasyon + yüklem).
    imperatif/aorist/gen/poss zaten HARİÇ (yazar/yarın korunur). Test `test_homograph_correction.py`; base
    freq'siz+pos'suz → 44 cümle golden `elements` DEĞİŞMEZ. Tam paket 4476 yeşil.
  - ✅ **Bağlam-tabanlı acc-nesne homografı (context K6)** (2026-07-20; SPEC
    `docs/superpowers/specs/2026-07-20-context-acc-object-homograph-design.md`): izole homograf
    düzeltmesinde acc-dalı çıkarılmıştı (yarı/arı bozuyordu); `topu`(top:acc nesne) izole ayırt
    edilemez → **bağlam** gerekir. `context.py` K6: `_ACC_OBJECT_PRON` CURATED set (`{"topu"}`,
    genişletilebilir; birileri/kimi/hepsi DIŞLANDI — bare-baskın/rakipsiz), `_k6` kuralı — token sette
    VE nesne bağlamı (önünde fiil-olmayan içerik token + cümlede finit fiil) → acc'e +kanıt, nom'a −kanıt.
    Recall-güvenli (BUDAMAZ). **sentence.py wiring:** `_best_per_token` YALNIZ curated-set tokenda
    context re-rank (**freqless tiebreak** → K6 belirleyici, freq base'i her yerde acc yapmaz); diğer token
    izole `prefer_inflected` (44 golden ETKİLENMEZ). **TUZAK — Çocuk=diminutive:çok** izole mis-analiz →
    has_prev_nom "_NOMINAL_KINDS" yerine "fiil-olmayan içerik token" (dayanıklı). **TUZAK — freqless
    sentence-LOCAL** (hakem MEDIUM): rank_in_context(freq=) tüketiciler (lemmatize) topu→top:acc'i izole
    freq'le çözer (K6 değil, pre-existing). `Çocuk topu bahçede oynadı`→belirtili nesne (**son golden skip
    kalktı**). Hakem SHIP (0 CRITICAL/HIGH; MEDIUM SPEC-notu, LOW drift-lock+perf). Test `test_context_k6.py`
    (drift-lock: set={topu}). Tam paket 4533 yeşil.
  - ✅ **D3: Sayı çözümlemesi** (`analysis.py` genişletme):
    - `analyze()` → yeni kind'lar: `ordinal` (birinci→bir), `distributive` (ikişer→iki).
    - `_NUMBER_SIMPLE_ROOTS` kapalı küme (24 kök) precision garantisi; oracle analysis-by-generation.
    - Bileşik sayı yüzeyleri (`yirmi birinci`) çok-token dalında `_try_number_all` önce çalışır.
    - `roots` filtresi doğru çalışır (`roots is not None and root not in roots → atla`).
    - Golden: 24 giriş, bağımsız (motor-körü, Opus): ordinal 1-10+2 bileşik, distributif 1-10+2 bileşik.
  - ✅ **D4: Bağlaç morfolojisi** (`conjunction.py`, SPEC `spec/conjunction-spec.md`) — TAMAMLANDI:
    - `turkgram/conjunction.py` — `conjoin(word, conj)` (de/da ses uyumu; ise ayrı yazılır, harmoni yok;
      fallback `_last_vowel()==None → "de"`; korelatif anahtar → ValueError), `coordinate(items, conj)`
      (ikili/üçlü/korelatif; boş→ValueError, tek→aynen; korelatifler yalnız 2 öğe:
      `hem_hem`/`ya_ya`/`ne_ne`/`ister_ister`/`gerek_gerek`/`hem_hem_de`).
    - `analyze()` genişletme — `_try_conjunction_all()` oracle-dışı kapalı-liste dalı: `"de"/"da"` tam-token
      → `kind="conjunction"`, `pos="conj"`. `_KINDS`'a `"conjunction"` (SONA), `_POS`'a `"conj"` eklendi.
      TUZAK: `analyze("de")` **bilinçli belirsizlik** — hem bağlaç hem `demek` imp-2sg; disambiguation sıralar.
    - TR API: `bağla(kelime, bağlaç)` / `koordine_et(ögeler, bağlaç)` (`sıralı()` ile çakışmaması için).
      `_BAĞLAÇ`: `"de"`/`"da"` ayrı anahtar; korelatif Türkçe boşluklu → alt-çizgili iç anahtar.
    - 70 yeni test; Hakem: 52.458 korpus çağrısı 0 çökme.

- **Faz 6 ✅** — yapım eki (türetme) analizi (`analysis.py`, SPEC `docs/superpowers/specs/2026-07-16-faz6-derivasyon-design.md`):
  - **Tek-katman leksik türetme analizi** — oracle analysis-by-generation; fiilimsi + çatı DIŞLI.
  - `_LEXICAL_SUFFIXES` + `_DERIVED_POS` (`derivation.py`): 27 suffix (isim→isim 8, isim→fiil 8,
    fiil→isim 11); her eleman (category, label, src_pos) üçlüsü. `-Ar-` çakışması (category, label)
    çiftiyle çözüldü: `("isim → fiil", "-Ar-")` DAHİL, `("fiil → fiil (çatı)", "-Ar- (ettirgen)")` DIŞLI.
    `_DERIVED_POS` → adj (−lI/−sIz/−CIl/−CA/−IcI/−gAn/−Ik/−gIn), noun (geri kalan isim çıktıları),
    verb (isim→fiil tüm).
  - `_template_to_allomorphs(template)` + `_strip_derivation(surface, label, src_pos)` (`analysis.py`):
    arşifonem şablonu → tüm olası biçimler (itertools.product); ters suffix soyma + kaynaştırma-y geri alma.
    Fiil çıktılı suffix (isim→fiil): yüzeyde -mAk sonekini soy → gövde. TUZAK — **fiil→isim gövde vs mastar:**
    `_strip_derivation` çıplak gövde döner (seç); `_try_derivation_all` mastarı yeniden kurar:
    `stem + "m" + low_vowel(stem) + "k"` → `seçmek` (oracle + `Analysis.lemma` için).
  - `_try_derivation_all(surface, analyses, seen, roots)` (`analysis.py`): `_KINDS`'ta `"derivation"` bağlaç
    sonrası (çekim önceliklenir; NOT: `"postposition"` edat analiziyle en sona eklendi). `analyze()` pos∈{None,noun,verb,adj} guard.
    §8.1 precision: `roots is not None and lemma not in roots → atla`; `hypothetical = (roots is None)`.
    Segments: `_segs_to_tuple([(stem, "kök"), (suffix_surf, label)])`.
  - 35 yeni test (32 golden + 3 davranış); Golden: 32 giriş (31 suffix + 1 ek), bağımsız (motor-körü, Opus),
    tüm 27 suffix kapsandı. Hakem: 500 leksikon lemması × isim+fiil = ~14k biçim, **0 çökme, 0 genuine miss**.
  - TUZAK — zincirli türetme kapsam dışı (tek katman): `gözlükçü` (göz→gözlük→gözlükçü) çözülmez — bilinçli sınır.

Yeni dosyalar (2026-07-16, Faz 6 yapım eki analizi):
- `docs/superpowers/specs/2026-07-16-faz6-derivasyon-design.md` — onaylı tasarım dokümanı
- `docs/superpowers/plans/2026-07-16-faz6-derivasyon-analizi.md` — implementasyon planı
- `turkgram/derivation.py` — `_LEXICAL_SUFFIXES`, `_DERIVED_POS` eklendi
- `turkgram/analysis.py` — `_template_to_allomorphs`, `_strip_derivation`, `_try_derivation_all` eklendi;
  `_KINDS`'a `"derivation"` (sona); `analyze()` entegrasyonu
- `tests/golden_derivation_analysis.py` — 32-girdi bağımsız golden (motor-körü, Opus)
- `tests/test_derivation_analysis.py` — runner (35 test)
- `tools/sweep_derivation_analysis.py` — korpus tarama aracı

Yeni dosyalar (2026-07-16, Faz 5 D4 bağlaç morfolojisi):
- `spec/conjunction-spec.md` — SPEC (kapalı küme, de/da uyumu, korelatifler, analyze tuzakları)
- `turkgram/conjunction.py` — `conjoin()`, `coordinate()`, `CONJUNCTIONS`, `_VALID_CONJ`
- `turkgram/__init__.py` — `conjunction`, `conjoin`, `coordinate`, `CONJUNCTIONS` export eklendi
- `turkgram/tr.py` — `bağla()`, `koordine_et()`, `_BAĞLAÇ` eklendi
- `turkgram/analysis.py` — `_try_conjunction_all()`, `_KINDS`+`"conjunction"`, `_POS`+`"conj"` eklendi
- `tests/golden_conjunction.py` — 104-satır bağımsız golden (motor-körü, Opus)
- `tests/test_conjunction.py` — runner (70 test)
- `docs/superpowers/specs/2026-07-16-conjunction-design.md` — onaylı tasarım dokümanı
- `docs/superpowers/plans/2026-07-16-faz5-d4-baglac-morfolojisi.md` — implementasyon planı

Yeni dosyalar (2026-07-16, Faz 5 D2 edat yönetimi + D3 sayı çözümlemesi):
- `spec/postposition-spec.md` — 19 edat SPEC (için asimetrisi, bitişik ile, üzere nom)
- `turkgram/postposition.py` — `postposition()`, `_ICIN_GEN_PRONOUNS`, `_POSTPOSITION_CASE`
- `turkgram/__init__.py` — `postposition` eklendi
- `turkgram/tr.py` — `edat_obeği()` sarmalayıcı eklendi
- `tests/golden_postposition.py` — 86-girdi bağımsız golden (motor-körü, Opus)
- `tests/test_postposition.py` — runner (86 test + ValueError + TR denklik)
- `turkgram/analysis.py` — `_try_number_all()`, `_NUMBER_SIMPLE_ROOTS`, ordinal/distributive kind desteği
- `tests/golden_number_analysis.py` — 24-girdi bağımsız golden (motor-körü, Opus)
- `tests/test_number_analysis.py` — runner (24 test)
- `docs/superpowers/plans/2026-07-16-faz5-d2-edat-yonetimi.md` — implementasyon planı

Yeni dosyalar (2026-07-16, Faz 5 D1 sayı morfolojisi):
- `spec/number-spec.md` — ordinal + distributif SPEC
- `turkgram/number.py` — `ordinal()`, `distributive()`, `_tr_lower`, `_split_compound`, `_voice_final`, `_VOICE_MAP`
- `tests/golden_number.py` — 66-girdi bağımsız golden (26 ordinal + 24 distributif + 16 decline; motor-körü, Opus)
- `tests/test_number.py` — runner (116 test: parametrik + TR denklik)
- `docs/superpowers/plans/2026-07-16-faz5-sayi-morfolojisi.md` — implementasyon planı

Yeni dosyalar (2026-07-14):
- `turkgram/statistical.py` — istatistiksel disambiguation motoru (Art.-1 + Art.-2)
  `parse_oflazer`, `parse_oflazer_full`, `_analysis_fine_state`, `_fine_state_from_oflazer`,
  `load_model`, `rank_statistical`, `viterbi`, `model_from_counts`
- `turkgram/data/disambig_emission_tr.tsv` — TrMor2018'den 31.190 emisyon log-prob [Art.-1]
- `turkgram/data/disambig_transition_tr.tsv` — 161 geçiş log-prob [Art.-1]
- `turkgram/data/disambig_emission_fine_tr.tsv` — 31.310 ince emisyon [Art.-2]
- `turkgram/data/disambig_transition_fine_tr.tsv` — 726 ince geçiş [Art.-2]
- `tools/build_disambig_model.py` — TrMor2018 → kompakt TSV (Artım-1); `--fine` ile Artım-2
- `tools/diff_harness.py` — dört-yollu diferansiyel harness (geliştirme aracı)
- `tests/golden_statistical.py` — Art.-1 bağımsız golden (eşleme/sayım/Viterbi, 49 test)
- `tests/test_statistical.py` — Art.-1 runner (49 test)
- `tests/golden_statistical_artim2.py` — Art.-2 bağımsız golden (eksen/ince-durum/cümle)
- `tests/test_statistical_artim2.py` — Art.-2 runner (92 test)

Yeni dosyalar (2026-07-14, Faz 3 C1 zamir):
- `spec/pronoun-spec.md` — zamir morfolojisi SPEC (P1-P8: suppletif çoğul + n-gövde zamirleri)
- `turkgram/morphology_noun.py` — `_PLURAL_SUPPLETION`, `_N_STEM_PRONOUNS`, `_decline_n_stem_pronoun`
  eklendi; `decline()` suppletif çoğul + n-gövde dalı eklendi
- `tests/golden_pronoun.py` — 129-girdi bağımsız golden (motordan bağımsız, elle-doğrulanmış)
- `tests/test_pronoun.py` — runner (129 test)

Yeni dosyalar (2026-07-14, Faz 3 C2 sıfat):
- `spec/adjective-spec.md` — sıfat morfolojisi SPEC (pekiştirme + küçültme)
- `turkgram/adjective.py` — `intensify()`, `diminutive()`, `INTENSIFIER_PREFIX`
- `tests/golden_adjective.py` — 53-girdi bağımsız golden
- `tests/test_adjective.py` — runner (53 test)

Yeni dosyalar (2026-07-14, Faz 3 C2 sıfat analiz):
- `turkgram/analysis.py` — `_try_adj_all()` + `pos='adj'` desteği eklendi
- `turkgram/tr.py` — `yoğunlaştır()`, `küçült()` Türkçe sarmalayıcılar + `_EK_TRLESTIR` eklendi
- `tests/golden_adjective_analysis.py` — 28-girdi bağımsız analiz golden
- `tests/test_adjective_analysis.py` — runner (28 test)

Yeni dosyalar (2026-07-16, parse_text + tokenizer):
- `docs/superpowers/specs/2026-07-16-parse-text-tokenizer-design.md` — onaylı tasarım dokümanı
- `docs/superpowers/plans/2026-07-16-parse-text-tokenizer.md` — implementasyon planı
- `turkgram/tokenize.py` — `tokenize(text) → list[str]`: boşluk+noktalama+apostrof; kıvrık apostrof bölünmez
- `turkgram/analysis.py` — `_cached_analyze` (lru_cache 4096) + `parse_text` eklendi
- `turkgram/__init__.py` — `tokenize` + `parse_text` export eklendi
- `tests/golden_tokenize.py` — 26-girdi bağımsız golden (motor-körü, elle-doğrulanmış)
- `tests/test_tokenize.py` — runner (26 test)
- `tests/test_parse_text.py` — parse_text davranış + H-10 entegrasyon testleri (9 test)

- **Faz 9 ✅** — hecelemleme + vurgu (`turkgram/syllabify.py`):
  - **`syllabify(word) → list[str]`** — O(n) ünlü-tabanlı hece sınır tespiti; kural kümesi:
    V·CV (birer ünsüz sağa), VC·CV (iki ünsüz ortadan), VCC·CV (üçlü: ilk ikisi sola) +
    **`_VALID_ONSETS`** frozenset'i ile maksimal onset (yabancı küme: `tr`/`kr`/`pr`/`kl` vb.)
    → `elektrik→["e","lek","trik"]`, `kontrol→["kon","trol"]`. Bitişik ünlü → V·V.
    Circumflex dahil: â/î/û `_VOWELS` kümesinde (kâtip→["kâ","tip"]).
  - **`stress(word) → int | None`** — 0-tabanlı vurgulu hece indeksi (baştan); varsayılan son
    hece; `_STRESS_EXCEPTIONS` elle küratörlenmiş 31 giriş (şehir adları + alıntılar):
    `ankara→0`, `istanbul→1` (is·TAN·bul), `stres→0`, `klima→1`. Boş string → `None`.
  - **`stress_mark(word) → str`** — vurgulu heceyi Türkçe-duyarlı büyük harfle işaretle
    (`_tr_upper`: i→İ, ı→I; Python `str.upper()` değil); U+00B7 orta nokta ayıracı:
    `geldi→"gel·Dİ"`, `ankara→"AN·ka·ra"`, `istanbul→"is·TAN·bul"`.
  - `turkgram.tr`: `hecele()` / `vurgu()` / `vurgu_işaretle()` sarmalayıcılar.
  - Hakem: 26.229 leksikon lemması + 31 istisna, 0 çökme.
  - 101 yeni test (50 syllabify + 39 stress_mark + 12 TR denklik/edge); **toplam: 3825 test**.
- **Faz 9d ✅** — ikileme (reduplication) (`turkgram/reduplication.py`, SPEC `docs/superpowers/specs/2026-07-17-reduplication-design.md`):
  - **Üç tür:** tam ikileme (`yavaş yavaş`), -A ulaç ikilemesi (`koşa koşa`), m-ikileme (`kitap mitap`).
  - **`full_reduplicate(word)`** — sözcük tekrarı; her POS geçerli; boş → ValueError.
  - **`converb_reduplicate(lemma)`** — fiil mastarından -A ulaç biçimi × 2; `_a_converb` iç yardımcısı
    `_stem_before_suffix` + `low_vowel` kullanır (`converb(lemma,"optative")` MEVCUT DEĞİL). ye_de +
    glide-y ünlü-final: gitmek→gide gide, yemek→yiye yiye, okumak→okuya okuya.
  - **`m_reduplicate(word)`** — ünsüz-final: ilk ünsüz→m (kitap→mitap); ünlü-final: başa m (araba→maraba);
    m-başlı sözcük → ValueError (p-ikileme kapsam dışı).
  - **Türkçe API** (`tr.py`): `tam_ikile()` / `ulaç_ikile()` / `m_ikile()`; `_tr_lower` normalizasyonu.
  - **Analiz entegrasyonu** (`analysis.py`, `_analyze_multi_token`): 3 yeni kind —
    `reduplication_full` / `reduplication_converb` / `reduplication_m`. `_try_reduplication_all`
    `_KINDS` zincirinden değil, `_analyze_multi_token`'dan çağrılır (tüm türler çift-token yüzey).
    TUZAK — **`reduplication_converb` `roots=None` → analizi YOK:** kök listesi olmadan -A biçiminden
    fiil mastarı kurtarılamaz. `roots` sağlanırsa tüm köklerde `converb_reduplicate(lemma)==surface`
    oracle denenır. `güle güle` belirsizliği: `güle` roots'ta varsa hem `reduplication_full` hem
    `reduplication_converb`; yoksa yalnız converb.
    TUZAK — **POS gürültü modu:** `_cached_analyze(token1, roots=None)` full/m için pos tespitinde
    kullanılır; gürültü modunda her zaman "verb" döner → test golden'ı `pos=None` kullanır (pos
    doğrulaması atlanır). Converb'de `pos="verb"` sabit (hardcoded).
  - Hakem: 26.229 lemma × full/m + 3.220 fiil × converb = 0 çökme.
  - 97 yeni test; **toplam: 4015 test**.

- **Faz 9b ✅** — yazım denetimi (`turkgram/spellcheck.py`, SPEC `docs/superpowers/specs/2026-07-16-spellcheck-design.md`):
  - **`is_valid(word, *, roots=None)`** — morfoloji tabanlı geçerlilik: `analyze()` + `lexicon.load()`
    (opt-in semantik inversiyonu: `roots=None` → leksikon, `analyze`'ın gürültü modunun TERSİ).
    Agglütinatif biçimler tam kapsanır; DoS koruması 200 karakter.
  - **`_BKTree`** iç sınıfı — metric-space indeks; `_frozen` kilidi (`lru_cache` singleton güvenliği;
    `build()` sonrası `_insert()` `RuntimeError` fırlatır). ×2 tam-sayı ölçekleme (0.5 mesafe float-safe).
  - **`_tr_distance(a, b) → float`** — Türkçe-ağırlıklı Levenshtein: 6 konfüzyon çifti
    (ı↔i / ö↔o / ü↔u / ş↔s / ç↔c / ğ↔g) maliyet 0.5; `_TR_PAIRS: frozenset[frozenset[str]]` O(1) simetrik.
  - **`suggest(word, *, roots=None, max_suggestions=5, max_distance=2.0)`** — V1: **kök (lemma)**
    döner (`"seker"→["şeker"]`, `"gozluk"→["gözlük"]`); sıralama: (uzaklık, -frekans, alfabe).
  - **`check(word)`** → `SpellResult(frozen=True)` — `is_valid=True` → kısa-devre (BK-tree atlanır).
  - **Türkçe API** (`tr.py`): `yazım_geçerli()` / `öneri()` / `denetle()`.
  - **CLI**: `python -m turkgram check <kelime>` — `evdte: GEÇERSİZ` / `evde: GEÇERLİ`.
  - TUZAK: `seker` = `sekmek` geniş 3sg → GEÇERLİ; golden `dag` (dağ) kullandı (V1 seker tuzağı).
  - TUZAK: `tr.py` sarmalayıcılar `_tr_lower` ÇAĞIRMAZ — `spellcheck` modülü içeride zaten normalize eder.
  - Hakem: 26k leksikon, 0 çökme. 58 yeni test; **toplam: 3883 test**.

Yeni dosyalar (2026-07-16, Faz 9 hecelemleme+vurgu):
- `docs/superpowers/specs/2026-07-16-syllabify-design.md` — onaylı tasarım dokümanı
- `docs/superpowers/plans/2026-07-16-faz9-syllabify.md` — implementasyon planı
- `turkgram/syllabify.py` — `syllabify`, `stress`, `stress_mark`, `_VALID_ONSETS`, `_STRESS_EXCEPTIONS`, `_tr_upper`
- `turkgram/__init__.py` — `syllabify`, `stress`, `stress_mark` export eklendi
- `turkgram/tr.py` — `hecele()`, `vurgu()`, `vurgu_işaretle()` Türkçe sarmalayıcılar eklendi
- `tests/golden_syllabify.py` — 101-girdi bağımsız golden (motor-körü, Opus)
- `tests/test_syllabify.py` — runner (101 test)

Yeni dosyalar (2026-07-17, Faz 9d ikileme):
- `docs/superpowers/specs/2026-07-17-reduplication-design.md` — onaylı tasarım dokümanı
- `docs/superpowers/plans/2026-07-17-faz9d-reduplication.md` — implementasyon planı
- `turkgram/reduplication.py` — `full_reduplicate`, `converb_reduplicate`, `m_reduplicate`, `_a_converb`
- `turkgram/__init__.py` — reduplication modülü + 3 fonksiyon export eklendi
- `turkgram/tr.py` — `tam_ikile()`, `ulaç_ikile()`, `m_ikile()` Türkçe sarmalayıcılar eklendi
- `turkgram/analysis.py` — `_try_reduplication_all()` + `_analyze_multi_token` genişletme;
  `_KINDS`'a `"reduplication_full"/"reduplication_converb"/"reduplication_m"` (sona)
- `tests/golden_reduplication.py` — 56-girdi bağımsız golden (16 full + 20 converb + 20 m; motor-körü, Opus)
- `tests/test_reduplication.py` — üretim runner (61 test: parametrik + ValueError + boş string)
- `tests/golden_reduplication_analysis.py` — 33-girdi bağımsız analiz golden (motor-körü, Opus);
  NOT: pos=None sınırı (gürültü modu)
- `tests/test_reduplication_analysis.py` — analiz runner + TR API denklik (36 test)
- `tools/sweep_reduplication.py` — korpus tarama aracı (26k lemma, 0 çökme)

Yeni dosyalar (2026-07-17, Faz 9b yazım denetimi):
- `docs/superpowers/specs/2026-07-16-spellcheck-design.md` — onaylı tasarım dokümanı
- `docs/superpowers/plans/2026-07-16-faz9b-spellcheck.md` — implementasyon planı
- `turkgram/spellcheck.py` — `_BKTree`, `_tr_distance`, `_TR_PAIRS`, `SpellResult`, `is_valid`, `suggest`, `check`
- `turkgram/__init__.py` — `spellcheck` modülü + `SpellResult` export eklendi
- `turkgram/tr.py` — `yazım_geçerli()`, `öneri()`, `denetle()` Türkçe sarmalayıcılar eklendi
- `turkgram/__main__.py` — `cmd_check()` + `check` alt-komutu eklendi
- `tests/golden_spellcheck.py` — 40-girdi bağımsız golden (motor-körü, Opus); NOT: seker→dag tuzağı
- `tests/test_spellcheck.py` — runner (58 test)
- `tools/sweep_spellcheck.py` — korpus tarama aracı (26k leksikon, 0 çökme)

Yeni dosyalar (2026-07-17, Faz E3/E4 yan cümle desteği):
- `docs/superpowers/specs/2026-07-17-e3-e4-subordinate-clauses-design.md` — onaylı tasarım dokümanı
- `docs/superpowers/plans/2026-07-17-faz-e3-e4-yan-cumle.md` — implementasyon planı
- `turkgram/parse.py` — `_apply_r6_ki` (CompP/RelP) + `_apply_r7_diye` (DiyeP) + R5 stop-list güncellemesi; `_CONVERB_VERB_TOKENS={"diye"}` (yüzey tabanlı VERB etiketi); `_node_matches` children opsiyonel
- `tests/golden_subordinate.py` — 10-girdi bağımsız golden (motor-körü, Opus): 5 ki-cümlesi + 3 diye-cümlesi + 2 regresyon
- `tests/test_subordinate.py` — runner (10 test)
- `tests/test_parse.py` — `_node_matches` children key yoksa `True` dön (opsiyonel alt-ağaç)
- `tools/sweep_syntax_e.py` — CompP/RelP/DiyeP hakem kontrolleri + `_tag`/`PhraseNode` import

**Faz E3/E4 kritik tuzak — `diye` analizi:** `diye` morfolojik olarak `demek` opt-3sg (`kind='conjugate', tense='opt'`); `kind='converb'` ASLA üretilmez. Spec §4.1'in `kind=='converb'` koşulu çalışmaz — yüzey tabanlı kapalı küme tespiti (`ki`/`ve` gibi) kullanılır. `_CONVERB_VERB_TOKENS={"diye"}` `_leaf_tag`'de VERB etiketi garantiler; R7 `node.token.lower() == "diye"` kontrolüyle tetiklenir.

**Faz E3/E4 kritik tuzak — `NP ki NP`:** Eski davranış CoordP (R4); R6 R4'ten önce çalıştığından sol=NP → RelP. Linguistik olarak doğru (Türkçede `ki` koordinatör değil).
