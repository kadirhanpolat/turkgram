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

## 5. Notlar

- `tools/diff_harness.py` gold-reader `*.txt` glob'lar; gerçek gold tek dosya
  (`trmor2018.gold`, UTF-8). `eval_statistical.py` kendi okuyucusunu kullanır (düzeltildi).
- Ölçüm major-POS düzeyinde (Artım-1 viterbi). Artım-2 ince-durum viterbi'si YOK
  (`viterbi` yalnız `_analysis_pos` major kullanır) → ince-düzey HMM değerlendirmesi
  ayrı iş (fine viterbi gerekir).
