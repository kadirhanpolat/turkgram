# Fiilimsi + İyelik/Durum İstifi — SPEC (Faz 1 / A3)

Ana oturum tarafından elle yazılmış **dilbilgisel değişmez** (Korkmaz §677 sıfat-fiil/
ad-fiil). Golden bu SPEC'ten **motordan bağımsız** kurulur. Adlaşmış yan cümle çekirdeği.

## Kavram

Nominalize eden fiilimsi = fiilden AD gövdesi üretir; bu gövde İYELİK + DURUM alır
(adlaşmış yan cümle: *okuduğum kitap*, *gitmesini istedim*, *geldiğinde*). Motor iki
adımdır: (1) fiilimsi bare gövdeyi fiil primitifleriyle KUR; (2) gövdeyi İSİM ÇEKİM
motoruna (`decline`) besle — iyelik/durum, k→ğ yumuşaması, pronominal -n- oradan gelir.

## API

```python
def participle(lemma: str, kind: str, *,
               possessive: str | None = None, case: str | None = None) -> str
```
`kind ∈ {dik, acak, ma, mak, is}`. iyelik/durum verilmezse bare fiilimsi döner.
Türkçe: `tr.fiilimsi(fiil, tür, *, iyelik, durum)`.

## Bare fiilimsi gövdeleri (fiil primitifleri)

`stem_v` = ünlü-başlı varyant (yumuşama/ye_de: git→gid, ye→yi); `stem_c` = çıplak kök;
`y` = ünlü-final kökte kaynaştırma; `A` alçak, `I` yüksek-4'lü.

| kind | ek | tür | taban | gerçekleme | örnek |
|------|----|-----|-------|-----------|-------|
| `dik` | -DIk | sıfat-fiil | stem_c | `+ D + I + "k"` (D sertleşme) | okuduk, gittik, geldik, gördük |
| `acak` | -AcAk | sıfat-fiil | stem_v | `+ y? + A + "c" + A + "k"` | gelecek, gidecek, okuyacak, yiyecek |
| `ma` | -mA | ad-fiil | stem_c | `+ "m" + A` | gelme, gitme, okuma |
| `mak` | -mAk | ad-fiil (mastar) | stem_c | `+ "m" + A + "k"` | gelmek, gitmek, okumak |
| `is` | -Iş | ad-fiil | stem_v | `+ y? + I + "ş"` (4'lü) | geliş, gidiş, okuyuş, görüş |

**Bare gövdedeki yumuşama/ye_de:** yalnız ünlü-başlı taban (acak/is) tetikler: **gid**ecek,
**yi**yecek, **gid**iş; ünsüz-başlı (dik/ma/mak) tetiklemez: **git**tik, **git**me, **ye**me.

## İyelik/durum istifi (İSİM motoruna delege)

Bare gövde `decline(bare, possessive=..., case=...)` ile çekilir. İSİM motoru şunları
GETİRİR (yeniden kullanım — ayrı iş YOK):
- **k→ğ yumuşaması** (çok-heceli k-final → ünlü-başlı iyelik önünde): okuduk→**okuduğum**,
  gelecek→**geleceğim**, gördük→**gördüğüm**.
- **Pronominal -n-** (3. kişi iyelik + durum): gitme→gitme-si→**gitmesini** (acc),
  geldik→geldiği→**geldiğinde** (loc).
- İyelik buffer'ları, çoğul, durum ekleri.

## Kritik biçimler (golden yakalasın)
- **okuduğum / geleceğim / gördüğüm** — k→ğ (dik/acak + iyelik).
- **gitmesini** (gitme+si+n+i) / **geldiğinde** (geldik+i+n+de) — pronominal -n- (3. kişi + durum).
- **gitmem** (gitme+m, ünlü-final 1sg) / **gelmemizi** (gelme+miz+i).
- **gidecek/gidiş** (yumuşama, ünlü-başlı) vs **gittik/gitme** (yumuşama YOK, ünsüz-başlı).
- **yiyecek/yiyiş** (ye_de) vs **yedik/yeme** (ye_de YOK).

## -mAk mastarının defektifliği (SPEC notu)
Mastar -mAk AD olarak DEFEKTİFtir: belirtme/yönelme -mA üstünden gider (*gitmeyi*/*gitmeye*,
git**me**+yi/ye — git**mek**+i DEĞİL). -mAk yalnız yalın/ayrılma/bulunma alır (gitmek, gitmekten,
gitmekte). **A3 kapsamı:** `mak` için yalnız {yalın, abl, loc} durumları test edilir; acc/dat
istenirse `ma`'ya yönlendirilir (motor mekanik üretir ama golden mak+acc/dat KOYMAZ — defektif).

## Golden zorunlu kapsam (bağımsız ajan)
5 kind × fiil sınıfları (düz/ünlü-final/yumuşama/ye_de/yuvarlak) × iyelik(6) + durum örnekleri
+ pronominal -n- (3. kişi + acc/loc/dat). ~120 hücre, elle-doğrulanmış.
