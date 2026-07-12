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
