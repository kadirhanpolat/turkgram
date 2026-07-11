# voice-spec.md — Çatı (voice) morfotaktik katmanı

**Kapsam:** Türkiye Türkçesi dört çatı eki (ettirgen, edilgen, dönüşlü, işteş)
ve bunların **yığılması** (istiflenmesi). Kaynak: Korkmaz *Şekil Bilgisi* §488–499
(kural referansı; düzyazı/örnek KOPYALANMAZ — CLAUDE.md #3). Biçimler elle-doğrulanmış
morfofonolojiden türetilir.

Bu katman gövdeyi **çatılı gövdeye** dönüştürür; oluşan gövde NORMAL fiil gibi çekilir
(kip/zaman/kişi/olumsuz/soru hepsi çatılı gövdeye biner). Tasvir (`aspect-spec.md`) ve
ek-fiil (`copula`) ile aynı **delegasyon deseni**: türetilmiş kök → `VerbStem` → çekim.

---

## 1. Çekirdek değişmez

- Motor çatılı biçimi **ÜRETİR, SAKLAMAZ** (CLAUDE.md #5). Kök + çatı zinciri → gövde.
- `apply_voice(vs, chain) -> VerbStem`: `chain` bir çatı-etiketi listesi; sırayla uygular,
  her adımda morfofonolojiyi çözer, **güncellenmiş** `VerbStem` döndürür (root = çatılı gövde).
- Çatılı gövde **her zaman çok-heceli ve ünsüz-final** olur (her ek bir hece + ünsüz katar:
  -r/-l/-n/-ş/-t). Dolayısıyla:
  - Aorist otomatik **-Ir** olur (motorun çok-heceli sezgisi; `aorist_ir=False` yeter).
  - `softens`/`special(ye_de)` bayrakları çatılı gövdede **düşer** (türetilmiş kök,
    orijinal t/ye_de artık yüzeyde yok). Bu bayraklar YALNIZ zincirin **ilk** ekinde,
    orijinal köke uygulanırken devrede olur.

## 2. Çatı etiketleri (çekirdek anahtarları — İngilizce)

| Etiket | Çatı | Türkçe (tr.py) |
|--------|------|----------------|
| `caus` | ettirgen | `ettirgen` |
| `pass` | edilgen  | `edilgen`  |
| `refl` | dönüşlü  | `dönüşlü`  |
| `recip`| işteş    | `işteş`    |

`voice_chain` = bu etiketlerden liste. Boş/`None` → çatısız (mevcut davranış).
Bilinmeyen etiket → geçerli seçenekleri sıralayan `ValueError`.

---

## 3. ETTİRGEN (`caus`) — Korkmaz §498

En çok allomorflu, kısmen **leksik** koşullu ek. Korkmaz'ın saydığı başlıca ekler:
-DIr-/-DUr-, -(I)t-/-(U)t-, -(I)r-/-(U)r-, -Ar-, -DAr-, -(I)z-/-(U)z-. Bu sürüm ilk
dördünü modeller; -DAr- (dön→dönder), -(I)z- (em→emzir) **donmuş/marjinal** kabul edilip
(gerekirse leksik tabloda tekil giriş) kapsam dışı. Ölçüt sırası:

### 3.1 Leksik istisnalar (kapalı küme; YALNIZ orijinal köke, ilk ekte)
Fonolojiyle öngörülemez; tabloda tutulur (`CAUSATIVE_LEXICAL`).

- **-Ir/-Ur** (§498.3; tek-heceli ç/ş/t/… sonrası): aş→aşır, düş→düşür, geç→geçir,
  göç→göçür, iç→içir, kaç→kaçır, piş→pişir, şiş→şişir, yat→yatır, uç→uçur, doy→doyur.
- **-Ar/-Er** (§498; leksik): çık→çıkar, kop→kopar, on→onar.
- **-It/-Ut** (§498.1; seyrek tek-heceli k/p/ç/m sonrası): kork→korkut, ürk→ürküt,
  ak→akıt, kok→kokut, sark→sarkıt, sap→sapıt.
- **Süpletif** (biçimce türetilemez, sözlükselleşmiş): bu sürümde YOK. görmek→göstermek,
  gelmek→getirmek anlamca ayrı sözcük; üretken gör→gördür geçerli, gel çatı golden'ı dışı.

### 3.2 Fonolojik varsayılan (leksik değilse)
- **-(I)t-** (§498.1) — (a) ünlü-final gövde (her hece): oku→okut, uyu→uyut,
  başla→başlat, ara→arat, temizle→temizlet; (b) **çok-heceli** -l/-r ile biten:
  otur→oturt, azal→azalt, kısal→kısalt, çağır→çağırt, ağar→ağart.
  > **TUZAK:** tek-heceli -l/-r → -DIr, -t DEĞİL (al→aldır, gör→gördür, kal→kaldır,
  > gül→güldür). -t'nin -l/-r dalı yalnız çok-heceli. Ölçüt: `hece_sayısı ≥ 2 ve son ∈ {l,r}`.
- **-DIr-** (§498.2, en işlek) — diğer tüm ünsüz-final (4'lü harmoni + sertleşme):
  yap→yaptır, sev→sevdir, koş→koştur, gül→güldür, gör→gördür, yaz→yazdır, sus→sustur,
  aç→açtır, sat→sattır, al→aldır, bin→bindir, kes→kestir, de→dedir, ye→yedir.

### 3.3 Çift/üçlü ettirgen (yığılma içi tekrar)
Türetilmiş gövdeye ettirgen tekrar eklenince ölçüt **fonolojik** çalışır (leksik yok):
- yap→yaptır (§3.2 -DIr) → yaptır **-r final** → -t → **yaptırt** → yaptırt **-t final**
  (ünsüz) → -DIr → **yaptırttır** (Korkmaz'ın *yap-tır-t-tır-* zinciri).

---

## 4. EDİLGEN (`pass`) — Korkmaz §498

Tek ek, üç yüzey biçimi (ölçüt son ses):
- **Ünlü-final kök → -n** (yalnız -n, önünde bağlama ünlüsü YOK): oku→okun, ara→aran,
  başla→başlan, de→den, ye→yen.
- **-l ile biten kök → -In** (4'lü; -ll- kümesini bozar): bil→bilin, al→alın, bul→bulun,
  gül→gülün, ol→olun, del→delin.
- **Diğer ünsüz-final → -Il** (4'lü): yap→yapıl, sev→sevil, gör→görül, yaz→yazıl,
  aç→açıl, kır→kırıl, kes→kesil.

> `-r` ile biten kök -l değildir → -Il alır (gör→görül, kır→kırıl). Yalnız **-l** özeldir.

## 5. DÖNÜŞLÜ (`refl`) — Korkmaz §494

Biçimce edilgen -n/-In ile örtüşür; ölçüt son ses (l-özel dalı YOK, dönüşlüde -In
ünsüz-finalde genel):
- **Ünlü-final → -n**: yıka→yıkan, tara→taran, süsle→süslen, giz(le)→gizlen.
- **Ünsüz-final → -In** (4'lü): giy→giyin, döv→dövün, sev→sevin, süz→süzün, ört→örtün,
  sok→sokun, taşı→taşın (ünlü-final → -n; not: taşı örneği §—ünlü dalına).

> Not: dönüşlü ve edilgen biçim çakışabilir (sevin- vs sevil-). Anlam ayrımı sözdizimseldir;
> motor yalnız istenen çatının biçimini üretir. Kullanıcı hangi çatıyı ister onu geçirir.

## 6. İŞTEŞ (`recip`) — Korkmaz §496

- **Ünsüz-final → -Iş** (4'lü): döv→dövüş, gör→görüş, sev→seviş, gül→gülüş, bak→bakış,
  vur→vuruş, at→atış, tut→tutuş, öp→öpüş, kaç→kaçış.
- **Ünlü-final → -ş**: ağla→ağlaş, uyu→uyuş, koku→? (kokuş- ayrı). Örnek: ağla→ağlaş.

---

## 7. Yığılma (istifleme) sırası — Korkmaz §499

Kanonik dizilim (içten dışa = yüzey soldan sağa):

```
DÖNÜŞLÜ / İŞTEŞ  →  ETTİRGEN  →  EDİLGEN
   refl/recip          caus          pass
```

- Motor `voice_chain`'i **verilen sırayla** uygular (kanonikleştirme yapmaz; golden kanonik
  sıraları test eder). Her adım güncel gövdenin son sesine bakar.
- **Örnek showcase** (döv, işteş+ettirgen+edilgen):
  döv → **dövüş** (recip -Iş) → **dövüştür** (caus; dövüş -ş ünsüz → -DIr, ş sert → -tür)
  → **dövüştürül** (pass; -r final → -Il, harmoni ü) → *dövüştürüldü*.
- **Ettirgen+edilgen**: yap → yaptır → **yaptırıl** (-r final → -Il) → *yaptırıldı*.
  oku → okut → **okutul** (-t final ünsüz → -Il, harmoni u) → *okutuldu*.
- **Çift ettirgen+edilgen**: yap → yaptır → yaptırt → **yaptırtıl** → *yaptırtıldı*.
- **Üçlü ettirgen+edilgen** (Korkmaz zinciri): yap → yaptır → yaptırt → yaptırttır →
  **yaptırttırıl** → *yaptırttırıldı*.

---

## 8. Morfofonoloji — çatılı gövdeye biner (mevcut primitifleri YENİDEN KULLAN)

- İlk ek orijinal köke: ünlü-başlı çatı eki (-Ir/-Il/-In/-Iş/-Ar/-It ve edilgen -n/dönüşlü -n)
  önünde `_stem_before_suffix(vs, vowel_initial=True)` → yumuşama (git→gid) / ye_de (ye→yi)
  tetiklenir. Ünsüz-başlı çatı eki (-DIr/-t) önünde sert kök (yumuşama YOK).
  - Örn. et→ettir (ünsüz -DIr, yumuşama yok; sert t+t); git→gidil? (edilgen -Il ünlü-başlı →
    gid+il = gidil "gidilmek" ✓).
- 4'lü harmoni: `high_vowel`; 2'li: `low_vowel`; sertleşme (-DIr→-tIr, -t sabit): `hardens`.
- Türetilmiş gövde ünsüz-final → sonraki çatı eki ve tüm çekim ona bakar.
- Çatılı gövdenin çekimi: k→ğ, aorist -Ir, -Iyor ünlü düşmesi vs. mevcut `_conjugate_core`
  kurallarıyla **otomatik** (delegasyon; sıfır ek çekim morfolojisi).

## 9. API entegrasyonu

- `conjugate(..., voice_chain: list[str] | None = None)`: `parse_verb` sonrası, `aspect`'ten
  ÖNCE `vs = apply_voice(vs, voice_chain)`. Sonra normal akış (aux/soru/core).
  - `voice_chain` + `aspect` birlikte: önce çatı, sonra tasvir mi? Bu sürümde **çatı gövdesi
    üzerine tasvir** (dövüştürüver…) desteklenmez zorunlu değil; golden yalnız çatı×çekim test
    eder. (Birlikte kullanım Faz sonrası; ayrık tutulur.)
- `apply_voice` `__init__`'te dışa açılır.
- `tr.py`: `ettirgen`/`edilgen`/`dönüşlü`/`işteş` → `caus`/`pass`/`refl`/`recip` haritası;
  `çatı=[...]` param → `voice_chain`.

## 10. Golden kapsamı (bağımsız, elle-doğrulanmış)

- Tekli her çatı: allomorf dallarını kapsayan ~temsili fiiller (default -DIr/-t, leksik -Ir/-Ar/-It;
  edilgen -Il/-In/-n; dönüşlü -n/-In; işteş -Iş/-ş).
- Yığınlar: caus+pass, recip+caus+pass, çift/üçlü caus+pass.
- Her hücre birkaç çekim (pres.3sg, past.3sg, aorist.3sg, past.neg.3sg) → türetilmiş gövdenin
  çekime doğru bindiğini doğrular.
- Anahtar sözleşmesi: `"<chain>.<tense>.<person>"`, chain `+` ile birleşik
  (örn. `"recip+caus+pass.past.3sg"`), neg için `.neg` (örn. `"caus.past.neg.3sg"`).
