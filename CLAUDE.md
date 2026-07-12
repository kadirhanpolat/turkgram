# CLAUDE.md — turkgram (Türkiye Türkçesi grameri, kod olarak)

Bu dosya, bu repoda çalışan herhangi bir ajanın **ilk fırsatta yanlış yapacağı**
kararları listeler. Betimleyici gramerlerden (Korkmaz *Türkiye Türkçesi Grameri —
Şekil Bilgisi*, Ergin, Deny, Vural) elle küratörlenmiş kuralları çalıştırılabilir
kod eden **bağımsız, dağıtılabilir** bir kütüphane.

Köken: İngilizce–Türkçe sözlük projesinden (`D:\PYTHON\dictionary`) Faz 0'da ayrıldı.
Sözlük bu paketi `pip install -e ../turkgram` ile tüketir.

---

## 1. Ne ÜRETİR, ne SAKLAMAZ (çekirdek değişmez)

Motor biçimleri **RUNTIME ÜRETİR, SAKLAMAZ**. Kök + morfofonolojik sınıftan
üretir; kombinatoryal tabloları diske dizmez. (Sözlük projesi #5 emsali.)

- **İngilizce çekirdek:** `morphology.py` (fiil çekimi), `morphology_noun.py` (isim
  çekimi + `copula`), `nonfinite.py` (ulaç `converb` + fiilimsi `participle`),
  `voice.py` (çatı `apply_voice`), `derivation.py` (yapım eki). Genel API `__init__.py`.
- **Çözümleme (Faz 2a):** `analysis.py` (`analyze`: yüzey→kök+eksen+segment) +
  `analysis_candidates.py` (öneri üretimi). Analysis-by-generation: üreteç oracle (bkz. #6).
- **Türkçe yüz:** `tr.py` — Türkçe-karakterli sarmalayıcılar (`çekimle`/`ad_çekimle`/
  `ekfiil`/`ulaç`/`fiilimsi`/`türet`/`çözümle`), içeride İngilizce çekirdeği çağırır (bkz. #4).

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
  (analysis-by-generation, beş kind: conjugate/decline/copula/converb/participle) + pedagojik
  segmentasyon. Round-trip sistematik sınıflarda doğrulandı; korpus 0 çökme. `-Iyor` ünlü-düşmesi,
  **suppletif zamir eğik durumu (`bana`/`sana`)** ve **nominal ekfiil soru grubu (`evde miydi`)**
  KAPATILDI. **Kalan 2b açığı** (design §3.1): birleşik çok-token fiil (`göz ardı etmek`);
  `-ken` ulacı doğru kapsam-dışı.
- **Faz 2b** — gerçek-metin sağlamlığı: geniş kök leksikonu, olasılıksal disambiguation,
  motor-dışı biçimler, §3.1 açıkları. FST araçları (Zemberek/TRmorph) adopt-referans.
- **Faz 3/4** — türetme genişletme; sıfat/zamir; sözdizimi (defer). Bkz. `docs/faz1-bosluk-analizi.md`.

Test durumu: son ölçüm **2177 test yeşil** (+ round-trip süpürme `-m slow`: recall tam +
p95 bütçe, 795s). Her commit'te regresyonsuz + korpus 0 çökme (2435 çağrı, 0 çökme).
