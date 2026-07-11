# turkgram

**Türkiye Türkçesi grameri, kod olarak.** Betimleyici başvuru gramerlerinden
(Zeynep Korkmaz *Türkiye Türkçesi Grameri*, Muharrem Ergin, Jean Deny, Hanifi Vural)
elle küratörlenmiş dilbilgisel değişmezleri **çalıştırılabilir kurallara** döken
saf-Python, bağımlılıksız bir kütüphane.

> Bu kütüphane bir gramer *kitabını* kopyalamaz — kitaplardaki **kuralları/olguları**
> (telifsiz) koda çevirir; düzyazı ve örnek cümleler alınmaz. İstisnalar küçük kapalı
> tablolarda tutulur, düzenli biçimler runtime **üretilir** (saklanmaz).

## Kapsam (v0.1 — Faz 0)

Şu an yalnız **çekim/türetme ÜRETİMİ** (encode):

| Alan | Modül | Başlıca API |
|------|-------|-------------|
| Fiil çekimi | `turkgram.morphology` | `conjugate`, `paradigm`, `parse_verb`, `inflect_last_token` |
| İsim çekimi | `turkgram.morphology_noun` | `decline`, `paradigm_noun`, `parse_noun`, `predicative`, `with_ki`, `equative` |
| Yapım eki (türetme) | `turkgram.derivation` | `derivations` |

Fiil: 9 kip (5 haber + 4 dilek) + birleşik zaman (ek-fiil hikâye/rivayet/şart) +
soru boyutu + olumsuz + yeterlik. İsim: durum × iyelik × çokluk + ekfiil/-ki/-CA
katmanları, pronominal -n-, yumuşama/ünlü-düşmesi kuralı + istisna tablosu.

### Sonraki fazlar
- **Faz 1** — çekim derinleştirme (Korkmaz boşluk analizi: çatı, birleşik fiil, istisnalar)
- **Faz 2** — **çözümleme/analiz** (parse: biçim → kök + ekler; en büyük yeni bileşen)
- **Faz 3** — türetme genişletme · **Faz 4** — sözdizimi/cümle bilgisi

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
