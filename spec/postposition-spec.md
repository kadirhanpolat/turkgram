# Edat/İlgeç Yönetimi SPEC — Faz 5 D2

Referans: Korkmaz *Türkiye Türkçesi Grameri — Şekil Bilgisi* §275–290 (edatlar/ilgeçler).
Kural olgu; düzyazı/örnek cümleler telif dışı kopyalanmadı.

---

## §1 Kapsam

Bu SPEC yalnız **kapalı küme edatlar** için isim öbeği üretimini kapsar.

Edat öbeği = `decline(lemma, case=yönetilen_durum) + ' ' + edat`

Edat **analizi** (`analyze()` içinde `kind="postposition"`) ve PP öbeği doğrulaması §7–§9'da işlenir.
Tasarım: `docs/superpowers/specs/2026-07-17-edat-analizi-design.md`.

**Kapsam dışı (bu SPEC'te işlenmez):**
- Çok-kelimeli edatlar ve zarf-fiil öbekleri (bir türlü, ilgili olarak) → sözdizimsel
- Edatın anlamsal seçimi (hangi edatın kullanılacağı kararı) → uygulamaya bırakılır

---

## §2 Edat–Durum Tablosu

| Edat | Yönettiği durum | Örnek | Not |
|------|-----------------|-------|-----|
| için | nom (isim) / gen (zamir) | ev için / benim için | İsimler yalın; kişi+n-gövde zamirleri genitif. onlar → nom (`onlar için`) |
| ile | nom / ins | ev ile / evle | Bkz. §3 (ayrı vs bitişik) |
| göre | dat | eve göre | — |
| kadar | dat | eve kadar | — |
| karşı | dat | eve karşı | — |
| rağmen | dat | eve rağmen | — |
| doğru | dat | eve doğru | — |
| dek | dat | eve dek | kadar eşanlamlısı |
| değin | dat | eve değin | kadar eşanlamlısı, yazı dili |
| üzere | nom | ev üzere | "bu şart üzere"; fiil-mastar tümleci sözdizimsel (kapsam dışı) |
| önce | abl | evden önce | — |
| sonra | abl | evden sonra | — |
| beri | abl | evden beri | — |
| itibaren | abl | evden itibaren | — |
| başka | abl | evden başka | — |
| dolayı | abl | evden dolayı | — |
| ötürü | abl | evden ötürü | — |
| gibi | nom | ev gibi | Yalın isim kullanılır |
| aşkın | acc | evi aşkın | — |

Toplam: **19 edat**.

---

## §3 ile Allomorfu — Ayrı vs Bitişik

`ile` edatı iki farklı biçimde kullanılır:

### Ayrı yazım (varsayılan)
İsim yalın (nom) halde; `ile` ayrı sözcük olarak eklenir:
```
ev   → ev ile
araba → araba ile
ben  → ben ile   (resmi/ağır; bağlaç)
```

### Bitişik yazım — instrumentalis eki `-lA`
İsmin instrumentalis/araç hali (`case='ins'`) ile özdeştir. `ile` ayrıca eklenmez;
ins hali zaten `ile`'nin bağlı biçimidir:
```
ev   → evle          (decline('ev', case='ins'))
araba → arabayla      (decline('araba', case='ins')) — ünlü-final → -yla
ben  → benimle        (decline('ben', case='ins'))
o    → onunla         (decline('o', case='ins'))
```

**Uygulama:** `postposition(lemma, 'ile', bitisik=True)` → `decline(lemma, case='ins')`
döndürür; sonuna ' ile' EKLENMEZ.

---

## §4 Zamir Entegrasyonu

Zamir morfolojisi `decline()` içinde zaten tanımlıdır (bkz. Faz 3 C1 zamir morfolojisi).
`postposition()` doğrudan `decline()` çağırır; zamir için özel kod YOKTUR:

| Lemma | Edat | İşlem | Sonuç |
|-------|------|--------|-------|
| ben | için | decline('ben', 'gen') + ' için' | benim için |
| sen | göre | decline('sen', 'dat') + ' göre' | sana göre |
| o | ile (ayrı) | decline('o', 'nom') + ' ile' | o ile |
| o | ile (bitişik) | decline('o', 'ins') | onunla |
| biz | sonra | decline('biz', 'abl') + ' sonra' | bizden sonra |
| siz | kadar | decline('siz', 'dat') + ' kadar' | size kadar |
| onlar | için | decline('onlar', 'nom') + ' için' | onlar için |
| bu | gibi | decline('bu', 'nom') + ' gibi' | bu gibi |
| şu | kadar | decline('şu', 'dat') + ' kadar' | şuna kadar |
| hepsi | için | decline('hepsi', 'gen') + ' için' | hepsinin için |

---

## §5 API

```python
def postposition(lemma: str, edat: str, bitisik: bool = False) -> str:
    """İsim lemması + edat → tam edat öbeği.

    Parametreler:
        lemma   : Türkçe kelime kökü (ev, okul, ben, hepsi)
        edat    : Edat adı, küçük harf Türkçe (için, ile, göre, …)
        bitisik : Yalnız 'ile' için geçerli; True → ins biçimini döndürür (evle)

    Döner: tam edat öbeği string'i ("evin için", "evle")

    Hatalar:
        ValueError: bilinmeyen edat → geçerli seçenekler listelenir
        ValueError: bitisik=True + edat != 'ile' → açıklayıcı mesaj
    """
```

**TR API** (`tr.py`):
```python
def edat_obeği(isim: str, edat: str, bitisik: bool = False) -> str:
    """Türkçe sarmalayıcı — postposition() çağırır."""
```

---

## §6 Kapsam Dışı Detaylar

- **Anlamsal seçim:** hangi edatın kullanılacağı kararı uygulamaya bırakılır
- **Çok-kelimeli edatlar** (`bir türlü`, `göz önünde bulundurarak`) → sözdizimsel, defer
- **`ile` + zamir şekli seçimi** (`ben ile` vs `benimle`) → stil/kayıt tercihi, API her ikisini destekler
- **Ek edatlar** (aralarında, üzerinde gibi) → varlık-iyelik öbekleri, sözdizimsel
- **`bitişik ile` alternatif analizi** (`evle` → ev+ile-bitişik ayrı etiketi) → `evle` zaten
  `decline(case='ins')`'ten çözülür; V1'de ayrı postposition etiketi eklenmez

---

## §7 Edat Analizi (`analyze()` içinde `kind="postposition"`)

Faz E (`parse.py`) tamamlandığı için ertelenen edat analizi açıldı. İki katman:

### §7.1 Tek-token analiz — `_try_postposition_all`

Bağlaç (`de`/`da`) deseninin aynası: **closed-set, oracle-free, additive, her zaman döner**.

```python
Analysis(
    lemma=edat,            # edatın kendisi ("için")
    pos="postp",           # yeni POS (mevcut "conj" geleneğiyle uyumlu)
    kind="postposition",   # _KINDS'a SONA
    kwargs={},             # BOŞ — yönetim lemmadan/tablodan türetilebilir, kwargs'a girmez
    segments=(("için", "kök"),),
    hypothetical=False,    # closed-set → her zaman güvenilir
)
```

- **Additive:** hiçbir okumanın yerini almaz. `analyze("sonra")` hem `postposition` hem eşsesli
  zarf/isim okumasını döner; `analyze("göre")` hem `postposition` hem `gör-e` ulaç okumasını.
  Disambiguation sıralar. (Emsal: `de` = bağlaç + `demek` imp-2sg belirsizliği.)
- **Dispatch:** `conjunction` ile aynı grupta (yüzey closed-set), `number`/`derivation`'dan ÖNCE.
- **Eşsesli homograflar** (adversarial): `aşkın` (=isim `aşk+ın`), `başka` (=sıfat), `üzere` (=`üzer+e`)
  — postposition okuması eklenir ama disambiguation'da doğru okumayı GEÇMEZ (golden sabitler).

### §7.2 PP doğrulaması — `parse.py` R2

- ADP yaprağı artık `Analysis(kind="postposition")` taşır → R2 buna güvenir.
- PP düğümüne `governs` (yönetilen durum kümesi) iliştirilir. `PhraseNode` frozen dataclass →
  yeni opsiyonel alan: `governs: frozenset[str] | None = None` (varsayılan None → mevcut düğüm
  eşitlik testleri kırılmaz; yalnız PP dolu taşır).
- NP tümlecinin durumu `governs`'a uyuyor mu → **yumuşak uyum işareti** (K2 gibi: işaretle, ASLA
  reddetme; recall-güvenli). Bu bilgi E5/E6 dependency/CoNLL-U `case` ilişkisini besler.
- **`için`/zamir asimetrisi burada çözülür:** tek-token analizde tümleç bilinmez → `yönet={nom,gen}`.
  İsim→nom, zamir→gen ayrımı PP doğrulamasında (önceki NP görülünce) devreye girer.

---

## §8 Konsolide Tablo — Tek Doğruluk Kaynağı

Edat bilgisi üç yerde (üretim `postposition.py`, K2 `context.py`, yeni analiz) elle tutuluyordu ve
sapmıştı. Tek tablo `postposition.py::_POSTPOSITIONS`; üretim + analiz + K2 hepsi oradan beslenir.

```python
_POSTPOSITIONS = {
    "edat": {
        "üret":       "<tek case>",           # postposition() üretim case'i (üretilebilir=False ise yok)
        "üret_zamir": "gen",                  # OPSİYONEL — yalnız için (zamir asimetrisi)
        "yönet":      frozenset({...}),        # K2 + analiz KABUL-KÜMESİ (elle yazılır, üret'ten TÜRETİLMEZ)
        "üretilebilir": True/False,            # False → postposition() ValueError (donmuş kalıp)
    },
}
```

**KRİTİK — `yönet` elle yazılır, `üret`'ten türetilmez.** Zamirlerde çok-case alan edatlar:
`ile→{nom,gen}`, `gibi→{nom,gen}`, `kadar→{nom,gen,dat}` (benim ile / benim gibi / senin kadar).
Tek-case `üret`'ten türetilirse bu kümeler daralır → K2 recall kırılır.

`context.py` `_POSTP_GOV = {e: v["yönet"] for e,v in _POSTPOSITIONS.items()}` olarak türetilir;
K2 algoritması DEĞİŞMEZ. Build-time golden: türetilen tablo mevcut `_POSTP_GOV`'un tam anahtar
kümesinde birebir eşit (drift kilidi).

`_ICIN_GEN_PRONOUNS` **korunur** — `üret_zamir` yalnız *hangi* case'i seçer, zamir kümesini kodlamaz.

### §8.1 Genişletilmiş envanter (19 → 23 edat)

**`üretilebilir: False` (donmuş kalıp; analiz + K2 tanır, `postposition()` üretmez):**

| Edat | yönet | Örnek |
|------|-------|-------|
| dair | {dat} | buna dair, konuya dair |
| ilişkin | {dat} | soruna ilişkin |
| ait | {dat} | bana ait, okula ait |
| yana | {abl} | benden yana |

Bu 4 edat `parse.py` ADP tanıma kümesine de eklenir (aksi halde R2 `buna dair` için PP kurmaz).

**Çok-case `yönet` (zamir asimetrisi; §8 KRİTİK):**

| Edat | üret | yönet |
|------|------|-------|
| için | nom (zamir gen) | {nom, gen} |
| ile | nom | {nom, gen} |
| gibi | nom | {nom, gen} |
| kadar | dat | {nom, gen, dat} |

### §8.2 `postposition()` iki ayrı ValueError

- `edat not in _POSTPOSITIONS` → bilinmeyen edat; `Geçerliler:` **yalnız `üretilebilir:True`** listeler.
- `not v["üretilebilir"]` → donmuş edat: ayrı mesaj (ör. `'dair' donmuş bir edat, üretilemez`).
  `dair` "Geçerliler" listesinde GÖRÜNMEZ.

---

## §9 Değişmezler

- `postposition()` üretim çıktısı DEĞİŞMEZ (mevcut 86-girdi golden yeşil).
- K2 **mevcut 19 edat** davranışı DEĞİŞMEZ; 4 yeni edat (dek/üzere/başka/aşkın) için doğrular (recall-güvenli).
- `analyze(roots=None)` postposition dalıyla **her zaman** postposition okuması döner.
- PP doğrulaması hiçbir geçerli yapıyı budamaz.
- `_KINDS`/`_POS` genişlemesi geriye uyumu kırmaz; `PhraseNode.governs` varsayılan None.
