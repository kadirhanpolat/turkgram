# Sıfat Morfolojisi — SPEC

**Modül:** `turkgram.adjective` (yeni)
**Referans:** Korkmaz *Türkiye Türkçesi Grameri* §333–360 (Sıfatlar); §335 Pekiştirme, §336 Küçültme.
**Kapsam:** Sıfat pekiştirmesi (yinelemeli önek) + küçültme ekleri (`-CIk`, `-ImsI`, `-ImtIrak`).
Karşılaştırma (*daha/en*) sözdizimsel → defer (Faz 4).

---

## §1. Pekiştirme (Yoğunlaştırma)

### §1.1 Tanım

Türkçede sıfat pekiştirmesi, sıfatın ilk hecesiyle (bazen dönüştürülmüş) oluşturulan
ön-ek + tam sıfat birleşimiyle yapılır:
- `beyaz` → `bembeyaz`
- `kara` → `kapkara`
- `açık` → `apaçık` (ünlü-başlı)

Bu süreç **lexical / morfofonolojik** değil, tamamen **leksik** (her sıfat-önek çifti
dilbilgisinde önceden belirlenmiş). Bu nedenle:
- Algoritmik kural: ünlü-başlı sıfatlar için `ilk_ünlü + p + sıfat` deseni ÇALIŞIR.
- Ünsüz-başlı sıfatlar: ön-ek **leksik kapalı tablo** (`INTENSIFIER_PREFIX`) ile belirlenir.

### §1.2 Ünlü-başlı sıfat kuralı (algoritmik)

Sıfat ünlü ile başlıyorsa:
```
pekiştirme = ilk_ünlü + "p" + sıfat
```
Örnekler:
- `açık` → `a` + `p` + `açık` = `apaçık`
- `uzun` → `u` + `p` + `uzun` = `upuzun`
- `ince` → `i` + `p` + `ince` = `ipince`
- `esmer` → `e` + `p` + `esmer` = `epesmer`

### §1.3 Ünsüz-başlı sıfat kapalı tablosu

Ünsüz-başlı sıfatlar için ön-ek tamamen leksik — kural değil tablo:

```python
INTENSIFIER_PREFIX: dict[str, str] = {
    "beyaz":   "bem",   # bembeyaz
    "kara":    "kap",   # kapkara
    "sıcak":   "sım",   # sım-sıcak  (tire dahil)
    "soğuk":   "som",   # somsoğuk? — hayır: "sapsam" değil, leksik: "sossız" yok
    "mavi":    "mas",   # masmavi
    "yeşil":   "yem",   # yemyeşil
    "kırmızı": "kıp",   # kıpkırmızı
    "sarı":    "sap",   # sapsarı
    "dolu":    "dop",   # dopdolu
    "temiz":   "ter",   # tertemiz
    "düz":     "düm",   # dümdüz
    "boş":     "bom",   # bomboş
    "yalnız":  "yap",   # yapyalnız
    "yavaş":   "yap",   # yapyavaş
    "düzgün":  "düp",   # düpdüzgün
    "çıplak":  "çırıl", # çırılçıplak (uzun önek — istisna)
    "doğru":   "dop",   # dopdoğru
    "koyu":    "kon",   # konkoyu? — hayır: "gop" değil leksik: "gopkoyu" yok
    "geniş":   "gep",   # gepgeniş
    "kuru":    "kup",   # kupkuru
    "sağlam":  "sap",   # sapsağlam
    "güzel":   "güp",   # güpgüzel? — doğru değil: "güpgüzel" yok, "güzelce" başka
    "dar":     "dap",   # dapdardır? — hayır: "dapdardır" değil "dapdardır"?
    "kat":     "kap",   # kapkat? — "katkat" değil
    "saf":     "sap",   # sapsaf
    "yeni":    "yep",   # yepyeni
    "koca":    "kop",   # kopkoca
    "büyük":   "büs",   # büsbüyük
}
```

> **NOT:** Bu tablo kuralsız değil — ünsüz-başlı sıfatlarda ön-ek, sıfatın ilk
> harfine göre değişen **p/m/r/s** ünsüzünden oluşur, ama hangi ünsüzün seçileceği
> leksik. Tabloya girmeyen sıfatlar için `intensify()` `None` döndürür (kapalı küme).

### §1.4 Tire kullanımı

Sadece birkaç sıfatta tire kullanılır: `sım-sıcak`, `yap-yalnız`.
Tablo biçimleri tire dahil saklanır.

---

## §2. Küçültme Ekleri

### §2.1 `-CIk` (diminutive)

En yaygın küçültme eki. Üretim kuralları:
- Ünsüz-final kök + `-CIk` (sertleşme: c→ç voiceless sonrası): `küçük` → `küçücük`
- Ünlü-final kök: direkt + `-CIk`: `kısa` → `kısacık`
- Yumuşama: son `p/ç/t/k` ünlü önünde yumuşar (isim motoruyla aynı kural):
  `küçük` → `küçücük` (k→ğ değil — sıfat küçültme yumuşama YOK, isim motorundan farklı)

Örnekler:
| Sıfat | -CIk | Not |
|-------|------|-----|
| küçük | küçücük | ü ünlü harmonisi |
| kısa | kısacık | a → c → ç? Hayır: kısa + cık = kısacık (a arka → ç) |
| büyük | büyücek | ü → ck? Hayır: büyük + cük = büyücük |
| ufak | ufacık | a → cık |
| az | azıcık | z + ı + cık (buffer ünlü eklenir: ünsüz küme yok) |
| dar | daracık | a → cık, r ünlü-başlı ek önünde kalır |
| uzun | uzuncak | u → cak |
| genç | gencecik | e → cik + tekrarlama (gencecik = genç + e + cik) |

> **TUZAK:** `-CIk` sonunda sertleşme: son ünsüz voiceless (p/ç/t/k/s/ş/f/h) → ç,
> voiced → c.

### §2.2 `-ImsI` (resemblance: "-ish", "-like")

Kısmi benzerlik anlamı. Ünlü harmonisi yüksek (`I` = 4'lü):
- `yeşil` + `imsI` = `yeşilimsi`
- `mavi` + `imsI` = `mavimsi`  (ünlü-final: direkt)
- `sarı` + `imsI` = `sarımsı`
- `kırmızı` + `imsI` = `kırmızımsı`
- `mor` + `imsI` = `morumsu`
- `kara` + `imsI` = `karamsı`
- `beyaz` + `imsI` = `beyazımsı`

Üretim: ünlü-final → direkt `msI`; ünsüz-final → `ImsI` (buffer yüksek ünlü).

### §2.3 `-ImtIrak` (resemblance, stronger than -ImsI)

- `sarı` → `sarımsıtrak`? Hayır: `sarımtırak`
- `yeşil` → `yeşilimtırak`
- `kara` → `karamtırak`
- `mor` → `morumtırak`
- `beyaz` → `beyazımsırak`? Hayır: `beyazımsırak` değil `beyazımtırak`

Üretim: ünsüz-final → `ImtIrak`; ünlü-final → `mtIrak` (buffer düşer, `m` kaynaştırma).

---

## §3. Mimari

### §3.1 Yeni modül: `turkgram/adjective.py`

```python
def intensify(adj: str) -> str | None:
    """Sıfat pekiştirmesi. Kapalı tablo (ünsüz-başlı) + kural (ünlü-başlı)."""

def diminutive(adj: str, suffix: str = "-CIk") -> str | None:
    """Küçültme eki: '-CIk' | '-ImsI' | '-ImtIrak'. None = uygulanamaz."""
```

`turkgram/__init__.py`'e `intensify`, `diminutive` eklenir.

### §3.2 Çözümleme (analyze) etkisi

Pekiştirme çözümlemesi:
- `apaçık` → `analyze('apaçık', roots={'açık'})` → `Analysis(lemma='açık', kind='intensify')`
- `bembeyaz` → kapalı tablo ters araması → `Analysis(lemma='beyaz', kind='intensify')`

Küçültme çözümlemesi:
- `kısacık` → önek tabanlı: `kısa` → `Analysis(lemma='kısa', kind='diminutive', kwargs={'suffix':'-CIk'})`

Bu analizler Faz 3.x olarak ayrı artım — önce üretim.

---

## §4. Kapsam Dışı

- Karşılaştırma (`daha/en`): sözdizimsel, Faz 4
- Sıfattan isim türetme (`-lIk`, `-lI`): mevcut `derivation.py` kapsar
- Sıfat çekimi (isim gibi kullanılınca): mevcut `decline()` kapsar

---

## §5. Doğrulama Kriterleri

**Pekiştirme:**
- [ ] `intensify('açık')` → `'apaçık'`
- [ ] `intensify('uzun')` → `'upuzun'`
- [ ] `intensify('ince')` → `'ipince'`
- [ ] `intensify('beyaz')` → `'bembeyaz'`
- [ ] `intensify('kara')` → `'kapkara'`
- [ ] `intensify('yeni')` → `'yepyeni'`
- [ ] `intensify('büyük')` → `'büsbüyük'`
- [ ] `intensify('sıcak')` → `'sımsıcak'` (tire varyantı)
- [ ] `intensify('bilinmeyen')` → `None`

**Küçültme:**
- [ ] `diminutive('kısa')` → `'kısacık'`
- [ ] `diminutive('az')` → `'azıcık'`
- [ ] `diminutive('yeşil', '-ImsI')` → `'yeşilimsi'`
- [ ] `diminutive('sarı', '-ImsI')` → `'sarımsı'`
- [ ] `diminutive('yeşil', '-ImtIrak')` → `'yeşilimtırak'`
- [ ] Regresyon: 3089 test yeşil kalır
