# turkgram Faz 1 — Fiil Çekim Morfolojisi Derinleştirme (A1–A6) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Motorun fiil çekimini Korkmaz *Şekil Bilgisi* seviyesine tamamlamak — nominal
ek-fiil, ulaç envanteri, tasvir fiilleri, fiilimsi+iyelik/durum istifi ve çatı entegre
çekim+yığılma — çözümlemeye/sözdizimine kaçmadan.

**Architecture:** Mevcut kural-tabanlı RUNTIME üretici (`morphology.py` fiil + `morphology_noun.py`
isim) genişletilir. Her boşluk için morfofonoloji primitifleri (`_stem_before_suffix`, harmoni,
yumuşama, kaynaştırma) YENİDEN KULLANILIR. Çatı (A1) yeni bir **morfotaktik katman** ekler:
gövde → çatı zinciri → çekim. Motor biçim SAKLAMAZ (#5), üretir.

**Tech Stack:** Saf Python 3.10+, sıfır çalışma-zamanı bağımlılığı; pytest; golden tablolar
(motordan bağımsız, elle-doğrulanmış).

**İş akışı (HER task, CLAUDE.md #5 — DEĞİŞMEZ):**
1. **SPEC** (grammatical-invariant) ANA OTURUM tarafından elle yazılır — Korkmaz'dan kural,
   örnek/düzyazı KOPYALANMAZ (#11). Alt-modele bırakılmaz (Türkçe morfoloji hataları ince).
2. **Golden** motordan BAĞIMSIZ kurulur (elle-doğrulanmış beklenen biçimler) — TDD "failing test".
3. **Motor** golden'ı geçecek minimal kod.
4. **Hakem + code-review** (python-reviewer) + tüm korpus çökme taraması.

**Kaynak:** `docs/faz1-bosluk-analizi.md` (boşluk tanımları), `morphology-spec.md` §1–§11,
`work/turkgram_faz1/korkmaz_toc.txt` (Korkmaz § referansları — repoya girmez, #11).

---

## Dosya yapısı (oluşturulacak / değişecek)

| Dosya | Sorumluluk | Faz 1'de |
|-------|-----------|----------|
| `turkgram/morphology.py` | Fiil çekim çekirdeği | A2/A5 ekler; A1 çatı-gövde girişi |
| `turkgram/voice.py` **(YENİ)** | Çatı morfotaktik katmanı (ettirgen/edilgen/dönüşlü/işteş + yığılma) | A1 |
| `turkgram/nonfinite.py` **(YENİ)** | Fiilimsi (isim-fiil/sıfat-fiil/zarf-fiil) çekim çıktısı + iyelik/durum istifi | A3/A5 |
| `turkgram/morphology_noun.py` | İsim çekimi | A4 nominal ek-fiil (kopula) |
| `turkgram/__init__.py` | Genel API | Yeni fonksiyonları dışa aç |
| `morphology-spec.md` | Fiil SPEC | §12 tasvir, §13 çatı bölümleri eklenir |
| `spec/nonfinite-spec.md` **(YENİ)** | Fiilimsi SPEC | A3 |
| `spec/voice-spec.md` **(YENİ)** | Çatı SPEC | A1 |
| `tests/golden_verbs.py` | Fiil golden | A2/A5 hücreleri |
| `tests/golden_copula.py` **(YENİ)** | Nominal ek-fiil golden | A4 |
| `tests/golden_nonfinite.py` **(YENİ)** | Fiilimsi golden | A3/A5 |
| `tests/golden_voice.py` **(YENİ)** | Çatı golden | A1 |
| `tests/test_*.py` | Birim + golden koşucu | her task |

Sıra: **A4 → A5 → A6 → A2 → A3 → A1** (düşük-zorluk-yüksek-değerden çatının en zoruna).
Her task kendi başına çalışan, test edilebilir yazılım üretir; ayrı commit.

---

## Task A4: Nominal ek-fiil (kopula) — *öğrenciydim, evdeymiş, hastaysa*

**Neden ilk:** En düşük zorluk, yüksek değer. Fiil `aux` mantığının (i-di/i-miş/i-se) nominal
gövdeye taşınması. Tam çekim tablosunu isim/sıfat yüklemine açar.

**Files:**
- Modify: `turkgram/morphology_noun.py` (yeni `copula()` + `predicative` genişletme)
- Modify: `turkgram/__init__.py` (export `copula`)
- Create: `tests/golden_copula.py`
- Create: `tests/test_copula.py`
- SPEC: `morphology-spec.md` §12 (ek-fiil, nominal yüklem) — ana oturum yazar

**SPEC deliverable (ana oturum, #5):** ek-fiilin nominal gövdeye eklenmesi:
- Geniş/şimdi: `-DIr` (var — `predicative`); zero-copula 3sg (öğrenci-∅).
- Hikâye `-(y)DI`: öğrenci-y-di-m (öğrenciydim), ev-de-y-di (evdeydi), hasta-y-dı.
- Rivayet `-(y)mIş`: öğrenciymiş, evdeymiş.
- Şart `-(y)sA`: öğrenciyse, evdeyse, hastaysa.
- Kaynaştırma `-y-` ünlü-final gövdede (öğrenci-**y**-di); ünsüz-final gövdede yok (ev-di→evdi? HAYIR: ev-**...**; DİKKAT: ünsüz-final nominal + DI → *evdi* yanlış, doğru *evdeydi* değildir — nominal ek-fiil ÜNSÜZ-final gövdede de -y- almaz: "güzeldi" (güzel-di), "öğretmendi". SPEC bunu netleştirir: -y- yalnız ÜNLÜ-final gövdede.)
- Kişi ekleri: k-tipi (hikâye/şart: -m/-n/-∅/-k/-nIz/-lAr), z-tipi (rivayet: -Im/-sIn/…).
- Soru × kopula: "öğrenci miydim / öğrenci miymiş / öğrenci misin".

**Golden coverage (bağımsız):** en az 10 nominal (ünlü-final: öğrenci/hasta/kapı; ünsüz-final:
ev/güzel/öğretmen/kitap; sert-final: genç/aş) × {pres(-DIr/zero), hikaye, rivayet, sart} × 3 kişi
+ soru örnekleri. ~150 hücre elle.

**Steps:**
- [ ] **1. SPEC yaz** `morphology-spec.md` §12 (ana oturum, Korkmaz §579–583 kural).
- [ ] **2. Golden kur** `tests/golden_copula.py` — `GOLDEN_COPULA = {'ev': {'hikaye.3sg':'evdi', 'hikaye.loc.3sg':'evdeydi', ...}}` (motordan bağımsız). *Not: kopula durum-ekli gövdeye de biner (evde+ydi); golden hem yalın hem loc gövde üstünde test eder.*
- [ ] **3. Failing test** `tests/test_copula.py`: `pytest tests/test_copula.py -v` → FAIL (copula yok).
- [ ] **4. Motor** `morphology_noun.py::copula(headword, aux, person, *, case=None, possessive=None, question=False)` — decline ile gövde üret, ek-fiil ekle (fiil `_ekfiil`/`_conjugate_aux` mantığı emsali; kaynaştırma yalnız ünlü-final).
- [ ] **5. Test yeşil** + `tests/` tümü yeşil.
- [ ] **6. Korpus çökme taraması:** tüm nominal korpusta copula × aux × kişi 0 çökme.
- [ ] **7. Commit** `feat(copula): nominal ek-fiil (hikaye/rivayet/sart + soru)`

---

## Task A5: Ulaç envanteri tamamlama + A6 aorist doğrulama

**Files:**
- Create: `turkgram/nonfinite.py` (zarf-fiil üreticisi — A3'ün de temeli)
- Modify: `turkgram/morphology.py` (yeni tense anahtarları ya da nonfinite'e delege)
- Create: `tests/golden_nonfinite.py` (ulaç bölümü)
- Modify: `tests/golden_verbs.py` (aorist doğrulama hücreleri)
- SPEC: `spec/nonfinite-spec.md` (zarf-fiil bölümü)

**SPEC deliverable:** eksik zarf-fiil (ulaç) ekleri — Korkmaz §677:
`-ken` (gelirken, evdeyken — ek-fiil üstüne de), `-DIğIndA/-DIğI zaman`, `-mAksIzIn`
(gelmeksizin), `-cAsInA` (gelircesine), `-AsIyA` (ölesiye), `-DIğIndAn` — mevcut 6'ya (`-ArAk/-Ip/-IncA/-mAdAn/-AlI/-DIkçA`) ek. Morfofonoloji: ünlü-başlılık, yumuşama, ye/de emsali.
**A6:** Korkmaz geniş zaman bölümüyle 13-istisna -Ir aorist listesini çapraz-doğrula; sapma varsa `IRREGULAR` tablosunu düzelt (muhtemelen tam — doğrulama + not).

**Golden coverage:** her yeni ulaç × 8 fiil sınıfı (ünsüz/ünlü-final, yumuşama, ye/de) ~60 hücre;
aorist doğrulama: Korkmaz'ın verdiği tek-heceli fiil listesi vs bizimki (fark raporu).

**Steps:**
- [ ] **1. SPEC** `spec/nonfinite-spec.md` zarf-fiil bölümü (ana oturum).
- [ ] **2. Golden** `tests/golden_nonfinite.py` ulaç hücreleri (bağımsız).
- [ ] **3. Failing test** → FAIL.
- [ ] **4. Motor** `nonfinite.py::converb(lemma, kind)` (mevcut `conv_arak` mantığını genelle).
- [ ] **5. A6:** Korkmaz aorist listesini `korkmaz_toc.txt` bölümünden çıkar, `IRREGULAR` ile diff; rapor + gerekiyorsa düzelt.
- [ ] **6. Test yeşil** + korpus taraması.
- [ ] **7. Commit** `feat(nonfinite): ulaç envanteri tamamla + aorist doğrula`

---

## Task A2: Tasvir fiilleri (aktionsart) — *yapıver, bakakaldı, gelеdur*

**Files:**
- Modify: `turkgram/morphology.py` (`aspect` parametresi — `ability` emsali)
- Modify: `turkgram/__init__.py`
- Create: `tests/golden_aspect.py`, `tests/test_aspect.py`
- SPEC: `morphology-spec.md` §13 (tasvir fiilleri)

**SPEC deliverable (Korkmaz §472):** tasvir ekleri — gövdeye zarf-fiil + yardımcı fiil kaynaşması:
- **Tezlik** `-Iver-`: yap-ı-ver, gel-i-ver, oku-y-u-ver (kaynaştırma) → sonra çekim (yapıverdi).
- **Süreklilik** `-Adur-` (gidedur, bakadur), `-Agel-` (süregel), `-Ayaz-` (düşeyaz — yaklaşma), `-Akal-` (bakakal).
- Yapı: gövde + (kaynaştırma) + `-A/-I` + yardımcı fiil kökü (ver/dur/gel/kal/yaz) → çekilir.
- `ability` emsali: `aspect ∈ {None, tezlik, süreklilik_dur, süreklilik_gel, yaklaşma, ...}`;
  olumsuz/soru gövdeye biner (yapıvermedi).

**Golden coverage:** her tasvir eki × 5 fiil × {pres/past/3sg + olumsuz} ~80 hücre.

**Steps:**
- [ ] **1. SPEC** §13 (ana oturum, Korkmaz §472 kural — hangi yardımcı fiil hangi işlev).
- [ ] **2. Golden** `tests/golden_aspect.py` (bağımsız).
- [ ] **3. Failing test** → FAIL.
- [ ] **4. Motor:** `conjugate(..., aspect=...)`; `ability` gövde-öncesi mantığını (`_stem_before_suffix`) yeniden kullan.
- [ ] **5. Test yeşil** + korpus taraması.
- [ ] **6. Hakem/review** (tezlik `-Iver` en yaygın; süreklilik ekleri arkaik/edebî — kapsam kararı).
- [ ] **7. Commit** `feat(aspect): tasvir fiilleri (tezlik/süreklilik/yaklaşma)`

---

## Task A3: Fiilimsi + iyelik/durum istifi — *okuduğum, geleceğimiz, gitmesini*

**Files:**
- Modify: `turkgram/nonfinite.py` (sıfat-fiil/ad-fiil + istif)
- Modify: `turkgram/morphology_noun.py` (fiilimsi gövdesini isim çekimine besle)
- Create: `tests/golden_nonfinite.py` (sıfat-fiil/ad-fiil bölümü — A5'ten devam)
- SPEC: `spec/nonfinite-spec.md` (sıfat-fiil/ad-fiil bölümü)

**SPEC deliverable:** adlaşmış yan cümle — fiilimsi gövdesi + iyelik + durum:
- Ad-fiil `-mA`: gitme → gitme-si-ni (gitmesini), gitme-m (gitmem); `-mAk`: gitmek-ten;
  `-Iş`: gidiş-in.
- Sıfat-fiil `-DIk` + iyelik: oku-duğ-um (okuduğum), gel-diğ-in, git-tiğ-i-ni (yumuşama+pronominal -n-);
  `-AcAk` + iyelik: gel-eceğ-im (geleceğim), yap-acağ-ımız.
- İstif: fiilimsi gövdesi → `morphology_noun.decline` çekirdeğine besle (iyelik+durum katmanları
  yeniden kullanılır; `-DIk/-AcAk` k→ğ yumuşaması + 3.kişi pronominal -n-).

**Golden coverage:** `-DIk`/`-AcAk`/`-mA`/`-mAk` × iyelik(6) × durum(birkaç) × yumuşama/ye_de
~120 hücre. Kritik: gittiğini (git yumuşama + -DIk + 3sg iyelik + acc + pronominal -n-).

**Steps:**
- [ ] **1. SPEC** sıfat-fiil/ad-fiil + istif (ana oturum; pronominal -n- ve k→ğ kritik).
- [ ] **2. Golden** `tests/golden_nonfinite.py` (bağımsız; en ince: gittiğini/geleceğimizi).
- [ ] **3. Failing test** → FAIL.
- [ ] **4. Motor:** `nonfinite.py::participle(lemma, kind, *, possessive, case)` → gövdeyi kur, `morphology_noun` çekirdeğini çağır.
- [ ] **5. Test yeşil** + korpus taraması (fiil × fiilimsi × iyelik × durum 0 çökme).
- [ ] **6. Hakem/review** (pronominal -n- ve yumuşama istisnaları — isim motoru emsali).
- [ ] **7. Commit** `feat(nonfinite): fiilimsi + iyelik/durum istifi (adlaşmış cümle)`

---

## Task A1: Çatı entegre çekim + yığılma — *yaptırttırılmak, dövüştürülüyor*

**Neden son:** En değerli ama en zor — yeni morfotaktik katman. Çatı zincirini gövdeye
uygular, sonra tüm çekim (kip/zaman/kişi/olumsuz/soru) çatılı gövdeye biner.

**Files:**
- Create: `turkgram/voice.py` (çatı morfotaktik katmanı)
- Modify: `turkgram/morphology.py` (`conjugate` çatılı gövde girişini kabul eder)
- Modify: `turkgram/__init__.py`
- Create: `tests/golden_voice.py`, `tests/test_voice.py`
- SPEC: `spec/voice-spec.md`

**SPEC deliverable (Korkmaz §488–499):** dört çatı + yığılma sırası:
- **Ettirgen** `-DIr-/-t-/-Ir-/-Ar-` (allomorf seçimi: ünsüz-final kök→-DIr, ünlü-final/çok-heceli→-t,
  leksik -Ir/-Ar: piş-ir/çık-ar); **çift ettirgen** yap-tır-t (yaptırt).
- **Edilgen** `-Il-/-In-` (ünlü-final ve l-final kök → -In: oku-**n**, bil-**in**; diğer → -Il: yap-ıl).
- **Dönüşlü** `-In-` (yıka-n, giy-in).
- **İşteş** `-Iş-` (döv-üş, gör-üş).
- **Yığılma sırası** (Korkmaz): DÖNÜŞLÜ/İŞTEŞ → ETTİRGEN → EDİLGEN (döv-üş-tür-ül: dövüştürül).
  Motor bir `voice_chain: list[str]` alır, sırayla uygular, morfofonolojiyi her adımda çözer.
- Çatılı gövde ünsüz/ünlü-final durumunu GÜNCELLER → sonraki ek harmoni/yumuşama ona bakar.

**Golden coverage:** her çatı tekli (~20 fiil) + yaygın yığınlar (ettirgen+edilgen: yapıldır?→
yaptırıldı; işteş+ettirgen+edilgen: dövüştürüldü) × birkaç çekim. En ince: allomorf seçimi +
yığılma harmonisi. ~150 hücre. Bağımsız golden ŞART (yığılma hataları çok ince).

**Steps:**
- [ ] **1. SPEC** `spec/voice-spec.md` (ana oturum — allomorf ölçütü + yığılma sırası en kritik; Korkmaz §498–499 + §488).
- [ ] **2. Golden** `tests/golden_voice.py` (bağımsız; yığınlar dahil).
- [ ] **3. Failing test** → FAIL.
- [ ] **4. Motor** `voice.py::apply_voice(vs, chain) -> VerbStem'` — her adımda ek + morfofonoloji, güncel gövde döndür; `conjugate` çatılı gövdeyle çekim yapar.
- [ ] **5. Test yeşil** + korpus taraması (çekirdek fiiller × çatı zincirleri 0 çökme).
- [ ] **6. Hakem + code-review** (python-reviewer) — allomorf/yığılma en hataya açık; iki bağımsız denetim.
- [ ] **7. Commit** `feat(voice): çatı entegre çekim + yığılma (ettirgen/edilgen/dönüşlü/işteş)`

---

## Kesişen (cross-cutting) gereksinimler

- **Her task:** SPEC (ana oturum) → golden (bağımsız) → motor → hakem+review → tam `pytest`
  yeşil + korpus çökme taraması. Golden Korkmaz örneğinden DEĞİL, elle-doğrulanmış biçimden.
- **Geriye uyum:** mevcut 1276 test HER commit'te yeşil kalmalı (davranış eklenir, değişmez).
- **API:** yeni parametreler var-olan imzalara opsiyonel eklenir (`aspect=`, `voice_chain=`);
  yeni fonksiyonlar `copula`/`converb`/`participle`/`apply_voice` `__init__`'te dışa açılır.
- **#5:** motor RUNTIME üretir, `entries.morph` doldurmaz. **#11:** Korkmaz düzyazı/örneği
  repoya girmez; golden elle üretilir.
- **Sözlük entegrasyonu (opsiyonel, Faz 1 sonu):** `inflect_display` yeni biçimleri kompakt
  çekim/çekim sayfasına ekleyebilir (roadmap 2c emsali) — Faz 1 kapsamı DIŞI, ayrı iş.

## Doğrulama (Faz 1 tamamlanma ölçütü)

- [ ] Tüm golden (verbs/nouns/copula/nonfinite/aspect/voice) yeşil.
- [ ] Korpus çökme taraması: TR fiil korpusu × yeni eksenler 0 çökme.
- [ ] Mevcut 1276 test regresyonsuz.
- [ ] `docs/faz1-bosluk-analizi.md` A ekseni maddeleri "kapandı" işaretli.
