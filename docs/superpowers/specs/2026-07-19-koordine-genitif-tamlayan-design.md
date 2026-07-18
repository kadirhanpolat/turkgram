# Koordine genitif tamlayan + özel-isim apostrof-ek yeniden kurulum — Tasarım

**Tarih:** 2026-07-19
**Kapsam:** Constituency parser (`parse.py`) + dependency (`dependency.py`)
**Statü:** SPEC (ana oturum yazdı) → bağımsız golden → motor → hakem

## 1. Amaç

`Ali'nin ve Veli'nin evi` → `NP( CoordP(Ali'nin ve Veli'nin), evi )` biçiminde
**koordine belirtili isim tamlaması** kurmak. İki bağımsız açık kapatılır:

- **B1 — Özel-isim apostrof-ek yeniden kurulum:** Tokenizer `Ali'nin`'i
  `["Ali", "'nin"]` böler (bilinçli, `tokenize` golden'da kilitli). Parser bu
  ikiliyi tek `NOUN[case]` yaprağına birleştirmeli, aksi halde hiçbir kural
  genitif özel-isim göremez.
- **B2 — Genitif tamlama genellemesi:** Mevcut R0 yalnız bitişik `NOUN[gen]
  NOUN[poss]` (`evin kapısı`) işler. Koordine tamlayan (`evin ve kapının rengi`,
  `Ali'nin ve Veli'nin evi`) için `CoordP(hepsi gen) + head` birleşmesi eksik.

Kullanıcı kararı (2026-07-19): yeniden kurulum **parse katmanında** olur;
tokenizer ve `tokenize` golden'ı DEĞİŞMEZ.

## 2. B1 — Özel-isim apostrof-ek merge (R_proper)

### 2.1 Tetikleme (yüzey tabanlı, kapalı sinyal)

Bitişik iki yaprak `(a, b)`:
- `a` herhangi bir yaprak (özel-isim adayı — leksikonda olması ŞART DEĞİL),
- `b.token` düz apostrof `'` (U+0027) ile başlar.

Türkçe imlada apostrof YALNIZCA özel-ad/sayı/kısaltma + çekim eki sınırında
kullanılır → apostrofun kendisi kesin sinyaldir (edat/bağlaç/diye kapalı-küme
yüzey deseninin emsali; oracle-dışı, recall-güvenli).

### 2.2 Durum sınıflandırıcı (yumuşama-FREE, deterministik)

**TUZAK — motor yumuşatır, imla yumuşatmaz:** `decline("Ahmet","gen")` →
`Ahmedin` (t→d); imla `Ahmet'in` (yumuşama YOK). Bu yüzden merged-surface
oracle (`decline == yüzey`) yumuşayan özel-isimde KIRILIR. Çözüm: apostrof
ekini (`b.token[1:]`, `_tr_lower`) doğrudan durum-eki iskeletiyle sınıflandır;
ismi VERBATIM (yumuşamasız) kullan.

Ek → durum tablosu (regex, `^…$` anchored, Türkçe ünlü duyarlı):

| durum | regex | örnek ekler |
|-------|-------|-------------|
| gen   | `^n?[ıiuü]n$`   | nin nın nun nün / in ın un ün |
| acc   | `^y?[ıiuü]$`    | yi yı yu yü / i ı u ü |
| dat   | `^y?[ae]$`      | ye ya / e a |
| loc   | `^[dt][ae]$`    | de da / te ta |
| abl   | `^[dt][ae]n$`   | den dan / ten tan |
| ins   | `^y?l[ae]$`     | yle yla / le la |
| (plural — kapsam DIŞI, V1) | — | ler lar |

Regex'ler karşılıklı dışlayıcı (anchored). **Tam bir eşleşme yoksa (0 veya >1)
→ MERGE ETME** (recall-güvenli; malformed/kapsam-dışı ek dokunulmaz kalır).
Plural + iyelik+durum kombinasyonları V1 kapsam dışı.

### 2.3 Üretilen yaprak

`LeafNode(tag="NOUN", token=a.token + b.token, analysis=Analysis(...))`:
- `lemma = a.token` (VERBATIM, büyük harfli özel-ad korunur → CoNLL-U lemma "Ali"),
- `pos = "noun"`, `kind = "decline"`,
- `kwargs = {"case": <sınıf>}` (nom hariç; nom zaten apostrof gerektirmez),
- `segments = ((a.token,"KÖK"), (b.token[1:], <durum-etiketi>))` — pedagoji için
  minimal; spanّ hesabı gerektirmez (parse-içi, round-trip iddiası yok),
- `hypothetical = False`.

`token` apostroflu birleşik yüzey (`Ali'nin`) → `PhraseNode.surface` doğal
`Ali'nin ve Veli'nin evi` verir.

### 2.4 Boru hattı konumu

R_proper **en başta** (R8/R9'dan önce) çalışır: sonraki tüm kurallar (R0,
R_gencoord, R1, R4) yeniden kurulmuş `NOUN[case]` yaprağını görür.

## 3. B2 — Genitif tamlama genellemesi

### 3.1 R_gencoord — genitif koordinasyonu (R0'dan ÖNCE)

`NOUN[gen] (CCONJ NOUN[gen])+` → `CoordP`.

R3c (sıfat koordinasyonu) emsali: R0'dan ÖNCE çalışır. Aksi halde R0 sağdaki
`NOUN[gen] head` çiftini erken yakalar (`Veli'nin evi`), ilk tamlayan (`Ali'nin
ve`) başıboş kalır.

Yalnız YAPRAK `NOUN[gen]` konjunktlar (bu aşamada henüz NP kurulmadı). Konjunkt
sayısı ≥ 2.

### 3.2 R0 genelleme — possessor + head → NP

Eski: `NOUN[gen] NOUN[poss]` → NP.
Yeni: `possessor + head` → NP, nerede:
- `possessor` = `NOUN[gen]` **VEYA** `CoordP` (R_gencoord çıktısı; tüm konjunktlar
  gen NOUN),
- `head` = bitişik `NOUN` (herhangi durum) veya `NP`.

**TUZAK — head'in poss etiketi ŞART DEĞİL (recall-güvenli):** `evi`/`rengi`
poss/acc homografı; `parse_text` rank_in_context UYGULAMAZ, `parse_phrase` izole
`disambiguation.rank` kullanır → homograf head acc sıralanabilir. Dilbilimsel
olgu: **Türkçede yalın genitif ZORUNLU possessed-head ister** (tamlayan tek
başına duramaz) → gen-possessor + bitişik ad = tamlama, head'in yüzey-durumu ne
olursa olsun. Bu yüzden birleşme head poss-etiketini kontrol ETMEZ. (Yan fayda:
`adamın evi` basit tamlaması da yapısal olarak düzelir — önceden `evi` acc → R0
fire etmiyordu.)

**Sıra:** R0-genel R_gencoord'dan SONRA (CoordP possessor'u görebilmek için),
R1'den ÖNCE (head henüz çıplak NOUN).

CoordP possessor + head birleşmesinde CoordP olduğu gibi ilk çocuk, head ikinci
çocuk: `NP( CoordP(...), head )`.

### 3.3 Sözcük sırası (regresyon güvenliği)

- `NOUN[gen] head` bitişik → NP (tamlama). Doğru.
- `NOUN[nom] ... VERB` (özne) → gen değil, R0 tetiklenmez. Değişmez.
- Gen konjunkt + head YOKSA (`Ali'nin ve Veli'nin` tek başına) → CoordP kalır
  (R_gencoord ürünü), R0-genel head bulamaz → dokunmaz. Doğru (koordine tamlayan
  öbeği, cümle argümanı olabilir).

## 4. Dependency (`dependency.py`)

### 4.1 Baş bulma (`_find_head_leaf`)

NP başı = possessed head. Mevcut NP dalı (en sağdaki possessive NOUN → yoksa en
sağdaki NOUN) zaten head'i (`evi`) döndürür (CoordP'yi atlar, sağdaki NOUN'u
bulur). **Değişiklik gerekmez.**

### 4.2 Deprel (`_child_deprel`)

- **NP-child CoordP (gen konjunktlar) → `nmod:poss`:** Mevcut NP+CoordP dalı
  yalnız ADJ/AdjP konjunkt için amod döner; NP/NOUN konjunkt (gen) durumunda
  düşer → `dep`. Ekle: `conj_cat in ("NP","NOUN")` ve konjunkt başı gen ise
  `nmod:poss`.
- **CoordP içi:** `cc` (CCONJ) + `conj` (NP konjunkt) — mevcut CoordP dalı zaten
  kapsar. Değişmez.
- **NP-child NOUN[gen] (basit possessor) → `nmod:poss`:** Mevcut satır
  (`case=="gen" → nmod:poss`) zaten kapsar.

### 4.3 Head possessive feats

Head poss/acc homografında acc sıralanırsa `Number[psor]`/`Person[psor]` feats
eksik kalabilir (yüzey-durum acc yazılır). Bu **pre-existing disambiguation
sınırı** (K5 parse'a bağlı değil); yapısal ağaç + `nmod:poss` deprel DOĞRU.
Feats düzeltmesi kapsam DIŞI (ayrı iş: parse_phrase'e context entegrasyonu).

## 5. Test planı

**Bağımsız golden (Opus, motor-körü):**
- B1 merge: `Ali'nin evi` (gen), `İstanbul'da` (loc), `Ankara'ya` (dat, tek yaprak).
- B2 koordine: `Ali'nin ve Veli'nin evi`, `evin ve kapının rengi` (common-noun),
  `Ali'nin ve Veli'nin ve Ayşe'nin evi` (3'lü).
- Basit tamlama regresyon: `evin kapısı` (poss net), `adamın evi` (acc homograf → yapısal NP).
- Negatif: `Ali'nin ve Veli'nin` (head yok → CoordP kalır).
- Dependency: koordine tamlayan → nmod:poss + conj/cc.

**Hakem:** korpus sweep (dict-db isim çiftleri × gen-koordinasyon × head, 0 çökme);
tam paket regresyonsuz; adversarial verify (R0 gevşetme yan etkisi + sınıflandırıcı
ambiguite).

## 6. Kapsam dışı (V1)

- Plural/iyelik+durum apostrof ekleri (`Ali'ler`, `Ali'sinin`).
- Head possessive feats disambiguation (poss/acc homograf).
- Sayı/kısaltma + apostrof (`2026'da` merge — yalnız özel-ad hedeflendi; ama
  R_proper yüzey tabanlı olduğundan `2026'da` da loc merge olur → kabul, zararsız).
- Karışık koordinasyon (`Ali'nin ve büyük ev` — gen + non-gen konjunkt).
