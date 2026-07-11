# Nominal Ek-Fiil (Kopula) — SPEC (Faz 1 / A4)

Ana oturum tarafından elle yazılmış **dilbilgisel değişmez**. Korkmaz *Şekil Bilgisi*
§579–583 (ek-fiil) + birleşik kip mantığı. Golden bu SPEC'ten **motordan bağımsız** kurulur.
Örnek biçimler dilbilgisinden türetilir (Korkmaz düzyazısı KOPYALANMAZ, #11).

## Kapsam

Ek-fiil (i-), **ad soylu bir yüklemi** (isim/sıfat/durum-ekli gövde) çekimler. Modern
Türkçede büyük ölçüde ekleşmiştir. Dört zaman:

| aux | işaretleyici | kişi tipi | ad |
|-----|-------------|-----------|-----|
| `None`/`pres` | `-DIr` / kişi ekleri | z-tipi | geniş/bildirme |
| `hikaye` | `-(y)DI` | k-tipi | görülen geçmiş |
| `rivayet` | `-(y)mIş` | z-tipi | öğrenilen geçmiş |
| `sart` | `-(y)sA` | k-tipi | dilek-şart |

## API

```python
def copula(headword: str, aux: str | None = None, person: str = "3sg", *,
           case: str | None = None, possessive: str | None = None,
           number: str = "sg", question: bool = False) -> str
```

- Gövde `decline(headword, number=, possessive=, case=)` ile kurulur; ek-fiil bu gövdeye biner.
  (Yalın yüklem: case/possessive verilmez → `decline` yalın biçim.)
- `person ∈ {1sg,2sg,3sg,1pl,2pl,3pl}`.

## Kurallar (DEĞİŞMEZ)

### 1. Gövde son sesine göre kaynaştırma / sertleşme
Ek-fiil, kurulan **gövdenin son sesine** bakar (headword'e değil — durum-ekli gövde de olabilir):
- **Ünlü-final gövde** → kaynaştırma `-y-`: öğrenci-**y**-di, hasta-**y**-mış, kapı-**y**-sa,
  evde-**y**-di (durum-ekli), okulda-**y**-mış.
- **Ünsüz-final gövde** → `-y-` YOK: ev-di (**evdi**), güzel-di (**güzeldi**), öğretmen-di.
- `-DI` (hikâye) **d/t sertleşmesi**: gövde sert ünsüzle biterse (`f s t k ç ş h p`) → `-tI`:
  genç-**t**i (**gençti**), aş-**t**ı (**aştı**), dost-**t**u (**dosttu**), ihtiyaç-**t**ı.
- `-mIş` ve `-sA` sertleşME (m, s zaten sert-uyumsuz): genç-**miş** (gençmiş), genç-**se** (gençse).

### 2. Kişi ekleri
- **k-tipi** (hikâye/şart — fiil Grup 1): 1sg `-m` · 2sg `-n` · 3sg `-∅` · 1pl `-k` · 2pl `-nIz` · 3pl `-lAr`.
  - öğrenci-y-di-m (öğrenciydim), -n, -∅, -k, -niz, -ler.
- **z-tipi** (rivayet + geniş — fiil Grup 2): 1sg `-Im` · 2sg `-sIn` · 3sg `-∅` · 1pl `-Iz` · 2pl `-sInIz` · 3pl `-lAr`.
  - öğrenci-y-miş-im, -sin, -∅, -iz, -siniz, -ler.

### 3. Geniş/bildirme (aux=None)
- 3sg: `-DIr` (öğrenci**dir**, ev**dir**, kitap**tır**) — YA DA sıfır kopula (öğrenci). Motor
  `-DIr`'ı üretir (var olan `predicative` davranışı; sıfır biçim ayrı bayrak gerektirmez).
- Kişili: öğrenci-y-im (**öğrenciyim**), öğrenci-sin, öğrenci(-dir), öğrenci-y-iz,
  öğrenci-siniz, öğrenci-ler; ünsüz-final: öğretmen-im (**öğretmenim**), öğretmen-sin…
  (Bu paradigma mevcut `predicative`'te var → geniş copula = predicative.)

### 3pl kuralı
`-lAr` ek-fiile 3sg gövde üstünden eklenir (öğrenci-y-di-**ler** = öğrenciydiler,
öğrenci-y-miş-**ler** = öğrenciymişler). "öğrencilerdi" (çoğul-isim + di) FARKLI bir yapıdır
(number='pl' ile üretilir), copula 3pl DEĞİL. (`_ekfiil` bunu doğru yapar.)

### 4. Soru (question=True) — `mI` gövde ile ek-fiil ARASINA
Ek-fiil tarihsel olarak ayrı sözcük (i-di) → `mI` ONDAN ÖNCE gelir, ek-fiil+kişi `mI`'ye biner:
`gövde + " " + mI + ek-fiil + kişi`.
- geniş: öğrenci mi-y-im (**öğrenci miyim**), öğrenci mi-sin, öğrenci mi (3sg), öğrenci mi-y-iz.
- hikâye: öğrenci mi-y-di-m (**öğrenci miydim**), öğrenci mi-y-di (öğrenci miydi).
- rivayet: öğrenci mi-y-miş-im (**öğrenci miymişim**).
- şart: (nadir) öğrenci mi-y-se — pratikte az; motor üretebilir.
`mI` 4'lü harmoni gövdenin son ünlüsüne (`_q_particle` emsali). imp/ulaç YOK (nominal).

## Golden zorunlu kapsam (bağımsız ajan)
En az 10 ad: ünlü-final (öğrenci, hasta, kapı, masa), ünsüz-final (ev, güzel, öğretmen),
sert-final (genç, aş, dost, kitap). Her biri × {pres(-DIr + 1sg/2sg), hikaye, rivayet, sart}
× {1sg, 2sg, 3sg, 3pl} + durum-ekli gövde (evde-ydi, okulda-ymış) + soru (öğrenci miydim,
gençti mi? → gövde sert: "genç miydi") örnekleri. ~150 hücre, elle-doğrulanmış.

## Tuzaklar (golden yakalasın)
- Ünsüz-final `-y-` YOK: **evdi** (evydi DEĞİL), **güzeldi**.
- Sert-final sertleşme: **gençti** (gençdi DEĞİL), **aştı**, **dosttu**.
- Durum-ekli gövde son sesi belirler: **evdeydi** (evde ünlü-final → -y-).
- 3pl copula: **öğrenciydiler** (öğrenci-y-di-ler), çoğul-isim **öğrencilerdi** ile karışmaz.
- `-mIş`/`-sA` sertleşMEZ: **gençmiş / gençse** (gençtmiş DEĞİL).
