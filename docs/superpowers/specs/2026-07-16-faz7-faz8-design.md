# Faz 7 + Faz 8 Tasarım Dokümanı

Tarih: 2026-07-16  
Konu: `_root_candidates` sınır fix'leri (Faz 7) + Metin normalleştirme ve IPA transkripsiyon (Faz 8)

---

## Faz 7 — `_root_candidates` 3 Sınır Fix

### Hedef

`analysis_candidates.py`'deki üç bilinen açık kapatılır. Tümü pre-existing (tüm kind'larda
geçerli), ~%0.1 miss oranı oluşturur. Her fix bağımsız, minimal patch; mevcut davranış
korunur.

### Fix 1 — Disharmonik Alıntı (`inhimak`)

**Problem:** `_root_candidates` yüzey önekinden mastar kurarken yalnız ünlü harmoniye göre
`-mak`/`-mek` seçer. Disharmonik alıntı lemmalar (örn. `inhimak`) düzenli-harmoni
varsayımıyla `inhimek` olarak üretilir → round-trip kaçırır.

**Fix:** Her iki mastar varyantı (`-mak` ve `-mek`) aday olarak üretilir. `roots is not None`
modunda yalnız leksikonda bulunan tutulur. `roots is None` (hypothetical) modunda ikisi de
aday kalır (zaten gürültülü mod).

**Etki:** Leksikonsuz modda aday sayısı çok az artar (yalnız ünsüz-uyumsuz tabanlar); precision
düşmez çünkü oracle round-trip filtreler.

### Fix 2 — Monosilab -Iyor Ünlü-Düşme (`somak→suyor`)

**Problem:** `analysis_candidates.py` satır 213–235'te `-Iyor` kurtarma kodu mevcuttur:
`yor_idx = surface.find("yor")` → `pre_yor` yüksek ünlü mü kontrol → `taban = surface[:yor_idx-1]` → 8 ünlü dener.
Ancak satır 230'da `if taban and any(c in _VOWELS for c in taban)` guard'ı vardır.
Monosilab durumda (`suyor` → `taban = "s"`) taban ünlüsüzdür → guard **False** → dal hiç girilmez →
`somak` bulunamaz.

**Fix:** Satır 230'daki guard `any(c in _VOWELS for c in taban)` koşulunu kaldır; yerine
`len(taban) >= 1` koy. Taban ünlüsüz olsa da 8-ünlü deneme + oracle filtreleme doğru kökü bulur.
Çok-heceli kökler zaten bu dala girdiğinde taban ünlü içerir → davranışları değişmez.

**Etki:** Monosilab ünlü-düşme lemmalar (`somak→suyor`, `çomak→çuyor`) artık `-Iyor`
biçimlerinden kurtarılır. Mevcut çok-heceli davranış korunur.

### Fix 3 — "yor"-Alt-Dizi Çakışması (`yorgalamak→yorgalıyor`)

**Problem:** `analysis_candidates.py` satır 223'te `yor_idx = surface_token.find("yor")`
kullanılır; `find` **ilk** oluşumu bulur. `yorgalıyor` için `find("yor") → 0` (sözcük başı).
Satır 224'teki `yor_idx > 1` guard'ı 0 için **False** → `-Iyor` kurtarma dalı hiç girilmez →
`yorgalamak` bulunamaz. Benzer şekilde `yorumlamak→yorumluyor` da etkilenir.

**Fix:** `surface_token.find("yor")` → `surface_token.rfind("yor")` değiştirilir.
`rfind` **son** oluşumu bulur; `-Iyor` eki her zaman yüzey sonundadır → son "yor" her zaman
doğru konumdur. Guard `yor_idx > 1` korunur (1 karakterlik taban anlamsız, zaten bloklansın).

**Etki:** `yorgalamak`, `yorumlamak` gibi gövde-içi "yor" barındıran lemmalar artık `-Iyor`
biçimlerinden doğru kurtarılır. `find`→`rfind` minimal, geri-uyumlu değişiklik.

### Test Stratejisi

Her fix için bağımsız golden (motor-körü, Opus): bilinen miss yüzeyleri + round-trip kontrolü.
Tam paket regresyon (3564+ test) fix sonrası sıfır kırılma beklenir. Korpus taraması:
`lexicon.load()` leksikonu üzerinden sistematik.

---

## Faz 8 — `normalization.py` + `phonology.py`

### Hedef

İki yeni bağımsız modül: metin normalleştirme (sayı/tarih/kısaltma/sembol → sözel) ve IPA
transkripsiyon. Her ikisi de saf-Python, bağımlılıksız, MIT-dağıtılabilir.

---

### `normalization.py`

#### `number_to_words(n: int) -> str`

Tam sayıyı Türkçe sözel gösterimine çevirir.

**İmza:** `n: int` — yalnız tam sayı. Float/ondalık için ayrı fonksiyon (aşağıya bak).

**Kapsam:** -999,999,999,999 … 999,999,999,999 (trilyon altı)

**Basamak grupları:** trilyon / milyar / milyon / bin / yüzler / onlar / birler

**Özel kurallar:**
- `1000 → "bin"` (bir bin değil; Türkçe kuralı)
- `1001 → "bin bir"`, `2000 → "iki bin"`, `100 → "yüz"`, `200 → "iki yüz"`
- `0 → "sıfır"`
- Negatif: `"eksi " + number_to_words(abs(n))`

#### `float_to_words(n: float) -> str`

Ondalık sayıyı sözel çevirir: tam kısım `number_to_words` ile, ondalık kısım rakam-rakam.
`3.14 → "üç virgül bir dört"`. Negatif: tam kısım `number_to_words` kuralını devralır
(`-3.14 → "eksi üç virgül bir dört"`). Gösterim precision'ı `str(n)` belirler; IEEE 754
gürültüsü (`0.1 + 0.2 = 0.30000000000000004`) normalize edilmez — bu kapsam dışıdır
(Faz B tokenizasyon fazında `Decimal` ile ele alınacak).

#### `date_to_words(gün: int, ay: str | int, yıl: int) -> str`

Tarih bileşenlerini Türkçe sözel biçime çevirir.

- `date_to_words(15, "Temmuz", 2026) → "on beş Temmuz iki bin yirmi altı"`
- `date_to_words(1, 3, 2025) → "bir Mart iki bin yirmi beş"`
- Ay adları kapalı tablo (12 giriş, tam ve kısaltma kabul edilir).

#### `time_to_words(saat: int, dakika: int) -> str`

- `time_to_words(14, 30) → "on dört otuz"`
- `time_to_words(9, 5) → "dokuz beş"` (dakika önde sıfır olmadan okunur)
- `time_to_words(9, 0) → "dokuz"` (tam saat)
- `time_to_words(0, 5) → "sıfır beş"` (gece yarısını geçmiş → sıfır + dakika)
- `time_to_words(0, 0) → "sıfır"` (gece yarısı 00:00)

#### `expand_abbreviation(token: str) -> str`

Kapalı tablo (~40 giriş). Tam-token eşleme (büyük/küçük harf normalize edilir).

Örnek girişler: `TL→türk lirası`, `USD→dolar`, `km→kilometre`, `cm→santimetre`,
`kg→kilogram`, `gr→gram`, `m²→metrekare`, `%→yüzde`, `@→et`, `No→numara`,
`Dr→doktor`, `Prof→profesör`, `Öğr→öğrenci`, `vb→ve benzeri`, `vd→ve diğerleri`,
`TDK→Türk Dil Kurumu`, `TBMM→Türkiye Büyük Millet Meclisi`.

Bilinmeyen token → token aynen döner (sessiz fallback).

#### `normalize(text: str) -> str`

Token bazlı pipeline:

1. Metni boşluğa göre token'a böl
2. Her token için: `re.fullmatch(r"-?\d+", token)` → sayı → `number_to_words`; kısaltma tablosunda mı? → `expand_abbreviation`; sembol (`%`, `@`) → genişlet; değilse → aynen bırak
3. Token'ları birleştir

Kelime sırasını korur.

**Kapsam dışı (açık sınırlar):**
- Bitiştik sayı+birim: `"42km"`, `"TL."` gibi boşluksuz yazımlar işlenmez; tokenize çağıranın sorumluluğu.
- Morfoloji-duyarlı normalleştirme: `"42'nci → kırk ikinci"` (kesme işareti ayrımı).
- Bağlamlı kısaltma: `"Dr."` kişi adı önünde mi, ek önünde mi.
Bu sınırlar Faz B (tokenizasyon) fazına ertelenir.

---

### `phonology.py`

#### `to_ipa(text: str) -> str`

Türkçe metin → IPA transkripsiyon dizesi. Karakter düzeyinde, sol→sağ.

**Harf→IPA tablosu (seçili):**

| Türkçe | IPA | Not |
|--------|-----|-----|
| a | /a/ | |
| b | /b/ | |
| c | /dʒ/ | affricate |
| ç | /tʃ/ | affricate |
| d | /d/ | |
| e | /e/ | |
| f | /f/ | |
| g | /ɡ/ | |
| ğ | /ː/ | önceki ünlüyü uzatır (kelime-ortası) |
| h | /h/ | |
| ı | /ɯ/ | yüksek-arka-düz |
| i | /i/ | |
| j | /ʒ/ | |
| k | /k/ veya /c/ | ince/kalın ünlü bağlamına göre |
| l | /l/ veya /ɫ/ | ince/kalın |
| m | /m/ | |
| n | /n/ | |
| o | /o/ | |
| ö | /ø/ | |
| p | /p/ | |
| r | /ɾ/ | tap/flap |
| s | /s/ | |
| ş | /ʃ/ | |
| t | /t/ | |
| u | /u/ | |
| ü | /y/ | yuvarlak-ön |
| v | /v/ | |
| y | /j/ | |
| z | /z/ | |

**ğ işlemi:** kelime-ortası → önceki ünlü uzar (`/ː/` eklenir, `ğ` atlanır);
kelime-sonu/başı → sessiz atlanır. Not: standart Türkçe sözcüklerde `ğ` kelime başında
gelmez; ham/hatalı girdilerde bu konumla karşılaşılırsa sessizce atlanır (belgelendi).

**k/l bağlam seçimi:** Sol-komşu ünlüye bak (işlenen karakterin solundaki ilk ünlü);
yoksa sağ-komşu ünlüye bak. `{a,ı,o,u}` → `k→/k/`, `l→/ɫ/` (art damak);
`{e,i,ö,ü}` → `k→/c/`, `l→/l/` (ön damak). Her ikisi de yoksa art damak varsayılan.

**Kapsam dışı (defer):** ünsüz sedalılık uyumu (kelime sınırı `p→b`, `t→d`, `ç→c`),
hece yapısı analizi, vurgu işaretleme. `ğ` kelime-sonu uzama etkisi (`dağ → /daː/`):
bu fazda kelime-sonu `ğ` sessizce atlanır (`/da/`); tam IPA ayrı Faz'a ertelenir.
IEEE 754 float gürültüsü (`0.1+0.2`): Faz B'ye ertelenir.
Tümü dilbilimsel/teknik karmaşıklık barındırır.

#### `ipa_table() -> dict[str, str]`

Harf→IPA sözlüğünü döner. Test ve belgeleme için.

---

### TR API (`tr.py`) Eklemeleri

```python
tr.sayıya_çevir(42)                      # "kırk iki"
tr.ondalığa_çevir(3.14)                  # "üç virgül bir dört"
tr.tarihe_çevir(15, "Temmuz", 2026)     # "on beş Temmuz iki bin yirmi altı"
tr.saate_çevir(14, 30)                  # "on dört otuz"
tr.kısaltma_aç("TL")                    # "türk lirası"
tr.normalleştir("42 km yol")            # "kırk iki kilometre yol"
tr.ipa("merhaba")                       # "/meɾhaba/"
```

### Test Stratejisi

**`normalization.py`:**
- `number_to_words`: 0, 1, 10, 11, 100, 1000, 1001, 10000, 1000000, negatif, ondalık → golden
- `date_to_words`, `time_to_words`: sınır değerler + ay adları
- `expand_abbreviation`: tüm 40 giriş golden
- `normalize`: pipeline testi (sayı+kısaltma karışık metin)
- TR denklik: `tr.sayıya_çevir == number_to_words`

**`phonology.py`:**
- `to_ipa`: tüm Türkçe harfler tek-tek + kelime düzeyinde örnek (merhaba, Türkiye, öğrenci)
- `ğ` bağlam testi: kelime-ortası uzama, başı/sonu guard
- `k`/`l` bağlam testi: ince/kalın ünlü komşuluğu
- `ipa_table`: dönen sözlük tam ve doğru mu

Her modül SPEC → bağımsız golden (motor-körü, Opus) → motor → hakem döngüsü.

---

## Yol Haritası

| Faz | İçerik | Modüller |
|-----|--------|----------|
| **7** | `_root_candidates` 3 sınır fix | `analysis_candidates.py` |
| **8** | Metin normalleştirme + IPA | `normalization.py`, `phonology.py`, `tr.py` |
| 9 (gelecek) | Zincirli türetme (2 katman) | `analysis.py`, `derivation.py` |
| 10 (gelecek) | İkileme adverbial | `syntax.py` veya yeni modül |
| 11 (gelecek) | Tokenizasyon + NLP pipeline | yeni modül |
