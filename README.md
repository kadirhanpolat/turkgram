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
| Çatı (voice) | `turkgram.voice` | **`apply_voice`** (ettirgen/edilgen/dönüşlü/işteş + yığılma) |
| İsim çekimi | `turkgram.morphology_noun` | `decline`, `paradigm_noun`, `predicative`, **`copula`**, `with_ki`, `equative` |
| Fiilimsi | `turkgram.nonfinite` | **`converb`** (ulaç), **`participle`** (sıfat-fiil/ad-fiil + iyelik/durum) |
| Yapım eki (türetme) | `turkgram.derivation` | `derivations` |
| **Çözümleme (parse)** | `turkgram.analysis` | **`analyze`** (yüzey → kök+eksen + segmentasyon) |
| Türkçe yüz | `turkgram.tr` | `çekimle`, `ad_çekimle`, `ekfiil`, `ulaç`, `fiilimsi`, `türet`, **`çözümle`** |

Fiil: 9 kip (5 haber + 4 dilek) + birleşik zaman + soru + olumsuz + yeterlik +
**tasvir** (tezlik/sürerlik) + **çatı** (ettirgen/edilgen/dönüşlü/işteş, yığılabilir →
dövüştürüldü). İsim: durum × iyelik × çokluk + ekfiil/-ki/-CA, pronominal -n-, **nominal
ek-fiil kopula** (öğrenciydim). Fiilimsi: **8 ulaç** + **sıfat-fiil/ad-fiil + iyelik/durum
istifi** (okuduğum/gitmesini).

**Çözümleme (Faz 2a):** üretimin tersi — yüzey biçimden kök + eksen değerleri + pedagojik
morfem dökümü. *Analysis-by-generation*: üreteç tek doğruluk kaynağı (analizör yalnız
üretecin üretebildiği çözümleri döndürür → biçim-precision inşa gereği garanti).

## Durum / Yol haritası

- **Faz 0 ✅** — bağımsız paket, motor + testler taşındı, Türkçe API (`tr.py`).
- **Faz 1 ✅** (fiil çekim derinleştirme — `docs/faz1-implementation-plan.md`):
  A4 nominal ek-fiil · A5+A6 ulaç envanteri + aorist · A2 tasvir fiilleri · A3
  fiilimsi+iyelik/durum istifi · **A1 çatı** (ettirgen/edilgen/dönüşlü/işteş + yığılma).
- **Faz 2a ✅** — çözümleyici (`analysis.py`, `tr.çözümle`; `docs/faz2a-*`): yüzey →
  kök+eksen + segmentasyon (beş kind). Round-trip sistematik sınıflarda doğrulandı, korpus
  0 çökme. `-Iyor` ünlü-düşmesi, suppletif zamir eğik durumu (`bana`/`sana`) ve nominal
  ekfiil soru grubu (`evde miydi`) kapatıldı. Kalan 2b açığı: birleşik çok-token fiil
  (`göz ardı etmek`); ayrıntı: tasarım §3.1.
- **Faz 2b** — gerçek-metin sağlamlığı (leksikon + disambiguation). **Faz 3/4** — türetme
  genişletme, sıfat/zamir, sözdizimi. Boşluk analizi: `docs/faz1-bosluk-analizi.md`.

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

# Çatı (voice) — yığılabilir
tg.conjugate("dövmek", "past", "3sg", voice_chain=["recip","caus","pass"])  # 'dövüştürüldü'

# Çözümleme (parse) — yüzey → kök + eksen + segmentasyon
tg.analyze("okuduğum", roots={"okumak"})       # [Analysis(lemma='okumak', kind='participle',
                                               #   kwargs={'ptype':'dik','possessive':'1sg'},
                                               #   segments=(oku|duğ[DIk]|um[Im]), ...)]
tg.analyze("bana", roots={"ben"})              # suppletif zamir → decline(case='dat')
tg.analyze("evde miydi", roots={"ev"})         # nominal ekfiil soru → copula(case='loc',
                                               #   aux='hikaye', question=True)
tg.analyze("göz ardı etti", roots={"göz ardı etmek"})  # birleşik çok-token fiil (§8.2)

# Gömülü kök leksikonu (opt-in) — çıplak-önek gürültüsünü eler
from turkgram import lexicon
roots = lexicon.load()                         # ~26k lemma (Zemberek, Apache-2.0)
tg.analyze("evler", roots=roots)               # → yalnız [ev, decline(number='pl')]
lexicon.load("verb")                           # POS filtreli (fiil mastarları)
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
tr.çekimle("dövmek", "geçmiş", "3tekil", çatı=["işteş","ettirgen","edilgen"]) # dövüştürüldü
tr.fiilimsi("gitmek", "ma", iyelik="3tekil", durum="belirtme")   # gitmesini
tr.çözümle("dövüştürüldü", kökler={"dövmek"})   # [Analysis(... çatı=[işteş,ettirgen,edilgen])]
```

Fonksiyon: `çekimle`/`çekim_tablosu`/`fiil_çöz` · `ad_çekimle`/`ad_çekim_tablosu`/`ad_çöz` ·
`ekfiil`/`yüklem`/`ki_ekle`/`eşitlik` · `türet` · **`çözümle`** (çözümleme; Türkçe eksen
değerleri + segment). Parametre: `kip`/`kişi`/`olumsuz`/`yeterlik`/`soru`/`birleşik`/**`çatı`** ·
`durum`/`iyelik`/`sayı`. Çekim tablosu anahtarları da Türkçe (`şimdiki.3tekil`, `çoğul.bulunma`).

## Testler

```bash
pip install -e ".[test]"
pytest
```

Golden testler (`tests/golden_*.py` — fiil/isim/copula/ulaç/fiilimsi/tasvir/çatı ve
çözümleme/segmentasyon) motordan **bağımsız** olarak, elle-doğrulanmış biçimlerle
kurulmuştur — motorun kendi çıktısıyla değil, dilbilgisiyle sınanır. Round-trip tam
süpürme `-m slow` ile: `pytest -m slow`.

## Lisans

MIT. (Gramer kuralları olgudur; telifli metin içermez — bu yüzden dağıtılabilir.)

Gömülü kök leksikonu (`turkgram/data/lexicon_tr.tsv`) **Zemberek-NLP** projesinin
`master-dictionary` sözlüğünden türetilmiş lemma+POS olgularını içerir (Apache-2.0);
atıf ve değişiklik beyanı [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md).
