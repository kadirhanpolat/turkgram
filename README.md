# turkgram

**Türkiye Türkçesi grameri, kod olarak.** Betimleyici başvuru gramerlerinden
(Zeynep Korkmaz *Türkiye Türkçesi Grameri*, Muharrem Ergin, Jean Deny, Hanifi Vural)
elle küratörlenmiş dilbilgisel değişmezleri **çalıştırılabilir kurallara** döken
saf-Python, bağımlılıksız bir kütüphane.

> Bu kütüphane bir gramer *kitabını* kopyalamaz — kitaplardaki **kuralları/olguları**
> (telifsiz) koda çevirir; düzyazı ve örnek cümleler alınmaz. İstisnalar küçük kapalı
> tablolarda tutulur, düzenli biçimler runtime **üretilir** (saklanmaz).

## Kapsam (encode/üretim)

| Alan | Modül | Başlıca API |
|------|-------|-------------|
| Fiil çekimi | `turkgram.morphology` | `conjugate`, `paradigm`, `parse_verb`, `inflect_last_token` |
| İsim çekimi | `turkgram.morphology_noun` | `decline`, `paradigm_noun`, `predicative`, **`copula`**, `with_ki`, `equative` |
| Fiilimsi | `turkgram.nonfinite` | **`converb`** (ulaç), **`participle`** (sıfat-fiil/ad-fiil + iyelik/durum) |
| Yapım eki (türetme) | `turkgram.derivation` | `derivations` |
| Türkçe yüz | `turkgram.tr` | `çekimle`, `ad_çekimle`, `ekfiil`, `ulaç`, `fiilimsi`, `türet` |

Fiil: 9 kip (5 haber + 4 dilek) + birleşik zaman + soru + olumsuz + yeterlik +
**tasvir** (tezlik/sürerlik). İsim: durum × iyelik × çokluk + ekfiil/-ki/-CA, pronominal
-n-, **nominal ek-fiil kopula** (öğrenciydim). Fiilimsi: **8 ulaç** + **sıfat-fiil/ad-fiil
+ iyelik/durum istifi** (okuduğum/gitmesini).

## Durum / Yol haritası

- **Faz 0 ✅** — bağımsız paket, motor + testler taşındı, Türkçe API (`tr.py`).
- **Faz 1** (fiil çekim derinleştirme — `docs/faz1-implementation-plan.md`):
  ✅ A4 nominal ek-fiil · ✅ A5+A6 ulaç envanteri + aorist doğrulama · ✅ A2 tasvir
  fiilleri · ✅ A3 fiilimsi+iyelik/durum istifi · ⏳ **A1 çatı** (ettirgen/edilgen/
  dönüşlü/işteş entegre çekim + yığılma — kalan, en zor).
- **Faz 2** — çözümleme/analiz (parse); **Faz 3/4** — türetme genişletme, sıfat/zamir,
  sözdizimi. Boşluk analizi: `docs/faz1-bosluk-analizi.md`.

Geliştirme kuralları (SPEC → bağımsız golden → motor → hakem): `CLAUDE.md`.

## Kurulum

```bash
pip install -e .
```

## Kullanım

```python
import turkgram as tg

tg.conjugate("gelmek", "pres", "1sg")          # 'geliyorum'
tg.conjugate("gitmek", "past", "3sg", negative=True)  # 'gitmedi'
tg.decline("kitap", case="dat")                # 'kitaba'
tg.decline("ev", possessive="3sg", case="loc") # 'evinde'
tg.derivations("göz", "noun")                  # [-lIk, -CI, -lI, ... türevleri]
tg.paradigm("okumak")                          # tam çekim tablosu (dict)
```

## Türkçe API (`turkgram.tr`)

Türkçe adlı paralel katman — içeride aynı çekirdeği çağırır (`docs/tr-api-tasarim.md`).
Terimler karma: kanonik akademik + tanıdık alias (`görülen_geçmiş` ≡ `dili_geçmiş`).

```python
import turkgram.tr as tr
tr.çekimle("gelmek", "şimdiki", "1tekil")                       # geliyorum
tr.çekimle("gitmek", "görülen_geçmiş", "3tekil", olumsuz=True)  # gitmedi
tr.ad_çekimle("ev", iyelik="3tekil", durum="bulunma")           # evinde
tr.ekfiil("öğrenci", "hikaye", "1tekil")                        # öğrenciydim
tr.türet("göz", "isim")                                         # -lIk/-CI… türevleri
tr.ulaç("gitmek", "arak")                                       # giderek
tr.çekimle("yapmak", "görülen_geçmiş", "3tekil", tasvir="tezlik") # yapıverdi
tr.fiilimsi("gitmek", "ma", iyelik="3tekil", durum="belirtme")   # gitmesini
```

Fonksiyon: `çekimle`/`çekim_tablosu`/`fiil_çöz` · `ad_çekimle`/`ad_çekim_tablosu`/`ad_çöz` ·
`ekfiil`/`yüklem`/`ki_ekle`/`eşitlik` · `türet`. Parametre: `kip`/`kişi`/`olumsuz`/`yeterlik`/
`soru`/`birleşik` · `durum`/`iyelik`/`sayı`.

## Testler

```bash
pip install -e ".[test]"
pytest
```

Golden testler (`tests/golden_verbs.py`, `tests/golden_nouns.py`) motordan
**bağımsız** olarak, elle-doğrulanmış biçimlerle kurulmuştur — motorun kendi
çıktısıyla değil, dilbilgisiyle sınanır.

## Lisans

MIT. (Gramer kuralları olgudur; telifli metin içermez — bu yüzden dağıtılabilir.)
