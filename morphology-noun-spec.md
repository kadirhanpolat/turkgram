# TR İsim Çekim Motoru — faz 2 SPEC (roadmap 2a, CLAUDE.md #5)

Bu belge, isim çekim motorunun **dilbilgisel değişmezlerini** ve **API sözleşmesini**
kilitler. Motoru yazan ajan da golden tabloyu kuran ajan da BUNA uyar; ikisi bağımsız
çalışır, anlaşmazlıkları hakem (ana oturum) çözer.

Kapsam kararı (2026-07-11, kullanıcı):
1. **Yumuşama/ünlü-düşmesi verisi:** KURAL + istisna tablosu (ŞİMDİ; GTS taki turu YOK).
   Fiil motorundaki `IRREGULAR` emsali — üretken varsayılan + elle-küratörlü istisna kümesi.
2. **Paradigma genişliği:** GENİŞ = çekirdek üretken sistem (durum + çoğul + iyelik +
   birleşimleri) **+ ek katmanlar** (yüklemleme -DIr, ile-hâli -lA, aitlik -ki, eşitlik -CA)
   + zamir/özel-ad istisnaları.

Fiil motoru (`morphology.py`, `morphology-spec.md`) DEĞİŞMEZ. İsim motoru harmoni
yardımcılarını ondan **import eder** (DRY; fiil motoru ve 728 testi bozulmaz).

---

## 1. Girdi / çıktı sözleşmesi (API — DEĞİŞMEZ)

Dosya: `morphology_noun.py` (repo kökü). Saf Python, dış bağımlılık YOK.
`from morphology import last_vowel, low_vowel, high_vowel, ends_in_vowel, hardens, VOWELS, ...`

```python
def parse_noun(headword: str) -> NounStem

def decline(headword: str, *,
            number: str = "sg",           # 'sg' | 'pl'
            possessive: str | None = None, # None|'1sg'|'2sg'|'3sg'|'1pl'|'2pl'|'3pl'
            case: str = "nom",            # 'nom'|'acc'|'dat'|'loc'|'abl'|'gen'|'ins'
            ) -> str

def paradigm_noun(headword: str) -> dict
```

- `headword`: yalın isim ("kitap", "ev", "burun", "su", "araba"). Ekli DEĞİL.
  Birleşik isim ("ana dil") → **yalnız SON token çekilir**, öncekiler aynen öne eklenir
  (fiil `inflect_last_token` emsali; `_decline_last_token` yardımcı).
- Çıktı: tek string, küçük harf, Türkçe karakterlerle.
- Türkçede olmayan/anlamsız birleşim istenirse yine biçim üretilir (motor betimleyicidir,
  kabul-edilebilirlik sözlüğün işi değil). Geçersiz `number/possessive/case` → `ValueError`.

### Ek katmanları (GENİŞ — ayrı yardımcılar, `decline` çekirdeğinden SONRA uygulanır)
```python
def predicative(headword: str, *, person: str = "3sg", **core) -> str   # -DIr / kişi ekleri
def with_ki(headword: str, *, case: str = "loc", **core) -> str          # -ki (aitlik)
def equative(headword: str) -> str                                        # -CA (eşitlik)
```
- `ins` (ile-hâli, -lA) çekirdek `case` değeri olarak da sunulur (kalemle, arabayla).
- Ayrıntı §7'de.

---

## 2. İsim gövdesi (NounStem) — parse_noun

Yalın başlıktan türet (SAKLA-ma, sınıf tut):

| alan | tip | anlam |
|---|---|---|
| `headword` | str | tam başlık |
| `prefix` | str | birleşik isimde önceki tokenlar ("ana ") |
| `root` | str | çekilecek çıplak kök ("kitap", "ev") |
| `softens` | bool | son ünsüz ünlü önünde yumuşar (kitap→kitab) |
| `drops_vowel` | bool | son hece ünlüsü ünlü önünde düşer (burun→burn) |
| `doubles` | bool | son ünsüz ünlü önünde ikizleşir (hak→hakk, his→hiss) |
| `special` | str \| None | zamir/istisna anahtarı (su, ben, sen, o, bu, şu, ne) |

`softens`, `drops_vowel`, `doubles` **BİRLİKTE** olabilir (şehir: yalnız drops; hak: yalnız
doubles; genelde biri). Harmoni sınıfı SAKLANMAZ — `last_vowel(root)`'tan hesaplanır (#5).

---

## 3. Morfofonoloji (kurallar — üret, saklama)

Ünlü uyumu, ünsüz sertleşmesi (fstkçşhp), kaynaştırma `y` — fiil SPEC §2 ile AYNI;
yardımcılar `morphology.py`'den import edilir. İsme özgü kurallar:

### 3.1 Kök varyantı — `root_variant(vs, vowel_next: bool) -> str`
Bir sonraki segment ÜNLÜ ile başlıyorsa (`vowel_next=True`) ve ilgili bayrak açıksa kök
değişir; aksi hâlde çıplak kök döner. **Yalnız kök sınırında** olur (araya ünsüz-başlı
ek — çoğul -lAr — girerse kök KORUNUR).

- **softens** (t→d, p→b, ç→c, k→ğ; `nk`→`ng`): kitap→kitab, ağaç→ağac, kanat→kanad,
  bebek→bebeğ, renk→reng, çocuk→çocuğ. Yalnız `vowel_next`. Ünsüz-başlı ek önünde kök sert:
  kitap-ta (loc), kitap-lar (çoğul), kitap-tan (abl) — p KORUNUR.
- **drops_vowel**: son hecenin ünlüsü düşer: burun→burn, ağız→ağz, alın→aln, şehir→şehr,
  oğul→oğl, göğüs→göğs. Yalnız `vowel_next`. Ünsüz-başlı ek önünde ünlü korunur:
  burun-lar, burun-dan. Not: bir isim hem drops hem softens olabilir (yok denecek kadar
  nadir; sette drops-only ve softens-only ayrı).
- **doubles**: son ünsüz ikizleşir: hak→hakk, his→hiss, af→aff, sır→sırr, ret→redd
  (ret ayrıca t→d softens: red+d = redd). Yalnız `vowel_next`.

### 3.2 Yumuşama KURALI + istisna (softens bayrağı nasıl set edilir)
`p ç t k` (ve `nk`) ile biten kökler için **varsayılan tahmin**:
- **Çok heceli** (≥2 hece) + son harf `p/ç/t/k` → **softens = True** (kitap, ağaç, kanat,
  bebek, kağıt, dolap, sokak). İstisna kümesi `SOFTEN_NO` bunu bozar.
- **Tek heceli** → **softens = False** (top, saç, at, ok, ip, süt, kürk, park). İstisna
  kümesi `SOFTEN_YES` bunu bozar.
- `SOFTEN_NO` (çok-heceli ama SERT kalan — küratörlü): sepet, millet, devlet, saat, dikkat,
  sıfat, sanat, hukuk, merak, ahlak, taahhüt, kanaat, hayat, hâkant… (temsilî; ajan genişletir).
- `SOFTEN_YES` (tek-heceli ama YUMUŞAYAN — küratörlü): dip→dib, uç→uc, kap→kab, but→bud,
  kurt→kurd, yurt→yurd, gök→göğ, cilt→cild, kayıp→kayb (kayıp çok-heceli+drops), renk→reng,
  denk→deng, çok(sıfat, isim-dışı), tek→tek(değişmez), ad→ad… (temsilî; ajan genişletir).
- `nk` ile biten → k→**g** (renk→rengi, denk→dengi, çelenk→çelengi), ğ DEĞİL.

**Hakem notu:** Bu tahmin %100 değil; golden ajanı bağımsız gerçek biçimleri seçer,
uyuşmazlık motorun exception tablosunu düzeltir (fiil aorist-Ir emsali). İstisna kümeleri
KAPALI ve küçük tutulur; kapsam eksiği tabloya eklenir, kural değişmez.

### 3.3 Ünlü düşmesi (drops_vowel) — TAMAMEN leksik
Yüzeyden tahmin YOK — açık liste `DROP_VOWEL`: ağız, alın, boyun, burun, göğüs, karın,
oğul, gönül, şehir, fikir, isim, resim, akıl, nakil, sabır, beyin, koyun, ömür, vakit,
metin, mekez→(merkez? hayır), zehir, şehir, nehir, cehiz(?), keyif→keyf, kayıp, hüküm,
emir, kavim… (temsilî; ajan yaygınları küratörler). Çoğu 2 heceli, son hece dar ünlülü.
`vakit` ayrıca t sert kalır (vakti, vakdi DEĞİL) — yani vakit drops ama softens DEĞİL.

### 3.4 İkizleşme (doubles) — TAMAMEN leksik
Açık liste `DOUBLE`: hak, his, his→(zan→zann), af, sır, ret, had, hat(→hattı), tıp(→tıbbı?
tıp softens değil doubles: tıbbı), zam(→zammı), şık(→şıkkı), cet(→ceddi t→d+double).
(temsilî; ajan yaygın Arapça alıntıları küratörler.)

---

## 4. Durum (hâl) ekleri — çekirdek

| durum | ek | ünlü tipi | buffer (ünlü-final kök) | soften tetikler? |
|---|---|---|---|---|
| nom (yalın) | ∅ | — | — | hayır |
| acc (belirtme) | -I | 4'lü yüksek | **-y-** (kapı-y-ı) | EVET (ünlü-başlı) |
| dat (yönelme) | -A | 2'li alçak | **-y-** (kapı-y-a) | EVET |
| loc (bulunma) | -DA | 2'li alçak + d/t | yok (ünsüz-başlı) | hayır (kitap-ta) |
| abl (ayrılma) | -DAn | 2'li alçak + d/t | yok | hayır (kitap-tan) |
| gen (ilgi) | -In | 4'lü yüksek | **-n-** (kapı-n-ın) | EVET (kitab-ın) |
| ins (ile) | -lA | 2'li alçak | **-y-** (kapı-y-la) | hayır (ünsüz l-başlı; §7) |

**KRİTİK buffer ayrımı:** ünlü-final kökte acc/dat **-y-** (kapıyı, kapıya) ama gen **-n-**
(kapının). loc/abl ünsüz-başlıdır, buffer YOK, d/t sertleşmesi uygulanır (masa-da, kapı-dan;
kitap-ta, ağaç-tan). Genitiv -In ünlü-başlıdır → ünsüz-final kökte yumuşama (kitab-ın).

---

## 5. İyelik (possessive) ekleri

Kök doğrudan iyelik alır (çoğul araya girmezse). Ünlü-final kökte yüksek-ünlü buffer düşer.

| kişi | ünsüz-final | ünlü-final | soften tetikler? | örnek |
|---|---|---|---|---|
| 1sg | -Im | -m | EVET | ev-im, kitab-ım, kapı-m, araba-m |
| 2sg | -In | -n | EVET | ev-in, kitab-ın, kapı-n |
| 3sg | -I | -sI (buffer s) | EVET | ev-i, kitab-ı, kapı-sı, araba-sı |
| 1pl | -ImIz | -mIz | EVET | ev-imiz, kitab-ımız, kapı-mız |
| 2pl | -InIz | -nIz | EVET | ev-iniz, kitab-ınız, kapı-nız |
| 3pl | -lArI | -lArI | HAYIR (l-başlı) | ev-leri, kitap-ları, kapı-ları |

- 1sg/2sg/3sg/1pl/2pl ünlü-başlıdır → kök yumuşar/düşer (kitab-ım, burn-um).
- **3pl -lArI ünsüz-başlıdır (l)** → kök KORUNUR (kitap-ları, p sert). Aynı zamanda -lArI
  çoğul-benzeridir; "evleri" hem "ev+ler+i (3sg)" hem "ev+leri (3pl)" olabilir (kabul, homograf).
- 3sg buffer **s** yalnız ünlü-final kökte (masa-sı); ünsüz-final ve çoğul sonrası yok
  (ev-i, evler-i).

### 5.1 Çoğul + iyelik
Çoğul -lAr araya girince kök korunur, iyelik çoğula eklenir (çoğul ünsüz r ile biter →
iyelik ünsüz-final biçimi): kitap-lar-ım (kitaplarım, p sert), ev-ler-i (evleri),
kitap-lar-ımız (kitaplarımız), ev-ler-iniz (evleriniz).

---

## 6. Pronominal -n- (3. kişi iyelik / zamir + durum) — KRİTİK

3. kişi iyelikten (-(s)I 3sg, -lArI 3pl) SONRA herhangi bir durum eki (nom hariç) gelmeden
önce **buffer -n-** girer:

- ev-i (3sg) + loc → ev-i-**n**-de = **evinde**
- ev-i + acc → ev-i-**n**-i = **evini**
- ev-i + dat → ev-i-**n**-e = **evine**
- ev-i + abl → ev-i-**n**-den = **evinden**
- ev-i + gen → ev-i-**n**-in = **evinin**
- ev-leri (3pl) + loc → ev-ler-i-**n**-de = **evlerinde**
- kitap-ları + dat → kitap-ları-**n**-a = **kitaplarına**

**3. kişi DIŞI iyelik + durum**: normal buffer (pronominal n YOK):
- ev-im (1sg) + loc → **evimde** (im ünsüz-final, -DA ünsüz-başlı, buffer yok)
- ev-im + acc → **evimi** · ev-im + dat → **evime** · ev-im + gen → **evimin**
- ev-in (2sg) + acc → **evini** (ev-in-i; 3sg+acc "evini" ile homograf — ikisi de doğru)

Pronominal -n- ayrıca zamir/işaret gövdelerinde (bu/şu/o) ve -ki sonrasında görülür (§7, §8).

---

## 7. Ek katmanlar (GENİŞ) — çekirdekten sonra

### 7.1 ins / ile-hâli (-lA / -ylA)
2'li alçak; ünlü-final kökte buffer **-y-**: kalem-le, kitap-la, araba-yla, su-yla.
Zamirlerde iyelik+le: ben-im-le (benimle), sen-in-le, on-un-la, biz-im-le, siz-in-le,
onlar-la. `case='ins'` olarak sunulur. Kök yumuşamaz (l ünsüz-başlı): kitap-la (p sert).

### 7.2 predicative / yüklemleme (-DIr + kişi)
Bildirme eki. 4'lü yüksek + d/t sertleşme; ünsüz-başlı (buffer/yumuşama yok).
- 3sg: -DIr → ev-dir, kitap-tır, güzel-dir, su-dur, masa-dır.
- Kişi ekleri (ek-eylem): 1sg -(y)Im (evim/öğrenciyim), 2sg -sIn, 1pl -(y)Iz, 2pl -sInIz,
  3pl -DIrlAr/-lAr. v1'de öncelik 3sg -DIr; kişi ekleri `predicative(person=...)` ile.
- Not: -DIr ünsüz-başlı → yumuşama YOK (kitap-tır, kitab-ır DEĞİL).

### 7.3 -ki (aitlik / relational)
Durum ekinden (çoğunlukla loc/gen) SONRA: ev-de-ki (evdeki), masa-da-ki, yarın-ki,
benim-ki (gen+ki), onun-ki. **Değişmez -ki** — İSTİSNA kümesi `Kİ_ROUND` uyum gösterir:
bugün-kü, dün-kü, gün-kü, öbür-kü (yalnız bu kapalı küme; başkası -ki). -ki'den sonra durum
gelirse pronominal -n-: evdeki-**n**-i (evdekini), benimki-**n**-e.

### 7.4 -CA (eşitlik / equative)
2'li alçak + c/ç sertleşme (sert ünsüz sonrası ç): Türk-çe, İngiliz-ce, çocuk-ça, ben-ce,
güzel-ce, hızlı-ca, sen-ce. `equative()` yardımcısı; kök yumuşamaz (C ünsüz-başlı).

---

## 8. Zamir / özel-ad istisnaları (`special`)

Kapalı küçük tablo. Zamir gövdeleri durum önünde değişir:

| başlık | acc | dat | loc | abl | gen | ins | not |
|---|---|---|---|---|---|---|---|
| ben | beni | **bana** | bende | benden | benim | benimle | dat düzensiz (ban-a) |
| sen | seni | **sana** | sende | senden | senin | seninle | dat düzensiz (san-a) |
| o | **onu** | ona | onda | ondan | onun | onunla | gövde on- (pronominal n) |
| bu | bunu | buna | bunda | bundan | bunun | bununla | gövde bun- |
| şu | şunu | şuna | şunda | şundan | şunun | şununla | gövde şun- |
| biz | bizi | bize | bizde | bizden | bizim | bizimle | düzenli |
| siz | sizi | size | sizde | sizden | sizin | sizinle | düzenli |
| ne | neyi | neye | nede/neyde | neden | neyin | neyle | buffer -y- (ne-y-i) |
| su | suyu | suya | suda | sudan | **suyun** | suyla | gen buffer -y- (düzensiz; normalde -n-) |

- `o/bu/şu` gövdeleri durum önünde **on-/bun-/şun-** olur; çoğul: onlar/bunlar/şunlar,
  onlar-ı (acc). Bu bir pronominal-n çekirdeğidir.
- `su`: gen normalde ünlü-final → -n- (kapının) beklenir ama **suyun** (-y-). İstisna.
- `ben/sen`: dat -A önünde ünlü a→a değil kök e→a (ban-a/san-a) düzensiz; diğer durumlar düzenli.
- Özel adlar: ek öncesi **kesme işareti** (Ankara'da, Ahmet'in) ORTOGRAFİK; motor düz biçim
  üretir, kesme opsiyonel `apostrophe=True` bayrağıyla (v1'de kapsam-dışı, not düşülür).

---

## 9. Kompozisyon algoritması (decline çekirdeği)

Sıra: **ROOT + (çoğul -lAr) + (iyelik) + (durum)**. Soldan sağa; her katman harmoni
kaynağını günceller (son ünlü).

1. `vs = parse_noun(headword)`; `special` varsa §8 tablosundan git.
2. **base** = root. Yumuşama/düşme yalnız kök sınırında, sonraki segment ünlü-başlıysa:
   - çoğul VARSA → araya -lAr (ünsüz) girer, kök KORUNUR; base = root + plural.
   - çoğul YOKSA → sonraki ek (iyelik ya da doğrudan durum) ünlü-başlı mı? `root_variant(vs, vowel_next)`.
3. **iyelik** varsa base'e ekle (ünlü-final base'te buffer kuralları §5); 3. kişi ise
   `has_pron_n=True`.
4. **durum** varsa:
   - nom → ek yok.
   - `has_pron_n` (3. kişi iyelik ya da zamir gövdesi) → durum önüne -n- (§6).
   - değilse ünlü-final base'te acc/dat -y-, gen -n-, ins -y- (§4/§7).
   - loc/abl/predicative ünsüz-başlı → buffer yok, d/t sertleşme.
5. prefix'i (birleşik isim) öne ekle.

**Harmoni her adımda güncel son ünlüden**: kitaplarımızdan = kitap+lar(a)+ımız(ı→ı,u)+dan.
kitap→lar(a-arka)→ım(harmoni a→ı)ız→dan(harmoni ı→a). Doğru: **kitaplarımızdan**.

---

## 10. Golden test tablosu (bağımsız ajan kurar)

En az **30 isim** × çekirdek hücreler; beklenenler **motordan DEĞİL** dilbilgisinden.
Kapsamı ZORUNLU:
1. Düz ünsüz-final: **ev, göz, kalem, kitap(soften), yol, top(soften-yok), okul**
2. Ünlü-final: **kapı, masa, araba, elma, ütü, kutu, arı**
3. Yumuşama: **kitap→kitabı, ağaç→ağacı, kanat→kanadı, bebek→bebeği, renk→rengi(k→g)**
4. Softens-YOK tuzağı: **sepet→sepeti, top→topu, saat→saati, at→atı, millet→milleti**
5. Ünlü düşmesi: **burun→burnu, şehir→şehri, ağız→ağzı, oğul→oğlu, akıl→aklı**
6. İkizleşme: **hak→hakkı, his→hissi, af→affı**
7. Yuvarlak harmoni: **göz→gözü, okul→okulu, burun→burnu, köy→köyü**
8. Zamir istisnaları: **ben→bana, sen→sana, o→ona/onu, bu→bunu, su→suyu/suyun**
9. Çoğul+iyelik+durum zinciri: **kitaplarımızda, evlerinden, gözlerine**
10. Pronominal -n-: **evinde, evini, kitabına, evlerinde**

Her isim için EN AZ: acc/dat/loc/abl/gen 3'er (yalın), plural nom, 3sg poss, 1sg poss,
3sg poss+loc (pronominal n), ins, predicative 3sg. Zamirler için §8 satırı.

Format: `tests/golden_nouns.py` → `GOLDEN_NOUNS = {'kitap': {'acc':'kitabı', 'dat':'kitaba',
'loc':'kitapta', 'gen':'kitabın', 'poss.3sg':'kitabı', 'poss.3sg.loc':'kitabında',
'pl.nom':'kitaplar', ...}, ...}`. Anahtar şeması golden ajanı + motor ajanı arasında SPEC'te
sabit: `case` (yalın durum), `pl.<case>`, `poss.<kişi>`, `poss.<kişi>.<case>`, `ins`,
`pred.3sg`, `ki.<case>`, `ca`.

---

## 11. zeyrek çapraz-kontrol (üçüncü ağ, opsiyonel)
`tests/test_morphology_noun.py`: zeyrek varsa üretilen biçim analiz edilir; çözümlerden biri
kök isme dönmeli. zeyrek yoksa `skip`. zeyrek isim çekimini fiilden daha iyi tanır ama
homograf/türetme çakışmaları olur → SERT KAPI DEĞİL, golden birincil (fiil emsali: 4 zararsız
çakışma sabitlenir, yeni çakışmada test kırılır).

---

## 12. Çıktı entegrasyonu
Motor `entries.morph` DOLDURMAZ — RUNTIME üreticidir (#5). Kart ürünü (2c) ileride
`paradigm_noun()` / `decline()` çağırır. Bu faz yalnız motoru + testleri kurar;
kart entegrasyonu ayrı iş (2c).
