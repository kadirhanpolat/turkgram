# TR Fiil Çekim Motoru — v1 SPEC (roadmap 2a, CLAUDE.md #5)

Bu belge, motorun **dilbilgisel değişmezlerini** ve **API sözleşmesini** kilitler.
Motoru yazan ajan da golden tabloyu kuran ajan da BUNA uyar; ikisi bağımsız çalışır,
anlaşmazlıkları hakem (ana oturum) çözer. Üçüncü ağ: `zeyrek` çapraz-analizi.

Kapsam kararı (2026-07-11, kullanıcı): **yalnız fiil**, **geniş paradigma**,
**golden + zeyrek** doğrulama.

---

## 1. Girdi / çıktı sözleşmesi (API — DEĞİŞMEZ)

Dosya: `morphology.py` (repo kökü). Saf Python, dış bağımlılık YOK (zeyrek yalnız testte).

```python
# Kök + morfofonolojik parametreler (mastar "gelmek"ten türetilir + istisna tablosu)
def parse_verb(lemma: str) -> VerbStem

# Tek biçim üret
def conjugate(lemma: str, tense: str, person: str | None = None,
              *, negative: bool = False, ability: bool = False) -> str

# Tam paradigma (aşağıdaki tüm tense × person, olumlu+olumsuz)
def paradigm(lemma: str) -> dict
```

- `lemma`: mastar biçimi, **"-mek/-mak" ekli** ("gelmek", "tanımak", "okumak").
  Birleşik/hafif-fiil ("aday olmak", "arzu etmek") → **yalnız SON token çekilir**,
  önceki tokenlar aynen öne eklenir (`inflect_last_token` yardımcı).
- `person`: `'1sg' '2sg' '3sg' '1pl' '2pl' '3pl'` | ulaç/ortaç gibi kişisizlerde `None`.
- Çıktı: tek string, küçük harf, Türkçe karakterlerle.

### Tense anahtarları (geniş set)
| anahtar | ek | ad |
|---|---|---|
| `pres` | -Iyor | şimdiki zaman |
| `past` | -DI | görülen geçmiş |
| `fut` | -AcAk | gelecek |
| `aorist` | -Ir/-Ar/-r | geniş zaman |
| `evid` | -mIş | öğrenilen geçmiş |
| `cond` | -sA | dilek-şart |
| `necess` | -mAlI | gereklilik |
| `imp` | (kişi ekleri) | emir |
| `conv_arak` | -ArAk | ulaç (kişisiz) |
| `part_dik` | -DIğI | ortaç (kişisiz, 3sg iyelikli varsayılan) |

`ability=True` → köke **-Abil-** yeterlik eki eklenir, sonra tense (yapabiliyor,
gelebilir). `negative=True` → olumsuzluk (-mA-); geniş zamanda olumsuz özel
(gelmem/gelmez, aşağıda).

---

## 2. Morfofonoloji (kurallar — üret, saklama)

### 2.1 Ünlüler
- Arka: `a ı o u` · Ön: `e i ö ü`
- Düz: `a e ı i` · Yuvarlak: `o ö u ü`

### 2.2 Ünlü uyumu
- **A-tipi (2'li, alçak):** son ünlü arka → `a`, ön → `e`.
- **I-tipi (4'lü, yüksek):**
  - arka+düz → `ı` · ön+düz → `i` · arka+yuvarlak → `u` · ön+yuvarlak → `ü`
- Harmoni **kökün (ya da bir önceki ekin) SON ünlüsüne** bakar; ek zinciri boyunca
  ilerledikçe harmoni kaynağı güncellenir.

### 2.3 Ünsüz uyumu (ek-başı sertleşme)
Kök/gövde **sert ünsüzle** biterse (`f s t k ç ş h p` — "fıstıkçı şahap"),
ek-başı yumuşak ünsüz sertleşir:
- `-DI → -tI` (yaptı, geçti) · `-DIğI → -tIğI` (yaptığı) · `-DIr → -tIr`

### 2.4 Kaynaştırma ünsüzü `y`
Ünlüyle biten kök + ünlüyle başlayan ek arasında `y`:
- bekle + AcAk → bekle**y**ecek · oku + AcAk → oku**y**acak · anla + A → anla**y**a

### 2.5 -Iyor (şimdiki zaman) — özel kural
1. Kök ünsüzle biter → harmonik yüksek ünlü ekle: gel-**i**-yor, yaz-**ı**-yor, gör-**ü**-yor, sor-**u**-yor.
2. Kök ünlüyle biter → **son ünlü DÜŞER**, harmonik yüksek ünlü + yor:
   - başla → başl-**ı**-yor · bekle → bekl-**i**-yor · oku → ok-**u**-yor · yürü → yür-**ü**-yor
   - Bu kural ye/de'yi de doğru üretir: ye → y-**i**-yor = **yiyor**, de → **diyor**.
3. Olumsuz -mA da ünlüyle biter → aynı düşme: gelme → gelm-**i**-yor = **gelmiyor**;
   yapma → yapm-**ı**-yor = **yapmıyor**.
4. -Abil + -Iyor: gelebil-**i**-yor = gelebiliyor.

### 2.6 Aorist (geniş zaman) — LEKSİK bayrak gerekir
- Ünlü-final kök → `-r`: bekle-r, oku-r, anla-r.
- **Tek heceli ünsüz-final:** VARSAYILAN `-Ar` (yap-ar, yaz-ar, gel... İSTİSNA).
  - **13 istisna → `-Ir/-Ur`** (leksik `aorist='Ir'`): **al-ır, bil-ir, bul-ur, dur-ur,
    gel-ir, gör-ür, kal-ır, ol-ur, öl-ür, san-ır, var-ır, ver-ir, vur-ur**.
    (gülmek, sarmak vb. DÜZENLİ -Ar: güler, sarar.)
- **Çok heceli ünsüz-final** → `-Ir/-Ur` (4'lü harmoni): getir-ir, otur-ur, çalış-ır, düşün-ür.
- **Olumsuz geniş zaman ÖZEL** (ek DEĞİL, kalıp):
  - 1sg: -mAm (gelmem, yapmam) · 1pl: -mAyIz (gelmeyiz)
  - 2sg: -mAzsIn · 3sg: -mAz · 2pl: -mAzsInIz · 3pl: -mAzlAr
  - Yani olumlu -Ir/-Ar yerine olumsuzda -mA(z) tabanı; 1. kişilerde z düşer.

### 2.7 Kök-içi ünsüz yumuşaması — LEKSİK bayrak
Ünlüyle başlayan ek önünde kök-sonu sertleşen ünsüz yumuşar (`softens=True`):
- **git → gid** (gidiyor, gidecek, gider ama git-ti sert kalır — yumuşama yalnız ÜNLÜ önünde)
- **et → ed** (ediyor, edecek) · **tat → tad** · **güt → güd**
- Bağlı sette: **gitmek, etmek**. (tatmak/gütmek bağlı sette yok ama tabloya ekle.)
- DİKKAT: yumuşama YALNIZ ünlü-başlı ek önünde; ünsüz-başlı ek (-DI, -mIş) önünde
  kök sert kalır: git-ti (gitti), et-ti (etti) — d DEĞİL.

### 2.8 ye / de özel sınıfı — LEKSİK bayrak `special='ye_de'`
Kök ünlüsü `e`, **kaynaştırma -y- girdiği her yerde** (= ünlü-başlı ek önünde) `e→i`:
- ye + AcAk → yiyecek · ye + ArAk → **yiyerek** · ye + Abil → **yiyebilir** · ye + En → yiyen · ye + Iyor → yiyor
- de + AcAk → diyecek · de + ArAk → **diyerek** · de + Iyor → diyor
- AMA **ünsüz-başlı ek** önünde (kaynaştırma yok) NORMAL, e korunur:
  **yer/der** (aorist -r), **yedi/dedi** (-DI), **yemiş** (-mIş), **yese/dese** (-sA),
  **yemeli** (-mAlI).
- DÜZELTİLMİŞ KURAL (2026-07-11, golden hakem): e→i tetikleyici **yüksek ünlü DEĞİL**,
  **kaynaştırma -y- ekleme**dir. Ünlü-başlı ek → -y- girer → e→i (alçak ünlü olsa bile:
  yiyerek, yiyecek). Ünsüz-başlı ek → -y- yok → e kalır (yer, yedi). aorist -r ÜNSÜZ →
  **yer** (yir DEĞİL).

---

## 3. Kişi ekleri (şahıs)

### 3.1 Grup 1 (-DI ve -sA sonrası: k-tipi)
| kişi | ek |
|---|---|
| 1sg | -m (geldim, gelsem) |
| 2sg | -n (geldin, gelsen) |
| 3sg | ∅ (geldi, gelse) |
| 1pl | -k (geldik, gelsek) |
| 2pl | -nIz (geldiniz, gelseniz) |
| 3pl | -lAr (geldiler, gelseler) |

### 3.2 Grup 2 (-Iyor, -AcAk, -Ir, -mIş, -mAlI sonrası: z-tipi)
| kişi | ek |
|---|---|
| 1sg | -Im (geliyorum, geleceğim, gelirim, gelmişim, gelmeliyim) |
| 2sg | -sIn (geliyorsun) |
| 3sg | ∅ (geliyor) |
| 1pl | -Iz (geliyoruz) |
| 2pl | -sInIz (geliyorsunuz) |
| 3pl | -lAr (geliyorlar) |

- **-AcAk + 1sg/1pl'de k→ğ yumuşaması:** gelecek+im → gelece**ğ**im, gelece**ğ**iz.
  (k, ünlü-başlı iyelik/kişi eki önünde ğ olur.) 3pl gelecekler (k korunur, -lAr ünsüz-başlı).
- **-mAlI + kişi:** -mAlI zaten ünlü-final → 1sg gelmeli-y-im (kaynaştırma y): gelmeliyim.

### 3.3 Emir (imp)
- 2sg: ∅ (gel! yap! oku!) — kökün kendisi.
- 3sg: -sIn (gelsin, yapsın)
- 2pl: -In / -InIz (gelin/geliniz, yapın/yapınız); ünlü-final: oku-yun
- 3pl: -sInlAr (gelsinler)
- (1sg/1pl emir yok; varsa None döndür.)

---

## 4. Olumsuz (-mA-)

- Taban: kök + **-mA** (4'lü değil, 2'li: gel-me, yap-ma, oku-ma).
- Sonra tense normal işler, AMA -mA ünlü-final olduğundan:
  - +Iyor → -mA düşer: gelme→gelmiyor, yapma→yapmıyor (§2.5.3).
  - +AcAk → kaynaştırma y: gelmeyecek, yapmayacak.
  - +DI → gelmedi, yapmadı.
  - Aorist olumsuz → §2.6 ÖZEL kalıp (gelmem/gelmez), -mA+Ir DEĞİL.
- ability + negative: -AmA- (gelemem, yapamıyor) — yeterliğin olumsuzu -A + mA
  (gel-e-me-mek → gelememek). v1'de `ability=True, negative=True` →
  köke -A(y)ama- tabanı: gel-e-me, yap-a-ma → sonra tense.

---

## 5. -Abil yeterlik (ability=True)
- Taban: kök + kaynaştırma + **-Abil-**: gel-e-bil, yap-a-bil, oku-y-abil.
- Sonra tense taban olarak `-Abil` gövdesine uygulanır (gövde ünsüz-final `l`):
  gelebil+Iyor→gelebiliyor, gelebil+ecek→gelebilecek, gelebil+ir→gelebilir.
- Olumsuz yeterlik (§4 son madde): -AmA-.

---

## 6. İstisna tablosu (motorun içinde, küçük kapalı küme)

```python
IRREGULAR = {
  # aorist -Ir/-Ur alan 13 tek-heceli
  'almak':'Ir','bilmek':'Ir','bulmak':'Ir','durmak':'Ir','gelmek':'Ir',
  'görmek':'Ir','kalmak':'Ir','olmak':'Ir','ölmek':'Ir','sanmak':'Ir',
  'varmak':'Ir','vermek':'Ir','vurmak':'Ir',
  # kök yumuşaması (t→d ünlü önünde)
  'gitmek':'soft','etmek':'soft','tatmak':'soft','gütmek':'soft',
  # ye/de sınıfı
  'yemek':'ye_de','demek':'ye_de',
}
```
Bir fiil hem aorist-Ir hem soft OLABİLİR mi? Bu sette hayır; ama yapı iki ayrı
bayrak taşısın (`aorist_ir: bool`, `softens: bool`, `special: str|None`).

---

## 7. Golden test tablosu (bağımsız ajan kurar)

En az **35 fiil**, her biri için elle-doğrulanmış beklenen biçimler. Kapsamı ZORUNLU:
1. Düz ünsüz-final çok-heceli: **anlamak, çalışmak, düşünmek, oturmak, konuşmak**
2. Ünlü-final: **oku(mak), bekle(mek), başla(mak), yürü(mek), ara(mak)**
3. Tek-heceli -Ir aorist: **gelmek, almak, olmak, görmek, vermek, bilmek, durmak**
4. Tek-heceli -Ar aorist (düzenli): **yapmak, yazmak, bakmak, sarmak, gülmek**
5. Yumuşama: **gitmek, etmek**
6. ye/de: **yemek, demek**
7. Yuvarlak-ünlü harmoni: **okumak, görmek, konuşmak, yürümek, gülmek**
8. Ettirgen/uzun gövde (düzenli olduğunu doğrula): **anlatmak, güldürmek, temizlemek**

Her fiil için EN AZ şu hücreler (3sg + 1sg örnekleri):
- pres 3sg/1sg, past 3sg/1sg, fut 3sg/1sg, aorist 3sg (+olumsuz 3sg), evid 3sg,
  cond 3sg, necess 3sg, imp 2sg/2pl, conv_arak, ability pres 3sg, negative pres 3sg.

Format: `tests/golden_verbs.py` → `GOLDEN = { 'gelmek': {'pres.3sg':'geliyor', ...}, ... }`.
Beklenen biçimler **motordan DEĞİL**, dilbilgisinden türetilir (bağımsızlık şart).

---

## 8. zeyrek çapraz-kontrol (üçüncü ağ)
`tests/test_morphology.py` içinde: `pip install zeyrek` varsa, üretilen HER biçim
zeyrek ile analiz edilir; **çözümlerden biri lemma köküne (mastarsız kök) geri
dönmeli**. zeyrek yoksa test `skip`. zeyrek bazı biçimleri tanımayabilir → tanınmayan
biçimler `xfail` listesine değil, RAPORA yazılır (motor hatası mı zeyrek eksiği mi
hakem karar verir). zeyrek ASLA golden'ın yerine geçmez — golden birincil.

---

## 10. İstek kipi (opt) + Soru (question) — v1.1 (2026-07-11, tam çekim tablosu için)

Tam kip haritası (5 haber + 4 dilek) için iki ekleme. Klasik dilbilgisi: haber
kipleri = pres/past/evid/fut/aorist; dilek kipleri = necess/**opt**/cond/imp.

### 10.1 İstek kipi (optative, `-A`)
İşaretleyici `-A` (2'li harmoni a/e), ünlü-final gövdede kaynaştırma `-y-`.
Ardından istek kişi ekleri (işaretleyici ünlüsüne uyumlu):
- 1sg `-yIm`, 2sg `-sIn`, 3sg `-∅`, 1pl `-lIm`, 2pl `-sInIz`, 3pl `-lAr`.

`gelmek`→ geleyim/gelesin/gele/gelelim/gelesiniz/geleler ·
`almak`→ alayım/alasın/ala/alalım/alasınız/alalar ·
`okumak`(ünlü-final)→ okuyayım/okuyasın/okuya/… (kaynaştırma -y-) ·
`yemek`(ye_de)→ yiyeyim/… · `gitmek`(soft)→ gideyim/… ·
olumsuz `gelmemek`→ gelmeyeyim/… (taban gelme + -y-e) ·
ability `gelebilmek`→ gelebileyim/… (taban -Abil + -A).
`-A` ünlü-BAŞLI ek → yumuşama/ye_de TETİKLER (gid-e, yi-y-e); mevcut
`_stem_before_suffix(vowel_initial=True)` yeniden kullanılır.

### 10.2 Soru (interrogative, `-mI`) — YÖN: tense değil, BOYUT
Soru edatı `mI` (4'lü harmoni mı/mi/mu/mü, önceki sözcüğün son ünlüsüne göre)
**AYRI yazılır** (boşluklu). Yerleşimi kişi-eki TİPİNE bağlıdır:

- **z-tipi zamanlar** (pres/fut/evid/aorist/necess — Grup 2 kişi ekleri):
  `mI` tense-gövdesinden SONRA, kişi eki `mI`'ye biner (pronominal klitik).
  Gövde = o zamanın 3sg biçimidir (3sg eki ∅). `geliyor muyum / musun / mu /
  muyuz / musunuz`, 3pl İSTİSNA: `-lAr` fiilde kalır, `mI` sonra → `geliyorlar mı`.
  `gelecek miyim` (dikkat: haber `geleceğim` DEĞİL — soru bare -AcAk + mI + kişi),
  `gelir miyim`, `gelmiş miyim`, `gelmeli miyim`, olumsuz aorist `gelmez miyim`.
- **k-tipi zamanlar** (past/cond + **opt** — Grup 1 kişi ekleri): kişi eki FİİLDE,
  `mI` en SONA (tam çekimli biçim + boşluk + mI).
  `geldim mi / geldin mi / geldi mi / geldik mi / geldiniz mi / geldiler mi`;
  `gelsem mi`; istek `geleyim mi / gele mi / gelelim mi`.
- **imp/conv_arak/part_dik**: soru UYGULANMAZ (None).

`mI = "m" + high_vowel(önceki_sözcük)`; z-tipi kişi `mI`'ye: 1sg `-yIm` 2sg `-sIn`
3sg `-∅` 1pl `-yIz` 2pl `-sInIz` (mI ünlü-final → 1sg/1pl kaynaştırma -y-).

### 10.3 API
`conjugate(lemma, tense, person, *, negative, ability, question=False)`; yeni
tense `"opt"`. `paradigm` `opt`'u ekler (9 kip tam). Golden bağımsız: `opt` tam
paradigma + `question` örnekleri her tip için (pres/fut/aorist/past/cond/opt).

---

## 11. Birleşik zaman (ek-fiil / `aux`) — v1.2 (2026-07-11, tam çekim tablosu)

Birleşik zaman = BASİT kip gövdesi + **ek-fiil** (i-di/i-miş/i-se) + kişi. Ek-fiil,
basit kipin 3sg biçimine (bare gövde) eklenir. `aux ∈ {None, hikaye, rivayet, sart}`.

- **Hikâye** (`hikaye`, i-di): gövde + `-(y)DI` + Grup-1 kişi (k-tipi). D sertleşme
  gövdenin son ünsüzünden (gelecek→gelecekti, geliyor→geliyordu, gelmiş→gelmişti);
  ünlü-final gövdede kaynaştırma -y- (gelmeli→gelmeliydi, gel**se**→gelseydi).
- **Rivayet** (`rivayet`, i-miş): gövde + `-(y)mIş` + Grup-2 kişi (z-tipi).
  geliyormuş(um), gelecekmiş, gelirmiş, gelmeliymiş.
- **Şart** (`sart`, i-se): gövde + `-(y)sA` + Grup-1 kişi. geliyorsa(m), gelirse.

**Olumsuz/yeterlik BEDAVA:** ek-fiil basit gövdeye eklendiğinden `negative`/`ability`
zaten gövdede işler (gelmiyordu / gelebiliyordu / gelmezdi). Ayrı iş YOK.

**3pl kuralı (tutarlı):** `-lAr` BASİT gövdede kalır, ek-fiil 3sg olarak eklenir
(geliyor**lar**dı, gelecek**ler**di, gelmiş**ler**di, gelir**ler**di). "geliyordular"
DEĞİL. (Gereklilik/istek/şartta gelmeli**ler**di gibi biçimler daha az yaygın ama
dilbilgisel; motor tutarlılığı için tek kural.)

**Soru × birleşik (`question=True, aux=...`):** `mI` edatı gövde ile ek-fiil ARASINA
girer, ek-fiil+kişi `mI`'ye biner: gövde + " " + `mI` + `-(y)EKFİİL` + kişi.
geliyor muydum (geliyor+mu+y+du+m), gelir miymişim, gelecek miydi. 3pl: base3pl +
" " + mI + ek-fiil-3sg (geliyorlar mıydı). imp/ulaç/ortaç aux almaz → None.

`aux` `paradigm`'e GİRMEZ (basit kalır); tam çekim tablosu doğrudan conjugate çağırır.

---

## 9. Çıktı entegrasyonu (v1 sonu)
Motor `entries.morph` alanını DOLDURMAZ (şema saklamayı reddediyor, #5) — motor
RUNTIME üreticidir. Ama `parse_verb` çıktısı (aorist_ir/softens/special/harmoni
sınıfı) istenirse morph JSONB'ye yazılabilir bir sözlük döndürür; bu v1'de opsiyonel.
Kart ürünü (card.py) ileride `paradigm()` çağırır (roadmap 2c).
