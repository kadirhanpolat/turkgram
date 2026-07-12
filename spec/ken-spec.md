# -ken zarf-fiili (iken) — SPEC (Faz 2b / motor-dışı biçim 2)

Ana oturum tarafından elle yazılmış **dilbilgisel değişmez** (Korkmaz §683 "-ken" /
ek-fiil "iken" ekleşmesi). Golden bu SPEC'ten **motordan bağımsız** kurulur.
`nonfinite-spec.md` bu eki "A5 DIŞI (biçim-eklenen / copula işi)" diye erteliyordu.

## Kapsam

`-ken` = **çekimli fiil gövdesi VEYA nominal yüklem** üstüne binen zaman zarf-fiili
("… -iken / … iken"). İki bağlanma:
- **Fiil (finit taban):** aorist/şimdiki/-mIş/-AcAk 3sg tabanı + `ken`.
  `gelir → gelirken`, `geliyor → geliyorken`, `gelmiş → gelmişken`, `gelecek → gelecekken`.
- **Nominal (ek-fiil iken):** ad/sıfat (+ durum) + `(y)ken`.
  `çocuk → çocukken`, `hasta → hastayken`, `evde → evdeyken`.

## DEĞİŞMEZ ÇEKİRDEK: `-ken` ÜNLÜ UYUMUNA GİRMEZ

`-ken` **donmuş** ektir; ünlü uyumu YOKtur. Daima `"ken"`:
`okurken` (kan DEĞİL), `bakarken`, `olurken`, `çocukken`, `kapıdayken`. Bu, golden'ın
en kritik değişmezi — motorun harmoni sezgisi buraya UYGULANMAZ.

## API

```python
# Fiil:
def converb_ken(lemma: str, *, base: str = "aorist", negative: bool = False) -> str
# Nominal (copula genişletmesi):
copula(headword, aux="ken", *, case=None, possessive=None, number="sg") -> str
```
`base ∈ {"aorist", "pres", "evid", "fut"}`. Her ikisi de KİŞİSİZ (kişi uyumu YOK;
"gelirdimken" gibi biçim YOKtur).

## Yapı (DEĞİŞMEZ)

### Fiil
1. Finit taban = `conjugate(lemma, base, "3sg", negative=negative)` (motordan aynen).
2. Sonuç = `taban + "ken"`. Glide YOK — finit taban daima ünsüzle biter.

### Nominal
1. Gövde = `decline(headword, case=…, possessive=…)` (durum verilmezse yalın).
2. Glide `y` = gövde ünlüyle bitiyorsa "y", yoksa "".
3. Sonuç = `gövde + y + "ken"`.

## Elle-doğrulanmış hücreler (golden bağımsız kursun)

### Fiil — aorist tabanı (base="aorist")
| lemma | aorist 3sg | -ken |
|-------|-----------|------|
| gelmek | gelir | gelirken |
| gitmek | gider | giderken |
| okumak | okur | okurken |
| bakmak | bakar | bakarken |
| gülmek | güler | gülerken |
| olmak | olur | olurken |
| yapmak | yapar | yaparken |

### Fiil — diğer tabanlar
| lemma | base | taban 3sg | -ken |
|-------|------|-----------|------|
| gelmek | pres | geliyor | geliyorken |
| gelmek | evid | gelmiş | gelmişken |
| gelmek | fut | gelecek | gelecekken |
| okumak | pres | okuyor | okuyorken |
| gitmek | fut | gidecek | gidecekken |

### Fiil — olumsuz (negative=True)
| lemma | base | taban neg 3sg | -ken |
|-------|------|---------------|------|
| gelmek | aorist | gelmez | gelmezken |
| gelmek | pres | gelmiyor | gelmiyorken |
| gelmek | fut | gelmeyecek | gelmeyecekken |

### Nominal (copula aux="ken")
| headword | case | gövde | (y)ken | not |
|----------|------|-------|--------|-----|
| çocuk | — | çocuk | çocukken | ünsüz-final → glide YOK |
| öğretmen | — | öğretmen | öğretmenken | |
| genç | — | genç | gençken | |
| hasta | — | hasta | hastayken | ünlü-final → glide y |
| ev | loc | evde | evdeyken | evde ünlü-final → y |
| okul | loc | okulda | okuldayken | ünlü-final → y |
| kapı | loc | kapıda | kapıdayken | |

## Kritik değişmezler (golden yakalasın)
- **`ken` DEĞİŞMEZ:** hiçbir bağlamda kan/kön/kun OLMAZ. Kalın-ünlülü tabanda bile ken.
- **Fiil tabanında glide YOK:** geliyorken (geliyoryken DEĞİL), gelecekken.
- **Nominal glide yalnız ünlü-final gövdede:** hastayken/evdeyken (y var), çocukken/gençken (y yok).
- **-AcAk + ken çift-k korunur:** gelecekken (gelecekken; k düşmez/yumuşamaz).

## Golden zorunlu kapsam
En az 7 aorist + 5 diğer-taban + 3 olumsuz + 7 nominal hücre; kalın/ince, ünlü/ünsüz-final,
durum-lu/yalın nominal. Her hücre elle-doğrulanmış. `ken` değişmezliği her satırda sağlanmalı.

---

# ÇÖZÜMLEME (analysis) — Faz 2b, motor-dışı biçim 2

`analyze` `-ken` yüzeylerini (gelirken, evdeyken) geri tanımıyordu. Bu bölüm çözümleme
sözleşmesini kilitler. İki bağlanma → iki çözüm yolu:

## Fiil `-ken` → YENİ kind `converb_ken`

- `kind = "converb_ken"`, `pos = "verb"`. `_KINDS` sırasına `converb_casina`'dan SONRA.
- Kanonik kwargs: `base` **daima** (`aorist`|`pres`|`evid`|`fut`); `negative` yalnız True.
  Örnek: `gelirken → {base:aorist}`; `gelmiyorken → {base:pres, negative:True}`.
- Enum: `base ∈ {aorist,pres,evid,fut} × negative ∈ {F,T}` = **8 hipotez**; `_KEN_MARKER`
  = `ken$` gereklilik filtresi (recall-güvenli; marker yoksa hiç enumerate etme).
- Kök adayı: mevcut önek+ters-mutasyon + `-Iyor` ünlü-düşme kurtarması (pres tabanı
  `geliyorken`/`oynuyorken`) YETERLİ — yeni mantık GEREKMEZ.
- Segmentasyon DELEGASYON (A3 emsali, casina §6g gibi): `base_form=conjugate(lemma,base,
  "3sg",neg)` dilimlerini `_segment_conjugate`'ten al + tek `(surface[len(base_form):], "ken")`
  dilimi. Glide YOK → `ken` dilimi daima tam "ken".

## Nominal `-ken` → MEVCUT kind `copula` (aux="ken")

Yeni kind YOK; üretim de `copula(aux="ken")`. Çözümleyici copula enum'ına `"ken"` ekler:
- `_COPULA_AUX`'a `"ken"`; `("copula_aux","ken") → /ken/` filtresi.
- **`ken` KİŞİSİZ + soru YOK:** enum yalnız `person="3sg", question=False` üretir (kişi
  kombinasyonu patlaması yok). Kanonik kwargs: `{aux:"ken"[, case][, possessive][, number]}` —
  **person ve question ATILIR** (`_canon_copula` aux=="ken" özel dalı). Örnek:
  `çocukken → {aux:ken}`; `evdeyken → {aux:ken, case:loc}`.
- Segmentasyon: mevcut `_segment_copula` aux dalı ölçer (kaynaştırma -y- SAĞdaki `ken`
  diliminde: `ev|de|yken`). `aux:ken` etiketi = "ken".

## BELİRSİZLİK (golden yakalasın)

`-ken` yüzeyi hem fiil hem isim okunabilir: `gelirken` = (gelmek aorist +ken) VEYA
(**gelir** "income/gelir" isim + ken nominal). roots ikisini de içeriyorsa İKİ analiz döner.
Precision golden bunu `roots={ilgili lemma}` ile ayrıştırır; her yüzey için o roots kümesinde
geçerli TÜM okumalar beklenir. `giderken` = gitmek VEYA **gider** (isim) benzer.

## Round-trip değişmezi (hakem)

- Fiil: `converb_ken(lemma, base, negative)` her yüzey `analyze(…, roots={lemma})` ile
  `(lemma,"verb","converb_ken",{base[,negative]})` verir. Leksikon × 4 base × 2 neg → 0 miss.
- Nominal: `copula(headword, "ken", case=c)` her yüzey `analyze(…, roots={headword})` ile
  `(headword,"noun","copula",{aux:"ken"[,case]})` verir. Leksikon isimleri × durum → 0 miss.

## Kapsam dışı
Kişili `-ken` YOKtur (üretimde de yok). Kişisizlik değişmez.
