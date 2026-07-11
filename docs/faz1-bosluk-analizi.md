# Faz 1 — Boşluk Analizi: turkgram v0.1 ↔ Korkmaz *Türkiye Türkçesi Grameri (Şekil Bilgisi)*

**Amaç:** Yeni gramer kuralı/kod yazmadan önce (search-first) mevcut motorun kapsadığı
gramer yüzeyini, kaynak gramerin (Korkmaz) kapsadığı yüzeyle karşılaştırıp **boşlukları**
öncelik + karar (extend / build / defer) ile listelemek. Bu rapor Faz 1 spec'ini ve
Faz 2 (çözümleme) sırasını besler.

## Yöntem ve kaynaklar

- **Mevcut kapsam:** `morphology-spec.md` (fiil, §1–§11), `morphology-noun-spec.md`
  (isim), `turkgram/derivation.py` ek envanteri.
- **Kaynak yüzeyi:** Zeynep Korkmaz, *Türkiye Türkçesi Grameri — Şekil Bilgisi* (TDK),
  1344 s.; içindekiler PDF'ten çıkarıldı (`work/turkgram_faz1/korkmaz_toc.txt`).
  Kitap SÖZCÜK-SINIFI morfolojisini bölümler: **İsim · Sıfat · Zamir · Zarf · Fiil ·
  Edat/Bağlaç/Ünlem**. Fiil bölümü: çatı (§488–499), tasvir fiilleri (§472), yeterlik
  (§243.1), bildirme/tasarlama kipleri (§514–564), ek-fiil (§579–583), birleşik kipler
  Hikâye/Rivayet/Şart × her kip (§591–593), fiilimsi ekleri (§677 civarı).
- **Referans araçlar (bilinen-uygulanabilir kontrol listesi):** Zemberek (ahmetaa,
  Java, FST morfotaktik — çözümleme + üretim), TRmorph (foma), Google turkish-morphology
  (OpenFst). Üçü de aşağıdaki boşlukları (çatı, tasvir, tam fiilimsi, zamir düzensizleri)
  standart olarak kapsar → boşluklarımız egzotik değil, uygulanabilir.

## Mevcut kapsam (turkgram v0.1)

| Alan | Kapsanan |
|------|----------|
| **Fiil çekimi** | 9 kip (5 bildirme: pres/past/fut/aorist/evid + 4 tasarlama: opt/cond/necess/imp); olumsuz; yeterlik `-Abil`; soru `mI`; birleşik zaman `aux ∈ {hikaye,rivayet,sart}`. Aorist düzensizleri (13 tek-heceli), yumuşama (git/et), ye/de. |
| **İsim çekimi** | durum(6) × iyelik(6) × çoğul; ek katmanlar `-DIr`/`-ki`/`-CA`; pronominal `-n-`; yumuşama/ünlü-düşmesi/ikizleşme (leksik). |
| **Türetme** | Küratörlü yapım eki seti (isim→isim, isim→fiil, fiil→isim); çatı türevleri (`-DIr/-t/-Ir/-Ar` ettirgen, `-Il` edilgen, `-In` dönüşlü, `-Iş` işteş); fiilimsi (isim-fiil `-mA/-Iş`; sıfat-fiil `-An/-mAz/-DIk/-AcAk/-mIş/-AsI`; zarf-fiil `-ArAk/-Ip/-IncA/-mAdAn/-AlI/-DIkçA`) — **mekanik biçim üretici** (varlık sorgusuyla linklenir), çekim paradigmasına ENTEGRE DEĞİL. |
| **Yön** | Yalnız **ÜRETİM** (encode). Çözümleme (parse) YOK. |

## Boşluklar

Dört eksene ayrılır. **A = Faz 1'in asıl hedefi** (çekim derinleştirme); B/C/D sonraki fazlar.

### A. Çekim/fiil morfolojisi derinleştirme — Faz 1 çekirdeği

| # | Boşluk | Korkmaz | Mevcut durum | Karar | Zorluk |
|---|--------|---------|--------------|-------|--------|
| A1 | **Çatı entegre çekim + yığılma** (ettirgen+ettirgen+edilgen: *yaptırttırılmak*; dönüşlü/işteş üstüne zaman) | §488–499 çatıyı çekirdek fiil morfolojisi sayar | derivation.py tek çatı biçimi üretir (mastar), ama çatı-işaretli gövde ÇEKİLEMEZ, yığılamaz | **build** (çatı morfotaktik katmanı: gövde → çatı zinciri → çekim) | Yüksek |
| A2 | **Tasvir fiilleri** (tezlik `-Iver`, süreklilik `-Adur/-Agel/-Ayagör`, yaklaşma `-Ayaz`, `-Akal`) | §472 "Durum ve Tasvir Bildiren Fiiller" | YOK (yalnız yeterlik `-Abil` var) | **extend** (yeterlik emsali: gövdeye tasvir eki + çekim) | Orta |
| A3 | **Fiilimsi + iyelik/durum yığını** (adlaşmış yan cümle: *okuduğum, geleceğimiz, gitmesini*) | Sıfat-fiil/ad-fiil §677; iyelik+durum ekleri üstüne biner | conjugate yalnız `conv_arak`+`part_dik` verir; derivation fiilimsi'yi türetme olarak üretir ama iyelik/durum İSTİFLEMEZ | **extend** (fiilimsi gövdesi → isim çekim motoruna besle) | Orta |
| A4 | **Nominal yüklem ek-fiili** (isim+idi/imiş/ise: *öğrenciydim, evdeymiş, hastaysa*) | §579–583 ek-fiil | isim `predicative` yalnız `-DIr`/geniş; geçmiş/duyulan/şart kopula YOK | **extend** (fiil `aux` mantığını nominal gövdeye taşı) | Düşük |
| A5 | **Fiilimsi ulaç envanteri tamamla** (`-ken`, `-DIğIndA`, `-AsIyA`, `-mAksIzIn`, `-cAsInA`) | §677 zarf-fiil listesi Korkmaz'da daha geniş | 6 ulaç var; ~5 eksik | **extend** (tablo genişletme) | Düşük |
| A6 | **Aorist/düzensiz kapsamı doğrula** (Korkmaz'ın -Ir/-Ar ayrım ölçütü vs bizim 13-istisna) | Geniş zaman bölümü | 13 istisna kapalı küme | **defer/verify** (Korkmaz listesiyle çapraz-kontrol; muhtemelen tam) | Düşük |

### B. Çözümleme / analiz (parse) — Faz 2 (dik eksen, en büyük yeni bileşen)

Motor yalnız üretir; *kitaplarımızdan* → kök+ekler ÇÖZME yok. Korkmaz betimler (üretim/analiz
ayrımı yapmaz), ama gerçek kullanım (NLP, sözlük arama, öğrenci geri-bildirimi) analiz ister.
**Karar: build ya da adopt.** FST araçları (Zemberek/TRmorph/Google turkish-morphology) analizi
+ disambiguation'ı hazır çözer → Faz 2'de "kendi kural-analizörü mü, FST adopt mu" ayrı tasarım
turu. Bu bir "Korkmaz boşluğu" değil, mimari eksen.

### C. Sözcük-sınıfı genişleme — sonraki fazlar

| Boşluk | Korkmaz | Karar |
|--------|---------|-------|
| **Sıfat morfolojisi**: pekiştirme (*sım-sıcak, kapkara, bembeyaz*), küçültme (`-CIk`, `-ImsI/-ImtIrak`), karşılaştırma (*daha/en* — sözdizimsel) | SIFATLAR bölümü (§~333) | extend (pekiştirme/küçültme kurallı; karşılaştırma sözdizimi) |
| **Zamir çekimi düzensizleri**: *ben→bana, biz→bize, o→ona, bu→buna, kim→kime* | ZAMİRLER (§399+) | extend (isim motoruna zamir istisna tablosu; `_decline_pronoun` kısmen var) |
| **Zarf/Edat/Bağlaç/Ünlem** | ZARFLAR/EDAT bölümleri | **defer** — çoğu çekimsiz; morfoloji değil sözlük/sözdizimi işi |

### D. Sözdizimi / cümle bilgisi — en son faz

Tamlama, çatı-cümle uyumu, öbek yapısı. Korkmaz'ın kapsamı ağırlıkla şekil bilgisi (morfoloji);
sözdizimi ayrı ve en büyük eksen. **defer** (Faz 4).

## Faz 1 önerilen kapsam (dar-ama-derin)

Sözdizimine/analize kaçmadan, **fiil çekim morfolojisini Korkmaz seviyesine tamamla**.
Değer/zorluk sırası:

1. **A4 Nominal ek-fiil** (düşük zorluk, yüksek değer — tam çekim tablosunu nominal yükleme açar)
2. **A5 Ulaç envanteri + A6 aorist doğrulama** (düşük zorluk, tablo işi)
3. **A2 Tasvir fiilleri** (orta — yeterlik emsali, aktionsart ekseni)
4. **A3 Fiilimsi + iyelik/durum istifi** (orta — adlaşmış cümle, yüksek pedagojik değer)
5. **A1 Çatı entegre çekim + yığılma** (yüksek — çekirdek ama en zor; morfotaktik katman gerektirir, muhtemelen Faz 1'in kapanışı ya da Faz 1.5)

**İş akışı (her madde, CLAUDE.md #5 emsali):** ana oturum Korkmaz'dan grammatical-invariant
SPEC yazar (elle, alt-modele bırakma) → golden testler motordan BAĞIMSIZ kurulur → motor →
hakem + code-review. Golden Korkmaz'ın örnek biçimlerinden DEĞİL (telif), elle-doğrulanmış
biçimlerden.

## Faz 2 notu (adopt-referans)

Çözümleme için sıfırdan yazmadan önce Zemberek (Apache-2.0) morfotaktik modelini ve
foma/OpenFst tabanlı TRmorph/Google turkish-morphology'yi değerlendir — üretim motorumuzun
kural tabanı ile FST analizi köprülenebilir (üretim kuralları çoğu kez tersine çevrilebilir).

---

*Kaynak: Korkmaz içindekiler `work/turkgram_faz1/korkmaz_toc.txt` (PDF s5–34).
Referans araç kapsamı: ahmetaa/zemberek-nlp, TRmorph (foma), google-research/turkish-morphology.*
