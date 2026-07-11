# Tasvir Fiilleri (Aktionsart) — SPEC (Faz 1 / A2)

Ana oturum tarafından elle yazılmış **dilbilgisel değişmez** (Korkmaz §472 "Durum ve
Tasvir Bildiren Fiiller"). Golden bu SPEC'ten **motordan bağımsız** kurulur.

## Kavram

Tasvir fiili = ESAS fiil + bağlama ünlüsü + **yardımcı (tasvir) fiil**; oluşan birleşik
gövde bir FİİL gibi çekilir. Yardımcı fiil kaynaşmıştır (sözlüksel değil).

| aspect | ek | yardımcı | bağ ünlü | işlev | örnek |
|--------|----|----------|----------|-------|-------|
| `iver` | -Iver- | ver | **-I** (yüksek 4'lü) | **tezlik** (çabuk/kolay) | yapıver, geliver, okuyuver |
| `adur` | -Adur- | dur | -A (alçak) | **sürerlik** (devam) | gidedur, bakadur |
| `agel` | -Agel- | gel | -A | sürerlik (öteden beri) | çekegel, süregel |
| `akal` | -Akal- | kal | -A | **kalma** (donup kalma) | bakakal, donakal |
| `ayaz` | -Ayaz- | yaz | -A | **yaklaşma** (az kalsın) | düşeyaz, öleyaz |

## API

`conjugate(lemma, tense, person, *, negative, ability, question, aux, aspect=None)`;
`aspect ∈ {iver, adur, agel, akal, ayaz}`. Türkçe: `tr.çekimle(..., tasvir=...)`
(`tezlik`≡iver, `sürerlik`≡adur, `yaklaşma`≡ayaz).

## Kurallar (DEĞİŞMEZ)

### 1. Tasvir gövdesi
`gövde = esas_kök(ünlü-başlı varyant) + [y] + bağ_ünlü + yardımcı_kök`
- Esas kök **ünlü-başlı ek** alıyormuş gibi işlenir → YUMUŞAMA/ye_de tetiklenir
  (`_stem_before_suffix(vs, True)`): git→**gid**iver/gidedur; ye→**yi**yiver.
- Ünlü-final kök → kaynaştırma **-y-**: oku→**okuyu**ver, oku→**okuya**dur.
- Bağ ünlü: `iver`→**-I** (yüksek 4'lü, yuvarlak duyarlı: yapıver/geliver/görüver/okuyuver);
  diğerleri→**-A** (alçak 2'li: gidedur/bakakal/düşeyaz).

### 2. Çekim — yardımcı fiil çekilir
Oluşan gövde (ver/dur/gel/kal/yaz ile biter) NORMAL fiil gibi çekilir. Yardımcı fiilin
LEKSİK özellikleri geçerlidir:
- **Aorist:** ver/dur/gel/kal → **-Ir** (13 istisnadan): yapıver**ir**, gidedur**ur**,
  bakakal**ır**, çekegel**ir**. yaz → **-Ar** (düzenli): düşeyaz**ar**.
- Yumuşama YOK (ver/dur/gel/kal/yaz ünsüz-final, yumuşamaz).
- Şimdiki: yapıver**iyor** (ver-i-yor), gidedur**uyor** (dur-u-yor).
- Görülen geçmiş: yapıver**di**, bakakal**dı**.

### 3. Olumsuz / yeterlik / soru / birleşik — BEDAVA
Hepsi oluşan tasvir gövdesine işler (ayrı iş YOK):
- olumsuz: yapıver**me**di (yapıver + -mA + -DI), bakakal**ma**dı.
- yeterlik: yapıver**ebil**ir (nadir ama dilbilgisel).
- soru: yapıverdi **mi**. birleşik: yapıver**miş**ti (rivayet+hikaye zinciri gövdeye).

## Golden zorunlu kapsam (bağımsız ajan)
5 aspect × fiil sınıfları: düz ünsüz (yap/bak/gel), yumuşama (git), ye_de (ye), ünlü-final
(oku/ara), yuvarlak (gör/gül). Her (fiil, aspect) için EN AZ: pres.3sg, past.3sg,
aorist.3sg, past.3sg+olumsuz. Kritik: gidiver/gidedur (yumuşama), okuyuver/okuyadur
(kaynaştırma + tezlik yüksek vs sürerlik alçak), yapıverir/düşeyazar (aux aorist -Ir/-Ar),
bakakalır. ~80 hücre, elle-doğrulanmış.

## Not (kapsam)
Tezlik `-Iver` en yaygın/üretken; `-Agel/-Ayaz` edebî/arkaik. Motor hepsini mekanik üretir;
semantik-uygunluk (hangi fiil hangi tasvir alır) lekstiktir, motorun işi değil (biçim üreticidir).
