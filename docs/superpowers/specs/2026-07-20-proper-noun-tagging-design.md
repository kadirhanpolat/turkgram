# SPEC/Tasarım — Kural-tabanlı özel-ad etiketleme (proper-noun tagging)

Tarih: 2026-07-20. Ana oturum. Referans: Türkçe imla (özel ad büyük harf + apostrof-ek
ayrımı: `Ankara'da` vs `evde`). Kullanıcı kararı (2026-07-20): kural-tabanlı, kapalı-set;
**istatistiksel/ML NER DEĞİL** (mimari-kararlar 2026-07-16: NER kalıcı kapsam dışı).

---

## 0. Kimlik uyumu (KRİTİK)

Bu **NER DEĞİL** (öğrenme/olasılık yok). **Kural-tabanlı özel-ad tanıma:** kapalı-set
gazetteer (kişi/yer/kurum, OLGU verisi — MIT-güvenli) + Türkçe imla sinyalleri (büyük harf,
apostrof-ek). Deterministik, saf-Python. `_PERSON_NAMES` (sentence.py, çıplak-tekil ad
override) deseninin bağımsız modüle genişlemesi. Motor/analyze DOKUNULMAZ; **OPT-IN.**

## 1. Modül — `turkgram/proper_noun.py`

```python
PERSON_NAMES: frozenset[str]   # küçük harf; kişi adları (Ali/Ayşe/…)
PLACE_NAMES:  frozenset[str]   # 81 il + ülkeler + yaygın yer (İstanbul/Türkiye/Almanya)
ORG_NAMES:    frozenset[str]   # yaygın kurum (küçük, kapalı; TBMM/YÖK/…)

@dataclass(frozen=True)
class ProperNoun:
    surface: str
    type: str        # 'PER' | 'LOC' | 'ORG' | 'PROPER'
    index: int       # 1-tabanlı token id (yüzey sırası)

def proper_type(surface, *, sentence_initial=False, is_common=False) -> str | None:
    """Tek yüzey → 'PER'|'LOC'|'ORG'|'PROPER'|None (kural-tabanlı)."""

def tag(text, *, roots=None) -> list[ProperNoun]:
    """Tokenize + özel-adları etiketle. Apostrof-ekli ad birleştirilir (Ankara'ya→Ankara)."""
```

**Türkçe API (`tr.py`):** `özel_adlar(metin, kökler=None)` → `list[ProperNoun]`.

## 2. Tanıma kuralları (`proper_type`)

Öncelik sırası (ilk eşleşen kazanır):
1. **Gazetteer** (apostrof-eki sıyrılmış tabanla): `PLACE_NAMES`→LOC, `PERSON_NAMES`→PER,
   `ORG_NAMES`→ORG. Konumdan (cümle-başı) BAĞIMSIZ (kesin sinyal).
2. **Apostrof-ek sinyali** (`Ankara'da`/`Ali'nin` — ASCII `'` sonrası ek): büyük-harf taban +
   apostrof → **PROPER** (Türkçe imlada YALNIZ özel ad apostrofla ek alır; `evde` almaz →
   kesin özel-ad sinyali, cümle-başı olsa da).
3. **Cümle-içi büyük harf** (`sentence_initial=False` + baş-harf büyük): **PROPER** (Türkçe
   özel adı her konumda büyük yazar; cümle-içi büyük harf ≈ özel ad).
4. **Cümle-başı büyük harf** (`sentence_initial=True`): belirsiz (her cümle büyükle başlar).
   `is_common=True` (leksikonda ortak ad, ör. `Kitap`) → None; `is_common=False` (OOV, ör.
   `Kadirhan`) → **PROPER**. leksikon-danışması `tag(roots=…)` ile.
5. Aksi → None (özel ad değil).

**TUZAK — büyük-harf ZORUNLU (hakem HIGH):** Türkçe özel ad daima büyük harfle yazılır →
**küçük-harf yüzey hiçbir kural tetiklemez** (kural 0.5: `not base[:1].isupper() → None`).
Gazetteer eşleşmesi de büyük-harf gate'lidir (`deniz`=ad, `Deniz`=PER). Aksi halde gazetteer
homografı 63 küçük-harf ortak lemmayı (deniz/gül/kaya/can…) yanlış etiketlerdi.

**TUZAK — apostrof güçlü ama mutlak değil (hakem LOW):** apostrof-ek (kural 2) standart imlada
yalnız özel adda olur → güçlü sinyal; ama cümle-başı büyük-harf + apostrof ortak addan
(`Kitabı'nda`, imla-dışı) gelirse PROPER verir (nadir/yapay girdi; V1 kabul). Cümle-başı caps
(kural 4) common/proper ayrımı leksikon+analyze danışmasına bağlı; roots=None → cümle-başı OOV
→ PROPER (varsayılan). Kapalı-sınıf işlev/belgisiz sözcükleri (`_NEVER_PROPER`) her konumda elenir.

## 3. `tag()` — token-düzeyi (apostrof birleştirme)

`tokenize(text)` → token akışı. `Ankara'ya` → `["Ankara","'ya"]` (ASCII apostrof böler).
`tag`: bir NAME tokenını takip eden `'ek` tokenı apostrof-sinyali sayılır (kural 2) + `'ek`
ayrı özel-ad DEĞİL (atlanır). Kıvrık apostrof (`Ankara'ya`) bölünmez → tek token, içinde `'`.
`sentence_initial` = ilk içerik tokenı (indeks 1) VEYA cümle-sonu noktalama sonrası (V1: yalnız
indeks 1; çok-cümle defer). `roots` verilirse cümle-başı ortak-ad danışması (`_tr_lower(base)`
leksikonda mı → is_common).

## 4. `sentence.py` entegrasyonu (mevcut override genişlemesi)

`_classify` çıplak-tekil ad override'ı (`_PERSON_NAMES` + `_NOUN_OVERRIDE`) → **`proper_noun`
gazetteer'ine delege**: PER/LOC/ORG gazetteer üyesi (büyük-harf gate'li) → AD (özne adayı),
modifier zincirine yutulmaz. Böylece yer/kurum adları da (`İstanbul güzeldi`→İstanbul özne)
çıplak-tekil override'dan yararlanır. **Element'e TÜR alanı EKLENMEZ** (öge modeli sade kalır;
tür ayrı `proper_noun.tag` ile alınır). `_PERSON_NAMES` sentence.py'den proper_noun'a TAŞINIR
(tek doğruluk kaynağı); sentence.py import eder. Mevcut `test_bare_noun_override` DEĞİŞMEZ.

## 5. Gazetteer içeriği (OLGU — MIT-güvenli)

- **PERSON_NAMES:** mevcut `_PERSON_NAMES` (~90 yaygın Türkçe ad) taşınır.
- **PLACE_NAMES:** 81 Türkiye ili + yaygın ülkeler (Türkiye/Almanya/Fransa/…) + kıta/deniz
  (Asya/Avrupa/Akdeniz…). Küçük harf normalize (`_tr_lower`).
- **ORG_NAMES:** küçük kapalı-set yaygın kurum kısaltması/adı (TBMM/YÖK/TÜBİTAK/…). Kurum
  açık-sınıf → gazetteer küçük tutulur; caps/apostrof sinyali gerisini PROPER yakalar.

Atıf: yer/kişi adları OLGU (telifsiz); gazetteer elle küratörlenir (kaynak kod kopyalanmaz).

## 6. Kapsam DIŞI (V1 — bilinçli)

- **İstatistiksel/ML NER** — kalıcı kapsam dışı (mimari-kararlar, kimlik).
- **Çok-token varlık** (`Mustafa Kemal Atatürk`, `Kadıköy Belediyesi`) — V1 token-düzeyi
  (her token ayrı); span-birleştirme defer.
- **Tür belirsizliği** (`Ordu`=il/ordu, `Van`=il/van) — gazetteer üyesi → LOC (homograf
  bilinçli; bağlam-tabanlı ayrım defer).
- **Cümle-başı çok-cümlede** — V1 yalnız metnin ilk tokenı sentence_initial; nokta-sonrası defer.

## 10. Çok-token varlık span (2026-07-20)

`tag()` bitişik + **tip-uyumlu** özel-ad tokenlarını tek `ProperNoun` span'ine birleştirir
(`ProperNoun.tokens` = bileşen tokenlar; `surface` = boşlukla birleşik; `index` = başlangıç).

**Katılma kuralı (`_can_join`, YÖN + TİP-farkındalıklı — TUZAK, hakem HIGH):** koşulsuz
PROPER-emme AŞIRI birleştirir (`Ankara Abajur`→LOC, cümle-içi büyük-harf ortak ad→PROPER).
Emme yön+tip özeldir:
- **PER span** → ardıl **PER** (Ali Veli) veya **PROPER** (soyad: Yılmaz/Atatürk) alır.
- **LOC/ORG span** → ardıl **YALNIZ head-noun PROPER** (`_HEAD_NOUNS`: Üniversitesi/Belediyesi/
  …) alır; keyfi PROPER (Abajur) ALMAZ → `Ankara Üniversitesi`→LOC ama `Ankara Abajur`→AYRI.
- **PROPER span** → ardıl **PER** (→kişi adı, Kadirhan Ali) veya **PROPER** alır; typed LOC/ORG
  ALMAZ → `Kadirhan Ankara`→AYRI (kişi + yer).
- **İki gazetteer LOC/ORG** (`Türkiye Avrupa`) / **farklı tipli** (`Ali Ankara`) / **araya token**
  (`Ayşe ile Fatma`) → AYRI.

Apostrof span sonunda olabilir (`Mustafa Kemal'in`→PER "Mustafa Kemal"). **Kapsam DIŞI:**
apostrofsuz-çekimli özel ad (`Ali Ankarada`, imla-dışı → Ankarada PROPER → PER'e emilir; doğru
imla `Ali Ankara'ya`→ayrı); org tip-çıkarımı yaklaşık (Ankara Üniversitesi→LOC, idealde ORG).

## 7. Test planı (CLAUDE.md §2)

- **Bağımsız golden** (Opus motor-körü): kişi/yer/kurum + apostrof + cümle-içi caps + cümle-başı
  (common vs OOV) + negatif (ortak ad, küçük harf) → beklenen `[(surface, type, index)]`.
- **sentence entegrasyonu:** `İstanbul güzeldi`→İstanbul özne; `test_bare_noun_override` DEĞİŞMEZ.
- **Regresyon:** tam paket; `_PERSON_NAMES` taşıması sonrası sentence testleri yeşil.
- **Hakem:** adversarial — yanlış-pozitif (ortak ad→proper), apostrof/caps sinyali, kimlik ihlali.

## 8. Dosyalar

- `turkgram/proper_noun.py` — gazetteer + `proper_type` + `tag` + `ProperNoun`.
- `turkgram/__init__.py` — export.
- `turkgram/tr.py` — `özel_adlar` sarmalayıcı.
- `turkgram/sentence.py` — `_PERSON_NAMES` taşı + `_classify` proper_noun gazetteer delege.
- `tests/golden_proper_noun.py` + `tests/test_proper_noun.py`.
- `tools/sweep_proper_noun.py` — leksikon caps taraması (yanlış-pozitif oranı).
- Bu doküman.
