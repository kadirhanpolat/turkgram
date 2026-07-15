# Sayı Morfolojisi SPEC — Faz 5 D1

Referans: Korkmaz *Türkiye Türkçesi Grameri — Şekil Bilgisi* §97–100 (sayı sıfatları),
§113 (yapım ekleri). Kural olgu; düzyazı/örnek cümleler telif dışı kopyalanmadı.

---

## §1 Kapsam

Bu SPEC yalnız **ordinal** (sıra sayı: birinci/ikinci) ve **distributif** (üleştirme sayı:
birer/ikişer) eklerini kapsar.

**Kapsam dışı (bu SPEC'te işlenmez):**
- Kesir sayıları (onda bir, yüzde beş)
- Yaklaşık sayılar (beş-altı, onlarca)
- Topluluk sayıları (beşer, onar — kümeli kullanım; aynı biçim, sözdizimsel fark)
- Sayı adları üretimi (integer → Türkçe sözcük: 1→"bir"); bu modülün girdisi
  zaten Türkçe sayı sözcüğüdür

**Çekim entegrasyonu:** Üretilen ordinal/distributif biçimler tam Türkçe isim/sıfat
gibi davranır → mevcut `decline(form, case=...)` motoru ile doğrudan çekilebilir.
Bu modülde yeni çekim morfolojisi YOKTUR (delegasyon, A3 emsali).

---

## §2 Ordinal — -(I)ncI

### Kural

Ordinal eki **-(I)ncI**:

- **I** = 4'lü yüksek ünlü uyumu (ı / i / u / ü) — son ünlüye göre
- **n** = sabit n
- **c** = daima **c** (asla ç); n'den önce gelen konum sedalılaşmayı zorunlu kılar
- **I** = aynı yüksek ünlü (son I ile aynı harf)

**Allomorf:**

| Gövde-final | Ek biçimi | Örnek |
|-------------|-----------|-------|
| Ünsüz-final | `+IncI` (I gövdeye yapışır) | bir → bir**i**nc**i** |
| Ünlü-final  | `+ncI` (baştaki I düşer) | altı → altı**nc**ı |

### Ordinal tablosu (1–1000 temsili)

| Kök | Son ünlü | Harmoni (yüksek) | Biçim |
|-----|----------|-------------------|-------|
| sıfır | ı | ı | sıfırıncı |
| bir | i | i | birinci |
| iki | i | i | ikinci |
| üç | ü | ü | üçüncü |
| dört | ö | ü | dördüncü |
| beş | e | i | beşinci |
| altı | ı | ı | altıncı |
| yedi | i | i | yedinci |
| sekiz | i | i | sekizinci |
| dokuz | u | u | dokuzuncu |
| on | o | u | onuncu |
| on bir | i | i | on birinci |
| on iki | i | i | on ikinci |
| yirmi | i | i | yirminci |
| yirmi bir | i | i | yirmi birinci |
| otuz | u | u | otuzuncu |
| kırk | ı | ı | kırkıncı |
| elli | i | i | ellinci |
| altmış | ı | ı | altmışıncı |
| yetmiş | i | i | yetmişinci |
| seksen | e | i | sekseninci |
| doksan | a | ı | doksanıncı |
| yüz | ü | ü | yüzüncü |
| iki yüz | ü | ü | iki yüzüncü |
| bin | i | i | bininci |
| iki bin | i | i | iki bininci |
| milyon | o | u | milyonuncu |

### Sedalılaşma notu

Ordinal eki ünlü ile başlar (I) → ünsüz-final gövdenin son ünsüzü ünlü-başlı ek
önünde sedalılaşabilir. Türkçe sayı sözcüklerinde bu durum pratikte görülmez
(dört → dördüncü: t→d sedalılaşması; ama bu harfin normal çekim sedalılaşmasıyla
aynı mekanizma). Motor standart `_stem_before_suffix` / `hardens` çağırmaksızın
**doğrudan** eki yapıştırabilir — sayı sözcükleri kapalı küme olduğundan istisnalar
kodlanmış tabloya alınabilir; ancak genel harmoni yeterli çalışır.

**Neden C daima c?** `-n` + `-c` = nc dizisi; Türkçe fonotaktik kuralı gereği `n`
sonrası `ç` sertleşmesi olmaz → c sabit.

### Bileşik sayılarda ordinal

Son bileşen kuralı: yalnız **son sözcük** eki alır, öncekiler değişmez.

```
yirmi bir  → yirmi birinci
kırk beş   → kırk beşinci
iki yüz    → iki yüzüncü
bin dokuz yüz doksan dokuz → bin dokuz yüz doksan dokuzuncu
```

**Uygulama notu:** `ordinal(kök: str)` girdisi tek sözcük (son bileşen) alır;
bileşik için çağıran son token'ı ayırarak iletir (`ordinal("bir")` → "birinci",
çağıran `"yirmi " + ordinal("bir")` birleştirir).

---

## §3 Distributif — -(ş)Ar

### Kural

Distributif eki **(ş)Ar**:

- **ş** = yalnız **ünlü-final gövde** sonrasında; ünsüz-final → ş yoktur
- **A** = 2'li alçak ünlü uyumu (a / e) — son ünlüye göre
- **r** = sabit r

**Allomorf:**

| Gövde-final | Ek biçimi | Örnek |
|-------------|-----------|-------|
| Ünlü-final  | `+şAr` | iki → iki**şer** |
| Ünsüz-final | `+Ar`  | bir → bir**er** |

### Gövde sonu sedalılaşması (ünsüz-final)

Ek ünlü ile başladığı için gövde son ünsüzü sedalılaşabilir. Türkçe sayı sözcüklerinde
yalnız **dört** bu sedalılaşmayı gösterir:

| Kök | Son harf | Sedalılaşma | Distributif |
|-----|----------|-------------|-------------|
| dört | t | t → d | dörder |
| beş | ş | yok (ş haritada değil) | beşer |
| sekiz | z | yok | sekizer |
| yüz | z | yok | yüzer |

Sedalılaşma kapalı tablo `_VOICE_MAP = {t:d, ç:c, k:ğ, p:b}` ile uygulanır.
`ş`, `z`, `r`, `n`, `l`, `m` → değişmez.

### Distributif tablosu (1–1000 temsili)

| Kök | Son ünlü | Final | Harmoni (alçak) | Biçim |
|-----|----------|-------|-----------------|-------|
| bir | i | ünsüz r | e | birer |
| iki | i | ünlü i | e | ikişer |
| üç | ü | ünsüz ç (ç→c değil, harmoni e) | e | üçer |
| dört | ö | ünsüz t → d | e | dörder |
| beş | e | ünsüz ş | e | beşer |
| altı | ı | ünlü ı | a | altışar |
| yedi | i | ünlü i | e | yedişer |
| sekiz | i | ünsüz z | e | sekizer |
| dokuz | u | ünsüz z | a | dokuzar |
| on | o | ünsüz n | a | onar |
| yirmi | i | ünlü i | e | yirmişer |
| otuz | u | ünsüz z | a | otuzar |
| kırk | ı | ünsüz k | a | kırkar |
| elli | i | ünlü i | e | ellişer |
| altmış | ı | ünsüz ş | a | altmışar |
| yetmiş | i | ünsüz ş | e | yetmişer |
| seksen | e | ünsüz n | e | seksener |
| doksan | a | ünsüz n | a | doksanar |
| yüz | ü | ünsüz z | e | yüzer |
| bin | i | ünsüz n | e | biner |
| milyon | o | ünsüz n | a | milyonar |

### Bileşik sayılarda distributif

Ordinal ile aynı kural: son bileşen eki alır.

```
yirmi bir  → yirmi birer
kırk iki   → kırk ikişer
```

---

## §4 Çekim Entegrasyonu

Ordinal ve distributif biçimler `decline()` motoruna girer — tüm hal ekleri standart
isim morfolojisiyle çalışır (yeni morfoloji GEREKMEZ).

Örnekler:

| Biçim | Durum | Çekilmiş |
|-------|-------|----------|
| birinci | gen | birincinin |
| birinci | dat | birinciye |
| birinci | acc | birinciyi |
| birinci | abl | birinciden |
| birinci | loc | birincide |
| birinci | ins | birinciyle |
| üçüncü | gen | üçüncünün |
| onuncu | acc | onuncuyu |
| birer | gen | birerin |
| ikişer | dat | ikişere |

---

## §5 Kapsam Dışı Detaylar

- **Kesir:** "onda bir", "yüzde beş" → sözdizimsel, bu modülde değil
- **Sıfır:** sıfır → sıfırıncı (ordinal); sıfırar (distributif, teorik; pratikte kullanılmaz)
- **Bileşik birden fazla boşluk:** `ordinal("bir")` tek token alır; bileşik yönetimi çağıranda
- **İyelik çekimi:** `decline(ordinal("bir"), possessive="1sg")` → "birincim" — delegasyonla çalışır
