# Faz E — Sözdizim Genişletme: Tasarım Dokümanı

**Tarih:** 2026-07-17  
**Durum:** Onaylandı  
**Kapsam:** E1 Zengin öbek üretimi → E2 Constituency parser → E5 Dependency çıkarımı → E6 UD/CoNLL-U export

---

## 1. Genel Mimari

Faz E dört art arda alt-fazdan oluşur. Her alt-faz bir öncekinin çıktısını girdi olarak alır.

```
[Morfoloji katmanı]  decline / conjugate / postposition / conjunction  (dokunulmaz)
       ↓
[E1]  Zengin öbek üretimi   →  syntax.py genişletme
       ↓
[E2]  Constituency parser   →  parse.py  (yeni)
       ↓
[E5]  Dependency çıkarımı   →  dependency.py  (yeni)
       ↓
[E6]  UD/CoNLL-U export     →  dependency.py içinde to_conllu()
```

**Temel kararlar:**

- Saf Python, sıfır dış bağımlılık.
- Tüm veri yapıları `frozen=True` dataclass — değişmezlik korunur.
- `analyze()` / `decline()` / `conjugate()` imzaları dokunulmaz.
- Yan cümleler (ki/diye) ve zincirli fiilimsi öbekleri kapsam dışı — E3/E4 ayrı faz.

---

## 2. Dosya Planı

| Dosya | Değişiklik |
|-------|-----------|
| `turkgram/syntax.py` | E1 eklentileri: `np_uret`, `pp_uret`, `advp_uret`, `koordine_np` |
| `turkgram/parse.py` | Yeni — E2 constituency parser: `LeafNode`, `PhraseNode`, `parse_phrase` |
| `turkgram/dependency.py` | Yeni — E5+E6: `DepToken`, `constituency_to_dep`, `to_conllu` |
| `turkgram/__init__.py` | Yeni public API'ler export edilir |
| `turkgram/tr.py` | Türkçe sarmalayıcılar |

---

## 3. E1 — Zengin Öbek Üretimi

### 3.1 `np_uret` — Karmaşık İsim Öbeği

```python
def np_uret(
    head: str,
    *,
    on_sifatlar: list[str] = [],
    tamlayan: str | None = None,
    miktar: str | None = None,
    durum: str = "nom",
    iyelik: str | None = None,
) -> str
```

**Üretim sırası (Türkçe soldan-sağa):**
1. `miktar` (varsa) → değişmez
2. `on_sifatlar` → sırayla, değişmez (Türkçe'de sıfat çekilmez)
3. `tamlayan` → `decline(tamlayan, case='gen')` (belirtili tamlama)
4. `head` → `decline(head, case=durum, possessive=iyelik)`

**Örnekler:**
```python
np_uret('kapı', on_sifatlar=['büyük'], tamlayan='ev', durum='acc')
→ 'büyük evin kapısını'

np_uret('kitap', miktar='üç', durum='dat')
→ 'üç kitaba'
```

### 3.2 `pp_uret` — Edat Öbeği

```python
def pp_uret(isim: str, edat: str, *, bitişik: bool = False) -> str
```

Mevcut `postposition.postposition()` işlevini saran ince sarmalayıcı. Yeni morfoloji yok.

```python
pp_uret('ev', 'göre')   → 'eve göre'
pp_uret('okul', 'ile', bitişik=True)  → 'okulla'
```

### 3.3 `advp_uret` — Zarf Öbeği

```python
def advp_uret(zarf: str, *, derece: str | None = None) -> str
```

`derece` ∈ `{'çok', 'oldukça', 'pek', 'biraz', 'en', 'daha'}`. Derece varsa önüne gider.

```python
advp_uret('hızlı', derece='çok')  → 'çok hızlı'
advp_uret('iyi')                  → 'iyi'
```

### 3.4 `koordine_np` — Koordinasyon Öbeği

```python
def koordine_np(ogeler: list[str], baglac: str = "ve") -> str
```

Mevcut `conjunction.coordinate()` işlevini saran sarmalayıcı. İki ve üzeri öğe desteklenir.

```python
koordine_np(['kitap', 'defter'])           → 'kitap ve defter'
koordine_np(['kitap', 'defter'], 'veya')   → 'kitap veya defter'
```

**Not:** VP genişletmesi E1 kapsamı dışında — `conjugate()` API'si yeterli.

---

## 4. E2 — Constituency Parser

### 4.1 Veri Yapıları

```python
@dataclass(frozen=True)
class LeafNode:
    tag: str          # 'NOUN' | 'VERB' | 'ADJ' | 'ADP' | 'ADV' | 'CCONJ' | …
    token: str        # yüzey biçimi
    analysis: Analysis | None

@dataclass(frozen=True)
class PhraseNode:
    tag: str                                   # 'NP' | 'VP' | 'S' | 'AdvP' | 'PP' | 'CoordP'
    children: tuple[PhraseNode | LeafNode, ...]
    surface: str                               # ' '.join(leaf.token for leaf in tree)
```

### 4.2 API

```python
def parse_phrase(
    tokens: list[str],
    analyses: list[list[Analysis]],
) -> PhraseNode
```

**Giriş:** `tokenize()` + `parse_text()` çıktıları (zaten mevcut).  
**Çıkış:** Kök etiketi `'S'` olan `PhraseNode` ağacı.

### 4.3 Parser Kuralları

Kural-tabanlı, Türkçe SOV sırasına göre. Tek geçiş (bottom-up gruplama):

| Kural | Örüntü | Çıktı |
|-------|---------|-------|
| R1 | `ADJ* NOUN (GEN NOUN)*` | `NP` |
| R2 | `NP ADP` | `PP` |
| R3 | `ADV* ADJ` | `AdvP` |
| R4 | `NP (CCONJ NP)+` | `CoordP` |
| R5 | `NP* VP` | `S` |

**Türkçe özgü davranışlar:**

- **Fiilimsi modifier:** `kind=participle` analizine sahip token → sol taraftaki `NOUN`'a bağlanan `NP` oluşturur.
- **Serbest sözcük sırası:** VP sona gelemezse `S` yine kurulur; `PhraseNode` üzerinde `warnings` alanı eklenmez — kullanıcı `surface` üzerinden kontrol eder.
- **Belirsizlik çözümü:** Birden fazla analiz varsa `disambiguation.rank()` ile en üst aday seçilir.

### 4.4 POS Etiket Eşlemesi

`Analysis.pos` → constituency `tag`:

| `Analysis.pos` | `LeafNode.tag` |
|----------------|----------------|
| `'verb'` | `'VERB'` |
| `'noun'` | `'NOUN'` |
| `'adj'` | `'ADJ'` |
| `'adv'` | `'ADV'` |
| `'conj'` | `'CCONJ'` |
| `None` (kind=decline) | `'NOUN'` |
| `None` (kind=copula) | `'VERB'` |

---

## 5. E5 — Dependency Graph Çıkarımı

### 5.1 `DepToken` Veri Yapısı

```python
@dataclass(frozen=True)
class DepToken:
    id: int       # 1-tabanlı (CoNLL-U standardı)
    form: str     # yüzey biçimi
    lemma: str | None
    upos: str     # UD evrensel POS
    xpos: str     # dil-özgü: turkgram kind ('conjugate', 'decline', …)
    feats: str    # UD morfolojik özellikler ('Case=Acc|Number=Sing|…' ya da '_')
    head: int     # 0 = kök
    deprel: str   # UD ilişkisi ('root', 'nsubj', 'obj', 'nmod', …)
    misc: str     # '_' ya da ek bilgi
```

### 5.2 API

```python
def constituency_to_dep(tree: PhraseNode) -> list[DepToken]
```

### 5.3 Head-Finding Kuralları

| Öbek | Baş (head) | Bağımlı ilişkileri |
|------|-----------|---------------------|
| `NP` | En sağdaki `NOUN` | Sol `ADJ` → `amod`; `miktar` → `nummod`; tamlayan `NP` → `nmod` |
| `PP` | `ADP` (edat) | `NP` → `nmod` |
| `AdvP` | `ADJ` ya da `ADV` | `derece` → `advmod` |
| `CoordP` | İlk `NP` | Diğer `NP`'ler → `conj`; `CCONJ` → `cc` |
| `VP` | `VERB` | Özne `NP` → `nsubj`; nesne `NP` → `obj`; `PP` → `obl`; `AdvP` → `advmod` |
| `S` | `VP` başı | Kök bağı (`head=0`, `deprel='root'`) |

### 5.4 UD Features Eşlemesi

`Analysis` alanları → CoNLL-U `feats` sütunu:

| Analysis alanı | UD feat |
|----------------|---------|
| `case='acc'` | `Case=Acc` |
| `case='dat'` | `Case=Dat` |
| `case='gen'` | `Case=Gen` |
| `case='abl'` | `Case=Abl` |
| `case='loc'` | `Case=Loc` |
| `case='ins'` | `Case=Ins` |
| `tense='past'` | `Tense=Past` |
| `tense='pres'` | `Tense=Pres` |
| `tense='fut'` | `Tense=Fut` |
| `person='1sg'` | `Number=Sing\|Person=1` |
| `person='3pl'` | `Number=Plur\|Person=3` |
| `possessive='2sg'` | `Number[psor]=Sing\|Person[psor]=2` |
| `negative=True` | `Polarity=Neg` |

Birden fazla özellik varsa alfabetik sıra ve `|` ayraç (UD standardı).

---

## 6. E6 — CoNLL-U Export

### 6.1 API

```python
def to_conllu(
    tokens: list[DepToken],
    *,
    sent_id: str = "",
    text: str = "",
) -> str
```

**Çıktı formatı (CoNLL-U):**
```
# sent_id = 1
# text = öğrenci kitabı okudu
1	öğrenci	öğrenci	NOUN	decline	Case=Nom|Number=Sing	3	nsubj	_	_
2	kitabı	kitap	NOUN	decline	Case=Acc|Number=Sing	3	obj	_	_
3	okudu	okumak	VERB	conjugate	Number=Sing|Person=3|Tense=Past	0	root	_	_
```

### 6.2 Tam Uçtan Uca Örnek

```python
from turkgram import tokenize, parse_text
from turkgram.parse import parse_phrase
from turkgram.dependency import constituency_to_dep, to_conllu

text = "öğrenci kitabı okudu"
tokens = tokenize(text)
analyses = parse_text(text)
tree = parse_phrase(tokens, analyses)
dep = constituency_to_dep(tree)
print(to_conllu(dep, sent_id="1", text=text))
```

---

## 7. Test Stratejisi

Her alt-faz için ayrı golden + runner (mevcut iş akışıyla tutarlı):

| Alt-faz | Golden dosya | Runner |
|---------|-------------|--------|
| E1 | `tests/golden_syntax_rich.py` | `tests/test_syntax_rich.py` |
| E2 | `tests/golden_parse.py` | `tests/test_parse.py` |
| E5 | `tests/golden_dependency.py` | `tests/test_dependency.py` |
| E6 | `tests/golden_conllu.py` | `tests/test_conllu.py` |

Golden'lar motordan bağımsız kurulur (Opus, motor-körü) — mevcut CLAUDE.md §2 iş akışı.

---

## 8. Kapsam Dışı (Bu Faz)

- Yan cümleler: ki-cümleleri, diye-cümleleri (E3/E4 ayrı faz)
- Zincirli fiilimsi öbekleri: `okuduğu kitabı aldığı çanta`
- İstatistiksel/ML parsing
- spaCy pipeline entegrasyonu
- Named entity recognition

---

## 9. Bağımlılıklar

Faz E yalnızca turkgram'ın mevcut modüllerini kullanır:

- `morphology.conjugate` — VP için
- `morphology_noun.decline` — NP durum çekimi için
- `postposition.postposition` — PP için (pp_uret sarmalayıcı)
- `conjunction.coordinate` — CoordP için (koordine_np sarmalayıcı)
- `analysis.parse_text` + `tokenize.tokenize` — parser girdisi için
- `disambiguation.rank` — belirsizlik çözümü için
