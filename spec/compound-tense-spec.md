# Bileşik (birleşik) zaman çekimi — SPEC (Faz 2b / motor-dışı biçim 3)

Ana oturum tarafından elle yazılmış **dilbilgisel değişmez** (Korkmaz §… birleşik çekimler:
hikâye / rivayet / şart). Golden bu SPEC'ten **motordan bağımsız** kurulur.

## Kapsam

**Bileşik zaman** = basit zaman finit tabanı + ek-fiil (i-di / i-miş / i-se):
- **hikâye** — `-(y)DI` (görülen geçmiş ek-fiili): geliyor**du**, gelir**di**, gelecek**ti**.
- **rivayet** — `-(y)mIş` (duyulan ek-fiili): geliyor**muş**, gelir**miş**.
- **şart** — `-(y)sA` (şart ek-fiili): geliyor**sa**, gelir**se**, gelecek**se**.

**Basit taban** (üstüne ek-fiil binen) ∈ {`pres` (şimdiki -Iyor), `aorist` (geniş -Ir/-Ar),
`fut` (gelecek -AcAk), `evid` (öğrenilen -mIş)}. **Ek-fiil** ∈ {hikaye, rivayet, sart}.
4 taban × 3 ek-fiil = 12 bileşik zaman. Basit-geçmiş (-DI) tabanı KAPSAM DIŞI (geldiydi,
ağızsal).

## API

```python
def compound(lemma: str, base: str, copula: str, person: str = "3sg", *,
             negative: bool = False) -> str
```
`base ∈ {pres, aorist, fut, evid}`, `copula ∈ {hikaye, rivayet, sart}`,
`person ∈ {1sg,2sg,3sg,1pl,2pl,3pl}`.

## Yapı (DEĞİŞMEZ) — üç adım

1. **Basit taban** = `conjugate(lemma, base, TABAN_KİŞİ, negative=negative)` (motordan aynen).
2. **Ek-fiil + kişi**, tabanın son sesine göre gerçeklenir (mevcut `_copula_suffix` deseni):
   - hikâye: `+ (y) + D + I + kişi_k` (D=t sert-final sonrası; I=4'lü **tabanın son ünlüsünden**).
   - rivayet: `+ (y) + "m" + I + "ş" + kişi_z`.
   - şart: `+ (y) + "s" + A + kişi_k`.
   - Finit taban ünsüz-final → glide (y) düşer.
3. **3pl YERLEŞİMİ (kritik değişmez):** çoğul eki `-lAr` **tabana** biner, ek-fiil **3sg**
   olur → `geliyorlardı` (geliyordular DEĞİL). Yani:
   - `person == "3pl"`: TABAN_KİŞİ = **"3pl"** (geliyorlar), ek-fiil **3sg** eklenir.
   - diğer kişiler: TABAN_KİŞİ = **"3sg"** (geliyor), ek-fiil o kişiyle eklenir.

Kişi ekleri (ek-fiil üstünde):
- **k-tipi** (hikaye/şart): 1sg -m, 2sg -n, 3sg -Ø, 1pl -k, 2pl -nIz. (3pl → adım 3.)
- **z-tipi** (rivayet): 1sg -Im, 2sg -sIn, 3sg -Ø, 1pl -Iz, 2pl -sInIz.

## Elle-doğrulanmış paradigmalar (golden bağımsız kursun)

### şimdiki hikâye (base=pres, copula=hikaye) — gelmek
| kişi | biçim |
|------|-------|
| 1sg | geliyordum |
| 2sg | geliyordun |
| 3sg | geliyordu |
| 1pl | geliyorduk |
| 2pl | geliyordunuz |
| 3pl | **geliyorlardı** |

Not: I=u çünkü tabanın son ünlüsü "o" (geliyor) → yüksek yuvarlak-arka.

### geniş rivayet (base=aorist, copula=rivayet) — gelmek
| kişi | biçim |
|------|-------|
| 1sg | gelirmişim |
| 2sg | gelirmişsin |
| 3sg | gelirmiş |
| 1pl | gelirmişiz |
| 2pl | gelirmişsiniz |
| 3pl | **gelirlermiş** |

### gelecek hikâye (base=fut, copula=hikaye) — gelmek
| kişi | biçim |
|------|-------|
| 1sg | gelecektim |
| 3sg | gelecekti |
| 3pl | **geleceklerdi** |

Not: gelecek sert-final (k) → D=t (gelecek**t**i).

### miş'li geçmişin hikâyesi (base=evid, copula=hikaye) — gelmek
| kişi | biçim |
|------|-------|
| 1sg | gelmiştim |
| 3sg | gelmişti |
| 3pl | **gelmişlerdi** |

Not: gelmiş sert-final (ş) → D=t (gelmiş**t**i).

### geniş şart (base=aorist, copula=sart) — gelmek
| kişi | biçim |
|------|-------|
| 1sg | gelirsem |
| 2sg | gelirsen |
| 3sg | gelirse |
| 3pl | **gelirlerse** |

### örnek: farklı fiil — yapmak, şimdiki hikâye
| kişi | biçim |
|------|-------|
| 3sg | yapıyordu |
| 3pl | yapıyorlardı |

### olumsuz (negative=True)
| lemma | base | copula | kişi | biçim |
|-------|------|--------|------|-------|
| gelmek | pres | hikaye | 3sg | gelmiyordu |
| gelmek | aorist | hikaye | 3sg | gelmezdi |
| gelmek | fut | hikaye | 3sg | gelmeyecekti |
| gelmek | evid | hikaye | 3sg | gelmemişti |

## Kritik değişmezler (golden yakalasın)
- **3pl = tabanda -lAr, ek-fiil 3sg:** geliyorlardı / gelirlermiş / geleceklerdi / gelmişlerdi /
  gelirlerse. ASLA geliyordular / gelirmişler-formu değil (rivayette gelirlermiş, gelirmişler DEĞİL).
- **Ek-fiil ünlüsü tabanın son ünlüsünden:** geliyor→"o"→u (geliyordu); gelir→"i"→i (gelirdi);
  yapıyor→"o"→u (yapıyordu).
- **-DI sertleşmesi tabanın son sesinden:** gelecek(k)→ti, gelmiş(ş)→ti, geliyor(r)→du, gelir(r)→di.
- **Olumsuz taban motordan:** gelmiyordu/gelmezdi/gelmeyecekti/gelmemişti — taban conjugate'ten aynen.
- **glide YOK:** tüm finit tabanlar ünsüz-final → (y) düşer.

## Golden zorunlu kapsam
En az 5 tam paradigma (6 kişi) farklı taban×ek-fiil'den + 2. fiil (yapmak) + 4 olumsuz.
Her paradigmada 3pl satırı ZORUNLU (en kritik hücre). Elle-doğrulanmış, motora bakmadan.

---

# ÇÖZÜMLEME (analysis) — Faz 2b, motor-dışı biçim 3 (regresyon kilidi)

**Bileşik zaman çözümlemesi YENİ MOTOR GEREKTİRMEZ.** `compound(lemma, base, copula, person,
negative)` üreteci, motorun `conjugate(lemma, base, person, aux=copula, negative=negative)`
çıktısıyla **BİREBİR AYNIDIR** (gömülü leksikon 3250 fiil × 4 taban × 3 ek-fiil × 6 kişi ×
2 olumsuz = 216.000 çağrı, 0 fark — `_copula_suffix` şart-2pl fix'i sonrası). `conjugate`'in
`aux` ekseni zaten çözümleyicinin `_enumerate_conjugate` grid'inde (`_CONJ_AUX`) + segmentasyonda
(`_seg_tense_aux`) var.

Dolayısıyla bileşik zaman yüzeyleri **`kind="conjugate"` + `aux` kwargs** olarak çözülür:
- `geliyordu → (gelmek, conjugate, {tense:pres, person:3sg, aux:hikaye})`
- `gelirmiş → (gelmek, conjugate, {tense:aorist, person:3sg, aux:rivayet})`
- `geliyorlardı → (gelmek, conjugate, {tense:pres, person:3pl, aux:hikaye})` (3pl taban+lAr, ek-fiil 3sg)
- `gelseydim → (gelmek, conjugate, {tense:cond, person:1sg, aux:hikaye})`

Bu SPEC bölümü **regresyon kilidi**: golden + korpus round-trip, ileride `aux` çözümleme yolu
kırılırsa yakalar. `compound` kind'ı çözümlemede KULLANILMAZ (üreteç yüzü; analiz `conjugate`
üstünden gelir — tek kanonik okuma, çift kayıt yok).

## Round-trip değişmezi (hakem)
`compound(lemma, base, copula, person, negative)` her yüzey `analyze(…, roots={lemma})` ile
`(lemma, "conjugate", {tense:base, person, aux:copula[, negative]})` verir. Leksikon × tam
grid → 0 miss (pre-existing disharmonic/monosyllabic kök-aday sınırları hariç).
