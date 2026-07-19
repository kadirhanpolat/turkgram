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
| Sözdizimi üretim | `turkgram.syntax` | `isim_tamlamasi`, `sifat_tamlamasi`, `cumle_uret`, **`np_uret`** (öbek+niteleyici+tamlayan+durum), **`pp_uret`**, **`degmod_uret`**, **`koordine_np`** |
| **Constituency parser** | `turkgram.parse` | **`parse_phrase`** (token+analiz → `PhraseNode` ağacı; R0-R7 kuralları; SOV özne tespiti; **E3/E4:** ki-cümleleri CompP/RelP, diye-cümleleri DiyeP) |
| **Dependency graph + CoNLL-U** | `turkgram.dependency` | **`constituency_to_dep`** (ağaç → `list[DepToken]`; UD ilişkileri), **`to_conllu`** (CoNLL-U export) |
| **Çözümleme (parse)** | `turkgram.analysis` | **`analyze`** (yüzey → kök+eksen + segmentasyon; fiil/isim/sıfat/sayı/bağlaç/yapım eki; `max_derivation_depth` ile **zincirli türetme** + `Analysis.chain`), **`analysis_to_dict`** (JSON serileştirme; `schema_version`/`confidence`/`hypothetical`) |
| Kök leksikonu + frekans | `turkgram.lexicon` | **`load`** (roots; lazy-cached), **`load_freq`**, `pos_map` (gömülü; opt-in) |
| Disambiguation | `turkgram.disambiguation` | **`rank`**, **`disambiguate`** (aday sıralama + güven; opt-in) |
| Cümle-bağlamı | `turkgram.context` | **`rank_in_context`** (komşuluk kurallarıyla yeniden sıralama; opt-in) |
| **İstatistiksel disambiguation** | `turkgram.statistical` | **`load_model`**, **`rank_statistical`**, **`viterbi`**, `parse_oflazer_full` (opt-in) |
| **Tokenizer + toplu analiz** | `turkgram.tokenize` / `turkgram.analysis` | **`tokenize`** (metin → token listesi: boşluk+noktalama+apostrof), **`parse_text`** (metin → `list[list[Analysis]]`; indeks hizalamalı, H-08 cache, `rank_in_context` entegrasyonu) |
| **CLI** | `turkgram.__main__` | `python -m turkgram analyze <yüzey> [--format text\|json] [--roots a,b] [--depth N] [--disambiguate] [--lexicon]` · `python -m turkgram version` (sürüm + `DATA_VERSION` + `ANALYSIS_DICT_SCHEMA_VERSION`) |
| **Hecelemleme + vurgu** | `turkgram.syllabify` | **`syllabify`** (hece listesi: gel·di·ği·miz), **`stress`** (0-tabanlı vurgulu hece indeksi), **`stress_mark`** (AN·ka·ra; Türkçe büyük harf) |
| **Yazım denetimi** | `turkgram.spellcheck` | **`is_valid`** (morfoloji tabanlı geçerlilik), **`suggest`** (BK-tree + Türkçe-ağırlıklı Levenshtein; **V2:** morfolojik şablon → yüzey yeniden üretim: `"goruyorum"→["görüyorum",…]`), **`check`** → `SpellResult(word, is_valid, suggestions)` |
| **İkileme (reduplication)** | `turkgram.reduplication` | **`full_reduplicate`** (yavaş yavaş), **`converb_reduplicate`** (koşa koşa; -A ulaç × 2), **`m_reduplicate`** (kitap mitap; m-ikileme) |
| Türkçe yüz | `turkgram.tr` | `çekimle`, `ad_çekimle`, `ekfiil`, `ulaç`, `fiilimsi`, `gibilik`, `iken`, `birleşik_çekim`, `türet`, **`çözümle`**, **`yoğunlaştır`**, **`küçült`**, **`sıralı`**, **`dağıtımlı`**, **`edat_obeği`**, **`bağla`**, **`koordine_et`**, **`hecele`**, **`vurgu`**, **`vurgu_işaretle`**, **`yazım_geçerli`**, **`öneri`**, **`denetle`**, **`tam_ikile`**, **`ulaç_ikile`**, **`m_ikile`**, **`isim_obeği`**, **`derece_obeği`**, **`koordinasyon`** |

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

**İkileme (Faz 9d):** Türkçe'nin üç düzenli ikileme türü: `full_reduplicate` (tam ikileme: `yavaş yavaş`,
`ev ev`), `converb_reduplicate` (fiil mastarından -A ulaç biçimi × 2: `koşmak→koşa koşa`,
`gitmek→gide gide`, `yemek→yiye yiye`), `m_reduplicate` (m-ikileme: `kitap→kitap mitap`,
`araba→araba maraba`; m-başlı → ValueError). Analiz: `analyze("koşa koşa", roots=lexicon.load())`
→ `Analysis(kind='reduplication_converb', lemma='koşmak')`. `roots=None` → converb analizi döndürülmez.

**Çözümleme (Faz 2a-6+):** üretimin tersi — yüzey biçimden kök + eksen değerleri + pedagojik
morfem dökümü. *Analysis-by-generation*: üreteç tek doğruluk kaynağı. Sıfat çözümlemesi:
`analyze('bembeyaz', roots={'beyaz'})` → `Analysis(kind='intensify')`. Sayı çözümlemesi:
`analyze('birinci', roots={'bir'})` → `Analysis(kind='ordinal')`,
`analyze('dörder', roots={'dört'})` → `Analysis(kind='distributive')`. **Faz 6 ile yapım
eki çözümlemesi eklendi (tek katman, fiilimsi+çatı dışlı):** `analyze('gözlük', roots={'göz'})`
→ `Analysis(kind='derivation', lemma='göz', kwargs={'suffix':'-lIk'})`. 27 leksik suffix
(isim→isim 8, isim→fiil 8, fiil→isim 11; `-sAl` dahil: toplumsal/evrensel); `roots` ile precision
garantisi. **Zincirli türetme** (`max_derivation_depth=5`): `gözlükçülük` → kök `göz` (3 katman);
`Analysis.chain` pedagojik zinciri tutar, `segments` tüm katmanları düz listede birleştirir.

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
  - Kalan: FST araçları adopt-referans (ikileme adverbial-kurulum ✅ tamamlandı, aşağıya bkz.).
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
  - **D2-devamı ✅ Edat çözümlemesi** (`analysis.py` + `parse.py`, SPEC §7-§9) — ertelenen açıldı:
    tek doğruluk kaynağı `_POSTPOSITIONS` (23 edat); `analyze("için")` → `kind='postposition'`
    (closed-set, additive); `context._POSTP_GOV` türetilir (K2 değişmez); PP düğümü `governs`
    taşır (donmuş `dair`/`ilişkin`/`ait`/`yana` dahil). Homograf-güvenli; drift-lock golden. 29 test.
  - **D3 ✅ Sayı çözümlemesi** (`analysis.py` genişleme) — `ordinal`/`distributive` kind;
    `_NUMBER_SIMPLE_ROOTS` precision garantisi; bileşik yüzeyler çok-token dalında. 24 test.
  - **D4 ✅ Bağlaç morfolojisi** (`conjunction.py`, SPEC `spec/conjunction-spec.md`) —
    `conjoin()` (de/da ses uyumu; fallback None→"de"; korelatif→ValueError), `coordinate()`
    (ikili/üçlü/korelatif; korelatif yalnız 2 öğe). `analyze("de"/"da")` (`kind='conjunction'`,
    bilinçli belirsizlik: "de" hem bağlaç hem fiil). TR API `bağla()`/`koordine_et()`.
    Korpus: 52.458 çağrı, 0 hata. 70 test.
- **Faz 6 ✅** — yapım eki (türetme) çözümlemesi (`analysis.py` + `derivation.py` genişleme):
  - **Tek katman leksik türetme** (fiilimsi+çatı dışlı): 27 suffix (isim→isim 8, isim→fiil 8,
    fiil→isim 11; **`-sAl` eklendi**: toplumsal/ulusal/evrensel). `_LEXICAL_SUFFIXES` + `_DERIVED_POS`
    (`derivation.py`); yeni fonksiyon `_template_to_allomorphs`, `_strip_derivation`,
    `_strip_one_layer`, `_try_derivation_all` (`analysis.py`).
  - `_KINDS`'a `"derivation"` sona (bağlaç sonrası, çekim önceliklenir).
  - Fiil→isim tuzağı: `_strip_derivation` çıplak gövde döner → `_try_derivation_all` mastarı
    yeniden kurar (`seç` + `-mek` → `seçmek`).
  - §8.1 precision: `roots is not None and lemma not in roots → atla`.
  - Hakem: ~14k form (500 lemma × isim+fiil), 0 çökme, 0 genuine miss. 32 golden + 35 test.
  - **Zincirli türetme** (`max_derivation_depth`, BFS): `analyze('gözlükçülük', roots=roots, max_derivation_depth=5)` → `Analysis(chain=(göz, gözlük, gözlükçü))`. `Analysis.chain` pedagojik zincir
    (chain[0]=en derin kök), `segments` tüm morfemler düz: `[(göz,kök),(lük,-lIk),(çü,-CI),(lük,-lIk)]`.
    `max_derivation_depth=1` varsayılanı → sıfır geriye uyum kırılması. Çatı/fiilimsi sınırı doğal
    (bu ekler `_LEXICAL_SUFFIXES` dışı). 26k lemma × depth=3 tarama: 0 çökme. 7 yeni test.
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
- **2026-07-16 ✅** — mimari inceleme + LLM çıktı API + CLI:
  - **Mimari inceleme** — 5 bağımsız Opus-4.8 ajan adversarial critique (42 bulgu;
    `docs/architecture-critique-genisletme.md`). Kimlik kararı: turkgram = bağımsız
    saf-Python gramer kütüphanesi; spaCy entegrasyonu kapsam dışı; NER/dependency-parsing
    kalıcı defer.
  - **H-09 ✅ `lexicon.load()` lazy singleton** — `_load_filtered(frozenset)` +
    `@lru_cache(maxsize=16)`; tekrar çağrılarda 26k TSV yeniden parse edilmez.
  - **H-03 ✅ `analysis_to_dict()`** (`turkgram.analysis`) — `Analysis` → versioned JSON
    dict; alanlar: `schema_version`, `lemma`, `pos`, `kind`, `kwargs`, `hypothetical`,
    `confidence` (dışarıdan; `disambiguate()` çifti), `segments`, `chain` (rekürsif).
    `voice_chain` tuple → list. `ANALYSIS_DICT_SCHEMA_VERSION = "1"`.
  - **H-04 ✅ `DATA_VERSION`** (`turkgram.__init__`) — `"2026-07-16"` sabit; veri
    bütünlüğü testi + CLI sürüm çıktısı.
  - **CLI ✅** (`turkgram/__main__.py`) — `python -m turkgram analyze <yüzey>` (text/json
    format, `--roots`, `--depth`, `--disambiguate`, `--lexicon`) + `version` komutu;
    Windows UTF-8 zorlaması; DoS koruması (200 karakter).
  - 31 yeni test (19 `analysis_to_dict` + 12 CLI); toplam: 3689 test.
- **2026-07-16 ✅** — tokenizer + toplu analiz:
  - **`tokenize(text) → list[str]`** (`turkgram/tokenize.py`) — boşluk + noktalama ayrıştırma +
    apostrof bölme (ASCII U+0027, sağ parçada kalır: `Ankara'nın → ["Ankara", "'nın"]`);
    kıvrık apostrof (U+2019) bölünmez.
  - **`parse_text(text, roots=None, *, max_derivation_depth=1) → list[list[Analysis]]`**
    (`turkgram/analysis.py`) — her token için `analyze()` çağırır; noktalama → `[]` (indeks
    hizalaması korunur); `_cached_analyze` (`lru_cache(maxsize=4096)`, `frozenset` key,
    `roots is not None` ayrımı) H-08 perf borcunu giderir; `rank_in_context` entegrasyonu
    doğrudan beslenebilir (H-10, `context.py` guard zaten mevcuttu).
  - 35 yeni test (26 tokenizer + 9 parse_text); **toplam: 3724 test**.
- **Faz 9 ✅** — hecelemleme + vurgu (`turkgram/syllabify.py`):
  - **`syllabify(word) → list[str]`** — O(n) ünlü-tabanlı hece sınır tespiti; kural kümesi:
    V·CV (birer ünsüz sağa), VC·CV (iki ünsüz ortadan), VCC·CV (üçlü: ilk ikisi sola) +
    **`_VALID_ONSETS`** frozenset'i ile maksimal onset (yabancı küme: `tr`/`kr`/`pr`/`kl` vb.)
    → `elektrik→["e","lek","trik"]`, `kontrol→["kon","trol"]`. Bitişik ünlü → V·V.
    Circumflex dahil: â/î/û `_VOWELS` kümesinde (kâtip→["kâ","tip"]).
  - **`stress(word) → int | None`** — 0-tabanlı vurgulu hece indeksi (baştan); varsayılan son
    hece; `_STRESS_EXCEPTIONS` elle küratörlenmiş 31 giriş (şehir adları + alıntılar):
    `ankara→0`, `istanbul→1` (is·TAN·bul), `stres→0`, `klima→1`. Boş string → `None`.
  - **`stress_mark(word) → str`** — vurgulu heceyi Türkçe-duyarlı büyük harfle işaretle
    (`_tr_upper`: i→İ, ı→I; Python `str.upper()` değil); U+00B7 orta nokta ayıracı:
    `geldi→"gel·Dİ"`, `ankara→"AN·ka·ra"`, `istanbul→"is·TAN·bul"`.
  - `turkgram.tr`: `hecele()` / `vurgu()` / `vurgu_işaretle()` sarmalayıcılar.
  - Hakem: 26.229 leksikon lemması + 31 istisna, 0 çökme.
  - 101 yeni test (50 syllabify + 39 stress_mark + 12 TR denklik/edge); **toplam: 3825 test**.
- **Faz 9b ✅** — yazım denetimi (`turkgram/spellcheck.py`):
  - **`is_valid(word)`** — morfoloji tabanlı geçerlilik: `analyze()` + `lexicon.load()` (opt-in ters); agglütinatif biçimler tam kapsanır (`evlerde`, `gelmişti` → True).
  - **`_BKTree` + Türkçe-ağırlıklı Levenshtein** — 6 Türkçe karakter karfüzyon çifti (ı↔i, ö↔o, ü↔u, ş↔s, ç↔c, ğ↔g) → maliyet 0.5; diğer op 1.0. BK-tree `_frozen` kilidi (lru_cache singleton güvenliği).
  - **`suggest(word, *, max_suggestions=5, max_distance=2.0)`** — **V2: morfolojik şablon yeniden üretim.** (1) V1: BK-tree tüm kelime (çıplak isim typo'ları; `"dag"→["dağ"]`). (2) V2 ek: `analyze(word, roots=None)` → hypothetical analizler → BK-tree kök üzerinde → `_call_generator` ile yüzey yeniden üret (`"goruyorum"→["görüyorum",…]`). V1-önce sıralaması V2'nin doğru distance'ı bloke etmesini önler. Harmoni-tutarsız çok-karakter tiposunda V2 oracle reddi nedeniyle devreye girmez — bilinçli sınır.
  - **`check(word)`** → `SpellResult(frozen=True)` — `is_valid=True` → kısa-devre (BK-tree atlanır).
  - **Türkçe API**: `yazım_geçerli()` / `öneri()` / `denetle()`. **CLI**: `python -m turkgram check <kelime>`.
  - TUZAK: `seker` = `sekmek` geniş 3sg → GEÇERLİ; golden `dag` (dağ) kullandı.
  - Hakem: 26k leksikon, 0 çökme. 59 yeni test (V2: +1 `goruyorum→görüyorum`); **toplam: 4016 test**.
- **Faz 9d ✅** — İkileme (reduplication, `turkgram/reduplication.py`):
  - **`full_reduplicate(word)`** — sözcük tekrarı: `yavaş yavaş`, `ev ev`.
  - **`converb_reduplicate(lemma)`** — fiil mastarından -A ulaç × 2: `gitmek→gide gide`,
    `yemek→yiye yiye`, `okumak→okuya okuya`. ye_de + glide-y otomatik.
  - **`m_reduplicate(word)`** — m-ikileme: `kitap→kitap mitap`, `araba→araba maraba`;
    m-başlı sözcük → `ValueError` (p-ikileme kapsam dışı).
  - Analiz: `analyze("koşa koşa", roots=lexicon.load())` → `Analysis(kind='reduplication_converb',
    lemma='koşmak')`; `analyze("kitap mitap", roots={"kitap"})` → `Analysis(kind='reduplication_m')`.
    `roots=None` → converb analizi döndürülmez.
  - **Türkçe API**: `tam_ikile()` / `ulaç_ikile()` / `m_ikile()`.
  - Hakem: 26k lemma + 3.2k fiil, 0 çökme. 97 yeni test; **toplam: 4015 test**.
- **Faz 9c ✅** — Lemmatizer (`turkgram/lemmatize.py`):
  - **`lemmatize(word)`** → `str | None` — tek kelime veya çok-token → lemma; çözümsüz → `None`.
  - **`lemmatize_text(text)`** → `list[str | None]` — metin → token başına lemma; `context.rank_in_context` ile bağlamsal disambiguation.
  - **`lemmatize_detail(word)`** → `LemmaResult(lemma, pos, confidence, corrected)` — zengin sonuç.
  - **`lemmatize_text_detail(text)`** → `list[LemmaResult | None]` — metin düzeyi zengin API.
  - **Fallback zinciri:** `analyze` → boşsa `spellcheck.suggest` → tekrar `analyze` → yoksa `None`; `corrected=True` flag spellcheck düzeltmesi işaretler.
  - **Türkçe API:** `temel_biçim()` / `temel_biçim_metin()` / `temel_biçim_detay()` / `temel_biçim_metin_detay()`.
  - TUZAK: `roots=None` → `lexicon.load()` otomatik (analyze hypothetical modundan farklı — lemmatizer her zaman leksikon güdümlü).
  - Hakem: 26k leksikon stratified sweep, 0 çökme. 35 yeni test; **toplam: 3922 test**.
- **Faz E ✅** — Sözdizim genişletme (zengin öbek üretimi + constituency parser + dependency graph + CoNLL-U):
  - **E1** — `np_uret(head, *, on_sifatlar, tamlayan, miktar, durum, iyelik)` (tam NP üretimi: `büyük evin kapısını`), `pp_uret`, `degmod_uret`, `koordine_np` (`syntax.py`). TR API: `isim_obeği()` / `derece_obeği()` / `koordinasyon()` (`tr.py`).
  - **E2** — `parse_phrase(tokens, analyses) → PhraseNode` (`parse.py`): `LeafNode`/`PhraseNode` (frozen dataclasses). Kurallar sırası: **R0** NOUN[gen]+NOUN[poss] → NP (belirtili tamlama: `evin kapısı`), **R3** AdjP, **R1** NP (niteleyici* NOUN), **R1b** participle NP, **R2** PP (NP+ADP), **R4** CoordP, **R5** VP+özne ayrımı (SOV: yalın NP → özne dışarı; eğik NP → VP içine).
  - **E5+E6** — `constituency_to_dep(tree) → list[DepToken]` + `to_conllu(tokens)` (`dependency.py`): UD uyumlu (nsubj/obj/nmod:poss/amod/nummod/obl/cc/conj/root); `_process_children` şeffaf baş geçişi (VP içi nesne/tamlayan doğru bağlanır).
  - **E3+E4 (yan cümle desteği, 2026-07-17)** — `parse.py`'ye R6_ki + R7_diye eklendi; R5 stop listesi güncellendi.
    - **R6_ki:** sol∈{VERB/VP/S}+ki → **CompP** (`biliyorum ki geldi`); sol∈{NP}+ki → **RelP** (`öyle bir şey ki gördüm`); sol∈{ADJ/...} → geçiş (R4'e bırak: `iyi ki`). i==0 guard.
    - **R7_diye:** yüzey tabanlı kapalı küme tespiti (`diye` donmuş subordinator; opt-3sg morfolojisi, `kind='converb'` değil); sol-sequence + diye → **DiyeP** (`gelir diye bekledi`); DiyeP S-düzeyinde (VP dışı — R5 stop guard ile güvence altında).
    - Pipeline: R0→R3→R1→R1b→R2→**R6**→**R7**→R4→R5→wrap.
    - Kritik tuzak: `NP ki NP` artık RelP (eski CoordP → R6 önce intercept eder, linguistik olarak doğru).
  - **Kritik tuzak (R0):** belirtili tamlama R1'DEN önce NOUN[gen]+NOUN[poss] → NP; aksi halde gen-isim VP'de yanlış bağlanır.
  - **Kritik tuzak (dependency):** VP başı = S başı olduğunda VP şeffaf geçilmeli; `_process_children` ile VP içi çocuklar (kitabı:obj, evin:nmod:poss) doğru yükleme bağlanır.
  - Hakem: 613 çağrı (E1-E2-E5-E6) + 617 çağrı (E3-E4), 0 çökme. 45 yeni E test; **toplam: 4061 test**.

- **İkileme adverbial-yeniden-kurulum (AdvP) ✅ (2026-07-18)** — parser ikilemeyi tek `AdvP` öbeği olarak yeniden kurar:
  - Tam ikileme (`yavaş yavaş yürüdü` → `VP(AdvP, yürüdü)`) + ulaç ikilemesi (`koşa koşa geldi`) → yeni `AdvP` öbeği; parser **R8_redup** kuralı (`parse._apply_r8_redup`, yüzey-tabanlı, bitişik özdeş çift `_tr_lower` İ/I-güvenli; NOUN-takip guard'ıyla adnominal `uzun uzun yollar` → `NP` korunur). VERB çifti guard'sız (`koşa` optatif-eşsesli → VERB). m-ikileme kapsam dışı (nominal, defer).
  - R8 R0'dan önce; R5 absorpsiyon kümesine `AdvP` (VP-içi tarz zarfı). Dependency: AdvP başı → fiile `advmod`, ikinci token → başa `compound:redup` (UD-geçerli; `dependency.py` açık dallarla).
  - Tasarım: `docs/superpowers/specs/2026-07-18-ikileme-adverbial-design.md`; plan: `docs/superpowers/plans/2026-07-18-ikileme-adverbial.md`. Hakem: 0 çökme + adversarial APPROVE. **+6 test (4102).**

- **m-İkileme nominal-yeniden-kurulum (NP) ✅ (2026-07-18)** — AdvP'nin nominal kardeşi; parser NOUN-tabanlı m-ikilemeyi tek `NP` öbeği kurar:
  - NOUN m-ikileme (`kitap mitap aldı` → `S(NP[kitap mitap], VP[aldı])`, `araba maraba`) → tek `NP` (genelleyici/pekiştirici ad, özne/nesne rolü); parser **R9_mredup** kuralı (`parse._apply_r9_mredup`, R8 emsali): bitişik `NOUN` + yüzey m-testi `m_reduplicate(taban)==taban+" "+reduplikant`. NP olduğu için R1/R5 nominal rolü doğrudan işler (ek entegrasyon yok). Reduplikant (`mitap`) parse-iç `MRED` etiketi (öbek dışına sızmaz).
  - R9 R8'den sonra, R0/R1'den önce. Dependency: taban → başa `compound:redup`; reduplikant upos taban POS'undan miras (NOUN taban→NOUN, ADJ taban→ADJ). **V2:** ADJ-taban (`güzel müzel` → `AdjP`, isim niteler: `güzel müzel elbise` → `NP(AdjP, elbise)`) eklendi; `a.tag in ("NOUN","ADJ")`.
  - Tasarım: `docs/superpowers/specs/2026-07-18-m-ikileme-nominal-design.md`; plan: `docs/superpowers/plans/2026-07-18-m-ikileme-nominal.md`. Hakem: 0 çökme + adversarial APPROVE (V1 HIGH sertleştirme + V2 temiz). **+8 test (4110).**

- **Koordine ikileme/zarf (CoordP) ✅ (2026-07-18)** — R4 (CoordP kuralı) genelleştirildi: `_COORDINABLE=("NP","AdjP","AdvP")` aynı-kategori koordinasyonu:
  - Koordine zarf (`yavaş yavaş ve hızlı hızlı yürüdü` → `VP(CoordP(AdvP ve AdvP), yürüdü)`) + serbest koordine sıfat (`güzel müzel ve çirkin mirkin` → `CoordP(AdjP ve AdjP)`). Karışık kategori (`NP ve AdvP`) koordine olmaz; koordine-NP (`kitap ve kalem`) değişmez.
  - Dependency: konjunkt kategorisi AdvP/AdjP ise CoordP → `advmod` (nominal case-based mantıktan önce); cc/conj → ilk konjunkt başı; compound:redup içeride. AdjP+isim koordinasyonu (R1<R4 sıralaması) kapsam dışı (defer).
  - Hakem: 0 çökme + adversarial APPROVE. **+3 test (4113).**

- **Koordine sıfat niteleyici + isim ✅ (2026-07-18)** — `kırmızı ve mavi araba` / `güzel müzel ve çirkin mirkin elbise` → `NP(CoordP(sıfatlar), isim)`:
  - R1<R4 sıralama engeli (R1 ikinci sıfatı isme kapar) → **R1'den ÖNCE** çalışan yeni kural **R3c** (`_apply_r3c_adj_coord`, R3'ten sonra): `(ADJ|AdjP) (CCONJ (ADJ|AdjP))+ → CoordP` (karışık `çok güzel ve kırmızı` serbest). R1 modifier setine `CoordP` eklendi (R1-zamanında CoordP yalnız R3c'den = sıfat, güvenli).
  - Dependency: NP-child sıfat-CoordP → `amod`. Sözcük sırası attributive/predicative ayırır (sıfat önce → `NP(CoordP, isim)`; sonra → `S(NP, CoordP)`). Tek-ADJ koordinasyonu (`kırmızı ve mavi`) da kapsandı.
  - Hakem: 0 çökme + adversarial (2 MEDIUM geçersiz doğrulandı). **+3 test (4116).**

- **Koordine genitif tamlayan + özel-isim apostrof-ek ✅ (2026-07-19)** — `Ali'nin ve Veli'nin evi` → `NP(CoordP(Ali'nin ve Veli'nin), evi)`:
  - **B1** özel-isim apostrof-ek merge (`_apply_r_proper`, EN BAŞTA): tokenizer `Ali'nin`'i `["Ali","'nin"]` böler → tek `NOUN[case]` yaprağı. Yüzey tabanlı (apostrof kesin sinyal). TUZAK: motor yumuşatır (`Ahmedin`) imla yumuşatmaz (`Ahmet'in`) → deterministik regex durum-sınıflandırıcı (ismi verbatim; belirsiz ek → merge yok, recall-güvenli).
  - **B2** genitif tamlama genellemesi: `_apply_r_gencoord` (R0'dan ÖNCE) `NOUN[gen] (CCONJ NOUN[gen])+ → CoordP`; **R0 genelleşti** possessor(NOUN[gen]|gen-CoordP)+head → NP, head poss ŞART DEĞİL. Yan fayda: `adamın evi` + common-noun koord (`evin ve kapının rengi`) da düzeldi. Dependency: koordine gen-CoordP → `nmod:poss`.
  - Hakem: SHIP (0 CRITICAL/HIGH/MEDIUM; sweep 1540 çağrı 0 çökme). **+11 test (4127).**

- **`-ki` aitlik eki çözümlemesi ✅ (2026-07-19)** — `evdeki`/`benimki`/`içindeki`/`bugünkü` (yeni kind `with_ki`):
  - Üretim vardı (`with_ki`), çözümleme yoktu → casina/ken deseni (marker `k[ıiuü]$` + oracle + delegasyonlu segmentasyon `iç|i=3sg|nde=loc|ki`).
  - TUZAK (hakem HIGH): Kİ_ROUND (bugün/dün/gün/öbür) case/possessive'i yok sayar → tek kanonik hipotez (case=loc).
  - Kapsam dışı V1: stacked -ki (`dakileri`), possessive≠3sg. Hakem SHIP; sweep 1000 çağrı 0 çökme. **+14 test (4179).**

- **Türetilmiş gövde + çekim istifi ✅ (2026-07-19)** — `bencilliği`/`evsizliğini`/`bencilliklerinden` (türetilmiş gövde + durum/iyelik/çoğul):
  - Saf çok-katman türetme (`gözlükçülük`) çalışıyordu ama türetilmiş gövde çekim alamıyordu. `_try_derivation_inflected`: ara türetilmiş gövde D (`bencillik`) + `decline(D,infl)==surface` çift oracle → birleşik analiz (lemma=en-derin kök, chain+çekim ekseni).
  - GATE `max_derivation_depth>=2` (perf; default depth=1 etkilenmez, opt-in). lru_cache'ler eklendi. Hakem SHIP; sweep 1196 çağrı 0 çökme/miss. **+8 test (4187).**

- **İstatistiksel disambiguation coverage artışı ✅ (2026-07-19)** — TrMor2018 gold değerlendirmesiyle HMM doğruluğu **%44→%75**:
  - `tools/eval_statistical.py` (gold accuracy + recall/disambiguation ayrımı). Adımlar: POS-eşleme fix → lexicon-aware refine → full-POS roots → çok-POS enjeksiyon → OOV→Noun fallback.
  - CRF-gate KARARI: ERTELENDİ (HMM covered'da tavana yakın; darboğaz coverage, dizi-modeli değil). Tümü saf-Python, `analyze()` değişmeden, opt-in.

- **analyze() perf ~26× ✅ (2026-07-19)** — tam-leksikon 165→6.3ms; dört recall-güvenli opt (adj O(roots)→O(aday); `_make_frozen` lambda-elenme; copula+conjugate person-ending prune). Davranış-korunumlu (copula 40k + conjugate 50k exhaustive diferansiyel 0 recall-miss).

- **Ünlü düşmesi kapsam ✅ (2026-07-19)** — `DROP_VOWEL` += 15 (omuz/zihin/…/kayıt), `FRONT_HARMONY` += 4 disharmonik (nakil/haciz/kavim/kavis). Set-üyeliği → false-drop yok; lütuf ertelendi (ters-disharmonik). **4229 test.**

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
tg.analyze("toplumsal", roots=roots)           # -sAl eki: Analysis(lemma='toplum', suffix='-sAl')

# Zincirli türetme analizi (Faz 6+, max_derivation_depth)
results = tg.analyze("gözlükçülük", roots=roots, max_derivation_depth=5)
chains = [r for r in results if r.kind == "derivation" and r.chain]
# chains[0].chain[0].lemma  → 'göz'      (en derin kök)
# chains[0].chain           → [Analysis(göz), Analysis(gözlük), Analysis(gözlükçü)]
# list(chains[0].segments)  → [Segment(göz,kök), Segment(lük,-lIk), Segment(çü,-CI), Segment(lük,-lIk)]

tg.analyze("doğalcılık", roots=roots, max_derivation_depth=5)
# → chain: doğal → doğalcı → doğalcılık  (2 katman; doğa→doğal motorda kapsam dışı)
tg.analyze("kutsallaşmak", max_derivation_depth=4)
# → hypothetical zincir: kut → kutsal → kutsallaşmak  (roots=None, arkaik kök)

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

# JSON serileştirme (H-03) — analysis_to_dict + ANALYSIS_DICT_SCHEMA_VERSION
from turkgram import analysis_to_dict, ANALYSIS_DICT_SCHEMA_VERSION
a = tg.analyze("okuduğum", roots={"okumak"})[0]
analysis_to_dict(a)
# {'schema_version': '1', 'lemma': 'okumak', 'pos': 'verb', 'kind': 'participle',
#  'kwargs': {'ptype': 'dik', 'possessive': '1sg'}, 'hypothetical': False,
#  'confidence': None, 'segments': [...], 'chain': []}
#
# Disambiguation güveniyle:
from turkgram.disambiguation import disambiguate
cands = tg.analyze("gelin", roots=lexicon.load())
for a, conf in disambiguate(cands):
    d = analysis_to_dict(a, confidence=conf)  # d['confidence'] ∈ [0,1]

# Tokenizer + toplu analiz
from turkgram import tokenize, parse_text
tokenize("Ali geldi.")                         # ['Ali', 'geldi', '.']
tokenize("Ankara'nın sınırı")                 # ['Ankara', "'nın", 'sınırı']
results = parse_text("Ali eve geldi.", roots=lexicon.load())
# len(results) == len(tokenize("Ali eve geldi."))  — indeks hizalamalı
# results[-1]  → []  (noktalama)
# rank_in_context(tokenize(text), parse_text(text, roots=roots))  — H-10 entegrasyonu

# Hecelemleme + vurgu (Faz 9)
from turkgram.syllabify import syllabify, stress, stress_mark
syllabify("geldiğimiz")                        # ['gel', 'di', 'ği', 'miz']
syllabify("elektrik")                          # ['e', 'lek', 'trik']  (maksimal onset: tr)
syllabify("kontrol")                           # ['kon', 'trol']
syllabify("kâtip")                             # ['kâ', 'tip']          (circumflex)
stress("geldi")                                # 1  (son hece, 0-tabanlı)
stress("ankara")                               # 0  (AN·ka·ra, istisna)
stress("istanbul")                             # 1  (is·TAN·bul, istisna)
stress("")                                     # None
stress_mark("geldi")                           # 'gel·Dİ'
stress_mark("ankara")                          # 'AN·ka·ra'
stress_mark("istanbul")                        # 'is·TAN·bul'
stress_mark("elektrik")                        # 'e·lek·TRİK'

# Yazım denetimi (Faz 9b)
from turkgram import spellcheck, SpellResult
spellcheck.is_valid("evde")                    # True
spellcheck.is_valid("evdte")                   # False
spellcheck.suggest("seker")                    # ['şeker']  (ş/s = distance 0.5)
spellcheck.suggest("gozluk")                   # ['gözlük']  (ö/o + ü/u = distance 1.0)
result = spellcheck.check("dag")
# SpellResult(word='dag', is_valid=False, suggestions=('dağ',))
import turkgram.tr as tr
tr.yazım_geçerli("geliyorum")                  # True
tr.öneri("kapi")                               # ['kapı']
tr.denetle("cok")                              # SpellResult(word='cok', is_valid=False, ...)
# python -m turkgram check evdte
# python -m turkgram check evde

# İkileme (Faz 9d)
from turkgram.reduplication import full_reduplicate, converb_reduplicate, m_reduplicate
full_reduplicate("yavaş")                      # 'yavaş yavaş'
full_reduplicate("ev")                         # 'ev ev'
converb_reduplicate("koşmak")                  # 'koşa koşa'
converb_reduplicate("gitmek")                  # 'gide gide'   (ye_de yumuşama)
converb_reduplicate("yemek")                   # 'yiye yiye'   (ye_de + glide-y)
converb_reduplicate("okumak")                  # 'okuya okuya' (ünlü-final + glide-y)
m_reduplicate("kitap")                         # 'kitap mitap' (k→m)
m_reduplicate("araba")                         # 'araba maraba' (ünlü-başlı: m+word)
# m_reduplicate("masa")                        # → ValueError (m-başlı sözcük)

# İkileme analizi
roots = lexicon.load()
tg.analyze("koşa koşa", roots=roots)           # [Analysis(kind='reduplication_converb', lemma='koşmak')]
tg.analyze("yavaş yavaş", roots={"yavaş"})     # [Analysis(kind='reduplication_full', lemma='yavaş')]
tg.analyze("kitap mitap", roots={"kitap"})     # [Analysis(kind='reduplication_m', lemma='kitap')]
tg.analyze("güle güle", roots=roots)           # belirsiz: reduplication_converb (gülmek) + full (güle)
tg.analyze("koşa koşa")                        # roots=None → [] (converb yok, full hypothetical)

# Zengin öbek üretimi (Faz E1)
from turkgram.syntax import np_uret, pp_uret, degmod_uret, koordine_np
np_uret("kapı")                                 # 'kapı'
np_uret("kapı", tamlayan="ev")                  # 'evin kapısı'
np_uret("kapı", tamlayan="ev", durum="acc")     # 'evin kapısını'
np_uret("öğrenci", on_sifatlar=("başarılı",), miktar="üç")  # 'üç başarılı öğrenci'
np_uret("ev", iyelik="1sg")                     # 'evim'
pp_uret("ev", "göre")                           # 'eve göre'
pp_uret("ben", "için")                          # 'benim için'
degmod_uret("büyük", derece="çok")              # 'çok büyük'
degmod_uret("iyi", derece="en")                 # 'en iyi'
koordine_np(["kitap", "defter", "kalem"], "ve") # 'kitap, defter ve kalem'

# Constituency parser (Faz E2)
from turkgram import tokenize, parse_text
from turkgram.parse import parse_phrase, LeafNode, PhraseNode
tokens = tokenize("öğrenci kitabı okudu")
analyses = parse_text("öğrenci kitabı okudu", roots={"öğrenci", "kitap", "okumak"})
tree = parse_phrase(tokens, analyses)
# tree.tag        → 'S'
# tree.surface    → 'öğrenci kitabı okudu'
# tree.children   → (NP('öğrenci'), VP('kitabı okudu'))

# Dependency graph + CoNLL-U (Faz E5+E6)
from turkgram.dependency import constituency_to_dep, to_conllu
dep = constituency_to_dep(tree)
# dep[0]  → DepToken(id=1, form='öğrenci', upos='NOUN', head=3, deprel='nsubj')
# dep[1]  → DepToken(id=2, form='kitabı',  upos='NOUN', head=3, deprel='obj')
# dep[2]  → DepToken(id=3, form='okudu',   upos='VERB', head=0, deprel='root')
print(to_conllu(dep, sent_id="1", text="öğrenci kitabı okudu"))
# # sent_id = 1
# # text = öğrenci kitabı okudu
# 1  öğrenci  öğrenci  NOUN  decline  Case=Nom|Number=Sing  3  nsubj  _  _
# 2  kitabı   kitap    NOUN  decline  Case=Acc|Number=Sing  3  obj    _  _
# 3  okudu    okumak   VERB  conjugate  Number=Sing|Person=3|Tense=Past  0  root  _  _

# Yan cümle desteği — E3 ki-cümleleri + E4 diye-cümleleri
tokens3 = tokenize("biliyorum ki geldi")
analyses3 = parse_text("biliyorum ki geldi", roots={"bilmek", "gelmek"})
tree3 = parse_phrase(tokens3, analyses3)
# tree3.tag        → 'CompP'  (sol VERB + ki → CompP)
# tree3.children   → (VERB['biliyorum'], CCONJ['ki'], VERB['geldi'])

tokens4 = tokenize("gelir diye bekledi")
analyses4 = parse_text("gelir diye bekledi", roots={"gelmek", "beklemek"})
tree4 = parse_phrase(tokens4, analyses4)
# tree4.tag           → 'S'
# tree4.children[0]   → DiyeP('gelir diye')  ← S-düzeyi, VP içinde DEĞİL
# tree4.children[1]   → VP('bekledi')

# Belirtili tamlama — gen+poss NP (R0 kuralı)
tokens2 = tokenize("evin kapısını gördüm")
analyses2 = parse_text("evin kapısını gördüm", roots={"ev", "kapı", "görmek"})
tree2 = parse_phrase(tokens2, analyses2)
dep2 = constituency_to_dep(tree2)
# dep2[0]  → DepToken(form='evin',     deprel='nmod:poss', head=2)
# dep2[1]  → DepToken(form='kapısını', deprel='obj',       head=3)

# CLI — python -m turkgram
# python -m turkgram analyze okudum
# python -m turkgram analyze okudum --format json
# python -m turkgram analyze gözlükçülük --roots göz --depth 5
# python -m turkgram analyze okudum --disambiguate --lexicon
# python -m turkgram version
# → turkgram 0.X.X  |  data: 2026-07-16  |  dict schema: 1

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
tr.hecele("elektrik")                           # ['e', 'lek', 'trik']
tr.vurgu("ankara")                              # 0
tr.vurgu_işaretle("istanbul")                   # 'is·TAN·bul'
tr.tam_ikile("yavaş")                          # 'yavaş yavaş'
tr.ulaç_ikile("koşmak")                        # 'koşa koşa'
tr.m_ikile("kitap")                            # 'kitap mitap'
tr.tam_ikile("BÜYÜK")                          # 'büyük büyük'  (_tr_lower: B→b)
tr.isim_obeği("kapı", tamlayan="ev", durum="belirtme")  # 'evin kapısını'
tr.isim_obeği("öğrenci", on_sifatlar=("başarılı",), miktar="üç")  # 'üç başarılı öğrenci'
tr.derece_obeği("büyük", derece="çok")         # 'çok büyük'
tr.koordinasyon(["kitap", "defter"], "ve")     # 'kitap ve defter'
```

Fonksiyon: `çekimle`/`çekim_tablosu`/`fiil_çöz` · `ad_çekimle`/`ad_çekim_tablosu`/`ad_çöz` ·
`ekfiil`/`yüklem`/`ki_ekle`/`eşitlik` · `türet` · **`çözümle`** (çözümleme; Türkçe eksen
değerleri + segment) · **`sıralı`**/**`dağıtımlı`** (sayı morfolojisi) · **`edat_obeği`** (edat öbeği) ·
**`bağla`** (de/da ses uyumu) / **`koordine_et`** (ikili/üçlü/korelatif) ·
**`sayıya_çevir`**/**`ondalığa_çevir`**/**`tarihe_çevir`**/**`saate_çevir`** (normalleştirme) ·
**`kısaltma_aç`**/**`normalleştir`** (pipeline) · **`ipa`** (IPA transkripsiyon) · **`yazım_geçerli`**/**`öneri`**/**`denetle`** (yazım denetimi) ·
**`tam_ikile`**/**`ulaç_ikile`**/**`m_ikile`** (ikileme) ·
**`isim_obeği`**/**`derece_obeği`**/**`koordinasyon`** (zengin öbek üretimi, Faz E1).
Parametre: `kip`/`kişi`/`olumsuz`/`yeterlik`/`soru`/`birleşik`/**`çatı`** ·
`durum`/`iyelik`/`sayı`. Çekim tablosu anahtarları da Türkçe (`şimdiki.3tekil`, `çoğul.bulunma`).

## Testler

```bash
pip install -e ".[test]"
pytest
```

Golden testler (`tests/golden_*.py` — fiil/isim/copula/ulaç/fiilimsi/tasvir/çatı/sayı/edat/
tokenizer/hecelemleme/ikileme/lemmatizer/bağlaç/türetme/sözdizimi/dependency ve çözümleme/segmentasyon)
motordan **bağımsız** olarak, elle-doğrulanmış biçimlerle kurulmuştur — motorun kendi çıktısıyla
değil, dilbilgisiyle sınanır.
**4229 test** (slow hariç). Round-trip tam süpürme `-m slow` ile: `pytest -m slow`.

## Lisans

MIT. (Gramer kuralları olgudur; telifli metin içermez — bu yüzden dağıtılabilir.)

Gömülü referans verisi türetilmiş **olgu** içerir (ham kaynak kopyalanmaz):
- Kök leksikonu (`data/lexicon_tr.tsv`) — **Zemberek-NLP** `master-dictionary`'den lemma+POS (Apache-2.0).
- Lemma-frekans (`data/lemma_freq_tr.tsv`) — **hermitdave/FrequencyWords** (OpenSubtitles TR) yüzey-frekansından türetilmiş lemma-sayımı (MIT).
- İstatistiksel model (`data/disambig_*_tr.tsv`) — **TrMor2018** (ai-ku/TrMor2018, MIT) 460k-token eğitim verisinden türetilmiş log-olasılık sayımları; ham metin pakete girmez.

Atıf ve değişiklik beyanı: [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md).


