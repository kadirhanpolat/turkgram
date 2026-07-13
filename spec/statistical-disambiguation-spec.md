# SPEC — İstatistiksel disambiguation katmanı + diferansiyel harness (Faz 2b, madde A)

> Durum: **TASLAK — yazımda.** Bu SPEC ana oturumda elle yazılır (CLAUDE.md §2).
> Kural-tabanlı `context.py` katmanının **bağımsız istatistiksel muadili** + kural/istatistik/gold
> ayrışmalarını ölçen **diferansiyel değerlendirme harness'i**. OPT-IN; `analyze`/izole `rank`/
> `context.rank_in_context` DOKUNULMAZ (Faz 2b geriye-uyum değişmezi).

---

## 0. Amaç ve konumlandırma (kullanıcı kararı, 2026-07-13)

Bu katman **üretim fallback'i değil, geliştirme-aşaması teşhis aracıdır** (kullanıcı kararı).
Kural-tabanlı katman (`context.py`) kanonik yol olarak KALIR (CLAUDE.md "kural-tabanlı >
istatistiksel; MIT-dağıtılabilir, deterministik"). İstatistiksel katman AYRI, bağımsız bir rank
yolu olarak durur ve tek amacı **kuralın kör noktalarına ışık tutmak**:

- İki bağımsız istatistiksel model + kural + insan-etiketli gold → **dört-yollu kör-nokta haritası**.
- Ayrışmalar → kural katmanına yeni kural/kapalı-liste ekleme fırsatı üretir (kuralı GELİŞTİRİR).
- Üründe ileride fallback'e dönüşebilir, ama şimdilik referans/karşılaştırma amaçlı.

---

## 1. Karar günlüğü (sabit)

| Karar | Seçim | Gerekçe |
|-------|-------|---------|
| Konumlandırma | Bağımsız alternatif katman (fallback değil) | Geliştirme aşamasında kuralın açıklarını gösterir |
| Model | **Çarpımsal skorlama + HMM** (iki model) | Paylaşımlı sayım tabanı; ayrışmaları "dizi-bağlamı önemi"ni ölçer |
| CRF | **Defer** (bkz. §7) | Dış bağımlılık + determinizm/MIT-gömme değişmezini zorlar; ek teşhis değeri düşük |
| Eğitim verisi | **TrMor2018 train** (MIT) | Tek tam-MIT + disambiguation-formatlı kaynak (bkz. §2) |
| Gold/değerlendirme | **TrMor2018 handtagged gold** | Repo şartı: eğitim/testte KULLANMA, yalnız referans |
| Gömme | Ham korpus DEĞİL; **türetilmiş kompakt model** (`data/*.tsv`) | Leksikon/frekans emsali; ham 76MB gitignore'lu |
| Bağımlılık | **Saf-Python, bağımlılıksız** | CLAUDE.md değişmezi; deterministik + MIT-gömülebilir |
| Eşleme derinliği | **Kademeli: önce kök+POS (Artım-1), sonra eksen (Artım-2)** | Kaba hizalama hızlı çalışır; ince eksenler veriye bakarak derinleştirilir (§5) |

---

## 2. Veri kaynağı — TrMor2018 (ai-ku, MIT)

Repo: `github.com/ai-ku/TrMor2018` → `tools/trmor2018/` (gitignore'lu, ham ~76MB).
Lisans temiz **MIT**; etiketler Oflazer FST + Xerox xfst ile üretilmiş → `THIRD_PARTY_LICENSES.md`'de
atıf/izin notu zorunlu (README "use with permission"; olgu-çıkarımı savunması, Zemberek/hermitdave emsali).

**Format** (`TrMor2018/trmor2018.train`):
```
<DATA> / <CORPUS> / <DOC> / <S ...>…</S>   ← XML sınırları (cümle-bağlamı hazır)
word<TAB>analiz1<TAB>analiz2...            ← ilk analiz = DOĞRU; belirsiz yoksa tek analiz
```
Analiz dizgesi: `lemma+Tag+Tag...`, `^DB` = türetme sınırı (inflectional group).
Oflazer envanteri: `Noun/Verb/Adj/Adverb/Postp/Num/Det/Punc/Prop`; `A3sg/A3pl`; `Pnon/P1sg/P3sg`;
`Nom/Acc/Dat/Loc/Abl/Gen`; `Caus/Pass/Pos/Neg`; `Past/Fut/Aor/PresPart/FutPart/AorPart`; `Inf2/Ness/Zero`…

| Set | Token | Rol |
|-----|-------|-----|
| TrMor2018 train | 460.669 (215k ambiguous, 1779 unknown) | **eğitim** (semi-auto, %95.56 doğru) |
| TrMor2018 gold (handtagged) | elle-etiketli alt-küme | **yalnız değerlendirme** (repo şartı) |
| TrMor2016 test | 19.262 | ek test (farklı, boşluk-ayrık format) |
| TrMor2006 train | 837.524 | ek eğitim (düşük doğruluk, opsiyonel) |

---

## 3. Modeller (iki, paylaşımlı sayım tabanından)

Tek sayım tablosu iki modeli de besler; HMM üstüne geçiş matrisi + Viterbi ekler (~%20 ek iş).

- **Çarpımsal skorlama (baseline):** aday-başına log-olasılık = lemma-frekans × etiket-unigram.
  Bağlamsız (her token bağımsız). `disambiguation.rank`'in doğal istatistiksel uzantısı.
- **HMM (dizi):** aynı emisyon sayımları + etiket-geçiş (bigram/trigram) + **Viterbi** cümle çözümü.
  Klasik morfolojik disambiguation temeli. Saf-Python, deterministik.

**Ayrışmanın teşhis değeri:** çarpımsal ≠ HMM → dizi-bağlamı o token'da belirleyici → kural katmanı
orada bir K-kuralı içermeli. Bu, `context.py` K1–K5'in ampirik doğrulaması.

---

## 4. Diferansiyel harness (dört-yollu)

Aynı cümle kümesinde: **çarpımsal / HMM / kural (`context.rank_in_context`) / TrMor-gold** çıktısını
hizalar ve ayrışmaları sınıflar:

| Ayrışma | Yorum |
|---------|-------|
| çarpımsal ≠ HMM | dizi-bağlamı belirleyici → kurala K-kuralı adayı |
| HMM ≠ kural | kuralın açığı VEYA HMM hatası → gold'a bak |
| hepsi ≠ gold | tüm sinyaller yetersiz → yeni sinyal gerek |

Çıktı: agreement %, ayrışma-sınıfı dökümü, kural-boşluğu adayları. Metrik/rapor formatı SPEC'te.

---

## 5. Etiket eşlemesi — KADEMELİ (kullanıcı kararı, 2026-07-13)

TrMor Oflazer-etiketi (`hazine+Noun+A3sg+Pnon+Nom`) ↔ turkgram analiz-uzayı (`{kind: decline,
case: nom, …}`) hizalaması. Diferansiyel harness'in temel taşı + en hataya-açık kısım (elle yazılır).
**Karar: kademeli** — kaba hizalama hızlı çalışır, ince eksenler veriye bakarak derinleştirilir
(SPEC felsefesi "bağımsız golden gerçek bug yakalar" ile aynı: hangi eksenin gerçekten ayrışmaya
sebep olduğunu ampirik gör, sonra eşle).

### Artım-1 — kök + major POS (ilk sürüm, harness'i işlevsel kılar)

Yalnız **lemma + kaba POS** hizalanır; ince eksenler (durum/zaman/iyelik) göz ardı. Eşleme:

| TrMor major POS | turkgram karşılığı |
|-----------------|--------------------|
| `Noun` (+`Prop`) | isim (kind=`decline`/`copula`; kök=lemma) |
| `Verb` | fiil (kind=`conjugate`/`converb*`/`participle`; kök=lemma) |
| `Adj` | sıfat |
| `Adverb` | zarf |
| `Postp` | edat |
| `Num`, `Det`, `Pron`, `Punc`, `Conj`, `Interj` | sayı/belirteç/zamir/noktalama/bağlaç/ünlem |

Hizalama birimi: **(kök, major-POS)** çifti. `^DB` (türetme sınırı) zincirinde **son inflectional
group'un POS'u** major-POS alınır (Oflazer geleneği: yüzeyin nihai sözcük-türü). Kök = ilk group'un
lemması. Artım-1 harness ayrışması yalnız kaba düzeyde (isim↔fiil↔sıfat karışması) yakalanır.

### Artım-2 — tam eksen eşlemesi (ikinci sürüm, kendi golden'ıyla)

Oflazer inflectional-özellikleri → turkgram eksenleri (elle, en dikkatli kısım):

| Oflazer | turkgram eksen |
|---------|----------------|
| `A1sg/A2sg/A3sg/A1pl/A2pl/A3pl` | person (1sg…3pl) |
| `Pnon/P1sg/P2sg/P3sg/P1pl/P2pl/P3pl` | iyelik |
| `Nom/Acc/Dat/Loc/Abl/Gen/Ins` | case |
| `Pos/Neg` | negative |
| `Past/Narr/Fut/Aor/Pres/Prog1(Iyor)/Cond/…` | tense/mood |
| `Caus/Pass/Reflex/Recip` | voice zinciri |
| `PresPart/FutPart/PastPart/AorPart` | participle |
| `Inf1/Inf2/Inf3/Ness/Zero` | isimleştirme/participle türü |
| `^DB` | kind sınırı / türetme (delegasyon deseni, CLAUDE.md §6c) |

Artım-2 SPEC alt-bölümü + BAĞIMSIZ golden ile gelir; Artım-1 çalışıp gerçek ayrışmalar görüldükten
sonra hangi eksenlerin öncelikli olduğu veriyle belirlenir. **Recall-güvenli:** eşleme yalnız
karşılaştırma için; `analyze` aday uzayını DEĞİŞTİRMEZ.

**TUZAK:** Oflazer envanteri ≠ turkgram envanteri birebir değil (Oflazer `Prog1`=`-Iyor`, `Narr`=evid;
turkgram kendi kind/eksen adları). Eşleme TEK-YÖNLÜ sözlük (Oflazer→turkgram), bilinmeyen etiket →
`unmapped` işaretlenir (harness'te ayrı sınıf, sessizce eşleşmiş sayılmaz — recall-güvenli).

---

## 6. İş akışı ve golden planı (CLAUDE.md §2)

SPEC (bu dosya, elle) → bağımsız golden (Opus, motor-körü) → motor (çarpımsal+HMM+harness) →
hakem + korpus taraması. Golden istatistik modelinden BAĞIMSIZ kurulur.

**Golden'ın bağımsızlığı (kritik):** İstatistiksel modelin çıktısına BAKMADAN kurulur. Üç golden türü:
- **Sayım golden'ı:** küçük, elle-kurulmuş mini-korpustan (5–10 cümle) beklenen geçiş/emisyon
  sayımları elle hesaplanır → motor aynı sayımları üretmeli (model matematiği doğrulanır).
- **Viterbi golden'ı:** elle-tasarlanmış belirsiz cümlelerde (ör. `yüzü` = yüz+iyelik / yüz+isim /
  yüz-fiil) beklenen HMM yolu elle-çözülür → motor Viterbi'si eşleşmeli.
- **Eşleme golden'ı:** seçili Oflazer-etiketi → turkgram-eksen çiftleri elle-doğrulanır (Artım-1
  kök+POS; Artım-2 eksen). Bilinmeyen etiket → `unmapped` beklenir (sessiz-eşleşme YOK).

**Hakem:** gömülü leksikon + TrMor gold üzerinde 0 çökme + harness agreement raporu makul (kural ve
HMM gold'a yakın, çarpımsal daha düşük — beklenen sıralama). Recall-güvenli: `analyze` çıktısı DEĞİŞMEZ.

---

## 7. Kompakt model gömme (leksikon/frekans emsali)

Ham TrMor gitignore'lu; wheel'e yalnız **türetilmiş kompakt model** girer (`data/` + MANIFEST +
package-data, `lemma_freq_tr.tsv` emsali). Üretici `tools/build_disambig_model.py` (ham korpus →
sayım → normalize → tsv). Gömülen tablolar (TSV, saf-olgu):

- `data/disambig_emission_tr.tsv` — (etiket-özellik → sayım/olasılık) emisyon.
- `data/disambig_transition_tr.tsv` — (etiket-bigram → sayım/olasılık) geçiş.
- Kelime-hazinesi/eşleme yardımcı tabloları gerektiğince.

Boyut hedefi: kaba-taneli etiket-uzayı + budama (nadir bigram eşiği). Determinizm: olasılıklar
dosyada sabit; float sıralama değil kanonik tie-break (disambiguation.py emsali).

---

## 8. API (opt-in giriş noktaları, `analyze` DOKUNULMAZ)

Yeni modül `turkgram/statistical.py` (öneri):
- `load_model()` → gömülü tsv'lerden kompakt model (lexicon.load emsali, opt-in).
- `rank_statistical(analyses, model=, method="hmm"|"product")` → izole/token sıralama.
- `viterbi(tokens, analyses_per_token, model=)` → cümle-düzeyi dizi çözümü (HMM).

Diferansiyel harness `tools/diff_harness.py` (gömülmez, geliştirme aracı): çarpımsal/HMM/kural/gold
ayrışma raporu. `context.rank_in_context` ve `disambiguation.rank` DOKUNULMAZ; bu katman AYRI.

---

## 9. Gelecek çalışma — CRF (defer, kullanım yerleri)

CRF şimdilik ERTELENDİ (§1). Aşağıdaki koşullardan biri doğarsa **üçüncü istatistiksel eksen**
olarak eklenir (o zaman değişmez-esnetme bilinçli kabul edilir):

1. **Harness "daha güçlü referans" gösterirse:** iki-model harness çalışıp gerçek ayrışmalar
   ölçüldükten sonra, HMM'in bigram varsayımı sistematik yetersiz kalıyorsa (zengin özellik
   gerektiren hatalar) → CRF daha iyi bir istatistiksel üst-sınır referansı sağlar.
2. **Zengin özellik gerektiğinde:** son-ek n-gram'ları, komşu-etiket pencereleri, biçim-bilgisi
   gibi HMM'in temsil edemediği özellikler kritik çıkarsa (CRF'in doğal üstünlüğü).
3. **Üretim fallback'i yüksek-doğruluk isterse:** katman üründe fallback'e dönüşürse ve en yüksek
   doğruluk gerekiyorsa, CRF **opt-in ekstra bağımlılık** olarak paketlenebilir (saf-Python çekirdek
   DOKUNULMAZ; `pip install turkgram[crf]` gibi ayrı ekstra → değişmez korunur).
4. **Nöral referans köprüsü:** CRF, ileride nöral dizi-etiketleyiciye (MorphNet emsali) geçişte
   ara istatistiksel referans olur.

CRF eklenirse: sklearn-crfsuite vb. dış bağımlılık **yalnız opt-in extra**; çekirdek saf-Python +
deterministik + MIT-gömülebilir KALIR (CLAUDE.md değişmezi). Serileştirme/determinizm o noktada
ayrıca çözülür.
