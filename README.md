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
| Fiilimsi | `turkgram.nonfinite` | **`converb`** (8 ulaç), **`participle`** (sıfat-fiil/ad-fiil), **`converb_casina`** (-cAsInA), **`converb_ken`** (-ken) |
| Bileşik zaman | `turkgram.compound` | **`compound`** (hikaye/rivayet/şart birleşik çekim; 3çoğul geliyorlardı) |
| Yapım eki (türetme) | `turkgram.derivation` | `derivations` |
| Sıfat morfolojisi | `turkgram.adjective` | **`intensify`** (pekiştirme: bembeyaz, apaçık), **`diminutive`** (-CIk/-ImsI/-ImtIrak) |
| **Sayı morfolojisi** | `turkgram.number` | **`ordinal`** (birinci/dördüncü), **`distributive`** (birer/dörder) |
| **Edat öbeği** | `turkgram.postposition` | **`postposition`** (19 edat; ev için / bana göre / evle) |
| **Bağlaç morfolojisi** | `turkgram.conjunction` | **`conjoin`** (de/da ses uyumu), **`coordinate`** (ikili/üçlü/korelatif) |
| Sözdizimi üretim | `turkgram.syntax` | `isim_tamlamasi`, `sifat_tamlamasi`, `cumle_uret` |
| **Çözümleme (parse)** | `turkgram.analysis` | **`analyze`** (yüzey → kök+eksen + segmentasyon; fiil/isim/sıfat/sayı/bağlaç/yapım eki) |
| Kök leksikonu + frekans | `turkgram.lexicon` | **`load`** (roots), **`load_freq`**, `pos_map` (gömülü; opt-in) |
| Disambiguation | `turkgram.disambiguation` | **`rank`**, **`disambiguate`** (aday sıralama + güven; opt-in) |
| Cümle-bağlamı | `turkgram.context` | **`rank_in_context`** (komşuluk kurallarıyla yeniden sıralama; opt-in) |
| **İstatistiksel disambiguation** | `turkgram.statistical` | **`load_model`**, **`rank_statistical`**, **`viterbi`**, `parse_oflazer_full` (opt-in) |
| Türkçe yüz | `turkgram.tr` | `çekimle`, `ad_çekimle`, `ekfiil`, `ulaç`, `fiilimsi`, `gibilik`, `iken`, `birleşik_çekim`, `türet`, **`çözümle`**, **`yoğunlaştır`**, **`küçült`**, **`sıralı`**, **`dağıtımlı`**, **`edat_obeği`**, **`bağla`**, **`koordine_et`** |

Fiil: 9 kip (5 haber + 4 dilek) + birleşik zaman (`geliyordu`/`gelirmiş`, 3çoğul `geliyorlardı`) +
soru + olumsuz + yeterlik + **tasvir** (tezlik/sürerlik) + **çatı** (ettirgen/edilgen/dönüşlü/
işteş, yığılabilir → dövüştürüldü). İsim: durum × iyelik × çokluk + ekfiil/-ki/-CA, pronominal
-n-, **nominal ek-fiil kopula** (öğrenciydim), **-ken** (evdeyken). Fiilimsi: **8 ulaç** +
**sıfat-fiil/ad-fiil + iyelik/durum istifi** (okuduğum/gitmesini) + **biçim-eklenen ulaçlar**
(-cAsInA gülercesine, -ken gelirken). **Sıfat:** pekiştirme (bembeyaz/apaçık) + küçültme
(-CIk: kısacık; -ImsI: yeşilimsi; -ImtIrak: sarımtırak). **Zamir çekimi:** suppletif çoğul
(ben→biz/seni→siz) + n-gövde zamirleri (hepsini/hepsine/hepsiyle). **Sayı morfolojisi:**
ordinal `-(I)ncI` (birinci/dördüncü/onuncu) + distributif `-(ş)Ar` (birer/dörder/altışar);
çekim delegasyon (`birincinin`). **Edat öbeği:** 19 edat kapalı küme; `için` isim-zamir
asimetrisi (ev için / benim için), `ile` bitişik (evle/okulla).

**Çözümleme (Faz 2a-6):** üretimin tersi — yüzey biçimden kök + eksen değerleri + pedagojik
morfem dökümü. *Analysis-by-generation*: üreteç tek doğruluk kaynağı. Sıfat çözümlemesi:
`analyze('bembeyaz', roots={'beyaz'})` → `Analysis(kind='intensify')`. Sayı çözümlemesi:
`analyze('birinci', roots={'bir'})` → `Analysis(kind='ordinal')`,
`analyze('dörder', roots={'dört'})` → `Analysis(kind='distributive')`. **Faz 6 ile yapım
eki çözümlemesi eklendi (tek katman, fiilimsi+çatı dışlı):** `analyze('gözlük', roots={'göz'})`
→ `Analysis(kind='derivation', lemma='göz', kwargs={'suffix':'-lIk'})`. 27 leksik suffix
(isim→isim 8, isim→fiil 8, fiil→isim 11); `roots` ile precision garantisi.

## Durum / Yol haritası

- **Faz 0 ✅** — bağımsız paket, motor + testler taşındı, Türkçe API (`tr.py`).
- **Faz 1 ✅** (fiil çekim derinleştirme — `docs/faz1-implementation-plan.md`):
  A4 nominal ek-fiil · A5+A6 ulaç envanteri + aorist · A2 tasvir fiilleri · A3
  fiilimsi+iyelik/durum istifi · **A1 çatı** (ettirgen/edilgen/dönüşlü/işteş + yığılma).
- **Faz 2a ✅** — çözümleyici (`analysis.py`, `tr.çözümle`; `docs/faz2a-*`): yüzey →
  kök+eksen + segmentasyon (beş kind). Round-trip sistematik sınıflarda doğrulandı, korpus
  0 çökme. `-Iyor` ünlü-düşmesi, suppletif zamir eğik durumu (`bana`/`sana`) ve nominal
  ekfiil soru grubu (`evde miydi`) kapatıldı.
- **Faz 2b ✅ (kısmen)** — gerçek-metin sağlamlığı:
  - **Birleşik çok-token fiil** (`göz ardı etti`→`göz ardı etmek`) + **soru** (`göz ardı etti mi`)
    — değişken-uzunluk nominal önek (SPEC §8.2).
  - **Gömülü kök leksikonu** (`lexicon.load()`, Zemberek Apache-2.0, ~26k lemma) — çıplak-önek
    gürültüsünü eler (opt-in; `analyze(roots=None)` değişmez).
  - **Olasılıksal disambiguation** (`disambiguation.rank`/`disambiguate`) — dilbilimsel öncelik
    + opsiyonel sıklık + güven (softmax).
  - **Gömülü lemma-frekans** (`lexicon.load_freq()`, hermitdave MIT'ten türetilmiş) — sıklık
    kancasını besler. Motor-tabanlı rebuild (`tools/build_surface_freq.py`): 4033→**20429 lemma**.
  - **Motor-dışı biçimler** (kolay→zor, SPEC→bağımsız golden→motor→hakem): **-cAsInA** gibilik
    ulacı (`converb_casina`, gülercesine), **-ken** zaman ulacı (`converb_ken`/nominal `copula`,
    gelirken/evdeyken), **bileşik zaman** (`compound`, geliyordu; 3çoğul `geliyorlardı`).
  - **Bu biçimlerin ÇÖZÜMLEMESİ** (üretimin tersi) tamamlandı: `-cAsInA` (kind `converb_casina`),
    `-ken` (fiil `converb_ken` + nominal `copula` aux=ken), **bileşik zaman** (zaten `conjugate`+aux
    olarak çözülür → regresyon kilidi). Korpus hakemi ~130k round-trip çağrı, 0 çökme, 0 biçim-özgü miss.
  - **Cümle-bağlamı disambiguation** (`context.rank_in_context`) — kural-tabanlı sözdizimsel katman:
    5 komşuluk kuralı (niteleyici+ad, edat yönetimi, ayrı soru mI, kişi uyumu, tamlayan-iyelik) izole
    sıralamanın üstüne biner; kural yoksa izoleye düşer. Recall-güvenli (opt-in). Ör. `üç gelin`→isim,
    `ben geldim`→1sg, `ben öğretmenim`→copula, `okula doğru`→yönelme.
  - **İstatistiksel disambiguation katmanı** ✅ (madde A — SPEC: `spec/statistical-disambiguation-spec.md`):
    kural-tabanlı `context.py`'nin **bağımsız istatistiksel muadili** + kural/istatistik/gold
    ayrışmalarını ölçen dört-yollu diferansiyel harness (`tools/diff_harness.py`).
    - **Artım-1** (major POS, kaba): `parse_oflazer`, `rank_statistical` (çarpımsal), `viterbi` (HMM);
      gömülü model: 31.190 emisyon + 161 geçiş bigram (TrMor2018, 460k token, MIT).
    - **Artım-2** (tam eksen): `parse_oflazer_full` (tense/case/possessive/voice/ptype);
      ince-taneli HMM durumları (`Verb:past`, `Noun:acc`); 31.310 emisyon + 726 geçiş.
    Saf-Python, opt-in, `analyze`/`context` dokunulmaz. CRF ertelendi (SPEC §9).
  - Kalan: ikileme adverbial-kurulum (sözdizimsel, defer); FST araçları adopt-referans.
- **Faz 3 ✅** — sözcük-sınıfı genişleme:
  - **C1 ✅ Zamir çekimi** — suppletif çoğul (`ben→biz`, `sen→siz`) + n-gövde zamirleri
    (`hepsi/kendi/hiçbiri/…`; eğik: `hepsini/hepsine/hepsiyle`; instrumental istisnası doğru).
    129 yeni golden test.
  - **C2 ✅ Sıfat morfolojisi** (`adjective.py`, SPEC `spec/adjective-spec.md`) —
    pekiştirme `intensify()` (ünlü-başlı algoritmik + ünsüz-başlı kapalı tablo) +
    küçültme `diminutive()` (3 ek: `-CIk`/`-ImsI`/`-ImtIrak`) + sıfat `analyze()` desteği
    (`kind='intensify'|'diminutive'`, pos='adj') + Türkçe API (`yoğunlaştır()`/`küçült()`).
    53 üretim + 28 analiz golden testi.
- **Faz 4 ✅** — sözdizimi üretim: `syntax.py` — `isim_tamlamasi()` (belirtili/belirtisiz isim
  tamlaması: evin kapısı/taş köprüsü) + `sifat_tamlamasi()` + `cumle_uret()` (özne+yüklem kip
  uyumu, pro-drop); `zarf_yap()` (-CA zarfı: güzelce). 57 syntax + 15 zarf golden testi.
- **Faz 5 ✅ (D1-D3)** — sözcük-sınıfı tamamlama:
  - **D1 ✅ Sayı morfolojisi** (`number.py`, SPEC `spec/number-spec.md`) — ordinal `-(I)ncI`
    (birinci/dördüncü; bileşik: yirmi birinci) + distributif `-(ş)Ar` (birer/dörder/altışar;
    yalnız `t→d` sedalılaşma). `tr.py`: `sıralı()`/`dağıtımlı()`. 116 test.
  - **D2 ✅ Edat/ilgeç yönetimi** (`postposition.py`, SPEC `spec/postposition-spec.md`) — 19
    edat kapalı kümesi. Kritik: `için` isim-zamir asimetrisi (`ev için` / `benim için`) +
    `üzere` nom (`ev üzere`). `bitişik=True` ile `ile` → ins (`evle`/`okulla`). `tr.py`:
    `edat_obeği()`. 86 test.
  - **D3 ✅ Sayı çözümlemesi** (`analysis.py` genişleme) — `ordinal`/`distributive` kind;
    `_NUMBER_SIMPLE_ROOTS` precision garantisi; bileşik yüzeyler çok-token dalında. 24 test.
  - **D4 ✅ Bağlaç morfolojisi** (`conjunction.py`, SPEC `spec/conjunction-spec.md`) —
    `conjoin()` (de/da ses uyumu; fallback None→"de"; korelatif→ValueError), `coordinate()`
    (ikili/üçlü/korelatif; korelatif yalnız 2 öğe). `analyze("de"/"da")` (`kind='conjunction'`,
    bilinçli belirsizlik: "de" hem bağlaç hem fiil). TR API `bağla()`/`koordine_et()`.
    Korpus: 52.458 çağrı, 0 hata. 70 test.
- **Faz 6 ✅** — yapım eki (türetme) çözümlemesi (`analysis.py` + `derivation.py` genişleme):
  - **Tek katman leksik türetme** (fiilimsi+çatı dışlı): 27 suffix (isim→isim 8, isim→fiil 8,
    fiil→isim 11). `_LEXICAL_SUFFIXES` + `_DERIVED_POS` (`derivation.py`); yeni fonksiyon
    `_template_to_allomorphs`, `_strip_derivation`, `_try_derivation_all` (`analysis.py`).
  - `_KINDS`'a `"derivation"` sona (bağlaç sonrası, çekim önceliklenir).
  - Fiil→isim tuzağı: `_strip_derivation` çıplak gövde döner → `_try_derivation_all` mastarı
    yeniden kurar (`seç` + `-mek` → `seçmek`). Zincirli türetme kapsam dışı (tek katman).
  - §8.1 precision: `roots is not None and lemma not in roots → atla`.
  - Hakem: ~14k form (500 lemma × isim+fiil), 0 çökme, 0 genuine miss. 32 golden + 35 test.
- **Faz 7 ✅** — `_root_candidates` 3 bilinen sınır fix (`analysis_candidates.py`):
  - **Fix 1 disharmonik alıntı:** hem primary blok hem ters-mutasyon bloğu artık her iki mastar
    varyantını (`-mak`/`-mek`) üretiyor → `inhimak` gibi disharmonik lemmalar bulunur.
  - **Fix 2 monosilab -Iyor guard:** `any(c in _VOWELS for c in taban)` guard'ı kaldırıldı →
    `somak→suyor`, `çomak→çuyor` gibi monosilab ünlü-düşme vakaları kurtarılır.
  - **Fix 3 "yor"-alt-dizi:** `find("yor")` → `rfind("yor")` → `yorgalamak`, `yorumlamak`
    gibi gövde-içi "yor" barındıran lemmalar artık doğru kurtarılır.
  - 5 yeni golden test; 3569 toplam PASS, 0 regresyon.
- **Faz 8 ✅** — metin normalleştirme + IPA transkripsiyon:
  - **`normalization.py`**: `number_to_words` (0–999 milyar aralığı; `1000→"bin"` DEĞİL "bir bin";
    negatif: "eksi kırk iki"; `bool` guard; IEEE 754 `-0.0` fix), `float_to_words` ("üç virgül bir
    dört"), `date_to_words` (ay int/str, validasyon), `time_to_words` (saat/dakika validasyon),
    `expand_abbreviation` (30+ kısaltma tablosu: TL/km/vb/%), `normalize` (token pipeline:
    sayı + kısaltma + sembol genişletme).
  - **`phonology.py`**: `to_ipa` — 28 Türkçe harf → IPA tam eşleme + bağlam-duyarlı kurallar:
    **ğ** (kelime-ortası ünlü-uzama `øː`, kelime-sonu sessiz), **k** (ön-ünlü yanında `/c/`,
    art-ünlü / bağımsız `/k/`), **l** (art-ünlü yanında `/ɫ/`, ön-ünlü / bağımsız `/l/`).
    `ipa_table()` temel eşleme tablosu. Örnekler: `öğrenci→"øːɾendʒi"`, `dağ→"da"`,
    `kelime→"celime"`, `kırk→"kɯɾk"`, `çay→"tʃaj"`.
  - **`tr.py`** sarmalayıcılar: `sayıya_çevir()` / `ondalığa_çevir()` / `tarihe_çevir()` /
    `saate_çevir()` / `kısaltma_aç()` / `normalleştir()` / `ipa()`.
  - 82 yeni test; 3651 toplam PASS, 0 regresyon.

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
tg.analyze("gülercesine", roots={"gülmek"})    # -cAsInA → converb_casina(base='aorist')
tg.analyze("geliyorken", roots={"gelmek"})     # -ken fiil → converb_ken(base='pres')
tg.analyze("evdeyken", roots={"ev"})           # -ken nominal → copula(aux='ken', case='loc')
tg.analyze("gelirken", roots={"gelmek","gelir"})  # belirsiz: converb_ken | copula(gelir+ken)
tg.analyze("geliyordu", roots={"gelmek"})      # bileşik zaman → conjugate(pres, aux='hikaye')

# Yapım eki çözümlemesi (Faz 6)
tg.analyze("gözlük", roots={"göz"})           # Analysis(kind='derivation', lemma='göz',
                                               #   kwargs={'suffix':'-lIk'}, pos='noun')
tg.analyze("çalışkan", roots={"çalışmak"})    # Analysis(kind='derivation', kwargs={'suffix':'-gAn'})
tg.analyze("seçmek", roots={"seç"})           # fiil→isim: stem çıkart, mastar yeniden kur
                                               # Analysis(kind='derivation', lemma='seçmek',
                                               #   kwargs={'suffix':'-Im'})

# Sayı morfolojisi (Faz 5 D1)
from turkgram.number import ordinal, distributive
ordinal("dört")                                # 'dördüncü'
ordinal("yirmi bir")                           # 'yirmi birinci'  (bileşik: son sözcük)
distributive("altı")                           # 'altışar'
distributive("dört")                           # 'dörder'  (t→d sedalılaşma)
tg.decline(ordinal("bir"), case="gen")         # 'birincinin'  (çekim delegasyonu)
tg.analyze("birinci", roots={"bir"})           # Analysis(kind='ordinal', lemma='bir')
tg.analyze("yirmi birinci", roots={"yirmi bir"})  # bileşik ordinal

# Edat öbeği (Faz 5 D2)
from turkgram.postposition import postposition
postposition("ev", "için")                     # 'ev için'  (isim → nom)
postposition("ben", "için")                    # 'benim için'  (zamir → gen)
postposition("okul", "göre")                   # 'okula göre'
postposition("ev", "önce")                     # 'evden önce'
postposition("okul", "ile", bitişik=True)      # 'okulla'  (ünsüz-final ins -la)
postposition("araba", "ile", bitişik=True)     # 'arabayla'  (ünlü-final ins -yla)

# Bağlaç (Faz 5 D4)
from turkgram.conjunction import conjoin, coordinate
conjoin("ev", "de")                            # 'ev de'  (ses uyumu)
conjoin("okul", "de")                          # 'okul da'
coordinate(["Ali", "Ayşe", "Fatma"], "ve")    # 'Ali, Ayşe ve Fatma'
coordinate(["Ali", "Ayşe"], "hem_hem")         # 'hem Ali hem Ayşe'  (korelatif)
tg.analyze("da", roots={"da"})                 # kind='conjunction' (belirsizlik: "da" hem bağlaç)

# Normalleştirme + IPA (Faz 8)
from turkgram.normalization import number_to_words, normalize, expand_abbreviation
number_to_words(1000)                          # 'bin'  (NOT "bir bin")
number_to_words(2026)                          # 'iki bin yirmi altı'
number_to_words(-42)                           # 'eksi kırk iki'
normalize("42 km yol")                         # 'kırk iki kilometre yol'
normalize("TL 100")                            # 'türk lirası yüz'
expand_abbreviation("vb")                      # 've benzeri'

from turkgram.phonology import to_ipa, ipa_table
to_ipa("öğrenci")                              # 'øːɾendʒi'  (ğ → ünlü uzar)
to_ipa("dağ")                                  # 'da'         (kelime-sonu ğ sessiz)
to_ipa("kelime")                               # 'celime'     (k ön-ünlü → /c/)
to_ipa("kırk")                                 # 'kɯɾk'       (k art-ünlü → /k/)
to_ipa("çay")                                  # 'tʃaj'

# Gömülü kök leksikonu (opt-in) — çıplak-önek gürültüsünü eler
from turkgram import lexicon
roots = lexicon.load()                         # ~26k lemma (Zemberek, Apache-2.0)
tg.analyze("evler", roots=roots)               # → yalnız [ev, decline(number='pl')]
lexicon.load("verb")                           # POS filtreli (fiil mastarları)

# Disambiguation (opt-in) — adayları olabilirlik sırasına koy + güven (olasılık)
from turkgram import disambiguation as dis
cands = tg.analyze("gelin", roots=roots)
dis.rank(cands, pos=lexicon.pos_map())         # → [gelin(isim), gelmek(emir)…] (ekonomi+POS)
dis.disambiguate(cands, pos=lexicon.pos_map()) # → [(Analysis, güven), …] güven∈[0,1], ∑=1
dis.rank(cands, freq={"gelmek": 1000})         # sıklık kancası: manuel ağırlık
dis.rank(cands, freq=lexicon.load_freq())      # gömülü lemma-frekansı (OpenSubtitles, MIT)

# Cümle-bağlamı (opt-in) — kural-tabanlı sözdizimsel katman
from turkgram import context as ctx
tokens = ["üç", "gelin"]
per_token = [tg.analyze(t, roots=roots) for t in tokens]
ctx.rank_in_context(tokens, per_token, pos=lexicon.pos_map())  # → gelin = isim (K1 niteleyici)

# İstatistiksel disambiguation (opt-in, Faz 2b madde A)
from turkgram.statistical import load_model, rank_statistical, viterbi
model = load_model()                                    # gömülü TrMor2018 modeli
# Çarpımsal (bağlamsız, token-başına):
rank_statistical(cands, model, surface="gelin")         # → [gelin(isim, prob-↑), gelmek…]
# HMM Viterbi (cümle-düzeyi dizi çözümü):
per_token = [tg.analyze(t, roots=roots) for t in ["üç", "gelin"]]
viterbi(["üç", "gelin"], per_token, model)              # → [[üç...], [gelin(isim)...]]
# Artım-2 — tam eksen çözümleme (Oflazer analiz dizgesinden)
from turkgram.statistical import parse_oflazer_full
parse_oflazer_full("rahatla+Verb^DB+Verb+Caus+Pos+Past+A3sg")
# → ('rahatla', 'Verb', {'tense':'past','person':'3sg','voice':['caus']})
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
tr.sıralı("dört")                                # dördüncü
tr.sıralı("yirmi bir")                           # yirmi birinci
tr.dağıtımlı("altı")                             # altışar
tr.edat_obeği("ev", "için")                      # ev için
tr.edat_obeği("ben", "için")                     # benim için
tr.edat_obeği("okul", "ile", bitişik=True)       # okulla
tr.sayıya_çevir(1000)                           # bin
tr.sayıya_çevir(-42)                            # eksi kırk iki
tr.normalleştir("42 km yol")                    # kırk iki kilometre yol
tr.ipa("öğrenci")                               # øːɾendʒi
tr.ipa("kelime")                                # celime
```

Fonksiyon: `çekimle`/`çekim_tablosu`/`fiil_çöz` · `ad_çekimle`/`ad_çekim_tablosu`/`ad_çöz` ·
`ekfiil`/`yüklem`/`ki_ekle`/`eşitlik` · `türet` · **`çözümle`** (çözümleme; Türkçe eksen
değerleri + segment) · **`sıralı`**/**`dağıtımlı`** (sayı morfolojisi) · **`edat_obeği`** (edat öbeği) ·
**`bağla`** (de/da ses uyumu) / **`koordine_et`** (ikili/üçlü/korelatif) ·
**`sayıya_çevir`**/**`ondalığa_çevir`**/**`tarihe_çevir`**/**`saate_çevir`** (normalleştirme) ·
**`kısaltma_aç`**/**`normalleştir`** (pipeline) · **`ipa`** (IPA transkripsiyon).
Parametre: `kip`/`kişi`/`olumsuz`/`yeterlik`/`soru`/`birleşik`/**`çatı`** ·
`durum`/`iyelik`/`sayı`. Çekim tablosu anahtarları da Türkçe (`şimdiki.3tekil`, `çoğul.bulunma`).

## Testler

```bash
pip install -e ".[test]"
pytest
```

Golden testler (`tests/golden_*.py` — fiil/isim/copula/ulaç/fiilimsi/tasvir/çatı/sayı/edat ve
çözümleme/segmentasyon) motordan **bağımsız** olarak, elle-doğrulanmış biçimlerle
kurulmuştur — motorun kendi çıktısıyla değil, dilbilgisiyle sınanır.
**3651 test** (slow hariç). Round-trip tam süpürme `-m slow` ile: `pytest -m slow`.

## Lisans

MIT. (Gramer kuralları olgudur; telifli metin içermez — bu yüzden dağıtılabilir.)

Gömülü referans verisi türetilmiş **olgu** içerir (ham kaynak kopyalanmaz):
- Kök leksikonu (`data/lexicon_tr.tsv`) — **Zemberek-NLP** `master-dictionary`'den lemma+POS (Apache-2.0).
- Lemma-frekans (`data/lemma_freq_tr.tsv`) — **hermitdave/FrequencyWords** (OpenSubtitles TR) yüzey-frekansından türetilmiş lemma-sayımı (MIT).
- İstatistiksel model (`data/disambig_*_tr.tsv`) — **TrMor2018** (ai-ku/TrMor2018, MIT) 460k-token eğitim verisinden türetilmiş log-olasılık sayımları; ham metin pakete girmez.

Atıf ve değişiklik beyanı: [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md).
