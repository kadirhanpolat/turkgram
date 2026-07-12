# analysis-spec.md — Çözümleyici (morphological analyzer), Faz 2a

**Kaynak tasarım:** `docs/faz2a-cozumleyici-tasarim.md` (onaylı) · **Kritik:**
`docs/faz2a-mimari-kritik.md`. Bu SPEC uygulamanın grammatical-invariant ölçütlerini
sabitler: ses-filtreleri, ters-mutasyon envanteri, çatı kapalı kümesi, kanonik kwargs,
segmentasyon kesim politikası. Motordan BAĞIMSIZ golden bu SPEC'ten kurulur.

---

## 1. Kapsanan paradigma (üretecin dili = beş `kind`)

| `kind` | Üreteç | Eksen uzayı (analizörün enumerate ettiği) |
|--------|--------|-------------------------------------------|
| `conjugate` | `morphology.conjugate` | tense∈**9** (pres,past,fut,aorist,evid,cond,necess,opt,imp) × person∈6 × negative × ability × question × aux∈{None,hikaye,rivayet,sart} × aspect∈{None,iver,adur,agel,akal,ayaz} × voice_chain∈24 |
| `decline` | `morphology_noun.decline` | case∈7 × possessive∈{None,6} × number∈{sg,pl} |
| `copula` | `morphology_noun.copula` | aux∈{None,hikaye,rivayet,sart} × person∈6 × case∈{None,7} × possessive∈{None,6} × number × question |
| `converb` | `nonfinite.converb` | kind∈8 (arak,ip,inca,madan,dikce,meksizin,eli,esiye) |
| `participle` | `nonfinite.participle` | ptype∈5 (dik,acak,ma,mak,is) × possessive∈{None,6} × case∈{None,7} |

**TUZAK — `conv_arak`/`part_dik` conjugate'ten ÇIKARILIR:** `conjugate`'in TENSES demeti
bu ikisini içerir ama yüzeyleri `converb`/`participle` kind'larının alt kümesidir (gelerek,
geldiği). Çift-kapsama ve `kind` çakışmasını önlemek için analizör bunları YALNIZ
converb/participle kind'ı olarak üretir; conjugate grid'i 9 finite tense ile sınırlıdır.
Round-trip süpürmesi (test §4.1) de conjugate'i 9 tense ile koşar.

`predicative`/`with_ki`/`equative`/`equative` `copula`(None aux = geniş/bildirme) ve
`decline` yüzeyinin alt kümesidir:
- `predicative(hw, person=p)` ≡ `copula(hw, None, p)` (aynı fonksiyon; copula None-aux dalı
  predicative'i çağırır) → `kind="copula", kwargs={aux:None?...}`. **Karar:** geniş-zaman
  bildirme `kind="copula"` altında `aux` anahtarı YOK (kanonik: aux=None atılır) + `person`.
- `with_ki` (evdeki) ve `equative` (evce) `decline` çekirdeğinin ÜSTÜNE ek katman; 2a'da
  `kind="decline"` alt-uzayında DEĞİL, ayrı ele alınır: **kapsam kararı** — `with_ki`/
  `equative` 2a'da `decline` kind'ı içinde `case="loc"/"gen"`+"ki" ve `-CA` olarak ÜRETİLMEZ
  (nadir, düşük değer); `paradigm_noun`'daki `ki.*`/`ca` anahtarları 2a round-trip
  süpürmesinde HARİÇ. (2b genişletme kapısı.) Bu, tek-seferlik kontrolün (tasarım §5)
  sonucudur: predicative copula'ya eşlenir; ki/ca 2a-dışı bırakılır.

---

## 2. Kombinatoryal güvenlik — ünlü-yuvası sınırı (BİRİNCİL guard)

**Değişmez:** Bir hipotezin ünlü-taşıyan morfem sayısı ≤ aday kök sonrası (suffix
bölgesindeki) ünlü sayısı. Her vowel-bearing morfem (tense -Iyor/-AcAk/…, aspect aux,
ekfiil, çatı eki -DIr/-Il/-Iş/-t, çoğul -lAr, iyelik, durum -A/-I…) en az bir ünlü yuvası
tüketir. Ünlüsüz morfemler (3sg-∅, nom-∅, bazı kişi ekleri) sayılmaz.

- Bu sınır **yapısal ve güvenli**: recall'u asla kırmaz (gerçek biçim zaten bu eşitsizliği
  sağlar) ama çatı zinciri derinliğini, aspect/aux çarpımını, uzun kwargs kombinasyonlarını
  aday kök başına doğal olarak budar. Kısa suffix → az morfem.
- Uygulama: hipotez üretimi ünlü-yuvası bütçesini aşan kombinasyonları erkenden eler
  (üreteç çağrılmadan).

**İkincil guard — ses filtreleri (§3):** ünlü-yuvası sınırından SONRA, her opsiyonel
eksene kanıtlanabilir-gerekli substring gate'i.

---

## 3. Ses-filtresi önermeleri (her biri: eksen işaretliyse yüzeyde X ZORUNLU)

Filtre **yanlız gereklilik** ifade eder → yanlış budayamaz (recall güvenli). Emin
olunamayan eksene filtre YOK (her zaman dene; yalnız maliyet). `[ıiuü]`=yüksek,
`[ae]`=alçak ünlü sınıfı; substring yüzeyin (tokenize sonrası gövde parçasının) herhangi
yerinde.

### 3.1 conjugate tense (yüksek değer — grid'in ana ekseni)
| tense | ZORUNLU substring | gerekçe |
|-------|-------------------|---------|
| `pres` | `yor` | -Iyor sabit |
| `fut` | `c[ae]` | -AcAk (k→ğ olsa da "ce"/"ca" kalır: geleceğim) |
| `evid` | `m[ıiuü]ş` | -mIş |
| `necess` | `m[ae]l[ıi]` | -mAlI |
| `cond` | `s[ae]` | -sA |
| `past` | `[dt][ıiuü]` | -DI (sertleşme dahil) |
| `aorist` | — | -Ir/-Ar/-r/-mAz çok şekilli → filtre YOK |
| `opt` | — | -A çıplak → YOK |
| `imp` | — | -∅/-sIn/-In → YOK |

### 3.2 Kesişen eksenler
| eksen | ZORUNLU | gerekçe |
|-------|---------|---------|
| `question=True` | ` m[ıiuü]` (boşluk + mI) | soru edatı ayrı token |
| `aux=hikaye` | `[dt][ıiuü]` | -(y)DI ekfiil |
| `aux=rivayet` | `m[ıiuü]ş` | -(y)mIş |
| `aux=sart` | `s[ae]` | -(y)sA |
| `aspect=iver` | `ver` | yardımcı kök |
| `aspect=adur` | `dur` | |
| `aspect=agel` | `gel` | |
| `aspect=akal` | `kal` | |
| `aspect=ayaz` | `yaz` | |
| `negative` | `m[ae]` | -mA / -mAz / -AmA hepsi "m"+alçak içerir |
| `ability` | `[ae]bil` VEYA `[ae]m[ae]` | -Abil (olumlu) / -AmA (olumsuz yeterlik) |

> `ability` iki-şıklı önerme: yeterlik olumlu -Abil ("ebil"/"abil"), olumsuz -AmA
> ("ama"/"eme") — ikisinden biri zorunlu (disjunction hâlâ gerekliliktir → güvenli).

### 3.3 Diğer kind'lar (küçük grid → az/hiç filtre)
- `decline`/`copula`/`converb`/`participle` grid'leri küçük (≤ birkaç yüz hücre, ünlü-yuvası
  sınırıyla daha da az) → yalnız güçlü olanlar: `copula aux=rivayet ⇒ m[ıiuü]ş`;
  `converb=dikce ⇒ kç`/`kc`; `participle=is ⇒ ş`. Gerisi filtresiz (maliyet düşük).

**Filtre sağlamlık yükümlülüğü (test §4.6 / Task 9.1):** her filtre için, filtrenin
budadığı ~200 rastgele hücre üretilir; hiçbirinin yüzeyi filtre-substring'ini İÇERMEMELİ.
Bir ihlal = filtre yanlış (gevşetilir). Gevşetme her zaman güvenli (recall↑, precision
oracle'da).

---

## 4. Ters-mutasyon envanteri (kök adayı çeşitleri — §1.1 tasarım)

Aday kök = yüzey gövde-parçasının öneki. Her önek için, üreteç yumuşama/düşme/ikizleşmesinin
TERSİ uygulanarak ek kök adayları üretilir (üreteç envanterinden, elle kopya değil):

| Yüzeyde görülen | Aday köke ekle | Üreteç kuralı (ileri) |
|-----------------|----------------|------------------------|
| `d` (son) | `t` | fiil git→gid; isim yumuşama t→d |
| `ğ` (son) | `k` | k→ğ (çok-heceli/istisna) |
| `b` (son) | `p` | p→b (kitap→kitab) |
| `c` (son) | `ç` | ç→c (amaç→amac) |
| `g` (son) | `k` (nk bağlamı) | nk→ng (renk→reng) |
| `i`/`ı`/… önek-sonu | ye_de: `e` (yi→ye, di→de) | ye_de e→i |
| düşen ünlü | son heceye harmoni-uyumlu yüksek ünlü geri-ekle (burn→burun) | drops_vowel |
| ikiz ünsüz (`kk`,`dd`) | tekleştir (hakk→hak, redd→ret) | doubles |

- Kural: ters-mutasyon YALNIZ önekin SON sesine/hecesine; her önek başına O(1) çeşit → aday
  kök sayısı ≤ len(yüzey) × ~6. Bütçe (test §4.5) gerçek koruma.
- Aday kök doğrulaması üreteçtedir: yanlış aday (mas- için "masmak") yalnız üreteç onu
  yüzeye götürürse kabul (ve `hypothetical=True` işaretli, C-03).

---

## 5. Çatı zinciri kapalı kümesi (24) — kritik C-04

Kanonik sıra (voice-spec §7): (refl|recip)? → caus{0..3} → pass? Enumerate:
```
dönüşlü/işteş katmanı ∈ { (), (refl,), (recip,) }        # 3
ettirgen katmanı     ∈ { (), (caus,), (caus,caus), (caus,caus,caus) }   # 4
edilgen katmanı      ∈ { (), (pass,) }                    # 2
```
Kartezyen = 3×4×2 = **24 zincir** (boş zincir `()` dahil = çatısız). `voice_chain=()` →
kwargs'ta `voice_chain` anahtarı YOK (kanonik). Ünlü-yuvası sınırı (§2) çoğu sözcükte
zinciri zaten () veya tek-morfeme indirir.

---

## 6. Kanonik kwargs (dedup + eşitlik + golden anahtarı) — kritik M-01

- **Default eksenler kwargs'ta YER ALMAZ.** Kind başına default:
  - `conjugate`: person=`3sg`? HAYIR — person daima açık (üreteç default'u 3sg ama analiz
    kişiyi belirler). Atılanlar: `negative=False`, `ability=False`, `question=False`,
    `aux=None`, `aspect=None`, `voice_chain=()`. **Kalan zorunlu:** `tense`, `person`.
  - `decline`: atılan `number="sg"`, `possessive=None`, `case="nom"`. En az biri kalmalı
    (hepsi default = yalın nom tekil → kwargs boş; geçerli, "ev" analizi).
  - `copula`: atılan `aux=None`, `case=None`, `possessive=None`, `number="sg"`,
    `question=False`. Kalan zorunlu: `person`. (Geniş bildirme "evdir" = person=3sg.)
  - `converb`: `kind` zorunlu (tek eksen).
  - `participle`: `ptype` zorunlu; atılan `possessive=None`, `case=None`.
- **`case='nom'` ≡ case YOK:** hiçbir kind'da `case='nom'` EMİT EDİLMEZ; "üstü örtük durum"
  okuması case-absent'tir. Enumerasyonda 'nom' ve None aynı kabul edilip atılır (yoksa
  `{ptype:ma}` ile `{ptype:ma,case:nom}` sahte-çift olur). Aynı şekilde `number='sg'`,
  `possessive=None`, `aux=None`, `question=False`, `voice_chain=()` daima atılır.
- Eşitlik/dedup anahtarı: `(lemma, pos, kind, frozenset(kanonik kwargs.items()))`.
- **Türkçe kwargs (tr.çözümle):** aynı kanonik yapı, değerler Türkçe kanonik temsilci
  (past→görülen_geçmiş, loc→bulunma, caus→ettirgen); voice_chain listesi Türkçe
  (["işteş","ettirgen","edilgen"]).

---

## 7. Segmentasyon kesim politikası — kritik C-02 (kendi golden'ı)

kwargs doğrulandıktan SONRA türetilir. `Segment(surface, label, span)` dizisi; dilimler
birleşince yüzeyi (tokenize sonrası gövde-parça) verir.

**Kesim yöntemi (incremental generation):** doğrulanmış kwargs'tan başlayıp eksenleri
TERS sırada tek tek KALDIR, her kaldırmada üreteç çıktısının kısaldığı ek O morfemin yüzey
dilimidir. Örn. `decline("ev", possessive="1sg", case="dat")` = "evime"; `case` kaldır →
"evim" → "e" durum dilimi; `possessive` kaldır → "ev" → "im" iyelik dilimi; kalan "ev" kök.
Bu, kesimi ÜRETEÇTEN türetir (elle segment-tahmini değil) → oracle-tutarlı.

**Etiket politikası:**
- Etiket = kanonik morfem adı (yüzey allomorf değil): iyelik-1sg → `Im`, durum-dat → `A`,
  görülen-geçmiş → `DI`, ortaç-dik → `DIk`, çoğul → `lAr`, kök → `KÖK` (ya da lemma).
- Kaynaştırma ünsüzü (-y-/-n-/-s-) SAĞdaki morfemin dilimine dahil: "arabası" →
  `araba · sı(3sg)`; "evine" → `ev · i(2sg?) · ne`? — pronominal -n- durum diliminin
  başında: `ev · i(3sg) · nde`. (Incremental yöntem bunu otomatik verir: farkın nerede
  başladığı kaynaştırmayı doğru tarafa koyar.)
- Yumuşama yüzey biçimiyle gösterilir: "okuduğum" → `oku · duğ(DIk) · um(Im)` (yüzey "duğ",
  etiket "DIk").
- span: her dilimin yüzeydeki [başlangıç, bitiş) ofseti; bitişik ve örtüşmez; birleşince
  gövde-parça yüzeyi.

**Belirsizlikte segment:** analiz belirsizse (birden çok Analysis) her Analysis kendi
segmentasyonunu taşır; golden yalnız tek-çözümlü yüzeylerle segmentasyonu sınar (Task 3
talimatı).

---

## 8. Giriş sözleşmesi (özet — tasarım §2)

- `analyze(surface, pos=None, *, roots=None) -> list[Analysis]`. `_tr_lower` normalizasyon
  (İ→i, I→ı). Boş/tip-hatası → `ValueError`; bilinmeyen pos → seçenek-listeleyen `ValueError`.
- Çözümsüz → `[]`. Çok-token yalnız iki kalıp (soru grubu: son token `m[ıiuü]…`; birleşik
  önek: baştaki token(lar) + kalan gövde → lemma "önek + gövde-lemması").
- Deterministik sıra: (morfem/segment sayısı ↑, çatısız<çatılı, `_KINDS.index(kind)`, lemma,
  repr(sorted kwargs)). `hypothetical` sıralamada rol almaz.
- `roots` (lemma kümesi) verilmişse lemma∉roots elenir, kalan `hypothetical=False`; aksi
  hepsi `hypothetical=True`.

### 8.1 Çıplak-önek gürültüsü ve `roots` (kritik — golden test kararı)
Leksikonsuz analizör, yüzeyin KENDİSİNİ ve her önekini çıplak-isim kökü olarak önerir
(üreteç doğrular): `decline("okuyor")="okuyor"`, `decline("evler",case="loc")="evlerde"`,
`decline("evlerde")="evlerde"` — hepsi üreteç-geçerli form-analizi (`hypothetical=True`),
ama gürültü. Bu, leksikonsuz analysis-by-generation'ın DOĞASIDIR (tasarım C-03).
- **Gerçek tüketici `roots` verir** (dict-db) → gürültü elenir, "ev" kalır "evler" düşer.
- **Precision golden testi `roots=LEKSIKON` ile koşulur** (küratörlü gerçek lemma kümesi);
  golden = roots-filtreli TAM küme. Filtresiz (`roots=None`) çıktı gürültü içerir → yalnız
  "her hypothetical, en az bir gerçek okuma ⊆ çıktı" gibi hafif testlerle sınanır, tam-küme
  DEĞİL.
- Round-trip süpürmesi (§ test) `roots`=süpürme lemma-seti ile ya da İÇERME (tam-küme değil)
  ile sınar; gürültü membership'i bozmaz.

### 8.2 Birleşik çok-token fiil — yardımcı fiille kurulan (Faz 2b)
Kaynak: Korkmaz *Şekil Bilgisi*, Birleşik Fiiller — yardımcı fiillerle kurulan birleşik fiil =
isim/isim-soylu unsur + yardımcı fiil (`et-`, `ol-`, `eyle-`, `kıl-`, `buyur-`, `yap-`…).
Yalnız KURAL alınmıştır; düzyazı/örnek KOPYALANMAZ (#3). Değişmez: **nominal unsur çekim
almaz; yalnız SON kelime (yardımcı fiil) çekimlenir.** Nominal unsur çok-kelimeli olabilir.

- **Kalıp:** Yüzey N token (N≥2), son token çekimli fiil; `tokens[:-1]` birleşimi = değişmez
  nominal önek. Lemma = `"<önek> <fiil-lemması>"` (ör. `göz ardı etti` → `göz ardı etmek`,
  past 3sg; `yok oldu` → `yok olmak`, past 3sg; `kabul ediyor` → `kabul etmek`, pres 3sg).
- **Genelleme:** Faz 2a'daki 2-token birleşik önek kalıbı (§8 madde 2) N-token'a genişler;
  `len>2 → []` erken-kesimi YALNIZ bu kalıp (soru-dışı, birleşik) için kalkar. Nominal önek
  yardımcı-fiil kapalı kümesine kısıtlanmaz — precision `roots`-garantilidir (aşağı).
- **Motor sözleşmesi:** Üreteç birleşik lemmayı zaten çeker (`conjugate("göz ardı etmek",…)`
  boşlukta böler, son kelimeyi çeker, öneki değişmez taşır). Analizör-tarafı iş YALNIZ önek
  uzunluğu genellemesi; yeni morfoloji YOK.
- **Precision `roots`-garantili (§8.1):** `"<önek> <fiil-lemması>"` ancak `roots`'ta gerçek
  birleşik lemma ise `hypothetical=False` üretilir; ikileme+leksik-fiil (`katıla katıla
  gülmek`) sözlük-lemması değilse elenir. `roots=None` → hypothetical gürültü (doğal, §8.1).
- **Kapsam-dışı (bu artım; 2b içinde ertelendi):**
  (a) **Birleşik + soru** (`göz ardı etti mi`): çok-token soru yolu (§8 madde 1) tek-token
      önek varsayar; N-token önekli soru dalı ayrı iş.
  (b) **İkileme'nin adverbial yeniden-kurulumu** (`katıla katıla` = -A ulaç ikilemesi zarf-öbeği
      + leksik fiil): kompozisyonel değil sözdizimsel çözümleme → defer. Bu artımda ikileme
      yalnız sözlük-lemması olarak (roots'ta varsa) birleşik-lemma gibi geçer.

---

## 9. Bağımsızlık ve golden

- Golden'lar (precision `golden_analysis.py`, segmentasyon `golden_segments.py`) motoru
  GÖRMEDEN, bu SPEC + dilbilgisinden kurulur (CLAUDE.md §2; iki bağımsız türetme, A1 emsali).
- Korkmaz düzyazı/örneği repoya girmez (#3); golden elle-doğrulanmış biçimlerden.
- Precision golden TAM-küme eşitliği sınar (fazla çözüm = precision hatası); round-trip
  süpürmesi içerme sınar (recall).
