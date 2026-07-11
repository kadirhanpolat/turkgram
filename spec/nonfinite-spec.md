# Fiilimsi (Nonfinite) — SPEC (Faz 1 / A5: zarf-fiil / ulaç)

Ana oturum tarafından elle yazılmış **dilbilgisel değişmez** (Korkmaz §677 zarf-fiil).
Golden bu SPEC'ten **motordan bağımsız** kurulur. Bu belge A5'in ULAÇ bölümünü kilitler;
sıfat-fiil/ad-fiil (A3) ve iyelik/durum istifi ayrı bölümde eklenecek.

## Kapsam (A5)

**Zarf-fiil (ulaç)** = fiil kökünden kişisiz zarf üreten ekler. A5 yalnız **kök-eklenen**
(root-attaching) ulaçları üretir. `-ken`, `-cAsInA`, `-DIğIndA` gibi **biçim-eklenen**
(çekimli gövde/ortaç üstüne binen) ulaçlar A5 DIŞI (ek-fiil/A3 işidir; aşağıda not).

## API

```python
def converb(lemma: str, kind: str) -> str
```
`kind ∈ {arak, ip, inca, madan, eli, dikce, meksizin, esiye}`. `lemma` mastar ("gelmek").
Türkçe API: `turkgram.tr.ulaç(fiil, tür)`.

## Morfofonoloji (yeniden kullanım)

Kök varyantı `morphology._stem_before_suffix(vs, vowel_initial)` ile alınır (yumuşama
git→gid, ye_de ye→yi YALNIZ ünlü-başlı ekte). Ünlü-final kök + ünlü-başlı ek → kaynaştırma
`-y-`. Bu, motorun `conv_arak` (-ArAk) üretimiyle BİREBİR tutarlıdır.

## Ulaç ekleri (DEĞİŞMEZ)

Aşağıda `stem_v` = `_stem_before_suffix(vs, True)` (ünlü-başlı: yumuşamalı), `stem_c` =
`_stem_before_suffix(vs, False)` (ünsüz-başlı: çıplak kök). `y` = ünlü-final kökte "y".
`A` = alçak (a/e, low_vowel), `I` = yüksek 4'lü (ı/i/u/ü, high_vowel), `Iyi` = A'nın
frontness'ine göre YÜKSEK-DÜZ (a→ı, e→i; yuvarlaklık YOK).

| kind | ek | taban | gerçekleme | örnekler |
|------|----|-------|-----------|----------|
| `arak` | -ArAk | stem_v | `+ y? + A + "r" + A + "k"` | gelerek, okuyarak, giderek, yiyerek, yaparak |
| `ip` | -Ip | stem_v | `+ y? + I + "p"` (4'lü) | gelip, yapıp, okuyup, gülüp, gidip, yiyip |
| `inca` | -IncA | stem_v | `+ y? + I + "nc" + A` | gelince, yapınca, okuyunca, gidince, yiyince |
| `eli` | -AlI | stem_v | `+ y? + A + "l" + Iyi` | geleli, yapalı, okuyalı, gideli, göreli |
| `esiye` | -AsIyA | stem_v | `+ y? + A + "s" + Iyi + "y" + A` | ölesiye, gülesiye, patlayasıya, dövesiye |
| `madan` | -mAdAn | stem_c | `+ "m" + A + "d" + A + "n"` | gelmeden, gitmeden, okumadan, yemeden, yapmadan |
| `dikce` | -DIkçA | stem_c | `+ D + I + "kç" + A` (D=t/d sertleşme) | geldikçe, gittikçe, okudukça, yedikçe, yaptıkça |
| `meksizin` | -mAksIzIn | stem_c | `+ "m" + A + "ks" + Iyi + "z" + Iyi + "n"` | gelmeksizin, gitmeksizin, okumaksızın, yapmaksızın |

### Kritik harmoni notları (golden yakalasın)
- **`-Ip` / `-IncA` YÜKSEK ünlüsü 4'lü (yuvarlak duyarlı):** okuyup/okuyunca (u), gülüp (ü),
  gelip (i), yapıp (ı). `high_vowel(stem_v)` doğrudan.
- **`-AlI` / `-AsIyA` / `-mAksIzIn` YÜKSEK ünlüsü DÜZ (Iyi):** -A'dan sonra gelen yüksek ünlü
  yuvarlaklığı KAYBEDER → okuyalı (u→a→ı DEĞİL, ı), okumaksızın (ı). `Iyi = "i" if
  low_vowel(stem)=="e" else "ı"`.
- **Ünsüz-başlı ekte (madan/dikce/meksizin) YUMUŞAMA YOK:** gitmeden (gidmeden DEĞİL),
  gittikçe, gitmeksizin — stem_c çıplak kök. ye_de de tetiklenmez: yemeden (yiyeden DEĞİL),
  yedikçe.
- **`-DIkçA` sertleşme:** git→gittikçe (t), yap→yaptıkça (t); gel→geldikçe (d).
- **Kaynaştırma -y- yalnız ünlü-final kök + ünlü-başlı ek:** okuyarak/okuyup/okuyunca/okuyalı;
  okumadan/okudukça (ünsüz-başlı → y YOK).

## Golden zorunlu kapsam (bağımsız ajan)
8 ulaç × en az 8 fiil sınıfı: düz ünsüz çok-heceli (yapmak/okumak→ünlü-final/çalışmak),
ünlü-final (oku/bekle/ara), yumuşama (git/et), ye_de (ye/de), yuvarlak (oku/gül/gör),
tek-heceli. Her fiil × her uygulanabilir ulaç. Kritik hücreler: giderek/gitmeden/gittikçe
(yumuşama var/yok), yiyerek/yemeden (ye_de var/yok), okuyalı/okumaksızın (düz yüksek).
~64 hücre, elle-doğrulanmış.

## A5 DIŞI (biçim-eklenen ulaçlar — not)
- **`-ken`** (gelir-ken, evde-y-ken): ÇEKİMLİ gövde/nominal üstüne biner (ek-fiil -ken) →
  copula/aux işi. A5'te YOK.
- **`-cAsInA`** (gelir-cesine, gelmiş-çesine): AORİST/ortaç üstüne biner → biçim-eklenen. A5'te YOK.
- **`-DIğIndA`** (geldiğinde): sıfat-fiil -DIk + iyelik + durum (loc) = fiilimsi+durum istifi
  → A3 işi. A5'te YOK.

## A6 — Aorist -Ir istisna listesi doğrulama
Motorun 13 tek-heceli -Ir/-Ur listesi (al/bil/bul/dur/gel/gör/kal/ol/öl/san/var/ver/vur)
Korkmaz/Ergin/Banguoğlu üçlüsünde IDENTIK kanonik settir → doğrulandı, ekleme YOK.
(Golden zaten -Ir vs -Ar ayrımını kapsıyor: gelir/gülер, yapar/alır.)
