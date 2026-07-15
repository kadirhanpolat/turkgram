# Edat/İlgeç Yönetimi SPEC — Faz 5 D2

Referans: Korkmaz *Türkiye Türkçesi Grameri — Şekil Bilgisi* §275–290 (edatlar/ilgeçler).
Kural olgu; düzyazı/örnek cümleler telif dışı kopyalanmadı.

---

## §1 Kapsam

Bu SPEC yalnız **kapalı küme edatlar** için isim öbeği üretimini kapsar.

Edat öbeği = `decline(lemma, case=yönetilen_durum) + ' ' + edat`

**Kapsam dışı (bu SPEC'te işlenmez):**
- Çok-kelimeli edatlar ve zarf-fiil öbekleri (bir türlü, ilgili olarak) → sözdizimsel
- Edat analizi (`analyze()` içinde edat kind'ı) → sözdizimsel bağlam gerektirir, defer
- Edatın anlamsal seçimi (hangi edatın kullanılacağı kararı) → uygulamaya bırakılır

---

## §2 Edat–Durum Tablosu

| Edat | Yönettiği durum | Örnek | Not |
|------|-----------------|-------|-----|
| için | gen | evin için | — |
| ile | nom / ins | ev ile / evle | Bkz. §3 (ayrı vs bitişik) |
| göre | dat | eve göre | — |
| kadar | dat | eve kadar | — |
| karşı | dat | eve karşı | — |
| rağmen | dat | eve rağmen | — |
| doğru | dat | eve doğru | — |
| dek | dat | eve dek | kadar eşanlamlısı |
| değin | dat | eve değin | kadar eşanlamlısı, yazı dili |
| üzere | dat | eve üzere | — |
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
| onlar | için | decline('onlar', 'gen') + ' için' | onların için |
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
- **Edat çözümlemesi** → sözdizimsel bağlam gerektirir, `analyze()` kapsam dışı
- **`ile` + zamir şekli seçimi** (`ben ile` vs `benimle`) → stil/kayıt tercihi, API her ikisini destekler
- **Ek edatlar** (aralarında, üzerinde gibi) → varlık-iyelik öbekleri, sözdizimsel
