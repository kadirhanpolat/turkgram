# Faz 2a — Çözümleyici (morphological analyzer) Tasarımı

**Tarih:** 2026-07-12 · **Durum:** onaylı tasarım (brainstorm + 5-mercek adversarial kritik)
· **Kritik sicili:** `docs/faz2a-mimari-kritik.md` (12 bulgu; C-05 mimari revizyonu bu
dokümana işlenmiş hâlidir)

## 0. Bağlam ve kapsam kararları

turkgram Faz 0-1 yalnız ÜRETİR (encode). Faz 2 ters yön: yüzey biçim → kök + eksen
değerleri (çözümleme/parse). Kullanıcı kararları:

- **Katmanlı bölme:** **2a (bu doküman)** = çekirdek analizör: üretecin dili üzerinde
  round-trip + pedagojik morfem dökümü. **2b (ayrı spec, sonra)** = gerçek-metin
  sağlamlığı: geniş kök leksikonu, olasılıksal disambiguation, motor-dışı biçimler.
- **Mimari:** hibrit "aday öner + üreteç doğrula" ailesi; kritik sonrası somut biçimi §2.
- Sabitler: saf Python 3, sıfır bağımlılık, MIT (CLAUDE.md #1/#3). FST araçları
  (Zemberek/TRmorph/turkish-morphology) yalnız adopt-REFERANS, runtime bağımlılığı değil.

**Başarı ölçütü (2a):** üretecin ürettiği her biçim geri çözülür (recall, yapısal) ve
hiçbir çözüm üretecin üretmeyeceği bir (lemma, kwargs) değildir (form-precision, yapısal).

## 1. Mimari — "önek-tabanlı aday + ses-filtreli enumerasyon + üreteç oracle"

Yeni modül `turkgram/analysis.py`. Boru hattı:

### 1.0 Normalizasyon + tokenizasyon (kritik C-01, H-03)
- Girişte `_tr_lower` (İ→i, I→ı; #10 emsali). Boş/`None`/tamamı-boşluk → `ValueError`.
- Yüzey boşluk içeriyorsa YALNIZ iki meşru kalıp:
  1. **Soru grubu:** sondaki token `m[ıiuü]…` şeklindeyse (mI + kişi/ekfiil) soru adayı —
     "geliyor musun", "yapmış mıydı".
  2. **Birleşik önek:** baştaki token(lar) birleşik-fiil öneki adayı — "aday oldu"
     (lemma adayı "aday olmak").
  Başka çok-token girdi → `[]`.

### 1.1 Kök adayları = yüzeyin önekleri (kritik C-05)
- Gövde-tokenin ünlü içeren her öneki aday kök; katmanlı ek-soyma YOK (üretecin
  morfotaktiğinin gölge-kopyası tutulmaz — drift/senkron yükü kalkar).
- Her önek için **ters-mutasyon çeşitleri, üretecin kendi envanterinden türetilir**
  (kritik H-01; elle kopya değil): t→d'nin tersi d→t, k→ğ'nin ğ→k, p→b'nin b→p,
  ç→c'nin c→ç, ye_de i→e, düşen yüksek ünlünün harmoni-uyumlu geri-eklenmesi
  (burnu→burun tipi, isim motoru envanteri).
- Fiil adayı: önek + mAk/mek (harmoniye göre); isim adayı: önek doğrudan.
- Doğal sınır: ≤ len(yüzey) × ~5 aday kök.

### 1.2 Eksen grid'i + SES filtreleri (kritik C-04, C-05, H-02)
Her (kök, pos) için çekim uzayı enumerate edilir; hücre yalnız **kanıtlanabilir-gerekli
yüzey izi** yüzeyde varsa denenir:

| Eksen değeri | Gereklilik önermesi (yüzeyde substring) |
|---|---|
| `pres` | `yor` |
| `fut` | `c[ae]` |
| `evid` / aux `rivayet` | `m[ıiuü]ş` |
| `necess` | `m[ae]l[ıi]` |
| `question` | boşluk + `m[ıiuü]` |
| `aspect=iver/adur/...` | yardımcı kök (`ver`/`dur`/`gel`/`kal`/`yaz`) |
| `voice_chain` | zincir üyesinin izi (ör. `pass` ⇒ `l` veya `n` kök-sonrası bölgede) — GEVŞEK tutulabilir |

- Filtre **yanlış budayamaz**: her biri "bu eksen işaretliyse yüzeyde X izi zorunlu"
  önermesidir; önerme üreteç-golden'ıyla sınanır (bkz. §4 hakem maddesi). Emin olunamayan
  eksene filtre YAZILMAZ (filtresiz = her zaman dene; yalnız maliyet artar, recall asla).
- **Çatı zinciri kapalı küme (kritik C-04):** kanonik sıra (refl|recip ≤1) → (caus ≤3) →
  (pass ≤1) ⇒ 3×4×2 = **24 zincir**. Sınırsız arama yok.
- Yeterlik×olumsuzluk 4 yüzey şekli (-Abil / -AmA / -mA / -AmAyAbil) ayrı hücreler olarak
  grid'de zaten var (kritik H-02) — stripper olmadığı için özel durum gerektirmez.

### 1.3 Oracle doğrulama
- Dedup **doğrulamadan önce**, kanonik kwargs anahtarıyla (M-01): default eksenler atılır
  (`negative=False`, `aspect=None`… kwargs'ta YER ALMAZ); eşitlik `(lemma, pos, kanonik kwargs)`.
- Her aday: üreteç çağrısı `try/except ValueError`; `None` dönüş = red; `çıktı == yüzey`
  ⇔ KABUL. Üreteç tek doğruluk kaynağı → analizör dili ⊆ üreteç dili.
- `functools.lru_cache` üreteç çağrılarında (saf fonksiyonlar); sözcük başına üreteç-çağrı
  bütçesi ölçülür (§4.5).

### 1.4 Segmentasyon (kritik C-02 — ayrı alt-teslimat, "bedava" DEĞİL)
- kwargs doğrulandıktan SONRA deterministik türetilir; oracle'ın kapsamadığı tek alan
  olduğundan **kendi bağımsız golden'ı** vardır.
- Kesim politikası (SPEC'te ayrıntılanır): yüzey dilimleri + kanonik etiket + span;
  kaynaştırma -y-/-n-/-s- SAĞdaki eke bağlı; yumuşama yüzey biçimiyle gösterilir
  (`oku|duğ|um`, etiketler `oku · DIk · Im`); dilimler birleşince yüzeyi verir (span garantisi).
- Precision iddiası yalnız (lemma, kwargs) için geçerlidir: **form-precision**. Segments
  golden-doğrulamalı, by-construction değil.

## 2. API sözleşmesi

### 2.1 İngilizce çekirdek (`analysis.py`)

```python
@dataclass(frozen=True)
class Segment:
    surface: str            # "duğ"
    label: str              # "DIk" (kanonik morfem etiketi)
    span: tuple[int, int]   # yüzeyde [başlangıç, bitiş); dilimler birleşince yüzey

@dataclass(frozen=True)
class Analysis:
    lemma: str                    # "okumak"
    pos: str                      # "verb" | "noun"
    kwargs: Mapping[str, Any]     # KANONİK (default eksen yok)
    segments: tuple[Segment, ...]
    hypothetical: bool            # True = kök hiçbir roots filtresinden geçmedi

def analyze(surface: str, pos: str | None = None,
            *, roots: Collection[str] | None = None) -> list[Analysis]:
```

- `pos=None` → fiil+isim ikisi de; değer verilirse sert filtre; bilinmeyen →
  seçenek-listeleyen `ValueError` (tr.py geleneği).
- Çözümsüz geçerli girdi → `[]` (istisna değil). Geçersiz girdi (boş/tip) → `ValueError`.
- `roots` (lemma kümesi, ör. dict-db kökleri): kümede olmayan lemma elenir, kalanlar
  `hypothetical=False`; verilmezse hepsi `hypothetical=True` (kritik C-03 — sahte-kök
  form-analizi açıkça işaretli; "masa"→mas-A çözümü hypothetical olarak meşru).
- **Deterministik toplam sıralama:** (morfem sayısı ↑, çatısız < çatılı, lemma alfabetik,
  kanonik kwargs serileştirmesi). Golden tam liste sırasını sabitler.
- Yüzey-özdeş, kwargs-farklı çözümler AYRI (geldik: past-1pl ≠ part_dik okuması).
- 2b rezervi: `score` alanı İLERİDE default'lu eklenir (kırıcı değil; şimdi YOK — YAGNI).
- `__init__.py`: `analyze`, `Analysis`, `Segment` dışa açılır; `parse_verb` (üreteç
  gövde-hazırlığı) ↔ `analyze` (yüzey çözümleme) ayrımı docstring'de tek cümle.

### 2.2 Türkçe yüz (`tr.çözümle`) — kritik H-04

```python
def çözümle(yüzey, tür=None, *, kökler=None) -> list[Analysis]
```

- `tür`: `"fiil"|"isim"` → `_TUR`. `kökler` → `roots`.
- Dönen `Analysis.kwargs` **kanonik Türkçe** değere çevrilir: `_KIP`/`_KISI`/`_DURUM`/
  `_TASVIR`/`_CATI` sözlüklerinin ters haritası; alias çakışmasında kanonik akademik
  temsilci (`past→görülen_geçmiş`, `loc→bulunma`, `caus→ettirgen`) — `_ANAHTAR` emsali.
- Türkçe round-trip sözleşmesi: `tr.çekimle(a.lemma, **a.kwargs_türkçe) == yüzey`.
- Segment etiketleri Türkçe yüzde Türkçeleşir (`DIk→ortaç`, `Iyor→şimdiki`) — küçük harita.
- Test = çeviri denkliği (CLAUDE.md #4); biçim doğruluğu çekirdek golden'da.

## 3. Kapsam sınırları (2a'da BİLİNÇLİ YOK)

- **Türetme döngü dışı:** `derivation.py` yapım ekleri verifier'da yok. `-mA/-mAk/-Iş`
  ad-fiilleri `participle` üzerinden SINIRLI kapsanır (üreteç destekliyor). "okuma"nın
  leksik "reading" okuması 2b.
- **Olasılıksal disambiguation yok** — sıralama deterministik ama sıklık/bağlam bilmez (2b).
- **Sözlükselleşmiş biçim uyarısı yok** ("dolmuş","gelir" kompozisyonel analiz alır; M-02 → 2b).
- **Motor-dışı biçimler** tanımca `[]` (2b).
- `lexicon=` gibi ileri-parametre YOK; `roots` basit `Collection[str]` (kritik YAGNI reddi
  sonrası sadeleşmiş hâl; 2b genişletmesi default'lu ek parametreyle kırılmadan yapılır).

## 4. Test stratejisi

1. **Round-trip tam süpürme (recall kanıtı):** morfofonolojik sınıf başına sabit lemma
   seti (düz ünsüz/ünlü-final; yumuşayan git/et; ye_de; aorist-Ir; birleşik "aday olmak";
   arka/ön × düz/yuvarlak; isimde genç-tipi) × üretecin TAM kwargs çarpımı (geçersiz
   kesişim atlanır): `analyze(conjugate(L,**kw))` sonucu `(L, kanonik kw)` içermeli.
   Elle seçilmiş pil DEĞİL (kritik: seçilmiş pil kapsamayı kapatamaz). CI'da `-m slow`;
   commit'te hızlı alt-küme.
2. **Precision golden (BAĞIMSIZ, CLAUDE.md §2):** ~40 yüzey için elle-doğrulanmış TAM
   çözüm kümesi (belirsizler: "gelin" ≥3, "evin" 2, "okuma", "gelmem" aorist-neg-1sg) —
   motora bakmadan, iki bağımsız türetme (A1 emsali). **Tam-küme eşitliği** (fazla çözüm
   = precision hatası olarak yakalanır).
3. **Segmentasyon golden (BAĞIMSIZ):** ~30 biçim elle kesimli; politika SPEC'ten.
4. **tr denkliği:** çeviri + kanonik-alias + Türkçe round-trip.
5. **Korpus + bütçe bekçisi:** dict-db TR başlıkları → temsili çekim üret → hepsi analyze:
   0 istisna, kendini-içerme, **p95 üreteç-çağrısı/sözcük ≤ 2000** ve duvar-saati bütçesi
   assert (performans regresyonu CI'da yakalanır).
6. **Hakem (çok-oy, A1 emsali):** ses-filtrelerinin "yanlış budayamaz" önermeleri tek tek
   sınanır — her filtre için filtrenin budadığı rastgele hücreler üretilir, hiçbirinin
   yüzeyle eşleşmediği doğrulanır; ayrıca dilbilimsel adversarial tur.

## 5. İş akışı ve dosyalar (CLAUDE.md §2 değişmez)

1. **SPEC** `spec/analysis-spec.md` (ana oturum): ses-filtresi önermeleri, ters-mutasyon
   envanteri, segmentasyon kesim politikası, kanonik kwargs tanımı.
2. **Golden'lar** (bağımsız): `tests/golden_analysis.py` (precision),
   `tests/golden_segments.py` (segmentasyon).
3. **Motor:** `turkgram/analysis.py`; `tr.py`'ye `çözümle`; `__init__.py` dışa açma.
4. **Testler:** `tests/test_analysis.py` (golden koşucu + round-trip süpürme + bütçe),
   `tests/test_tr.py` genişletmesi.
5. **Hakem + korpus** → commit `feat(analysis): çözümleyici — Faz 2a`.

Mevcut 2005 test her adımda regresyonsuz.
