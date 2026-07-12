# -cAsInA "gibilik/benzerlik" zarf-fiili — SPEC (Faz 2b / motor-dışı biçim 1)

Ana oturum tarafından elle yazılmış **dilbilgisel değişmez** (Korkmaz §684 benzerlik/
gibilik zarf-fiili). Golden bu SPEC'ten **motordan bağımsız** kurulur. `nonfinite-spec.md`
bu eki "A5 DIŞI (biçim-eklenen ulaç)" diye açıkça erteliyordu; burada kilitleniyor.

## Kapsam

`-cAsInA` = **çekimli fiil gövdesi üstüne binen** zarf-fiil ("sanki … -iyormuş gibi").
Kök-eklenen (A5) ulaçların aksine, **finit taban** üstüne gelir:
- **geniş zaman (aorist) tabanı** — kanonik: `güler → gülercesine`, `yapar → yaparcasına`.
- **-mIş (evid) tabanı** — `gelmiş → gelmişçesine`, `yapmış → yapmışçasına`.

Bu SPEC yalnız bu iki fiil tabanını kapsar. Nominal-eklenen (`delicesine`, `aptalcasına`)
ve `-AcAk` tabanı KAPSAM DIŞI (sonraki iş).

## API

```python
def converb_casina(lemma: str, *, base: str = "aorist", negative: bool = False) -> str
```
`base ∈ {"aorist", "evid"}`. `lemma` mastar ("gelmek"). Kişisiz (kişi uyumu YOK).

## Yapı (DEĞİŞMEZ)

1. **Finit taban** = motorun `conjugate(lemma, base, "3sg", negative=negative)` çıktısı.
   Bu tabana DOKUNULMAZ — `-cAsInA` onun üstüne biner. (gelir/güler/yapar/okur/gider;
   gelmiş/yapmış/gitmiş/okumuş; olumsuz: gelmez/yapmaz.)
2. **Ek** = `-CAsInA`, tabanın **son sesine** göre gerçeklenir:
   - `C` = **ç** eğer taban sert ünsüzle bitiyorsa (hardens), yoksa **c**.
   - `A` = alçak ünlü (a/e), tabanın **son ünlüsünün** kalın/inceliğine göre.
   - `Iyi` = YÜKSEK-DÜZ (yuvarlaklık YOK): `A=="a"` ise **ı**, `A=="e"` ise **i**.
   - Gerçekleme: `taban + C + A + "s" + Iyi + "n" + A`.

Ünlü glide (-y-) YOKtur: finit taban daima ünsüzle biter → ek doğrudan eklenir.

## Elle-doğrulanmış hücreler (golden bağımsız kursun)

### aorist tabanı (base="aorist")
| lemma | aorist 3sg | -cAsInA | not |
|-------|-----------|---------|-----|
| gelmek | gelir | gelircesine | son ünsüz r→c, son ünlü i→e/i |
| gülmek | güler | gülercesine | son ünlü e→e/i |
| yapmak | yapar | yaparcasına | r→c, a→a/ı |
| okumak | okur | okurcasına | son ünlü u→a/ı (DÜZ: ı, yuvarlak DEĞİL) |
| gitmek | gider | gidercesine | yumuşama tabandan gelir (gid-) |
| bakmak | bakar | bakarcasına | |
| almak | alır | alırcasına | -Ir istisna |
| görmek | görür | görürcesine | son ünlü ü→e/i (DÜZ: i) |

### -mIş (evid) tabanı (base="evid")
| lemma | evid 3sg | -cAsInA | not |
|-------|----------|---------|-----|
| gelmek | gelmiş | gelmişçesine | ş sert → ç |
| yapmak | yapmış | yapmışçasına | ş → ç, a→a/ı |
| gitmek | gitmiş | gitmişçesine | ş → ç |
| okumak | okumuş | okumuşçasına | son ünlü u→a/ı (DÜZ) |
| görmek | görmüş | görmüşçesine | ş → ç, son ünlü ü→e/i (DÜZ) |

### olumsuz (negative=True, aorist)
| lemma | aorist neg 3sg | -cAsInA |
|-------|----------------|---------|
| gelmek | gelmez | gelmezcesine |
| yapmak | yapmaz | yapmazcasına |
| okumak | okumaz | okumazcasına |

## Kritik değişmezler (golden yakalasın)
- **Son ünlü DÜZ-yüksek:** okur → okur**casına** (ı), okurcusuna DEĞİL; görür → görür**cesine** (i).
  Yuvarlaklık `Iyi`'ye taşınmaz.
- **c/ç yalnız son sesten:** gelir(r)→c, gelmiş(ş)→ç, gelmez(z)→c. Kök değil, TABANIN sonu.
- **Taban motordan aynen:** yumuşama (gid-), -Ir istisnası (alır/görür), olumsuz (gelmez)
  hepsi `conjugate` çıktısında zaten çözülü; bu ek onları değiştirmez.

## Golden zorunlu kapsam
En az 8 aorist + 5 evid + 3 olumsuz hücre; kalın/ince, düz/yuvarlak, yumuşama, -Ir istisna,
tek/çok-heceli çeşitliliği. Her hücre elle-doğrulanmış (motora bakmadan).
