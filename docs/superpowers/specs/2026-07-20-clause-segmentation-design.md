# SPEC/Tasarım — Cümle katmanı V3: yargı bölme (clause segmentation)

Tarih: 2026-07-20. Ana oturum elle yazdı (CLAUDE.md §2). Referans: Korkmaz *Türkiye
Türkçesi Grameri — Şekil Bilgisi* (cümle bilgisi: basit/birleşik/sıralı/bağlı cümle,
yan cümle = yargı). Wikipedia "Türkçe dilbilgisi" navbox: *Cümle* (yapısına göre).
Telif: yalnız KURAL + terim; düzyazı/örnek KOPYALANMAZ (CLAUDE.md §3).

Öncül: `2026-07-20-cumle-cozumleme-design.md` (V1/V2 öge etiketleme + cümle türü).

---

## 1. Amaç

Mevcut `analyze_sentence` çok-cümleli girdide **tek düz öge listesi** üretir; yargıları
(clause) ayırmaz. V2'deki "çok-cümle öge gate" (özne/nesne heuristiğini çok-yüklemli
cümlede bastırma) bir *geçici çözümdür* — yargılar hâlâ tek düz listede karışıktır.

**V3 hedefi:** cümleyi **yargılara böl** ve her yargının kendi öge çözümlemesini
(özne / tümleç / yüklem) çıkar. Yargı bölme, "çok-cümle gate"i doğal olarak çözer:
her yargı **tek yüklemlidir** → özne/belirtisiz-nesne heuristiği yargı-içinde doğru
uygulanır (bastırmaya gerek kalmaz).

**Kapsam (kullanıcı kararı, 2026-07-20):**
1. **Koordinat yargılar** — bağlı (ve/ama/fakat…) + sıralı (bağlaçsız, seri finit fiil).
2. **Yan cümleler** — fiilimsi (zarf-fiil `gelince`, ortaç `okuyan`) + şart (`gelirse`).
3. **DEFER:** ki'li (`biliyorum ki…`) + diye'li birleşik + iç-içe birleşik cümle.

**Çekirdek değişmez ihlali YOK:** yeni morfoloji/üreteç yok. `analyze()`/`parse.py`/
`dependency.py` DOKUNULMAZ. **ADDITIVE:** mevcut düz `elements` + `sentence_type`
DAVRANIŞI DEĞİŞMEZ (44 golden kilitli); yalnız `SentenceAnalysis`'e yeni `clauses`
alanı eklenir. **OPT-IN** (kullanım deseni `roots=lexicon.load()` aynen).

## 2. Veri modeli — `turkgram/sentence.py`

```python
@dataclass(frozen=True)
class Clause:
    role: str                    # 'temel' | 'yan' | 'bağımsız'
    elements: tuple[Element, ...]   # yargı-içi ögeler (özne/tümleç/yüklem…)
    predicate_id: int            # yüklemin 1-tabanlı token id'si (yüklemsiz→0)
    connector: "str | None"      # bu yargıyı bağlayan koordinat bağlaç ('ve'/'ama'…)
                                 #   veya None (ilk yargı + yan cümleler → None)

@dataclass(frozen=True)
class SentenceAnalysis:
    text: str
    elements: tuple[Element, ...]      # DEĞİŞMEZ (düz, V1/V2 çıktısı)
    sentence_type: SentenceType        # DEĞİŞMEZ
    clauses: tuple[Clause, ...] = ()   # YENİ (V3). Boş cümle → ().
```

`Element` V1'deki ile aynı (label, tokens, head_id, aliases). `clauses` alanı sona
**varsayılan `()`** ile eklenir → mevcut pozisyonel yapı/testler kırılmaz.

## 3. Rol tanımları (`Clause.role`)

Deterministik kural (kip/anlam sınıflaması YOK — kullanıcı "sade" kararı):

- **`yan`** — yükleminin biçimi **bağımlı** (yan-yargı): fiilimsi (converb/participle)
  VEYA şart (cond / `-sA` yüzeyi). Morfolojik bağımlılık; leksik bağlaç yok.
- **`temel`** — cümlenin **ana yargısı**: yan kardeşi VARSA (birleşik cümle) ya da
  cümle **tek yargılıysa** (basit cümle). Yani "ana ve yalnız yargı" da `temel`.
- **`bağımsız`** — koordinat bağımsız yargı: iki+ **yan-olmayan** yüklem varsa
  (sıralı/bağlı cümle) her biri `bağımsız`.

Kural (tek geçişte):
```
non_yan = yan-olmayan yüklemli yargı sayısı
if yargı.yüklem bağımlı (fiilimsi/şart):   role = 'yan'
elif non_yan >= 2:                          role = 'bağımsız'
else:                                       role = 'temel'
```

Örnekler:
| cümle | yargı → rol |
|-------|-------------|
| `Ben eve gidiyorum` (basit) | temel |
| `Ali geldi ve Veli gitti` (bağlı) | bağımsız + bağımsız |
| `Geldi gitti` (sıralı) | bağımsız + bağımsız |
| `Eve gelince yattım` (birleşik/fiilimsi) | yan + temel |
| `Gelirse gideriz` (birleşik/şart) | yan + temel |
| `Koşarak geldi` (birleşik/fiilimsi) | yan + temel |

## 4. Segmentasyon algoritması (token-düzeyi; parser'a GÜVENMEZ)

Mimari V1 ile aynı: `tokenize` → `parse_text` → token-düzeyi en-iyi analiz → `_classify`.
Yargı bölme sınıflanmış token akışı (`toks`) üzerinde yapılır.

### 4.1 Yüklem-sınır tokenları

Bir token bir yargıyı **kapatan yüklem** ise:
- rol **ULAC/ORTAC** (fiilimsi) → yan yüklem sınırı;
- rol **FIIL** + şart (`tense=='cond'` VEYA `tense=='aorist'` ∧ `-sA` yüzeyi) → yan sınır;
- rol **FIIL** + anlatı zamanı (`past/evid/pres/fut/aorist`) → koordinat/ana sınır;
- **ana yüklem** `pred_i` (mevcut V1 tespiti) → HER ZAMAN sınır (emir `git` gibi
  anlatı-dışı ana fiil de dahil);
- rol **NOMPRED** VEYA cümle-sonu nominal ana yüklem (isim cümlesi) → sınır.

**TUZAK — fiil-eşsesli ad özne (Kar/Yaz):** anlatı-dışı, şartsız, bağlaçsız FIIL
sınır SAYILMAZ (imperatif/optatif homografı ad öznedir; `_classify` bunu zaten
çoğunlukla AD olarak verir, ama FIIL rank edilirse sınır olmaz → `_label_body` özne
yapar). Bu, V1'deki `_NARRATIVE_TENSES`/`has_conj_body` gate'inin aynısıdır.

### 4.2 Bölme (soldan sağa tek geçiş)

```
start = 0 ; pending_connector = None
for k, t in toks:
    if t koordinat bağlaç (_COORD_CONJ yüzeyi):   # ve/ama/fakat…
        pending_connector = t.surface             # SONRAKİ yargının bağlacı
        # bağlaç yargı ögesi DEĞİL; boundary metadata
        (start'ı bir sonraki içeriğe taşı — bağlacı yargıya alma)
        continue
    if t yüklem-sınırı (§4.1):
        clause_toks = toks[start .. k]  (bağlaç hariç)
        yargı oluştur(clause_toks, connector=pending_connector)
        start = k+1 ; pending_connector = None
# kuyruk: son yüklemden sonra kalan mI/değil → son yargıya iliştir
```

- **Sondaki `mI`/`değil`** (yüklem eklentisi) son yargının yüklem ögesine katılır
  (V1 `trailing` mantığı, yargı-düzeyinde).
- `de`/`da`/`ki` `_R_CONJ`'dir ama koordinat bağlaç DEĞİLDİR → V1'deki gibi yargı-içi
  "cümle dışı unsur" kalır (ki'li birleşik DEFER).
- Hiç yüklem sınırı bulunmazsa (yüklemsiz/eksiltili) → tek yargı, `predicate_id=0`.

### 4.3 Yargı-içi öge etiketleme

Her yargı `clause_toks` için:
1. Yargının **yüklemi** = span'in yüklem-sınırı tokenı (fiilimsi/şart/finit/nominal).
2. Yüklem DIŞI gövde → **`_label_body`** (V1 while-loop'undan EXTRACT edilen ortak
   yardımcı) → ögeler. Yüklem span'den çıktığı için fiilimsi kendi sol tümlecini
   YUTMAZ (V1 flat'te `Eve gelince` tek zarf tümleci idi; yargıda `Eve`=dolaylı
   tümleç + `gelince`=yüklem AYRI).
3. **Özne/belirtisiz-nesne heuristiği yargı-içinde** uygulanır (tek yüklem → güvenli;
   V2 gate'e gerek yok): gövdede yüklem-olmayan finit yoksa ve ≥2 nom "özne" varsa
   sonuncusu belirtisiz nesne.
4. Yüklem ögesi (`label="yüklem"`, tokens = yüklem + varsa kuyruk mI/değil) eklenir;
   ögeler `head_id`'e göre sıralanır.

**`_label_body` PAYLAŞIMI:** V1'in düz yolu (`analyze_sentence`) ile yargı yolu AYNI
`_label_body`'yi çağırır → tek doğruluk kaynağı, mantık çoğaltması YOK. Düz yol kendi
gate/trailing/yüklem adımlarını AYNEN korur (44 golden kilitli); yargı yolu kendi
per-yargı yüklem+heuristik adımını yapar.

## 5. Örnek çıktılar (golden ground-truth taslağı; bağımsız golden doğrular)

`Eve gelince yattım`:
```
elements (DÜZ, DEĞİŞMEZ): [zarf tümleci(Eve gelince)@2, yüklem(yattım)@3]
clauses:
  Clause(role='yan',   elements=[dolaylı tümleç(Eve)@1, yüklem(gelince)@2], predicate_id=2, connector=None)
  Clause(role='temel', elements=[yüklem(yattım)@3],                          predicate_id=3, connector=None)
```

`Ali geldi ve Veli gitti`:
```
elements (DÜZ, DEĞİŞMEZ): [özne(Ali)@1, yüklem(geldi)@2, cümle dışı unsur(ve)@3, özne(Veli)@4, yüklem(gitti)@5]
clauses:
  Clause(role='bağımsız', elements=[özne(Ali)@1,  yüklem(geldi)@2], predicate_id=2, connector=None)
  Clause(role='bağımsız', elements=[özne(Veli)@4, yüklem(gitti)@5], predicate_id=5, connector='ve')
```

`Gelirse gideriz`:
```
clauses:
  Clause(role='yan',   elements=[yüklem(Gelirse)@1], predicate_id=1, connector=None)
  Clause(role='temel', elements=[yüklem(gideriz)@2], predicate_id=2, connector=None)
```

`Ben eve gidiyorum` (basit): tek Clause(role='temel', elements=düz-öge, predicate_id=3, connector=None).

## 5b. V4 — ki/diye yüzey subordinatörleri + çok-düzey zincir (2026-07-20)

V3 koordinat + fiilimsi/şart bölüyordu; leksik subordinatörler (`ki`/`diye`) yargı-içi
"cümle dışı unsur" kalıyordu (DEFER idi). V4 bunları yüzey-tabanlı (parser R6/R7 emsali)
yan yargı bağlayıcısı olarak çözer. **Kullanıcı kararı:** ki+diye + çok-düzey zincir;
gerçek gömme (aktarma `Gel dedi`, adlaşmış `geldiğini biliyorum`) DEFER.

**`ki` — İLERİ subordinatör** (temel `ki` yan): `Biliyorum ki gelecek` → temel(Biliyorum)
+ yan(gelecek, connector='ki'). Mekanik: `ki` ÖNCESİ token zorla sınır (temel yargı kapanır;
nominal-yüklem homografı `Öyle yorgunum ki` için — yorgunum copula-homograf decline ranklanıp
sınır olmasa da ki-1 zorlar); `ki` sıyrılır (öge değil) → connector='ki'. **ki-domain:** `ki`
sonrası HER yargı `yan` (forced_yan propagasyonu) → `Biliyorum ki gelince görecek` = temel +
yan(gelince,ki) + yan(görecek). connector='ki' yalnız İLK ki-yargısında.

**`diye` — GERİ subordinatör** (yan `diye` temel): `Gelsin diye bekledim` → yan(Gelsin,
connector='diye') + temel(bekledim). Mekanik: `diye` ÖNCESİ token (d-1) zorla sınır → önceki
yargı kapanır; `diye` sıyrılır + ÖNCEKİ yargıyı yan işaretler (connector='diye'). `diye`
morfolojik olarak `demek` opt-3sg'dir ama yüzey kapalı-set tespiti kullanılır (parser
`_CONVERB_VERB_TOKENS` emsali; `kind='converb'` ASLA üretilmez).

**Rol:** `_rec_yan(r)` = `forced_yan` (ki/diye marker) VEYA `_pred_is_yan(pred)` (fiilimsi/şart).
Böylece ki/diye leksik yan + morfolojik yan aynı role kuralına girer (yan/bağımsız/temel §3).

**Kapsam DIŞI (V4):** gerçek gömme (aktarma tümcesi `"Gel" dedi`, adlaşmış yan cümle
`geldiğini biliyorum` — -DIK/-mA argümanı) → token düzeyi mimarisi için çok büyük, DEFER.
`ki`/`diye` içindeki derin yapı (ki-domain'de gelince+görecek iki ayrı yan yargı) en-iyi-çaba
(sözdizimsel iç yapı düzleştirilir).

**Malformed subordinatör konumu — best-effort (hakem HIGH giderildi):** bare/trailing/başlangıç
subordinatör (`Bekledim diye`, `Biliyorum ki`, `ki gelecek` — eksiltili/kesik girdi) GARANTİLİ
değildir. Guard'lar: (1) `ki` YALNIZ segment başındaysa (sonrası içerik) subordine eder →
trailing `Biliyorum ki` ana yargıyı `yan` YAPMAZ; (2) marker (ki/diye) yüklem pozisyonuna
düşerse (`diye`=demek opt pred_i olabilir) `_clause_pred` kept'ten gerçek yüklemi bulur, kept
boşsa yargı üretilmez → phantom `yüklem=('diye',)` ÖNLENİR. Çökme yok; malformed girdide yapı
en-iyi-çaba (regresyon kilidi `test_trailing_bare_subordinator_robust`).

## 6. Kapsam DIŞI (V1 — bilinçli sınırlar)

- **ki'li / diye'li birleşik** (`biliyorum ki gelecek`, `gelsin diye bekledim`) — DEFER.
  Parser'da R6/R7 var ama token-düzeyi katmana taşımak ek iş; `ki`/`diye` yargı-içi
  "cümle dışı unsur" kalır (yargı bölünmez).
- **İç-içe birleşik** (yan cümle içinde yan cümle) — DEFER; V1 düz tek-düzey bölme.
- **Ortaç (sıfat-fiil) iç yapısı** (`Kitabı okuyan çocuk`): ORTAC yan yüklem sınırı
  sayılır (yan yargı), ama sıfat-fiilin ardıl ismi nitelemesi (relative clause NP
  füzyonu) **en-iyi-çaba**; V1 ortacı kendi yan yargısı yapar, ardıl isim ayrı temel
  yargıda kalır (dokümante sınır — golden işaretli).
- **Leksikon-POS / disambiguation açıkları** V1'den miras (proper-noun-adj homograf,
  SOV yalın-nom belirsizliği) — yargı-içi öge etiketlemede de geçerli.
- **Paylaşılan öge** (sıralı cümlede ortak özne: `Kitabı aldı ve okudu` — özne ilk
  yargıda, ikinci ortak) V1'de paylaştırılmaz; her yargı yalnız kendi tokenlarını taşır.
- **Nominal yüklem sınırı — copula VAR / çıplak YOK (hakem MEDIUM):** ek-fiilli nominal
  yüklem (`güzeldi`/`öğretmendi`/`evdeydi` → NOMPRED) yüklem-sınırıdır → copula-yüklem
  koordinasyonu bölünür (`Hava güzeldi ve deniz sıcaktı` → 2 bağımsız). **Copulasız çıplak
  nominal** (`güzel`/`öğretmen` → `decline`, role AD) yüklem-öznesinden ayırt edilemez
  (durum yok, copula yok) → `Hava güzel ve deniz sıcak` tek yargı kalır (best-effort;
  leksikon-disambiguation kök nedeni, mimari değil). `_is_boundary` NOMPRED dalı SPEC §4.1
  ile uyumlu.
- **Fiil-homografı özne (pre-existing, V3-özgü DEĞİL):** disambiguation bazı finit fiilleri
  isim rank eder (`verdi`→`decline`) → `pred_i` seçimi (V1'den miras) o token'ı yüklem
  saymaz → `Ali kitabı aldı Veli defteri verdi` under-segment (tek yargı). V1 flat `elements`
  de aynı; segmentasyon flat `pred_i`'yi devralır → disambiguation iyileşince bedava düzelir.

## 7. Test planı (CLAUDE.md §2)

- **Bağımsız golden** (Opus, motor-körü): elle-doğrulanmış cümleler → beklenen `clauses`
  listesi (her yargı: rol, öge listesi, predicate_id, connector). Kapsam: basit (1 temel),
  bağlı (ve/ama, 2 bağımsız), sıralı (bağlaçsız, 2 bağımsız), birleşik-fiilimsi
  (gelince/koşarak, yan+temel), birleşik-şart (gelirse, yan+temel), çok-öge yan yargı
  (Eve gelince = dolaylı tümleç+yüklem). Parser-zayıf/sınır vakalar İŞARETLİ (skip veya
  beklenen=gerçek regresyon kilidi).
- **Düz `elements` REGRESYONU:** mevcut 44 golden `elements` + `sentence_type` AYNEN
  geçer (additive kanıtı). `test_sentence.py` DEĞİŞMEZ + yeni `test_clause.py`.
- **Korpus çökme taraması:** leksikon/örnek çok-cümleler × `analyze_sentence`, 0 çökme;
  her cümlede `clauses` tutarlılık (yüklem sayısı = temel+bağımsız+yan yüklemli yargı).
- **Hakem:** adversarial — yanlış yargı sınırı (aşırı/eksik bölme), yanlış rol, düz
  `elements` regresyonu, çekirdek değişmez ihlali taraması.

## 8. Dosyalar

- `turkgram/sentence.py` — `Clause` dataclass + `clauses` alanı + `_segment_clauses`
  + `_label_body` extract (düz yol + yargı yolu paylaşır).
- `turkgram/__init__.py` — `Clause` export.
- `turkgram/tr.py` — değişiklik YOK (`cümle_çözümle` zaten `SentenceAnalysis` döner).
- `tests/golden_clause.py` — bağımsız golden (Opus motor-körü).
- `tests/test_clause.py` — runner.
- `tools/sweep_clause.py` — korpus çökme + tutarlılık taraması.
- Bu doküman: SPEC/tasarım.
