# Mimari Kritik — Faz 2a Çözümleyici (hibrit "soyma önerir, üreteç doğrular")

**Tarih:** 2026-07-12  **Tur:** 1 (5 paralel bağımsız mercek)  **Ham bulgu:** 44 → tekil 12

Mercekler: algoritmik bütünlük, Türkçe dilbilim uzmanı, API/arayüz sağlamlığı,
performans/kombinatoryal patlama, YAGNI/pragmatist.

## Bulgu sicili

| ID | Mercek | Şiddet | Saldırılan iddia | Senaryo | Tahkim | Karar |
|----|--------|--------|------------------|---------|--------|-------|
| C-01 | Algoritmik+Dilbilim (2 mercek bağımsız) | Critical | "yüzeyi sağdan sola soyar" — tek-token varsayımı | `question=True` biçimleri BOŞLUK içerir ("geliyor musun"); birleşik fiil öneki ("aday oldu"). Tek-token stripper kip katmanına hiç ulaşamaz → round-trip tüm soru ekseni + birleşiklerde gün-1'de kırık | Geçerli — üreteç dili çok-tokenli; tasarım tokenizasyonu hiç tanımlamamış | **Fix** — ön-tokenizasyon aşaması: sondaki mI-grubu ayrılır, birleşik önek adaylanır |
| C-02 | Algoritmik+Dilbilim (2 mercek, 3 bulgu) | Critical | "Precision %100 by construction" — segments alanı için SAHTE | Oracle yalnız `output == surface` sınar; `segments` gevşek öneriden gelir ve HİÇ doğrulanmaz → doğru kwargs + yanlış kesim noktası kabul edilir; pedagojik çıktı (2a'nın amiral özelliği) sıfır garantili | Geçerli — asimetri iddiası yalnız (lemma,kwargs) için doğru; segmentasyon ayrıca tasarlanmalı | **Fix** — segmentasyon ayrı spec bölümü: politika (yüzey dilimi + kanonik etiket + span) + kendi elle-doğrulanmış golden'ı; "bedavaya gelir" iddiası silinir |
| C-03 | Dilbilim+YAGNI | Critical | "leksikon gerekmez" + "%100 precision" birlikte | Üretecin kök sözlüğü yok → uydurma kök round-trip'i geçer: "masa" → mas-A (istek) KABUL. Biçim-precision ≠ sözlüksel precision; öğrenciye saçma kök sunulur | Geçerli — iddia "form-precision" olarak daraltılmalı; gerçek tüketici köke zaten sahip | **Fix** — `analyze(..., roots=None)` opsiyonel kök-filtre (dict-db kökleri hazır); filtresiz sonuç `hypothetical=True` işaretli; spec iddiası "form-precision" |
| C-04 | Performans+Algoritmik | Critical | voice_chain sınırsız → sonlanma yok | caus tekrarlanabilir; "tırtırtır…" girdisinde zincir uzunluğu 1..k sınırsız sayılır → askıda kalma | Geçerli — ama Türkçe zincirler yapısal sınırlı | **Fix** — kanonik sıra (refl\|recip ≤1) → (caus ≤3) → (pass ≤1) = **24 zincirlik kapalı küme**; sınırsız arama yok |
| C-05 | YAGNI ↔ Performans (ÇATIŞMA) | Critical | "_suffix_markers kaba tanıyıcılar" (YAGNI: at, enumerate) vs "12.672 grid patlar" (Perf: budama şart) | YAGNI: marker'lar üretecin el-yazımı gölge grameri, sonsuza dek senkron yükü. Perf: saf enumeration kök-adayı × 12.672 × 24 zincir = yüz binlerce conjugate çağrısı/sözcük | Her ikisi kısmen haklı → sentez: **katmanlı stripper ATILIR**; yerine (a) kök adayları = yüzeyin ÖNEKLERİ (+ ters-mutasyon çeşitleri, ≤len×5, doğal sınırlı), (b) eksen grid'i SES (sound) ön-filtrelerle budanır: yalnız KANITLANABILIR gerekli yüzey izi olan hücreler ("pres ⇒ 'yor' içerir", "evid ⇒ m[ıiuü]ş içerir", "question ⇒ ' m[ıiuü]'") — filtre yanlış budayamaz (kanıtlanabilir gereklilik) → precision VE recall yapısal, morfotaktik gölge grameri YOK | **Fix** — mimari revize: "önek-tabanlı kök adayı + ses-filtreli grid enumerasyonu + üreteç oracle". LRU cache + sözcük başına çağrı bütçesi (p95 ≤ ~2000 çağrı) ölçülür |
| H-01 | Algoritmik+Dilbilim | High | ters-mutasyon listesi eksik (d→t,c→ç,ğ→k,ünlü) | ye_de sınıfı (yi→ye: "yiyor"→yemek) ve b→p listede yok → düzensiz sınıf gün-1 çözülemez | Geçerli — liste üretecin kendi mutasyon envanterinden türetilmeli, elle kopya değil | **Fix** — ters-imge kümesi `_stem_before_suffix`+isim motoru mutasyonlarından türetilir (t→d,k→ğ,p→b,ç→c,ye_de e→i,ünlü düşmesi) |
| H-02 | Dilbilim | High | yeterlik×olumsuzluk yüzey şekilleri (-Abil/-AmA/-mA/-AmAyAbil) tek katman sanılmış | "okuyamadı" (abil yüzeyde kaybolur, suppletif -AmA) katı sıralı stripper'da hiç hipotezlenmez | C-05 revizyonuyla büyük ölçüde düşer (grid hücresi ability×negative zaten enumerate edilir); ses-filtresi bu hücrede yalnız "m[ae]" gerekliliği | **Fix (C-05 içinde)** — golden'a 4 şekil × temsili fiiller |
| H-03 | API | High | `Analysis` tipi/sıralama/hata sözleşmesi tanımsız | `analyze("")`, çok-sözcük, bilinmeyen pos, boş sonuç vs istisna; `analyses[0]` deterministik değil | Geçerli — v1'de donmalı | **Fix** — `@dataclass(frozen=True) Analysis(lemma, pos, kwargs, segments, hypothetical)`; deterministik toplam sıralama (morfem sayısı↑, çatısız önce, lemma alfabetik); boş girdi/tip → ValueError; çözümsüz → `[]`; `_tr_lower` normalizasyonu girişte |
| H-04 | API | High | tr.py yüzü (`çözümle`) hiç tasarlanmamış | tr kullanıcısı İngilizce eksen değerleri alır; `tr.çekimle(**tr.çözümle(w))` ters-çeviri belirsiz (alias çakışmaları) | Geçerli — proje kuralı (#4) Türkçe yüz zorunlu | **Fix** — `tr.çözümle`: kwargs KANONİK Türkçe değere çevrilir (alias'ların kanonik temsilcisi; `_ANAHTAR` emsali ters harita) |
| M-01 | Algoritmik | Medium | dedup anahtarı tanımsız (default-dolu vs default-siz kwargs) | `{"tense":"past"}` ≡ `{"tense":"past","negative":False}` çift sayılır | Geçerli | **Fix** — kanonik form: default eksenler ATILIR; eşitlik (lemma,pos,kanonik kwargs) |
| M-02 | Dilbilim | Medium | sözlükselleşmiş biçimler ("dolmuş","yiyecek","gelir") kompozisyonel analizle sunulur | Öğrenciye "dolmuş = dol-muş (dolmak, öğr. geçmiş)" TEK doğru gibi | Geçerli ama 2a kapsamı değil — leksikal bilgi 2b/sözlük katmanı | **Defer (2b)** — Analysis zaten `hypothetical`/form-analizi diye çerçeveli |
| M-03 | API | Medium→Reject | "list[Analysis] 2b skorunu taşıyamaz, KIRICI" | — | Geçersiz — frozen dataclass'a default'lu opsiyonel alan eklemek geriye-uyumludur; golden eşitliği zaten (lemma,kwargs) üzerinden | **Reject** |
| M-04 | YAGNI | Medium→Reject | "2a'yı public API yapma, test-utility olarak sakla" | — | Kullanıcı kararıyla çelişir (2a = round-trip + pedagojik ÜRÜN, kullanım: sözlük + öğrenci); API H-03 ile donuyor | **Reject** (kullanıcı kapsam kararı) |

## Tahkim özeti (Faz 3 müzakeresi)

**C-05 (çekirdek çatışma) — kararın gerekçesi:** Katmanlı stripper iki dünyanın en
kötüsüydü: üretecin morfotaktiğini elle tersten kodlar (drift/senkron yükü, YAGNI haklı)
ama yine de recall'u garanti edemez. Saf enumeration ise kök adayları olmadan çalışamaz ve
budamasız pahalı (Perf haklı). Sentez: kök adayları **yüzeyin önekleri**nden gelir (doğal
sınırlı, gölge-gramer gerektirmez); eksen grid'i **yalnız kanıtlanabilir-gerekli yüzey izi**
filtreleriyle budanır (yanlış budayamaz → recall yapısal); çatı zinciri **24'lük kapalı küme**.
Precision + recall ikisi de by-construction; tek el-yazımı parça birkaç ses-filtresi
(her biri tek satırlık "substring gerekli" önermesi, üreteç golden'ıyla sınanabilir).

**Sonuç:** 6 Fix (2'si mimari revizyon), 1 Defer, 2 Reject, geri kalanı Fix-küçük.
Tasarım Bölüm 1-2 bu kararlarla revize edilmeli; Bölüm 3-4 (API sözleşmesi + test) revize
mimariye göre sunulacak.
