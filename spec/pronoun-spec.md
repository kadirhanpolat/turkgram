# Zamir Morfolojisi — SPEC

**Modül:** `turkgram.morphology_noun` (`decline`, `parse_noun`, `PRONOUN_FORMS`)
**Referans:** Korkmaz *Türkiye Türkçesi Grameri* §399–430 (Zamirler); Ergin §246–265.
**Kapsam:** Kişi zamirleri (ben/sen/o/biz/siz) + işaret (bu/şu/o) + soru (kim/ne)
+ dönüşlü (kendi) + belirsiz (hepsi/herkes/hiçbiri/birisi/biri/öteki/öbürü/hangisi)
— çekim üretimi ve çözümleme (analyze) yansıması.

---

## §1. Mevcut Kapsam ve Açıklar

### Doğru çalışıyor
| Zamir | Durum | Durum |
|-------|-------|-------|
| ben, sen | tekil tüm durumlar | ✅ PRONOUN_FORMS tablosu |
| o, bu, şu | tekil tüm durumlar | ✅ PRONOUN_FORMS |
| o/bu/şu | çoğul (onlar/bunlar/şunlar + çekim) | ✅ `_N_STEM` n-gövde |
| biz, siz | tüm durumlar | ✅ PRONOUN_FORMS |
| kim, ne | tüm durumlar | ✅ düzenli çekim |
| su | iyelik | ✅ `_decline_su_possessive` |

### Açıklar — bu SPEC kapatır

| # | Zamir | Sorun | Beklenen | Mevcut (yanlış) |
|---|-------|-------|----------|----------------|
| P1 | `ben` çoğul | Suppletif — ben çoğulu biz'dir | `'biz'` | `'benler'` |
| P2 | `sen` çoğul | Suppletif — sen çoğulu siz'dir | `'siz'` | `'senler'` |
| P3 | `hepsi` | n-gövde zamiri: eğik durumda -n- | `hepsini/hepsine/…` | `hepsiyi/hepsiye/…` |
| P4 | `kendi` | n-gövde zamiri (dönüşlü) | `kendini/kendine/…` | `kendiyi/kendiye/…` |
| P5 | `herkes` | Kapalı-tablo: son ses k, ek başı ünsüz | `herkesi/herkese/…` | doğrulama golden ile |
| P6 | `hiçbiri` | n-gövde zamiri | `hiçbirini/hiçbirine/…` | hatalı |
| P7 | `birisi`/`biri` | n-gövde zamiri | `birisini/birini/…` | hatalı |
| P8 | `öteki`/`öbürü`/`hangisi` | n-gövde zamiri | `ötekini/öbürünü/hangisini/…` | hatalı |

---

## §2. Zamir Sınıfları

### §2.1 Suppletif Çoğul (P1, P2)

`ben` ve `sen`'in çoğulları suppletiftir:
- `ben` → çoğul lemma: `biz`
- `sen` → çoğul lemma: `siz`

`decline('ben', number='pl', case='dat')` → `decline('biz', number='pl', case='dat')` → `'bize'`

Kapalı tablo:
```python
_PLURAL_SUPPLETION: dict[str, str] = {"ben": "biz", "sen": "siz"}
```

### §2.2 N-Gövde Zamirleri (P3, P4, P6, P7, P8)

Zamirler ünlü-final kök (hepsi, kendi, birisi…) olmasına rağmen eğik durumlarda
-y- kaynaştırması ALMAZ; bunun yerine **-n-** pronominal kaynaştırması alır.

Kural: `has_pron_n = True` → mevcut `_apply_case` mekanizması -n- ekler.

N-gövde zamir kapalı kümesi:
```python
_N_STEM_PRONOUNS: frozenset[str] = frozenset({
    "hepsi", "kendi", "hiçbiri", "birisi", "biri",
    "öteki", "öbürü", "hangisi", "bazısı", "çoğu", "azı",
})
```

Çekim tabloları (elle doğrulanmış):

**hepsi:**
| Durum | Biçim | Not |
|-------|-------|-----|
| nom | hepsi | — |
| acc | hepsini | -n- + -I |
| dat | hepsine | -n- + -A |
| loc | hepsinde | -n- + -DA |
| abl | hepsinden | -n- + -DAn |
| gen | hepsinin | -n- + -In |
| ins | hepsiyle | ünlü-final + -ylA (pron-n tetiklenmez) |

**kendi:**
| Durum | Biçim | Not |
|-------|-------|-----|
| nom | kendi | — |
| acc | kendini | -n- + -I |
| dat | kendine | -n- + -A |
| loc | kendinde | -n- + -DA |
| abl | kendinden | -n- + -DAn |
| gen | kendinin | -n- + -In |
| ins | kendiyle | ünlü-final + -ylA |

**öbürü:**
| Durum | Biçim |
|-------|-------|
| nom | öbürü |
| acc | öbürünü |
| dat | öbürüne |
| loc | öbüründe |
| abl | öbüründen |
| gen | öbürünün |
| ins | öbürüyle |

> **İnstrumental kuralı:** `-yle/-le` eki pronominal-n'yi tetiklemez
> (hepsiyle, kendiyle — NOT hepsiniyle). Mevcut `_apply_case` davranışıyla uyumlu.

### §2.3 `herkes` (P5)

`herkes` düzenli ses-kurallarıyla çekilir (motor zaten doğru üretir):
- `herkesi / herkese / herkeste / herkesten / herkesin / herkesle`

Golden ile sabitlenir; motor değişikliği GEREKMİYOR.

---

## §3. Implementasyon

### `morphology_noun.py` değişiklikleri

1. **`_N_STEM_PRONOUNS`** kapalı kümesi ekle.
2. **`_PLURAL_SUPPLETION`** tablosu ekle.
3. **`decline()`** içinde:
   - Suppletif çoğul dalı: `ben`/`sen` + `number='pl'` → yeniden yönlendir.
   - N-gövde zamir dalı: kök `_N_STEM_PRONOUNS`'da ise `has_pron_n=True` ile `_decline_core` çağır.

`_decline_core` zaten `has_pron_n` parametresini `_apply_case`'e iletir
— yeni morfoloji YOK, yalnız bayrak doğru set edilecek.

### `analysis_candidates.py` değişiklikleri

`_SUPPLETIVE_PRONOUN_ROOTS` sadece `bana`/`sana` içeriyor ve bu yeterli.
N-gövde zamirlerinin eğik biçimleri önek mekanizmasıyla çözülür:
`hepsini` → önek `hepsi` → oracle `decline('hepsi', case='acc')` eşleşir → ✅

Ek kapalı-tablo kaydı GEREKMİYOR.

---

## §4. Kapsam Dışı (Defer)

- Dönüşlü zamir + iyelik istifi (`kendimi/kendini/kendimizi`): Faz 3.x
- Zamir + copula bileşim (`bendeyken`, `bizdeymiş`): mevcut mekanizma kapsar
- Soru + zamir öbekleri (`kime göre`): sözdizimi, Faz 4

---

## §5. Doğrulama Kriterleri

- [ ] `decline('ben', number='pl')` → `'biz'`
- [ ] `decline('sen', number='pl')` → `'siz'`
- [ ] `decline('ben', number='pl', case='dat')` → `'bize'`
- [ ] `decline('hepsi', case='acc')` → `'hepsini'`
- [ ] `decline('hepsi', case='dat')` → `'hepsine'`
- [ ] `decline('hepsi', case='loc')` → `'hepsinde'`
- [ ] `decline('hepsi', case='abl')` → `'hepsinden'`
- [ ] `decline('hepsi', case='gen')` → `'hepsinin'`
- [ ] `decline('hepsi', case='ins')` → `'hepsiyle'`
- [ ] `decline('kendi', case='acc')` → `'kendini'`
- [ ] `decline('kendi', case='dat')` → `'kendine'`
- [ ] `decline('kendi', case='ins')` → `'kendiyle'`
- [ ] `decline('öbürü', case='acc')` → `'öbürünü'`
- [ ] `analyze('hepsini', roots={'hepsi'})` → `kind='decline', case='acc'`
- [ ] `analyze('kendine', roots={'kendi'})` → `kind='decline', case='dat'`
- [ ] Regresyon: 2960+ test yeşil
- [ ] Korpus hakem: 0 çökme
