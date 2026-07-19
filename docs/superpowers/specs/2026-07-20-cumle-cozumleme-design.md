# SPEC/Tasarım — Cümle çözümleme katmanı (öge etiketleme + cümle türü)

Tarih: 2026-07-20. Ana oturum elle yazdı (CLAUDE.md §2). Referans: Korkmaz *Türkiye
Türkçesi Grameri — Şekil Bilgisi* (cümle bilgisi); geleneksel okul grameri (dilbilgisi).
Wikipedia "Türkçe dilbilgisi" navbox: *Cümlenin ögeleri* + *Cümle* (türleri) satırları.
Telif: yalnız KURAL + terim; düzyazı/örnek KOPYALANMAZ (CLAUDE.md §3).

---

## 1. Amaç

Mevcut `parse.py` (constituency) + `dependency.py` (UD-graph) çıktısının ÜSTÜNE oturan,
**saf analiz** katmanı. İki pedagojik çıktı üretir (Türkçe okul/betimleyici grameri):

1. **Öge çözümleme:** cümlenin ögelerini etiketle — özne / yüklem / nesne (belirtili,
   belirtisiz) / dolaylı tümleç / zarf tümleci / edat tümleci / cümle dışı unsur.
2. **Cümle türü sınıflandırma:** çok-eksenli — yükleme göre (fiil/isim), yüklemin yerine
   göre (kurallı/devrik), olumluluk (olumlu/olumsuz), soru (bool), kip/anlam (emir/istek/
   dilek/şart/gereklilik/haber), yapıya göre (basit/birleşik/sıralı/bağlı), eksiltili (bool).

**Çekirdek değişmez ihlali YOK:** yeni morfoloji yok, üreteç yok. `analyze()`/`parse.py`/
`dependency.py` DOKUNULMAZ. Yeni modül `turkgram/sentence.py`. **OPT-IN.**

## 2. Modül ve API — `turkgram/sentence.py`

```python
@dataclass(frozen=True)
class Element:
    label: str            # kanonik öge etiketi (§4)
    tokens: tuple[str, ...]
    head_id: int          # öge başının dependency id'si (1-tabanlı; yüklem head_id=root)
    aliases: tuple[str, ...] = ()   # tanıdık eşanlamlı (§4, KARMA gelenek — CLAUDE.md §4)

@dataclass(frozen=True)
class SentenceType:
    yuklem_turu: str      # 'fiil' | 'isim'
    yuklem_yeri: str      # 'kurallı' | 'devrik'
    olumluluk: str        # 'olumlu' | 'olumsuz'
    soru: bool
    kip: "str | None"     # 'emir'|'istek'|'dilek'|'şart'|'gereklilik'|'haber' | None
    yapi: str             # 'basit' | 'birleşik' | 'sıralı' | 'bağlı'
    eksiltili: bool

@dataclass(frozen=True)
class SentenceAnalysis:
    text: str
    elements: tuple[Element, ...]
    sentence_type: SentenceType

def analyze_sentence(text: str, *, roots: "Collection[str] | None" = None) -> SentenceAnalysis:
    ...
```

**İç akış (UYGULAMA KARARI — §3):** `tokenize(text)` → `parse_text(text, roots)` → her token için
en-iyi analiz (`disambiguation.rank`) → **token-düzeyi morfolojik durum** üstünden öge relabel (§4)
+ cümle-türü sınıflandırma (§5). `roots=None` → leksikon yüklenmez (etiketler zayıf) →
**kullanım deseni `roots=lexicon.load()`**.

**Türkçe API (`tr.py`):** `cümle_çözümle(metin, kökler=None)` → `SentenceAnalysis`.

## 3. Mimari karar — token-düzeyi morfoloji (dependency/constituency DEĞİL)

**KARAR DEĞİŞİKLİĞİ (uygulama sırasında, ampirik):** İlk tasarım dependency graph üstünden öge
çıkarımı öngörüyordu. Ampirik ölçüm (`constituency_to_dep` golden cümlelerde) gösterdi ki parser
YAPISI kırılgan: özel-ad/çoğul-ad → ADJ yanlış etiketi, özne nesne NP'sine yutuluyor, `değil`→
VERB, ayrı `mI` düşüyor. Bu yapısal hatalar öge etiketlemeyi bozar.

**Uygulanan mimari:** öge grubu **doğrudan token-düzeyi en-iyi analizden + morfolojik durumdan**
kurulur (constituency ağacına GÜVENMEZ). Her token için `rank`'ten en-iyi analiz; öge etiketi
tokenin **durumundan** (case) türetilir:

- **Yüklem** = en sağdaki FİİL-yeteneği olan token (`verb_reading`; homograf noun'a takılmaz,
  `verdi`=noun/verb → verb okuması yüklem); yoksa son nominal (isim cümlesi).
- **Öbek grubu (light chunking):** modifier* (adj/num/det leksikon-POS + demonstratif) + baş isim.
  Zincir isimle biterse nominal öge; derece sözcüğüyle (çok/pek) başlayıp isim başı yoksa zarf
  tümleci. İsim başı + ardıl edat → edat tümleci.
- **Durum→etiket** (§4): acc→belirtili nesne, dat/loc/abl→dolaylı tümleç, nom→özne/belirtisiz nesne.

**Yüzey kapalı-setler** (motor homograf/OOV nedeniyle çözemez): `mI` (regex), `değil`, `yok`,
edat (`postposition._POSTPOSITIONS`), bağlaç, demonstratif (bu/şu/o), derece sözcükleri.

**Neden token-düzeyi:** Türkçe öge çözümlemesi zaten "durum ekine bak" temellidir; token
morfolojisi parser yapısından daha sağlam (özel-ad ADJ hatası, özne yutulması atlanır).
Karşılık: proper-noun-adj homograf (pos_map: ali/çocuk=adj) ve SOV yalın-nom belirsizliği
KALIR (§6 dokümante sınır) — bunlar leksikon-POS/disambiguation kök nedeni, mimari değil.

## 4. Öge etiketleme (deprel + morfolojik durum → kanonik etiket)

| deprel | ek koşul (feats) | Kanonik etiket | Alias (KARMA) |
|--------|------------------|----------------|---------------|
| `root` | upos=VERB | **yüklem** | — |
| `root` | upos∈{NOUN,ADJ} (isim cümlesi) | **yüklem** | — |
| `nsubj` | — | **özne** | — |
| `obj` | `Case=Acc` | **belirtili nesne** | düz nesne |
| `obj` | `Case=Nom` (veya acc-dışı) | **belirtisiz nesne** | — |
| `obl` | `Case∈{Dat,Loc,Abl}` | **dolaylı tümleç** | yer tamlayıcısı |
| `advmod` | — | **zarf tümleci** | — |
| `obl` | zarf-değeri (aşağıda) | **zarf tümleci** | — |
| PP başı / `case`+ADP | — | **edat tümleci** | edat öbeği |
| top-level ünlem/vocative | pos=ünlem, ya da bağlaç | **cümle dışı unsur** | — |

**TUZAK — dolaylı tümleç vs zarf tümleci (semantik, sınır kararı):** Geleneksel okul grameri
-e/-de/-den durumundaki tümleci **dolaylı tümleç** sayar (Korkmaz: *yer tamlayıcısı*). Zaman/
tarz anlamı taşıyan biçimler (bugün, akşama, sabahleyin) **zarf tümleci**dir. Motor semantik
bilmez → **V1 KURALI:** `obl` + `Case∈{Dat,Loc,Abl}` → **dolaylı tümleç** (varsayılan, durum-
tabanlı, deterministik). `advmod` (durumsuz zarf: çok, hızlı, dün — sıfat/zarf leksikon-POS'lu)
→ **zarf tümleci**. Zaman adlarının -de/-e ile zarf-değeri V1'de dolaylı-tümleç olarak kalır
(bilinçli sınır; semantik zaman-adı sözlüğü V2). Bu, dependency `advmod`/`obl` ayrımını AYNEN
kullanır — yeni sınıflandırma yükü yok.

**Alias mekanizması (CLAUDE.md §4 KARMA gelenek):** `Element.aliases` kanonik-dışı tanıdık
terimi taşır (dolaylı tümleç→yer tamlayıcısı). **KULLANICI KARARI (2026-07-20):** kanonik =
geleneksel okul grameri **dolaylı tümleç** (en yaygın öğretilen); alias = Korkmaz akademik
**yer tamlayıcısı**. NOT: bu, CLAUDE.md §4 "kanonik akademik" varsayılanından bilinçli sapmadır
(yalnız bu terim; özne/yüklem/nesne/zarf tümleci iki gelenekte özdeş). Test denkliği ikisini de
sabitler.

## 5. Cümle türü sınıflandırma (eksenler)

Yüklem = dependency root (head=0). Her eksen root + token-akışından deterministik türer.

### 5.1 Yükleme göre — `yuklem_turu`
- root upos == VERB (kind∈{conjugate,converb,...}) → **`fiil`** (fiil cümlesi).
- root upos∈{NOUN,ADJ} (kind∈{decline,copula} — nominal yüklem/ek-fiil) → **`isim`** (isim cümlesi).

### 5.2 Yüklemin yerine göre — `yuklem_yeri`
- Yüklem cümlenin SON (noktalama-dışı) ögesiyse → **`kurallı`**.
- Değilse → **`devrik`**. (Soru edatı `mI` yüklemden SONRA gelir ama yüklemin parçasıdır →
  kurallılığı BOZMAZ; §5.4 mI yüklem-bitişik sayılır.)

### 5.3 Olumluluk — `olumluluk`
- Fiil yüklem: `Polarity=Neg` (kwargs `negative=True`) → **`olumsuz`**; yoksa **`olumlu`**.
- İsim yüklem: `değil` VEYA `yok` token'ı yüklem konumunda → **`olumsuz`** (yüzey kapalı-set;
  motor `değil`/`yok`'u düzgün çözmez → `_NEG_PARTICLES={"değil","yok"}` yüzey tespiti).
  `var`/olumlu nominal → **`olumlu`**.

### 5.4 Soru — `soru` (bool)
- Ayrı `mI` edatı token akışında var mı (`context._QUESTION_PARTICLES={mı,mi,mu,mü}` +
  kişili biçimler `miyim/misin/mısın/muyuz/…` → `_QUESTION_PARTICLE_RE`), VEYA yüklem
  Analysis'inde `question=True` → **`True`**. **TUZAK:** motor ayrı `mi`/`misin`'i
  hypothetical bırakır → yüzey kapalı-set/regex tespiti (bozuk analizden bağımsız).

### 5.5 Kip / anlam — `kip`
Fiil yükleminin `kwargs['tense']`'inden (Analysis) türetilir:
- `imp` → **`emir`**; `opt` → **`istek`**; `cond` → **`şart`** (dilek-şart); `necess` →
  **`gereklilik`**; `wish`/optatif-dışı dilek → **`dilek`** (varsa); diğer (past/pres/fut/
  aorist/evid) → **`haber`**. İsim cümlesi → **`haber`** (varsayılan; ek-fiil bildirir).
  Not: `şart` hem yapı (birleşik) hem kip olabilir; burada YÜKLEM kipi olarak raporlanır.

### 5.6 Yapıya göre — `yapi`
Yan cümle/koordinasyon sayımından (parser öbekleri + bağlaç):
- Tek yüklem, yan cümle yok → **`basit`**.
- Yan cümle öbeği (CompP/RelP/DiyeP) VEYA fiilimsi (converb/participle) yan-yargı VAR →
  **`birleşik`**.
- İki+ bağımsız yüklem, aralarında bağlaç YOK (virgülle sıralı) → **`sıralı`**.
- İki+ bağımsız yüklem, bağlaç (ve/ama/fakat…) İLE bağlı → **`bağlı`**.
- **TUZAK — parser çok-cümle zayıf (CLAUDE.md Faz E sınırı):** koordine/sıralı yüklem
  yapısı parser'da güvenilmez (`Ali geldi ve gitti` düzgün S-koord kurmaz). V1 `yapi`
  sınıflandırması **en-iyi-çaba**: bağlaç token + finit-yüklem sayısı heuristiği; karmaşık
  cümlede yanılabilir (golden basit + net vakalara odaklanır, karmaşık = defer/işaretli).

### 5.7 Eksiltili — `eksiltili` (bool)
Dependency root'u YOKSA veya yüklem konumu boşsa (yüklemsiz cümle: "Herkes içeri!") →
**`True`**. Nadir; V1 yalnız root-yokluğu sinyali.

## 6. Kapsam DIŞI (V1 — bilinçli sınırlar)

- **Leksikon-POS / disambiguation açıkları miras alınır:** `pos_map` (Zemberek) bazı adları
  adj etiketler (ali/çocuk=adj) → proper-noun-adj homograf; yalın-nom özne/nesne SOV belirsizliği
  (`topu`=acc/nom). **Etkisi yalnız yanlış etiket DEĞİL — özne TAMAMEN kaybolabilir:** `Çocuklar
  bahçede oynuyor`'da `Çocuklar`(adj-homograf) modifier zinciriyle `bahçede`'yi yutar → özne düşer.
  Golden'da 2 vaka işaretli (skip); parser/leksikon-POS iyileşince motor DEĞİŞMEDEN düzelir.
- **V2 İYİLEŞTİRME (2026-07-20):** çoğul/iyelik özne kurtarma — niteleme sıfatı morfolojik
  olarak ÇIPLAKtır; çekim eki (çoğul `-lAr`/iyelik) alan adj-etiketli token aslında İSİMdir
  (`Çocuklar`=çoğul→isim başı) → `_classify` MOD/ADV yalnız ÇIPLAK adj-etiketli tokende üretir.
  `Çocuklar bahçede oynuyor` öznesi geri kazanıldı; `kırmızı araba` (çıplak sıfat) bozulmadı.
  KALAN sınır yalnız ÇIPLAK tekil homograf (Ali/Çocuk — çekimsiz, ayırt edilemez).
- **DÜZELTİLDİ (hakem sonrası):** (a) fiil-eşsesli ad özne (Kar/Yaz/Gül = ad + imperatif homograf)
  → gövde finit-fiil yalnız ANLATI zamanında (past/evid/pres/fut/aorist) veya açık bağlaçla
  koordinat yüklem sayılır; imperatif/optatif homograf → özne (yanlış `sıralı` engellendi).
  (b) cümle-son olmayan `mI` (Geldi mi acaba) → soru GLOBAL token taramasıyla tespit (yüklem-bitişik
  şartı kalktı). (c) edat/bağlaç fiil-homografı (göre=gör-e) yüklem tespitinde atlanır.
- **Karmaşık çok-cümle yapı sınıflandırması** (sıralı/bağlı/birleşik ince ayrımı) en-iyi-çaba.
- **Zaman-adı zarf-değeri** (akşama=zarf) → V1 dolaylı tümleç (semantik sözlük V2).
- **Ara cümle / eksiltili / kaynaşmış** ince türler → V1 temel eksenler.
- **Üretim yok** (analiz katmanı) → cümle-türünden cümle üretme YOK.

## 7. Kullanım deseni ve tuzaklar

- `analyze_sentence(text, roots=lexicon.load())` — gerçek POS için leksikon ŞART; `roots=None`
  gürültü modu → öge etiketleri güvenilmez (yalnız yapı-test için).
- Öge span'leri token id (1-tabanlı, dependency ile hizalı) taşır → şeffaflık için `deps`
  alanı ham UD graph'ı verir.
- `değil`/`yok`/`mI` motor tarafından çözülmez → cümle katmanı YÜZEY kapalı-set kullanır
  (interjection/conjunction emsali; bozuk analizden bağımsız, recall-güvenli).

## 8. Test planı (CLAUDE.md §2)

- **Bağımsız golden** (Opus, motor-körü): elle-doğrulanmış cümleler → beklenen (öge listesi
  + cümle-türü eksenleri). Basit fiil/isim cümleleri; olumlu/olumsuz; soru; emir/istek/
  gereklilik/şart; kurallı/devrik. Parser-zayıf vakalar (koordinasyon) golden'da İŞARETLİ
  (beklenen = parser'ın verdiği, ideal değil; regresyon kilidi).
- **Öge denkliği:** kanonik + alias ikisi de sabitlenir.
- **Regresyon:** tam paket + korpus çökme taraması (leksikon cümleleri × analyze_sentence,
  0 çökme). `analyze`/`parse`/`dependency` çıktısı DEĞİŞMEZ (yeni modül, dokunmadan).
- **Hakem:** adversarial — öge yanlış-etiketleme + cümle-türü yanlış-sınıflama + çekirdek
  değişmez ihlali taraması.

## 9. Dosyalar

- `turkgram/sentence.py` — `Element`/`SentenceType`/`SentenceAnalysis`/`analyze_sentence` +
  `_NEG_PARTICLES`/`_QUESTION_PARTICLE_RE` + öge relabel + tür sınıflandırma.
- `turkgram/__init__.py` — export.
- `turkgram/tr.py` — `cümle_çözümle` sarmalayıcı.
- `tests/golden_sentence.py` — bağımsız golden (Opus motor-körü).
- `tests/test_sentence.py` — runner.
- `tools/sweep_sentence.py` — korpus çökme taraması.
- Bu doküman: SPEC/tasarım.
